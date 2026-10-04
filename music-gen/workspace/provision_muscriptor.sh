#!/usr/bin/env bash
# Re-provision MuScriptor per workspace/MUSCRIPTOR_RECEIPTS.md (2026-09-02):
#   muscriptor 0.3.0 in workspace/learned_transcribers_venv (python 3.11, CPU torch)
#   weights: muscriptor-medium from the open mirror cocktailpeanut/muscriptor-medium
# Verifies the two sha256 receipts before declaring success.
set -euo pipefail
cd "$(dirname "$0")/.."
VENV=workspace/learned_transcribers_venv
MODELS=workspace/models/muscriptor-medium
mkdir -p "$MODELS"
echo "== venv == $(date -u +%H:%M:%S)"
if [ ! -x "$VENV/bin/python" ]; then uv venv "$VENV" --python 3.11 --quiet; fi
uv pip install --python "$VENV/bin/python" --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cpu
uv pip install --python "$VENV/bin/python" --quiet "muscriptor==0.3.0"
"$VENV/bin/muscriptor" --help | head -3
echo "== weights == $(date -u +%H:%M:%S)"
BASE="https://huggingface.co/cocktailpeanut/muscriptor-medium/resolve/main"
for f in config.json model.safetensors; do
  if [ ! -s "$MODELS/$f" ]; then curl -sL --retry 5 --retry-delay 5 -C - -o "$MODELS/$f" "$BASE/$f"; fi
done
cat > "$MODELS/SHA256SUMS" <<'EOF'
43e13a70fc9ae0af36b7447c06f3eac2282daeb69d79c1ff840ede7fdaa26a3b  config.json
ac80adbdf85d87231735fd948af7013441c0afced316c4e9067fd5d8a7fb97ec  model.safetensors
EOF
(cd "$MODELS" && sha256sum -c SHA256SUMS)
echo "MUSCRIPTOR_DONE $(date -u +%H:%M:%S)"
