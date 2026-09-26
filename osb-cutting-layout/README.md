# OSB cutting layout

Cut list for 4 ft × 8 ft (48″ × 96″) OSB sheets, ⅛″ saw kerf, all sizes in inches.

**Result: 11 sheets, 29 cuts, 19 panels.** Open `cutting-plan.html` for the full plan
with two drawings per sheet (layout + numbered cut order). The SVGs are also in `drawings/`.

| Sheet | Panels (length × width on the sheet) | Cuts |
|---|---|---|
| 1 | Floor 82 × 48 | 1 |
| 2 | Ceiling 82 × 48 | 1 |
| 3 | Side wall A 90 × 48 | 1 |
| 4 | Side wall B 87 × 48 | 1 |
| 5 | Back wall 87 × 48 | 1 |
| 6 | Inside side wall 77.5 × 48, Front wall A 48 × 17 | 2 |
| 7 | Side wall A 90 × 34, Floor 82 × 13 | 4 |
| 8 | Side wall B 87 × 34, Ceiling 82 × 13 | 4 |
| 9 | Front wall C 75 × 25.5, Front wall D 11.75 × 25.5, Front wall B 87 × 17.5 | 5 |
| 10 | Inside side wall 77.5 × 23, Back wall 87 × 12, Inside ceiling 72.5 × ≈12.75 | 5 |
| 11 | Inside ceiling 72.5 × 37.75, Front wall A 39 × 17 | 4 |

Why 11 is the minimum (details in the page):
- Area alone forces at least 10 sheets (44,115 sq in ÷ 4,608).
- Every panel of an oversized piece is longer than 48″ in one direction, so those panels
  can't sit end to end on a sheet. They need a width budget of 527.5″ plus kerfs.
  With all front walls whole that's 528.25″ against 528″ for 11 sheets, so 12 sheets.
  Splitting front wall A (48 + 39) makes 11 work.
- 10 sheets only works if some pieces are cut into 3+ panels (search found 31 panels).

Files: `layout.py` (the plan, a validator for bounds/kerf/areas, and the SVG drawings),
`build_page.py` (HTML page), `search.py` (the randomized search used while iterating).
