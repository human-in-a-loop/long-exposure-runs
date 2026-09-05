#!/usr/bin/python3
"""One-shot: patch c28 ledger events (lines 1469-1488) to add 'agent' field."""
import json


def main() -> None:
    with open("promise_ledger.jsonl") as f:
        lines = f.readlines()
    patched = 0
    for i in range(1468, 1488):
        d = json.loads(lines[i])
        if "agent" not in d:
            d["agent"] = "worker"
            lines[i] = json.dumps(d, sort_keys=True) + "\n"
            patched += 1
    with open("promise_ledger.jsonl", "w") as f:
        f.writelines(lines)
    print(f"patched {patched} lines")


if __name__ == "__main__":
    main()
