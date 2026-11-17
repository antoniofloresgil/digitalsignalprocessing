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

## 2026-11-16: advanced proofs appendix

- **What and why.** `appendices/advanced-proofs.qmd` proves the eleven results
  that the chapters used to state without proof, or only sketch, because the
  proof needs tools the chapter had not introduced: completeness of $\ell^2$ and
  infinite orthonormal expansions, completeness of the trigonometric system
  (Fejér), uniqueness of Fourier coefficients, the DTFT on $\ell^2$, Fourier
  inversion, Plancherel, finite-duration signals are not bandlimited, Gibbs, the
  uncertainty principle, the alternation theorem and the mean ergodic theorem.
  The chapters now cite the appendix instead of "see Prandoni" or "a standard
  result", keeping the rule that a result is either proved or pointed to where
  it is proved.
- **The only black boxes are five facts of Lebesgue integration**, listed at the
  start of the appendix (completeness of $L^2$, density of continuous
  functions, dominated/monotone convergence, Fubini, Lebesgue differentiation).
  The book does not develop measure theory; every other step is proved.
- **Real analysis instead of complex analysis** for "time-limited signals are not
  bandlimited": vanishing derivatives give vanishing moments, and Weierstrass
  density (proved from Fejér's theorem) finishes. This keeps the "no complex
  analysis" promise of the preface.
- **Experiments.** Every section ends with runnable cells whose `assert`s hold for
  any seed (random cells were run with 60 different seeds), following the
  live-cell rules of `AGENTS.md`.
- **A correction found while writing it.** Chapter 9 said that the optimal error
  alternates $L + 2$ times "where $L$ is the number of free coefficients"; the
  correct count is $L + 2$ alternations for $L + 1$ free coefficients (a cosine
  polynomial of degree $L$). The chapter now says so, and the appendix
  confirms 17 alternations for the length-31 filter ($L = 15$).
- **Pandoc pitfall.** A paragraph that starts with `(3)` is read as a numbered
  list item, and a display equation inside it breaks the PDF; the equation must
  be indented four spaces as list content.
- **Pyodide integers are 32-bit.** `np.arange(a, b) ** 2` overflows silently when
  the squares exceed $2^{31}$, which CPython (64-bit) hides; found by running
  every cell of the appendix in Pyodide. Use `dtype=float` for such sums.

## 2026-11-17: chapter 15 (digital pedalboard) and the planned SDR annex

- **Chapter 15, "Project: A Digital Pedalboard"**, goes in Part V next to the
  modem. It follows four stages (generate, show, process, output) around one
  idea: the pitch tuner of stage 3 is the measuring instrument that checks every
  effect of stage 4. Sources: Karplus-Strong string as a feedback filter with an
  all-pass fractional delay (@karplus1983, @jaffe1983); EQ biquads
  (@bristowjohnson); distortion with oversampling; Schroeder/Moorer reverb
  (@schroeder1962, @moorer1979); WSOLA pitch shifter (@verhelst1993); frequency
  estimation against the Cramér-Rao bound (@rife1974, @kay1993); output with
  quantisation, dither and 2x interpolation.
- **Sampling rate 24 kHz**, so that the 48 kHz output stage is an exact factor 2
  and the cells stay fast in Pyodide.
- **Decisions taken while testing the cells over 30 seeds** (the asserts must hold
  for any seed, and the first versions did not):
  - The pluck is a *triangle* (a string lifted by a pick) plus 15 % noise, not a
    pure noise burst: with noise alone the fundamental of some strings is nearly
    absent by chance, and the autocorrelation tuner then jumps an octave. The
    triangle also gives a physical meaning to the pick position (exercise 1).
  - The loop gain is capped at 0.9995: a high note cannot ring for the requested
    $T_{60}$, because the averaging filter alone costs $\cos(\pi f_0/F_s)$ per
    period (an A5 asked for 2 s gave $g > 1$, an unstable string).
  - The tuner refines the *strongest of the first eight harmonics* and divides by
    its number; refining near the fundamental was biased by stronger neighbours
    after the distortion.
  - Onsets are detected on the energy above 1.5 kHz with a 100 ms refractory
    period; on the whole signal the beating of neighbouring notes (E4 and F4)
    produces false onsets. The processed signals reuse the onsets of the dry one,
    since the pedals add no delay.
  - The melody rings for $T_{60}$ = 1.2 s: with 2 s the tail of the previous note
    biased the reading of the next one by up to 10 cents (a real limit of a
    monophonic tuner, which the chapter tells the reader).
  - **Polyphonic detection was left out.** Matching pursuit on harmonic templates
    identified a triad correctly in about 21 of 24 trials at best (octave errors
    because harmonics of different notes coincide), too unreliable to be a result
    of the book; it is Exercise 3. The chord is only synthesised and heard.
  - Dither is checked by the correlation of the output with the music
    ($\sigma_x/\sqrt{\sigma_x^2 + \Delta^2/4}$), not by reading a note from a
    sub-LSB signal, which fails for some seeds because the strongest line can be
    noise.
  - The decimation filter of the oversampled distortion overshoots (peak 1.16 to
    1.42 for a signal that never exceeds 1), which the chapter shows and which
    motivates the normalisation of the output stage.
- **Audio in the HTML edition** uses the same mechanism as the GIF animations: an
  object whose `_repr_html_` returns `<audio controls src="data:audio/wav;base64,...">`,
  which works in build-time cells and in the editable Pyodide cells alike. The
  PDF shows waveforms and spectrograms instead (audio cells are
  `content-visible when-format="html"`).
- **Planned, not started: a software-defined radio annex** (simulated FM
  broadcast at IQ baseband: mixing, multi-stage decimation, FM demodulation,
  de-emphasis, audio out), deeper than the chapter projects, to be written once
  chapter 15 is finished. Its references are already in `references.bib`
  (@mitola1995, @reed2002, @collins2018, @rice2009, @harris2004, @crochiere1983,
  @hogenauer1981, @carson1922, @haykin2009, @lyons2011, @itu450). The entries
  were written from memory and must be checked against the sources before the
  annex is published.
