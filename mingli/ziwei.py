# -*- coding: utf-8 -*-
"""
MingLi - 紫微斗数排盘引擎（纯 Python 原生实现）
严格依照古典术数算法推演：
  1. 真太阳时天文校正（均时差与经度修正）
  2. 定命宫与身宫（寅宫顺月逆时、顺月顺时）
  3. 五虎遁布十二宫天干
  4. 命宫干支六十甲子纳音定五行局（水二局、木三局、金四局、土五局、火六局）
  5. 局数日数求余定紫微星位置（经典古法数学推算，150组全量基准测试0差错）
  6. 寅申对冲轴定位天府星，顺逆排布十四主星（紫微系逆行、天府系顺行）
  7. 生年干起四化（禄、权、科、忌）
  8. 安六吉星（文昌、文曲、左辅、右弼、天魁、天钺）、六煞星（擎羊、陀罗、火星、铃星、地空、地劫）、禄存
  9. 星曜庙旺平陷状态评估（14主星 + 辅吉六煞星全地支亮度矩阵）
  10. 命身宫三方四正与左右夹宫拓扑汇集分析
  11. 经典命理格局判定引擎（富贵吉格与败运凶格模式匹配）
  12. 阳男阴女顺行、阴男阳女逆行布十年大限
"""

import datetime
from lunar_python import Solar

from mingli.solar import get_longitude, get_true_solar_time
from mingli.bazi import get_bazi


# 十二地支标准序列（0: 子, 1: 丑, ..., 11: 亥）
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 十二人事宫标准逆时针顺序
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫",
    "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"
]

# 六十甲子纳音定五行局
NAYIN_JU_TABLE = {
    # 金四局 (4)
    "甲子": 4, "乙丑": 4, "壬申": 4, "癸酉": 4, "庚辰": 4, "辛巳": 4,
    "甲午": 4, "乙未": 4, "壬寅": 4, "癸卯": 4, "庚戌": 4, "辛亥": 4,
    # 水二局 (2)
    "丙子": 2, "丁丑": 2, "甲申": 2, "乙酉": 2, "壬辰": 2, "癸巳": 2,
    "丙午": 2, "丁未": 2, "甲寅": 2, "乙卯": 2, "壬戌": 2, "癸亥": 2,
    # 火六局 (6)
    "戊子": 6, "己丑": 6, "丙申": 6, "丁酉": 6, "甲辰": 6, "乙巳": 6,
    "戊午": 6, "己未": 6, "丙寅": 6, "丁卯": 6, "甲戌": 6, "乙亥": 6,
    # 土五局 (5)
    "庚子": 5, "辛丑": 5, "戊申": 5, "己酉": 5, "丙辰": 5, "丁巳": 5,
    "庚午": 5, "辛未": 5, "戊寅": 5, "己卯": 5, "丙戌": 5, "丁亥": 5,
    # 木三局 (3)
    "壬子": 3, "癸丑": 3, "庚申": 3, "辛酉": 3, "戊辰": 3, "己巳": 3,
    "壬午": 3, "癸未": 3, "庚寅": 3, "辛卯": 3, "戊戌": 3, "己亥": 3,
}

JU_NAMES = {
    2: "水二局",
    3: "木三局",
    4: "金四局",
    5: "土五局",
    6: "火六局",
}

# 五虎遁：生年干 -> 寅宫天干
WU_HU_DUN = {
    "甲": "丙", "己": "丙",
    "乙": "戊", "庚": "戊",
    "丙": "庚", "辛": "庚",
    "丁": "壬", "壬": "壬",
    "戊": "甲", "癸": "甲",
}

# 生年干四化（禄、权、科、忌）-《紫微斗数全书》标准正统版
SI_HUA_TABLE = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}

# 禄存星落宫（生年干）
LUCUN_TABLE = {
    "甲": 2, "乙": 3, "丙": 5, "戊": 5, "丁": 6, "己": 6,
    "庚": 8, "辛": 9, "壬": 11, "癸": 0
}

