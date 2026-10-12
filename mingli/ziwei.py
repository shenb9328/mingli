# -*- coding: utf-8 -*-
"""
MingLi - 紫微斗数排盘引擎（纯 Python 实现）
严格依照古典术数算法推演：
  1. 真太阳时天文校正（均时差与经度修正）
  2. 定命宫与身宫（寅宫顺月逆时、顺月顺时）
  3. 五虎遁布十二宫天干
  4. 命宫干支六十甲子纳音定五行局（水二局、木三局、金四局、土五局、火六局）
  5. 局数日数求余定紫微星位置（经典古法数学推算）
  6. 寅申对冲轴定位天府星，顺逆排布十四主星（紫微系逆行、天府系顺行）
  7. 生年干起四化（禄、权、科、忌）
  8. 安六吉星（文昌、文曲、左辅、右弼、天魁、天钺）、六煞星（擎羊、陀罗、火星、铃星、地空、地劫）、禄存
  9. 阳男阴女顺行、阴男阳女逆行布十年大限
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

# 生年干四化（禄、权、科、忌）
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

# 天魁、天钺（贵人，生年干）
KUI_YUE_TABLE = {
    "甲": (1, 7), "戊": (1, 7), "庚": (1, 7),
    "乙": (0, 8), "己": (0, 8),
    "丙": (11, 9), "丁": (11, 9),
    "壬": (3, 5), "癸": (3, 5),
    "辛": (6, 2)
}


def calc_ziwei_star_pos(lunar_day: int, ju_number: int) -> int:
    """
    依照古典安星法则计算紫微星地支落宫（0: 子 .. 11: 亥）
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


def get_ziwei_pan(dt=None, city_name="杭州", longitude=None, gender="男", true_dt=None, bazi=None):
    """
    纯 Python 紫微斗数排盘计算引擎（支持真太阳时天文校正）

    :param dt: 输入标准公历 datetime，默认为当前北京时间
    :param city_name: 测算城市（自动查表经度并做均时差计算）
    :param longitude: 自定义经度（若指定则优先使用）
    :param gender: "男" 或 "女"（影响大限走向：阳男阴女顺行，阴男阳女逆行）
    :param true_dt: 可选的真太阳时 datetime（若已有则直接复用）
    :param bazi: 可选的 BaZiResult 实例（若已有则直接复用）
    :return: 包含十二宫位、十四主星、吉凶星煞、生年四化、大限排布的完整数据字典
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

    lunar_month = bazi.lunar_month
    lunar_day = bazi.lunar_day
    hour_idx = DIZHI.index(time_zhi)
    year_zhi_idx = DIZHI.index(year_zhi)

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
        # 地支 i 相对于 寅宫(2) 的偏移
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

    # 紫微星系（逆时针）：紫微(0)、天机(-1)、太阳(-3)、武曲(-4)、天同(-5)、廉贞(-8)
    stars_in_palace[ziwei_idx].append("紫微")
    stars_in_palace[(ziwei_idx - 1) % 12].append("天机")
    stars_in_palace[(ziwei_idx - 3) % 12].append("太阳")
    stars_in_palace[(ziwei_idx - 4) % 12].append("武曲")
    stars_in_palace[(ziwei_idx - 5) % 12].append("天同")
    stars_in_palace[(ziwei_idx - 8) % 12].append("廉贞")

    # 天府星系（顺时针）：天府(0)、太阴(+1)、贪狼(+2)、巨门(+3)、天相(+4)、天梁(+5)、七杀(+6)、破军(+10)
    stars_in_palace[tianfu_idx].append("天府")
    stars_in_palace[(tianfu_idx + 1) % 12].append("太阴")
    stars_in_palace[(tianfu_idx + 2) % 12].append("贪狼")
    stars_in_palace[(tianfu_idx + 3) % 12].append("巨门")
    stars_in_palace[(tianfu_idx + 4) % 12].append("天相")
    stars_in_palace[(tianfu_idx + 5) % 12].append("天梁")
    stars_in_palace[(tianfu_idx + 6) % 12].append("七杀")
    stars_in_palace[(tianfu_idx + 10) % 12].append("破军")

    # 8. 安辅曜与煞星
    # 文昌（辰宫逆时）、文曲（辰宫顺时）
    chang_idx = (4 - hour_idx) % 12
    qu_idx = (4 + hour_idx) % 12
    stars_in_palace[chang_idx].append("文昌")
    stars_in_palace[qu_idx].append("文曲")

    # 左辅（辰宫顺月）、右弼（戌宫逆月）
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

    # 地空、地劫（亥宫起子时：空逆劫顺）
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
    # 阳干：甲丙戊庚壬；阴干：乙丁己辛癸
    is_yang_year = year_gan in ["甲", "丙", "戊", "庚", "壬"]
    is_forward = (is_yang_year and gender == "男") or ((not is_yang_year) and gender == "女")

    # 11. 组装十二宫数据
    palaces = []
    si_hua_summary = {}

    for i in range(12):
        # 人事宫位：以命宫为 0，逆时针排布
        name_idx = (ming_idx - i) % 12
        palace_name = PALACE_NAMES[name_idx]

        is_shen = (i == shen_idx)
        gan = palace_gan[i]
        zhi = DIZHI[i]
        gz = f"{gan}{zhi}"

        # 大限计算
        if is_forward:
            step = (i - ming_idx) % 12
        else:
            step = (ming_idx - i) % 12
        limit_start = ju_number + step * 10
        limit_end = limit_start + 9
        daxian_str = f"{limit_start}-{limit_end}"

        # 宫内星曜与四化挂载
        star_list = stars_in_palace[i]
        star_items = []
        for s in star_list:
            hua = star_to_hua.get(s)
            if hua:
                star_items.append({"name": s, "hua": f"化{hua}"})
                si_hua_summary[f"化{hua}"] = f"{s}（{palace_name}·{zhi}）"
            else:
                star_items.append({"name": s, "hua": None})

        palaces.append({
            "index": i,
            "zhi": zhi,
            "gan": gan,
            "ganzhi": gz,
            "name": palace_name,
            "is_ming": (i == ming_idx),
            "is_shen": is_shen,
            "daxian": daxian_str,
            "stars": star_items
        })

    # 按地支标准索引排序
    palaces.sort(key=lambda x: x["index"])

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
        "palaces": palaces
    }
