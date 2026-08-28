#!/usr/bin/env python3
"""Render the Kauai Coastal Field Guide from data/ into site/.

Reads:
  data/species/*.yaml        — one file per species (source of truth)
  data/images.lock.json      — verified image manifest from fetch_images.py
  data/glossary.yaml         — glossary terms
  REFERENCES.md              — numbered references

Writes:
  site/index.html
  site/species/<slug>.html
  site/glossary.html
  site/safety-and-ethics.html
  site/credits.html
  site/references.html

Assumes site/style.css, site/filter.js, and site/assets/{photos,diagrams}
already exist (produced separately). Output is fully offline.
"""
from __future__ import annotations
import html
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT / "site"
SPECIES_DIR = DATA / "species"
IMAGES_LOCK = DATA / "images.lock.json"
GLOSSARY_FILE = DATA / "glossary.yaml"
REFS_FILE = ROOT / "REFERENCES.md"
REFS_SHARDS_DIR = DATA / "references"
REFS_MAP_FILE = DATA / "references.map.json"
IMAGE_MANIFEST = DATA / "images.json"
IMAGE_SHARD_GLOB = "images.branch-*.json"
# Token like "A:3" — shard-letter (single uppercase) + colon + 1-based index.
CITATION_TOKEN_RE = re.compile(r"^([A-Z]):(\d+)$")
# Same token embedded inline in prose text, wrapped in [ ] like "[A:3]".
INLINE_CITATION_TOKEN_RE = re.compile(r"\[([A-Z]):(\d+)\]")


def rewrite_inline_citation_tokens(text: str, token_map: dict) -> str:
    """Rewrite prose-embedded [X:n] tokens to their resolved global integers.
    Unknown tokens are left as-is so that build errors surface at check time;
    callers should also gate this against token_map completeness."""
    def _sub(m):
        tok = f"{m.group(1)}:{m.group(2)}"
        if tok in token_map:
            return f"[{token_map[tok]}]"
        return m.group(0)
    return INLINE_CITATION_TOKEN_RE.sub(_sub, text)

TIER_LABELS = {
    "common": ("COMMON", "Plants a hiker or boater will actually encounter on beaches, dunes, sea cliffs, and valley mouths."),
    "notable": ("NOTABLE", "Culturally or ecologically significant natives and Polynesian-introduced canoe plants."),
    "rare_exotic": ("RARE & EXOTIC", "Rare endemics of the Nā Pali coastal cliffs plus notable invasives that dominate or threaten these habitats."),
}
TIER_ORDER = ["common", "notable", "rare_exotic"]
ZONE_LABELS = {
    "strand": "Beach strand",
    "dune": "Dune",
    "sea_cliff": "Sea cliff",
    "valley_mouth": "Valley mouth",
    "riparian": "Riparian",
}
ZONE_ORDER = ["strand", "dune", "sea_cliff", "valley_mouth", "riparian"]
STATUS_LABELS = {
    "endemic": "Endemic",
    "indigenous": "Indigenous (native, non-endemic)",
    "polynesian_introduction": "Polynesian introduction (canoe plant)",
    "modern_introduction": "Modern introduction",
    "invasive": "Invasive",
}


def load_species() -> list[dict]:
    species = []
    for path in sorted(SPECIES_DIR.glob("*.yaml")):
        with path.open() as f:
            data = yaml.safe_load(f)
        data["_path"] = str(path.relative_to(ROOT))
        species.append(data)
    return species


def load_images_lock() -> dict:
    if not IMAGES_LOCK.exists():
        return {}
    with IMAGES_LOCK.open() as f:
        return json.load(f)


def load_glossary() -> list[dict]:
    if not GLOSSARY_FILE.exists():
        return []
    with GLOSSARY_FILE.open() as f:
        data = yaml.safe_load(f) or []
    return data


def _parse_ref_file(path: Path) -> list[tuple[int, str]]:
    """Extract [N] entries from a numbered reference markdown file."""
    pat = re.compile(r"^\[(\d+)\]\s+(.*)$")
    entries = []
    for line in path.read_text().splitlines():
        m = pat.match(line.strip())
        if m:
            entries.append((int(m.group(1)), m.group(2)))
    return entries


