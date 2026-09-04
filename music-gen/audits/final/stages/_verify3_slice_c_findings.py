import json
finding = {
    "ts": "2026-09-04T00:00:00Z",
    "milestone_id": "M-V3-RULES-1/first-activation/rubric-committed",
    "finding_kind": "path_drift",
    "severity": "MINOR",
    "narrative": (
        "POR narrates v3_rules spec doc at "
        "docs/v3_rules_deterministic_extractor_spec_c23.md; on-disk canonical "
        "path is docs/specs/v3_rules_deterministic_extractor_spec_c23.md. "
        "SHA e81ff589200f6d6b... byte-exact under on-disk path; three-way "
        "rubric_hash_v3_rules chain preserved. Cosmetic only."
    ),
}
with open(
    "/home/user/long-exposure-runs/music-gen/audits/final/findings.jsonl", "a"
) as f:
    f.write(json.dumps(finding) + "\n")
print("appended")
