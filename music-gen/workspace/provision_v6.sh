#!/usr/bin/env bash
# Music-Gen v6 workspace provisioning (2026-10-04 container rebuild).
# Trimmed from provision.sh: drops Ardour/MuseScore/DawDreamer (unused by the v5/v6
# pipeline), keeps fluidsynth+GM, sfizz_render, Surge XT, Dexed, LV2 suites, and the
# python analysis/separation stack in the SYSTEM interpreter (/usr/bin/python3 is the
# pinned interpreter per docs/interpreter_guard_policy.md).
# Logs to workspace/provision_v6.log; idempotent-ish.
set -euo pipefail
SURGE_VERSION="${SURGE_VERSION:-1.3.4}"
DEXED_VERSION="${DEXED_VERSION:-1.0.1}"
SFIZZ_VERSION="${SFIZZ_VERSION:-1.2.3}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
export DEBIAN_FRONTEND=noninteractive

echo "== apt layer == $(date -u +%H:%M:%S)"
apt-get update -qq
apt-get install -y -qq \
  ffmpeg fluidsynth fluid-soundfont-gm \
  calf-plugins x42-plugins lsp-plugins-lv2 dragonfly-reverb-lv2 dpf-plugins-lv2 \
  avldrums.lv2 avldrums.lv2-soundfont synthv1-lv2 samplv1-lv2 drumkv1-lv2 \
  lilv-utils cmake build-essential pkg-config libsndfile1-dev libjack-jackd2-dev unzip

echo "== python layer (system /usr/bin/python3) == $(date -u +%H:%M:%S)"
PIP="/usr/bin/python3 -m pip"
$PIP install --quiet --upgrade pip
$PIP install --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cpu
$PIP install --quiet \
  numpy scipy scikit-learn matplotlib pandas \
  librosa pretty_midi mido soundfile pyloudnorm \
  pedalboard demucs stempeg \
  transformers nnAudio laion-clap

echo "== Surge XT ${SURGE_VERSION} == $(date -u +%H:%M:%S)"
if [ ! -d "/usr/lib/vst3/Surge XT.vst3" ]; then
  curl -sL -o "$WORK/surge-xt.deb" \
    "https://github.com/surge-synthesizer/releases-xt/releases/download/${SURGE_VERSION}/surge-xt-linux-x64-${SURGE_VERSION}.deb" \
    && apt-get install -y -qq "$WORK/surge-xt.deb" || echo "WARN: Surge XT install failed (non-fatal)"
fi

echo "== Dexed ${DEXED_VERSION} == $(date -u +%H:%M:%S)"
if [ ! -d "/usr/lib/vst3/Dexed.vst3" ]; then
  if curl -sL -o "$WORK/dexed.zip" \
    "https://github.com/asb2m10/dexed/releases/download/v${DEXED_VERSION}/dexed-${DEXED_VERSION}-lnx.zip"; then
    unzip -o -q "$WORK/dexed.zip" -d "$WORK/dexed" && mkdir -p /usr/lib/vst3 /usr/lib/clap \
      && cp -r "$WORK/dexed/Dexed.vst3" /usr/lib/vst3/ && cp "$WORK/dexed/Dexed.clap" /usr/lib/clap/ \
      || echo "WARN: Dexed unpack failed (non-fatal)"
  else echo "WARN: Dexed download failed (non-fatal)"; fi
fi

echo "== sfizz ${SFIZZ_VERSION} (libsfizz + sfizz_render) == $(date -u +%H:%M:%S)"
if ! command -v sfizz_render >/dev/null; then
  curl -sL -o "$WORK/sfizz.tar.gz" \
    "https://github.com/sfztools/sfizz/releases/download/${SFIZZ_VERSION}/sfizz-${SFIZZ_VERSION}.tar.gz"
  tar xzf "$WORK/sfizz.tar.gz" -C "$WORK"
  cmake -S "$WORK/sfizz-${SFIZZ_VERSION}" -B "$WORK/sfizz-build" \
    -DCMAKE_BUILD_TYPE=Release -DSFIZZ_RENDER=ON -DSFIZZ_VST=OFF -DSFIZZ_LV2=OFF \
    -DCMAKE_INSTALL_PREFIX=/usr >/dev/null
  cmake --build "$WORK/sfizz-build" -j"$(nproc)" >/dev/null
  cmake --install "$WORK/sfizz-build" >/dev/null
  ldconfig
fi

echo "== pre-seed demucs htdemucs + htdemucs_6s weights == $(date -u +%H:%M:%S)"
/usr/bin/python3 - <<'PY'
from demucs.pretrained import get_model
for name in ("htdemucs", "htdemucs_6s"):
    get_model(name); print(name, "cached")
PY

echo "== versions =="
/usr/bin/python3 - <<'PY'
import importlib
for m in ("numpy","scipy","torch","torchaudio","demucs","librosa","soundfile","mido","pretty_midi","sklearn","pedalboard","transformers","laion_clap","nnAudio","stempeg","pyloudnorm"):
    try: print(f"  {m:14s}", getattr(importlib.import_module(m),"__version__","ok"))
    except Exception as e: print(f"  {m:14s} MISSING ({type(e).__name__})")
PY
fluidsynth --version | head -1; ls -la /usr/share/sounds/sf2/; command -v sfizz_render && echo "sfizz_render OK"
echo "PROVISION_V6_DONE $(date -u +%H:%M:%S)"
