"""Builds cutting-plan.html (all sheets, both drawings each) from layout.py."""
import html, os
from layout import SHEETS, PARTS, ASSEMBLY, COLORS, validate, layout_svg, cuts_svg, fmt

n_sheets, n_cuts, n_panels = validate()

CSS = """
:root{--bg:#EDF0F1;--surface:#FFFFFF;--ink:#1C2427;--muted:#5B676C;--line:#CBD3D6;
--sheet:#EAD9B4;--sheet-edge:#7A6647;--hatch:#C2AE84;--cut:#C0392B;--cut-ink:#FFFFFF;--panel-ink:#1F1A14;
--accent:#C0392B;--tag:#E3E8EA}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#14191B;--surface:#1D2427;--ink:#E3E8EA;
--muted:#9AA7AC;--line:#34403F;--sheet:#5B4E38;--sheet-edge:#B39A70;--hatch:#7D6B4C;--tag:#2A3336}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#14191B;--surface:#1D2427;--ink:#E3E8EA;--muted:#9AA7AC;--line:#34403F;
--sheet:#5B4E38;--sheet-edge:#B39A70;--hatch:#7D6B4C;--tag:#2A3336}
body{background:var(--bg);color:var(--ink);font:16px/1.55 "Source Sans 3",system-ui,sans-serif;padding-inline:16px;padding-block:28px 64px}
main{max-width:1060px;margin:0 auto;display:flex;flex-direction:column;gap:40px}
h1,h2,h3{font-family:"Barlow Condensed","Arial Narrow",sans-serif;font-weight:600;line-height:1.1;text-wrap:balance;margin:0}
h1{font-size:44px;letter-spacing:.01em}
h2{font-size:28px}
h3{font-size:22px}
p{margin:0;max-width:68ch}
.mono,td.n{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}
.eyebrow{font:600 12px/1 "IBM Plex Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
header{display:flex;flex-direction:column;gap:14px}
.totals{display:flex;flex-wrap:wrap;gap:12px 36px;margin-top:6px}
.totals div{display:flex;flex-direction:column}
.totals b{font:600 40px/1 "Barlow Condensed",sans-serif}
.totals span{color:var(--muted);font-size:14px}
section{display:flex;flex-direction:column;gap:14px}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font:600 12px "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.swatch{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:7px;vertical-align:-1px;border:1px solid rgba(0,0,0,.35)}
ol.proof{margin:0;padding-left:22px;display:flex;flex-direction:column;gap:8px;max-width:72ch}
.sheet{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:20px;display:flex;flex-direction:column;gap:14px}
.sheet-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px}
.sheet-head .count{color:var(--muted);font-size:14px}
.drawings{display:grid;grid-template-columns:1fr;gap:18px}
figure{margin:0;display:flex;flex-direction:column;gap:6px;min-width:0}
figcaption{font:600 12px "IBM Plex Mono",monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.svgbox{overflow-x:auto}
.svgbox svg{width:100%;min-width:560px;height:auto;display:block}
ol.cuts{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px;counter-reset:c}
ol.cuts li{display:flex;gap:10px;align-items:baseline}
ol.cuts li::before{counter-increment:c;content:counter(c);flex:none;width:22px;height:22px;border-radius:50%;background:var(--cut);color:var(--cut-ink);
font:700 12px/22px "IBM Plex Mono",monospace;text-align:center}
.pieces{display:flex;flex-wrap:wrap;gap:6px}
.pieces span{background:var(--tag);border-radius:4px;padding:2px 8px;font-size:14px}
.note{border-left:3px solid var(--accent);padding:4px 0 4px 14px;max-width:72ch}
svg .sheet{fill:var(--sheet);stroke:var(--sheet-edge);stroke-width:1.5}
svg .hatchbg{fill:var(--sheet)}
svg .hatchline{stroke:var(--hatch);stroke-width:1}
svg .waste{fill:url(#hatch)}
svg .piece{stroke:#3A3128;stroke-width:1}
svg .under{fill:var(--sheet)}
svg .lab{font:600 12px "Source Sans 3",sans-serif;fill:var(--panel-ink)}
svg .dim{font:11px "IBM Plex Mono",monospace;fill:var(--ink)}
svg .piece + .lab, svg .lab + .dim{fill:var(--panel-ink)}
svg .dimline{stroke:var(--muted);stroke-width:.8;fill:none}
svg .axis{font:11px "IBM Plex Mono",monospace;fill:var(--muted)}
svg .cut{stroke:var(--cut);stroke-width:2.2;stroke-dasharray:7 4}
svg .cutdot{fill:var(--cut)}
svg .cutnum{font:700 11px "IBM Plex Mono",monospace;fill:var(--cut-ink)}
@media (max-width:760px){h1{font-size:36px}}
"""

