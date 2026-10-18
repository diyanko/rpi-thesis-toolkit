#!/usr/bin/env python3
"""Synthetic bibliography and browser-control checks; no TeX compilation.

Uses the existing Chrome helper, without adding a JS runtime dependency.
Run: python3 scripts/tests/test_bibcheck.py
"""
import json
import re
import shutil
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chrome import Chrome, LocalServer
from common import ROOT, find_chrome


BOOK = '@book{key, author={Alice Smith}, title={An example}, date={2024}, publisher={Example Press}}'
ARTICLE = '@article{key, author={Alice Smith}, title={An example}, date={2024}, journaltitle={Example Journal}, volume={1}, pages={1--9}}'
NUMERIC = r'\usepackage[style=numeric]{biblatex}'

@unittest.skipUnless(find_chrome(), 'no Chrome or Chromium')
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

    def test_value_components_need_delimiters_or_concatenation(self):
        for value in ('{An} {example}', '"An" "example"', '{An}junk', 'bare words', '{An} #'):
            with self.subTest(value=value):
                self.assertIn('syntax', self.ids(BOOK.replace('{An example}', value)))
        self.assertNotIn('syntax', self.ids(BOOK.replace('{An example}', '{An} # " example"')))

    def test_reference_key_fields_keep_unescaped_underscores(self):
        for field in ('crossref', 'xref', 'xdata', 'related', 'entryset', 'ids'):
            with self.subTest(field=field):
                self.assertNotIn('special', self.ids(BOOK[:-1] + ', ' + field + '={parent_2024}}'))

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

    def test_capitalized_and_volume_citation_signatures(self):
        for command in ('Cite', 'Citeauthor', 'Textcite', 'Autocite'):
            with self.subTest(command=command):
                self.assertIn('missing', self.ids(tex=[{'text': '\\' + command + '{absent}'}]))
        for citation in (r'\volcite{3}{key}', r'\pvolcite[see]{3}[12]{key}',
                         r'\Volcite{3}{key}', r'\volcites{3}{key}{4}[12]{key}'):
            with self.subTest(citation=citation):
                self.assertEqual(self.ids(tex=[{'text': citation}], unused=True), set())

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

    def test_later_visibility_options_win(self):
        bib = BOOK[:-1] + ', doi={10.1234/x}}'
        preamble = r'\usepackage[style=numeric,doi=false]{biblatex}'
        self.assertIn('disabled', self.ids(bib, preamble=preamble))
        self.assertNotIn('disabled', self.ids(bib, preamble=preamble + r'\ExecuteBibliographyOptions{doi=true}'))
        self.assertIn('disabled', self.ids(bib, preamble=preamble + r'\ExecuteBibliographyOptions{doi=true,doi={false}}'))

    def test_math_keeps_its_own_special_characters(self):
        for title in (r'The $L_p$ space', r'The \(L_p\) space', r'The $$L_p$$ space', r'The \[L_p\] space'):
            with self.subTest(title=title):
                self.assertNotIn('special', self.ids(BOOK.replace('An example', title)))
        self.assertIn('special', self.ids(BOOK.replace('An example', r'The $L_p$ space & more')))
        self.assertIn('special', self.ids(BOOK.replace('An example', r'A \$5 price & more')))

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
            self.assertTrue(all(finding[field] for field in ('key', 'field', 'fix', 'severity', 'guide')))
            self.assertRegex(finding['href'], r'^(citations|check-references)\.html#')

    def test_guide_links_point_at_existing_sections(self):
        guides = self.browser.evaluate('api.RULES.guides')
        for name, (href, text) in guides.items():
            with self.subTest(guide=name):
                page, anchor = href.split('#')
                source = (ROOT / 'docs' / page.replace('.html', '.md')).read_text()
                self.assertTrue('id="' + anchor + '"' in source or self.heading_id(source, anchor), href)
                self.assertTrue(text)

    @staticmethod
    def heading_id(source, anchor):
        for line in source.splitlines():
            if line.startswith('#'):
                slug = re.sub(r'[^a-z0-9 -]', '', line.lstrip('#').strip().lower()).replace(' ', '-')
                if slug == anchor:
                    return True
        return False

    def test_findings_name_their_line_and_the_other_entry(self):
        bib = BOOK + '\n\n' + BOOK.replace('Alice Smith', 'Bob Jones').replace('An example', 'Other')
        duplicate = next(f for f in self.check(bib)['findings'] if f['id'] == 'duplicate')
        self.assertEqual(duplicate['line'], 3)
        self.assertEqual(duplicate['related']['line'], 1)
        self.assertEqual(bib[duplicate['start']:duplicate['start'] + 5], '@book')
        self.assertEqual(bib[duplicate['related']['start']:duplicate['related']['end']], BOOK)
        # A field finding points at the field itself.
        special = next(f for f in self.check(BOOK.replace('An example', 'A & B'))['findings'] if f['id'] == 'special')
        self.assertTrue(BOOK.replace('An example', 'A & B')[special['start']:special['end']].startswith('title='))
        self.assertEqual(special['entry']['line'], 1)

    def test_one_unclosed_entry_does_not_hide_the_next(self):
        bib = '@book{first, title={Open, date={2020}, publisher={P}\n\n@book{second, author={A B}, date={2021}}\n'
        report = self.check(bib)
        syntax = [f for f in report['findings'] if f['id'] == 'syntax']
        self.assertEqual(len(syntax), 1)
        self.assertEqual((syntax[0]['key'], syntax[0]['line']), ('first', 1))
        self.assertIn('line 3', syntax[0]['fix'])
        self.assertEqual(report['entries'], 2)
        # The second entry is still checked on its own: it has no title.
        self.assertIn(('second', 'title'), {(f['key'], f['field']) for f in report['findings'] if f['id'] == 'required'})
        # The broken entry gets no missing-field claims.
        self.assertNotIn('first', {f['key'] for f in report['findings'] if f['id'] == 'required'})
        self.assertIn('extra closing brace', ' '.join(f['fix'] for f in self.check('@book{k, title={T}}, date={2020}}')['findings']))

    def fixed(self, bib, **options):
        """Apply every offered fix once; return (fixes, new text)."""
        report = self.check(bib, **options)
        fixes = [f['edit'] for f in report['findings'] if f.get('edit')]
        result = self.browser.evaluate('api.applyFixes(' + json.dumps(bib) + ', ' + json.dumps(fixes) + ')')
        return fixes, result['text']

    def test_safe_fixes_change_only_what_they_show(self):
        cases = [
            (BOOK.replace('An example', 'Fish & chips, 50% off_now #1'), 'special', 'title={Fish \\& chips, 50\\% off\\_now \\#1}'),
            (BOOK.replace('An example', r'The $L_p$ & more'), 'special', r'title={The $L_p$ \& more}'),
            (BOOK[:-1] + ', doi={https://doi.org/10.1234/a.b}}', 'doi', 'doi={10.1234/a.b}'),
            (BOOK[:-1] + ', doi="doi:10.1234/x"}', 'doi', 'doi="10.1234/x"'),
            (BOOK[:-1] + ', month={January}}', 'month', 'month={1}'),
            (BOOK[:-1] + ', month={Sept.}}', 'month', 'month={9}'),
            (BOOK.replace('date={2024}', 'year={2024-05-01}'), 'year', 'date={2024-05-01}'),
            (BOOK.replace(', date=', ' date='), 'syntax', 'title={An example}, date={2024}'),
        ]
        for bib, kind, expected in cases:
            with self.subTest(bib=bib):
                fixes, text = self.fixed(bib)
                self.assertEqual(len(fixes), 1)
                self.assertIn(expected, text)
                self.assertNotIn(kind, self.ids(text))
                self.assertTrue(fixes[0]['before'] and fixes[0]['after'] and fixes[0]['label'])
                self.assertTrue(text.startswith('@book{key,'))

    def test_uncertain_points_stay_advice(self):
        for bib in (BOOK.replace('Alice Smith', 'Alice Smith & Bob Jones'),             # a separator or a company
                    BOOK[:-1] + ', note={See \\url{https://x.org/?a=1&b=2}}}',         # a link keeps its characters
                    BOOK[:-1] + ', url={http://example.org}}',                           # https is not always available
                    BOOK[:-1] + ', doi={https://doi.org/10.1234%2Fx}}',                  # an encoded DOI
                    BOOK[:-1] + ', month={Spring}}',
                    BOOK.replace('date={2024}', 'year={2024-05-01}, date={2024}'),       # date already set
                    BOOK.replace('{An example}', '{A & B} # " more"'),                      # a joined value
                    BOOK.replace('key,', 'bad key,'),                                    # keys never change
                    BOOK.replace('Alice Smith', 'Example Research Institute'),
                    BOOK[:-1] + ', note={See \\ref{sec:method_v2}}}'):                 # a command's argument keeps its _
            with self.subTest(bib=bib):
                self.assertEqual(self.fixed(bib)[0], [])

    def test_apply_fixes_skips_overlaps_and_stale_text(self):
        bib = BOOK.replace('An example', 'A & B')
        fix = next(f['edit'] for f in self.check(bib)['findings'] if f.get('edit'))
        result = self.browser.evaluate('api.applyFixes(' + json.dumps(bib) + ', ' + json.dumps([fix, fix]) + ')')
        self.assertEqual(result['applied'], 1)
        self.assertEqual(self.browser.evaluate('api.applyFixes("changed", ' + json.dumps([fix]) + ').applied'), 0)

    def test_several_files_keep_their_names_and_lines(self):
        files = [{'name': 'a.bib', 'text': BOOK + '\n'}, {'name': 'b.bib', 'text': '\r\n' + BOOK.replace('An example', 'A & B')}]
        joined = self.browser.evaluate('api.joinSources(' + json.dumps(files) + ')')
        special = next(f for f in self.check(joined)['findings'] if f['id'] == 'special')
        self.assertEqual(self.browser.evaluate('api.sourceLine(' + json.dumps(joined) + ', ' + str(special['line']) + ')'), {'name': 'b.bib', 'line': 2})
        parts = self.browser.evaluate('api.splitSources(' + json.dumps(joined) + ')')
        self.assertEqual([p['name'] for p in parts], ['a.bib', 'b.bib'])
        self.assertEqual(parts[1]['text'], '\n' + BOOK.replace('An example', 'A & B') + '\n')
        self.assertEqual(self.browser.evaluate('api.joinSources([{name: "x.bib", text: "abc"}])'), 'abc')

    def test_inline_code_is_not_a_citation_and_lines_are_kept(self):
        tex = 'Text \\verb|\\cite{ghost}| and \\verb*+50% \\cite{ghost2}+ then \\cite{key}.\n\\lstinline!\\cite{ghost3}!\n\\begin{verbatim}\n\\cite{ghost4}\n\\end{verbatim}\n\\cite{absent}'
        missing = [f for f in self.check(tex=[{'name': 'ch.tex', 'text': tex}])['findings'] if f['id'] == 'missing']
        self.assertEqual([(f['key'], f['file'], f['line']) for f in missing], [('absent', 'ch.tex', 6)])
        self.assertIn('ghost', {f['key'] for f in self.check(tex=[{'text': '\\cite{ghost} \\verb|x|'}])['findings']})


