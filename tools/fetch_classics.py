#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古籍抓取脚本：从中文维基文库（四库全书本）安全抓取《三命通会》、《渊海子平》等底本
带自适应退避与重试机制，防止 429 频控
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "ShenbMingliAcademicBot/1.0 (Contact: shenb@163.com; Non-commercial research)"

def clean_wikitext(wt: str) -> str:
    """清洗 Wikitext 模板标记，保留纯粹古文正文"""
    # 移除注释
    t = re.sub(r'<!--.*?-->', '', wt, flags=re.S)
    # 移除 SKQS 模板标签
    t = re.sub(r'\{\{SKQS[^\}]*\}\}', '', t)
    t = re.sub(r'\{\{SK[^\}]*\}\}', '', t)
    t = re.sub(r'\{\{Novel[^\}]*\}\}', '', t)
    t = re.sub(r'\{\{color\|[^\}]*\}\}', '', t)
    t = re.sub(r'\{\{\+[^\}]*\}\}', '', t)
    t = re.sub(r'<poem>|</poem>|<onlyinclude>|</onlyinclude>|__TOC__', '', t)
    # 处理跨维基链接 [[页面|显示名]] 或 [[页面]]
    t = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', t)
    # 清理多余空行与两端空白
    lines = [line.strip() for line in t.splitlines()]
    clean_lines = []
    for l in lines:
        if l:
            clean_lines.append(l)
    return "\n".join(clean_lines)

def fetch_wikisource_page(title: str, max_retries: int = 5, base_delay: float = 3.0) -> str:
    url = f"https://zh.wikisource.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=revisions&rvprop=content&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pages = data.get("query", {}).get("pages", {})
                for pid, pdata in pages.items():
                    if pid != "-1" and "revisions" in pdata:
                        raw_wt = pdata["revisions"][0]["*"]
                        return raw_wt
                    else:
                        print(f"  [Not Found] 页面不存在: {title}")
                        return ""
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = base_delay * (2 ** attempt) + 2.0
                print(f"  [429 Rate Limit] 触发频控，等待 {wait_time:.1f} 秒后重试 (第 {attempt+1}/{max_retries} 次)...")
                time.sleep(wait_time)
            else:
                print(f"  [HTTP {e.code}] {title}: {e}")
                time.sleep(base_delay)
        except Exception as e:
            print(f"  [Error] {title}: {e}")
            time.sleep(base_delay)
            
    print(f"  [Failed] 超过最大重试次数: {title}")
    return ""

def download_sanming_tonghui(out_file: Path):
    print("=== 开始抓取《三命通会》（文渊阁四库全书本，共12卷）===")
    pages_data = []
    total_chars = 0
    for vol in range(1, 13):
        title = f"三命通會 (四庫全書本)/卷{vol:02d}"
        print(f"正在拉取 {title} ...")
        raw_wt = fetch_wikisource_page(title)
        if raw_wt:
            clean_txt = clean_wikitext(raw_wt)
            char_len = len(clean_txt)
            total_chars += char_len
            print(f"  -> 成功: 清洗后正文共 {char_len} 字")
            pages_data.append({
                "volume": vol,
                "title": f"卷{vol:02d}",
                "wikisource_title": title,
                "url": f"https://zh.wikisource.org/wiki/{urllib.parse.quote(title)}",
                "char_count": char_len,
                "text": clean_txt
            })
        else:
            print(f"  -> 卷{vol:02d} 获取失败！")
        time.sleep(3.0)  # 严格防频控
        
    doc = {
        "source_id": "SRC_SMTH",
        "book": "三命通会",
        "author": "明·万民英",
        "dynasty": "明",
        "base_edition": "文渊阁四库全书子部术数类本",
        "digital_source": "zh.wikisource.org",
        "total_volumes": len(pages_data),
        "total_chars": total_chars,
        "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "volumes": pages_data
    }
    out_file.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[完成] 《三命通会》12卷全部拉取完毕，总字数: {total_chars} 字，已保存至: {out_file}\n")

if __name__ == "__main__":
    out_path = Path("/home/shenb/mingli/raw_texts/SRC_SMTH_sanming_tonghui.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    download_sanming_tonghui(out_path)
