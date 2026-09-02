import hashlib, json, os, subprocess, sys

def sha(p):
    with open(p,'rb') as f: return hashlib.sha256(f.read()).hexdigest()

def probe_slice(name, doc, rubric_txt, verdict_path, extra_checks=None):
    print(f'=== {name} ===')
    try:
        doc_sha=sha(doc)
        hash_txt=open(rubric_txt).read().strip()
        v=json.load(open(verdict_path))
        print(f'  doc SHA: {doc_sha}')
        print(f'  rubric_hash.txt: {hash_txt}')
        v_hash = v.get('rubric_hash')
        print(f'  verdict.rubric_hash: {v_hash}')
        print(f'  verdict: {v.get("verdict")}')
        print(f'  3-way byte-equality: {doc_sha == hash_txt == v_hash}')
    except Exception as e:
        print(f'  ERROR: {e}')
    if extra_checks:
        extra_checks()

# Slice 1: M-TEX-1/palette-driven-bare-render (c33 clone-0)
def s1_extra():
    run1=open('data/palette_render/bare_combined.wav.sha.run1').read().strip()
    run2=open('data/palette_render/bare_combined.wav.sha.run2').read().strip()
    print(f'  bare_combined byte-det: run1==run2={run1==run2}')
    stems_dir='data/palette_render/per_stem'
    if os.path.isdir(stems_dir):
        for s in sorted(os.listdir(stems_dir)):
            sd=f'{stems_dir}/{s}'
            files=os.listdir(sd)
            for f1 in [f for f in files if 'run1' in f]:
                f2 = f1.replace('run1','run2')
                if f2 in files:
                    s1=open(os.path.join(sd,f1)).read().strip()
                    s2=open(os.path.join(sd,f2)).read().strip()
                    print(f'  per_stem/{s}: run1==run2={s1==s2}')
    for tsv in ['panel_original_vs_palette.tsv','panel_fluidsynth_vs_palette.tsv']:
        p=f'data/palette_render/{tsv}'
        if os.path.exists(p):
            lines=open(p).read().strip().split('\n')
            hdr = lines[0].split('\t')
            print(f'  {tsv}: {len(lines)} rows, {len(hdr)} cols; head={hdr[:6]}')
    ap=json.load(open('data/palette_render/anchor_preservation.json'))
    if isinstance(ap, dict):
        for k in ['anchors','entries','anchor_list']:
            if k in ap and isinstance(ap[k], (list,dict)):
                print(f'  anchor_preservation[{k}]: {len(ap[k])}')
                break
        else:
            print(f'  anchor_preservation top keys: {list(ap.keys())}')
    t='tests/test_palette_driven_bare_render.py'
    if os.path.exists(t):
        r=subprocess.run(['grep','-c','^def test_',t], capture_output=True, text=True)
        print(f'  test cases: {r.stdout.strip()}')

probe_slice(
  'SLICE 1: M-TEX-1/palette-driven-bare-render (c33 clone-0)',
  'docs/palette_driven_bare_render_rubric.md',
  'data/palette_render/rubric_hash.txt',
  'data/palette_render/verdict.json',
  s1_extra
)

# Slice 2: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization (c36 clone-2)
def s2_extra():
    per='data/vst3_nondeterminism/per_plugin'
    if os.path.isdir(per):
        for plug in sorted(os.listdir(per)):
            pd=f'{per}/{plug}'
            files = sorted(os.listdir(pd))
            print(f'  plugin={plug}: {len(files)} files; sample={files[:5]}')
    v=json.load(open('data/vst3_nondeterminism/characterization_verdict.json'))
    for k in ('verdict','plugin_verdicts','per_plugin'):
        if k in v: print(f'  verdict.{k}: {v[k] if not isinstance(v[k],dict) else list(v[k].keys())}')
    ap=json.load(open('data/vst3_nondeterminism/anchor_preservation.json'))
    for k in ['anchors','entries','anchor_files','files']:
        if k in ap and isinstance(ap[k], (list,dict)):
            print(f'  anchor_preservation[{k}]: {len(ap[k])}')
            break
    else:
        print(f'  anchor_preservation top keys: {list(ap.keys())[:8]}')
    t='tests/test_vst3_nondeterminism.py'
    if os.path.exists(t):
        r=subprocess.run(['grep','-c','^def test_',t], capture_output=True, text=True)
        print(f'  test cases: {r.stdout.strip()}')
    else:
        # try other name
        for cand in os.listdir('tests'):
            if 'vst3' in cand.lower() or 'nondeterminism' in cand.lower():
                r=subprocess.run(['grep','-c','^def test_',f'tests/{cand}'], capture_output=True, text=True)
                print(f'  {cand}: {r.stdout.strip()} tests')

probe_slice(
  'SLICE 2: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization (c36 clone-2)',
  'docs/vst3_nondeterminism_characterization_rubric.md',
  'data/vst3_nondeterminism/rubric_hash.txt',
  'data/vst3_nondeterminism/characterization_verdict.json',
  s2_extra
)

# Slice 3: _infra/anchor-manifest-v1 (c35 clone-2)
def s3_extra():
    m=json.load(open('data/anchor_manifest_v1.json'))
    print(f'  top keys: {list(m.keys())}')
    anchors = m.get('anchors') or m.get('entries') or m.get('anchor_entries')
    if anchors is not None:
        print(f'  anchor_count: {len(anchors)}')
        # sample
        if isinstance(anchors, list) and anchors:
            print(f'  first entry keys: {list(anchors[0].keys())[:8]}')
        elif isinstance(anchors, dict):
            print(f'  first key: {next(iter(anchors))}')
    print(f'  anchor_count field: {m.get("anchor_count")}')
    # For anchor manifest, no verdict.json in same dir — rubric is separate
    if os.path.exists('data/anchor_manifest/rubric_hash.txt'):
        print(f'  rubric_hash.txt: {open("data/anchor_manifest/rubric_hash.txt").read().strip()}')
    if os.path.exists('data/anchor_manifest/verdict.json'):
        vv=json.load(open('data/anchor_manifest/verdict.json'))
        print(f'  verdict: {vv.get("verdict")}, rubric_hash={vv.get("rubric_hash")}')
    # tests
    for cand in os.listdir('tests'):
        if 'anchor_manifest' in cand.lower():
            r=subprocess.run(['grep','-c','^def test_',f'tests/{cand}'], capture_output=True, text=True)
            print(f'  {cand}: {r.stdout.strip()} tests')

print('=== SLICE 3: _infra/anchor-manifest-v1 (c35 clone-2) ===')
if os.path.exists('docs/anchor_manifest_v1_rubric.md'):
    doc='docs/anchor_manifest_v1_rubric.md'
    print(f'  doc SHA: {sha(doc)}')
else:
    print(f'  rubric doc: ? — checking...')
    for cand in os.listdir('docs'):
        if 'anchor_manifest' in cand.lower():
            print(f'    found: docs/{cand} SHA={sha(f"docs/{cand}")}')
s3_extra()
