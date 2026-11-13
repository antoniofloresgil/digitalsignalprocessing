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
