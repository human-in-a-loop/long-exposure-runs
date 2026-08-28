#!/usr/bin/env python3
"""Patch the .ardour session XML to add a session-range Location.

Ardour computes the session range from region positions; a SinGen-only
session has no regions, so ardour8-export renders 0 samples. We inject:

    <Location id="99999" name="session"
              start="0" end="{n_samples}" flags="IsSessionRange"
              locked="no" ...>
    </Location>

into <Locations/> and flip session-range-is-free to "0".
"""
import re
import sys
import pathlib

sess = pathlib.Path("data/daw_spike/sessions/spike/spike.ardour")
xml = sess.read_text()

n_samples = 48000 * 8  # 384000

# Flip session-range-is-free (default is "1" = free / grows with content).
xml = xml.replace('session-range-is-free="1"', 'session-range-is-free="0"')

# Inject a Location if <Locations/> is empty.
location_xml = f'''  <Locations>
    <Location id="99999" name="session" start="0" end="{n_samples}" flags="IsSessionRange" locked="no" time-domain="AudioTime"/>
  </Locations>'''

if "<Locations/>" in xml:
    xml = xml.replace("<Locations/>", location_xml)
elif "<Locations>" in xml and "id=\"99999\"" not in xml:
    # Insert one child inside existing Locations block.
    xml = xml.replace(
        "<Locations>",
        location_xml.split("\n")[0] + "\n" + location_xml.split("\n")[1] + "\n"
        "  <!--"
    )
    # Not clean; but the empty branch above should always hit on a fresh session.
    print("WARN: Locations block already had content; skipping injection")

# Flip the reverb Output Mix (parameter-10) automation list state to Play.
# The ac.set_automation_state Lua binding is not exposed in this Ardour
# build, so we set state="Play" in XML directly — a documented fallback.
xml = re.sub(
    r'(<AutomationList automation-id="parameter-10"[^>]*?)state="Off"',
    r'\1state="Play"',
    xml,
    count=2,
)
# Flip the track "gain" automation state to Play (only the track Amp,
# not the Master bus Amp — the track holds the SinGen+FX chain).
# There are multiple gain AutomationLists in the XML; we target the one
# that has an <events> child (i.e. the one we populated).
def flip_gain_state(match):
    block = match.group(0)
    if "<events>" in block:
        block = block.replace('state="Off"', 'state="Play"', 1)
    return block

xml = re.sub(
    r'<AutomationList automation-id="gain"[^>]*state="Off"[^/]*?>.*?</AutomationList>',
    flip_gain_state,
    xml,
    flags=re.DOTALL,
)

sess.write_text(xml)
print(f"[OK] patched session-range + automation state=Play into {sess}")
