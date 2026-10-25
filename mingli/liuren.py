# -*- coding: utf-8 -*-
"""
MingLi - 正统小六壬速断排盘引擎
严格遵循古传小六壬“月上起日，日上起时”三传推演法：
  1. 月上起初一（初传 / 月落神）：大安起正月，顺数至生月
  2. 日上起子时（中传 / 日落神）：月神起初一，顺数至生日
  3. 时辰定落宫（末传 / 时落神 / 最终断语）：日神起子时，顺数至生时
标准六神序列：大安、留连、速喜、赤口、小吉、空亡
"""

import datetime
from lunar_python import Solar

# 六神标准序列表（0: 大安, 1: 留连, 2: 速喜, 3: 赤口, 4: 小吉, 5: 空亡）
LIU_REN = ["大安", "留连", "速喜", "赤口", "小吉", "空亡"]

# 地支时辰序号映射（子: 1, 丑: 2, ..., 亥: 12）
ZHI_TO_HOUR_NUM = {
    "子": 1, "丑": 2, "寅": 3, "卯": 4,
    "辰": 5, "巳": 6, "午": 7, "未": 8,
    "申": 9, "酉": 10, "戌": 11, "亥": 12
}

# 六神详注与古典诗诀断辞
LIUREN_LORE = {
    "大安": {
        "element": "木",
        "direction": "东方",
        "luck": "大吉",
        "poem": "大安事事昌，求谋在东方，失物去不远，宅舍保平安。",
        "desc": "身不动时，五行属木，为青龙吉星。主安康吉庆、谋事平稳、出行平安。"
    },
    "留连": {
        "element": "水",
        "direction": "北方",
        "luck": "延缓/平",
        "poem": "留连事难成，求谋日未明，官事只宜缓，去者未回程。",
        "desc": "卒未归时，五行属水，为玄武慢神。主纠缠迟滞、时机未至、宜守不宜急。"
    },
    "速喜": {
        "element": "火",
        "direction": "南方",
        "luck": "大吉",
        "poem": "速喜喜来临，求财向南行，失物申未午，逢人路上寻。",
        "desc": "人便至时，五行属火，为朱雀吉曜。主喜信神速、求谋顺遂、即刻见效。"
    },
    "赤口": {
        "element": "金",
        "direction": "西方",
        "luck": "凶/防险",
        "poem": "赤口主口舌，官事且紧防，失物急去找，行人有惊慌。",
        "desc": "官事备时，五行属金，为白虎星君。主口舌是非、争执阻碍、谨慎防备。"
    },
    "小吉": {
        "element": "水/木",
        "direction": "西南",
        "luck": "吉",
        "poem": "小吉最吉昌，路上好商量，阴人来报喜，失物在坤方。",
        "desc": "人来喜时，五行属水木，为六合格局。主贵人相助、商贾顺畅、和合吉利。"
    },
    "空亡": {
        "element": "土",
        "direction": "中央",
        "luck": "凶/落空",
        "poem": "空亡事不祥，阴人多乖张，求财无利益，行人有灾殃。",
        "desc": "音信稀时，五行属土，为勾陈腾蛇。主谋事落空、音讯杳茫、诸事宜缓。"
    }
}


def get_liuren_pan(dt=None, bazi=None):
    """
    计算正统小六壬排盘（月日时三传速断）

    :param dt: datetime 对象（默认为当前北京时间）
    :param bazi: 可选的 BaZiResult 实例（若已有则复用其农历月、日和时支）
    :return: 包含三传（月落神、日落神、时落神）、落宫断语、六神掌诀分布的完整字典
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).replace(tzinfo=None)

    # 提取农历月、日、时支数
    if bazi is not None:
        lunar_month = abs(bazi.lunar_month)
        lunar_day = bazi.lunar_day
        hour_zhi = bazi.time_zhi
        hour_num = ZHI_TO_HOUR_NUM.get(hour_zhi, 1)
    else:
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        lunar_month = abs(lunar.getMonth())
        lunar_day = lunar.getDay()
        time_zhi = lunar.getTimeZhi()
        hour_num = ZHI_TO_HOUR_NUM.get(time_zhi, 1)

    # 1. 初传（月落神）：大安(0)起正月，顺数至生月
    # 例如：1月在 0(大安), 2月在 1(留连)...
    month_idx = (lunar_month - 1) % 6
    month_god = LIU_REN[month_idx]

    # 2. 中传（日落神）：月落神起初一，顺数至生日
    day_idx = (month_idx + lunar_day - 1) % 6
    day_god = LIU_REN[day_idx]

    # 3. 末传（时落神 / 最终断语落宫）：日落神起子时，顺数至生时
    hour_idx = (day_idx + hour_num - 1) % 6
    hour_god = LIU_REN[hour_idx]

    # 局数编号（1~6）
    ju_number = hour_idx + 1

    # 标准掌诀六宫静态排布（1:大安, 2:留连, 3:速喜, 4:赤口, 5:小吉, 6:空亡）
    pan = {i + 1: LIU_REN[i] for i in range(6)}

    # 当前落神之古典意象与断辞
    lore = LIUREN_LORE[hour_god]

    return {
        "局数": ju_number,
        "当前": hour_god,
        "月传": month_god,
        "日传": day_god,
        "时传": hour_god,
        "三传": f"{month_god} ➔ {day_god} ➔ {hour_god}",
        "五行": lore["element"],
        "方位": lore["direction"],
        "吉凶": lore["luck"],
        "诗诀": lore["poem"],
        "解曰": lore["desc"],
        "六宫": pan
    }
