# Explain my error

Paste the error, or the whole log, from Overleaf or your editor; the page
finds the first real error and says what it means and how to fix it.

<p class="tool-privacy"><strong>Nothing is uploaded.</strong> The page reads the text in your browser. Still, remove anything confidential before you paste it anywhere.</p>

<div class="tool explain" data-explain hidden><form><label for="explain-text">Paste the error or the whole log</label><textarea class="explain-input tool-drop" id="explain-text" rows="10" spellcheck="false" autocapitalize="off" autocomplete="off"></textarea><p class="tool-actions"><button type="submit" class="button">Explain the error</button></p></form><div class="explain-result tool-results tool-card" role="status" aria-live="polite"></div></div>

<p class="explain-nojs tool-nojs" data-explain-nojs>The explainer needs JavaScript, which is off or not available in this browser. Look for your message in the table below, or read the error yourself with <a href="troubleshooting.md#read-an-error-message">Read an error message</a>.</p>

## Where to copy the error from

- **Overleaf:** click **Logs and output files** beside **Recompile**. Copy the
  first error, or open **Raw logs** at the bottom of the list and copy all
  of it.
- **VS Code:** open the **Output** panel and choose **LaTeX Compiler**, then
  copy all of it. **View → Problems** lists the errors too.
- **Another editor:** copy from its log or messages panel, or open
  `main.log` (in `build/` or next to `main.tex`) and copy all of it.
- **The optional build helper:** copy what it printed after
  **First error**.

Only the first error matters: fix it and compile again, since the later ones
are often side effects. If the page does not know the message, it shows the
steps from [Read an error message](troubleshooting.md#read-an-error-message).

## Messages this page knows

The same table is used by the optional
[build helper](going-further.md#build-commands), so both give the same advice.
More messages and fixes are in [common messages](troubleshooting.md#common-messages).

<div class="explain-known" data-explain-known></div>

Still stuck? [Ask for help](troubleshooting.md#ask-for-help) with the first
error, its file, and its line number.
