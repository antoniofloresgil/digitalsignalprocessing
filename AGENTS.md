# Project rules

## Scope and audience

- The book is written in English. Code is Python (NumPy, SciPy, Matplotlib).
- Readers are final-year computer science students. Assume first-course
  calculus, linear algebra and probability, but no complex analysis or
  transforms. Introduce every mathematical tool from scratch, only as far as
  the book needs it.
- Be mathematically rigorous. Define objects precisely and state results with
  their hypotheses in Quarto blocks (`::: {#def-...}`, `{#prp-...}`,
  `{#thm-...}`, `{#lem-...}`, `::: {.proof}`). Prove a result when the proof
  needs only tools already introduced; otherwise state it exactly and point to
  where it is proved. Never present a heuristic as a theorem. Back every
  result with a numerical experiment.
- Prandoni & Vetterli, *Signal Processing for Communications*, is the
  structural guide. Never copy its text, figures or exercises; write original
  explanations, examples and code, and cite it where an idea is borrowed.

## Chapter conventions

- One `.qmd` per chapter in `chapters/`, named `NN-slug.qmd`, labelled
  `{#sec-slug}`. Structure: motivation and learning goals, sections built
  around runnable experiments, Summary, Exercises.
- All figures are produced by code cells (`#| label: fig-...` with a caption).
  No hand-drawn or Mermaid figures: Mermaid needs a browser for the PDF.
- Seed randomness with `np.random.default_rng(...)` so builds are reproducible.
- *Try it* blocks are fenced as ```` ```{.pyodide} ```` (with the dot: the
  bare `{pyodide}` form breaks Pandoc parsing in the PDF), inside
  `::: {.content-visible when-format="html"}` plus a `callout-tip`. They must
  be self-contained (no imports from other cells) and use only packages
  available in Pyodide.
- Every code cell shows its output and is also runnable in the HTML edition
  (`tools/filters/live-cells.lua`, see `docs/architecture.md`). Therefore:
  cells must run in Pyodide (NumPy, SciPy, Matplotlib, Pillow only); a cell
  must get every name it uses from earlier cells or from itself, at module
  level (the dependency analysis is static and works on names); do not rely on
  the state of `rng` left by earlier cells, since each run starts from a fresh
  seed, so an `assert` on a random result must hold for any seed; never mutate
  global state that later cells rely on anywhere but in a cell that also binds
  the name (for example set `plt.rcParams` in the setup cell).
- Notation: `x[n]` discrete time, `x(t)` continuous time, `ω` digital
  frequency in rad/sample, `F_s` sampling frequency in Hz.

## Build

- Everything builds in the container from `docker/Dockerfile`; do not require
  host tools. `make render` must pass offline (`--network none`).
- Pin new Python packages in `docker/requirements.txt` and justify them.
- Do not commit `_book/`, `_freeze/` or `.quarto/`.

## Project knowledge

- Record significant design decisions in `docs/architecture.md`; keep this
  file for permanent rules only.
