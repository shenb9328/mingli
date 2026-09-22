# -*- coding: utf-8 -*-
"""V2.2 文献证据严格审计：宁可漏收，不可伪收。"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"
def load(n):
    with open(DATA/n,"r",encoding="utf-8") as f:return json.load(f)
sources=load("sources.json"); texts=load("classical_texts.json"); interps=load("interpretations.json"); rules=load("core_rules.json"); aux=load("auxiliary_rules.json"); evidence=load("evidence_records.json"); rejected=load("rejected_texts.json")
source_ids={x["source_id"] for x in sources}; text_ids={x["text_id"] for x in texts}; interp_ids={x["interp_id"] for x in interps}
errors=[]
for t in texts:
    e=t.get("evidence",{})
    if t["source_id"] not in source_ids: errors.append(f'{t["text_id"]}: source_id不存在')
    if e.get("evidence_level") not in {"E0","E1","E2","E3","E4","E5"}: errors.append(f'{t["text_id"]}: evidence_level非法')
    if e.get("evidence_level")=="E2" and not e.get("digital_refs"): errors.append(f'{t["text_id"]}: E2必须有digital_refs')
    if e.get("evidence_level") in {"E3","E4","E5"} and not e.get("scan_verified"): errors.append(f'{t["text_id"]}: E3-E5必须scan_verified=true')
    if e.get("evidence_level") in {"E4","E5"} and not (e.get("page") or e.get("scan_ref")): errors.append(f'{t["text_id"]}: E4/E5必须有页码或scan_ref')
for i in interps:
    if i["text_ref"] not in text_ids: errors.append(f'{i["interp_id"]}: text_ref不存在')
for r in rules+aux:
    for tid in r.get("text_refs",[]):
        if tid not in text_ids: errors.append(f'{r["rule_id"]}: text_ref不存在 {tid}')
    for iid in r.get("interp_refs",[]):
        if iid not in interp_ids: errors.append(f'{r["rule_id"]}: interp_ref不存在 {iid}')
print("====== V2.2 文献证据严格审计 ======")
print(f"可信原文: {len(texts)}"); print(f"注疏: {len(interps)}"); print(f"核心规则: {len(rules)}"); print(f"辅助规则: {len(aux)}"); print(f"隔离文本: {len(rejected)}")
print("证据分布:", {lv:sum(1 for x in texts if x.get("evidence",{}).get("evidence_level")==lv) for lv in ["E0","E1","E2","E3","E4","E5"]})
if errors:
    print("[FAIL]"); [print(" -",e) for e in errors]; raise SystemExit(1)
print("[PASS] 结构、外键与证据门槛审计通过")
print("[NOTE] 当前可信原文最高仅E2；E3/E4/E5必须后续以扫描页证据升级。")