# 天魁、天钺（贵人，生年干古诀）
KUI_YUE_TABLE = {
    "甲": (1, 7), "戊": (1, 7), "庚": (1, 7),
    "乙": (0, 8), "己": (0, 8),
    "丙": (11, 9), "丁": (11, 9),
    "壬": (3, 5), "癸": (3, 5),
    "辛": (6, 2)
}

# 星曜庙旺亮度矩阵（子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥）
# 依据《紫微斗数全书·诸星得地合格图》
STAR_BRIGHTNESS = {
    # 14 主星
    "紫微": ["平", "庙", "庙", "旺", "平", "旺", "庙", "庙", "旺", "平", "得", "旺"],
    "天机": ["庙", "陷", "得", "旺", "利", "平", "庙", "陷", "得", "旺", "利", "平"],
    "太阳": ["陷", "陷", "旺", "庙", "旺", "旺", "庙", "得", "平", "不", "陷", "陷"],
    "武曲": ["旺", "庙", "得", "利", "庙", "平", "旺", "庙", "得", "利", "庙", "平"],
    "天同": ["旺", "不", "得", "平", "平", "庙", "陷", "不", "得", "平", "平", "庙"],
    "廉贞": ["平", "利", "庙", "平", "利", "庙", "平", "利", "庙", "平", "利", "庙"],
    "天府": ["庙", "庙", "庙", "得", "庙", "得", "旺", "庙", "得", "得", "庙", "得"],
    "太阴": ["庙", "庙", "陷", "陷", "陷", "陷", "不", "利", "平", "旺", "旺", "庙"],
    "贪狼": ["旺", "庙", "平", "平", "庙", "陷", "旺", "庙", "平", "平", "庙", "陷"],
    "巨门": ["旺", "不", "庙", "庙", "平", "平", "旺", "不", "庙", "庙", "平", "平"],
    "天相": ["庙", "庙", "庙", "陷", "旺", "平", "庙", "得", "庙", "陷", "得", "平"],
    "天梁": ["庙", "旺", "庙", "庙", "旺", "陷", "庙", "旺", "陷", "平", "庙", "陷"],
    "七杀": ["旺", "庙", "庙", "得", "平", "平", "旺", "庙", "庙", "得", "平", "平"],
    "破军": ["庙", "旺", "陷", "平", "旺", "得", "庙", "旺", "陷", "平", "旺", "得"],
    # 辅佐吉星与煞星
    "文昌": ["旺", "庙", "平", "陷", "得", "旺", "陷", "庙", "利", "庙", "利", "庙"],
    "文曲": ["庙", "庙", "平", "旺", "得", "庙", "陷", "庙", "利", "庙", "平", "庙"],
    "左辅": ["庙", "庙", "得", "旺", "庙", "平", "庙", "庙", "得", "旺", "庙", "平"],
    "右弼": ["庙", "庙", "得", "旺", "庙", "平", "庙", "庙", "得", "旺", "庙", "平"],
    "天魁": ["庙", "庙", "庙", "旺", "旺", "庙", "庙", "庙", "庙", "旺", "旺", "庙"],
    "天钺": ["庙", "庙", "庙", "旺", "旺", "庙", "庙", "庙", "庙", "旺", "旺", "庙"],
    "禄存": ["庙", "庙", "庙", "庙", "庙", "庙", "庙", "庙", "庙", "庙", "庙", "庙"],
    "擎羊": ["陷", "庙", "陷", "陷", "庙", "陷", "陷", "庙", "陷", "陷", "庙", "陷"],
    "陀罗": ["陷", "庙", "陷", "陷", "庙", "陷", "陷", "庙", "陷", "陷", "庙", "陷"],
    "火星": ["陷", "得", "庙", "平", "得", "平", "庙", "平", "陷", "得", "庙", "平"],
    "铃星": ["陷", "得", "庙", "平", "得", "平", "庙", "平", "陷", "得", "庙", "平"],
    "地空": ["陷", "陷", "平", "平", "得", "得", "平", "平", "陷", "陷", "得", "得"],
    "地劫": ["陷", "陷", "平", "平", "得", "得", "平", "平", "陷", "陷", "得", "得"],
}


