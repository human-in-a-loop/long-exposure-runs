#!/usr/bin/python3
# Run all three probes + resolve verdict in canonical order.
# Author: cyd7bevdr@mozmail.com, cycle 38, fork 33a2a8003c84 / clone-1.
import sys
assert sys.executable == '/usr/bin/python3', sys.executable

from scripts.score_bridge_v2.probe_p1_mscore3_flags import main as p1_main
from scripts.score_bridge_v2.probe_p2_normalizer import run_probe as p2_main
from scripts.score_bridge_v2.probe_p3_alternative_backends import main as p3_main
from scripts.score_bridge_v2.verdict import (
    compute_anchor_preservation, resolve_verdict,
)


def main():
    print('== P1 ==')
    p1_main()
    print('== P2 ==')
    p2_main()
    print('== P3 ==')
    p3_main()
    print('== anchor preservation ==')
    compute_anchor_preservation()
    print('== verdict ==')
    v = resolve_verdict()
    print('verdict:', v['verdict'])


if __name__ == '__main__':
    main()
