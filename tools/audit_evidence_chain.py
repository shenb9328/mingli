#!/usr/bin/env python3
"""V3.7 evidence-chain and clean-text verification audit (Phase 2).

This audit is intentionally non-destructive: it reports provenance gaps and text
substantiation gaps without mutating classical_texts or core_rules.

Audits performed:
1. Structural integrity: IDs, duplicate IDs, missing fields, foreign keys.
2. Independent evidence record coverage: evidence_records.json vs classical_texts.
3. Clean-text substantiation (Phase 2):
   - Type A: Does classical_texts.text genuinely exist in clean_texts/?
   - Type B: Does source_id correctly correspond to the matching book?
   - Type C: Is text marked as 'original' actually coming from later commentary (e.g. Ren, Xu)?
   - Type D: Is evidence_level (E2/E3/E4) proportional to actual evidence support?
4. Rule & Interpretation traceability: rule -> text_ref, interp -> text_ref.

Usage:
  python3 tools/audit_evidence_chain.py [--json-out report.json] [--no-fail]
"""
from __future__ import annotations
import json
import argparse
import re
from pathlib import Path
from collections import Counter, defaultdict

try:
    import opencc
    _t2s = opencc.OpenCC('t2s')
    def to_simplified(s: str) -> str:
        return _t2s.convert(s)
except Exception:
    def to_simplified(s: str) -> str:
        return s

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CLEAN_DIR = ROOT / "clean_texts"

parser = argparse.ArgumentParser(description="Audit the V3.7 evidence chain and text substantiation")
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

# Prepare text normalization
def norm(s: str) -> str:
    if not s:
        return ""
    s = to_simplified(s)
    return re.sub(r'[\s\n\r\t，。、；：！？“”（）《》【】…—\-\.·’‘\'\"]', '', s)

# Load clean texts corpus by source_id
SOURCE_FILE_MAP = {
    'SRC_SMTH': ['三命通会_clean.txt'],
    'SRC_YHZP': ['渊海子平_clean.txt'],
    'SRC_DTS': ['滴天髓原文_clean.txt', '滴天髓阐微_clean.txt', '滴天髓补注_clean.txt'],
    'SRC_DTS_CW': ['滴天髓阐微_clean.txt'],
    'SRC_DTS_BJ': ['滴天髓补注_clean.txt'],
    'SRC_QTBG': ['窮通寶鑒_clean.txt', '穷通宝鉴_clean.txt'],
    'SRC_ZPZQ': ['子平真诠_clean.txt', '子平真诠评注_clean.txt'],
    'SRC_SFTK': ['神峰通考_clean.txt']
}

clean_corpus_by_sid = {}
clean_files_corpus = {}
for sid, files in SOURCE_FILE_MAP.items():
    combined = ""
    for f in files:
        p = CLEAN_DIR / f
        if p.exists():
            content = p.read_text(encoding="utf-8")
            clean_files_corpus[f] = norm(content)
            combined += content + "\n"
    clean_corpus_by_sid[sid] = norm(combined)

all_clean_corpus = norm("".join(clean_corpus_by_sid.values()))

text_ids = [x.get("text_id") or x.get("id") for x in texts]
text_set = {x for x in text_ids if x}
evidence_by_text = defaultdict(list)
for e in evidence:
    evidence_by_text[e.get("text_ref")].append(e)

source_ids = {x.get("source_id") for x in sources}
interp_ids = {x.get("interp_id") for x in interps}

issues = []
def issue(kind, detail):
    issues.append((kind, detail))

# 1. IDs and basic structure
dups = [k for k, v in Counter(text_ids).items() if k and v > 1]
for x in dups:
    issue("duplicate_text_id", x)

for t in texts:
    tid = t.get("text_id") or t.get("id")
    if not t.get("text_id") and t.get("id"):
        issue("legacy_id_field", f"{t.get('id')}: uses 'id' instead of 'text_id'")
    elif not tid:
        issue("missing_text_id", repr(t)[:160])
    if t.get("source_id") not in source_ids:
        issue("unknown_source_id", f"{tid}: {t.get('source_id')}")
    if not t.get("text"):
        issue("empty_text", tid)

