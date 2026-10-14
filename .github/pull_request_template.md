## What this changes

<!-- Which student task does this improve, and what is different afterwards? -->

**Changes your PDF?** <!-- yes or no -->

**AI-assisted?** <!-- yes or no; if yes, which tool -->

## Evidence for formatting claims

<!-- For any formatting change: the OGE manual or checklist, section, and
printed page, or the comparison with RPI's official LaTeX template. Write "none" if this
change does not affect formatting. -->

## Checks

Tick what you ran. Leave the rest unticked and say why; the automated checks
run on every pull request.

- [ ] Class, formatting, or `preamble.tex`: `scripts/build.py` and
      `scripts/check.py` pass, I looked at every affected PDF page, and
      `docs/project/requirements.md` has a matching row.
- [ ] Guide or other Markdown: `scripts/build_site.py` reports no broken links.
- [ ] Website: checked at phone, laptop, and wide widths, in light and dark
      mode, with visible keyboard focus and JavaScript off.
- [ ] Scripts or CI: `scripts/package.py` and `scripts/build.py` pass.
- [ ] `CHANGELOG.md` has an entry if students will notice this change.
- [ ] No emojis, private research, personal data, local paths, or generated
      files (HTML, PDF, `build/`, `dist/`, `_local/`).
- [ ] No RPI-owned files added (seal, original template, manuals, checklists,
      slides); RPI's pages are linked instead.

## Attribution

<!-- Name any third-party material and its terms. If someone outside the
project helped, should we offer them a credit in CREDITS.md? -->
