#!/usr/bin/env python3
"""Database coverage, linkage rate, and evidence health report generator.

Generates comprehensive metrics on:
1. Corpus size and distribution across 8 classics.
2. Rule linkage rate (classical_texts <-> core_rules).
3. Evidence integrity (evidence_records coverage, unsubstantiated texts, commentary layers).
4. Structural layer counts (auxiliary_rules, pattern_catalog, flaw_and_remedy, interpretations).
5. Data quality metrics (empty fields, character encoding, duplicates).

Usage:
  python3 tools/db_coverage_report.py [--json-out report.json]
"""
from __future__ import annotations
import json
import argparse
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CLEAN_DIR = ROOT / "clean_texts"

parser = argparse.ArgumentParser(description="Generate MingLi DB Coverage & Linkage Report")
parser.add_argument("--json-out", default=None, help="Path to write JSON report")
ARGS = parser.parse_args()

def load(name):
    p = DATA / name
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as f:
        return json.load(f)

texts = load("classical_texts.json") or []
rules = load("core_rules.json") or []
evidence = load("evidence_records.json") or []
interps = load("interpretations.json") or []
sources = load("sources.json") or []
aux_rules = load("auxiliary_rules.json") or []
catalog = load("pattern_catalog.json") or {}
logic = load("pattern_logic.json") or {}
flaws = load("flaw_and_remedy.json") or {}

# 1. Classical text distribution
text_ids = {t.get("text_id") or t.get("id") for t in texts}
sources_count = Counter(t.get("source_id") for t in texts)

# 2. Rule linkage rate
cited_text_ids = set()
for r in rules:
    for ref in r.get("text_refs", []):
        cited_text_ids.add(ref)

rules_with_text_refs = sum(1 for r in rules if r.get("text_refs"))
rules_with_interp_refs = sum(1 for r in rules if r.get("interp_refs"))
hanging_text_refs = [ref for r in rules for ref in r.get("text_refs", []) if ref not in text_ids]

# 3. Evidence coverage
ev_by_ref = {e.get("text_ref"): e for e in evidence}
covered_evidence = sum(1 for tid in text_ids if tid in ev_by_ref)

ev_levels = Counter((t.get("evidence") or {}).get("evidence_level", "MISSING") for t in texts)

# 4. Data quality metrics: Traditional vs Simplified, short texts
def has_traditional(s: str) -> bool:
    # Sample check for common traditional characters
    trad_sample = set("體點洩時裏門與無為過災殺傷祿貴經萬歷會衝戰")
    return any(c in trad_sample for c in s)

trad_texts = sum(1 for t in texts if has_traditional(t.get("text", "")))
short_texts = sum(1 for t in texts if len(t.get("text", "")) < 10)

# Check duplicate texts
text_contents = Counter(t.get("text", "").strip() for t in texts if t.get("text"))
duplicate_groups = {k: v for k, v in text_contents.items() if v > 1}

# Check confidence values in core_rules
conf_grades = Counter(str(r.get("confidence", {}).get("grade") if isinstance(r.get("confidence"), dict) else r.get("confidence")) for r in rules)
verif_grades = Counter(str(r.get("verification")) for r in rules)

report = {
    "summary": {
        "classical_texts_count": len(texts),
        "core_rules_count": len(rules),
        "evidence_records_count": len(evidence),
        "interpretations_count": len(interps),
        "auxiliary_rules_count": len(aux_rules),
        "pattern_catalog_count": len(catalog.get("patterns", []) if isinstance(catalog, dict) else catalog),
        "pattern_logic_count": len(logic.get("patterns", {}) if isinstance(logic, dict) else logic),
        "flaw_and_remedy_count": len(flaws.get("patterns", []) if isinstance(flaws, dict) else flaws),
    },
    "linkage": {
        "classical_texts_cited_by_rules": len(cited_text_ids),
        "citation_coverage_pct": round(len(cited_text_ids) / len(texts) * 100, 2) if texts else 0,
        "rules_with_text_refs": rules_with_text_refs,
        "rules_with_text_refs_pct": round(rules_with_text_refs / len(rules) * 100, 2) if rules else 0,
        "rules_with_interp_refs": rules_with_interp_refs,
        "hanging_text_refs_count": len(hanging_text_refs)
    },
    "evidence_health": {
        "independent_evidence_coverage": f"{covered_evidence}/{len(texts)}",
        "independent_coverage_pct": round(covered_evidence / len(texts) * 100, 2) if texts else 0,
        "embedded_evidence_levels": dict(sorted(ev_levels.items()))
    },
    "source_distribution": dict(sources_count.most_common()),
    "data_quality": {
        "texts_with_traditional_glyphs": trad_texts,
        "short_texts_under_10_chars": short_texts,
        "duplicate_text_groups_count": len(duplicate_groups),
        "confidence_grades": dict(conf_grades),
        "verification_values": dict(verif_grades)
    }
}

print("=" * 60)
print("       📊 MINGLI 知识库与规则引擎覆盖率报告")
print("=" * 60)
print(f"古籍文本总数 (classical_texts): {len(texts):>6} 条")
print(f"核心规则总数 (core_rules):      {len(rules):>6} 条")
print(f"独立证据记录 (evidence_records):{len(evidence):>6} 条 (覆盖率 {report['evidence_health']['independent_coverage_pct']}%)")
print(f"被规则引用的原文 (链接率):      {len(cited_text_ids):>6} 条 ({report['linkage']['citation_coverage_pct']}%)")
print(f"悬空无效引用 (hanging refs):    {len(hanging_text_refs):>6} 条")
print("-" * 60)
print("【文献分布】")
for s, c in sources_count.most_common():
    print(f"  {s:<12}: {c:>5} 条 ({c/len(texts)*100:4.1f}%)")
print("-" * 60)
print("【证据等级分布】")
for lvl, c in sorted(ev_levels.items()):
    print(f"  {lvl:<12}: {c:>5} 条 ({c/len(texts)*100:4.1f}%)")
print("-" * 60)
print("【结构化规则层现状】")
print(f"  辅助规则 (auxiliary_rules): {len(aux_rules):>4} 条")
print(f"  格局目录 (pattern_catalog): {report['summary']['pattern_catalog_count']:>4} 个")
print(f"  格局判定 (pattern_logic):   {report['summary']['pattern_logic_count']:>4} 项")
print(f"  病药救应 (flaw_and_remedy): {report['summary']['flaw_and_remedy_count']:>4} 条")
print(f"  先贤注疏 (interpretations): {len(interps):>4} 条")
print("-" * 60)
print("【数据质检警示】")
print(f"  繁体字形条目: {trad_texts} 条")
print(f"  文本短于10字: {short_texts} 条")
print(f"  重复文本组合: {len(duplicate_groups)} 组")
print("=" * 60)

if ARGS.json_out:
    p = Path(ARGS.json_out)
    if not p.is_absolute():
        p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"报告已保存至: {p}")
