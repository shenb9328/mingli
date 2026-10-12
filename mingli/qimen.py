# -*- coding: utf-8 -*-
"""
MingLi - 时家奇门遁甲排盘模块（转盘拆补法）
严格推演拆补法定局、阴阳九局、九星随时干、八门随时支、八神随大值符、天盘地盘、门迫、空亡与驿马星。
"""

from lunar_python import Solar

JIAZI = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]

EARTH_STEM_ORDER = {
    "阳遁": ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"],
    "阴遁": ["戊", "乙", "丙", "丁", "癸", "壬", "辛", "庚", "己"],
}

ROTATION_RING = [1, 8, 3, 4, 9, 2, 7, 6]
STAR_RING = ["天蓬", "天任", "天冲", "天辅", "天英", "天芮", "天柱", "天心"]
DOOR_RING = ["休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
GOD_RING_YANG = ["值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
GOD_RING_YIN = ["值符", "九天", "九地", "玄武", "白虎", "六合", "太阴", "螣蛇"]

XUNSHOU_TO_HIDDEN_YI = {
    "甲子": "戊", "甲戌": "己", "甲申": "庚", "甲午": "辛", "甲辰": "壬", "甲寅": "癸",
}

BRANCH_TO_PALACE = {
    "子": 1, "丑": 8, "寅": 8, "卯": 3, "辰": 4, "巳": 4, "午": 9, "未": 2, "申": 2, "酉": 7, "戌": 6, "亥": 6,
}

YIMA_TABLE = {
    "申": "寅", "子": "寅", "辰": "寅",
    "寅": "申", "午": "申", "戌": "申",
    "巳": "亥", "酉": "亥", "丑": "亥",
    "亥": "巳", "卯": "巳", "未": "巳"
}

PALACE_INFO = {
    1: {"name": "坎一宫"}, 2: {"name": "坤二宫"}, 3: {"name": "震三宫"},
    4: {"name": "巽四宫"}, 5: {"name": "中五宫"}, 6: {"name": "乾六宫"},
    7: {"name": "兑七宫"}, 8: {"name": "艮八宫"}, 9: {"name": "离九宫"},
}

DOOR_ELEMENT = {"休门": "水", "生门": "土", "伤门": "木", "杜门": "木", "景门": "火", "死门": "土", "惊门": "金", "开门": "金"}
PALACE_ELEMENT = {1: "水", 2: "土", 3: "木", 4: "木", 6: "金", 7: "金", 8: "土", 9: "火"}

JU_TABLE = {
    "冬至": {"上元": 1, "中元": 7, "下元": 4}, "小寒": {"上元": 2, "中元": 8, "下元": 5},
    "大寒": {"上元": 3, "中元": 9, "下元": 6}, "立春": {"上元": 8, "中元": 5, "下元": 2},
    "雨水": {"上元": 9, "中元": 6, "下元": 3}, "惊蛰": {"上元": 1, "中元": 7, "下元": 4},
    "春分": {"上元": 3, "中元": 9, "下元": 6}, "清明": {"上元": 4, "中元": 1, "下元": 7},
    "谷雨": {"上元": 5, "中元": 2, "下元": 8}, "立夏": {"上元": 4, "中元": 1, "下元": 7}, 
    "小满": {"上元": 5, "中元": 2, "下元": 8}, "芒种": {"上元": 6, "中元": 3, "下元": 9}, 
    "夏至": {"上元": 9, "中元": 3, "下元": 6}, "小暑": {"上元": 8, "中元": 2, "下元": 5}, 
    "大暑": {"上元": 7, "中元": 1, "下元": 4}, "立秋": {"上元": 2, "中元": 5, "下元": 8}, 
    "处暑": {"上元": 1, "中元": 4, "下元": 7}, "白露": {"上元": 9, "中元": 6, "下元": 3}, 
    "秋分": {"上元": 7, "中元": 1, "下元": 4}, "寒露": {"上元": 6, "中元": 9, "下元": 3},
    "霜降": {"上元": 5, "中元": 8, "下元": 2}, "立冬": {"上元": 6, "中元": 9, "下元": 3},
    "小雪": {"上元": 5, "中元": 8, "下元": 2}, "大雪": {"上元": 4, "中元": 7, "下元": 1},
}


def rotate_to_start(seq, start):
    idx = seq.index(start)
    return seq[idx:] + seq[:idx]


def get_xun_and_kong(ganzhi):
    idx = JIAZI.index(ganzhi)
    xun_idx = (idx // 10) * 10
    xunshou = JIAZI[xun_idx]
    stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    curr_stem, curr_branch = ganzhi[0], ganzhi[1]
    s_idx = stems.index(curr_stem)
    b_idx = branches.index(curr_branch)
    rem = 10 - s_idx
    kong1 = branches[(b_idx + rem) % 12]
    kong2 = branches[(b_idx + rem + 1) % 12]
    return xunshou, [kong1, kong2]


def is_門迫(door, palace_no):
    if palace_no == 5 or not door:
        return False
    d_el = DOOR_ELEMENT.get(door)
    p_el = PALACE_ELEMENT.get(palace_no)
    if d_el == "木" and p_el == "土": return True
    if d_el == "土" and p_el == "水": return True
    if d_el == "水" and p_el == "火": return True
    if d_el == "火" and p_el == "金": return True
    if d_el == "金" and p_el == "木": return True
    return False


def get_qimen_pan(true_dt, bazi):
    """
    根据真太阳时和八字计算时家奇门遁甲盘
    :param true_dt: 真太阳时 datetime 对象
    :param bazi: BaZiResult 实例
    :return: 包含局数、值符、值使、空亡、驿马、九宫格局数据的字典
    """
    year_gz, month_gz, day_gz, time_gz = bazi.year_gz, bazi.month_gz, bazi.day_gz, bazi.time_gz

    solar = Solar.fromYmdHms(true_dt.year, true_dt.month, true_dt.day, true_dt.hour, true_dt.minute, true_dt.second)
    lunar = solar.getLunar()
    current_jie_name = lunar.getPrevJieQi(False).getName()

    day_idx = JIAZI.index(day_gz)
    yuan = ["上元", "中元", "下元"][(day_idx // 5) % 3]

    YANG_TERMS = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种"]
    dun_type = "阳遁" if current_jie_name in YANG_TERMS else "阴遁"

    try:
        ju_number = JU_TABLE[current_jie_name][yuan]
    except KeyError:
        ju_number = 1

    num_chars = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
    ju_str = f"{dun_type}{num_chars[ju_number - 1]}局"

    day_xun, day_kong = get_xun_and_kong(day_gz)
    time_xun, time_kong = get_xun_and_kong(time_gz)

    day_kong_palaces = sorted(list({BRANCH_TO_PALACE[b] for b in day_kong}))
    time_kong_palaces = sorted(list({BRANCH_TO_PALACE[b] for b in time_kong}))

    palaces_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    rotated_p = rotate_to_start(palaces_list, ju_number)
    stems_order = EARTH_STEM_ORDER[dun_type]
    earth_plate = dict(zip(rotated_p, stems_order))

    BRANCH_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    hidden_yi = XUNSHOU_TO_HIDDEN_YI[time_xun]
    time_gan = time_gz[0]
    time_branch = time_gz[1]
    visible_time_gan = hidden_yi if time_gan == "甲" else time_gan

    def find_palace_by_stem(stem):
        for p, s in earth_plate.items():
            if s == stem:
                return 2 if p == 5 else p
        return 2

    xunshou_palace = find_palace_by_stem(hidden_yi)
    time_palace = find_palace_by_stem(visible_time_gan)

    # 1. 九星排盘（值符随时干）
    zhifu_star = STAR_RING[ROTATION_RING.index(xunshou_palace)]
    star_palace_order = rotate_to_start(ROTATION_RING, time_palace)
    star_order = rotate_to_start(STAR_RING, zhifu_star)
    star_map = dict(zip(star_palace_order, star_order))

    # 2. 八神排盘（小值符随大值符）
    if dun_type == "阳遁":
        god_palace_order = rotate_to_start(ROTATION_RING, time_palace)
        god_order = GOD_RING_YANG
    else:
        reverse_ring = list(reversed(ROTATION_RING))
        god_palace_order = rotate_to_start(reverse_ring, time_palace)
        god_order = GOD_RING_YIN
    god_map = dict(zip(god_palace_order, god_order))

    # 3. 天盘三奇六仪（九星携干转）
    sky_map = {}
    for p in ROTATION_RING:
        star_here = star_map[p]
        orig_palace = ROTATION_RING[STAR_RING.index(star_here)]
        sky_map[p] = earth_plate[orig_palace]

    # 4. 八门排盘（值使随时支）
    zhishi_door = DOOR_RING[ROTATION_RING.index(xunshou_palace)]
    xun_branch = time_xun[1]
    b_steps = (BRANCH_LIST.index(time_branch) - BRANCH_LIST.index(xun_branch)) % 12

    if dun_type == "阳遁":
        fly_palace = (xunshou_palace - 1 + b_steps) % 9 + 1
    else:
        fly_palace = (xunshou_palace - 1 - b_steps) % 9 + 1

    zhishi_palace = 2 if fly_palace == 5 else fly_palace

    door_palace_order = rotate_to_start(ROTATION_RING, zhishi_palace)
    door_order = rotate_to_start(DOOR_RING, zhishi_door)
    door_map = dict(zip(door_palace_order, door_order))

    yima_branch = YIMA_TABLE[time_branch]
    yima_palace = BRANCH_TO_PALACE[yima_branch]

    palaces_output = {}
    for p_no in range(1, 10):
        kong_type = ""
        if p_no in day_kong_palaces and p_no in time_kong_palaces:
            kong_type = "共空"
        elif p_no in day_kong_palaces:
            kong_type = "日空"
        elif p_no in time_kong_palaces:
            kong_type = "时空"

        other_status = []
        if p_no == yima_palace:
            other_status.append("驿马")

        door = None if p_no == 5 else door_map.get(p_no)
        star = "天禽" if p_no == 5 else star_map.get(p_no)
        god = None if p_no == 5 else god_map.get(p_no)

        if p_no == time_palace and star_map.get(p_no) == "天芮":
            star = "天禽"

        if is_門迫(door, p_no):
            other_status.append("迫")

        status_str = "、".join(other_status) if other_status else ""

        earth_stem = earth_plate.get(p_no, "")
        if p_no == 5:
            sky_stem = "-"
            m_s_g = "-"
            stems_display = f"-/{earth_stem}"
        else:
            sky_stem = sky_map.get(p_no, "")
            m_s_g = f"{god}/{star}/{door}"
            stems_display = f"{sky_stem}/{earth_stem}"

        palaces_output[p_no] = {
            "msg": m_s_g,
            "stems": stems_display,
            "kong": kong_type,
            "status": status_str
        }

    return {
        "ju_str": ju_str,
        "zhifu": f"{time_xun}{hidden_yi}落{PALACE_INFO[time_palace]['name']}",
        "zhishi": f"{zhishi_door}落{PALACE_INFO[zhishi_palace]['name']}",
        "day_kong": day_kong,
        "time_kong": time_kong,
        "yima": yima_branch,
        "palaces": palaces_output
    }
