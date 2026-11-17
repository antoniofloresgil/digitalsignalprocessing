"""Draw the book covers with Matplotlib.

The covers are generated, like every figure in the book, so they need no
external artwork or SVG tools. Run inside the book container:

    python tools/cover.py                 # front/back for the build
    python tools/cover.py --preview DIR   # PNG previews of every variant

Quarto runs the first form as a pre-render step (see _quarto.yml).
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = json.loads((ROOT / "design/palette.json").read_text(encoding="utf-8"))
C = IDENTITY["colors"]
VARIANT = IDENTITY["cover"]

# The page is drawn in "pixels" on an 800-wide A4 canvas, y pointing down,
# so layout numbers read like an SVG. 1 px = 210 mm / 800.
W, H = 800, 800 * 297 / 210
INCH = 210 / 25.4
PT = INCH * 72 / W  # points per canvas pixel


def page(background):
    fig = plt.figure(figsize=(INCH, INCH * H / W))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    fig.patch.set_facecolor(background)
    return fig, ax


def text(ax, x, y, s, size, color, weight="normal", **kw):
    ax.text(x, y, s, fontsize=size * PT, color=color, weight=weight,
            family="DejaVu Sans", va="baseline", **kw)


def glow(ax, x, y, color, width=2.2, layers=6):
    """A line with a soft halo, drawn as wider transparent copies."""
    for k in range(layers, 0, -1):
        ax.plot(x, y, color=color, lw=width + 2.6 * k, alpha=0.05,
                solid_capstyle="round")
    ax.plot(x, y, color=color, lw=width, solid_capstyle="round")


# ---------------------------------------------------------------- artwork
# Every variant draws inside the box (x0, y0)-(x1, y1) in canvas pixels.
BOX = (64, 560, 736, 1010)


def art_wave(ax):
    """A sound-like wave becomes samples, and the samples become a spectrum."""
    x0, y0, x1, y1 = BOX
    parts = [(3, 0.55, 0.0), (7, 0.30, 1.1), (12, 0.15, 2.3)]

    def signal(t):
        return sum(a * np.sin(2 * np.pi * f * t + p) for f, a, p in parts)

    # Upper band: continuous wave fading out as the samples take over.
    mid, amp = y0 + 120, 120
    t = np.linspace(0, 1, 1200)
    xs = x0 + t * (x1 - x0)
    ys = mid - amp * signal(t)
    fade = np.clip(1.25 - 1.2 * t, 0.12, 1)
    for k in range(len(t) - 1):
        ax.plot(xs[k:k + 2], ys[k:k + 2], color=C["cyan"], lw=9,
                alpha=0.06 * fade[k], solid_capstyle="round")
        ax.plot(xs[k:k + 2], ys[k:k + 2], color=C["cyan"], lw=2.2,
                alpha=fade[k], solid_capstyle="round")

    n = np.arange(48)
    tn = (n + 0.5) / len(n)
    xn, yn = x0 + tn * (x1 - x0), mid - amp * signal(tn)
    on = np.clip(2.2 * tn - 0.15, 0.15, 1)
    for xk, yk, a in zip(xn, yn, on):
        ax.plot([xk, xk], [mid, yk], color=C["copper"], lw=1.6, alpha=a)
        ax.plot(xk, yk, "o", ms=4.6, color=C["copper"], alpha=a, mec="none")
    ax.plot([x0, x1], [mid, mid], color=C["line"], lw=1)

    # Lower band: the same signal seen as three spectral lines.
    base, top = y1 - 10, y0 + 300
    ax.plot([x0, x1], [base, base], color=C["line"], lw=1.2)
    for f in np.arange(0, 17):
        xf = x0 + (f + 0.5) / 17 * (x1 - x0)
        ax.plot([xf, xf], [base, base + 6], color=C["line"], lw=1)
    for f, a, _ in parts:
        xf = x0 + (f + 0.5) / 17 * (x1 - x0)
        yf = base - (base - top) * a / 0.55
        glow(ax, [xf, xf], [base, yf], C["cyan"], width=3)
        ax.plot(xf, yf, "o", ms=8, color=C["paper"], mec=C["cyan"], mew=2)


def art_spectrogram(ax):
    """Time–frequency picture of a bird-like chirp with harmonics."""
    x0, y0, x1, y1 = BOX
    rng = np.random.default_rng(7)
    fs, dur = 8000, 2.0
    t = np.arange(int(fs * dur)) / fs
    phase = 2 * np.pi * (300 * t + 220 * np.sin(2 * np.pi * 0.7 * t) / (2 * np.pi * 0.7)
                         + 180 * t**2)
    x = sum(np.sin(k * phase) / k**1.4 for k in (1, 2, 3, 4))
    x += 0.4 * np.sin(2 * np.pi * 2600 * t) * (t > 1.2)
    x += 0.02 * rng.standard_normal(t.size)
    nfft, hop = 512, 64
    win = np.hanning(nfft)
    frames = np.lib.stride_tricks.sliding_window_view(x, nfft)[::hop] * win
    spec = 20 * np.log10(np.abs(np.fft.rfft(frames, axis=1)).T + 1e-3)
    spec = np.clip(spec - spec.max() + 60, 0, 60)
    cmap = LinearSegmentedColormap.from_list(
        "cover", [C["cover"], C["night"], "#155E75", C["cyan"], C["copper"], "#FFF4D6"])
    ax.imshow(spec[: nfft // 2 * 3 // 4], extent=(x0, x1, y1, y0), origin="lower",
              aspect="auto", cmap=cmap, interpolation="bilinear")
    ax.plot([x0, x1], [y1 + 6, y1 + 6], color=C["line"], lw=1)


def art_phasor(ax):
    """A rotating arrow on the unit circle traces a sinusoid; samples mark it."""
    x0, y0, x1, y1 = BOX
    r, cx, cy = 150, x0 + 160, (y0 + y1) / 2
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(cx + r * np.cos(th), cy - r * np.sin(th), color=C["line"], lw=1.4)
    ax.plot([cx - r - 20, cx + r + 20], [cy, cy], color=C["line"], lw=1)
    ax.plot([cx, cx], [cy - r - 20, cy + r + 20], color=C["line"], lw=1)
    w = 0.9
    for k in range(12):
        a = 2 * np.pi * k / 12
        ax.plot(cx + r * np.cos(a), cy - r * np.sin(a), "o", ms=4,
                color=C["copper"], alpha=0.55, mec="none")
    px, py = cx + r * np.cos(w), cy - r * np.sin(w)
    glow(ax, [cx, px], [cy, py], C["copper"], width=3)
    ax.plot(px, py, "o", ms=9, color=C["paper"], mec=C["copper"], mew=2)

    sx0 = cx + r + 60
    ax.plot([px, sx0], [py, py], color=C["muted"], lw=1, ls=(0, (3, 4)))
    u = np.linspace(0, 1, 600)
    xs = sx0 + u * (x1 - sx0)
    ys = cy - r * np.sin(w + 2 * np.pi * 1.75 * u)
    glow(ax, xs, ys, C["cyan"])
    un = np.arange(0, 22) / 21
    xn, yn = sx0 + un * (x1 - sx0), cy - r * np.sin(w + 2 * np.pi * 1.75 * un)
    ax.vlines(xn, cy, yn, color=C["copper"], lw=1.4, alpha=0.8)
    ax.plot(xn, yn, "o", ms=4.5, color=C["copper"], mec="none")
    ax.plot([sx0, x1], [cy, cy], color=C["line"], lw=1)


def art_bode(ax):
    """Bode plot of Butterworth low-pass filters of growing order."""
    from scipy import signal

    x0, y0, x1, y1 = BOX
    w = np.logspace(-2.3, np.log10(0.9 * np.pi), 800)  # rad/sample
    lw = np.log10(w)
    xs = x0 + (lw - lw[0]) / (lw[-1] - lw[0]) * (x1 - x0)

    # Faint decade grid shared by both panels.
    for d in (0.01, 0.1, 1):
        if d < w[0]:
            continue
        xd = x0 + (np.log10(d) - lw[0]) / (lw[-1] - lw[0]) * (x1 - x0)
        ax.plot([xd, xd], [y0, y1], color=C["line"], lw=0.8)

    mag_top, mag_bot = y0, y0 + 270       # 0 dB .. -100 dB
    ph_top, ph_bot = y0 + 310, y1         # 0 .. -540 degrees
    for yy in np.linspace(mag_top, mag_bot, 5):
        ax.plot([x0, x1], [yy, yy], color=C["line"], lw=0.6)
    ax.plot([x0, x1], [ph_top, ph_top], color=C["line"], lw=0.6)

    hero = 6
    for order in range(1, 9):
        b, a = signal.butter(order, 0.06)
        _, h = signal.freqz(b, a, worN=w)
        db = np.clip(20 * np.log10(np.abs(h) + 1e-12), -100, 3)
        ym = mag_top + (-db / 100) * (mag_bot - mag_top)
        if order == hero:
            glow(ax, xs, ym, C["cyan"], width=2.6)
            ph = np.degrees(np.unwrap(np.angle(h)))
            yp = ph_top + (-ph / 540) * (ph_bot - ph_top)
            glow(ax, xs, yp, C["copper"], width=2.4)
        else:
            ax.plot(xs, ym, color=C["cyan"], lw=1.1, alpha=0.18 + 0.04 * order)
    # Mark the cut-off frequency.
    xc = x0 + (np.log10(0.06 * np.pi) - lw[0]) / (lw[-1] - lw[0]) * (x1 - x0)
    ax.plot([xc, xc], [mag_top, ph_bot], color=C["muted"], lw=1, ls=(0, (3, 4)))
    yc = mag_top + (3.01 / 100) * (mag_bot - mag_top)
    ax.plot(xc, yc, "o", ms=8, color=C["paper"], mec=C["cyan"], mew=2)


def art_fourier(ax):
    """A discrete square wave rebuilt from more and more FFT harmonics."""
    x0, y0, x1, y1 = BOX
    N = 64
    n = np.arange(N)
    x = np.where((n // 16) % 2 == 0, 1.0, -1.0)
    X = np.fft.fft(x)

    def partial(K, t):
        """Sum of the DFT terms with |k| <= K, evaluated at fractional n=t."""
        out = np.full_like(t, X[0].real / N)
        for k in range(1, K + 1):
            out += 2 / N * np.abs(X[k]) * np.cos(2 * np.pi * k * t / N + np.angle(X[k]))
        return out

    mid, amp = y0 + 140, 105
    t = np.linspace(0, N - 1, 1400)
    xs = x0 + t / (N - 1) * (x1 - x0)
    levels = [1, 3, 5, 9, 15, 31]
    for i, K in enumerate(levels):
        ys = mid - amp * partial(K, t)
        if K == levels[-1]:
            glow(ax, xs, ys, C["cyan"], width=2.2)
        else:
            ax.plot(xs, ys, color=C["cyan"], lw=1.2, alpha=0.2 + 0.12 * i)
    xn = x0 + n / (N - 1) * (x1 - x0)
    ax.plot([x0, x1], [mid, mid], color=C["line"], lw=1)
    ax.vlines(xn, mid, mid - amp * x, color=C["copper"], lw=1.3, alpha=0.8)
    ax.plot(xn, mid - amp * x, "o", ms=4.2, color=C["copper"], mec="none")

    # The ingredients: |X[k]| for the first harmonics, used ones lit.
    base, top = y1 - 6, y0 + 330
    kmax = 32
    ax.plot([x0, x1], [base, base], color=C["line"], lw=1.2)
    peak = np.abs(X).max()
    for k in range(kmax + 1):
        xk = x0 + k / kmax * (x1 - x0)
        yk = base - (base - top) * np.abs(X[k]) / peak
        if np.abs(X[k]) < 1e-9:
            ax.plot(xk, base, "o", ms=3, color=C["line"], mec="none")
            continue
        glow(ax, [xk, xk], [base, yk], C["cyan"], width=2.4, layers=4)
        ax.plot(xk, yk, "o", ms=6.5, color=C["paper"], mec=C["cyan"], mew=1.8)


ART = {"wave": art_wave, "spectrogram": art_spectrogram, "phasor": art_phasor,
       "bode": art_bode, "fourier": art_fourier}


# ---------------------------------------------------------------- covers
def front(variant):
    fig, ax = page(C["cover"])
    ax.add_patch(plt.Rectangle((64, 64), 38, 5, color=C["copper"]))
    text(ax, 118, 73, "S I G N A L S   /   P Y T H O N", 13, C["muted"])
    text(ax, 60, 196, "Digital", 74, C["paper"])
    text(ax, 56, 296, "Signal", 100, C["paper"], weight="bold")
    text(ax, 56, 398, "Processing", 100, C["paper"], weight="bold")
    text(ax, 64, 470, "A Hands-On Introduction with Python", 27, C["muted"])
    ART[variant](ax)
    ax.plot([64, 736], [1050, 1050], color=C["line"], lw=1)
    text(ax, 64, 1090, "Antonio Flores Gil", 24, C["paper"])
    text(ax, 736, 1090, "N U M P Y   /   S C I P Y", 11, C["muted"], ha="right")
    return fig


BLURB = """\
Your phone, your music player and your Wi-Fi card all turn
the physical world into lists of numbers, transform those
numbers, and turn them back. This book shows how, for
readers who can program but have not studied transforms
or complex analysis.

