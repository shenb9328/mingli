# -*- coding: utf-8 -*-
"""
MingLi - Markdown 格式渲染器
提供兼容飞书 (Lark)、GitHub、Notion 等富文本环境的排版输出。
"""

import datetime
from mingli.meihua import get_trigrams
from mingli.renderers.utils import pad_string


def render_markdown(data):
    """
    格式化为精美 Markdown 格式（供飞书、GitHub、语雀等直接渲染）
    :param data: calculate_all 计算输出的全量字典
    :return: 渲染后的 Markdown 文本
    """
    lines = []
    city_display = data['city_info']['city']
    longitude = data['city_info']['longitude']
    
    solar_time_str = data['bazi']['solar_time']
    try:
        dt_solar = datetime.datetime.strptime(solar_time_str, "%Y-%m-%d %H:%M:%S")
        title_time = dt_solar.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        title_time = solar_time_str
        
    true_solar_time_str = data['bazi']['true_solar_time']
    try:
        dt_true = datetime.datetime.strptime(true_solar_time_str, "%Y-%m-%d %H:%M:%S")
        true_solar_time = dt_true.strftime("%H:%M")
    except ValueError:
        true_solar_time = true_solar_time_str
        
    lunar_time = data['bazi']['lunar_time']
    city_short = city_display.split(' ')[0]
    
    # 1. Output Header
    lines.append(f"**排盘时刻（{title_time} · 北京时间）地点：{city_short}排盘结果**\n")
    lines.append("---")
    lines.append("\n**基本信息**")
    lines.append(f"- **公历**：{solar_time_str}（北京时间）")
    lines.append(f"- **真太阳时**：{true_solar_time}")
    lines.append(f"- **农历**：{lunar_time}")
    lines.append(f"- **测算方位**：{city_display} 东经 {longitude:.2f}°\n")
    lines.append("---")
    
    # 2. Bazi Table
    lines.append("\n**八字四柱**")
    lines.append("```text")
    lines.append("柱    天干地支")
    lines.append("────  ────────")
    lines.append(f"年柱  {data['bazi']['pillars']['year']}")
    lines.append(f"月柱  {data['bazi']['pillars']['month']}")
    lines.append(f"日柱  {data['bazi']['pillars']['day']}")
    lines.append(f"时柱  {data['bazi']['pillars']['time']}")
    lines.append("```\n")
    lines.append("---")
    
    # 3. Xiao Liuren
    liuren = data['liuren']
    lines.append("\n**小六壬（时空三传速断）**")
    lines.append(f"- **三传路径**：{liuren.get('三传', liuren['当前'])}")
    lines.append(f"- **最终断诀**：【{liuren['当前']}】（五行{liuren.get('五行', '')} · {liuren.get('吉凶', '')} · 喜神{liuren.get('方位', '')}）")
    if "诗诀" in liuren:
        lines.append(f"- **断诗解曰**：*{liuren['诗诀']}* {liuren.get('解曰', '')}\n")
    lines.append("```text")
    lines.append("掌诀宫位  六神名称")
    lines.append("────────  ────────")
    for k in sorted([str(x) for x in liuren['六宫'].keys()], key=int):
        val = liuren['六宫'].get(int(k), liuren['六宫'].get(str(k), ""))
        mark = " (终局落宫)" if val == liuren['当前'] else ""
        lines.append(f"{pad_string('宫 ' + str(k), 10)}{val}{mark}")
    lines.append("```\n")
    lines.append("---")
    
    # 4. Meihua
    mh = data['meihua']
    move_str = ["一", "二", "三", "四", "五", "六"][int(mh['动爻']) - 1]
    lines.append("\n**梅花易数**")
    lines.append(f"- **本卦**：{mh['本卦']}{get_trigrams(mh['本卦'])}")
    lines.append(f"- **互卦**：{mh['互卦']}{get_trigrams(mh['互卦'])}")
    lines.append(f"- **变卦**：{mh['变卦']}{get_trigrams(mh['变卦'])}")
    lines.append(f"- **动爻**：{move_str}爻\n")
    lines.append("---")
    
    # 5. Qimen
    qm = data['qimen']
    lines.append("\n**奇门遁甲**")
    lines.append(f"- **局制**：{qm['ju_str']}")
    lines.append(f"- **值符**：{qm['zhifu']}")
    lines.append(f"- **值使**：{qm['zhishi']}")
    lines.append(f"- **日空**：{'、'.join(qm['day_kong']) if qm['day_kong'] else '无'}")
    lines.append(f"- **时空**：{'、'.join(qm['time_kong']) if qm['time_kong'] else '无'}")
    lines.append(f"- **驿马**：{qm['yima']}\n")
    
    lines.append("```text")
    lines.append("宫位  九星  八神  八门  天干   备注")
    lines.append("────  ────  ────  ────  ─────  ────")
    for p_no in sorted([str(x) for x in qm['palaces'].keys()], key=int):
        p_key = int(p_no) if int(p_no) in qm['palaces'] else p_no
        p_data = qm['palaces'][p_key]
        if str(p_no) == "5" or p_data['msg'] == "-":
            god, star, door = "—", "—", "—"
        else:
            parts = p_data['msg'].split('/')
            god, star, door = parts[0], parts[1], parts[2]
            
        stems = p_data['stems']
        
        remarks = []
        if p_data['kong']:
            remarks.append(p_data['kong'])
        if p_data['status']:
            remarks.append(p_data['status'])
        remarks_str = "、".join(remarks)
        
        col_no = pad_string(str(p_no), 6)
        col_star = pad_string(star, 6)
        col_god = pad_string(god, 6)
        col_door = pad_string(door, 6)
        col_stems = pad_string(stems, 7)
        col_remarks = remarks_str
        lines.append(f"{col_no}{col_star}{col_god}{col_door}{col_stems}{col_remarks}")
    lines.append("```\n")

    # 6. Ziwei Doushu
    if "ziwei" in data:
        zw = data["ziwei"]
        lines.append("---")
        lines.append("\n**紫微斗数**")
        lines.append(f"- **局制**：{zw['ju_name']}（{zw['yin_yang_gender']}，大限{zw['daxian_direction']}）")
        lines.append(f"- **命宫**：{zw['ming_gong']}  |  **身宫**：{zw['shen_gong']}")
        si_hua_str = "、".join([f"{k}【{v}】" for k, v in zw["si_hua"].items()])
        lines.append(f"- **生年四化**：{si_hua_str}")

        if "san_fang_si_zheng" in zw:
            sf = zw["san_fang_si_zheng"]
            opp_str = f"{sf['opposite']['name']}·{sf['opposite']['zhi']}"
            triad_str = "、".join([f"{p['name']}·{p['zhi']}" for p in sf["triad"]])
            flank_str = "、".join([f"{p['name']}·{p['zhi']}" for p in sf["flanking"]])
            lines.append(f"- **命宫三方四正**：对宫【{opp_str}】 | 三合【{triad_str}】 | 夹宫【{flank_str}】")

        if "patterns" in zw and zw["patterns"]:
            pt_lines = []
            for pt in zw["patterns"]:
                pt_lines.append(f"  * **【{pt['name']}】**（{pt['type']} · {pt['level']}）：{pt['desc']}")
            lines.append("- **命局经典格局**：\n" + "\n".join(pt_lines))

        lines.append("\n```text")
        lines.append("干支  人事宫   身宫  大限     星曜分布（含庙旺与生年四化）")
        lines.append("────  ───────  ────  ───────  ────────────────────────────────────")
        for p in zw["palaces"]:
            col_gz = pad_string(p["ganzhi"], 6)
            col_name = pad_string(p["name"], 9)
            col_shen = pad_string("身宫" if p["is_shen"] else "—", 6)
            col_daxian = pad_string(p["daxian"], 9)
            star_strs = []
            for s in p["stars"]:
                bright = s.get("brightness")
                b_str = f"[{bright}]" if bright else ""
                if s.get("hua"):
                    b_str = f"[{bright}·{s['hua']}]" if bright else f"[{s['hua']}]"
                star_strs.append(f"{s['name']}{b_str}")
            col_stars = " ".join(star_strs) if star_strs else "—"
            lines.append(f"{col_gz}{col_name}{col_shen}{col_daxian}{col_stars}")
        lines.append("```")

    return "\n".join(lines)
