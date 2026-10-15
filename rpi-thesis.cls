% rpi-thesis.cls: the formatting for an RPI master's thesis or doctoral
% dissertation. You normally never edit this file: your words go in chapters/,
% your details in metadata.tex, and extra packages in preamble.tex.
%
% Unofficial community class; not affiliated with or endorsed by RPI or OGE.
% Copyright (c) 2026 Diyanko Bhowmik and contributors. See LICENSE.md.
%
% For reviewers, including OGE staff: the class is the standard report class
% plus only what RPI's rules require. Each section below names the part of
% the Dissertation and Thesis Manual (2026) it follows; to adjust a rule,
% change only that section. docs/project/requirements.md maps every rule to
% its source and to how it is tested.
%
% What is in this file:
%    1. Identity and options          8. Page numbers
%    2. Fonts                         9. Appendices
%    3. Packages                     10. Your thesis settings (metadata.tex)
%    4. Page layout and spacing      11. Title page and seal
%    5. Headings                     12. Commands for main.tex
%    6. Contents and lists           13. Links and PDF properties
%    7. Captions and floats

% ---------------------------------------------------------------------------
% 1. Identity and options
% ---------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{rpi-thesis}[2026/10/15 v0.3.0 RPI community thesis starter]
% Settings live in metadata.tex, so the class takes no options.
\DeclareOption*{\ClassError{rpi-thesis}{Unsupported class option: \CurrentOption}
  {Use metadata.tex for settings. This starter uses 12pt, letterpaper, oneside.}}
\ProcessOptions\relax
\LoadClass[12pt,letterpaper,oneside]{report}

% ---------------------------------------------------------------------------
% 2. Fonts: Times-style text and math at 12 pt (manual 2.1, p. 16).
%    pdfLaTeX (the default) or, for Unicode input, LuaLaTeX and XeLaTeX.
% ---------------------------------------------------------------------------
\RequirePackage{iftex}
\ifPDFTeX
  \RequirePackage[T1]{fontenc}
  \RequirePackage{newtxtext,newtxmath}
  % newtxmath defines \openbox, which amsthm defines again. Clear it only if
  % amsthm is loaded later, so \usepackage{amsthm} in preamble.tex just works.
  \AddToHook{package/amsthm/before}{\let\openbox\relax}
  % newtxmath provides the AMS commands. Avoid redefinitions if a student
  % pastes \usepackage{amssymb} or \usepackage{amsfonts} into preamble.tex.
  \@namedef{ver@amssymb.sty}{2013/01/14 v3.01 (symbols provided by rpi-thesis)}
  \@namedef{ver@amsfonts.sty}{2013/01/14 v3.01 (symbols provided by rpi-thesis)}
