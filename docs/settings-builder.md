# Settings builder

Fill in your title page details, or start from the `metadata.tex` you have;
the page writes the settings block. Type plain text: `&` and `%` are handled
for you.

<p class="tool-privacy"><strong>Nothing is uploaded.</strong> The form and any file you choose stay in your browser and clear when you leave the page.</p>

<div class="tool settings-builder" data-settings-builder hidden>
<label class="tool-drop tool-file settings-load" for="settings-load"><span class="tool-file-button" data-icon="file">Start from your metadata.tex</span> <span class="tool-file-or">or drop it here. Optional: it fills in the form, read in your browser.</span></label><input class="visually-hidden" id="settings-load" type="file" accept=".tex,text/plain" data-settings-load>
<p class="tool-file-names" data-settings-loaded aria-live="polite"></p>
<div class="settings-layout">
<form autocomplete="off" novalidate>
<fieldset><legend>Title page settings</legend><div data-settings-fields></div></fieldset>
<fieldset><legend>Committee</legend><p>Every approved member, with at least one Chair or Co-Chair.</p><div data-settings-members></div><button class="button button-secondary button-small" type="button" data-settings-add data-icon="add">Add a member</button></fieldset>
</form>
<figure class="settings-preview" data-settings-preview><label class="tool-switch"><input type="checkbox" role="switch" checked data-settings-sketch> <span>Show a sketch of the title page</span></label><figcaption>A sketch drawn from the form, for spacing and spelling. Your PDF from LaTeX is the real title page.</figcaption></figure>
</div>
<div class="tool-status" role="status" aria-live="polite" data-settings-status></div>
<ul class="settings-errors" data-settings-errors></ul>
<p class="tool-label" id="settings-output-label">Block for metadata.tex</p>
<pre class="tool-output settings-output" data-settings-output data-empty="The block appears here when the form is complete." aria-labelledby="settings-output-label" aria-describedby="settings-paste"></pre>
<p class="tool-hint" id="settings-paste">Replace your existing settings and committee lines with this whole block.</p>
<p class="tool-actions"><button class="button" type="button" data-settings-copy data-icon="copy" disabled>Copy settings</button> <button class="button button-secondary" type="button" data-settings-download data-icon="download" disabled>Download metadata.tex</button></p>
</div>

<p class="tool-nojs" data-settings-nojs>The form needs JavaScript, which is off or not available in this browser.
You can still edit <code>metadata.tex</code> using the settings table below.
Keep text inside braces, for example <code>title = {Your thesis title},</code>.</p>

## After you copy

1. In `metadata.tex`, replace the `\thesissetup{...}` block and all
   `\committeemember` lines with the copied block, or put the downloaded
   `metadata.tex` in place of the old one.
2. Compile and check your title page. The form checks the settings, not
   whether the names are right; use the
   [final PDF checklist](submission.md#final-pdf-checklist).

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
has a different name or extension, keep it: choose **Use the seal's filename** in the
form, or drop the file on it. It fills in the location, for example
`assets/RPI seal (1).jpeg`. This only copies the filename; it does not upload
or move the image. Copy the updated settings block, then compile again.

Without JavaScript, set `seal-file` in `metadata.tex` to the file's actual
location, for example `seal-file = {assets/RPI seal (1).jpeg},`. Keep the
extension that came with the image; changing `.png` to `.jpg` does not
convert it. Until the file is in that location, the title page shows a box
naming the missing file.
