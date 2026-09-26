"""Adaptive-split guillotine search.

Pieces that do not fit a 48x96 sheet may be split once (max 2 panels per part,
i.e. one seam). When a free region is too small for the whole part, a panel
is sized to fill the region and the rest of the part goes back in the queue.
"""
import random, sys

W, L, K = 48.0, 96.0, 0.125
PARTS = [
    ("Floor", 61, 82), ("Ceiling", 61, 82),
    ("Side wall A", 90, 82), ("Side wall B", 87, 82),
    ("Front wall A", 87, 17), ("Front wall B", 87, 17.5),
    ("Front wall C", 75, 25.5), ("Front wall D", 11.75, 25.5),
    ("Back wall", 60, 87), ("Inside ceiling", 72.5, 50.5),
    ("Inside side wall", 77.5, 71),
]
MAXPANELS = int(sys.argv[3]) if len(sys.argv) > 3 else 2
MINPANEL = 6.0

def fits(a, b):
    return (a <= W and b <= L) or (a <= L and b <= W)

def run(rng, noise):
    queue = [(n, a, b, 1) for n, a, b in PARTS]  # (name, a, b, panels used so far)
    rng.shuffle(queue)
    queue.sort(key=lambda p: -(p[1] * p[2]) * (1 + noise * rng.random()))
    boards = []
    splits = []
    while queue:
        name, a, b, used = queue.pop(0)
        whole_ok = fits(a, b)
        best = None
        for bi in range(len(boards) + 1):
            free = boards[bi]['free'] if bi < len(boards) else [(0, 0, W + K, L + K)]
            new = bi == len(boards)
            for fi, (x, y, fw, fh) in enumerate(free):
                for (pw, ph) in ((a, b), (b, a)):
                    # whole
                    if whole_ok and pw + K <= fw + 1e-9 and ph + K <= fh + 1e-9:
                        waste = min(fw - pw - K, fh - ph - K)
                        s = (new, waste * (1 + noise * rng.random()), 0)
                        if best is None or s < best[0]:
                            best = (s, bi, fi, pw, ph, None)
                    # partial panel: keep ph whole, cut pw down to region width
                    if used < MAXPANELS and ph + K <= fh + 1e-9 and pw + K > fw:
                        cw = fw - K
                        rest = pw - cw
                        if cw >= MINPANEL and rest >= MINPANEL and (fits(rest, ph) or used + 1 < MAXPANELS):
                            waste = fh - ph - K
                            s = (new, waste * (1 + noise * rng.random()) + 0.5, 1)
                            if best is None or s < best[0]:
                                best = (s, bi, fi, cw, ph, (rest, ph))
                    if used < MAXPANELS and pw + K <= fw + 1e-9 and ph + K > fh:
                        ch = fh - K
                        rest = ph - ch
                        if ch >= MINPANEL and rest >= MINPANEL and (fits(pw, rest) or used + 1 < MAXPANELS):
                            waste = fw - pw - K
                            s = (new, waste * (1 + noise * rng.random()) + 0.5, 1)
                            if best is None or s < best[0]:
                                best = (s, bi, fi, pw, ch, (pw, rest))
        if best is None:
            return None
        _, bi, fi, pw, ph, rest = best
        if bi == len(boards):
            boards.append({'free': [(0, 0, W + K, L + K)], 'placed': []})
        bd = boards[bi]
        x, y, fw, fh = bd['free'].pop(fi)
        bd['placed'].append((name, x, y, pw, ph))
        if rest:
            queue.insert(0, (name, rest[0], rest[1], used + 1))
        ew, eh = pw + K, ph + K
        rw, rh = fw - ew, fh - eh
        if rng.random() < 0.5 if abs(rw * fh - rh * fw) < 1 else rw * fh > rh * fw:
            r1, r2 = (x + ew, y, rw, fh), (x, y + eh, ew, rh)
        else:
            r1, r2 = (x, y + eh, fw, rh), (x + ew, y, rw, eh)
        for r in (r1, r2):
            if r[2] > K + 1 and r[3] > K + 1:
                bd['free'].append(r)
    return boards

def score(boards):
    fill = sorted(sum(p[3] * p[4] for p in b['placed']) for b in boards)
    npieces = sum(len(b['placed']) for b in boards)
    return (len(boards), fill[0], npieces)

if __name__ == "__main__":
    iters = int(sys.argv[1]); seed = int(sys.argv[2])
    rng = random.Random(seed)
    best = None
    for it in range(iters):
        bds = run(rng, rng.choice([0, 0.05, 0.2, 0.5, 1.0]))
        if bds is None:
            continue
        s = score(bds)
        if best is None or s < best[0]:
            best = (s, bds)
            print(it, s, flush=True)
    for i, b in enumerate(best[1], 1):
        print(f"Board {i}")
        for p in b['placed']:
            print("   ", p)
