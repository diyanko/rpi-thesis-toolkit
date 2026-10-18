# Make it better for everyone

Made by students, for students. A question, a tip, or a fix you found the
hard way makes it better for you and for everyone writing after you. None of
these needs LaTeX or GitHub skills, and everyone taking part follows the
[code of conduct](CODE_OF_CONDUCT.md).

<ul class="guide-list doors contribute-doors" role="list">
<li class="card help-card"><div class="help-text"><h3>Send a note</h3><p>A question, an idea, a tip, or how it went on your computer.</p><p class="kicker">About a minute, no account</p></div><p class="help-action"><a class="button" data-form href="docs/troubleshooting.md#ask-for-help">Open the form</a></p></li>
<li class="card help-card"><div class="help-text"><h3>Open an issue</h3><p>A public note the maintainer answers: a bug or a suggestion.</p><p class="kicker">Free GitHub account</p></div><p class="help-action"><a class="button button-secondary" href="https://github.com/diyanko/rpi-thesis-toolkit/issues/new/choose">Open an issue</a></p></li>
<li class="card help-card"><div class="help-text"><h3>Propose a change</h3><p>A fix to the guide or the class, prepared for review.</p><p class="kicker">With your AI assistant</p></div><p class="help-action"><a class="button button-secondary" href="#three-ways-to-help">See how</a></p></li>
</ul>

## Three ways to help

**1. Use the form (no account).** The help and feedback form, linked from
[ask for help](docs/troubleshooting.md#ask-for-help), takes questions,
suggestions, tips, and test reports. It is a full contribution: much of the
guide started as someone's question.

**2. Open an issue.** An issue is a public note on the project's
[Issues tab](https://github.com/diyanko/rpi-thesis-toolkit/issues) (free
GitHub account needed). Click **New issue** and pick **LaTeX help or bug** or
**Suggest an improvement or share a tip**. Write in your own words,
screenshots welcome, and leave out private research and personal details. The
maintainer replies on the issue and may turn it into a change.

**3. Propose a change (a pull request), ideally with your own AI assistant.** A pull request
is a proposed change the maintainer reviews before it goes in. You do not have
to know the steps: give an assistant that can edit files and use GitHub this
prompt:

```prompt
Read AGENTS.md in https://github.com/diyanko/rpi-thesis-toolkit and follow its "Contributing as an agent" steps. If you cannot fork or push, stop and show me the diff. Do not push or open the pull request until I approve. What I'd like changed: [describe it].
```

The assistant then:

1. makes a fork, your own copy of the project on GitHub;
2. makes one focused change on a branch, a named set of changes kept apart
   from the main version;
3. runs the checks and shows you the result. Nothing is posted until you
   approve.

Prefer to do it by hand? Fork, branch, make one focused change, and fill in
the short pull request template. The guide is Markdown in `docs/`; edit the
`.md` file only. If you use a terminal, `python3 scripts/verify.py` (`py`
instead of `python3` on Windows) prints a last line to paste into the pull
request, and skips checks it cannot run on your computer. Automated checks
run on every pull request anyway, and a failure is fine: the maintainer helps
finish.

Not sure how an issue should read? Ask any AI chat to help you write it, and
leave out anything private from your thesis. Never include your own thesis
files or data in an issue or pull request.

## Especially welcome

Tools and workflows that saved you time; notes for your department or field;
edge cases and their fixes; corrections to the guide; test reports from
Windows, Linux, other editors, and Overleaf; and related academic formatting
(a journal version of a chapter, defense slides, a poster) as short tips.
Interested in reviewing pull requests or helping maintain? Say so in an issue
or the form; maintainers start with [maintenance](docs/project/maintenance.md).

When your help is used, the maintainer asks whether you would like a credit on
the [credits page](CREDITS.md#people). Credit is optional. Much of this
project is drafted with AI agents; every change gets a human review, and
saying that you used AI is fine.

## What needs evidence

- **Formatting claims** cite the current OGE *Dissertation and Thesis Manual*
  or checklist: section and printed page. Start from the
  [OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation)
  and the [requirements map](docs/project/requirements.md).
- **Differences from RPI's official LaTeX template** (from RPI ITS's
  [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation))
  need a reason: a clear mistake in it, or a better match to the manual.
- **Third-party material** names its source and terms.

Not sure where a rule comes from? Open the pull request anyway and say so.

## Permission and ownership

Submit only material you are entitled to contribute. New original code and
documentation are offered under this project's [MIT license](LICENSE.md),
which does not cover RPI materials or anyone's research. Never add RPI-owned
files (the seal, the original template, manuals, checklists, or slides); link
to RPI's pages instead
([what's ours and what isn't](CREDITS.md#whats-ours-and-what-isnt)). A
published thesis or a downloadable document is not automatically reusable. No
contributor license agreement is required.

This repository is for the toolkit, not anyone's thesis. The project is
unofficial and community-made; contributions never imply RPI or OGE approval.
Publishing, or contacting OGE on the project's behalf, needs explicit
maintainer authorization.
