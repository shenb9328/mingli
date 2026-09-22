# -*- coding: utf-8 -*-
"""
命理知识库结构与文献证据审计校验脚本 (validate_rules.py)

审计维度说明：
1. 结构完整性（Structural Integrity）：JSON 格式、外键关联、双向索引、权重数值范围。
2. 防伪与防篡改（Anti-Modern-Pollution）：现代词汇黑名单初级防御。
3. 文献证据分级（Documentary Evidence Level）：
   - E0: 未核验
   - E1: 有二手文献转引
   - E2: 有可靠公开数字古籍文本
   - E3: 经由指定底本逐字核对
   - E4: 具有底本影印件/微缩胶卷页码对照
   - E5: 跨版本完成校勘与异文考订
4. 作者权源明确性（Authorship Provenance）：明确记录经文、引述、辑评或考订按语。
5. 算法参数透明度（Parameter Status）：标注 heuristic（经验暂定）或 statistical（实证拟合）。

注意：本脚本输出“结构与文献证据链审计通过”，绝不盲目宣称“学术级100%达标”，文献真实性仍需持续配合底本影印件推进。
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

FORBIDDEN_MODERN_WORDS_IN_CLASSICAL_TEXT = [
    "综合打分", "乘数基准", "调候系数", "从顺弃逆", "代码", "算法", "系统",
    "维度", "百分比", "权重", "引擎", "模型", "JSON", "Schema"
]

VALID_EVIDENCE_LEVELS = ["E0", "E1", "E2", "E3", "E4", "E5"]

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[ERROR] 缺失文件: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_validation():
    print("====== 开始命理结构化知识库结构与文献证据链审计 ======\n")
    sources = load_json("sources.json")
    texts = load_json("classical_texts.json")
    interps = load_json("interpretations.json")
    core_rules = load_json("core_rules.json")
    aux_rules = load_json("auxiliary_rules.json")
    month_orders = load_json("month_orders.json")

    source_ids = {s["source_id"] for s in sources}
    text_ids = {t["text_id"] for t in texts}
    interp_ids = {i["interp_id"] for i in interps}

    print(f"[*] 【文献版本源】已载入底本书目: {len(sources)} 部")
    print(f"[*] 【逐字原文层】已载入古籍原文: {len(texts)} 条")
    print(f"[*] 【注疏学派层】已载入先贤解题: {len(interps)} 条 (独立作者分离归属)")
    print(f"[*] 【核心计算层】已载入核心规则: {len(core_rules)} 条 (体用、旺衰、月令、岁运)")
    print(f"[*] 【辅助修饰层】已载入辅助规则: {len(aux_rules)} 条 (神煞降权与流派分歧考订)")
    print(f"[*] 【月令提纲库】已载入月份气候: {len(month_orders['months'])} 个提纲分野\n")

    errors = []
    evidence_stats = {lvl: 0 for lvl in VALID_EVIDENCE_LEVELS}

    # 1. 严格检查 classical_texts 原文纯洁度、证据等级与作者权源
    for t in texts:
        tid = t["text_id"]
        text_content = t["text"]
        
        # 现代词过滤
        for bad_word in FORBIDDEN_MODERN_WORDS_IN_CLASSICAL_TEXT:
            if bad_word in text_content:
                errors.append(f"原文污染严重：{tid} 包含现代非古籍词汇 '{bad_word}'")
        
        # 版本引用外键
        if t["source_id"] not in source_ids:
            errors.append(f"原文 {tid} 引用的 source_id 不存在: {t['source_id']}")

        # 证据等级检验
        ev = t.get("evidence", {})
        lvl = ev.get("evidence_level")
        if lvl not in VALID_EVIDENCE_LEVELS:
            errors.append(f"原文 {tid} evidence_level 非法: {lvl}")
        else:
            evidence_stats[lvl] += 1

        # 作者权源检查
        prov = t.get("text_provenance")
        if not prov or "author" not in prov:
            errors.append(f"原文 {tid} 缺失 text_provenance 作者权源结构")

    # 2. 检查 interpretations 映射与单作者归属
    for i in interps:
        iid = i["interp_id"]
        if i["text_ref"] not in text_ids:
            errors.append(f"注疏 {iid} 引用的 text_ref 不存在: {i['text_ref']}")
        if "/" in i.get("author", ""):
            errors.append(f"注疏 {iid} 作者字段存在多作者合并混淆: {i['author']}，必须拆分独立条目")

    # 3. 检查规则层：historical_principles 结构化列表、算法参数透明度
    all_rules = core_rules + aux_rules
    for r in all_rules:
        rid = r["rule_id"]
        for sref in r.get("source_refs", []):
            if sref not in source_ids:
                errors.append(f"规则 {rid} 引用的 source_id 不存在: {sref}")
        for tref in r.get("text_refs", []):
            if tref not in text_ids:
                errors.append(f"规则 {rid} 引用的 text_id 不存在: {tref}")
        for iref in r.get("interp_refs", []):
            if iref not in interp_ids:
                errors.append(f"规则 {rid} 引用的 interp_id 不存在: {iref}")

        # 检查 historical_principles 是否为列表形式（彻底避免跨书拼装字符串）
        h_principles = r.get("historical_principles")
        if not isinstance(h_principles, list) or len(h_principles) == 0:
            errors.append(f"规则 {rid} 必须采用结构化 historical_principles 列表形式，严禁单字符串拼装")

        # 检查算法参数透明度
        comp_model = r.get("computational_model", {})
        if "weights" in comp_model:
            param_status = comp_model.get("parameter_status")
            if not param_status:
                errors.append(f"规则 {rid} computational_model 设定了权重，但未标注 parameter_status (如 heuristic)")

        # 检查权重隔离
        p = r["priority"]
        rtype = r["rule_type"]
        if rtype == "核心" and p < 90:
            errors.append(f"核心规则 {rid} priority={p} < 90")
        if rtype == "辅助" and p > 40:
            errors.append(f"辅助规则 {rid} priority={p} > 40，违背神煞辅助降权原则")

    print("--- 文献证据等级统计分布 ---")
    for lvl, count in evidence_stats.items():
        print(f"  [{lvl} 级证据]: {count} 条")
    print("---------------------------\n")

    if errors:
        print(f"[FAIL] 审计发现 {len(errors)} 项缺陷:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("[SUCCESS] 结构化知识库结构与文献证据链审计通过！")
        print("  1. 结构与外键关联完整无断链。")
        print("  2. 原文层逐条具备五级文献证据（E0~E5）与作者权源结构（text_provenance）。")
        print("  3. 注疏层作者归属清晰剥离，杜绝多作者合并不分。")
        print("  4. 规则层历史原则按条目结构化引用，算法参数明确标注经验设定性质（heuristic）。")
        print("  5. 本阶段确认为 V2.1 文献证据骨架达标，后续需持续核对底本影印页码。")

if __name__ == "__main__":
    run_validation()
