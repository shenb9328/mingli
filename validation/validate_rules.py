# -*- coding: utf-8 -*-
"""V2.2 文献证据严格审计：宁可漏收，不可伪收。"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"
def load(n):
    with open(DATA/n,"r",encoding="utf-8") as f:return json.load(f)
sources=load("sources.json"); texts=load("classical_texts.json"); interps=load("interpretations.json"); rules=load("core_rules.json"); aux=load("auxiliary_rules.json"); evidence=load("evidence_records.json"); rejected=load("rejected_texts.json")
relations=load("stem_branch_relations.json"); hidden=load("branch_hidden_stems.json"); ten_gods=load("ten_gods_schema.json"); luck=load("luck_rules.json"); shensha=load("shensha_schema.json"); jiazi=load("sixty_jiazi.json"); strength=load("heuristic_strength_model.json"); flaws=load("flaw_and_remedy.json"); pattern_logic=load("pattern_logic.json"); tiaohou=load("tiaohou_matrix.json"); growth=load("twelve_growth.json")
source_ids={x["source_id"] for x in sources}; text_ids={x["text_id"] for x in texts}; interp_ids={x["interp_id"] for x in interps}
errors=[]
# V3.2 结构矩阵审计
if len(tiaohou.get("records",[])) != 120: errors.append(f"tiaohou_matrix: 必须恰好120格，当前{len(tiaohou.get("records",[]))}")
expected={f"{s}_{m}" for s in "甲乙丙丁戊己庚辛壬癸" for m in "寅卯辰巳午未申酉戌亥子丑"}
actual={r.get("day_master")+"_"+r.get("month_branch") for r in tiaohou.get("records",[])}
if actual != expected: errors.append("tiaohou_matrix: 10×12键空间不完整或存在重复/非法组合")
for r in tiaohou.get("records",[]):
    if r.get("evidence_level") not in {"E0","E1","E2","E3","E4","E5"}: errors.append(f"{r.get("id")}: evidence_level非法")
    if r.get("evidence_level")=="E2" and not r.get("source_refs"): errors.append(f"{r.get("id")}: E2必须有source_refs")
if len(growth.get("stages",[])) != 12: errors.append("twelve_growth: stages必须12项")
# V3.3 工程模块审计
if len(jiazi.get("records",[])) != 60: errors.append("sixty_jiazi: 必须60项")
if len(shensha.get("schemas",[])) < 1: errors.append("shensha_schema: schemas不能为空")
if not strength.get("weights"): errors.append("heuristic_strength_model: weights不能为空")
if not flaws.get("patterns"): errors.append("flaw_and_remedy: patterns不能为空")
if not pattern_logic.get("patterns"): errors.append("pattern_logic: patterns不能为空")
if abs(sum(strength.get("weights",{}).values())-1)>1e-9: errors.append("heuristic_strength_model: weights之和必须为1")
for t in texts:
    e=t.get("evidence",{})
    if t["source_id"] not in source_ids: errors.append(f'{t["text_id"]}: source_id不存在')
    if e.get("evidence_level") not in {"E0","E1","E2","E3","E4","E5"}: errors.append(f'{t["text_id"]}: evidence_level非法')
    if e.get("evidence_level")=="E2" and not e.get("digital_refs"): errors.append(f'{t["text_id"]}: E2必须有digital_refs')
    if e.get("evidence_level") in {"E3","E4","E5"} and not e.get("scan_verified"): errors.append(f'{t["text_id"]}: E3-E5必须scan_verified=true')
    if e.get("evidence_level") in {"E4","E5"} and not (e.get("page") or e.get("scan_ref")): errors.append(f'{t["text_id"]}: E4/E5必须有页码或scan_ref')
relation_ids={x["relation_id"] for x in relations}
for r in aux:
    cm=r.get("computational_model",{})
    refs=cm.get("relation_refs",[])
    if cm.get("relation_ref"): refs=refs+[cm["relation_ref"]]
    for ref in refs:
        if ref not in relation_ids: errors.append(f'{r["rule_id"]}: relation_ref不存在 {ref}')
for i in interps:
    if i["text_ref"] not in text_ids: errors.append(f'{i["interp_id"]}: text_ref不存在')
for r in rules+aux:
    for sid in r.get("source_refs",[]):
        if sid not in source_ids: errors.append(f'{r["rule_id"]}: source_ref不存在 {sid}')
    for tid in r.get("text_refs",[]):
        if tid not in text_ids: errors.append(f'{r["rule_id"]}: text_ref不存在 {tid}')
    for iid in r.get("interp_refs",[]):
        if iid not in interp_ids: errors.append(f'{r["rule_id"]}: interp_ref不存在 {iid}')
print("====== V2.2 文献证据严格审计 ======")
print(f"可信原文: {len(texts)}"); print(f"注疏: {len(interps)}"); print(f"核心规则: {len(rules)}"); print(f"辅助规则: {len(aux)}"); print(f"隔离文本: {len(rejected)}"); print(f"关系规则: {len(relations)}"); print(f"藏干表: {len(hidden)}")
print("证据分布:", {lv:sum(1 for x in texts if x.get("evidence",{}).get("evidence_level")==lv) for lv in ["E0","E1","E2","E3","E4","E5"]})
if errors:
    print("[FAIL]"); [print(" -",e) for e in errors]; raise SystemExit(1)
print("[PASS] 结构、外键与证据门槛审计通过")
print("[NOTE] 当前可信原文最高仅E2；E3/E4/E5必须后续以扫描页证据升级。")
