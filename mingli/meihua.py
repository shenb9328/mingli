# -*- coding: utf-8 -*-
"""
MingLi - 梅花易数起卦与排盘模块
提供先天卦象计算，推算本卦、互卦、变卦及动爻体用生克。
"""

import datetime
from lunar_python import Solar

ZHI_NUM = {
    "子": 1, "丑": 2, "寅": 3, "卯": 4,
    "辰": 5, "巳": 6, "午": 7, "未": 8,
    "申": 9, "酉": 10, "戌": 11, "亥": 12
}

GUA = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤"
}

GUA_ATTR = {
    1: "天", 2: "泽", 3: "火", 4: "雷",
    5: "风", 6: "水", 7: "山", 8: "地"
}

GUA_LINES = {
    1: (1, 1, 1), 2: (1, 1, 0), 3: (1, 0, 1), 4: (1, 0, 0),
    5: (0, 1, 1), 6: (0, 1, 0), 7: (0, 0, 1), 8: (0, 0, 0)
}

LINES_TO_GUA = {v: k for k, v in GUA_LINES.items()}

HEXAGRAM_NAME = {
    (1, 1): "乾为天", (1, 2): "天泽履", (1, 3): "天火同人", (1, 4): "天雷无妄",
    (1, 5): "天风姤", (1, 6): "天水讼", (1, 7): "天山遁", (1, 8): "天地否",
    (2, 1): "泽天夬", (2, 2): "兑为泽", (2, 3): "泽火革", (2, 4): "泽雷随",
    (2, 5): "泽风大过", (2, 6): "泽水困", (2, 7): "泽山咸", (2, 8): "泽地萃",
    (3, 1): "火天大有", (3, 2): "火泽睽", (3, 3): "离为火", (3, 4): "火雷噬嗑",
    (3, 5): "火风鼎", (3, 6): "火水未济", (3, 7): "火山旅", (3, 8): "火地晋",
    (4, 1): "雷天大壮", (4, 2): "雷泽归妹", (4, 3): "雷火丰", (4, 4): "震为雷",
    (4, 5): "雷风恒", (4, 6): "雷水解", (4, 7): "雷山小过", (4, 8): "雷地豫",
    (5, 1): "风天小畜", (5, 2): "风泽中孚", (5, 3): "风火家人", (5, 4): "风雷益",
    (5, 5): "巽为风", (5, 6): "风水涣", (5, 7): "风山渐", (5, 8): "风地观",
    (6, 1): "水天需", (6, 2): "水泽节", (6, 3): "水火既济", (6, 4): "水雷屯",
    (6, 5): "水风井", (6, 6): "坎为水", (6, 7): "水山蹇", (6, 8): "水地比",
    (7, 1): "山天大畜", (7, 2): "山泽损", (7, 3): "山火贲", (7, 4): "山雷颐",
    (7, 5): "山风蛊", (7, 6): "山水蒙", (7, 7): "艮为山", (7, 8): "山地剥",
    (8, 1): "地天泰", (8, 2): "地泽临", (8, 3): "地火明夷", (8, 4): "地雷复",
    (8, 5): "地风升", (8, 6): "地水师", (8, 7): "地山谦", (8, 8): "坤为地"
}


def get_trigrams(gua_name):
    """
    根据六十四卦名获取其上下单卦名说明，如：（上巽下坎）
    """
    for (upper, lower), name in HEXAGRAM_NAME.items():
        if name == gua_name:
            return f"（上{GUA[upper]}下{GUA[lower]}）"
    return ""


class MeiHuaInput:
    """
    梅花易数输入参数封装
    """
    def __init__(self, year_zhi, month, day, hour_zhi):
        self.year_zhi = year_zhi   
        self.month = month         
        self.day = day             
        self.hour_zhi = hour_zhi   


def _calc_gua(mh: MeiHuaInput):
    y = ZHI_NUM[mh.year_zhi]
    h = ZHI_NUM[mh.hour_zhi]

    base = mh.month + mh.day + y

    upper = base % 8 or 8
    lower = (base + h) % 8 or 8
    move = (base + h) % 6 or 6

    return upper, lower, move


def _build_lines(upper, lower):
    return GUA_LINES[lower] + GUA_LINES[upper]


def _change(lines, move):
    new = list(lines)
    new[move - 1] = 1 - new[move - 1]
    return tuple(new)


def _mutual(lines):
    return (
        lines[1], lines[2], lines[3],
        lines[2], lines[3], lines[4]
    )


def _to_name(upper, lower):
    return HEXAGRAM_NAME[(upper, lower)]


def get_meihua_pan(dt=None, input_obj=None):
    """
    计算梅花易数起卦排盘
    :param dt: datetime 对象
    :param input_obj: 可选的 MeiHuaInput 实例
    :return: 包含本卦、互卦、变卦、动爻、上下卦的字典
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).replace(tzinfo=None)

    if input_obj is None:
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        input_obj = MeiHuaInput(
            year_zhi=lunar.getYearZhi(),   
            month=abs(lunar.getMonth()),
            day=lunar.getDay(),
            hour_zhi=lunar.getTimeZhi()
        )

    upper, lower, move = _calc_gua(input_obj)

    orig = _build_lines(upper, lower)
    chg = _change(orig, move)
    mut = _mutual(orig)

    mut_upper = LINES_TO_GUA[mut[3:6]]
    mut_lower = LINES_TO_GUA[mut[0:3]]

    chg_upper = LINES_TO_GUA[chg[3:6]]
    chg_lower = LINES_TO_GUA[chg[0:3]]

    orig_name = _to_name(upper, lower)
    mut_name = _to_name(mut_upper, mut_lower)
    chg_name = _to_name(chg_upper, chg_lower)

    return {
        "本卦": orig_name,
        "互卦": mut_name,
        "变卦": chg_name,
        "动爻": move,
        "上卦": GUA[upper],
        "下卦": GUA[lower]
    }
