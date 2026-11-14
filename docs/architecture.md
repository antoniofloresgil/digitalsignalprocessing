# Architecture decisions

## 2026-11-13: initial setup

- **Quarto book, HTML + PDF.** Follows the pattern of the author's
  *From Concept to Silicon* book, without its lab/audit machinery.
- **Python only.** NumPy/SciPy/Matplotlib are familiar to CS students and
  available both in the container and in Pyodide.
- **Code executes at render time.** Figures are always consistent with the
  code. `execute: freeze: auto` caches results locally; CI renders from
  scratch.
- **One container for everything.** `docker/Dockerfile` renders the book,
  runs JupyterLab and backs the VS Code dev container. Ubuntu base pinned by
  digest, Quarto by version and SHA-256, Python packages by version. Ubuntu
  APT packages are not pinned (accepted risk; revisit if builds drift).
- **In-browser execution with Quarto Live.** HTML output uses the
  `live-html` format from the `r-wasm/quarto-live` extension, vendored in
  `_extensions/` so rendering needs no network. Pyodide itself is loaded by
  the reader's browser from a CDN at reading time. Interactive cells appear
  only in HTML; the PDF shows normal executed cells.
- **Syllabus coverage check.** The outline was compared with the University
  of Murcia *Señales y Sistemas* course guide (code 6589, 2026/27). Added as
  a result: time-axis transformations, even/odd decomposition,
  correlation/autocorrelation, circular vs. linear convolution, measured
  DFT vs. FFT cost, and a numerical bridge to Fourier series and the
  continuous-time Fourier transform.
- **`{.pyodide}` fences, not `{pyodide}`.** The bare form is not a valid
  Pandoc attribute, so in the PDF build the fence is not recognised and the
  enclosing divs end up unclosed. The class form is accepted by the
  quarto-live filter (v0.1.3) and parses everywhere.

## 2026-11-13: editorial design

- **Same visual family as *From Concept to Silicon*.** A4, KOMA `scrreprt`,
  DejaVu Serif body with DejaVu Sans headings, night/amber/cyan palette
  (`design/palette.json`), cover → half title → title → credits → preface →
  contents → Part I. Ported from that book's generated style files, without
  its generator scripts: here the styles are edited directly.
- **The cover is code.** `tools/cover.py` draws front and back covers with
  Matplotlib as a pre-render step (`.quarto/cover/*.pdf` for the PDF,
  `design/cover.png` for HTML; both untracked). No SVG toolchain is needed.
  Five artwork variants exist; `design/palette.json` selects one. The chosen
  one, `fourier`, rebuilds a discrete square wave from growing sets of FFT
  harmonics above the coefficients |X[k]|: the book's central idea.
  Preview all variants with `python tools/cover.py --preview DIR`.
- **PDF structure filters.** `tools/filters/pdf-structure.lua` moves the
  contents after the preface and starts arabic numbering at Part I;
  `tools/filters/part-titles.lua` drops the "I." prefix that LaTeX already
  numbers.
- **No dark HTML theme**, matching the other book's single paper-toned theme.

## 2026-11-13: rigour and practice

- **Rigorous, but from scratch.** The author asked for a rigorous book. The
  audience is unchanged (no complex analysis or transforms assumed), but first
  courses in calculus, linear algebra and probability are. Results use Quarto
  theorem blocks (`def`, `prp`, `thm`, `lem`, `exm`, `.proof`), are proved when
  the tools are available, and are always paired with a runnable experiment.
- **Executable checks.** Chapters use `assert` to verify the results they
  state; a failing assertion fails the build, so the book is its own test.
- **Signals as Python functions.** Chapter 2 represents an infinite sequence
  as a function of an integer array, and operators as higher-order functions.
  Arrays appear only with an explicit extension rule (periodic or zero).
