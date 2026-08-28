#!/usr/bin/env python3
"""Generic session patcher for M-DAW-SPIKE-1/gap-closure sessions.

Injects a session-range Location and flips every AutomationList
that has non-empty <events> children from state="Off" to state="Play".
The `set_automation_state` Lua binding is not exposed in Ardour 8.x,
so this XML post-patch is the documented fallback (per cycle-1
daw_spike_report.md §5 GAP-2 fallback #1's precursor).

Invocation:
  /usr/bin/python3 scripts/daw_spike/patch_session_generic.py <sess.ardour>

Non-factor AST isolation preserved (no sidecar_nonfactor imports).
"""
import re
import sys
import pathlib

assert sys.executable == '/usr/bin/python3', sys.executable


def patch(sess_path: pathlib.Path, n_samples: int = 384000) -> dict:
    xml = sess_path.read_text()
    stats = {"range_injected": False, "state_flips": 0}

    xml = xml.replace('session-range-is-free="1"', 'session-range-is-free="0"')
    location_xml = (
        '  <Locations>\n'
        f'    <Location id="99999" name="session" start="0" end="{n_samples}" '
        'flags="IsSessionRange" locked="no" time-domain="AudioTime"/>\n'
        '  </Locations>'
    )
    if "<Locations/>" in xml:
        xml = xml.replace("<Locations/>", location_xml)
        stats["range_injected"] = True

    # Flip every AutomationList that has non-empty events content.
    # Pattern: <AutomationList ... state="Off" ...> ... <events> ... </events> ... </AutomationList>
    # We do a two-pass block replace: for each AutomationList, if it contains
    # <events> (with any non-empty child text) then flip state="Off" -> "Play".
    def flip(match: "re.Match") -> str:
        block = match.group(0)
        if "<events>" not in block:
            return block
        # Consider empty <events></events> as non-active.
        m = re.search(r'<events>\s*(\S)', block)
        if not m:
            return block
        new_block, n = re.subn(r'state="Off"', 'state="Play"', block, count=1)
        stats["state_flips"] += n
        return new_block

    xml = re.sub(
        r'<AutomationList\b[^>]*>.*?</AutomationList>',
        flip,
        xml,
        flags=re.DOTALL,
    )

    sess_path.write_text(xml)
    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("usage: patch_session_generic.py <sess.ardour> [n_samples]\n")
        sys.exit(2)
    p = pathlib.Path(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 384000
    stats = patch(p, n)
    print("patched", p, stats)
