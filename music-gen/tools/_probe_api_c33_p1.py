"""Cycle-33 clone-1 P1 exploration: iterate params byte-determinism."""
import dawdreamer as daw
import json, hashlib

def probe_p1(name, path):
    print('---', name, 'P1 ---')
    e1 = daw.RenderEngine(44100, 512)
    p1 = e1.make_plugin_processor('t', path)
    n = p1.get_plugin_parameter_size()
    d1 = {p1.get_parameter_name(i): p1.get_parameter(i) for i in range(n)}
    s1 = json.dumps(d1, sort_keys=True, separators=(",", ":"))
    e2 = daw.RenderEngine(44100, 512)
    p2 = e2.make_plugin_processor('t', path)
    d2 = {p2.get_parameter_name(i): p2.get_parameter(i) for i in range(n)}
    s2 = json.dumps(d2, sort_keys=True, separators=(",", ":"))
    print('  n=%d run1_sha=%s run2_sha=%s' % (n, hashlib.sha256(s1.encode()).hexdigest()[:16], hashlib.sha256(s2.encode()).hexdigest()[:16]))
    print('  IDENTICAL=', s1 == s2)

def probe_p3(name, path):
    print('---', name, 'P3 ---')
    e1 = daw.RenderEngine(44100, 512)
    p1 = e1.make_plugin_processor('t', path)
    d1 = p1.get_plugin_parameters_description()
    s1 = json.dumps(d1, sort_keys=True, separators=(",", ":"))
    e2 = daw.RenderEngine(44100, 512)
    p2 = e2.make_plugin_processor('t', path)
    d2 = p2.get_plugin_parameters_description()
    s2 = json.dumps(d2, sort_keys=True, separators=(",", ":"))
    print('  run1_sha=%s run2_sha=%s IDENTICAL=%s' % (
        hashlib.sha256(s1.encode()).hexdigest()[:16],
        hashlib.sha256(s2.encode()).hexdigest()[:16],
        s1 == s2))

for nm, pth in [('Surge XT', '/usr/lib/vst3/Surge XT.vst3'), ('Dexed', '/usr/lib/vst3/Dexed.vst3')]:
    probe_p1(nm, pth)
    probe_p3(nm, pth)