# 2. Independent evidence coverage
for t in texts:
    tid = t.get("text_id") or t.get("id")
    evs = evidence_by_text.get(tid, [])
    if not evs:
        issue("missing_evidence_record", tid)
    elif len(evs) > 1:
        issue("multiple_evidence_records", f"{tid}: {len(evs)}")

for e in evidence:
    ref = e.get("text_ref")
    if ref not in text_set:
        issue("orphan_evidence", f"{e.get('evidence_id')}: {ref}")
    if e.get("level") in {"E4", "E5"}:
        refs = e.get("references") or []
        if not refs:
            issue("high_level_without_reference", e.get("evidence_id"))
        if not e.get("scan_verified") and not any("scan" in str(r).lower() for r in refs):
            issue("high_level_without_scan_verification", e.get("evidence_id"))

# 3. Embedded provenance sanity
for t in texts:
    tid = t.get("text_id") or t.get("id")
    p = t.get("text_provenance") or {}
    ev = t.get("evidence") or {}
    if not p:
        issue("missing_text_provenance", tid)
    if not ev:
        issue("missing_embedded_evidence", tid)
    if ev.get("evidence_level") in {"E4", "E5"} and not (ev.get("base_edition") or ev.get("scan_ref")):
        issue("embedded_high_level_without_edition", tid)

# 4. Clean-text verification (Types A, B, C, D)
text_verification_stats = {
    "exact_book_match": 0,
    "cross_book_match": 0,
    "commentary_layer_identified": 0,
    "unsubstantiated_text": 0
}

for t in texts:
    tid = t.get("text_id") or t.get("id")
    raw_txt = t.get("text", "")
    n_txt = norm(raw_txt)
    sid = t.get("source_id")
    ev = t.get("evidence") or {}
    lvl = ev.get("evidence_level", "E0")
    prov = t.get("text_provenance") or {}

    if not n_txt:
        continue

    book_corpus = clean_corpus_by_sid.get(sid, "")
    
    # Check Type A & B: Substring presence in clean texts
    in_own_book = (n_txt in book_corpus) or (len(n_txt) >= 8 and n_txt[:8] in book_corpus)
    in_any_book = in_own_book or (n_txt in all_clean_corpus) or (len(n_txt) >= 8 and n_txt[:8] in all_clean_corpus)

    if in_own_book:
        text_verification_stats["exact_book_match"] += 1
    elif in_any_book:
        text_verification_stats["cross_book_match"] += 1
        issue("cross_book_source_mismatch", f"{tid}: claims source_id {sid} but text is found in another classic")
    else:
        text_verification_stats["unsubstantiated_text"] += 1
        issue("text_not_in_clean_corpus", f"{tid} ({sid}): {raw_txt[:30]}")

    # Check Type C: Commentary mislabeled as original text
    # e.g., text mentions Ren Tieqiao or Xu Lewu notes, or from later commentary books
    src_layer = t.get("source_layer", "")
    t_type = t.get("type", "")
    if sid == "SRC_DTS" and src_layer in {"original_text", "original_jingtou", "经文"}:
        # Check if text is only found in Chanwei (Ren commentary) or Buzhu (Xu commentary)
        orig_corpus = clean_files_corpus.get('滴天髓原文_clean.txt', '')
        if orig_corpus and n_txt not in orig_corpus and (len(n_txt) >= 8 and n_txt[:8] not in orig_corpus):
            cw_corpus = clean_files_corpus.get('滴天髓阐微_clean.txt', '')
            bj_corpus = clean_files_corpus.get('滴天髓补注_clean.txt', '')
            if (n_txt in cw_corpus or (len(n_txt) >= 8 and n_txt[:8] in cw_corpus)) or \
               (n_txt in bj_corpus or (len(n_txt) >= 8 and n_txt[:8] in bj_corpus)):
                text_verification_stats["commentary_layer_identified"] += 1
                issue("commentary_mislabeled_as_jingtou", f"{tid}: marked as DTS 经文 but text belongs to 任铁樵/徐乐吾评注层")

    if sid == "SRC_ZPZQ" and src_layer in {"original_text", "original_shen", "沈孝瞻原文"}:
        # Check if text only in Xu commentary
        zpzq_orig = clean_files_corpus.get('子平真诠_clean.txt', '')
        zpzq_pz = clean_files_corpus.get('子平真诠评注_clean.txt', '')
        if zpzq_orig and n_txt not in zpzq_orig and (len(n_txt) >= 8 and n_txt[:8] not in zpzq_orig):
            if zpzq_pz and (n_txt in zpzq_pz or (len(n_txt) >= 8 and n_txt[:8] in zpzq_pz)):
                text_verification_stats["commentary_layer_identified"] += 1
                issue("commentary_mislabeled_as_original_author", f"{tid}: marked as 沈孝瞻原文 but text only appears in 徐乐吾评注")

    # Check Type D: Evidence level versus actual substantiation
    if not in_any_book and lvl in {"E2", "E3", "E4", "E5"}:
        issue("unsubstantiated_high_evidence_level", f"{tid}: claims {lvl} but text cannot be matched in clean_texts corpus")

