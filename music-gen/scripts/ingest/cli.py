"""CLI entry point for the ingestion chassis.

Usage:
    python -m scripts.ingest.cli ingest <path>          # local file/folder
    python -m scripts.ingest.cli ingest --youtube URL   # playlist URL
    python -m scripts.ingest.cli replay   <manifest.jsonl>
    python -m scripts.ingest.cli validate <manifest.jsonl>
    python -m scripts.ingest.cli probe

Every substantive path uses the same seam as the module APIs so tests and
manual invocations cannot diverge.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from scripts.ingest import egress_probe, harvester, provenance
from scripts.ingest.chunker import chunk
from scripts.ingest.provenance import validate_manifest, write_manifest, read_manifest


CLIP_DIR = Path("data/ingestion/clips")
MANIFEST_DIR = Path("data/ingestion/manifests")


def _cmd_ingest(args: argparse.Namespace) -> int:
    if args.youtube:
        ms = harvester.youtube_playlist(args.youtube, CLIP_DIR, MANIFEST_DIR)
    else:
        p = Path(args.path)
        if p.is_dir():
            ms = harvester.local_folder(p, CLIP_DIR, MANIFEST_DIR)
        elif p.is_file():
            with tempfile.TemporaryDirectory() as td:
                d = Path(td) / (p.stem + ".wav")
                harvester._decode_to_wav(p, d)
                m = harvester._emit("local", str(p.resolve()), d,
                                    CLIP_DIR, MANIFEST_DIR)
                ms = [m]
        else:
            print(f"no such path: {p}", file=sys.stderr)
            return 2
    for m in ms:
        print(m)
    return 0


def _cmd_replay(args: argparse.Namespace) -> int:
    mp = Path(args.manifest)
    src, _ = read_manifest(mp)
    ref = Path(src["source_ref"])
    # Prefer the on-disk source; if source is a URL (youtube), the caller
    # must pass --source explicitly.
    source = Path(args.source) if args.source else ref
    if not source.exists():
        print(f"cannot find source {source}. Pass --source PATH.",
              file=sys.stderr)
        return 2
    mismatches = provenance.replay(mp, source, CLIP_DIR)
    if mismatches:
        print("REPLAY FAIL:")
        for m in mismatches:
            print(" -", m)
        return 1
    print("REPLAY OK")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    errs = validate_manifest(Path(args.manifest),
                             check_clip_files=not args.no_files)
    if errs:
        print("VALIDATE FAIL:")
        for e in errs:
            print(" -", e)
        return 1
    print("VALIDATE OK")
    return 0


def _cmd_probe(_args: argparse.Namespace) -> int:
    rec = egress_probe.probe()
    print(json.dumps(rec, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="scripts.ingest.cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    ing = sub.add_parser("ingest")
    ing.add_argument("path", nargs="?", default=None)
    ing.add_argument("--youtube", default=None,
                     help="YouTube playlist URL (mutually exclusive with path)")
    ing.set_defaults(fn=_cmd_ingest)

    rp = sub.add_parser("replay")
    rp.add_argument("manifest")
    rp.add_argument("--source", default=None)
    rp.set_defaults(fn=_cmd_replay)

    vl = sub.add_parser("validate")
    vl.add_argument("manifest")
    vl.add_argument("--no-files", action="store_true",
                    help="skip on-disk clip file check")
    vl.set_defaults(fn=_cmd_validate)

    pb = sub.add_parser("probe")
    pb.set_defaults(fn=_cmd_probe)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