\else
  % Establish conventional AMS command names before unicode-math replaces
  % their Unicode equivalents; it does not define every traditional alias.
  \RequirePackage{amssymb}
  \RequirePackage{fontspec}
  % Load the files from the TeX distribution; do not depend on OS font discovery.
  \setmainfont{texgyretermes}[
    Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,
    ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
  \RequirePackage{unicode-math}
  \setmathfont{texgyretermes-math.otf}
\fi

% ---------------------------------------------------------------------------
% 3. Packages every thesis uses. Add your own in preamble.tex.
% ---------------------------------------------------------------------------
\RequirePackage{etoolbox}    % hooks used below
\RequirePackage{graphicx}    % \includegraphics
\RequirePackage{amsmath}     % equations
\RequirePackage{booktabs}    % \toprule, \midrule, \bottomrule
\RequirePackage{url}         % \url
\RequirePackage{setspace}    % double and single spacing
\RequirePackage{titlesec}    % section 5
\RequirePackage[titles]{tocloft}  % section 6
\RequirePackage{caption}     % section 7

% ---------------------------------------------------------------------------
% 4. Page layout and spacing: 1 in margins (manual 2.2, p. 16); double-
%    spaced text, single-spaced quotations, captions, tables, and figures
%    (manual 2.1, p. 16).
% ---------------------------------------------------------------------------
% Page numbers sit 0.75 in from the page edge (footer and header baselines).
\RequirePackage[margin=1in,footskip=0.25in,headheight=12pt,headsep=0.25in]
  {geometry}
\AtBeginDocument{\doublespacing\pagestyle{plain}}
\setlength{\parindent}{0.4in}
\raggedbottom
\AtBeginEnvironment{quote}{\singlespacing}
\AtBeginEnvironment{quotation}{\singlespacing}
% Space around displayed equations grows with the line spacing.
\everydisplay\expandafter{\the\everydisplay
  \abovedisplayskip\baselinestretch\abovedisplayskip
  \belowdisplayskip\abovedisplayskip
  \abovedisplayshortskip\baselinestretch\abovedisplayshortskip
  \belowdisplayshortskip\baselinestretch\belowdisplayshortskip}
% Footnotes are numbered through the whole document, not per chapter.
\counterwithout{footnote}{chapter}
% URLs in the text font: one font throughout (OGE checklist).
\urlstyle{same}
% Reference lists are left-aligned, so long URLs do not stretch the spacing.
\AtEndPreamble{\@ifpackageloaded{biblatex}{\appto\bibsetup{\raggedright}}{}}

% ---------------------------------------------------------------------------
% 5. Headings (manual 2.3, pp. 17-18), following RPI's original thesis.cls:
%    large bold centered chapter titles numbered "1. TITLE", and the same
%    style for CONTENTS, the lists, front-matter sections, and REFERENCES.
% ---------------------------------------------------------------------------
% The space before a chapter title cancels the empty first line that
% otherwise pushes it below the 1 in margin (OGE's LaTeX tips sheet calls
% this a known glitch of the original class).
\titleformat{\chapter}[hang]
  {\vskip-\baselinestretch\dimexpr18pt\relax\centering\normalfont\large\bfseries}
  {\thechapter.}{0.4em}{}
\titlespacing*{\chapter}{0pt}{0pt}{15pt}
\titleformat{\section}{\normalfont\large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\normalsize\bfseries}{\thesubsection}{1em}{}
% Level 4 is italic, so that every heading level looks different (OGE manual).
\titleformat{\subsubsection}{\normalfont\normalsize\itshape}{\thesubsubsection}{1em}{}
\titlespacing*{\section}{0pt}{3.5ex plus 1ex minus .2ex}{.5ex plus .3ex}
\titlespacing*{\subsection}{0pt}{3.25ex plus 1ex minus .2ex}{.3ex plus .2ex}
\titlespacing*{\subsubsection}{0pt}{3.25ex plus 1ex minus .2ex}{.2ex plus .1ex}
\setcounter{secnumdepth}{3}
% Names printed by LaTeX, in capitals as on RPI's sample pages.
\renewcommand{\contentsname}{CONTENTS}
\renewcommand{\listtablename}{LIST OF TABLES}
\renewcommand{\listfigurename}{LIST OF FIGURES}
\renewcommand{\bibname}{REFERENCES}
\renewcommand{\appendixname}{APPENDIX}
\renewcommand{\abstractname}{ABSTRACT}
\newcommand{\appendicesname}{APPENDICES}
\newcommand{\referencesname}{REFERENCES}   % used by \thesisreferences

% ---------------------------------------------------------------------------
% 6. Contents and lists of tables and figures (manual 1.3-1.5, pp. 4-10)
% ---------------------------------------------------------------------------
\setcounter{tocdepth}{3}
\renewcommand{\cftchapfont}{\normalfont}
\renewcommand{\cftchappagefont}{\normalfont}
\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}
% Entries read exactly like the body headings: "1." and "A.".
\renewcommand{\cftchapaftersnum}{.}
\setlength{\cftbeforechapskip}{10pt}
\setlength{\cftbeforesecskip}{6pt}
\setlength{\cftbeforesubsecskip}{4pt}
\setlength{\cftbeforesubsubsecskip}{3pt}
\setlength{\cftbeforefigskip}{10pt}
\setlength{\cftbeforetabskip}{10pt}
\cftsetpnumwidth{3em}
% Number columns wide enough for 12.10, 12.10.10, and 12.10.10.10, so entry
% text never runs into the number column.
\cftsetindents{fig}{0em}{2.8em}
\cftsetindents{tab}{0em}{2.8em}
\cftsetindents{chap}{0em}{1.6em}
\cftsetindents{sec}{1.5em}{2.8em}
\cftsetindents{subsec}{4.3em}{3.8em}
\cftsetindents{subsubsec}{8.1em}{5em}
\cftsetrmarg{4em}