def _shard_letter_from_name(fname: str) -> str:
    """references/branch-a.md -> 'A'."""
    stem = Path(fname).stem  # 'branch-a'
    if not stem.startswith("branch-"):
        raise ValueError(f"unrecognized shard reference filename: {fname}")
    letter = stem[len("branch-"):]
    if len(letter) != 1 or not letter.isalpha():
        raise ValueError(f"shard reference filename must be branch-<letter>.md: {fname}")
    return letter.upper()


def load_references() -> tuple[list[tuple[int, str]], dict[str, int]]:
    """Load base REFERENCES.md + all data/references/branch-*.md shards.

    Returns (global_refs, token_map) where:
      global_refs is a list of (global_n, text) tuples in stable order
        (base first with its own numbers preserved 1..N; then each shard
        in lexicographic filename order, its entries assigned sequential
        global numbers starting from max(base)+1).
      token_map maps citation tokens like "A:1" -> global_n. Legacy
        integer citations in species YAMLs map straight to base numbers.
    """
    global_refs: list[tuple[int, str]] = []
    token_map: dict[str, int] = {}
    max_n = 0
    if REFS_FILE.exists():
        for n, text in _parse_ref_file(REFS_FILE):
            global_refs.append((n, text))
            if n > max_n:
                max_n = n
    if REFS_SHARDS_DIR.exists():
        for shard_path in sorted(REFS_SHARDS_DIR.glob("branch-*.md")):
            letter = _shard_letter_from_name(shard_path.name)
            for local_n, text in _parse_ref_file(shard_path):
                max_n += 1
                global_n = max_n
                global_refs.append((global_n, text))
                token = f"{letter}:{local_n}"
                token_map[token] = global_n
    return global_refs, token_map


def preflight_image_manifests() -> None:
    """Load base + branch shard image manifests and error on duplicate id.

    This runs at build time so a duplicate id introduced by a shard is caught
    even without re-running fetch_images.py.
    """
    seen: dict[str, str] = {}
    manifests: list[Path] = []
    if IMAGE_MANIFEST.exists():
        manifests.append(IMAGE_MANIFEST)
    manifests.extend(sorted(DATA.glob(IMAGE_SHARD_GLOB)))
    errors = []
    for path in manifests:
        try:
            entries = json.loads(path.read_text())
        except Exception as e:
            errors.append(f"{path.name}: cannot parse JSON — {e}")
            continue
        if not isinstance(entries, list):
            errors.append(f"{path.name}: must be a JSON array")
            continue
        for i, entry in enumerate(entries):
            iid = entry.get("id")
            if not iid:
                errors.append(f"{path.name}[{i}]: missing 'id'")
                continue
            if iid in seen:
                errors.append(f"duplicate image id '{iid}' in {path.name} and {seen[iid]}")
            else:
                seen[iid] = path.name
    if errors:
        raise SystemExit("build_site: image manifest preflight failed:\n  " + "\n  ".join(errors))


def resolve_citations(raw: list, token_map: dict[str, int], species_slug: str) -> list[int]:
    """Convert a species YAML citations list (mixed ints + tokens) to global ints."""
    out = []
    for c in raw or []:
        if isinstance(c, int):
            out.append(c)
            continue
        s = str(c).strip()
        if s.isdigit():
            out.append(int(s))
            continue
        m = CITATION_TOKEN_RE.match(s)
        if not m:
            raise SystemExit(f"build_site: species '{species_slug}' has bad citation token: {c!r}")
        if s not in token_map:
            raise SystemExit(
                f"build_site: species '{species_slug}' cites unresolved token '{s}' — "
                f"no matching entry in data/references/branch-{m.group(1).lower()}.md"
            )
        out.append(token_map[s])
    return out


def esc(x) -> str:
    if x is None:
        return ""
    return html.escape(str(x))


