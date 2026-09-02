# MuScriptor provisioning receipts — 2026-09-02

Package: `muscriptor` 0.3.0 (pip), installed into
`workspace/learned_transcribers_venv` (python 3.11.15, torch 2.14.0+cpu).

Weights: **muscriptor-medium** (1.23 GB safetensors), fetched from the open
community mirror `cocktailpeanut/muscriptor-medium` (canonical
`MuScriptor/muscriptor-medium` on HuggingFace is gated behind free license
acceptance; license CC-BY-NC-4.0 — this project is experimental and
never released, so non-commercial terms are satisfied).

Local path (gitignored): `workspace/models/muscriptor-medium/`

sha256:
```
43e13a70fc9ae0af36b7447c06f3eac2282daeb69d79c1ff840ede7fdaa26a3b  config.json
ac80adbdf85d87231735fd948af7013441c0afced316c4e9067fd5d8a7fb97ec  model.safetensors
```

Invocation (verified):
```
learned_transcribers_venv/bin/muscriptor transcribe <audio> \
  -m workspace/models/muscriptor-medium/model.safetensors \
  -d cpu --detect-tempo best-effort [-f midi|json|jsonl]
```

Greedy decoding is the default → deterministic output. `--instruments`
whitelists instrument groups (see `muscriptor list-instruments`).

Model-size policy: medium is the campaign default (CPU-only box; large is
5.47 GB). If medium is the binding quality constraint on a song, that is an
operator-report, not a license to hand-roll DSP.
