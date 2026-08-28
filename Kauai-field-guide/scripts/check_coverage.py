#!/usr/bin/env python3
"""Coverage checker for the field guide.

Per-species checks:
  - required top-level fields present and non-empty
  - status in the biogeographic enum
  - coastal_zones a non-empty subset of the zone enum
  - tier in {common, notable, rare_exotic}
  - how_to_identify: dict with growth_form, leaves, flowers/fruit (at least one),
    size, zone_hint; clinchers list has 2-4 items; look_alikes list present (may be empty).
  - >= 2 total visuals (images + diagrams), any mix.
  - each image entry has a matching record in data/images.lock.json with
    non-empty author, license (in allow-list), license_url, source, source_page.
  - >= 1 citation number referring to a real REFERENCES.md entry.

Tier-count check reports counts vs. the cycle-1 slice targets (informational,
not fatal here — the run-end target is 45+ overall).
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

import yaml

# Shared license allow-list.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _licenses import ALLOWED_LICENSES  # single source of truth

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SPECIES_DIR = DATA / "species"
IMAGES_LOCK = DATA / "images.lock.json"
REFS_FILE = ROOT / "REFERENCES.md"
REFS_SHARDS_DIR = DATA / "references"
DIAGRAMS_DIR = ROOT / "site" / "assets" / "diagrams"
CITATION_TOKEN_RE = re.compile(r"^([A-Z]):(\d+)$")
STATUS_ENUM = {"endemic", "indigenous", "polynesian_introduction", "modern_introduction", "invasive"}
ZONE_ENUM = {"strand", "dune", "sea_cliff", "valley_mouth", "riparian"}
TIER_ENUM = {"common", "notable", "rare_exotic"}
REQUIRED_TOP = ["slug", "scientific_name", "authority", "family", "common_names",
                "status", "coastal_zones", "tier", "occurrence_notes",
                "how_to_identify", "ecology", "citations"]
# 'images' key must be PRESENT (even if []) but may legitimately be empty
# for SVG-only species; the substantive >=2-visuals rule below handles
# whether that empty images list is actually acceptable.
REQUIRED_PRESENT = ["images"]


def load_refs() -> tuple[set[int], set[str]]:
    """Return (base_ref_nums, shard_token_set).

    base_ref_nums holds integer ids from REFERENCES.md.
    shard_token_set holds "X:n" tokens defined by data/references/branch-*.md.
    """
    pat = re.compile(r"^\[(\d+)\]")
    nums: set[int] = set()
    tokens: set[str] = set()
    if REFS_FILE.exists():
        for line in REFS_FILE.read_text().splitlines():
            m = pat.match(line.strip())
            if m:
                nums.add(int(m.group(1)))
    if REFS_SHARDS_DIR.exists():
        for shard in sorted(REFS_SHARDS_DIR.glob("branch-*.md")):
            stem = shard.stem  # branch-a
            letter = stem[len("branch-"):].upper()
            if len(letter) != 1:
                continue
            for line in shard.read_text().splitlines():
                m = pat.match(line.strip())
                if m:
                    tokens.add(f"{letter}:{int(m.group(1))}")
    return nums, tokens


def check_species(sp: dict, images: dict, ref_nums: set[int], ref_tokens: set[str]) -> list[str]:
    errs = []
    slug = sp.get("slug", "<no-slug>")
    for f in REQUIRED_TOP:
        if not sp.get(f):
            errs.append(f"{slug}: missing/empty required field '{f}'")
    for f in REQUIRED_PRESENT:
        if f not in sp:
            errs.append(f"{slug}: missing required field '{f}' (may be empty list)")

    if sp.get("status") not in STATUS_ENUM:
        errs.append(f"{slug}: status '{sp.get('status')}' not in enum {sorted(STATUS_ENUM)}")

    zones = sp.get("coastal_zones") or []
    if not zones:
        errs.append(f"{slug}: coastal_zones is empty")
    for z in zones:
        if z not in ZONE_ENUM:
            errs.append(f"{slug}: coastal_zone '{z}' not in enum {sorted(ZONE_ENUM)}")

    tier = sp.get("tier")
    if tier not in TIER_ENUM:
        errs.append(f"{slug}: tier '{tier}' not in enum {sorted(TIER_ENUM)}")

    common = sp.get("common_names") or {}
    if not (common.get("hawaiian") or common.get("english")):
        errs.append(f"{slug}: common_names.hawaiian OR common_names.english must be non-empty")

    idb = sp.get("how_to_identify") or {}
    for k in ("growth_form", "leaves", "size", "zone_hint"):
        if not idb.get(k):
            errs.append(f"{slug}: how_to_identify.{k} is missing/empty")
    if not (idb.get("flowers") or idb.get("fruit")):
        errs.append(f"{slug}: how_to_identify needs at least one of flowers/fruit")
    clinch = idb.get("clinchers") or []
    if not (2 <= len(clinch) <= 4):
        errs.append(f"{slug}: how_to_identify.clinchers must be 2-4 items (found {len(clinch)})")
    look_alikes = idb.get("look_alikes")
    if look_alikes is None or not isinstance(look_alikes, list):
        errs.append(f"{slug}: how_to_identify.look_alikes must be a list")
    elif len(look_alikes) < 1:
        errs.append(f"{slug}: how_to_identify.look_alikes must have >=1 entry (found 0)")

    imgs = sp.get("images") or []
    diags = sp.get("diagrams") or []
    if len(imgs) + len(diags) < 2:
        errs.append(f"{slug}: needs >=2 total visuals (found {len(imgs)} photos + {len(diags)} diagrams)")

    for i, e in enumerate(imgs):
        iid = e.get("id")
        if not iid:
            errs.append(f"{slug}: images[{i}] missing 'id'")
            continue
        rec = images.get(iid)
        if not rec:
            errs.append(f"{slug}: images[{i}] id '{iid}' not in data/images.lock.json")
            continue
        for req in ("author", "license", "license_url", "source", "source_page", "path"):
            if not rec.get(req):
                errs.append(f"{slug}: image '{iid}' missing lock field '{req}'")
        if rec.get("license") and rec["license"] not in ALLOWED_LICENSES:
            errs.append(f"{slug}: image '{iid}' license '{rec['license']}' not in allow-list")
        if rec.get("path"):
            on_disk = ROOT / "site" / rec["path"]
            if not on_disk.exists():
                errs.append(f"{slug}: image '{iid}' file missing on disk at site/{rec['path']}")

    for i, d in enumerate(diags):
        fn = d.get("file")
        if not fn:
            errs.append(f"{slug}: diagrams[{i}] missing 'file'")
            continue
        if not (DIAGRAMS_DIR / fn).exists():
            errs.append(f"{slug}: diagram file '{fn}' missing at site/assets/diagrams/")

    cits = sp.get("citations") or []
    if not cits:
        errs.append(f"{slug}: needs >=1 citation")
    for c in cits:
        if isinstance(c, int) or (isinstance(c, str) and c.isdigit()):
            n = int(c)
            if n not in ref_nums:
                errs.append(f"{slug}: citation [{n}] has no entry in REFERENCES.md")
        elif isinstance(c, str) and CITATION_TOKEN_RE.match(c):
            if c not in ref_tokens:
                errs.append(f"{slug}: citation token '{c}' has no entry in data/references/")
        else:
            errs.append(f"{slug}: citation '{c!r}' is neither an int nor a valid X:n token")

    return errs


def main() -> int:
    if not SPECIES_DIR.exists():
        print("check_coverage: no data/species/ directory", file=sys.stderr)
        return 2
    images = {}
    if IMAGES_LOCK.exists():
        images = json.loads(IMAGES_LOCK.read_text())
    ref_nums, ref_tokens = load_refs()

    species = []
    for p in sorted(SPECIES_DIR.glob("*.yaml")):
        with p.open() as f:
            species.append(yaml.safe_load(f))

    all_errs = []
    tier_counts = {"common": 0, "notable": 0, "rare_exotic": 0}
    for sp in species:
        errs = check_species(sp, images, ref_nums, ref_tokens)
        all_errs.extend(errs)
        if sp.get("tier") in tier_counts:
            tier_counts[sp["tier"]] += 1

    print(f"check_coverage: {len(species)} species; per-tier: "
          f"common={tier_counts['common']} notable={tier_counts['notable']} rare_exotic={tier_counts['rare_exotic']}")
    if all_errs:
        print(f"check_coverage: {len(all_errs)} problems")
        for e in all_errs:
            print(f"  {e}")
        return 1
    print("check_coverage: OK — all species pass required-field + visual + citation checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