- **No Unicode math in captions.** Greek letters and sub/superscripts in
  `fig-cap` end up in hyperref labels, which XeLaTeX never sees as stable, so
  every build ran LaTeX ten times. Captions use `$...$` math instead.
- **Python library guide** as the last appendix (`appendices/python-libraries.qmd`).

## 2026-11-13: chapters 3-14 and the math toolbox

- **Every chapter is executable and self-checking.** Each states its results in
  theorem blocks and verifies them with `assert`s on numerical experiments;
  measured quantities (timings, SNRs, BERs) are printed, never hard-coded in the
  text or captions. Timings are shown but never asserted, since they depend on
  the build machine.
- **Proof policy in practice.** Results are proved when the tools are in the
  book (geometric sums, Cauchy-Schwarz, absolute convergence, partial
  fractions). A few are stated with a reference instead: inversion of the
  continuous Fourier transform, mean-square convergence of Fourier series (used
  in the sampling theorem), the Gibbs overshoot limit, the alternation theorem,
  the non-bandlimitedness of time-limited signals (sketched via analyticity),
  and dither theory.
- **Modem parameters (chapter 14).** $F_s$ = 8 kHz, 1000 baud, 8 samples per
  symbol, root-raised-cosine pulses with roll-off 0.35 spanning ±8 symbols,
  carrier 1800 Hz, telephone band 300-3400 Hz (101-tap FIR), 64-symbol QPSK
  preamble, second-order decision-directed PLL. The line's delay also rotates
  the carrier by $\omega_c D$, which the "perfect synchronisation" sections
  compensate explicitly.
- **PDF contents geometry.** KOMA's dynamic number widths in the contents need
  more LaTeX runs than Quarto performs, so `styles/book.tex` fixes the widths.

## 2026-11-13: animations

- **Animations are animated GIFs.** quarto-live inserts HTML outputs with
  `innerHTML`, so `<script>`-based animations (`FuncAnimation.to_jshtml`) do not
  run in *Try it* boxes. Instead, frames are drawn with Matplotlib, joined into
  a GIF with Pillow (a Matplotlib dependency, available in the container and in
  Pyodide), and returned by an object whose `_repr_html_` is an
  `<img src="data:image/gif;base64,...">`. Build-time animations go inside
  `content-visible when-format="html"`, with a static frame-strip figure for the
  PDF. First use: the wagon-wheel animation in chapter 4.

## 2026-11-14: every code cell is runnable in the HTML edition

- **Why not "autorun everything".** Running a whole chapter in the browser on
  load does not work: quarto-live evaluates independent cells in no particular
  order, so cells that use earlier variables fail. Measured in Pyodide, the
  computation itself is cheap (every cell runs in under 7 s, whole chapters in a
  few seconds), so the problem is dependencies, not speed.
- **Mechanism.** `tools/filters/live-cells.lua` (HTML only, run at `pre-ast`,
  before quarto-live) replaces the code block of each executed cell by a
  quarto-live *exercise* editor. The cell keeps its build-time output below the
  editor, labelled "Output when the book was built", and its figure label and
  caption. `tools/live_deps.py` parses the source `.qmd` and, for each cell,
  finds the earlier cells it needs (static, by names: the nearest earlier cell
  binding each name it uses, transitively). That code is attached as the
  exercise's hidden `setup` block, which quarto-live runs in a fresh environment
  before the visible code on every Run. So each cell runs correctly alone, in any
  order, and always gives the same answer (the `rng` of the first cell restarts
  from its seed, which is why live numbers can differ slightly from the printed
  ones).
- **The source `.qmd` is the input.** Cells with `echo: false` or shown only in
  the PDF have no code in the HTML document but can still be dependencies, so the
  analysis reads the `.qmd` and matches cells by `execution_count`.
- **Validation.** Running every cell with its dependencies in a clean Pyodide
  namespace found one assertion that depended on the random stream
  (chapter 10), now fixed; every cell of the book passes. The PDF is unaffected
  (the filter is registered for `live-html` only).
