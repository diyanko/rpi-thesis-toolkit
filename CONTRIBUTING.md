# Help the next student

Every contribution helps the next student finish, and there is no wrong way
to start. A confusing sentence you noticed, a fix you found the hard way, or
a test on a new computer is as welcome as a change to the class file. You do
not need to know LaTeX or GitHub well. Everyone taking part follows the
[code of conduct](CODE_OF_CONDUCT.md).

## Pick the way that suits you

### No GitHub: use the form

Use the help and feedback form linked from
[ask for help](docs/troubleshooting.md#ask-for-help). It needs no account
and takes questions, suggestions, tips, and test reports. This is a full
contribution, not a lesser one: much of the guide started as someone's
question.

### Open an issue

An *issue* is a public note on the project's GitHub page: a question, a
problem, or an idea that anyone can read and reply to. If you have never
opened one:

1. Create a free account at [github.com/signup](https://github.com/signup).
2. Open the project's
   [Issues tab](https://github.com/diyanko/rpi-thesis-toolkit/issues).
3. Click **New issue**.
4. Choose a form: **LaTeX help or bug**, **Suggest an improvement**, or
   **Share a tip, tool, or workflow**.
5. Write in your own words. Screenshots are welcome: paste or drag them into
   a text box. Leave out private research and personal details.

What happens next: the maintainer replies on the issue, may ask a question
or two, and may turn your note into a change to the guide or the starter.

### Open a pull request

A *pull request* is a proposed change to the project's files that the
maintainer reviews and then adds. Pull requests are welcome from anyone.
Built your change with an AI assistant? That's welcome too.

1. Fork (make your own copy of) the repository, then make a branch for
   your change.
2. Make one focused change.
3. Optional: if you use a terminal, check it with `python3 scripts/build.py`
   after changing LaTeX, or `python3 scripts/build_site.py` after changing
   the guide. If you cannot, say so; the automated checks run anyway.
4. Open the pull request and fill in the short template.

New to forks and pull requests? GitHub's
[guide to contributing to a project](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project)
walks through each step.

Good to know:

- **Automated checks run on every pull request.** They compile the sample
  thesis, test the PDF, and check every link. Don't worry if one fails: the
  maintainer will help you finish.
- **Small pull requests are easiest to review.** One change at a time.
- **Formatting changes need a source** in the OGE *Dissertation and Thesis
  Manual* or a checklist (see [what needs evidence](#what-needs-evidence)).
- **The guide is Markdown in `docs/`.** Edit the `.md` file only. You do not
  need Pandoc; the website is built automatically.

### Let an AI assistant handle the GitHub steps

Not sure how issues or pull requests work? An AI chat or an AI assistant
that can edit files can do most of the steps with you. Many coding
assistants read this repository's [`AGENTS.md`](AGENTS.md) automatically,
which tells them the project's rules and checks. You stay in charge: read
what it prepared before anything is posted.

To write an issue or a tip (any AI chat, nothing to install):

```text
Help me write a short GitHub issue for the RPI Thesis Toolkit
(https://github.com/diyanko/rpi-thesis-toolkit). Here is what happened, or
my idea: [describe it]. Tell me which form to pick (LaTeX help, Suggestion,
or Share a tip), and write a title and text in plain language. Leave out
anything private from my thesis.
```

To prepare a pull request (an AI assistant that can edit files and use
GitHub):

```text
I want to contribute to https://github.com/diyanko/rpi-thesis-toolkit.
First read AGENTS.md and CONTRIBUTING.md and follow them. My change:
[describe it]. Fork the repository if needed, make one small change on a new
branch, and run the checks AGENTS.md lists for that kind of change if you
can. Show me the changes and the check results, and wait for my OK before
pushing. Then open a pull request with the template and mark it AI-assisted.
```

Keep it to one change, never include your own thesis files or data, and say
so in the pull request if a check failed. The maintainer reviews every
pull request and will help finish it.

## Especially welcome

- Tools and workflows that saved you time
- Notes and examples for your department or field
- Edge cases you hit, and how you fixed them
- Tips and tricks for formatting
- Corrections to the guide: a wrong step, a broken link, a confusing sentence
- Test reports from Windows, Linux, other editors, and Overleaf

## Beyond the thesis

The RPI thesis or dissertation in LaTeX stays the core. Related academic
formatting is welcome too: a journal or conference version of a chapter,
slides for a defense, or a poster. Share these as tips or short recipes, and
the maintainer will link them from the relevant [workflow](docs/workflows.md).
Keep them short and practical.

## Helping maintain

Interested in reviewing pull requests, answering questions, or helping
maintain the toolkit? You are welcome. Open an issue with the
**Suggest an improvement** form, or use the form linked from
[ask for help](docs/troubleshooting.md#ask-for-help), and say what you would
like to help with. Maintainers: start with the
[maintainer handbook](docs/project/README.md).

## How reviews work

Much of this project is drafted and maintained with AI coding agents; every
change is reviewed by a human maintainer and must pass the automated checks.
Your pull request gets the same: the checks run, and the maintainer reads
every line and helps you finish. If you used AI to help, you can say so in
the pull request; that is fine.

When your help is used, the maintainer asks whether you would like a credit
on the [credits page](CREDITS.md#people). Credit is optional.

## What needs evidence

- **Formatting claims** cite the current OGE *Dissertation and Thesis Manual*
  or checklist: section and printed page. Start from the
  [OGE submission page](https://graduate.rpi.edu/academic-progress/submit-your-thesis-dissertation)
  and see the [requirements map](docs/project/requirements.md).
- **Differences from RPI's official LaTeX template** (available from RPI
  ITS's [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation))
  need a reason: a clear mistake in that template, or a better match to the
  manual.
- **Third-party material** names its source and terms.

Not sure where a rule comes from? Open the pull request anyway and say so;
the maintainer can help find it.

## Permission and ownership

Submit only material you are entitled to contribute. New original code and
documentation are offered under this project's [MIT license](LICENSE.md),
which does not cover RPI materials or anyone's research. Never add RPI-owned
files (the seal, the original template, manuals, checklists, or slides);
link to RPI's pages instead
([what's ours and what isn't](CREDITS.md#whats-ours-and-what-isnt)). A
published thesis or a downloadable document is not automatically reusable.
No contributor license agreement is required.

This repository is for the toolkit, not for anyone's thesis. The project is
unofficial and community-made; contributions never imply RPI or OGE
approval. Publishing, or contacting OGE on the project's behalf, needs
explicit maintainer authorization.