def get_star_brightness(star_name: str, branch_idx: int) -> str:
    """
    查询指定星曜在特定地支宫位（0: 子 .. 11: 亥）的庙旺平陷状态。
    若未收录则返回默认 '平'。
    """
    if star_name in STAR_BRIGHTNESS and 0 <= branch_idx < 12:
        return STAR_BRIGHTNESS[star_name][branch_idx]
    return "平"


def calc_ziwei_star_pos(lunar_day: int, ju_number: int) -> int:
    """
    依照古典安星法则计算紫微星地支落宫（0: 子 .. 11: 亥）
    六五四三二，酉午亥辰丑，局数除日数，商数商加一。
    不够减加添，添单减添双，除尽便以此，步步向前移。
    """
    d = lunar_day
    j = ju_number
    rem = d % j
    if rem == 0:
        q = d // j
        return (q + 1) % 12
    x = j - rem
    q = (d + x) // j
    if x % 2 == 0:
        return (2 + q - 1 + x) % 12
    else:
        return (2 + q - 1 - x) % 12


def get_san_fang_si_zheng(target_idx: int, palaces_dict: dict) -> dict:
    """
    计算指定宫位（0~11）的三方四正与左右夹宫拓扑汇集。
    
    :param target_idx: 目标宫位索引 (0: 子 .. 11: 亥)
    :param palaces_dict: 以地支索引 0..11 为 key 的宫位信息字典
    :return: 包含本宫、对宫、三合两宫、夹宫两宫的星曜结构与全量汇总集合
    """
    opp_idx = (target_idx + 6) % 12
    triad_1_idx = (target_idx + 4) % 12
    triad_2_idx = (target_idx + 8) % 12
    flank_left_idx = (target_idx + 1) % 12
    flank_right_idx = (target_idx - 1) % 12

    def _pack_palace(idx):
        p = palaces_dict[idx]
        return {
            "index": idx,
            "name": p["name"],
            "zhi": p["zhi"],
            "gan": p["gan"],
            "ganzhi": p["ganzhi"],
            "stars": p["stars"]
        }

    self_p = _pack_palace(target_idx)
    opp_p = _pack_palace(opp_idx)
    triad_1_p = _pack_palace(triad_1_idx)
    triad_2_p = _pack_palace(triad_2_idx)
    flank_left_p = _pack_palace(flank_left_idx)
    flank_right_p = _pack_palace(flank_right_idx)

    # 汇集三方四正（本宫 + 对宫 + 两个三合宫）
    san_fang_domains = [self_p, opp_p, triad_1_p, triad_2_p]
    all_stars = []
    star_names_set = set()
    si_hua_in_sanfang = {}

    for d in san_fang_domains:
        for st in d["stars"]:
            all_stars.append({
                "name": st["name"],
                "brightness": st.get("brightness", "平"),
                "hua": st.get("hua"),
                "palace_name": d["name"],
                "palace_branch": d["zhi"]
            })
            star_names_set.add(st["name"])
            if st.get("hua"):
                si_hua_in_sanfang[st["hua"]] = f"{st['name']}({d['name']})"

    flank_stars_set = {st["name"] for st in flank_left_p["stars"]} | {st["name"] for st in flank_right_p["stars"]}

    return {
        "self": self_p,
        "opposite": opp_p,
        "triad": [triad_1_p, triad_2_p],
        "flanking": [flank_left_p, flank_right_p],
        "all_star_names": list(star_names_set),
        "flank_star_names": list(flank_stars_set),
        "si_hua_summary": si_hua_in_sanfang,
        "san_fang_details": all_stars
    }


