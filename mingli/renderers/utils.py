# -*- coding: utf-8 -*-
"""
MingLi - 渲染格式工具库
包含东亚字符等宽对齐、九宫格单宫格式化等辅助函数。
"""

import unicodedata


def get_display_width(s):
    """
    计算字符串在终端中的显示宽度（宽字符占 2 宽度，半角占 1 宽度）
    """
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width


def pad_string(s, total_width):
    """
    对齐填充字符串至指定宽度
    """
    curr_width = get_display_width(s)
    padding = max(0, total_width - curr_width)
    return s + " " * padding


def format_palace_block(p_no, name, data):
    """
    格式化单宫格子，统一宽度，便于终端九宫格对齐
    """
    if p_no == 5:
        line1 = f"  {name}"
        line2 = f"   中五宫"
        line3 = f" {data['stems']} {data['kong']}"
        line4 = f"  {data['status']}"
    else:
        # 分离神/星/门
        parts = data['msg'].split('/')
        god, star, door = parts[0], parts[1], parts[2]
        
        # 加上特殊状态标记
        status_append = ""
        if "迫" in data['status']:
            status_append += "迫"
        if "驿马" in data['status']:
            status_append += "马"
        
        line1 = f" {god} {star}"
        line2 = f"   {door} {status_append}"
        line3 = f" {data['stems']} {data['kong']}"
        line4 = f"  [{name}]"
        
    return [line1, line2, line3, line4]