def page(title: str, body: str, active: str = "") -> str:
    nav_items = [
        ("index.html", "Index", "index"),
        ("glossary.html", "Glossary", "glossary"),
        ("safety-and-ethics.html", "Safety & Ethics", "safety"),
        ("credits.html", "Image Credits", "credits"),
        ("references.html", "References", "references"),
    ]
    # Species pages live one level down; adjust relative paths.
    prefix = "../" if active == "species" else ""
    nav_html = " ".join(
        f'<a href="{prefix}{href}">{esc(label)}</a>'
        for href, label, _ in nav_items
    )
    return (
        "<!DOCTYPE html>\n"
        f'<html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{esc(title)}</title>"
        f'<link rel="stylesheet" href="{prefix}style.css">'
        "</head><body>"
        '<header class="site">'
        "<h1>Kauai Coastal Field Guide</h1>"
        "<p>Plants of the unpopulated coast — Nā Pali, Māhāʻulepū, and the roadless shore.</p>"
        "</header>"
        f'<nav class="top">{nav_html}</nav>'
        f"<main>{body}</main>"
        '<footer class="site">Offline field guide. Species records rendered from YAML by <code>scripts/build_site.py</code>. '
        "All photographs are used under CC-BY, CC-BY-SA, CC0, or public-domain terms — see the Image Credits page.</footer>"
        "</body></html>"
    )


def img_or_diagram_html(entry: dict, images: dict, diagrams_dir: Path, prefix: str) -> str:
    """Render one figure block for a species page.

    entry keys: id (for photos) OR file (for SVG diagrams); role, caption, diagnostic_pointer.
    """
    caption_bits = []
    if entry.get("diagnostic_pointer"):
        caption_bits.append(f"<strong>Look for:</strong> {esc(entry['diagnostic_pointer'])}")
    if entry.get("role"):
        role = entry["role"].replace("_", " ")
        caption_bits.append(f"<em>({esc(role)})</em>")

    if "id" in entry:
        rec = images.get(entry["id"])
        if not rec:
            return (
                f'<figure class="figure"><figcaption>[missing image: {esc(entry["id"])}]</figcaption></figure>'
            )
        rel = rec["path"]  # e.g. assets/photos/abc.jpg (site-relative)
        src = f"{prefix}{rel}"
        w = rec.get("width", "")
        h = rec.get("height", "")
        cap = entry.get("caption") or rec.get("caption") or ""
        credit = (
            f'{esc(rec["author"])} — <span>{esc(rec["license"])}</span> '
            f'(via {esc(rec["source"])})'
        )
        dim_attrs = ""
        if w and h:
            dim_attrs = f' width="{int(w)}" height="{int(h)}"'
        return (
            f'<figure class="figure">'
            f'<img src="{esc(src)}" alt="{esc(cap or entry.get("role",""))}"{dim_attrs} loading="lazy">'
            f'<figcaption>{esc(cap)} {" ".join(caption_bits)}'
            f'<span class="attr">Photo: {credit}</span>'
            f"</figcaption></figure>"
        )
    elif "file" in entry:
        svg_path = diagrams_dir / entry["file"]
        if not svg_path.exists():
            return f'<figure class="figure"><figcaption>[missing diagram: {esc(entry["file"])}]</figcaption></figure>'
        # Inline the SVG so it inherits page styles and needs no extra request.
        svg = svg_path.read_text()
        cap = entry.get("caption", "")
        return (
            f'<figure class="figure">{svg}'
            f'<figcaption>{esc(cap)} {" ".join(caption_bits)}'
            f'<span class="attr">Diagram: locally drawn (public domain)</span>'
            f"</figcaption></figure>"
        )
    else:
        return ""


def thumb_html(sp: dict, images: dict, diagrams_dir: Path, prefix: str) -> str:
    """Pick a representative thumbnail (first photo, else first diagram)."""
    for entry in sp.get("images", []) or []:
        rec = images.get(entry.get("id", ""))
        if rec:
            return f'<img class="thumb" src="{prefix}{esc(rec["path"])}" alt="{esc(sp["scientific_name"])}" loading="lazy">'
    for entry in sp.get("diagrams", []) or []:
        svg_path = diagrams_dir / entry["file"]
        if svg_path.exists():
            svg = svg_path.read_text()
            return f'<div class="thumb svg">{svg}</div>'
    return '<div class="thumb"></div>'


