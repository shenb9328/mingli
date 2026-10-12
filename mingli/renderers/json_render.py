# -*- coding: utf-8 -*-
"""
MingLi - JSON 格式渲染器
输出结构化推演中间态与全量数据，开箱即用对接 Web API。
"""

import json


def render_json(data):
    """
    格式化为标准 JSON 字符串
    :param data: calculate_all 计算输出的全量字典
    :return: 格式化 JSON 字符串
    """
    return json.dumps(data, ensure_ascii=False, indent=2)
