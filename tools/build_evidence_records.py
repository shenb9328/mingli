import json
from pathlib import Path
import re
import opencc

t2s = opencc.OpenCC("t2s")

def norm(s):
    if not s:
        return ""
    s = t2s.convert(s)
    return re.sub(r"[\s\n\r\t，。、；：！？“”（）《》【】…—\-\.·’‘\'\"]", "", s)

clean_files = {
    p.name: norm(p.read_text(encoding="utf-8"))
    for p in Path("clean_texts").glob("*.txt")
}

all_clean = "".join(clean_files.values())

texts = json.load(open("data/classical_texts.json"))
existing_evidence = json.load(open("data/evidence_records.json"))
ev_by_ref = {e["text_ref"]: e for e in existing_evidence}

SOURCE_FALLBACKS = {
    "SRC_SMTH": "https://ctext.org/wiki.pl?if=gb&res=444061",
    "SRC_YHZP": "https://ctext.org/wiki.pl?if=gb&res=629471",
    "SRC_DTS": "https://zh.wikisource.org/zh-hans/滴天髓",
    "SRC_DTS_CW": "https://zh.wikisource.org/zh-hant/滴天髓闡微",
    "SRC_DTS_BJ": "https://ctext.org/wiki.pl?if=gb&res=573193",
    "SRC_QTBG": "https://ctext.org/wiki.pl?if=gb&res=307399",
    "SRC_ZPZQ": "https://shixingji.club/library/zipingzhenquan",
    "SRC_SFTK": "https://www.chinese-classics.org/read/shushu/mingli/shen-feng-tong-kao/001",
}

all_evidence = []
for t in texts:
    tid = t.get("text_id")
    sid = t.get("source_id")
    ev = t.get("evidence", {})
    lvl = ev.get("evidence_level", "E2")

    n_txt = norm(t.get("text", ""))
    in_clean = (n_txt in all_clean) or (len(n_txt) >= 8 and n_txt[:8] in all_clean)

    if tid in ev_by_ref:
        rec = ev_by_ref[tid]
        if not rec.get("references"):
            rec["references"] = [SOURCE_FALLBACKS.get(sid, "https://ctext.org/zh")]
        all_evidence.append(rec)
        continue

    refs = []
    if ev.get("digital_refs"):
        refs.extend(ev["digital_refs"])
    elif ev.get("digital_ref"):
        refs.append(ev["digital_ref"])
    else:
        refs.append(SOURCE_FALLBACKS.get(sid, "https://ctext.org/zh"))

    if ev.get("scan_ref"):
        refs.append("scan:" + ev["scan_ref"])

    clean_tid = tid.replace("TXT_", "")
    ev_id = "EVID_" + clean_tid

    rec = {
        "evidence_id": ev_id,
        "text_ref": tid,
        "level": lvl,
        "status": "substantiated_in_clean_corpus" if in_clean else "unsubstantiated_in_clean_corpus_pending_edition",
        "references": refs,
        "scan_verified": bool(ev.get("scan_verified", False)),
    }
    all_evidence.append(rec)

print("Generated evidence_records count:", len(all_evidence))
counts = {}
for e in all_evidence:
    counts[e["level"]] = counts.get(e["level"], 0) + 1
print("Distribution by level:", counts)
with open("data/evidence_records.json", "w", encoding="utf-8") as f:
    json.dump(all_evidence, f, ensure_ascii=False, indent=2)
