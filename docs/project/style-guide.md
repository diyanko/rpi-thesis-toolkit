# Writing style guide

How to write anything a student or contributor reads: the guide in `docs/`,
the front-door pages, the website, LaTeX comments, issue forms, and error
messages. When in doubt, choose the plainer sentence.

## Audience

- Readers are students at every level, from undergraduates to doctoral
  students, in every department, with any technical background.
- Write for the least technical reader first: someone who has never used a
  terminal, has never heard of LaTeX, and may not be a native English
  speaker. Short sentences, one idea each. Define a technical word (compile,
  class file, package, preamble, environment, command, repository, ZIP,
  terminal) the first time a page uses it, in a few plain words.
- Mark every terminal command as optional ("Optional:", "If you already use
  LaTeX:"), and give a route without it. Never gatekeep ("for experienced
  users", "for experts").
- Scope formatting claims: the class formats RPI graduate theses and
  dissertations to OGE's rules. The writing, citation, figure, and workflow
  help suits any student and any document, but never imply the class meets
  undergraduate or other programs' requirements.
- Let examples span disciplines: a photo, map, or drawing as well as a plot;
  a table of interview themes as well as numbers; APA, Chicago, or MLA as
  well as IEEE. Prefer swapping an example word to adding a section.

## Voice

- Plain, warm, and direct. Speak to the reader as "you".
- Help the student finish their thesis; do not sell LaTeX. Mention trade-offs
  honestly, including when Word or another route is reasonable.
- Beginner steps first, as numbered steps with one action each.
- Collapse a block (`<details>`) only when its content is (a) clearly optional
  or advanced *and* longer than about five lines, or (b) an alternative for a
  specific system, editor, or situation that most readers skip. Leave short
  content and anything most readers need visible. Never leave a section
  whose only visible content is one sentence and a toggle: show the beginner
  route and collapse only the extra detail.
- Make the summary say who it is for and what is inside, with a consistent
  prefix: "Optional: ...", "If you already use LaTeX: ...", "If you use
  Windows: ...", "If the LaTeX installation fails: ...", or "Example: ...".
  Use the clearest one; avoid gatekeeping labels such as "For experienced
  users".

  ```html
  <details><summary>Optional: convert a long draft with Pandoc</summary>

  Text in Markdown here.

  </details>
  ```

  Leave a blank line after `</summary>` and before `</details>`.
- No filler or overclaiming: avoid "simply", "just", "perfect", "guaranteed",
  "compliant", or "approved". Say what was checked and what was not.
- Neutral voice for the project: no "we", "us", "our", or "I" in
  suggestions or calls to action. Write "this guide suggests", "Suggested:",
  or "the suggested workflow", and "Share how it went through the
  [help and feedback form](../troubleshooting.md#ask-for-help)" rather than
  "tell us" or "let us know". Neutral is not cold: keep speaking warmly to
  the reader as "you". Recommendations are suggestions, not rules: give the
  benefit and when another option may suit the reader better. No invented personal
  experiences, testing history, endorsements, or quotations.
- Qualify convenience claims instead of hiding work: "the same files make the
  same PDF when both use the same TeX version", "reuse needs its own template,
  some cleanup, and a requirements check", not "format once" or "the move is
  a paste".

## Page rules

A few rules keep every page easy to read and easy to change. Follow them
before adding anything new; change the rule here, not one page, when it no
longer fits.

1. **One home per topic.** Each fact, command, or how-to is explained fully in
   one place. Everywhere else gets one sentence and a link. When you find the
   same explanation twice, keep the better one and link to it.
2. **Lead with the action.** A page's main action is a button
   (`.button`, or one `.action-rows` row per way of doing it), near the top.
   Other links stay in the text.
3. **Name a tool where it helps,** in one sentence, at the step where a
   student needs it (the Settings builder at "put your name on it", Explain
   my error where a compile fails).
4. **Fold only alternatives and depth:** a specific editor, style, system, or
   optional detail longer than about five lines goes in
   `<details><summary>If you use ...: ...</summary>`. What most readers need
   stays visible.
5. **Warm and short.** Speak student to student ("Made by students, for
   students"); one idea per sentence; cut words before adding them.
6. **Only shared parts.** Use the components in the
   [component gallery](components.md), the color tokens, and the icon set;
   no styles for one page. A new kind of part goes in the gallery and in
   `STYLED` in `scripts/ui_check.py`, which checks it looks the same on every
   page. The build rejects colors outside the tokens.
7. **Phones:** keep the home page and the tool pages short on a phone; other
   pages only need to read well there.

## Core path and supporting material

The core path is LaTeX for the RPI thesis: get the starter, compile a first
PDF, write chapters, cite, submit. Keep it first and uncluttered on every
page. Workflow advice, drafting apps, Markdown, helpers, AI, and reuse are
supporting material: one sentence and a link where a student needs it, with
the full explanation in one bounded place
([how it works: the suggested workflow](../how-it-works.md#the-suggested-workflow-and-why)).

- **Keep four things distinct,** in plain words rather than badges: what OGE
  requires (link the OGE submission page), how this toolkit implements the
  formatting, what this guide suggests for convenience, and optional external
  helpers. Never suggest that OGE recommends Markdown, any app, AI help, or
  this toolkit.
- **Drafting tools:** principle first ("draft where you and your advisor can
  work comfortably"). Then Markdown-friendly tools before Google Docs and
  Word. Name exactly four drafting apps: Obsidian (local Markdown files; a
  shared vault is not simultaneous same-file editing), HackMD (collaborative
  Markdown in the browser), Google Docs (live co-writing and comments), and
  Notion (for people already using it; block-based, with Markdown export).
  Learning Markdown is never a prerequisite. Word stays fully supported for
  existing drafts and advisor review; don't lead with it in general lists,
  never disparage it, and never present the preference as an RPI rule.
  Recommend no plugin collections, note-taking systems, or new apps just to
  start writing.
- **Tools by task:** keep the practical helper picker visible in
  [writing basics](../writing.md#helpers-for-common-tasks), with direct links
  from [How do I…?](../how-do-i.md) and the relevant writing steps. Drafting
  choices stay in How it works; review and sharing help stay in
  [Going further](../going-further.md#common-situations), and conversion help
  in [Bring your draft](../bring-your-draft.md).
  Each tool has one canonical explanation; link to it rather than repeating
  a catalog across pages.
- **Citations:** a formatted citation typed as text, a citation-manager field,
  and a portable citation key are different things; only the key in
  `references.bib` works with `\parencite` and the other citation commands.

## Terminology

| Use | Not | Notes |
| --- | --- | --- |
| thesis or dissertation | thesis (when scope matters) | Page titles and first mentions name both. Afterwards "thesis" may stand for both. |
| master's thesis | masters thesis, MS thesis | |
| doctoral dissertation | PhD thesis | Covers both PhD and DEng |
| master's, PhD, DEng | Masters, Ph.D., D.Eng. | Class options: `masters`, `doctoral`, `engineering-doctorate` |
| Office of Graduate Education (OGE) | Graduate School, grad office | Spell out once per page, then OGE |
| the manual | the OGE manual 2026 | First mention: the OGE *Dissertation and Thesis Manual*; no edition year in student pages |
| RPI Thesis Toolkit | the repo | The whole project. "The starter" means the downloadable files; "the class" means `rpi-thesis.cls`. "The template" is fine in friendly, everyday wording (it's what students search for), but never "RPI's template". |
| Overleaf | overleaf, OverLeaf | |
| your computer | locally, local machine | |
| compile | build, typeset, render | Making the PDF. `build.py` is only the script's name. |
| Biber | biber, BibTeX | Biber is the program this starter uses; BibTeX is a different one |
| `.bib` file, `references.bib` | bib, bibtex file | |
| LaTeX, pdfLaTeX, LuaLaTeX, TeX Live, MiKTeX | Latex, latex | Product names in their official spelling |

## Talking about RPI

The toolkit is unofficial and community-made. It works alongside RPI's
official resources and links to them, but it is never RPI's or OGE's own work.

| Say | Never say (about this project) |
| --- | --- |
| "works with RPI's requirements", "follows the OGE manual" | "official", "approved", "endorsed", "compliant" |
| "RPI's official LaTeX template (available from RPI ITS)" | "RPI's template" or "the RPI template" for this starter |
| "for RPI students", "RPI Thesis Toolkit" (with the **Unofficial** tag) | "the RPI thesis template", "OGE's toolkit" |
| "Download the seal from RPI's Thesis Preparation page" | anything suggesting the seal is included or ours |

Using RPI's name descriptively is fine. Never suggest that OGE reviewed,
recommended, or approved anything, and never quote or paraphrase private
advice from RPI staff as an endorsement. Link to RPI's pages instead of
copying their documents or images.

## Technical help from AI

Be encouraging about AI as a practical tool that saves time and makes LaTeX
accessible to more people, and about open, free tools and plain-text files
that keep students in control of their own work. Keep mentions practical and
optional:

- **Scope is technical help only:** explaining an error, finding a missing
  brace or wrong command, formatting a table from data the student supplies,
  turning a screenshot, photo, or sketch the student supplies into editable
  code, placing or resizing an image and fixing captions or references, converting
  an existing equation to LaTeX without changing its meaning, fixing
  bibliography syntax or citation keys from existing records, and spotting
  formatting problems. Do not write about AI for composing thesis prose,
  research, or authorship, and add no AI policy or disclosure rules.
- **Plain terms:** "AI chat" for a tool that explains and suggests; "AI
  assistant that can edit files" for one that can change files or compile;
  "AI assistant that accepts images" for one that reads screenshots or
  photos. Never "agentic" or other jargon.
- **One option among several:** list it next to web search, official
  documentation, and [asking for help](../troubleshooting.md#ask-for-help).
  Every core workflow must work without AI.
- **Inclusive:** never require a subscription, paid feature, or AI account;
  say "a tool you already have access to". No pricing, quotas, model
  rankings, or promises that an AI tool is free. Never name an AI product.
- **Helper websites:** name only the tools in the `helpers` list of
  `sources.json`, each beside its task in
  [writing basics](../writing.md#helpers-for-common-tasks); add or replace
  one only after a re-review recorded there. Present them as optional,
  independent third-party services, and favour tools whose output stays an
  editable file.
- **Conversions:** students can describe an input, desired output, operating
  system, and target example in ordinary words. Explain that some assistants
  suggest steps and some can work on supplied files. Keep the original and
  compare the output; do not call AI deterministic or promise lossless
  conversion. Link one reusable prompt rather than adding one for each format.
- **Benefits first, then a short check:** share the first error and a small
  example; try one change; compile and look; undo if it does not help. One
  line about not sharing confidential material; no long warning sections.

## Degree scope

Every page serves master's and doctoral students alike. Never write a step,
example, or heading that implies the toolkit is only for one of them. When a
step differs by degree, say so explicitly ("Doctoral students: ...").

## Formatting

- No emojis or decorative symbol characters in text (such as check-mark, cross, or star characters). Small drawn icons in the site's own style, such as the ticks in "Best if…" lists, are fine.
  The arrow → is allowed only in menu paths (**File → Download**) and step
  sequences, not as decoration.
- Callouts use GitHub syntax (`> [!TIP]`, `> [!NOTE]`, `> [!WARNING]`,
  `> [!IMPORTANT]`), at most one or two per page. Use WARNING only for a
  real risk of losing work or a rejected thesis.
- Headings in sentence case, one H1 per page. Prefer task headings ("Add a
  citation") over topic headings ("Citations").
- Link text makes sense out of context: "the OGE submission page", not
  "here" or "this link".
- Dates in prose: `14 Oct 2026`. Dates in data, file names, and BibLaTeX
  fields: ISO, `2026-10-14`.
- Student pages contain no deadlines, staff names, office hours, or tool
  version numbers. Link to the stable OGE submission page instead; deep links
  and versions live in `docs/project/sources.json` and the maintainer docs.
- State the "unofficial; not affiliated with or endorsed by RPI or OGE"
  disclaimer once each in `README.md` and `docs/submission.md`, not on every
  page. The website header carries a short **Unofficial** tag.
- Link to official documentation for third-party tools instead of describing
  menus that will change.
- Refer to code by name (macro, key, or section comment), not line number.

## Diagrams

- One standalone SVG per diagram in `docs/diagrams/`, with `<title>` and
  `<desc>` inside the file and no scripts or external fonts.
- In Markdown, give the image meaningful alt text, then a short text fallback
  directly below it, starting with *In words:*.
- The page must still make sense if the picture does not load.

## Page or section

Add a new page only for a new student task with its own goal; add it to one
of the two groups in `NAV` in `scripts/build_site.py` (Core path, Go
further), and to the matching card in `site/index.html` and list in
`README.md`. Otherwise add a section to an existing page. Each topic has
one canonical page; elsewhere, link to it instead of repeating it.

Open every page with one sentence saying who it is for and what they need
first. End it so the next step is obvious: the previous/next links follow
`NAV`, so add a closing link only when a different page is the better next step.
Every page stands alone: a student may arrive from a search engine, so link to
the exact section instead of writing "as described above" or "on the previous
page".

Direct section links need the same care: name the prerequisite, where a
snippet belongs, and the next action. Let a reader choose a route before a
large diagram or reference table; keep required steps outside disclosures.
Put optional examples and uncommon troubleshooting details behind clear
summaries.

## Copyable terminal commands

Keep commands optional and link to the route without a terminal. Before a
command, name the folder to run it from, what to replace, and the expected
output. Use one line per command and quote example file names when they can
contain spaces. Put explanations outside the copyable block, not in inline
shell comments. Check syntax against macOS, Windows, and Linux; where the
shell matters, name it and give the appropriate route. Do not assume that
redirection, comments, or line continuations behave alike in every shell.
Record which systems were actually tested rather than implying all were.

## Error messages and LaTeX comments

Name the file, say what went wrong in plain words, and give the smallest
correction: "Graduation year must have four digits. In `metadata.tex`, write
the year like 2027."