@unittest.skipUnless(find_chrome(), 'no Chrome or Chromium')
class PageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (ROOT / 'docs/check-references.md').read_text()
        widget = re.search(r'<div class="[^"]*\bbibcheck"[\s\S]*?<div [^>]*data-results></div>\s*</div>', source).group()
        fallback = re.search(r'<p [^>]*data-bibcheck-nojs>[\s\S]*?</p>', source).group()
        def dynamic(path, query):
            if path == '/test.html':
                # Same classic deferred script as the real guide template.
                html = '<!doctype html><meta charset="utf-8">' + widget + fallback + '<script src="/tools-highlight.js" defer></script><script src="/bibcheck/ui.js" defer></script>'
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
        # A check shows the working state first, then its results.
        self.wait("document.querySelector('[role=status]').getAttribute('data-state') !== 'working'")

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
        self.assertIn('Looks fine', self.text())

    def test_new_input_removes_stale_results(self):
        self.choose([('references.bib', BOOK)])
        self.run_check()
        self.js("document.querySelector('[data-bib]').dispatchEvent(new Event('input')); true")
        self.assertEqual(self.text(), '')
        self.assertIn('Input changed', self.js("document.querySelector('[role=status]').textContent"))

    def test_wrong_file_type_and_empty_input(self):
        self.choose([('draft.pdf', 'not a bib file')])
        self.assertIn('Choose .bib and .tex files', self.js("document.querySelector('[role=status]').textContent"))
        self.run_check()
        self.assertIn('Paste references.bib', self.js("document.querySelector('[role=status]').textContent"))

    def paste(self, bib):
        self.js("document.querySelector('[data-bib]').value = " + json.dumps(bib) + '; true')

    def status(self):
        return self.js("document.querySelector('[role=status]').textContent")

    def test_line_control_selects_the_entry_in_the_box(self):
        filler = '\n'.join('% filler line ' + str(n) for n in range(80))
        bib = BOOK + '\n' + filler + '\n' + BOOK.replace('Alice Smith', 'Bob Jones').replace('An example', 'Other')
        self.paste(bib)
        self.run_check()
        self.assertIn('line 82', self.text())
        self.js("document.querySelector('[data-results] .bibcheck-line').click(); true")
        self.assertTrue(self.js("document.activeElement === document.querySelector('[data-bib]')"))
        start = self.js("document.querySelector('[data-bib]').selectionStart")
        end = self.js("document.querySelector('[data-bib]').selectionEnd")
        self.assertEqual(bib[start:end], BOOK.replace('Alice Smith', 'Bob Jones').replace('An example', 'Other'))
        self.assertGreater(self.js("document.querySelector('[data-bib]').scrollTop"), 0)
        # The control is a real button with a name that includes its text.
        self.assertEqual(self.js("document.querySelector('.bibcheck-line').tagName"), 'BUTTON')
        self.assertIn('line 82', self.js("document.querySelector('.bibcheck-line').getAttribute('aria-label')"))

    def test_fix_one_fix_all_download_and_undo(self):
        bib = BOOK.replace('An example', 'A & B')[:-1] + ', month={March}, doi={doi:10.1234/x}}'
        self.paste(bib)
        self.run_check()
        self.assertIn('title = {A \\& B}', self.text())
        self.assertEqual(self.js("document.querySelectorAll('[data-fix]').length"), 3)
        self.js("document.querySelector('[data-fix]').click(); true")
        self.assertEqual(self.js("document.querySelectorAll('[data-fix]').length"), 2)
        self.assertTrue(self.js("document.activeElement.hasAttribute('data-fix')"))
        self.assertIn('Fixed in key', self.status())
        self.js("document.querySelector('[data-fix-all]').click(); true")
        box = self.js("document.querySelector('[data-bib]').value")
        self.assertIn('month={3}', box)
        self.assertIn('doi={10.1234/x}', box)
        self.assertIn(r'title={A \& B}', box)
        self.assertEqual(self.js("document.querySelectorAll('[data-fix]').length"), 0)
        self.assertTrue(self.js("document.activeElement.hasAttribute('data-download')"))
        self.assertIn('Download references.bib', self.text())
        saved = self.js("""new Promise(resolve => {
            const make = URL.createObjectURL;
            URL.createObjectURL = blob => { blob.text().then(resolve); return make(blob); };
            HTMLAnchorElement.prototype.click = function () { window.savedName = this.download; };
            document.querySelector('[data-download]').click();
        })""")
        self.assertEqual(saved, box)
        self.assertEqual(self.js('window.savedName'), 'references.bib')
        self.js("document.querySelector('[data-undo]').click(); true")
        self.assertEqual(self.js("document.querySelector('[data-bib]').value"), bib)
        self.assertEqual(self.js("document.querySelectorAll('[data-fix]').length"), 3)

    def test_several_files_name_the_file_and_download_each(self):
        self.choose([('a.bib', BOOK + '\n'), ('b.bib', BOOK.replace('key,', 'other,').replace('An example', 'C & D'))])
        self.assertIn('% From the file b.bib', self.js("document.querySelector('[data-bib]').value"))
        self.run_check()
        self.assertIn('b.bib, line 1', self.text())
        self.js("document.querySelector('[data-fix-all]').click(); true")
        self.assertEqual(self.js("[...document.querySelectorAll('[data-download]')].map(b => b.textContent)"), ['Download b.bib'])

    def test_by_entry_view_groups_points_under_each_entry(self):
        self.paste(BOOK.replace('An example', 'A & B')[:-1] + ', month={Spring}}\n' + BOOK.replace('key,', 'second,').replace('date={2024}', 'date={May 2024}'))
        self.run_check()
        self.js("document.querySelector('input[value=entry]').click(); true")
        headings = self.js("[...document.querySelectorAll('[data-groups] h4')].map(h => h.textContent)")
        self.assertEqual(headings, ['key (line 1)', 'second (line 2)'])
        self.assertIn('May print wrong', self.text())
        self.js("document.querySelector('input[value=severity]').click(); true")
        self.assertIn('May print wrong (', self.js("document.querySelector('[data-groups] h4').textContent"))

    def test_javascript_disabled_leaves_checklist_route(self):
        self.browser.call('Emulation.setScriptExecutionDisabled', value=True)
        try:
            self.browser.open(self.server.url + '/test.html')
            self.assertTrue(self.js("document.querySelector('[data-bibcheck]').hidden"))
            self.assertFalse(self.js("document.querySelector('[data-bibcheck-nojs]').hidden"))
            self.assertIn('checklist', self.js("document.querySelector('[data-bibcheck-nojs]').textContent"))
        finally:
            self.browser.call('Emulation.setScriptExecutionDisabled', value=False)


class OfflineGuide(unittest.TestCase):
    @unittest.skipUnless(shutil.which('pandoc'), 'no Pandoc')
    def test_offline_render_replaces_controls_with_online_route_and_checklist(self):
        import build_site
        site = build_site.Site(offline=True)
        html = site.render('docs/check-references.md')
        self.assertEqual(site.errors, [])
        self.assertIn(site.site_url + '/guide/check-references.html', html)
        self.assertNotIn('data-bibcheck hidden', html)
        self.assertNotIn('bibcheck/ui.js', html)
        self.assertNotIn('bibcheck-interactive-start', html)
        self.assertIn('checklist below', html)
        self.assertIn('Checklist without JavaScript', html)


if __name__ == '__main__':
    unittest.main()
