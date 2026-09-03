---
created: 2026-08-29T19:20:00Z
cycle: 51
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc7-mix-balance-match
branch: fork-38eba9f21a61 clone-2 (Branch C)
---

# render_stem.py Signature v3 — Additive Kwargs Pre-Registration

**Pre-registration:** this document lands BEFORE any Python edit to
`scripts/palette_render/render_stem.py` (mtime hard, git-log advisory
per c46 path (ii) amendment). All three fanout branch discipline
invariants (byte-determinism × 2, NO PRNG, `/usr/bin/python3` guard)
apply to the extended signature.

## Ancestry

- c33 anchor: `render_stem(stem, instrument, out_dir) -> dict`
- c36 additive-kwargs extension: `render_stem(stem, instrument, out_dir, *, parameter_dict=None) -> dict`. Backwards-compat contract: `parameter_dict=None` → dispatch byte-identical to c33.
- **c51 Branch C signature v3 (this pre-registration):** add TWO additional keyword-only additive kwargs `eq_curve: dict | None = None` and `loudness_target: dict | None = None`. All three-None dispatch (`parameter_dict=None, eq_curve=None, loudness_target=None`) is byte-identical to c33 anchor path AND to c36 additive path.

## Signature v3

```python
def render_stem(stem: str, instrument: str, out_dir: Path,
                *,
                parameter_dict: dict | None = None,
                eq_curve: dict | None = None,
                loudness_target: dict | None = None) -> dict:
    ...
```

## Backwards-compatibility contract

- **c33 regression:** 3 c33 anchor SHAs — `drums-fluidsynth`, `bass-sfizz`,
  `other-sfizz` — reproduce byte-identically under
  `render_stem(stem, instrument, out_dir)` (positional-only, no kwargs).
- **c36 regression:** 3 c36 anchor SHAs (documented in
  `data/palette_render_v3/backwards_compat_check.json` — bass 6b9a5219…,
  other a2e5d058…, combined a8c1557c…) reproduce byte-identically under
  `render_stem(..., parameter_dict=None)`. When `parameter_dict` is
  non-None AND (`eq_curve is None`) AND (`loudness_target is None`), the
  c36 additive path is preserved bit-for-bit.
- **c51 new path:** activated when `eq_curve is not None` OR
  `loudness_target is not None`. VST3 branches (Surge XT / Dexed)
  explicitly raise `NotImplementedError` when either is non-None
  (respects c35 VST3 anti-pattern lock).

## eq_curve schema

`eq_curve` is a dict describing a deterministic 12-band log-spaced IIR
biquad EQ chain. Applied to the rendered stem (post-canonicalization,
before loudness match). Schema:

```json
{
  "method": "iirpeak_12band_log_spaced",
  "n_bands": 12,
  "f_low_hz": 20.0,
  "f_high_hz": 20000.0,
  "Q": 1.4,
  "target_spectrum_source_sha256": "<hex>",
  "band_center_freqs_hz": [ ... 12 values ... ],
  "band_gains_db": [ ... 12 values ... ]
}
```

The 12 band centers are computed at fit time by
`np.geomspace(20.0, 20000.0, 12)` (deterministic; no PRNG). The band
gains are computed from the original stem's average log-magnitude
spectrum on the chosen section — see `rc7_eq_curve_fit_method.md` for
the fit procedure. Filter application uses
`scipy.signal.iirpeak(f_c, Q=1.4, fs=44100)` per band with the gain
applied to the wet path as `gain_linear = 10**(gain_db/20)` and
`out = (1 - wet_mix) * dry + wet_mix * gain_linear * band_filter(dry)`,
where `wet_mix = 1.0` (each band's boost/cut is directly applied). The
12 filters are cascaded in ascending center-frequency order.

If `scipy.signal.iirpeak` is NOT importable (fetchability check), the
fallback is a pure-numpy 12-band mel-approximated shelving chain using
first-order coefficients; this fallback is recorded in the render's
`dispatch_summary.json` fallback_used=true and the report surfaces it
honestly. NO fabricated success — if EQ cannot land, `dispatch_summary`
records the failure and the render still emits the pre-EQ (post-loudness)
stem for panel comparison.

## loudness_target schema

`loudness_target` is a dict describing target RMS + LUFS-S values (both
in dB, both compared post-EQ). Schema:

```json
{
  "target_rms_db": -14.405,
  "target_lufs_s_db": -15.732,
  "reference_sha256": "<hex of the original stem>",
  "max_gain_db": 24.0
}
```

Applied AFTER `eq_curve`. Loudness match method:

1. Compute post-EQ RMS on mono mixdown.
2. Delta_rms_db = target_rms_db - measured_rms_db.
3. Apply scalar gain `10**(delta_rms_db/20)` clamped to `[-max_gain_db, +max_gain_db]`.
4. Recompute post-gain RMS; assert `|measured - target| <= 3.0 dB` (A7 accept).

LUFS-S is a diagnostic report metric (recorded in
`dispatch_summary.json`) but the primary accept is on RMS error since
LUFS-S requires pyloudnorm (fetchability-blocked on some environments —
falls back to an internal EBU-approximation using the same K-weighting
polynomial c4 `M-TEX-1/panel/envelope` uses; on env failure, LUFS-S =
`null` with reason and A7 gates on RMS alone). Honest first-class
degradation, no fabricated numbers.

## VST3 lock (c35 anti-pattern)

When `instrument ∈ {surge_xt, dexed}` AND (`eq_curve is not None` OR
`loudness_target is not None`), `render_stem` raises
`NotImplementedError` with message naming the c35 STILL_GAP anchor.
This mirrors the c36 handling of `parameter_dict` on VST3 branches
verbatim. No VST3 render is attempted this cycle.

## Return value extension

The result dict gains three optional keys when the new kwargs are used:

- `"eq_applied"`: True/False
- `"eq_bands_gains_db"`: list of 12 floats (only present when eq_applied)
- `"loudness_error_rms_db"`: float (only present when loudness_target used)

The base c33/c36 keys (`stem`, `instrument`, `render_run1_sha`,
`render_run2_sha`, `sha_equal`, `run1_wav_path`, ...) remain unchanged.

## Byte-determinism × 2 contract

- Two fresh `tempfile.mkdtemp()` runs of the c51 new path (`eq_curve`
  and/or `loudness_target` non-None) produce SHA-equal `render.wav`.
- The old-chain baseline comparison row (`panel_baseline_old_chain.tsv`)
  is measured but is READ-ONLY (does NOT rewrite c33 anchor).

## Files touched by this pre-registration cycle

- `scripts/palette_render/render_stem.py` — additive-kwargs edit
- `scripts/recreate_v2/rc7_mix_balance.py` — new implementation (replaces c50 NotImplementedError stub)
- `data/recreate_v2/rc7_out/` — new (per-song rendered mix outputs, deterministic)
- `docs/rc7_impl_report.md` — deliverable report

## Author

- Cycle: 51
- Branch: fork-38eba9f21a61 clone-2 (Branch C)
- Milestone: `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match`
- Author-email: cyd7bevdr@mozmail.com (attribution only)
