"""Cycle-33 clone-1 exploration probe (scratch). Archived to stale/ post-use."""
import dawdreamer as daw
import tempfile, os, hashlib

def probe(name, plugin_path):
    print('---', name, '---')
    if not os.path.exists(plugin_path):
        print('  MISSING plugin path'); return
    e = daw.RenderEngine(44100, 512)
    p = e.make_plugin_processor('t', plugin_path)
    d1 = tempfile.mkdtemp(); d2 = tempfile.mkdtemp()
    try:
        p.save_state(os.path.join(d1, 's.bin'))
        b1 = open(os.path.join(d1, 's.bin'), 'rb').read()
        print('  save_state OK sz=%d sha=%s' % (len(b1), hashlib.sha256(b1).hexdigest()[:16]))
    except Exception as ex:
        print('  save_state FAIL:', ex); return
    e2 = daw.RenderEngine(44100, 512)
    p2 = e2.make_plugin_processor('t', plugin_path)
    p2.save_state(os.path.join(d2, 's.bin'))
    b2 = open(os.path.join(d2, 's.bin'), 'rb').read()
    print('  run2   OK sz=%d sha=%s' % (len(b2), hashlib.sha256(b2).hexdigest()[:16]))
    print('  IDENTICAL=', b1 == b2)
    patch = p.get_patch()
    print('  patch len=%d' % len(patch))
    npars = p.get_plugin_parameter_size()
    print('  num_parameters=%d' % npars)

probe('Surge XT', '/usr/lib/vst3/Surge XT.vst3')
probe('Dexed', '/usr/lib/vst3/Dexed.vst3')