def page_svg(s, i):
    # unique hatch id per drawing so inline SVGs do not collide
    return s.replace('id="hatch"', f'id="hatch{i}"').replace("url(#hatch)", f"url(#hatch{i})")

def e(t): return html.escape(t, quote=True)

parts_rows = []
for part, (a, b) in PARTS.items():
    parts_rows.append(f'<tr><td><span class="swatch" style="background:{COLORS[part]}"></span>{e(part)}</td>'
                      f'<td class="n">{fmt(a)} × {fmt(b)}</td><td>{e(ASSEMBLY[part])}</td></tr>')

sheets_html = []
k = 0
for i, (title, pieces, cuts) in enumerate(SHEETS, 1):
    k += 1; lay = page_svg(layout_svg(title, pieces, False), k)
    k += 1; cut = page_svg(cuts_svg(title, pieces, cuts, False), k)
    tags = "".join(f'<span><span class="swatch" style="background:{COLORS[p[1]]}"></span>{e(p[0])} · <span class="mono">{fmt(p[4])} × {fmt(p[5])}</span></span>' for p in pieces)
    steps = "".join(f"<li>{e(c[4])}</li>" for c in cuts)
    sheets_html.append(f"""
<article class="sheet" id="sheet{i}">
  <div class="sheet-head"><h3>Sheet {i} · {e(title)}</h3><span class="count">{len(cuts)} cut{'s' if len(cuts) > 1 else ''}</span></div>
  <div class="pieces">{tags}</div>
  <div class="drawings">
    <figure><figcaption>Drawing {i}A · Layout</figcaption><div class="svgbox">{lay}</div></figure>
    <figure><figcaption>Drawing {i}B · Cut order</figcaption><div class="svgbox">{cut}</div></figure>
  </div>
  <ol class="cuts">{steps}</ol>
</article>""")

