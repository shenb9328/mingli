# -*- coding: utf-8 -*-
"""
MingLi - 小六壬速断模块
提供月日时三传与六宫分布速断（大安、留连、速喜、赤口、小吉、空亡）。
"""

import datetime

LIU_REN = ["大安", "留连", "速喜", "赤口", "小吉", "空亡"]


def get_liuren_pan(dt=None):
    """
    计算小六壬排盘
    :param dt: datetime 对象（如为空则使用当前北京时间）
    :return: 包含局数、当前落宫、六宫分布的字典
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).replace(tzinfo=None)

    base = (dt.year + dt.month + dt.day + dt.hour) % 6
    start_index = base

    pan = {}
    for i in range(6):
        pan[i + 1] = LIU_REN[(start_index + i) % 6]

    current = LIU_REN[start_index]

    return {
        "局数": base,
        "当前": current,
        "六宫": pan
    }