def species_search_blob(sp: dict) -> str:
    parts = [
        sp.get("scientific_name", ""),
        sp.get("family", ""),
        sp.get("tier", ""),
        sp.get("status", ""),
    ]
    parts += sp.get("common_names", {}).get("hawaiian", []) or []
    parts += sp.get("common_names", {}).get("english", []) or []
    parts += sp.get("coastal_zones", []) or []
    return " ".join(parts).lower()


def card_html(sp: dict, images: dict, diagrams_dir: Path, prefix: str) -> str:
    tier = sp.get("tier", "common")
    haw = ", ".join(sp.get("common_names", {}).get("hawaiian", []) or []) or "—"
    zones = " ".join(f'<span class="badge zone">{esc(ZONE_LABELS.get(z, z))}</span>' for z in sp.get("coastal_zones", []) or [])
    return (
        f'<a class="card" href="{prefix}species/{esc(sp["slug"])}.html" '
        f'data-search="{esc(species_search_blob(sp))}" data-tier="{esc(tier)}">'
        f'{thumb_html(sp, images, diagrams_dir, prefix)}'
        f'<div class="meta">'
        f'<p class="sci">{esc(sp["scientific_name"])}</p>'
        f'<p class="haw">{esc(haw)}</p>'
        f'<span class="badge {esc(tier if tier != "rare_exotic" else "rare")}">{esc(TIER_LABELS[tier][0])}</span>'
        f' {zones}'
        f'</div></a>'
    )


def render_index(species: list[dict], images: dict, diagrams_dir: Path) -> str:
    body = [
        '<section class="intro">',
        '<h2>How to use this guide</h2>',
        '<p>This is a picture-driven field guide to the plants of Kauai\'s roadless coast — '
        'the Nā Pali sea cliffs and valley mouths (Kalalau, Honopū, Nuʻalolo Kai, Miloliʻi, Awaʻawapuhi), '
        'and other uninhabited shorelines such as Māhāʻulepū. Species are grouped into three tiers:</p>',
        '<ul>',
        '<li><strong>COMMON</strong> — plants you will actually encounter on strand, dune, sea cliff, and valley mouth.</li>',
        '<li><strong>NOTABLE</strong> — culturally or ecologically important natives and Polynesian canoe plants.</li>',
        '<li><strong>RARE &amp; EXOTIC</strong> — Nā Pali cliff endemics (some federally listed) and dominant invasives.</li>',
        '</ul>',
        '<p>Use the search box to narrow by scientific name, Hawaiian name, family, status, or zone. '
        'Tap a card for a full identification profile with photos, diagnostic notes, and citations. '
        'See <a href="safety-and-ethics.html">Safety &amp; Ethics</a> before you go.</p>',
        '</section>',
        '<div class="filter-bar">',
        '<input type="search" id="filter-input" placeholder="Filter — try &quot;naupaka&quot;, &quot;endemic&quot;, or &quot;sea cliff&quot;">',
        '<span class="count" id="filter-count"></span>',
        '</div>',
    ]

    # Tier-grouped view
    body.append('<h2 style="margin-top:1.5rem;">Browse by tier</h2>')
    for tier in TIER_ORDER:
        tier_species = [s for s in species if s.get("tier") == tier]
        if not tier_species:
            continue
        label, desc = TIER_LABELS[tier]
        body.append(f'<section class="group tier"><h2>{esc(label)}</h2><p class="desc">{esc(desc)}</p></section>')
        body.append('<div class="group grid">')
        for sp in tier_species:
            body.append(card_html(sp, images, diagrams_dir, ""))
        body.append('</div>')
        # After the RARE tier grid, cross-list federally-listed species from other tiers.
        if tier == "rare_exotic":
            def is_federal_listed(sp: dict) -> bool:
                cs = (sp.get("conservation_status") or "").lower()
                # Match USFWS federal listings (Endangered / Threatened) regardless of tier.
                return ("us endangered" in cs) or ("us threatened" in cs) or ("federally listed" in cs)
            cross = [s for s in species if s.get("tier") != "rare_exotic" and is_federal_listed(s)]
            if cross:
                body.append(
                    '<section class="group tier cross-list">'
                    '<h2>Also federally listed (cross-listed from other tiers)</h2>'
                    '<p class="desc">Species surfaced by USFWS listing status even where their primary tier is COMMON or NOTABLE. Full profile lives in the species\' home tier above.</p>'
                    '</section>'
                )
                body.append('<div class="group grid">')
                for sp in cross:
                    body.append(card_html(sp, images, diagrams_dir, ""))
                body.append('</div>')

    # Zone-grouped view
    body.append('<h2 style="margin-top:2rem;">Browse by habitat zone</h2>')
    for zone in ZONE_ORDER:
        zone_species = [s for s in species if zone in (s.get("coastal_zones") or [])]
        if not zone_species:
            continue
        body.append(f'<section class="group tier"><h2>{esc(ZONE_LABELS[zone])}</h2></section>')
        body.append('<div class="group grid">')
        for sp in zone_species:
            body.append(card_html(sp, images, diagrams_dir, ""))
        body.append('</div>')

    body.append('<script src="filter.js"></script>')
    return page("Kauai Coastal Field Guide — Index", "\n".join(body))