page = f"""<title>OSB Sheet Cut Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600&family=IBM+Plex+Mono:wght@400;600;700&family=Source+Sans+3:wght@400;600&display=swap">
<style>{CSS}</style>
<main>
<header>
  <span class="eyebrow">4 × 8 OSB · inches · ⅛″ kerf</span>
  <h1>OSB sheet cut plan</h1>
  <p>Eleven 48″ × 96″ sheets make every rectangle on the list. Five sheets need a single crosscut. Every piece larger than a sheet is built from two panels with one seam. Front wall A is the only small piece that gets a seam.</p>
  <div class="totals">
    <div><b>{n_sheets}</b><span>sheets (proven minimum)</span></div>
    <div><b>{n_cuts}</b><span>saw cuts</span></div>
    <div><b>{n_panels}</b><span>panels cut</span></div>
    <div><b>8</b><span>seams (7 required + 1)</span></div>
  </div>
</header>

<section>
  <h2>Pieces and how each is built</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>Piece</th><th>Finished size</th><th>Panels</th></tr></thead>
    <tbody>{''.join(parts_rows)}</tbody>
  </table></div>
</section>

<section>
  <h2>Why 11 sheets is the minimum</h2>
  <ol class="proof">
    <li><b>Area.</b> The pieces total 44,115 sq in. A sheet is 4,608 sq in, so no layout can use fewer than 10 sheets.</li>
    <li><b>Seven pieces are bigger than a sheet.</b> Floor, ceiling, both side walls, back wall, inside ceiling and inside side wall each need at least one seam. Each of their panels keeps one full dimension of 50.5″ or more, so that dimension has to run down the 96″ length of the sheet.</li>
    <li><b>Long panels cannot share length.</b> Two panels that are each longer than 48″ cannot sit end to end on a 96″ sheet. So every long panel uses its own slice of the 48″ width, and the widths of all long panels on a sheet must fit in 48″ with a ⅛″ kerf between neighbours.</li>
    <li><b>With front walls A, B and C left whole</b>, the long panels need at least 527.5″ of sheet width plus 6 kerfs (17 long panels on 11 sheets), which is 528.25″. Eleven sheets give 528″. That fails by ¼″, so keeping every front wall in one piece takes <b>12 sheets</b>.</li>
    <li><b>Cutting front wall A into 48″ + 39″</b> turns it into two short panels that fit into offcuts at the ends of sheets 6 and 11. That frees 17″ of width and makes 11 sheets work.</li>
    <li><b>10 sheets would need 3-panel pieces.</b> With at most one seam per piece, 10 sheets leave only about 12″ of spare width, and front wall C (25.5″ wide) has no offcut deep enough to go into. A computer search found 10-sheet layouts only by cutting pieces into 3 or more panels (31 panels in total), which is a poor trade for one sheet.</li>
  </ol>
</section>

<section>
  <h2>Iterations</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>Try</th><th>Rule</th><th>Sheets</th><th>Result</th></tr></thead>
    <tbody>
      <tr><td class="n">1</td><td>Random split + best-fit packing</td><td class="n">14 → 12</td><td>Too much waste at the ends of 82″–90″ panels.</td></tr>
      <tr><td class="n">2</td><td>One seam per oversized piece, fronts whole</td><td class="n">12</td><td>Proven minimum for this rule (point 4 above).</td></tr>
      <tr><td class="n">3</td><td>Adaptive splits, up to 2 panels per piece</td><td class="n">11</td><td>Search split three front walls; hand work reduced that to front wall A only.</td></tr>
      <tr><td class="n">4</td><td>Adaptive splits, up to 3 panels per piece</td><td class="n">10</td><td>31 panels. Rejected: too many seams.</td></tr>
      <tr><td class="n">5</td><td>Final, hand-tuned for fewest cuts</td><td class="n">11</td><td>{n_cuts} cuts; full-width panels need one crosscut each.</td></tr>
    </tbody>
  </table></div>
</section>

<section>
  <h2>Before you cut</h2>
  <p class="note">Measure your sheets. This plan assumes full 48″ × 96″ and a ⅛″ blade. Some OSB is sold at 47⅞″ × 95⅞″; the plan still fits, but make the second panel of each seamed piece whatever the finished size minus the first panel actually measures. Cut sheet 10 before sheet 11: the inside-ceiling strip on sheet 10 is whatever is left after two rips, and sheet 11's inside-ceiling panel is cut to 50.5″ minus that strip.</p>
  <p class="note">Want no seam in front wall A? Use 12 sheets instead: sheet 6 becomes inside side wall only (1 cut), sheet 11 becomes inside ceiling only (2 cuts), and a 12th sheet gives front wall A whole (rip 17″, crosscut 87″). That is 28 cuts.</p>
</section>

<section>
  <h2>Sheets</h2>
  <p>Drawing A of each sheet shows the finished pieces with positions measured from the top-left corner. Drawing B shows the cuts in order. Hatched areas are scrap.</p>
  {''.join(sheets_html)}
</section>
</main>
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cutting-plan.html")
open(out, "w").write(page)
print("wrote", out)