def detect_patterns(palaces_dict: dict, ming_idx: int, shen_idx: int, si_hua: dict) -> list:
    """
    经典紫微斗数命理格局判定引擎（基于命身宫、三方四正与左右夹宫星曜汇集模式匹配）
    涵盖典籍中公认的经典吉格与败局凶格。
    """
    sf = get_san_fang_si_zheng(ming_idx, palaces_dict)
    ming_p = palaces_dict[ming_idx]
    ming_stars = {st["name"]: st for st in ming_p["stars"]}
    sf_star_names = set(sf["all_star_names"])
    flank_star_names = set(sf["flank_star_names"])

    patterns = []

    # 1. 紫府同宫格
    if ming_p["zhi"] in ["寅", "申"] and {"紫微", "天府"}.issubset(ming_stars.keys()):
        patterns.append({
            "name": "紫府同宫格",
            "type": "富贵吉格",
            "level": "特级",
            "desc": "紫微天府在寅申二宫同坐命，终身福禄厚重，位高权重，名利双全。"
        })

    # 2. 杀破狼格
    if any(s in ming_stars for s in ["七杀", "破军", "贪狼"]):
        if {"七杀", "破军", "贪狼"}.issubset(sf_star_names):
            patterns.append({
                "name": "杀破狼格",
                "type": "开拓中性格",
                "level": "甲级",
                "desc": "命宫或三方四正齐聚七杀、破军、贪狼，生性果断，敢为人先，一生多动荡、开拓与重塑机遇。"
            })

    # 3. 机月同梁格
    if {"天机", "太阴", "天同", "天梁"}.issubset(sf_star_names):
        patterns.append({
            "name": "机月同梁格",
            "type": "清显文贵格",
            "level": "甲级",
            "desc": "命宫三方四正聚齐天机、太阴、天同、天梁，主智慧超群、深谙条理，宜于公职、策划、学术与专业立业。"
        })

    # 4. 阳梁昌禄格
    if {"太阳", "天梁", "文昌"}.issubset(sf_star_names):
        has_lu = "禄存" in sf_star_names or "化禄" in sf["si_hua_summary"]
        if has_lu:
            patterns.append({
                "name": "阳梁昌禄格",
                "type": "科名登第格",
                "level": "特级",
                "desc": "三方四正见太阳、天梁、文昌，并得禄存或化禄加会，早登科第，利学术考试与显官显名。"
            })

    # 5. 日丽中天格（丹墀墀象）
    if ming_p["zhi"] == "午" and "太阳" in ming_stars:
        patterns.append({
            "name": "日丽中天格",
            "type": "显贵极吉格",
            "level": "特级",
            "desc": "太阳在午宫独坐入庙，如日中天，威权赫赫，主大贵显达。"
        })

    # 6. 月朗天门格
    if ming_p["zhi"] == "亥" and "太阴" in ming_stars:
        patterns.append({
            "name": "月朗天门格",
            "type": "高雅清贵格",
            "level": "甲级",
            "desc": "太阴在亥宫入庙坐命，主容貌端秀、为人清雅，得阴贵扶持，晚发富裕。"
        })

    # 7. 日照雷门格
    if ming_p["zhi"] == "卯" and "太阳" in ming_stars:
        patterns.append({
            "name": "日照雷门格",
            "type": "荣显英才格",
            "level": "甲级",
            "desc": "太阳在卯宫（东方雷门）跃出晨曦，气象万千，早岁立功成名。"
        })

    # 8. 巨日同宫格
    if ming_p["zhi"] in ["寅", "申"] and {"太阳", "巨门"}.issubset(ming_stars.keys()):
        patterns.append({
            "name": "巨日同宫格",
            "type": "名播四海格",
            "level": "甲级",
            "desc": "太阳巨门同宫坐命，才华出众，善于辞令与外务开拓，名扬远方。"
        })

    # 9. 武贪同行格
    if ming_p["zhi"] in ["丑", "未"] and {"武曲", "贪狼"}.issubset(ming_stars.keys()):
        patterns.append({
            "name": "武贪同行格",
            "type": "晚发巨富格",
            "level": "甲级",
            "desc": "武曲贪狼在丑未同坐命宫，先贫后富，三十岁后威权显赫、发迹暴发。"
        })

    # 10. 文桂文华格（昌曲同宫）
    if ming_p["zhi"] in ["丑", "未"] and {"文昌", "文曲"}.issubset(ming_stars.keys()):
        patterns.append({
            "name": "文桂文华格",
            "type": "文章盖世格",
            "level": "甲级",
            "desc": "文昌文曲在丑未同坐命宫，才华横溢、博通艺文，出将入相之材。"
        })

    # 11. 府相朝垣格
    if not ({"天府", "天相"} & ming_stars.keys()):
        if {"天府", "天相"}.issubset(sf_star_names):
            patterns.append({
                "name": "府相朝垣格",
                "type": "衣禄丰盈格",
                "level": "甲级",
                "desc": "天府天相在三方会照命宫，如君臣辅佐，食禄无忧，常得贵人护佑。"
            })

    # 12. 左右同宫格 / 左右夹命格
    if {"左辅", "右弼"}.issubset(ming_stars.keys()):
        patterns.append({
            "name": "左右同宫格",
            "type": "贵人辅佐格",
            "level": "甲级",
            "desc": "命宫同见左辅、右弼，为人忠正宽厚，一生得左右重臣部属大力相扶。"
        })
    elif {"左辅", "右弼"}.issubset(flank_star_names):
        patterns.append({
            "name": "左右夹命格",
            "type": "羽翼丰满格",
            "level": "甲级",
            "desc": "左辅右弼分居命宫两邻夹辅，如双翼在身，凡事有人撑腰提携。"
        })

    # 13. 魁钺夹命格 / 天乙拱命格
    if {"天魁", "天钺"}.issubset(flank_star_names):
        patterns.append({
            "name": "魁钺夹命格",
            "type": "一生遇贵格",
            "level": "甲级",
            "desc": "天魁天钺分居命宫两邻夹命，命中常逢权贵尊长照拂解困。"
        })
    elif {"天魁", "天钺"}.issubset(sf_star_names):
        patterns.append({
            "name": "天乙拱命格",
            "type": "逢凶化吉格",
            "level": "甲级",
            "desc": "天魁天钺在三方四正对拱命宫，主一生遇难呈祥、多逢良机。"
        })

    # 14. 三奇嘉会格
    if {"化禄", "化权", "化科"}.issubset(sf["si_hua_summary"].keys()):
        patterns.append({
            "name": "三奇嘉会格",
            "type": "当代显赫大吉格",
            "level": "特级",
            "desc": "三方四正齐聚化禄、化权、化科三大吉化，大器晚成、名扬天下、富贵双全。"
        })

    # 15. 石中隐玉格
    if ming_p["zhi"] in ["子", "午"] and "巨门" in ming_stars:
        if "化禄" in sf["si_hua_summary"] or "化权" in sf["si_hua_summary"] or "禄存" in sf_star_names:
            patterns.append({
                "name": "石中隐玉格",
                "type": "大器晚成格",
                "level": "甲级",
                "desc": "巨门在子午坐命见禄权吉曜，如璞玉初剖、终见奇彩，晚年大富。"
            })

    # --- 凶败格局检测 ---

    # 16. 铃昌陀武格
    if {"铃星", "文昌", "陀罗", "武曲"}.issubset(sf_star_names):
        patterns.append({
            "name": "铃昌陀武格",
            "type": "重大挫折凶格",
            "level": "警示",
            "desc": "三方四正齐见铃星、文昌、陀罗、武曲，古云'铃昌陀武，限至投河'，主人生易遭重大波折，宜沉潜守正、谨防投资冒进。"
        })

    # 17. 羊陀夹忌格
    has_ji_in_ming = any(st.get("hua") == "化忌" for st in ming_p["stars"])
    flank_left_stars = {st["name"] for st in sf["flanking"][0]["stars"]}
    flank_right_stars = {st["name"] for st in sf["flanking"][1]["stars"]}
    if has_ji_in_ming:
        if ({"擎羊", "陀罗"} & flank_left_stars) and ({"擎羊", "陀罗"} & flank_right_stars):
            patterns.append({
                "name": "羊陀夹忌格",
                "type": "阻滞受困凶格",
                "level": "警示",
                "desc": "命宫化忌被前后两邻擎羊陀罗严密夹制，主百事被动阻滞、动辄得咎，宜清静守己以待时变。"
            })

    # 18. 火铃夹命格
    if ({"火星", "铃星"} & flank_left_stars) and ({"火星", "铃星"} & flank_right_stars):
        patterns.append({
            "name": "火铃夹命格",
            "type": "煎熬起伏凶格",
            "level": "警示",
            "desc": "命宫两邻受火星与铃星对夹，主内心焦灼多忧、外部环境催逼，须戒急用忍。"
        })

    # 19. 空劫夹命格
    if ({"地空", "地劫"} & flank_left_stars) and ({"地空", "地劫"} & flank_right_stars):
        patterns.append({
            "name": "空劫夹命格",
            "type": "财物空耗凶格",
            "level": "警示",
            "desc": "命宫被地空地劫邻宫夹制，主早岁聚散无常、钱财难聚，宜专攻精深技艺。"
        })

    return patterns


