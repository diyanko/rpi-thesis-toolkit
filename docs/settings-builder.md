# Settings builder

Fill in your title page details to make the settings for `metadata.tex`.
Everything stays in this browser page. Nothing is uploaded or saved; leaving
or reloading the page clears what you entered.

1. Enter your details and add each committee member. Use full names. The
   block puts the chair and any co-chairs first.
2. Copy the block below. In `metadata.tex`, replace the existing
   `\thesissetup{...}` block and all `\committeemember` lines with it.
3. Save and compile `main.tex` (turn it into a PDF). Check your title page.
   The form checks settings, not whether your department or committee details
   are correct. Use the [final PDF checklist](submission.md#final-pdf-checklist).

Enter plain text. Characters such as `&` and `%` are handled for you. To put
math in your title, edit the copied block using the
[math in the title example](going-further.md#all-thesis-settings).
Choose the month you graduate, rather than the month you submit.

<div class="settings-builder" data-settings-builder hidden>
<form autocomplete="off" novalidate>
<fieldset><legend>Title page settings</legend><div data-settings-fields></div></fieldset>
<fieldset><legend>Committee</legend><p>Keep Chair or Co-Chair spelled exactly this way. Other roles may be left empty.</p><div data-settings-members></div><button class="button button-secondary" type="button" data-settings-add>Add a committee member</button></fieldset>
</form>
<p role="status" aria-live="polite" data-settings-status></p>
<ul data-settings-errors></ul>
<label for="settings-output">Block for metadata.tex</label>
<textarea id="settings-output" rows="16" readonly spellcheck="false" aria-describedby="settings-paste"></textarea>
<p id="settings-paste">Replace your existing settings and committee lines with this whole block.</p>
<button class="button" type="button" data-settings-copy disabled>Copy settings</button>
</div>

<p data-settings-nojs>The form needs JavaScript, which is off or unavailable.
You can still edit <code>metadata.tex</code> using the settings table below.
Keep text inside braces, for example <code>title = {Your thesis title},</code>.</p>

## Settings reference

Names and choices are case-sensitive. These are the same settings listed in
[Going further](going-further.md#all-thesis-settings).

{{settings-table}}

After the settings block, list one committee member per line. At least one
must be marked `Chair` or `Co-Chair`:

```latex
\committeemember[Chair]{Your committee chair}
\committeemember{Committee member two}
```

There is no fixed committee size. Check the title page when names or titles
are long.

## Add the seal

Download the seal from RPI using
[Add the RPI seal](get-started.md#add-the-rpi-seal-one-minute), then put it in
your project's `assets` folder. The seal is not included in the toolkit.

The usual name is `rpi-seal.jpg` (or `rpi-seal.png` for a PNG). If your file
has a different name or extension, keep it: select **Use the downloaded seal's
filename** in the form. It fills in the location, for example
`assets/RPI seal (1).jpeg`. This only copies the filename; it does not upload
or move the image. Copy the updated settings block, then compile again.

Without JavaScript, set `seal-file` in `metadata.tex` to the file's actual
location, for example `seal-file = {assets/RPI seal (1).jpeg},`. Keep the
extension that came with the image; changing `.png` to `.jpg` does not
convert it. Until the file is in that location, the title page shows a box
naming the missing file.
