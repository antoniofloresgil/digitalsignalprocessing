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

## 2026-11-17: chapter 15 (digital pedalboard)

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
## 2026-11-17: software-defined radio chapter

- **It is chapter 16, the last of Part V** (`chapters/16-software-defined-radio.qmd`;
  it was first written as Appendix E and moved by the author's decision after seeing
  the book), a project larger than the two before it, which
  tells the story of a receiver from antenna to loudspeaker. It starts with the
  trend of digitising everything (repeatability, flexibility, functions that
  circuits cannot give, no noise accumulation, cost, testing; each backed by a
  small experiment where it can be) and what is left analog in an SDR.
- **Project**: a stereo FM broadcast receiver. There is no antenna, so the
  appendix *synthesises what a dongle delivers*: four stations at 98.0-98.6 MHz
  offsets (-300, -100, +100, +300 kHz from the tuner centre), carrier amplitudes
  1, 0.5, 0.8, 0.12, white noise (35 dB carrier-to-noise for the strongest in its
  200 kHz channel), a 2.5 kHz tuner error and an 8-bit converter, stored as
  interleaved unsigned bytes like a real RTL-SDR file, so that a real recording
  can replace it.
- **Rates**: 48 kHz audio, 240 kHz composite and modulator, 960 kHz capture. All
  ratios are integers (x5, x4), so the receiver decimates by 4 and then by 5.
- **Simulation level**: the complex envelope (I/Q), not the 100 MHz passband. The
  equivalence is proved (quadrature mixer proposition) and checked on a
  scaled-down radio (100 kHz carrier, 800 kHz rate).
- **Theory included and proved**: FM of a tone has lines $J_n(\beta)$
  (Jacobi-Anger via Fourier coefficients) and Carson's rule is *tested*, not
  claimed (more than 98 % of the power in $|n| \le \beta + 1$); the quadrature
  mixer; the discriminator is exact and amplitude-independent; the composite
  signal is bounded by 1 ($|a+b| + |a-b| = 2\max(|a|,|b|)$).
- **Pre-emphasis** is the exact inverse of a one-pole de-emphasis
  ($a = e^{-1/(\tau F_s)}$), a two-tap FIR, because the bilinear transform puts a
  pole at Nyquist when inverted. At 15 kHz it gives 12.2 dB against 13.7 dB of
  the analog curve.
- **Pyodide pitfall**: `scipy.signal.welch` fails with "array is too big" for
  signals of more than about 10^5 samples (32-bit array sizes in `as_strided`),
  while `spectrogram` on the same sizes in chapter 15 worked. The appendix has its
  own `welch_psd` (a loop over segments), checked against SciPy on a short signal.
