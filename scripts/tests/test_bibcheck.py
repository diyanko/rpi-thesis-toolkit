#!/usr/bin/env python3
"""Synthetic bibliography and browser-control checks; no TeX compilation.

Uses the existing Chrome helper, without adding a JS runtime dependency.
Run: python3 scripts/tests/test_bibcheck.py
"""
import json
import re
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chrome import Chrome, LocalServer
from common import ROOT, find_chrome


BOOK = '@book{key, author={Alice Smith}, title={An example}, date={2024}, publisher={Example Press}}'
ARTICLE = '@article{key, author={Alice Smith}, title={An example}, date={2024}, journaltitle={Example Journal}, volume={1}, pages={1--9}}'
NUMERIC = r'\usepackage[style=numeric]{biblatex}'

@unittest.skipUnless(find_chrome(), 'no Chrome')
class BibCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def dynamic(path, query):
            if path == '/test.html':
                return (b'<script type="module">import * as api from "/bibcheck/core.js"; window.api = api;</script>', 'text/html')
        cls.server = LocalServer(ROOT / 'site', dynamic)
        cls.browser = Chrome(find_chrome())
        cls.browser.open(cls.server.url + '/test.html')
        cls.browser.evaluate("new Promise((resolve, reject) => { let n = 0; const poll = () => window.api ? resolve(true) : ++n > 100 ? reject(Error('module did not load')) : setTimeout(poll, 20); poll(); })")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.close()

    def check(self, bib=BOOK, **options):
        return self.browser.evaluate('api.checkReferences(' + json.dumps({'bib': bib, **options}) + ')')

    def ids(self, bib=BOOK, **options):
        return {f['id'] for f in self.check(bib, **options)['findings']}

    def test_starter_is_clean_with_and_without_preamble(self):
        bib = (ROOT / 'references.bib').read_text()
        preamble = (ROOT / 'preamble.tex').read_text()
        chapters = [{'name': str(p.relative_to(ROOT)), 'text': p.read_text()}
                    for folder in ('chapters', 'appendices') for p in (ROOT / folder).glob('*.tex')]
        self.assertEqual(self.check(bib)['findings'], [])
        self.assertEqual(self.check(bib, preamble=preamble, tex=chapters)['findings'], [])

    def test_parser_preserves_nested_protection_quotes_and_escaped_braces(self):
        bib = r'''% @book{ignored, title={Ignore}}
@string{press = "Example" # " Press"}
@comment{A comment with @online{nested}}
@book(key, author="Alice Smith", title={{NASA} and \{a\}}, date=2024, publisher=press)
'''
        self.assertEqual(self.ids(bib), set())
        data = self.browser.evaluate('api.parseBib(' + json.dumps(bib) + ')')
        self.assertEqual(data['entries'][0]['fields']['publisher'], 'Example Press')

    def test_broken_syntax_and_unknown_macros_are_not_silent(self):
        fixtures = [r'@book{broken, title={A title}', r'@book{key, title={Title} author={Alice}}',
                    r'@book{key, title={Title}, title={Again}}', r'@book{key, a field}']
        for bib in fixtures:
            with self.subTest(bib=bib):
                self.assertIn('syntax', self.ids(bib))
        self.assertIn('unsupported', self.ids('@book{k, title=unknownmacro}'))
        self.assertIn('empty', self.ids('% nothing here'))

    def test_keys_duplicate_case_and_spaces(self):
        self.assertIn('duplicate', self.ids(BOOK + '\n' + BOOK))
        self.assertIn('keyCase', self.ids(BOOK + '\n' + BOOK.replace('key,', 'KEY,')))
        self.assertIn('key', self.ids(BOOK.replace('key,', 'bad key,')))

    def test_citations_comments_multicites_optional_arguments_and_nocite(self):
        tex = r'''% \cite{commented}
\parencite[see][2]{key, absent} {grouped prose}
\textcites[4]{other}[5]{another}
\nocite{*}
\begin{verbatim}\cite{example}\end{verbatim}
'''
        report = self.check(tex=[{'name': 'chapter.tex', 'text': tex}], unused=True)
        missing = [f for f in report['findings'] if f['id'] == 'missing']
        self.assertEqual({f['key'] for f in missing}, {'absent', 'other', 'another'})
        self.assertTrue(all('chapter.tex' in f['fix'] for f in missing))
        self.assertNotIn('unused', {f['id'] for f in report['findings']})
        self.assertIn('unused', self.ids(tex=[{'text': r'\cite{absent}'}], unused=True))
        self.assertNotIn('unused', self.ids(unused=True))

    def test_field_profiles_and_style_detection(self):
        for style in ('numeric', 'authoryear', 'ieee', 'apa', 'mla', 'chem-acs'):
            with self.subTest(style=style):
                preamble = r'% \usepackage[style=wrong]{biblatex}' + '\n' + r'\usepackage[backend=biber, style = ' + style + ']{biblatex}'
                self.assertEqual(self.check(preamble=preamble)['style'], style)
        self.assertEqual(self.check(preamble=r'\usepackage[authordate]{biblatex-chicago}')['style'], 'chicago')
        self.assertIn('style', self.ids(preamble=r'\usepackage[style=custom]{biblatex}'))
        self.assertNotIn('required', self.ids(ARTICLE))
        self.assertIn('required', self.ids(ARTICLE.replace('journaltitle', 'notjournal')))
        self.assertIn('recommended', self.ids(ARTICLE, preamble=r'\usepackage[style=apa]{biblatex}'))
        self.assertNotIn('recommended', self.ids(ARTICLE, preamble=NUMERIC))
        self.assertIn('recommended', self.ids(BOOK, preamble=r'\usepackage[style=chicago-authordate]{biblatex}'))
        # BibTeX aliases imply a thesis type; the student need not repeat it.
        self.assertNotIn('required', self.ids('@phdthesis{k, author={Alice Smith}, title={Work}, year=2024, school={Example University}}'))

    def test_access_dates_apply_to_every_url(self):
        for entry_type in ('book', 'article', 'online'):
            with self.subTest(entry_type=entry_type):
                self.assertIn('access', self.ids('@' + entry_type + '{k, title={Work}, url={https://example.org}}'))
        self.assertNotIn('access', self.ids(BOOK[:-1] + ', doi={10.1234/example}}'))

    def test_dates_years_months_and_calendar(self):
        for date in ('2024-02-30', '2023-02-29', '2024-13', 'May 2024', '2024-00-01'):
            with self.subTest(date=date):
                self.assertIn('date', self.ids(BOOK.replace('2024', date)))
        for date in ('2024-02-29', '2024-01', '2020/2024', '2020/'):
            with self.subTest(date=date):
                self.assertNotIn('date', self.ids(BOOK.replace('2024', date)))
        self.assertIn('date', self.ids(BOOK[:-1] + ', urldate={2024}}'))
        self.assertIn('year', self.ids(BOOK.replace('date={2024}', 'year={twenty}')))
        self.assertIn('month', self.ids(BOOK[:-1] + ', month={January}}'))
        self.assertNotIn('month', self.ids(BOOK[:-1] + ', month=jan}'))
        self.assertIn('dateOverrides', self.ids(BOOK[:-1] + ', year=2023}'))

    def test_identifiers_and_links(self):
        for doi in ('https://doi.org/10.1234/example', 'doi:10.1234/example', '1234/no', '10.12/no', '10.1234/a b'):
            with self.subTest(doi=doi):
                self.assertIn('doi', self.ids(BOOK[:-1] + ', doi={' + doi + '}}'))
        self.assertNotIn('doi', self.ids(BOOK[:-1] + ', doi={10.1234/example_1}}'))
        for isbn in ('9780201529838', '0-201-52983-1'):
            self.assertNotIn('isbn', self.ids(BOOK[:-1] + ', isbn={' + isbn + '}}'))
        self.assertIn('isbn', self.ids(BOOK[:-1] + ', isbn={9780201529839}}'))
        self.assertIn('doiUrl', self.ids(BOOK[:-1] + ', doi={10.1234/a}, url={https://doi.org/10.1234/a}}'))
        self.assertIn('http', self.ids(BOOK[:-1] + ', url={http://example.org}}'))
        self.assertIn('url', self.ids(BOOK[:-1] + ', url={example.org}}'))

    def test_names_organizations_separators_particles_suffixes(self):
        for name, expected in [('Example Research Institute', 'organization'), ('Alice Smith; Bob Jones', 'separators'),
                               ('Alice Smith & Bob Jones', 'separators'), ('Alice Smith, Bob Jones', 'commas'),
                               ('Ludwig van Beethoven', 'particle'),
                               ('John Smith Jr.', 'suffix'), ('Smith, John, Jr., More', 'commas')]:
            with self.subTest(name=name):
                self.assertIn(expected, self.ids(BOOK.replace('Alice Smith', name)))
        for name in ('{Example Research Institute}', '{Research and Science Foundation}', 'Smith, Alice', 'Smith, Jr., John'):
            with self.subTest(name=name):
                self.assertNotIn('organization', self.ids(BOOK.replace('Alice Smith', name)))
                self.assertNotIn('suffix', self.ids(BOOK.replace('Alice Smith', name)))
        second = BOOK.replace('key,', 'second,').replace('Alice Smith', 'Smith, A.').replace('An example', 'Another title')
        self.assertIn('nameForms', self.ids(BOOK + second))
        self.assertNotIn('nameForms', self.ids(BOOK + second.replace('Smith, A.', 'Smith, Alice')))
        self.assertIn('nameForms', self.ids(BOOK.replace('Alice Smith', 'Alice Smith and\n Bob Jones') + second))

    def test_sentence_case_only_for_appropriate_styles_and_protection(self):
        title = BOOK.replace('An example', 'Work with NASA and Python')
        apa = r'\usepackage[style=apa]{biblatex}'
        self.assertIn('capitals', self.ids(title, preamble=apa))
        self.assertNotIn('capitals', self.ids(title, preamble=NUMERIC))
        protected = title.replace('NASA and Python', '{NASA} and {Python}')
        self.assertNotIn('capitals', self.ids(protected, preamble=apa))
        self.assertIn('capitals', self.ids(BOOK.replace('An example', 'NASA research'), preamble=apa))
        ieee = r'\usepackage[style=ieee]{biblatex}'
        self.assertIn('capitals', self.ids(ARTICLE.replace('An example', 'Work with NASA'), preamble=ieee))
        self.assertNotIn('capitals', self.ids(title, preamble=ieee))

    def test_special_characters_and_valid_unicode(self):
        for text in ('A & B', 'A % B', 'A_B', 'A # B', 'A \ufffd B', 'A Ã© B'):
            with self.subTest(text=text):
                self.assertTrue(self.ids(BOOK.replace('An example', text)) & {'special', 'encoding'})
        for text in (r'A \& B', r'A \% B', r'A\_B', r'A \# B', 'Études sur les océans', 'Ângela and JOÃO'):
            with self.subTest(text=text):
                self.assertFalse(self.ids(BOOK.replace('An example', text)) & {'special', 'encoding'})
        self.assertNotIn('special', self.ids(BOOK[:-1] + ', url={https://example.org/a_b%20c#d}}'))

    def test_ignored_fields_style_options_types_and_duplicate_records(self):
        self.assertIn('ignored', self.ids(BOOK[:-1] + ', abstract={Library only}}'))
        self.assertIn('disabled', self.ids(BOOK[:-1] + ', doi={10.1234/x}}', preamble=r'\usepackage[style=apa,doi=false]{biblatex}'))
        self.assertIn('miscArticle', self.ids(ARTICLE.replace('@article', '@misc')))
        self.assertIn('type', self.ids(BOOK.replace('@book', '@custom')))
        self.assertIn('duplicateEntry', self.ids(BOOK + BOOK.replace('key,', 'different,')))
        self.assertIn('duplicateEntry', self.ids(BOOK[:-1] + ',doi={10.1234/x}}' + BOOK.replace('key,', 'other,').replace('An example', 'Different title')[:-1] + ',doi={10.1234/x}}'))

    def test_inheritance_is_explicitly_partial(self):
        report = self.check('@inbook{child, crossref={parent}}')
        self.assertIn('unsupported', {f['id'] for f in report['findings']})
        self.assertNotIn('required', {f['id'] for f in report['findings']})
        self.assertIn('unsupported', self.ids('@xdata{parent, publisher={Example Press}}'))

    def test_each_finding_has_a_fix_severity_field_key_and_citations_link(self):
        report = self.check('@online{bad key, title={NASA & me}, url={http://example.org}}', preamble=r'\usepackage[style=apa]{biblatex}')
        order = ['break', 'wrong', 'advice', 'tidy']
        self.assertEqual([order.index(f['severity']) for f in report['findings']], sorted(order.index(f['severity']) for f in report['findings']))
        for finding in report['findings']:
            self.assertTrue(all(finding[field] for field in ('key', 'field', 'fix', 'severity')))
            self.assertTrue(finding['href'].startswith('citations.html#'))