Every idea comes with Python code you can run: in the
container that builds the book, in JupyterLab, or right in
the browser. Every figure, this cover included, is drawn
by that code."""

PARTS = [
    ("Signals", "Sampling, quantization, signals as vectors"),
    ("Frequency", "Complex sinusoids, the DFT and the FFT"),
    ("Filters", "Convolution, the z-transform, filter design"),
    ("From Analog to Digital and Back", "Noise, interpolation, A/D, multirate"),
    ("Putting It All Together", "Modem, pedalboard and software radio"),
]


def back():
    fig, ax = page(C["cover"])
    ax.add_patch(plt.Rectangle((64, 64), 38, 5, color=C["copper"]))
    text(ax, 64, 150, "Sample. Transform. Filter.", 46, C["paper"], weight="bold")
    text(ax, 64, 204, "Then run the code.", 40, C["muted"])
    for k, line in enumerate(BLURB.splitlines()):
        ax.text(64, 282 + 29 * k, line, fontsize=19 * PT, color=C["paper"],
                family="DejaVu Serif", va="baseline")

    y = 590
    ax.plot([64, 736], [y, y], color=C["line"], lw=1)
    text(ax, 64, y + 44, "F I V E   P A R T S ,   T H R E E   P R O J E C T S", 12,
         C["muted"], weight="bold")
    for k, (title, sub) in enumerate(PARTS):
        yk = y + 92 + 60 * k
        text(ax, 64, yk, f"0{k + 1}", 17, C["copper"], weight="bold")
        text(ax, 118, yk, title, 21, C["paper"], weight="bold")
        text(ax, 118, yk + 26, sub, 15, C["muted"])

    band = 1000
    ax.add_patch(plt.Rectangle((0, band), W, H - band, color=C["night"]))
    text(ax, 64, band + 44, "R E A D   T H E   B O O K   ·   R U N   T H E   C O D E",
         12, C["paper"], weight="bold")
    text(ax, 64, band + 78, "antoniofloresgil.github.io/digitalsignalprocessing",
         16, C["cyan"])
    text(ax, 64, band + 106, "Text CC BY-SA 4.0  ·  Code MIT", 12, C["muted"])
    return fig


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default=ROOT / ".quarto/cover", type=Path)
    ap.add_argument("--preview", type=Path, help="write PNGs of all variants here")
    args = ap.parse_args()

    if args.preview:
        args.preview.mkdir(parents=True, exist_ok=True)
        for name in ART:
            front(name).savefig(args.preview / f"front-{name}.png", dpi=60)
        back().savefig(args.preview / "back.png", dpi=60)
        return

    args.out_dir.mkdir(parents=True, exist_ok=True)
    fig = front(VARIANT)
    fig.savefig(args.out_dir / "front.pdf")
    fig.savefig(ROOT / "design/cover.png", dpi=90)  # HTML edition
    back().savefig(args.out_dir / "back.pdf")
    plt.close("all")


if __name__ == "__main__":
    main()
