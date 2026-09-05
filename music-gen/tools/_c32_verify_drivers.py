#!/usr/bin/python3
"""c32 helper: AST-parse and rehash the four c32-touched sound_match files."""
import ast
import hashlib
import pathlib

FILES = [
    "scripts/sound_match/fine_fit_sf2_v2.py",
    "scripts/sound_match/fine_fit_sf2_drums.py",
    "scripts/sound_match/fine_fit_sf2_guitar.py",
    "scripts/sound_match/_serial_lock_op1.py",
]

for f in FILES:
    src = pathlib.Path(f).read_bytes()
    ast.parse(src.decode())
    h = hashlib.sha256(src).hexdigest()
    print(f"OK  sha={h}  {f}")
