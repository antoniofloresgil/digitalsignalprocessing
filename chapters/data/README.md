# Guitar recording

[guitar-e4.wav](guitar-e4.wav) is the first two seconds of `E4.flac` from
the **Spanish classical guitar** sound bank, version 2019-06-18, recorded
in 2008 and created for FreePats by the contributor credited as roberto@zenvoid.org
(the page gives no name), with an AKG Perception 120 microphone. FreePats applied filters to the original capture.
The excerpt was decoded from the SFZ/FLAC archive and saved as mono
44,100 Hz, signed 16-bit PCM. The excerpt received no further filtering
or normalisation.

- [Original sound bank and recording notes](https://freepats.zenvoid.org/Guitar/acoustic-guitar.html)
- [Creative Commons CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)
- SHA-256 of the excerpt — `1e0e6a0a3d4720b3cd11833e426b114c6afc26a09708754f808a9cdee6df7fb2`

# Recorded FM radio signal

- [I/Q data](baghdad-fm-100-5.sigmf-data) · [SigMF metadata](baghdad-fm-100-5.sigmf-meta)
- **Source** — Mays Jalal and Ali Taresh, *Iraq RF Spectrum Dataset:
  Real-World Multi-Band Raw IQ Measurements from Baghdad, Part 1*,
  [Zenodo record of 26 September 2026, DOI 10.5281/zenodo.22983712](https://doi.org/10.5281/zenodo.22983712).
  It replaces the [version 1.0 record](https://doi.org/10.5281/zenodo.22019720) of
  21 August 2026 and keeps the same data archives (`Day1-2.zip` has MD5
  `cce7f511f833b252bf4d1446b5aeeeed` in both); it adds a master metadata file for the
  complete dataset (295 recordings, Day1–Day20, published in five Zenodo parts) and a
  [new README](https://zenodo.org/records/22983712/files/README_Iraq_RF_Spectrum_Dataset_Part1.md?download=1)
  that states the license.
- **License of the RF dataset** — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
  Copyright © 2026 Mays Jalal.
- **Capture** — Outdoor, non-elevated measurement, Baghdad, 2 June 2026, evening, RTL-SDR V3
  with a telescopic antenna, GNU Radio with the Osmocom source, manual gains of 40 dB (RF),
  30 dB (IF) and 20 dB (baseband). The tuner centre is 100.5 MHz and the sample rate
  is 2.048 million complex samples per second. The recording lasts 465 s. Its start time
  (about 20:56) is estimated from the file's modification time, with a precision of a
  minute. No external RF calibration was used, so the samples carry no absolute power scale.
- **Excerpt** — First 0.75 s of `Day1-2/Day1-2/FM-outdoor_100.5e6MHz.iq`
  in `Day1-2.zip` (reproduced from the archive on 2026-11-18: the mapping below gives
  exactly the bytes of the compact file). The source uses little-endian complex float32. Map
  each I or Q component `v` to `round((v + 0.9953125) * 128)` to restore
  the recorder's 256 equally spaced level codes. The compact file stores
  these as unsigned bytes, I followed by Q, without a header. No tuning,
  resampling or demodulation was applied to the file during preparation.
- **SHA-256** — `72a9941497cb680287c0bee138926c803577ea6a59d0634304ec59a0890d6f7a`
