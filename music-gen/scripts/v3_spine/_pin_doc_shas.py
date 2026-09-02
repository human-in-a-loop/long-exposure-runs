"""One-shot helper: pin doc SHAs to the three-way chain anchors."""
import hashlib
import os
from pathlib import Path


def main() -> None:
    specs = {
        'docs/v3_spine_canonical_midi_serializer_spec.md':
            'data/v3_spine/canonical_serializer_spec_hash.txt',
        'docs/v3_spine_rubric_v2.md':
            'data/v3_spine/rubric_hash_v2.txt',
    }
    for src, dst in specs.items():
        sha = hashlib.sha256(open(src, 'rb').read()).hexdigest()
        Path(os.path.dirname(dst)).mkdir(parents=True, exist_ok=True)
        with open(dst, 'w') as f:
            f.write(sha + '\n')
        print(src, '->', dst, sha[:16])


if __name__ == '__main__':
    main()