% ---------------------------------------------------------------------------
% 7. Captions and floats (manual 2.4-2.5, pp. 18-22): bold captions, tables
%    captioned above and figures below, both single-spaced.
% ---------------------------------------------------------------------------
\captionsetup{format=hang,font={normalfont,bf},labelfont=bf,labelsep=colon,
  justification=raggedright,singlelinecheck=false}
\captionsetup[table]{position=top}
\AtBeginEnvironment{figure}{\singlespacing}
\AtBeginEnvironment{table}{\singlespacing}
\AtBeginEnvironment{longtable}{\singlespacing}
\AtBeginEnvironment{sidewaysfigure}{\singlespacing}
\AtBeginEnvironment{sidewaystable}{\singlespacing}
% Let floats fill more of a page, so fewer drift away from their text.
\setcounter{topnumber}{2}
\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{4}
\renewcommand{\topfraction}{.8}
\renewcommand{\bottomfraction}{.8}
\renewcommand{\textfraction}{.2}
\renewcommand{\floatpagefraction}{.8}

% ---------------------------------------------------------------------------
% 8. Page numbers (manual 2.2, pp. 16-17): roman (i, ii, ...) in the front
%    matter, arabic from chapter 1, 0.75 in from the page edge. Body pages:
%    top right. Front matter and the first page of every chapter, the
%    references, and each appendix: bottom center (plain).
% ---------------------------------------------------------------------------
\newcommand{\ps@rpibody}{\let\@mkboth\@gobbletwo
  \renewcommand{\@oddhead}{\hfil\normalfont\thepage}%
  \renewcommand{\@evenhead}{\@oddhead}%
  \renewcommand{\@oddfoot}{}\renewcommand{\@evenfoot}{}}

% ---------------------------------------------------------------------------
% 9. Appendices: lettered like chapters ("A. TITLE"), with one APPENDICES
%    line in the contents, written on the first appendix page so it carries
%    that page number (manual 1.3, p. 4).
% ---------------------------------------------------------------------------
\newif\ifrpi@appendixline
\appto\appendix{\global\rpi@appendixlinetrue}
\pretocmd{\chapter}{\ifrpi@appendixline
    \global\rpi@appendixlinefalse\clearpage\phantomsection
    \addcontentsline{toc}{chapter}{\appendicesname}\fi}{}
  {\ClassError{rpi-thesis}{Could not set up appendices}{}}

% ---------------------------------------------------------------------------
% 10. Your thesis settings: \thesissetup{...} and \committeemember in
%     metadata.tex. Every key is listed in docs/advanced.md.
% ---------------------------------------------------------------------------
\ExplSyntaxOn
\tl_new:N \g_rpi_title_tl
\tl_new:N \g_rpi_author_tl
\tl_new:N \g_rpi_degree_tl
\tl_new:N \g_rpi_department_tl
\tl_new:N \g_rpi_month_tl
\tl_new:N \g_rpi_year_tl
\tl_new:N \g_rpi_seal_tl
\bool_new:N \g_rpi_copyright_bool
\bool_new:N \g_rpi_tables_bool
\bool_new:N \g_rpi_figures_bool
\seq_new:N \g_rpi_committee_seq
\int_new:N \g_rpi_chairs_int
\tl_new:N \l_rpi_setup_tl