# 5. Rule references
rule_missing_text = Counter()
rule_missing_interp = Counter()
for r in rules:
    rid = r.get("rule_id")
    for ref in r.get("text_refs", []) or []:
        if ref not in text_set:
            issue("rule_unknown_text_ref", f"{rid}: {ref}")
            rule_missing_text[rid] += 1
    for ref in r.get("interp_refs", []) or []:
        if ref not in interp_ids:
            issue("rule_unknown_interp_ref", f"{rid}: {ref}")
            rule_missing_interp[rid] += 1

for i in interps:
    if i.get("text_ref") not in text_set:
        issue("interpretation_unknown_text_ref", f"{i.get('interp_id')}: {i.get('text_ref')}")

# 6. Distributions
levels = Counter((t.get("evidence") or {}).get("evidence_level", "MISSING") for t in texts)
sources_count = Counter(t.get("source_id") for t in texts)

print("=== V3.7 Evidence Chain & Text Substantiation Audit ===")
print(f"classical_texts: {len(texts)}")
print(f"core_rules:      {len(rules)}")
print(f"interpretations: {len(interps)}")
print(f"evidence_records:{len(evidence)}")
print(f"independent evidence coverage: {sum(bool(evidence_by_text.get(t)) for t in text_set)}/{len(text_set)}")

print("\n--- Clean Texts Substantiation (Phase 2) ---")
print(f"Exact book match in clean_texts: {text_verification_stats['exact_book_match']}/{len(texts)} ({text_verification_stats['exact_book_match']/len(texts)*100:.1f}%)")
print(f"Cross-book match:                {text_verification_stats['cross_book_match']}/{len(texts)}")
print(f"Commentary layer mislabelings:   {text_verification_stats['commentary_layer_identified']}")
print(f"Unsubstantiated text in corpus:  {text_verification_stats['unsubstantiated_text']}/{len(texts)} ({text_verification_stats['unsubstantiated_text']/len(texts)*100:.1f}%)")

print("\nEmbedded evidence levels:")
for k, v in sorted(levels.items()):
    print(f"  {k}: {v}")
print("\nClassical text source distribution:")
for k, v in sources_count.most_common():
    print(f"  {k}: {v}")
print("\nIssue summary:")
for k, v in Counter(x[0] for x in issues).most_common():
    print(f"  {k}: {v}")

print("\nFirst 30 issues:")
for k, d in issues[:30]:
    print(f"  [{k}] {d}")

if ARGS.json_out:
    out = Path(ARGS.json_out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "audit_version": "V3.7-phase2",
        "classical_texts": len(texts),
        "core_rules": len(rules),
        "interpretations": len(interps),
        "evidence_records": len(evidence),
        "independent_evidence_coverage": {
            "covered": sum(bool(evidence_by_text.get(t)) for t in text_set),
            "total": len(text_set)
        },
        "text_substantiation": text_verification_stats,
        "embedded_evidence_levels": dict(sorted(levels.items())),
        "source_distribution": dict(sources_count.most_common()),
        "issue_counts": dict(Counter(x[0] for x in issues).most_common()),
        "issues": [{"kind": k, "detail": d} for k, d in issues],
    }
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote full report to: {out}")

raise SystemExit(0 if ARGS.no_fail else (1 if issues else 0))
