# -*- coding: utf-8 -*-
"""
MingLi - 终端 ANSI 格式渲染器
提供宽字符对齐的经典洛书九宫格与终端表格美化输出。
"""

from mingli.qimen import PALACE_INFO
from mingli.renderers.utils import format_palace_block, pad_string


def render_terminal(data):
    """
    格式化为终端美化文本与经典洛书九宫格
    :param data: calculate_all 计算输出的全量字典
    :return: 渲染后的终端字符串
    """
    lines = []
    lines.append("\n" + "=" * 66)
    lines.append("                      术数综合排盘系统")
    lines.append("=" * 66)

    ci = data["city_info"]
    bz = data["bazi"]
    lines.append("\n[ 核心时间与八字 ]")
    lines.append(f" 公历北京时间: {bz['solar_time']}")
    lines.append(f" 测算城市方位: {ci['city']} (东经 {ci['longitude']:.2f}°)")
    lines.append(f" 时差修正数据: 经度差修正({ci['lon_offset_min']:+.2f}分钟) | 均时差修正({ci['eot_offset_min']:+.2f}分钟) | 总修正({ci['total_offset_min']:+.2f}分钟)")
    lines.append(f" 当地真太阳时: {bz['true_solar_time']}")
    lines.append(f" 农历时间: {bz['lunar_time']}")
    lines.append(f" 四柱八字: {bz['eight_char_str']}")
    p = bz['pillars']
    lines.append(f" 拆解四柱: 年柱({p['year']})  月柱({p['month']})  日柱({p['day']})  时柱({p['time']})")
    lines.append("-" * 66)

    lr = data["liuren"]
    lines.append("[ 小六壬时空三传速断 ]")
    san_chuan = lr.get("三传", f"{lr.get('月传')} ➔ {lr.get('日传')} ➔ {lr.get('时传')}")
    lines.append(f" 三传路径: {san_chuan}  |  最终落宫: 【{lr['当前']}】 ({lr.get('吉凶', '')})")
    if "诗诀" in lr:
        lines.append(f" 诗诀解曰: {lr['诗诀']} ({lr['解曰']})")
    lr_宫位串 = "  ".join([f"宫{k}({v})" for k, v in lr["六宫"].items()])
    lines.append(f" 掌诀六宫: {lr_宫位串}")
    lines.append("-" * 66)

    mh = data["meihua"]
    lines.append("[ 梅花易数排盘 ]")
    lines.append(f" 本卦: {mh['本卦']}   |   互卦: {mh['互卦']}   |   变卦: {mh['变卦']}   |   动爻: {mh['动爻']}爻动")
    lines.append("-" * 66)

    qm = data["qimen"]
    lines.append("[ 奇门遁甲盘局 ]")
    lines.append(f" 节气定局: {qm['ju_str']} | 值符: {qm['zhifu']} | 值使: {qm['zhishi']}")
    day_kong_str = "-".join(qm['day_kong']) if qm['day_kong'] else "无"
    time_kong_str = "-".join(qm['time_kong']) if qm['time_kong'] else "无"
    lines.append(f" 空亡方位: 日空({day_kong_str}) 时空({time_kong_str}) | 驿马星: {qm['yima']}方\n")

    # 经典洛书九宫格
    rows_palaces = [
        [4, 9, 2],
        [3, 5, 7],
        [8, 1, 6]
    ]
    border = "+" + "--------------------+" * 3
    lines.append(border)
    for row in rows_palaces:
        p1 = format_palace_block(row[0], PALACE_INFO[row[0]]["name"], qm['palaces'][row[0]])
        p2 = format_palace_block(row[1], PALACE_INFO[row[1]]["name"], qm['palaces'][row[1]])
        p3 = format_palace_block(row[2], PALACE_INFO[row[2]]["name"], qm['palaces'][row[2]])
        for i in range(4):
            s1 = pad_string(p1[i], 18)
            s2 = pad_string(p2[i], 18)
            s3 = pad_string(p3[i], 18)
            lines.append(f"| {s1} | {s2} | {s3} |")
    lines.append(border)

    if "ziwei" in data:
        zw = data["ziwei"]
        lines.append("\n" + "-" * 66)
        lines.append("[ 紫微斗数排盘 ]")
        lines.append(f" 局制命身: {zw['ju_name']} ({zw['yin_yang_gender']}·{zw['daxian_direction']}) | 命宫【{zw['ming_gong']}】 身宫【{zw['shen_gong']}】")
        si_hua_items = [f"{k}: {v}" for k, v in zw["si_hua"].items()]
        lines.append(f" 生年四化: {' | '.join(si_hua_items)}")
        
        # 命宫三方四正
        if "san_fang_si_zheng" in zw:
            sf = zw["san_fang_si_zheng"]
            opp_str = f"{sf['opposite']['name']}·{sf['opposite']['zhi']}"
            triad_str = "、".join([f"{p['name']}·{p['zhi']}" for p in sf["triad"]])
            flank_str = "、".join([f"{p['name']}·{p['zhi']}" for p in sf["flanking"]])
            lines.append(f" 命宫拓扑: 对宫【{opp_str}】 | 三合【{triad_str}】 | 夹宫【{flank_str}】")
        
        # 经典格局判定
        if "patterns" in zw and zw["patterns"]:
            pt_strs = [f"【{p['name']}】({p['type']})" for p in zw["patterns"]]
            lines.append(f" 命局格局: {' '.join(pt_strs)}")

        lines.append(" 十二宫分布:")
        for p in zw["palaces"]:
            star_strs = []
            for s in p["stars"]:
                bright = s.get("brightness")
                b_str = f"[{bright}]" if bright else ""
                if s.get("hua"):
                    b_str = f"[{bright}·{s['hua']}]" if bright else f"[{s['hua']}]"
                star_strs.append(f"{s['name']}{b_str}")

            star_str = " ".join(star_strs) if star_strs else "—"
            shen_mark = " (身宫)" if p["is_shen"] else "       "
            lines.append(f"   {p['ganzhi']} · {p['name']}{shen_mark} [大限 {pad_string(p['daxian'], 7)}] : {star_str}")

    lines.append("\n" + "=" * 66)
    return "\n".join(lines)
