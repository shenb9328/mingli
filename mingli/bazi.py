# -*- coding: utf-8 -*-
"""
MingLi - 八字基础排盘模块
提供四柱干支、地支藏干、农历与节气换算。
"""

import datetime
from lunar_python import Solar, Lunar


class BaZiResult:
    """
    八字结构化结果
    """
    def __init__(self):
        self.solar_time = None
        self.lunar_time = None
        self.lunar_month = 1
        self.lunar_day = 1

        self.year_gz = ""
        self.month_gz = ""
        self.day_gz = ""
        self.time_gz = ""

        self.year_zhi = ""
        self.month_zhi = ""
        self.day_zhi = ""
        self.time_zhi = ""

        self.eight_char_str = ""

    def to_dict(self):
        return {
            "solar_time": self.solar_time,
            "lunar_time": self.lunar_time,
            "lunar_month": self.lunar_month,
            "lunar_day": self.lunar_day,
            "eight_char_str": self.eight_char_str,
            "pillars": {
                "year": self.year_gz,
                "month": self.month_gz,
                "day": self.day_gz,
                "time": self.time_gz
            }
        }


def get_bazi(dt=None, tz_offset=8):
    """
    输入：datetime
    输出：BaZiResult
    """
    tz = datetime.timezone(datetime.timedelta(hours=tz_offset))

    if dt is None:
        dt = datetime.datetime.now(tz)
    else:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        else:
            dt = dt.astimezone(tz)

    # 公历 -> Solar
    solar = Solar.fromYmdHms(
        dt.year, dt.month, dt.day,
        dt.hour, dt.minute, dt.second
    )

    lunar = solar.getLunar()
    eight_char = lunar.getEightChar()

    result = BaZiResult()

    result.solar_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    result.lunar_time = f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
    result.lunar_month = abs(lunar.getMonth())
    result.lunar_day = lunar.getDay()

    result.year_gz = eight_char.getYear()
    result.month_gz = eight_char.getMonth()
    result.day_gz = eight_char.getDay()
    result.time_gz = eight_char.getTime()

    result.year_zhi = lunar.getYearZhi()
    result.month_zhi = lunar.getMonthZhi()
    result.day_zhi = lunar.getDayZhi()
    result.time_zhi = lunar.getTimeZhi()

    result.eight_char_str = f"{result.year_gz} {result.month_gz} {result.day_gz} {result.time_gz}"

    return result
