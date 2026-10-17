# Settings builder

Fill in your title page details; the page writes the settings block for
`metadata.tex`.

<p class="tool-privacy"><strong>Nothing is uploaded.</strong> The form runs in your browser and saves nothing; leaving or reloading the page clears it.</p>

1. Enter your details and each committee member, with full names. Type
   plain text; `&` and `%` are handled for you.
2. Copy the block. In `metadata.tex`, replace the `\thesissetup{...}` block
   and all `\committeemember` lines with it.
3. Compile and check your title page. The form checks the settings, not
   whether the names are right; use the
   [final PDF checklist](submission.md#final-pdf-checklist).

Choose the month you graduate, not the month you submit. For math in a title,
edit the copied block ([example](going-further.md#all-thesis-settings)).

<div class="tool settings-builder" data-settings-builder hidden>
<form autocomplete="off" novalidate>
<fieldset><legend>Title page settings</legend><div data-settings-fields></div></fieldset>
<fieldset><legend>Committee</legend><p>Keep Chair or Co-Chair spelled exactly this way. Other roles may be left empty.</p><div data-settings-members></div><button class="button button-secondary" type="button" data-settings-add>Add a committee member</button></fieldset>
</form>
<p class="tool-status" role="status" aria-live="polite" data-settings-status></p>
<ul class="settings-errors" data-settings-errors></ul>
<p class="tool-label" id="settings-output-label">Block for metadata.tex</p>
<pre class="tool-output settings-output" data-settings-output data-empty="The block appears here." aria-labelledby="settings-output-label" aria-describedby="settings-paste"></pre>
<p class="tool-hint" id="settings-paste">Replace your existing settings and committee lines with this whole block.</p>
<p class="tool-actions"><button class="button" type="button" data-settings-copy disabled>Copy settings</button></p>
</div>

<p class="tool-nojs" data-settings-nojs>The form needs JavaScript, which is off or not available in this browser.
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
