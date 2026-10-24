#!/usr/bin/env python3
"""Exercise measurement with local browser fixtures; never send live events."""
import json
from pathlib import Path
import re
import sqlite3
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chrome import Chrome, LocalServer
from common import find_chrome

ROOT = Path(__file__).resolve().parents[2]
CHROME = find_chrome()


@unittest.skipUnless(CHROME, 'Chrome unavailable')
class Measurement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = LocalServer(ROOT)
        cls.server.__enter__()
        cls.browser = Chrome(str(CHROME))
        cls.browser.open(cls.server.url + '/site/measurement.js')

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.__exit__(None, None, None)

    def fixture(self, preference='', automated=False, privacy=False):
        self.browser.open(self.server.url + '/site/measurement.js')
        source = (ROOT / 'site/measurement.js').read_text()
        setup = f'''localStorage.clear(); sessionStorage.clear();
          Object.defineProperty(navigator,'webdriver',{{value:{json.dumps(automated)},configurable:true}});
          Object.defineProperty(navigator,'globalPrivacyControl',{{value:{json.dumps(privacy)},configurable:true}});
          Object.defineProperty(navigator,'doNotTrack',{{value:'0',configurable:true}});
          history.replaceState(null,'','/site/fixture{preference}');
          document.body.innerHTML='<div data-measurement-controls hidden><p data-measurement-status></p></div><a id="download" href="https://github.com/diyanko/rpi-thesis-toolkit/releases/download/v0.3.0/rpi-thesis-starter-v0.3.0.zip">Download</a>';
          window.sent=[]; window.fetch=(url,options)=>{{sent.push({{url,options}});return Promise.resolve();}};
          var script=document.createElement('script');
          script.dataset.site=location.origin+'/site/';
          script.dataset.repository='https://github.com/diyanko/rpi-thesis-toolkit';
          script.dataset.counter=location.origin+'/event';
          script.textContent={json.dumps(source)}; document.body.appendChild(script);
          document.addEventListener('click',e=>e.preventDefault(),{{once:true}});'''
        self.browser.evaluate(setup)

    def click(self):
        point = self.browser.evaluate("(()=>{var r=document.querySelector('#download').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
        for action in ('mousePressed', 'mouseReleased'):
            self.browser.call('Input.dispatchMouseEvent', type=action, button='left', clickCount=1, **point)

    def test_trusted_first_click_and_synthetic_repeat(self):
        self.fixture()
        self.browser.evaluate("document.querySelector('#download').click()")
        self.assertEqual(self.browser.evaluate('sent.length'), 0)
        # Install the cancellation again: synthetic click consumed the once listener.
        self.browser.evaluate("document.addEventListener('click',e=>e.preventDefault())")
        self.click()
        self.click()
        sent = self.browser.evaluate('sent')
        self.assertEqual(len(sent), 1)
        self.assertEqual(json.loads(sent[0]['options']['body']), {'asset': 'starter'})
        self.assertEqual(sent[0]['options']['credentials'], 'omit')
        self.assertEqual(sent[0]['options']['referrerPolicy'], 'no-referrer')
        self.assertTrue(sent[0]['options']['keepalive'])

    def test_optout_automation_and_privacy_signal(self):
        for preference, automated, privacy in [('?measurement=off', False, False), ('', True, False), ('', False, True)]:
            with self.subTest(preference=preference, automated=automated, privacy=privacy):
                self.fixture(preference, automated, privacy)
                self.click()
                self.assertEqual(self.browser.evaluate('sent.length'), 0)
                self.assertIn('off', self.browser.evaluate("document.querySelector('[data-measurement-status]').textContent"))

    def test_categories_and_unrelated_links(self):
        for path, category in [
            ('https://www.overleaf.com/docs?snip_uri=https%3A%2F%2Fgithub.com%2Fdiyanko%2Frpi-thesis-toolkit%2Freleases%2Fdownload%2Fv0.3.0%2Frpi-thesis-overleaf-v0.3.0.zip', 'overleaf'),
            ('/site/downloads/rpi-thesis.cls', 'class'),
            ('/site/downloads/rpi-thesis-cheatsheet.pdf', 'cheatsheet'),
            ('https://github.com/other/project/releases/download/v1/file.zip', None),
        ]:
            with self.subTest(category=category):
                self.fixture()
                self.browser.evaluate("document.querySelector('#download').href=" + json.dumps(path))
                self.click()
                sent = self.browser.evaluate('sent')
                self.assertEqual([json.loads(event['options']['body'])['asset'] for event in sent], [] if category is None else [category])

    def test_exclusion_changed_after_page_load(self):
        self.fixture()
        self.browser.evaluate("localStorage.setItem('rpi-thesis-measurement','off')")
        self.click()
        self.assertEqual(self.browser.evaluate('sent.length'), 0)

    def test_worker_validation_and_atomic_aggregate(self):
        source = (ROOT / 'services/download-counter/worker.js').read_text().replace('export default', 'window.counter =')
        result = self.browser.evaluate('''(async()=>{''' + source + '''
          var writes=[]; var db={prepare(sql){return {bind(...args){writes.push(args);return this},async run(){},async all(){return {results:[]}}}}};
          async function send(body,origin='https://diyanko.github.io') {var request=new Request('https://counter.example/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); return (await counter.fetch({url:request.url,method:request.method,body:request.body,headers:{get(name){return name==='Origin'?origin:request.headers.get(name)}}},{COUNTS:db})).status;}
          var statuses=[await send({asset:'starter'}),await send({asset:'starter',url:'private'}),await send({asset:'unknown'}),await send({asset:'starter'},'https://other.example'),await send({asset:'x'.repeat(100)})];
          var counts=await counter.fetch(new Request('https://counter.example/counts'),{COUNTS:db});
          return {statuses,writes,counts:await counts.json()};})()''')
        self.assertEqual(result['statuses'], [204, 400, 400, 403, 400])
        self.assertEqual(len(result['writes']), 1)
        self.assertRegex(result['writes'][0][0], r'^\d{4}-\d{2}-\d{2}$')
        self.assertEqual(result['writes'][0][1], 'starter')
        self.assertEqual(result['counts']['days'], [])
        sql = re.search(r'"(INSERT INTO daily_downloads[^"\n]+)"', source).group(1)
        with sqlite3.connect(':memory:') as db:
            db.executescript((ROOT / 'services/download-counter/schema.sql').read_text())
            for _ in range(2):
                db.execute(sql, ('2026-10-24', 'starter'))
            self.assertEqual(db.execute('SELECT total FROM daily_downloads').fetchone(), (2,))


if __name__ == '__main__':
    unittest.main()
