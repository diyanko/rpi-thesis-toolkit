# Help the next student

Every contribution helps the next student finish. A confusing sentence you
noticed, a fix you found the hard way, or a test on a new computer is as
welcome as a change to the class file. You do not need to know LaTeX or
GitHub. Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md).

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

**3. Open a pull request, ideally with your own AI assistant.** A pull request
is a proposed change the maintainer reviews. You do not have to know the
steps: give an assistant that can edit files and use GitHub (such as Claude
Code or Codex) this prompt:

```text
Read AGENTS.md in https://github.com/diyanko/rpi-thesis-toolkit and follow its
"Contributing as an agent" steps. What I'd like changed: [describe it].
```

It forks the repository, makes one focused change, runs the checks, and shows
you the result; you read it before anything is posted. Prefer to do it by
hand? Fork, branch, make one focused change, and fill in the short template.
If you use a terminal, `python3 scripts/verify.py quick` (guide or website) or
`python3 scripts/verify.py` (LaTeX or scripts; `py` instead of `python3` on
Windows) gives a last line to paste into the pull request. Automated checks
run on every pull request anyway, and a failure is fine: the maintainer helps
finish. The guide is Markdown in `docs/`; edit the `.md` file only.

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