\keys_define:nn { rpi/thesis }
  {
    title .tl_gset:N = \g_rpi_title_tl,
    author .tl_gset:N = \g_rpi_author_tl,
    degree .choice:,
    degree / masters .code:n =
      { \tl_gset:Nn \g_rpi_degree_tl {Master~of~Science} },
    degree / doctoral .code:n =
      { \tl_gset:Nn \g_rpi_degree_tl {Doctor~of~Philosophy} },
    degree / engineering-doctorate .code:n =
      { \tl_gset:Nn \g_rpi_degree_tl {Doctor~of~Engineering} },
    degree / unknown .code:n =
      { \ClassError{rpi-thesis}{Unknown~degree~choice~in~metadata.tex}
          {Use~masters,~doctoral,~or~engineering-doctorate.} },
    degree-name .tl_gset:N = \g_rpi_degree_tl,
    department .tl_gset:N = \g_rpi_department_tl,
    graduation-month .choice:,
    graduation-month / May .code:n = { \tl_gset:Nn \g_rpi_month_tl {May} },
    graduation-month / August .code:n = { \tl_gset:Nn \g_rpi_month_tl {August} },
    graduation-month / December .code:n = { \tl_gset:Nn \g_rpi_month_tl {December} },
    graduation-month / unknown .code:n =
      { \ClassError{rpi-thesis}{Unknown~graduation~month~in~metadata.tex}
          {Use~May,~August,~or~December.} },
    graduation-year .tl_gset:N = \g_rpi_year_tl,
    seal-file .tl_gset:N = \g_rpi_seal_tl,
    copyright-page .bool_gset:N = \g_rpi_copyright_bool,
    list-of-tables .bool_gset:N = \g_rpi_tables_bool,
    list-of-figures .bool_gset:N = \g_rpi_figures_bool,
  }
% Defaults
\keys_set:nn { rpi/thesis }
  { degree=doctoral, seal-file=assets/rpi-seal.jpg,
    copyright-page=false, list-of-tables=true, list-of-figures=true }

