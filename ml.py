#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MingLi (命理综合排盘系统) - 根目录统一兼容入口

本项目已完整重构为高内聚、低耦合的模块化架构 (mingli 包)。
各功能均已拆分为独立子模块，方便随意扩展与独立维护：
  - mingli.solar      : 城市经度数据、均时差与真太阳时计算
  - mingli.bazi       : 四柱八字基础排盘
  - mingli.liuren     : 小六壬速断排盘
  - mingli.meihua     : 梅花易数排盘与卦名爻变
  - mingli.qimen      : 时家奇门遁甲（转盘拆补法）
  - mingli.renderers  : 多格式渲染器 (Terminal, Markdown, JSON)
  - mingli.engine     : 调度引擎与模块注册中心 (register_module)
  - mingli.cli        : 命令行工具与交互模式
"""

import sys
import os

# 确保无论从何处调用，都能正确定位 mingli 模块
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from mingli import (
    # 核心调度与注册
    calculate_all,
    register_module,
    unregister_module,
    get_registered_modules,
    
    # 渲染器
    render_terminal,
    render_markdown,
    render_json,
    
    # 命令行与交互
    main_cli,
    run_all,
    parse_datetime,
    parse_arguments,
    
    # 八字
    BaZiResult,
    get_bazi,
    
    # 小六壬
    LIU_REN,
    get_liuren_pan,
    
    # 梅花易数
    MeiHuaInput,
    get_meihua_pan,
    get_trigrams,
    
    # 奇门遁甲
    get_qimen_pan,
    rotate_to_start,
    get_xun_and_kong,
    is_門迫,
    
    # 紫微斗数
    get_ziwei_pan,
    
    # 真太阳时与城市
    CITY_LONGITUDES,
    get_longitude,
    get_longitude_online,
    calculate_eot,
    get_true_solar_time,
)

if __name__ == "__main__":
    sys.exit(main_cli())