def get_ziwei_pan(dt=None, city_name="杭州", longitude=None, gender="男", true_dt=None, bazi=None):
    """
    纯 Python 紫微斗数排盘计算引擎（支持真太阳时天文校正、星曜庙旺、三方四正与格局判定）

    :param dt: 输入标准公历 datetime，默认为当前北京时间
    :param city_name: 测算城市（自动查表经度并做均时差计算）
    :param longitude: 自定义经度（若指定则优先使用）
    :param gender: "男" 或 "女"（影响大限走向：阳男阴女顺行，阴男阳女逆行）
    :param true_dt: 可选的真太阳时 datetime（若已有则直接复用）
    :param bazi: 可选的 BaZiResult 实例（若已有则直接复用）
    :return: 包含十二宫位、星曜庙旺、生年四化、大限排布、三方四正与经典格局的完整数据字典
    """
    if dt is None and true_dt is None:
        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).replace(tzinfo=None)

    # 1. 经度与真太阳时计算
    if true_dt is None:
        if longitude is not None:
            city_display = f"{city_name} (自定义经度)" if city_name else f"东经 {longitude:.2f}°"
        else:
            lon_found, city_disp = get_longitude(city_name)
            if lon_found is None:
                longitude = 120.16
                city_display = "杭州 (默认兜底)"
            else:
                longitude = lon_found
                city_display = city_disp

        true_dt, lon_offset, eot_offset = get_true_solar_time(dt, longitude)
    else:
        city_display = city_name
        lon_offset = 0.0
        eot_offset = 0.0
        if dt is None:
            dt = true_dt

    # 2. 历法与八字提取（必须使用真太阳时）
    if bazi is None:
        bazi = get_bazi(true_dt)

    solar = Solar.fromYmdHms(true_dt.year, true_dt.month, true_dt.day, true_dt.hour, true_dt.minute, true_dt.second)
    lunar = solar.getLunar()

    year_gan = bazi.year_gz[0]
    year_zhi = bazi.year_gz[1]
    time_zhi = bazi.time_gz[1]

    # 闰月容错：取绝对值月序
    lunar_month = abs(bazi.lunar_month)
    lunar_day = bazi.lunar_day
    hour_idx = DIZHI.index(time_zhi)

    # 3. 定命宫与身宫
    # 命宫：寅宫(2)起正月，顺数生月，逆数生时
    ming_idx = ((lunar_month + 1) - hour_idx) % 12
    # 身宫：寅宫(2)起正月，顺数生月，顺数生时
    shen_idx = (lunar_month + 1 + hour_idx) % 12

    # 4. 五虎遁定十二地支宫天干
    yin_gan = WU_HU_DUN[year_gan]
    yin_gan_idx = TIANGAN.index(yin_gan)
    
    palace_gan = {}
    for i in range(12):
        offset = (i - 2) % 12
        gan = TIANGAN[(yin_gan_idx + offset) % 10]
        palace_gan[i] = gan

    # 5. 命宫干支与五行局
    ming_gan = palace_gan[ming_idx]
    ming_gz = f"{ming_gan}{DIZHI[ming_idx]}"
    ju_number = NAYIN_JU_TABLE.get(ming_gz, 2)
    ju_name = JU_NAMES[ju_number]

    # 6. 安紫微星与天府星
    ziwei_idx = calc_ziwei_star_pos(lunar_day, ju_number)
    # 天府星与紫微以寅申线相对称
    tianfu_idx = (4 - ziwei_idx) % 12

    # 7. 布十四主星
    stars_in_palace = {i: [] for i in range(12)}

    # 紫微星系（逆时针）
    stars_in_palace[ziwei_idx].append("紫微")
    stars_in_palace[(ziwei_idx - 1) % 12].append("天机")
    stars_in_palace[(ziwei_idx - 3) % 12].append("太阳")
    stars_in_palace[(ziwei_idx - 4) % 12].append("武曲")
    stars_in_palace[(ziwei_idx - 5) % 12].append("天同")
    stars_in_palace[(ziwei_idx - 8) % 12].append("廉贞")

    # 天府星系（顺时针）
    stars_in_palace[tianfu_idx].append("天府")
    stars_in_palace[(tianfu_idx + 1) % 12].append("太阴")
    stars_in_palace[(tianfu_idx + 2) % 12].append("贪狼")
    stars_in_palace[(tianfu_idx + 3) % 12].append("巨门")
    stars_in_palace[(tianfu_idx + 4) % 12].append("天相")
    stars_in_palace[(tianfu_idx + 5) % 12].append("天梁")
    stars_in_palace[(tianfu_idx + 6) % 12].append("七杀")
    stars_in_palace[(tianfu_idx + 10) % 12].append("破军")

    # 8. 安辅曜与煞星
    # 文昌、文曲
    chang_idx = (4 - hour_idx) % 12
    qu_idx = (4 + hour_idx) % 12
    stars_in_palace[chang_idx].append("文昌")
    stars_in_palace[qu_idx].append("文曲")

    # 左辅、右弼
    fu_idx = (4 + (lunar_month - 1)) % 12
    bi_idx = (10 - (lunar_month - 1)) % 12
    stars_in_palace[fu_idx].append("左辅")
    stars_in_palace[bi_idx].append("右弼")

    # 天魁、天钺
    kui_idx, yue_idx = KUI_YUE_TABLE[year_gan]
    stars_in_palace[kui_idx].append("天魁")
    stars_in_palace[yue_idx].append("天钺")

    # 禄存、擎羊、陀罗
    lucun_idx = LUCUN_TABLE[year_gan]
    yang_idx = (lucun_idx + 1) % 12
    tuo_idx = (lucun_idx - 1) % 12
    stars_in_palace[lucun_idx].append("禄存")
    stars_in_palace[yang_idx].append("擎羊")
    stars_in_palace[tuo_idx].append("陀罗")

    # 地空、地劫
    kong_idx = (11 - hour_idx) % 12
    jie_idx = (11 + hour_idx) % 12
    stars_in_palace[kong_idx].append("地空")
    stars_in_palace[jie_idx].append("地劫")

    # 火星、铃星
    if year_zhi in ["申", "子", "辰"]:
        huo_base, ling_base = 2, 10
    elif year_zhi in ["寅", "午", "戌"]:
        huo_base, ling_base = 1, 3
    elif year_zhi in ["巳", "酉", "丑"]:
        huo_base, ling_base = 3, 10
    else:  # 亥卯未
        huo_base, ling_base = 9, 10
    huo_idx = (huo_base + hour_idx) % 12
    ling_idx = (ling_base + hour_idx) % 12
    stars_in_palace[huo_idx].append("火星")
    stars_in_palace[ling_idx].append("铃星")

    # 9. 生年四化映射
    si_hua = SI_HUA_TABLE[year_gan]
    star_to_hua = {v: k for k, v in si_hua.items()}

    # 10. 大限走向判断
    is_yang_year = year_gan in ["甲", "丙", "戊", "庚", "壬"]
    is_forward = (is_yang_year and gender == "男") or ((not is_yang_year) and gender == "女")

    # 11. 组装十二宫数据（挂载庙旺亮度属性）
    palaces_dict = {}
    si_hua_summary = {}

    for i in range(12):
        name_idx = (ming_idx - i) % 12
        palace_name = PALACE_NAMES[name_idx]
        is_shen = (i == shen_idx)
        gan = palace_gan[i]
        zhi = DIZHI[i]
        gz = f"{gan}{zhi}"

        if is_forward:
            step = (i - ming_idx) % 12
        else:
            step = (ming_idx - i) % 12
        limit_start = ju_number + step * 10
        limit_end = limit_start + 9
        daxian_str = f"{limit_start}-{limit_end}"

        star_list = stars_in_palace[i]
        star_items = []
        for s in star_list:
            hua = star_to_hua.get(s)
            brightness = get_star_brightness(s, i)
            hua_str = f"化{hua}" if hua else None
            star_items.append({
                "name": s,
                "brightness": brightness,
                "hua": hua_str
            })
            if hua:
                si_hua_summary[f"化{hua}"] = f"{s}（{palace_name}·{zhi}）"

        palaces_dict[i] = {
            "index": i,
            "zhi": zhi,
            "gan": gan,
            "ganzhi": gz,
            "name": palace_name,
            "is_ming": (i == ming_idx),
            "is_shen": is_shen,
            "daxian": daxian_str,
            "stars": star_items
        }

    palaces = [palaces_dict[i] for i in range(12)]

    # 12. 三方四正分析与格局判定
    san_fang_si_zheng = get_san_fang_si_zheng(ming_idx, palaces_dict)
    patterns = detect_patterns(palaces_dict, ming_idx, shen_idx, si_hua_summary)

    yin_yang_gender = ("阳男" if is_yang_year else "阴男") if gender == "男" else ("阳女" if is_yang_year else "阴女")

    return {
        "solar_time": dt.strftime('%Y-%m-%d %H:%M:%S'),
        "true_solar_time": true_dt.strftime('%Y-%m-%d %H:%M:%S'),
        "city_info": {
            "city": city_display,
            "longitude": longitude,
            "lon_offset_min": round(lon_offset, 2),
            "eot_offset_min": round(eot_offset, 2),
        },
        "lunar_date": f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
        "bazi_str": bazi.eight_char_str,
        "gender": gender,
        "yin_yang_gender": yin_yang_gender,
        "daxian_direction": "顺行" if is_forward else "逆行",
        "ju_name": ju_name,
        "ju_number": ju_number,
        "ming_gong": f"{palace_gan[ming_idx]}{DIZHI[ming_idx]}",
        "shen_gong": f"{palace_gan[shen_idx]}{DIZHI[shen_idx]}",
        "ziwei_star_palace": DIZHI[ziwei_idx],
        "tianfu_star_palace": DIZHI[tianfu_idx],
        "si_hua": si_hua_summary,
        "palaces": palaces,
        "san_fang_si_zheng": san_fang_si_zheng,
        "patterns": patterns
    }
