# Help the next student

You do not need to be a LaTeX expert to help. A confusing sentence you
noticed, a successful install on a new computer, or a small error example is
as useful as a fix to the class file. Everyone taking part follows the
[code of conduct](CODE_OF_CONDUCT.md).

## Ways to help

No GitHub account? See
[give feedback without a GitHub account](#give-feedback-without-a-github-account).
With an account:

- **Ask a question or report a problem:** use the **LaTeX help or bug** issue
  form. Say what you tried, what happened, your editor and operating system,
  and the first error or the page that looks wrong. A small made-up example
  is better than a whole thesis; never post private research.
- **Suggest an improvement:** use the **Suggest an improvement** issue form
  for unclear instructions or missing steps.
- **Test a task:** try one thing (install, first compile, first citation) and
  tell us where you paused and what would have helped.
- **Propose a change:** open a pull request. Small is best.

When your help is used, we will ask whether you would like a credit on the
[credits page](CREDITS.md#people). Credit is optional.

## Give feedback without a GitHub account

Use the help and feedback form linked from
[ask for help](docs/troubleshooting.md#ask-for-help). It takes questions,
suggestions, problem reports, and test results, and needs no sign-in.

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

## Making changes

- The guide is Markdown in `docs/`. Edit the `.md` file only. **You do not
  need Pandoc**: the website is built automatically when you open a pull
  request.
- Keep each pull request to one coherent change, and follow the
  [style guide](docs/project/style-guide.md).
- If you can, run `python3 scripts/build.py` after changing LaTeX. If you
  cannot, say so; the automated checks will run it for you.
- Change-log entries start with a **Changes your PDF?** line.

Maintainers: start with the [maintainer handbook](docs/project/README.md).

## How reviews work

Much of this project is drafted and maintained with AI coding agents; every
change is reviewed by a human maintainer and must pass the automated checks.
The same applies to your pull request: the checks compile the sample thesis,
test the PDF, and check every link, and the maintainer reads every line.
Expect questions about evidence for formatting changes. If you used AI to
help, say so in the pull request; that is fine.

## Permission and ownership

Submit only material you are entitled to contribute. New original code and
documentation are offered under this project's [MIT license](LICENSE.md),
which does not cover RPI materials or anyone's research. Never add RPI-owned
files (the seal, the original template, manuals, checklists, or slides);
link to RPI's pages instead
([what's ours and what isn't](CREDITS.md#whats-ours-and-what-isnt)). A published thesis
or a downloadable document is not automatically reusable. No contributor
license agreement is required.

This repository is for the toolkit, not for anyone's thesis. The project is
unofficial and community-made; contributions never imply RPI or OGE
approval. Publishing, or contacting OGE on the project's behalf, needs
explicit maintainer authorization.
