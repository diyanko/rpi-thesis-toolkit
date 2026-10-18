# Explain my error

Paste the error, or the whole log, from Overleaf or your editor; the page
finds the first real error and says what it means and how to fix it. With a
whole log, it also lists the other errors and the warnings worth a look.

<p class="tool-privacy"><strong>Nothing is uploaded.</strong> The page reads the text or the file in your browser and saves nothing. Still, remove anything confidential before you paste it anywhere.</p>

<div class="tool explain" data-explain hidden><form><label for="explain-text">Paste the error or the whole log</label><textarea class="explain-input tool-drop" id="explain-text" rows="10" spellcheck="false" autocapitalize="off" autocomplete="off" placeholder="Paste the error or the whole log here."></textarea><label class="tool-drop tool-file explain-pick" for="explain-file" data-drop><span class="tool-file-button" data-icon="file">Choose the .log file</span> <span class="tool-file-or">or drop main.log here</span></label><input class="visually-hidden" id="explain-file" type="file" accept=".log,.txt"><p class="tool-file-names" data-file-names></p><p class="tool-actions"><button type="submit" class="button" data-icon="bulb">Explain the error</button> <button type="button" class="button button-secondary explain-clear" data-icon="clear">Clear</button></p></form><div class="explain-status tool-status" role="status" aria-live="polite"></div><div class="explain-result tool-results tool-card"></div></div>

<p class="explain-nojs tool-nojs" data-explain-nojs>The explainer needs JavaScript, which is off or not available in this browser. Look for your message under <a href="#all-messages">Show all the messages it knows</a>, or read the error yourself with <a href="troubleshooting.md#read-an-error-message">Read an error message</a>.</p>

## Where to copy the error from

- **Overleaf:** click **Logs and output files** beside **Recompile**. Copy the
  first error, or open **Raw logs** at the bottom of the list and copy all
  of it.
- **VS Code:** open the **Output** panel and choose **LaTeX Compiler**, then
  copy all of it. **View → Problems** lists the errors too.
- **Another editor:** copy from its log or messages panel, or choose
  `main.log` (in `build/` or next to `main.tex`) with **Choose the .log file**.
- **The optional build helper:** copy what it printed after
  **First error**.

Fix the first error and compile again, since the later ones are often side
effects. The page marks the part of the `l.` line that LaTeX read before it
stopped, and says where to find the file and line in VS Code and on Overleaf.
If the page does not know the message, it shows the steps from
[Read an error message](troubleshooting.md#read-an-error-message).

Under the first error, a closed list (**Also in the log**) counts the rest:
other errors, citations and references not found (with their names), lines
too wide or loosely spaced (with the file and lines), missing characters, and
notes such as **Biber has not run**. Each says what it means and links to its
fix. After a first compile, citations and references are often listed only
because the bibliography step has not run yet: compile again before you
look for typos.

## Messages this page knows

The same table is used by the optional
[build helper](going-further.md#build-commands) and by
[common messages](troubleshooting.md#common-messages), so all three give the
same advice. Common messages also covers problems that show no message, such
as a figure that moves to another page.

<details id="all-messages">
<summary>Show all the messages it knows</summary>

<div class="explain-known" data-explain-known></div>

</details>

Still stuck? [Ask for help](troubleshooting.md#ask-for-help) with the first
error, its file, and its line number.
