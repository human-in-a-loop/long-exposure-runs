"""c74 one-shot: byte-det x2 check on M-V4-EAR-1 substantive scoring."""
import json, hashlib, tempfile, os, pathlib
from scripts.ear.v4_ear import build_exemplar_signatures, leave_one_out, sanity_gate, load_exemplar_set


def compute() -> str:
    es = load_exemplar_set()
    sigs = build_exemplar_signatures(es)
    scores = leave_one_out(es, sigs)
    gate = sanity_gate(scores)
    payload = {"scores": {k: round(v, 10) for k, v in scores.items()}, "sanity": gate}
    return json.dumps(payload, sort_keys=True)


def main() -> None:
    shas = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as td:
            os.chdir(td)
            os.chdir(pathlib.Path(__file__).resolve().parents[1])
            shas.append(hashlib.sha256(compute().encode()).hexdigest())
    result = {
        "run1_sha256": shas[0],
        "run2_sha256": shas[1],
        "byte_det_holds": shas[0] == shas[1],
        "cycle": 74,
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    out = pathlib.Path("data/v4/ear/byte_determinism_c74.json")
    out.write_text(json.dumps(result, sort_keys=True, indent=2))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
