# Digital Signal Processing: A Hands-On Introduction with Python

An open textbook on digital signal processing for computer science and
engineering students. Every idea comes with Python code; every figure is
produced by that code when the book is built. Mathematical tools (complex
numbers, Fourier analysis, the z-transform) are introduced from scratch.

## Read

- HTML (with in-browser *Try it* exercises): <https://antoniofloresgil.github.io/digitalsignalprocessing/>
- PDF: download it from the sidebar of the HTML edition.

## Run the code and build the book

You only need [Git](https://git-scm.com/downloads) and
[Docker](https://docs.docker.com/get-started/get-docker/). Everything else
(Python, NumPy, SciPy, Matplotlib, JupyterLab, Quarto, LaTeX) lives in one
container image defined in [`docker/Dockerfile`](docker/Dockerfile).

```sh
git clone https://github.com/antoniofloresgil/digitalsignalprocessing.git
cd digitalsignalprocessing

make lab        # JupyterLab at http://localhost:8888
make preview    # live book preview at http://localhost:4200
make render     # HTML + PDF into _book/
make shell      # a shell inside the container
```

In VS Code, *Reopen in Container* (Dev Containers extension) gives the same
environment. Without `make`, see the commands in
[appendices/running-the-code.qmd](appendices/running-the-code.qmd).

## Repository map

| Path | Content |
|------|---------|
| `_quarto.yml` | Book structure and output formats |
| `index.qmd`, `chapters/`, `appendices/` | Book text and executable code |
| `references.bib` | Bibliography |
| `docker/` | Container image and pinned Python packages |
| `_extensions/r-wasm/live/` | Quarto Live extension (in-browser Python via Pyodide) |
| `styles/` | HTML (SCSS) and PDF (LaTeX) styling |
| `.devcontainer/` | VS Code dev container |
| `docs/` | Design decisions for contributors |

## License

Text and figures: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Code: [MIT](https://opensource.org/license/mit). See [LICENSE.md](LICENSE.md).
