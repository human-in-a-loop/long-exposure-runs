#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T09:08:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v4
# ---
"""sfizz SFZ opcode-file-rewrite fallback (c36 deferred).

The on-disk anchor SFZ at data/texture/test.sfz is never modified in place.
Given cutoff (Hz) and/or resonance (dB), we synthesise a rewritten SFZ into
a fresh tempfile.mkstemp() path, inject `fil_cutoff=<Hz>` and/or
`fil_resonance=<dB>` opcodes into every `<region>` block, return the temp
Path. The caller invokes sfizz_render with the temp path, then unlinks it.

Determinism: no PRNG. The temp path name is process-local but the file
CONTENT is a pure function of (source SFZ bytes, cutoff, resonance) —
sfizz_render's output depends only on file content + MIDI + sample rate,
so byte-determinism of downstream render is preserved.

NO network. /usr/bin/python3 guarded. No sidecar_nonfactor imports.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable


def _inject_opcodes_into_region(region_body: str,
                                cutoff: float | None,
                                resonance: float | None) -> str:
    """Append fil_cutoff/fil_resonance lines to a <region> block body.

    We append rather than overwrite: if the source SFZ ever grew a
    fil_cutoff of its own, SFZ semantics say the LAST occurrence wins,
    so the appended line takes effect deterministically.
    """
    extra_lines: list[str] = []
    if cutoff is not None:
        extra_lines.append(f"fil_cutoff={float(cutoff):.6f}")
    if resonance is not None:
        extra_lines.append(f"fil_resonance={float(resonance):.6f}")
    if not extra_lines:
        return region_body
    # Preserve trailing newline if present.
    trailing_nl = region_body.endswith("\n")
    body = region_body.rstrip("\n")
    body = body + "\n" + "\n".join(extra_lines)
    if trailing_nl:
        body = body + "\n"
    return body


def rewrite_sfz_content(source_text: str,
                        cutoff: float | None,
                        resonance: float | None,
                        source_dir: Path | None = None) -> str:
    """Return the rewritten SFZ text.

    Splits on `<region>` headers, appends the filter opcodes to each
    region body. If the file has no `<region>` header we fall back to a
    single virtual region (append at end) — this preserves the c9-locked
    test.sfz behaviour where the whole file is one implicit region.

    When `source_dir` is provided, rewrites relative `sample=<path>` opcodes
    to absolute paths under that directory (SFZ resolves samples relative
    to the SFZ file, so a tempfile in /tmp would otherwise miss samples).
    """
    if source_dir is not None:
        source_text = _absolutize_sample_paths(source_text, source_dir)
    if "<region>" not in source_text:
        # Implicit single region — append at end.
        return _inject_opcodes_into_region(source_text, cutoff, resonance)
    # Split on `<region>` but preserve the delimiter.
    parts = source_text.split("<region>")
    # parts[0] is the preamble; parts[1:] each contain the body of one region
    # up to the next `<region>` (or EOF).
    out = [parts[0]]
    for body in parts[1:]:
        rewritten = _inject_opcodes_into_region(body, cutoff, resonance)
        out.append("<region>")
        out.append(rewritten)
    return "".join(out)


def _absolutize_sample_paths(text: str, source_dir: Path) -> str:
    """Replace `sample=<relative>` with `sample=<absolute>` so the rewritten
    SFZ can live anywhere on disk. Only rewrites values that don't already
    start with `/`.
    """
    lines = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("sample="):
            value = stripped[len("sample="):].strip()
            if value and not value.startswith("/"):
                abs_path = (source_dir / value).resolve()
                leading_ws = line[: len(line) - len(line.lstrip())]
                trailing_nl = "\n" if line.endswith("\n") else ""
                line = f"{leading_ws}sample={abs_path}{trailing_nl}"
        lines.append(line)
    return "".join(lines)


def rewrite_sfz_to_temp(source_sfz: Path,
                        cutoff: float | None,
                        resonance: float | None) -> Path:
    """Rewrite source_sfz to a fresh temp path with cutoff/resonance
    opcodes injected into every region. Returns the temp Path.

    Caller MUST unlink the returned path after use.
    """
    if not source_sfz.is_file():
        raise RuntimeError(f"source SFZ missing: {source_sfz}")
    source_text = source_sfz.read_text()
    rewritten = rewrite_sfz_content(
        source_text, cutoff, resonance, source_dir=source_sfz.parent
    )
    # tempfile.mkstemp returns (fd, name); close fd, keep name.
    fd, name = tempfile.mkstemp(prefix="palette_v4_sfz_", suffix=".sfz")
    tmp = Path(name)
    import os
    with os.fdopen(fd, "w") as f:
        f.write(rewritten)
    return tmp
