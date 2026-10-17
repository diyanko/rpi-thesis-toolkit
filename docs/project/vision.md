# Vision

One page that every change is checked against. When a decision changes, change
it here first.

## Who it is for

Any RPI graduate student writing a thesis or dissertation, from someone who has
never opened LaTeX to someone with a finished LaTeX draft, and the people around
them: advisors, committee members, and OGE reviewers. Write for the least
technical reader first.

## The promise

**Draft anywhere, format once.** Write where you and your advisor are
comfortable (Word, Google Docs, Markdown, LaTeX). Bring the words into the
starter, and the class handles RPI's formatting. Everything a student uses here
must lead to a thesis OGE accepts; the OGE manual outranks everything else in
this project.

## Principles

1. **Practical over complete.** Ship the small thing that removes a real
   obstacle; cut anything a student would not miss.
2. **One source for each fact.** A rule lives once in the
   [requirements map](requirements.md); pages, the class, and the tools read it.
3. **Private by design.** Tools run in the browser. Nothing a student pastes or
   drops is uploaded. No accounts, no tracking beyond cookie-less page counts.
4. **Works without extras.** Every page works without JavaScript; every core
   task works without Git, a terminal, or AI.
5. **Honest.** Unofficial and community-made; never claim approval. Show real
   facts and real feedback only.
6. **Plug-and-play setup.** We suggest a local editor with a LaTeX extension
   that builds on save and shows the PDF (VS Code with LaTeX Workshop is the
   worked example; any editor with a LaTeX extension works). Overleaf is the
   easy alternative. Either way: edit, save, see the PDF. No student step
   needs terminal commands or knowing what Biber is. These are suggestions,
   not the only way.
7. **Pictures where they explain.** Hand-drawn diagrams where a picture is
   faster than words; plain, clean text everywhere else.
8. **Simple to maintain.** Small files, standard library tools, one process doc
   ([AGENTS.md](../../AGENTS.md)), tests that check real output.

## One flow for every visitor

The home page gives the message, one big-picture drawing, and three doors:
**Start**, **Tools**, **Help**. Each visitor reaches their next step in one or
two clicks.

| Visitor | First click | Then |
| --- | --- | --- |
| First-time student | Start | Overleaf or your computer, first compile |
| Draft written elsewhere | Tools: Bring your work in | Paste, convert, place into the starter |
| Already uses LaTeX | Start: use just the class | Swap the class, compile |
| Stuck on an error | Help | Explain my error, or Fixing problems |
| Advisor or OGE reviewer | Tools: Check your PDF | Reviewer checklist |
| Contributor | Footer: Contribute | The form, an issue, or the agent prompt |

## Roadmap

Tracked as [GitHub issues](https://github.com/diyanko/rpi-thesis-toolkit/issues);
this list sets the order.

1. Shorter home page with a Tools group, sharing, and current trust facts.
2. Bring your work in: pasted text and tables first; files later.
3. Explain my error, Settings builder, and a style-aware reference check.
4. Before 1.0: a student tries the starter unaided, and OGE answers the open
   questions in the requirements map.

## How we decide

Show two or three concrete options (screenshots or mockups) for anything people
will see, and pick with the maintainer. Verify, review externally, and ship in
small batches.