def id_block_html(sp: dict) -> str:
    idb = sp.get("how_to_identify") or {}
    rows = []
    for key, label in [
        ("growth_form", "Growth form"),
        ("size", "Size"),
        ("leaves", "Leaves"),
        ("flowers", "Flowers"),
        ("fruit", "Fruit / seed"),
        ("bark_stem", "Bark / stem"),
        ("zone_hint", "Where it sits on the coast"),
    ]:
        if idb.get(key):
            rows.append(f"<dt>{esc(label)}</dt><dd>{esc(idb[key])}</dd>")
    dl = f'<dl class="id-block">{"".join(rows)}</dl>' if rows else ""

    clinchers = idb.get("clinchers") or []
    clinch_html = ""
    if clinchers:
        items = "".join(f"<li>{esc(c)}</li>" for c in clinchers)
        clinch_html = f'<div class="clinchers"><h3>Clinchers (features that lock the ID)</h3><ul>{items}</ul></div>'

    la = idb.get("look_alikes") or []
    la_html = ""
    if la:
        items = []
        for entry in la:
            spec = esc(entry.get("species", ""))
            how = esc(entry.get("how_to_distinguish", ""))
            items.append(f'<li><em>{spec}</em> — {how}</li>')
        la_html = f'<h3>Look-alikes</h3><ul class="lookalikes">{"".join(items)}</ul>'

    return dl + clinch_html + la_html


def cite_html(citations: list[int]) -> str:
    if not citations:
        return ""
    parts = ", ".join(f'<a class="cite" href="../references.html#ref-{n}">[{n}]</a>' for n in citations)
    return f' {parts}'