% Blank lines may group the settings, and a comma after the last one is fine.
\NewDocumentCommand \thesissetup { +m }
  {
    \tl_set:Nn \l_rpi_setup_tl {#1}
    \tl_replace_all:Nnn \l_rpi_setup_tl { \par } { }
    \keys_set:nV { rpi/thesis } \l_rpi_setup_tl
  }
% \committeemember[Chair]{Name}, [Co-Chair], or no role for other members.
\NewDocumentCommand \committeemember { O{} m }
  {
    \tl_if_blank:nT {#2}
      { \ClassError{rpi-thesis}{Blank~committee~member~name~in~metadata.tex}
          {Put~the~member's~name~inside~the~braces~of~each~committeemember~line.} }
    \seq_gput_right:Nn \g_rpi_committee_seq
      { #2 \tl_if_blank:nF {#1} {,~#1} \par }
    \str_if_eq:nnT {#1} {Chair} { \int_gincr:N \g_rpi_chairs_int }
    \str_if_eq:nnT {#1} {Co-Chair} { \int_gincr:N \g_rpi_chairs_int }
  }

% Errors name the setting and the fix, before anything is printed.
\cs_new_protected:Npn \rpi_require:Nn #1#2
  {
    \tl_if_blank:VT #1
      { \ClassError{rpi-thesis}{Missing~#2~in~metadata.tex}
          {Fill~in~#2~inside~the~thesissetup~braces~and~recompile.} }
  }
\cs_new_protected:Npn \rpi_validate:
  {
    \rpi_require:Nn \g_rpi_title_tl {title}
    \rpi_require:Nn \g_rpi_author_tl {author}
    \rpi_require:Nn \g_rpi_degree_tl {degree}
    \rpi_require:Nn \g_rpi_department_tl {department}
    \rpi_require:Nn \g_rpi_month_tl {graduation-month}
    \rpi_require:Nn \g_rpi_year_tl {graduation-year}
    \exp_args:NnV \regex_match:nnF {\A[0-9]{4}\Z} \g_rpi_year_tl
      { \ClassError{rpi-thesis}{Graduation~year~must~have~four~digits}
          {Use~a~year~such~as~2027~in~metadata.tex.} }
    \seq_if_empty:NT \g_rpi_committee_seq
      { \ClassError{rpi-thesis}{No~committee~members~in~metadata.tex}
          {Add~committeemember~commands,~including~the~chair.} }
    \int_compare:nNnT {\g_rpi_chairs_int} = {0}
      { \ClassError{rpi-thesis}{Committee~chair~is~missing}
          {Use~committeemember[Chair]~or~committeemember[Co-Chair].} }
  }

% ---------------------------------------------------------------------------
% 11. Title page and seal (manual 1.1, pp. 1-2)
% ---------------------------------------------------------------------------
% The seal belongs to RPI and is not part of this starter: each student
% downloads it (assets/README.md). If seal-file is missing, a PNG named
% assets/rpi-seal.png is used instead; failing that, a framed box the size of
% RPI's current seal (605 x 608 pixels) holds its place, so adding the seal
% later does not move anything else on the title page.
\tl_const:Nn \c_rpi_seal_png_tl { assets/rpi-seal.png }
\dim_new:N \l_rpi_seal_dim
\cs_new_protected:Npn \rpi_seal_image:n #1
  {
    \includegraphics[width=0.25\linewidth,keepaspectratio,
      alt={Seal~of~Rensselaer~Polytechnic~Institute}]{#1}\par
  }
\cs_new_protected:Npn \rpi_seal_placeholder:
  {
    \ClassWarning{rpi-thesis}{RPI~seal~not~found.~Download~it~from~RPI's~
      Thesis~Preparation~page~and~save~it~as~\tl_use:N \g_rpi_seal_tl\space
      (see~assets/README.md)}
    % latexmk reads these standard log lines and recompiles once either file
    % appears: the seal-file setting or the PNG used in its place.
    \iow_log:x { No~file~\tl_use:N \g_rpi_seal_tl . }
    \tl_if_eq:NNF \g_rpi_seal_tl \c_rpi_seal_png_tl
      { \iow_log:x { No~file~\tl_use:N \c_rpi_seal_png_tl . } }
    \dim_set:Nn \l_rpi_seal_dim { 0.25\linewidth }
    \group_begin:
      \setlength{\fboxsep}{0pt}
      \fbox
        {
          \parbox[c][\dim_eval:n { \l_rpi_seal_dim * 608 / 605 - 2\fboxrule }][c]
            { \dim_eval:n { \l_rpi_seal_dim - 2\fboxrule } }
            {
              \centering\small
              RPI~seal:\par add\par
              \mbox{\tl_use:N \g_rpi_seal_tl}\par
            }
        }
    \group_end:
    \par
  }
\cs_new_protected:Npn \rpi_seal:
  {
    \exp_args:NV \file_if_exist:nTF \g_rpi_seal_tl
      { \exp_args:NV \rpi_seal_image:n \g_rpi_seal_tl }
      {
        \exp_args:NV \file_if_exist:nTF \c_rpi_seal_png_tl
          {
            % Log the missing seal-file too, so adding it later recompiles.
            \iow_log:x { No~file~\tl_use:N \g_rpi_seal_tl . }
            \exp_args:NV \rpi_seal_image:n \c_rpi_seal_png_tl
          }
          { \rpi_seal_placeholder: }
      }
  }
\RenewDocumentCommand \maketitle { }
  {
    \rpi_validate:
    % Do not use report's titlepage environment: it resets page counters.
    \pagenumbering{roman}
    \thispagestyle{empty}
    \begin{singlespace}
    \begin{center}
      {\large\bfseries\MakeUppercase{\tl_use:N\g_rpi_title_tl}\par}
      \vspace{20pt}
      {\large\bfseries\tl_use:N\g_rpi_author_tl\par}
      \vspace{20pt}
      Submitted~in~Partial~Fulfillment~of~the~Requirements\par
      for~the~Degree~of\par
      \vspace{10pt}
      {\itshape\MakeUppercase{\tl_use:N\g_rpi_degree_tl}\par}
      \vspace{40pt}
      Approved~by:\par
      \seq_map_inline:Nn \g_rpi_committee_seq {##1}
      \vfill
      \rpi_seal:
      \vspace{20pt}
      {\itshape\tl_use:N\g_rpi_department_tl\par}
      Rensselaer~Polytechnic~Institute\par
      Troy,~New~York\par
      \vspace{12pt}
      [\tl_use:N\g_rpi_month_tl\space\tl_use:N\g_rpi_year_tl]\par
    \end{center}
    \end{singlespace}
    \clearpage
  }

% ---------------------------------------------------------------------------
% 12. Commands for main.tex, in the order they appear there
% ---------------------------------------------------------------------------
% \thesisfrontmatter: copyright page (if set; manual 1.2, p. 3), contents,
% and the lists.
% One even gap between list entries: ignore the extra gap report.cls adds at
% each new chapter, as RPI's original class did.
\cs_new_protected:Npn \rpi_even_list: { \cs_set_eq:NN \addvspace \use_none:n }
\NewDocumentCommand \thesisfrontmatter { }
  {
    \bool_if:NT \g_rpi_copyright_bool
      {
        % Wording from the OGE manual's example; placed at the foot of the
        % page as in RPI's original class.
        \null\vfill
        \begin{center}
          \textcopyright\space\tl_use:N\g_rpi_year_tl\par
          By\par\tl_use:N\g_rpi_author_tl\par All~rights~reserved\par
          \vspace{12pt}
        \end{center}
        \clearpage
      }
    \begin{singlespace}\tableofcontents\end{singlespace}\clearpage
    \bool_if:NT \g_rpi_tables_bool
      {
        \phantomsection\addcontentsline{toc}{chapter}{\listtablename}
        \begin{singlespace}\rpi_even_list:\listoftables\end{singlespace}\clearpage
      }
    \bool_if:NT \g_rpi_figures_bool
      {
        \phantomsection\addcontentsline{toc}{chapter}{\listfigurename}
        \begin{singlespace}\rpi_even_list:\listoffigures\end{singlespace}\clearpage
      }
  }
% \thesismainmatter: arabic page numbers, top right, from chapter 1.
\NewDocumentCommand \thesismainmatter { }
  { \clearpage\pagenumbering{arabic}\pagestyle{rpibody} }
\ExplSyntaxOff

% \frontchapter{ABSTRACT}: an unnumbered front-matter section, listed in the
% contents. The link target goes at the top of the new page, before the
% heading, so the contents and the PDF bookmark open at the heading.
% (\chapter*'s own \clearpage adds no page: the target alone leaves it empty.)
\NewDocumentCommand{\frontchapter}{m}{%
  \clearpage\phantomsection\addcontentsline{toc}{chapter}{#1}\chapter*{#1}}

% \chapterattribution{...} (manual 2.8, pp. 27-29): a single-spaced note at
% the foot of the current page, like a footnote but with no number or mark. Put it directly after
% \chapter so it lands on the chapter's first page. Repeat for several.
\NewDocumentCommand{\chapterattribution}{+m}{%
  \insert\footins{%
    \def\baselinestretch{1}\reset@font\footnotesize
    \interlinepenalty\interfootnotelinepenalty
    \splittopskip\footnotesep \splitmaxdepth\dp\strutbox
    \floatingpenalty\@MM \hsize\columnwidth \@parboxrestore
    \color@begingroup\noindent\rule{\z@}{\footnotesep}\ignorespaces
      #1\@finalstrut\strutbox\par\color@endgroup}}

% \thesisreferences: the reference list, single-spaced, titled REFERENCES
% (to change it: \renewcommand{\referencesname}{...} in preamble.tex),
% and listed in the contents. It needs biblatex, which preamble.tex loads.
\NewDocumentCommand{\thesisreferences}{}{%
  \@ifundefined{printbibliography}
    {\ClassError{rpi-thesis}{\string\thesisreferences\space needs biblatex}
      {Keep the biblatex line in preamble.tex, or use your own bibliography commands.}}
    {\begin{singlespace}\printbibliography[heading=bibintoc,title={\referencesname}]\end{singlespace}}}

% ---------------------------------------------------------------------------
% 13. Links and PDF properties. Links stay black in print and on screen
%     (manual 2.1, p. 16). hyperref loads last among the class's packages.
% ---------------------------------------------------------------------------
\RequirePackage[hidelinks,unicode]{hyperref}
% Title, author, and language for screen readers and library catalogs, and
% the class version (shown as "Creator"). Use \texorpdfstring for math in a
% title.
\ExplSyntaxOn
\AtBeginDocument
  {
    \hypersetup
      {
        pdftitle = \tl_use:N \g_rpi_title_tl ,
        pdfauthor = \tl_use:N \g_rpi_author_tl ,
        pdflang = en-US ,
        pdfdisplaydoctitle = true ,
        pdfcreator = LaTeX~with~rpi-thesis~\use:c { ver@rpi-thesis.cls }
      }
  }
\ExplSyntaxOff
\endinput
