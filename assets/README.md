# Add the RPI seal to your title page

Your title page needs RPI's seal. The seal belongs to Rensselaer Polytechnic
Institute, so it is not included in this starter: you download it yourself
from RPI. Until you do, the title page shows a box that says where the seal
goes, and the build prints a reminder. Nothing else on the page moves when
you add the seal.

## Download and save the seal

1. Open RPI ITS's
   [Thesis Preparation page](https://itssc.rpi.edu/hc/en-us/articles/360010087512-Thesis-Preparation)
   and download the current RPI seal image from it. (The sample title page in
   the OGE manual shows an older design; use the one from the Thesis
   Preparation page.)
2. Rename the file to exactly **`rpi-seal.jpg`** (all lower case, with a
   hyphen).
3. Put it in this `assets/` folder, next to this README.
4. Compile again. The seal replaces the placeholder box.

**On Overleaf:** in the file list, open the `assets` folder, click
**Upload**, choose the seal file, and rename it to `rpi-seal.jpg` if needed.
Then click **Recompile**.

**If RPI provides a PNG file:** save it as **`rpi-seal.png`** instead. The
class uses `assets/rpi-seal.png` automatically when `rpi-seal.jpg` is missing.

<details><summary>For experienced users: a different file name or folder</summary>

Set `seal-file` in `metadata.tex`, for example
`seal-file = assets/my-seal.png`. The title page prints the image 1.625 in
wide (a quarter of the text width), keeping its proportions.

</details>

## Whose file is this?

The seal is RPI's, not part of this community project, and not covered by
this project's license. Use it only on your own thesis or dissertation title
page as RPI instructs. Do not redistribute it: do not commit it to a public
repository, share it in a template, or use it as a logo. The `.gitignore`
in this starter already keeps `assets/rpi-seal.*` out of Git.
