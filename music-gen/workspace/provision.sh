#!/usr/bin/env bash
# Music-Gen workspace provisioning.
#
# Installs the full open-source toolchain the autonomous run depends on
# (see music-gen/README.md, "Workspace pre-provisioning"). Idempotent-ish:
# safe to re-run; apt/pip skip what is already present.
#
# Verified on Ubuntu 24.04 (2026-08-28). After running, execute
#   python3 smoke_test.py
# and require all stages green before launching the run.
set -euo pipefail

SURGE_VERSION="${SURGE_VERSION:-1.3.4}"
DEXED_VERSION="${DEXED_VERSION:-1.0.1}"
SFIZZ_VERSION="${SFIZZ_VERSION:-1.2.3}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "== apt layer =="
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
# DAW, score tool, media, sampler+GM soundfont, plugin suites, LV2 tooling,
# headless X fallback, build deps for sfizz.
apt-get install -y -qq \
  ardour musescore3 ffmpeg \
  fluidsynth fluid-soundfont-gm \
  calf-plugins x42-plugins lsp-plugins-lv2 \
  amsynth dpf-plugins-lv2 dragonfly-reverb-lv2 \
  avldrums.lv2 avldrums.lv2-soundfont \
  synthv1-lv2 samplv1-lv2 drumkv1-lv2 zynaddsubfx \
  lilv-utils xvfb \
  cmake build-essential pkg-config libsndfile1-dev libjack-jackd2-dev

echo "== python layer =="
# CPU-only torch first so demucs does not pull CUDA wheels.
pip install --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install --quiet \
  dawdreamer pedalboard \
  librosa pretty_midi mido soundfile \
  yt-dlp demucs basic-pitch

echo "== Surge XT ${SURGE_VERSION} (official .deb) =="
if [ ! -d "/usr/lib/vst3/Surge XT.vst3" ]; then
  curl -sL -o "$WORK/surge-xt.deb" \
    "https://github.com/surge-synthesizer/releases-xt/releases/download/${SURGE_VERSION}/surge-xt-linux-x64-${SURGE_VERSION}.deb"
  apt-get install -y -qq "$WORK/surge-xt.deb"
fi

echo "== Dexed ${DEXED_VERSION} (official linux build) =="
if [ ! -d "/usr/lib/vst3/Dexed.vst3" ]; then
  curl -sL -o "$WORK/dexed.zip" \
    "https://github.com/asb2m10/dexed/releases/download/v${DEXED_VERSION}/dexed-${DEXED_VERSION}-lnx.zip"
  unzip -o -q "$WORK/dexed.zip" -d "$WORK/dexed"
  cp -r "$WORK/dexed/Dexed.vst3" /usr/lib/vst3/
  mkdir -p /usr/lib/clap && cp "$WORK/dexed/Dexed.clap" /usr/lib/clap/
fi

echo "== sfizz ${SFIZZ_VERSION} (source build: libsfizz + sfizz_render) =="
if ! command -v sfizz_render >/dev/null; then
  curl -sL -o "$WORK/sfizz.tar.gz" \
    "https://github.com/sfztools/sfizz/releases/download/${SFIZZ_VERSION}/sfizz-${SFIZZ_VERSION}.tar.gz"
  tar xzf "$WORK/sfizz.tar.gz" -C "$WORK"
  cmake -S "$WORK/sfizz-${SFIZZ_VERSION}" -B "$WORK/sfizz-build" \
    -DCMAKE_BUILD_TYPE=Release -DSFIZZ_RENDER=ON -DSFIZZ_VST=OFF \
    -DCMAKE_INSTALL_PREFIX=/usr >/dev/null
  cmake --build "$WORK/sfizz-build" -j"$(nproc)" >/dev/null
  cmake --install "$WORK/sfizz-build" >/dev/null
  ldconfig
fi

echo "== pre-seed demucs weights (so the run never blocks on a download) =="
python3 - <<'PY'
from demucs.pretrained import get_model
get_model("htdemucs")
print("htdemucs weights cached")
PY

echo
echo "Provisioning complete. Now run: python3 smoke_test.py"
