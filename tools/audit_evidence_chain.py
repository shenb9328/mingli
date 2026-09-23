#!/usr/bin/env python3
"""V3.7 evidence-chain audit.

This audit is intentionally non-destructive: it reports provenance gaps without
changing classical_texts/core_rules. It is stricter than validate_rules.py.

Usage:
  python3 tools/audit_evidence_chain.py
"""
from __future__ import annotations
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

parser = argparse.ArgumentParser(description="Audit the V3.7 evidence chain")
parser.add_argument("--json-out", default=None, help="Write a machine-readable JSON report")
parser.add_argument("--no-fail", action="store_true", help="Do not exit non-zero when issues are found")
ARGS = parser.parse_args()

def load(name):
    with (DATA / name).open(encoding="utf-8") as f:
        return json.load(f)

texts = load("classical_texts.json")
rules = load("core_rules.json")
evidence = load("evidence_records.json")
interps = load("interpretations.json")
sources = load("sources.json")

text_ids = [x.get("text_id") for x in texts]
text_set = {x for x in text_ids if x}
evidence_by_text = defaultdict(list)
for e in evidence:
    evidence_by_text[e.get("text_ref")].append(e)

source_ids = {x.get("source_id") for x in sources}
interp_ids = {x.get("interp_id") for x in interps}

issues = []
def issue(kind, detail):
    issues.append((kind, detail))

# 1. IDs and source references
dups = [k for k,v in Counter(text_ids).items() if k and v > 1]
for x in dups:
    issue("duplicate_text_id", x)

for t in texts:
    tid=t.get("text_id")
    if not tid:
        issue("missing_text_id", repr(t)[:160])
    if t.get("source_id") not in source_ids:
        issue("unknown_source_id", f"{tid}: {t.get('source_id')}")
    if not t.get("text"):
        issue("empty_text", tid)

# 2. Independent evidence coverage
for t in texts:
    tid=t.get("text_id")
    evs=evidence_by_text.get(tid, [])
    if not evs:
        issue("missing_evidence_record", tid)
    elif len(evs) > 1:
        issue("multiple_evidence_records", f"{tid}: {len(evs)}")

for e in evidence:
    ref=e.get("text_ref")
    if ref not in text_set:
        issue("orphan_evidence", f"{e.get('evidence_id')}: {ref}")
    if e.get("level") in {"E4","E5"}:
        refs=e.get("references") or []
        if not refs:
            issue("high_level_without_reference", e.get("evidence_id"))
        if not e.get("scan_verified") and not any("scan" in str(r).lower() for r in refs):
            issue("high_level_without_scan_verification", e.get("evidence_id"))

# 3. Embedded provenance sanity
for t in texts:
    tid=t.get("text_id")
    p=t.get("text_provenance") or {}
    ev=t.get("evidence") or {}
    if not p:
        issue("missing_text_provenance", tid)
    if not ev:
        issue("missing_embedded_evidence", tid)
    if ev.get("evidence_level") in {"E4","E5"} and not ev.get("base_edition"):
        issue("embedded_high_level_without_edition", tid)

# 4. Rule references
rule_missing_text=Counter()
rule_missing_interp=Counter()
for r in rules:
    rid=r.get("rule_id")
    for ref in r.get("text_refs", []) or []:
        if ref not in text_set:
            issue("rule_unknown_text_ref", f"{rid}: {ref}")
            rule_missing_text[rid]+=1
    for ref in r.get("interp_refs", []) or []:
        if ref not in interp_ids:
            issue("rule_unknown_interp_ref", f"{rid}: {ref}")
            rule_missing_interp[rid]+=1

for i in interps:
    if i.get("text_ref") not in text_set:
        issue("interpretation_unknown_text_ref", f"{i.get('interp_id')}: {i.get('text_ref')}")

# 5. Evidence level distribution from embedded text layer
levels=Counter((t.get("evidence") or {}).get("evidence_level","MISSING") for t in texts)
sources_count=Counter(t.get("source_id") for t in texts)

print("=== V3.7 Evidence Chain Audit ===")
print(f"classical_texts: {len(texts)}")
print(f"core_rules:      {len(rules)}")
print(f"interpretations: {len(interps)}")
print(f"evidence_records:{len(evidence)}")
print(f"independent evidence coverage: {sum(bool(evidence_by_text.get(t)) for t in text_set)}/{len(text_set)}")
print("\nEmbedded evidence levels:")
for k,v in sorted(levels.items()):
    print(f"  {k}: {v}")
print("\nClassical text source distribution:")
for k,v in sources_count.most_common():
    print(f"  {k}: {v}")
print("\nIssue summary:")
for k,v in Counter(x[0] for x in issues).most_common():
    print(f"  {k}: {v}")

print("\nFirst 100 issues:")
for k,d in issues[:100]:
    print(f"  [{k}] {d}")

if ARGS.json_out:
    out = Path(ARGS.json_out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "audit_version": "V3.7",
        "classical_texts": len(texts),
        "core_rules": len(rules),
        "interpretations": len(interps),
        "evidence_records": len(evidence),
        "independent_evidence_coverage": {
            "covered": sum(bool(evidence_by_text.get(t)) for t in text_set),
            "total": len(text_set)
        },
        "embedded_evidence_levels": dict(sorted(levels.items())),
        "source_distribution": dict(sources_count.most_common()),
        "issue_counts": dict(Counter(x[0] for x in issues).most_common()),
        "issues": [{"kind": k, "detail": d} for k, d in issues],
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

raise SystemExit(0 if ARGS.no_fail else (1 if issues else 0))
