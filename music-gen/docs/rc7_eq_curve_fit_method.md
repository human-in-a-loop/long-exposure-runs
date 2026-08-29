---
created: 2026-08-29T19:20:30Z
cycle: 51
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc7-mix-balance-match
---

# RC7 EQ Curve Fit Method — Deterministic 12-Band Log-Spaced IIR Fit

**Pre-registration:** this document lands BEFORE any Python edit under
`scripts/palette_render/render_stem.py` or `scripts/recreate_v2/rc7_mix_balance.py`
(mtime hard, git-log advisory per c46 path (ii)).

Frozen prior to landing code:

- Center frequencies: `np.geomspace(20.0, 20000.0, 12)` — 12 log-spaced
  bands from 20 Hz to 20 kHz. All 12 centers pinned in the resulting
  `dispatch_summary.json.eq_curve.band_center_freqs_hz`.
- Filter type: `scipy.signal.iirpeak(f_c, Q=1.4, fs=44100)` per band.
- Q: **1.4** (locked).
- Fit target: the ORIGINAL stem's per-band average log-magnitude spectrum
  on the chosen section (from `focus_set_v2.json.chosen_section`).

## Fit procedure (deterministic, NO PRNG)

Given an original stem `x_orig` and a rendered stem `x_render`:

1. Extract the chosen section of both stems.
2. Mono mixdown (mean of L+R channels).
3. Compute FFT magnitude spectrum via `numpy.fft.rfft` with `n_fft=8192`, hop=n_fft (no window average — one long window over the section):
   - `X = np.abs(np.fft.rfft(mono, n=n_fft))` per stem
4. For each of 12 band centers `f_c`, compute the average log-magnitude on the band `[f_c/√2, f_c×√2]`:
   - `mag_orig[b] = mean(20*log10(X_orig[bin_lo:bin_hi] + 1e-10))`
   - `mag_render[b] = mean(20*log10(X_render[bin_lo:bin_hi] + 1e-10))`
5. Target gain per band: `gain_db[b] = mag_orig[b] - mag_render[b]`
6. Clamp: `gain_db[b] = clip(gain_db[b], -12.0, +12.0)` (locked ±12 dB per band; total EQ can shape ~24 dB peak-to-peak; loudness match handles broadband level after).

## Filter application

Chain the 12 peaking biquads in ascending center-frequency order:

```python
from scipy.signal import iirpeak, lfilter
out = mono_dry.copy()
for f_c, gain_db in zip(centers, gains_db):
    b, a = iirpeak(f_c, Q=1.4, fs=44100)
    gain_lin = 10.0 ** (gain_db / 20.0)
    band = lfilter(b, a, out)
    out = out + (gain_lin - 1.0) * band   # additive boost/cut on the resonant band
```

Stereo application: apply the SAME filter chain independently to L and
R channels (channel-parallel; no coupling to preserve stereo image).
Determinism: same input samples + same filter coefs → same output
samples (double-precision `float64` intermediate; final cast to
`float32` for canonicalization).

## Fallback

If `scipy.signal.iirpeak` cannot import (fetchability-check via
`try: import scipy.signal`), the fallback is:

```python
# Pure-numpy first-order shelf approximation per band
# g[n] = alpha * g[n-1] + (1-alpha) * x[n]   (per-band low-pass, then subtract)
```

The fallback produces a DIFFERENT sound but preserves byte-determinism
× 2 within the cycle. Fallback is recorded honestly in
`dispatch_summary.json.eq_fallback_used=true`, and the report §Fallback
surfaces this without swallowing the failure.

## RMS + LUFS-S loudness match

Applied AFTER the EQ chain. RMS match:

1. `measured_rms_db = 20*log10(sqrt(mean(mono**2)))`
2. `delta_db = target_rms_db - measured_rms_db`
3. `scalar = 10**(delta_db/20)`, clip to `[10**(-24/20), 10**(24/20)]` (±24 dB max)
4. `out *= scalar`; recompute; assert `|measured_after - target| <= 3.0 dB`

LUFS-S: computed via internal K-weighting polynomial (c4 M-TEX-1/panel/envelope
convention). Reference: EBU R128 K-filter — 2-pass biquad (pre-filter +
high-shelf). If pyloudnorm is importable, use it (byte-different across
versions — first fetchability check pins version in dispatch_summary);
else fall back to internal filter. LUFS-S is REPORT-ONLY (A7 accept is
on RMS).

## Determinism × 2 anchoring

- Same original stem SHA + same rendered stem SHA + same n_fft +
  same np.geomspace call → identical `gain_db` per band.
- Same filter coefs (deterministic `iirpeak`) + same input samples
  → identical output.
- Two fresh `tempfile.mkdtemp()` runs produce SHA-equal outputs.

## Author

- Cycle: 51, Branch: fork-38eba9f21a61 clone-2
- Milestone: `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match`
- Author-email: cyd7bevdr@mozmail.com