def render_species(sp: dict, images: dict, diagrams_dir: Path, refs: list[tuple[int,str]], token_map: dict[str,int] | None = None) -> str:
    token_map = token_map or {}
    sp = dict(sp)  # shallow copy so we don't mutate caller's dict
    sp["citations"] = resolve_citations(sp.get("citations", []) or [], token_map, sp.get("slug", "<?>"))
    haw = ", ".join(sp.get("common_names", {}).get("hawaiian", []) or []) or "—"
    eng = ", ".join(sp.get("common_names", {}).get("english", []) or []) or "—"
    tier = sp.get("tier", "common")
    badge_cls = tier if tier != "rare_exotic" else "rare"
    zones = " ".join(f'<span class="badge zone">{esc(ZONE_LABELS.get(z, z))}</span>' for z in sp.get("coastal_zones", []) or [])
    figs = "\n".join(
        img_or_diagram_html(e, images, diagrams_dir, "../") for e in (sp.get("images", []) or [])
    )
    figs += "\n".join(
        img_or_diagram_html(e, images, diagrams_dir, "../") for e in (sp.get("diagrams", []) or [])
    )

    meta_rows = [
        ("Family", esc(sp.get("family", ""))),
        ("Scientific name", f'<em>{esc(sp["scientific_name"])}</em> <span class="authority">{esc(sp.get("authority", ""))}</span>'),
        ("Hawaiian name(s)", esc(haw)),
        ("English name(s)", esc(eng)),
        ("Status", esc(STATUS_LABELS.get(sp.get("status", ""), sp.get("status", "")))),
        ("Conservation", esc(sp.get("conservation_status") or "—")),
        ("Coastal zones", zones or "—"),
        ("Occurrence", esc(sp.get("occurrence_notes", ""))),
    ]
    meta_tbl = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in meta_rows)

    hazards_html = ""
    if sp.get("hazards"):
        hazards_html = f'<div class="hazards"><strong>Hazards:</strong> {esc(sp["hazards"])}</div>'
    uncert_html = ""
    if sp.get("uncertainty"):
        uncert_html = f'<div class="uncertainty"><strong>Uncertainty:</strong> {esc(sp["uncertainty"])}</div>'

    body = f"""
<article class="profile">
  <div class="badges"><span class="badge {esc(badge_cls)}">{esc(TIER_LABELS[tier][0])}</span> {zones}</div>
  <h1>{esc(sp['scientific_name'])} <span class="authority">{esc(sp.get('authority',''))}</span></h1>
  <p class="common"><strong>{esc(haw)}</strong> · {esc(eng)}</p>

  <div class="gallery">{figs}</div>

  <section class="section">
    <h2>Quick facts</h2>
    <table class="meta-table">{meta_tbl}</table>
    {hazards_html}
    {uncert_html}
  </section>

  <section class="section">
    <h2>How to identify</h2>
    {id_block_html(sp)}
  </section>

  <section class="section">
    <h2>Ecology</h2>
    <p>{esc(sp.get('ecology',''))}{cite_html(sp.get('citations', []))}</p>
  </section>

  <section class="section">
    <h2>Cultural significance</h2>
    <p>{esc(sp.get('cultural_significance','') or '—')}</p>
  </section>

  <p><a href="../index.html">← Back to index</a></p>
</article>
"""
    rendered = page(f"{sp['scientific_name']} — Kauai Coastal Field Guide", body, active="species")
    # Rewrite any inline [X:n] citation tokens embedded in prose fields
    # (uncertainty, occurrence_notes, ecology, cultural_significance, …).
    return rewrite_inline_citation_tokens(rendered, token_map)