@unittest.skipUnless(find_chrome(), 'no Chrome')
class PageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (ROOT / 'docs/check-references.md').read_text()
        widget = re.search(r'<div class="bibcheck"[\s\S]*?<div data-results></div>\s*</div>', source).group()
        fallback = re.search(r'<p data-bibcheck-nojs>[\s\S]*?</p>', source).group()
        def dynamic(path, query):
            if path == '/test.html':
                # Same classic deferred script as the real guide template.
                html = '<!doctype html><meta charset="utf-8">' + widget + fallback + '<script src="/bibcheck/ui.js" defer></script>'
                return html.encode(), 'text/html'
        cls.server = LocalServer(ROOT / 'site', dynamic)
        cls.browser = Chrome(find_chrome())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.server.close()

    def js(self, expression):
        return self.browser.evaluate(expression)

    def setUp(self):
        self.browser.open(self.server.url + '/test.html')
        self.wait("!document.querySelector('[data-bibcheck]').hidden")

    def wait(self, predicate):
        self.js("new Promise((resolve, reject) => { let n = 0; const poll = () => (" + predicate + ") ? resolve(true) : ++n > 200 ? reject(Error('page did not settle')) : setTimeout(poll, 10); poll(); })")

    def choose(self, files, drop=False):
        script = 'const dt = new DataTransfer();'
        for name, text in files:
            script += 'dt.items.add(new File([' + json.dumps(text) + '], ' + json.dumps(name) + '));'
        if drop:
            script += "document.querySelector('[data-drop]').dispatchEvent(new DragEvent('drop', {dataTransfer:dt,bubbles:true,cancelable:true}));"
        else:
            script += "const file = document.querySelector('input[type=file]'); file.files = dt.files; file.dispatchEvent(new Event('change'));"
        self.js('(() => {' + script + 'return true;})()')
        self.wait("!/Reading files/.test(document.querySelector('[role=status]').textContent)")

    def run_check(self):
        self.js("document.querySelector('[data-run]').click(); true")

    def text(self):
        return self.js("document.querySelector('[data-results]').textContent")

    def test_paste_results_focus_clear_and_safe_text(self):
        bib = BOOK.replace('key,', '<img/src=x/onerror=alert(1)>,')
        self.js("document.querySelector('[data-bib]').value = " + json.dumps(bib) + '; true')
        self.run_check()
        self.assertIn('<img/src=x/onerror=alert(1)>', self.text())
        self.assertFalse(self.js("Boolean(document.querySelector('[data-results] img'))"))
        self.assertTrue(self.js("document.activeElement === document.querySelector('[data-results] h3')"))
        self.js("document.querySelector('[data-clear]').click(); true")
        self.assertEqual(self.text(), '')
        self.assertEqual(self.js("document.querySelector('[data-bib]').value"), '')
        self.assertTrue(self.js("document.activeElement === document.querySelector('[data-bib]')"))

    def test_choose_and_drop_style_and_coverage(self):
        self.choose([('references.bib', BOOK), ('preamble.tex', r'\usepackage[style=apa]{biblatex}'),
                     ('chapter.tex', r'\cite{absent}')])
        self.run_check()
        self.assertIn('style: apa', self.text())
        self.assertIn('absent', self.text())
        self.assertIn('chapter.tex', self.text())
        self.choose([('replacement.tex', r'\cite{key}')], drop=True)
        self.run_check()
        self.assertNotIn('absent', self.text())
        self.assertIn('style: apa', self.text())
        self.js("document.querySelector('[data-clear]').click(); true")
        self.choose([('references.bib', BOOK)], drop=True)
        self.run_check()
        self.assertIn('style: numeric', self.text())
        self.assertIn('coverage was not checked', self.text())
        self.assertIn('No problems found', self.text())

    def test_new_input_removes_stale_results(self):
        self.choose([('references.bib', BOOK)])
        self.run_check()
        self.js("document.querySelector('[data-bib]').dispatchEvent(new Event('input')); true")
        self.assertEqual(self.text(), '')
        self.assertIn('Input changed', self.js("document.querySelector('[role=status]').textContent"))

    def test_wrong_file_type_and_empty_input(self):
        self.choose([('draft.pdf', 'not a bib file')])
        self.assertIn('Other file types', self.js("document.querySelector('[role=status]').textContent"))
        self.run_check()
        self.assertIn('Paste references.bib', self.js("document.querySelector('[role=status]').textContent"))

    def test_javascript_disabled_leaves_checklist_route(self):
        self.browser.call('Emulation.setScriptExecutionDisabled', value=True)
        try:
            self.browser.open(self.server.url + '/test.html')
            self.assertTrue(self.js("document.querySelector('[data-bibcheck]').hidden"))
            self.assertFalse(self.js("document.querySelector('[data-bibcheck-nojs]').hidden"))
            self.assertIn('checklist', self.js("document.querySelector('[data-bibcheck-nojs]').textContent"))
        finally:
            self.browser.call('Emulation.setScriptExecutionDisabled', value=False)


if __name__ == '__main__':
    unittest.main()