- **Receiver design (stages 2-9).** Dial scan on the 200 kHz grid (power per
  channel against the noise floor measured beyond 410 kHz), carrier by the
  centroid of the channel power re-centred three times (error below 50 Hz, which
  also measures the tuner's 2.5 kHz error); complex-mixer tuning; Kaiser channel
  filter 90/110 kHz, 60 dB, 177 taps, polyphase decimation by 4 (adjacent-channel
  rejection about 67-69 dB against 0 or -3 dB for naive decimation); discriminator;
  pilot detection by power ratio; second-order PLL (50 Hz, zeta 0.707) on the
  band-passed pilot; coherent demodulation of the 38 kHz difference signal;
  decimation by 5; exact de-emphasis. `fm_receiver(bytes)` is the whole receiver.
- **Why a dial scan and not peak picking**: the faint station D is a shoulder on
  the skirt of C in the sliding-window power profile, with no local maximum, so a
  peak finder misses it; measuring the power of each channel of the grid does not.
- **Results proved or measured**: stereo crosstalk against pilot phase error is
  $\tan^2(\varepsilon/2)$ (proved, measured within 0.3 dB for 15-60 degrees);
  the output SNR of the discriminator is $3\beta^2 P_m\,\mathrm{CNR}_W$ above a
  threshold of about 12 dB (stated as a first-order derivation, not a theorem, and
  verified: within 0.1 dB above the threshold, collapsing below it); the noise
  spectrum slope is 1.97 (expected 2); the de-emphasis gain is 9.39 dB measured
  against 9.56 predicted; stereo is 16.0 dB noisier than mono against 16.2
  predicted.
- **The SNR of the strong stations is capped near 37 dB by distortion, not by
  noise or by the 8-bit converter**: a noise-free single station gives 37.0 dB
  with the 90/110 kHz channel filter and 49.0 dB with a 140/170 kHz one. It is
  the selectivity-fidelity trade-off, and the appendix shows it. (The 8-bit
  quantisation was checked and changes the audio SNR by less than 0.1 dB.)
- **Real recordings (stage 9).** The receiver was run on two public recordings
  (williamyang98/FM-Radio, release `sample_data`: 8-bit I/Q at 1.024 MS/s from a
  dongle in Sydney, MIT-licensed repository; 95.3 and 92.9 MHz, first 1.5 s each,
  downloaded on 2026-11-17 into the scratchpad, never into the repository because
  they are broadcast programmes and 17-209 MB). Result: one station each at the
  tuner centre, stereo, pilot amplitude 0.088 and 0.079, L/R correlation 0.84 and
  0.98, RDS visible at 57 kHz. The checks are structural (no ground truth, nobody
  listened to the audio). The build runs offline, so this section is a static
  listing plus a table, stated as not run by the build; what *is* run is a
  simulated recording at 1.024 MS/s tuned on station C, which exercises the same
  code path (`to_receiver_rate`: DC removal and 15/16 resampling; the dial-scan
  grid as a parameter).
- **A second receiver as the check on real data** (`independent_receiver`, in the
  chapter): native rate with decimation by 4, Remez channel filter, unwrapped-phase
  discriminator, Hilbert-transform subcarrier (no PLL), zero-phase Butterworth
  filters; stereo only. On the synthetic capture both receivers are 35-36 dB from the
  truth and agree to 48-54 dB (asserted, runnable). On the real recordings (static
  text) they agree to 43-48 dB in L, R and mono and to 36 and 26 dB in the stereo
  difference. The agreement measure must trim **both** ends of the signal (the first
  version trimmed only the start and the zero-phase filter transients at the end made
  two correct receivers look 15-30 dB apart) and compares only above 50 Hz (the
  tuner's slow drift dominates below). The sensitivity of the real recordings to the
  channel filter width (41-61 dB self-agreement for a 10 kHz change) is the
  yardstick for what "agree" means. An audio spectrogram of the real recordings
  looks like speech/music, but it cannot be a figure of the book (figures come from
  code, and the build has no recording), so it is only mentioned.
- **Robust noise floor.** The dial scan measures the floor as the quietest 100 kHz
  of the PSD, not the band edges: a real band has stations at its edges.
- **Not done**: a real-time implementation; RDS and AM are exercises.
- **Cost in the browser**: every cell passes in Pyodide; the slowest (the whole
  receiver, with its dependencies re-run) takes about 11 s, the rest under 7 s.
  The HTML page is about 4 MB because of the embedded audio.

- **Software-defined radio project**: first planned as an annex, then written as
  chapter 16 (see the entry "software-defined radio chapter" below). Its
  references are in `references.bib` (@mitola1995, @reed2002, @collins2018,
  @rice2009, @harris2004, @crochiere1983, @hogenauer1981, @carson1922, @haykin2009,
  @lyons2011, @itu450); the entries were written from memory and must be checked
  against the sources before publication.

## 2026-11-18 — recordings for the core labs

- The common control is a two-second, CC0 FreePats guitar recording. The
  spectral and block-filtering labs use the same explicitly injected tone
  to make paired measurement possible. Both document how to separate the
  interference residual from error in the wanted waveform.
- Put downloadable recordings in `chapters/data/`. List each recording as
  a resource in the chapter that uses it and as a Pyodide resource for that
  page. Quarto copies the file and Quarto Live places the same bytes under
  `data/` in the worker. This lets the visible Python read the same relative
  path during an offline render and in the browser, without duplicating
  datasets or adding any dependencies.
- The default course route uses the two labs and one project. Worked
  solutions live in a separate appendix so readers can try each exercise first.
- The spectral lab averages one periodogram at a time. SciPy's strided Welch
  implementation can exceed Pyodide's maximum virtual array size for this
  record and window length. For a short slice the chapter checks the result
  against the pinned SciPy implementation.
- The SDR chapter ships a CC BY 4.0 excerpt of the Iraq RF Spectrum Dataset,
  DOI `10.5281/zenodo.22019720`. The original float data's 256 converter levels
  are stored as byte codes and the rate and centre frequency live in a SigMF
  sidecar. The same receiver accepts simulated records, this real recording,
  and other unsigned interleaved I/Q files. An explicit carrier offset bypasses
  the dial scan for recordings where the relative station frequency is known.
  Receiver definitions occupy separate cells from the simulation so the live
  file examples do not also allocate or decode the synthetic RF band.

## 2026-11-18 — seed robustness and contents numbering

- **Asserts on random results must hold for any seed**, because each live cell
  in the browser starts from a fresh seed and a different stream than the
  sequential build. Running every chapter with 12 different global seeds found
  four asserts that held only at the book's seed (they were already in the
  previous commit). Fixes, each chosen by simulation over 20 000 seeds:
  - Chapter 3, delay estimation: attenuation 0.4 instead of 0.2 against noise
    of 0.5 (0.2 failed for 12 % of seeds, 0.4 for none).
  - Chapter 3, period estimation: "the highest peak" is fragile because the
    peak at twice the period is only 5 % lower. The estimate is now the first
    peak that reaches 80 % of the highest one, with noise 0.4 (the old version
    failed for half of the seeds, the new one for none).
  - Chapter 10: the tolerances were 2 standard deviations wide. The
    autocorrelation check now allows 3 % of r[0] (statistical error 0.4 %), and
    the filtered-noise power 8 % (statistical error 1.6 %).
  Every chapter that has a global seed passes with 12 seeds; chapters 3 and 10
  also with 60.
- **Contents numbering.** `tocnumwidth` of sections is 3.4 em in
  `styles/book.tex`: with 2.9 em the two-digit numbers of chapter 16
  (`16.10` onwards) touched their titles.
- **Chapter 16 stage names.** The stereo decoder and the measurements are
  optional extensions of the main path, but they keep their stage numbers
  (6 and 8) so that the plan table, the headings and the text agree.