def render_credits(species: list[dict], images: dict) -> str:
    # Aggregate all image records actually referenced by species pages.
    used = set()
    for sp in species:
        for e in sp.get("images", []) or []:
            if "id" in e:
                used.add(e["id"])
    rows = []
    for iid, rec in sorted(images.items()):
        if iid not in used:
            continue
        rows.append(
            f'<tr><td><a href="{esc(rec["path"])}">{esc(iid)}</a></td>'
            f'<td>{esc(rec["author"])}</td>'
            f'<td>{esc(rec["license"])}</td>'
            f'<td><a href="{esc(rec["source_page"])}">source page</a></td>'
            f'<td>{esc(rec.get("caption",""))}</td></tr>'
        )
    table = (
        '<table><thead><tr><th>Image ID</th><th>Author</th><th>License</th><th>Source</th><th>Caption</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )
    body = (
        '<div class="credits">'
        '<h2>Image credits</h2>'
        '<p>All photographs are used under CC-BY, CC-BY-SA, CC0, or public-domain terms. '
        'Source pages link to the original license declarations. Locally drawn SVG diagrams '
        'are released into the public domain.</p>'
        f'{table}'
        '</div>'
    )
    return page("Image Credits", body)


def render_glossary(glossary: list[dict]) -> str:
    items = []
    for entry in glossary:
        items.append(f'<dt>{esc(entry["term"])}</dt><dd>{esc(entry["definition"])}</dd>')
    body = (
        '<h2>Glossary</h2>'
        '<p>Botanical and Hawaiian terms used throughout the guide.</p>'
        f'<dl class="glossary">{"".join(items)}</dl>'
    )
    return page("Glossary", body)


def render_references(refs: list[tuple[int,str]]) -> str:
    items = "".join(f'<li id="ref-{n}"><strong>[{n}]</strong> {esc(t)}</li>' for n, t in refs)
    body = (
        '<div class="refs">'
        '<h2>References</h2>'
        '<p>Numbered references cited from species profiles. See also <code>REFERENCES.md</code>.</p>'
        f'<ol style="list-style:none;padding-left:0;">{items}</ol>'
        '</div>'
    )
    return page("References", body)


def render_safety() -> str:
    body = """
<h2>Safety, ethics, and cultural respect</h2>
<div class="notice">
  <strong>Wahi pana.</strong> The unpopulated Kauai coast — especially Nā Pali — is <em>wahi pana</em>,
  a storied and sacred landscape. Every valley, cliff, and beach carries names, genealogies, and
  histories that predate this guide. Move through it as a guest.
</div>
<h3>Leave No Trace</h3>
<ul>
  <li><strong>Do not collect</strong>. Every plant on this coast — common, notable, or rare — stays where it grew. Federally listed endemics (see the RARE &amp; EXOTIC tier) may not be touched, moved, or transported.</li>
  <li>Pack out everything you pack in. Human waste too — sand and salt do not compost it fast enough.</li>
  <li>Stay on established trails. Kalalau and adjacent valleys have fragile cliff ecosystems where a single boot print off-trail can dislodge soil around a rare endemic.</li>
  <li>Never introduce seeds, mud, or plant fragments from other islands or the main highway. Invasives like Christmas berry and lantana are already dominant here; you can carry the next problem in on your soles.</li>
</ul>
<h3>Hazards</h3>
<ul>
  <li>Some plants in this guide are toxic (raw kukui nuts, ʻākia, castor) or sting (nettles); each species profile carries a <strong>Hazards</strong> block where relevant.</li>
  <li>Sea-cliff plants live at the edge of hundred-foot drops. Do not approach cliff endemics for a closer look.</li>
  <li>Rockfall, flash floods, and sudden surf are the primary killers on this coast — not plants.</li>
</ul>
<h3>Cultural respect</h3>
<p>The Hawaiian names, uses, and associations noted in species profiles come from published cultural
sources. This guide never provides harvesting instructions for culturally significant plants —
those practices belong to and are transmitted within the Hawaiian community, not to guidebooks.
Where you encounter offerings, boundary markers (<em>ahu</em>), or altered ground, walk around.</p>
<h3>Reporting</h3>
<p>If you find a rare endemic outside its known range, or an invasive species establishing in a new
valley, report it to Hawaii DLNR/DOFAW or the National Tropical Botanical Garden rather than sharing
GPS coordinates publicly.</p>
"""
    return page("Safety & Ethics", body)


def main():
    SITE.mkdir(exist_ok=True)
    (SITE / "species").mkdir(exist_ok=True)
    (SITE / "assets" / "photos").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "diagrams").mkdir(parents=True, exist_ok=True)

    preflight_image_manifests()
    species = load_species()
    images = load_images_lock()
    glossary = load_glossary()
    refs, token_map = load_references()
    diagrams_dir = SITE / "assets" / "diagrams"

    # Sort species stably by tier then scientific name.
    species.sort(key=lambda s: (TIER_ORDER.index(s.get("tier", "common")) if s.get("tier") in TIER_ORDER else 99, s.get("scientific_name","")))

    (SITE / "index.html").write_text(render_index(species, images, diagrams_dir))
    for sp in species:
        (SITE / "species" / f'{sp["slug"]}.html').write_text(render_species(sp, images, diagrams_dir, refs, token_map))
    (SITE / "credits.html").write_text(render_credits(species, images))
    (SITE / "glossary.html").write_text(render_glossary(glossary))
    (SITE / "references.html").write_text(render_references(refs))
    (SITE / "safety-and-ethics.html").write_text(render_safety())

    # Emit citation token → global-id map for auditors.
    REFS_MAP_FILE.write_text(json.dumps(token_map, indent=2, sort_keys=True) + "\n")

    print(f"Built {len(species)} species pages + 5 static pages -> {SITE}")
    if token_map:
        print(f"  citation tokens resolved: {len(token_map)}")


if __name__ == "__main__":
    main()
