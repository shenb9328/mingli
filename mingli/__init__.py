# -*- coding: utf-8 -*-
"""
MingLi (命理综合排盘引擎)
~~~~~~~~~~~~~~~~~~~~~~

极速、专业、纯粹的中国传统术数排盘引擎与知识库体系。
支持四柱八字、奇门遁甲、梅花易数、小六壬等模块化推演与扩展。
"""

# 基础历法与真太阳时
from mingli.solar import (
    CITY_LONGITUDES,
    get_longitude,
    get_longitude_online,
    calculate_eot,
    get_true_solar_time,
)

# 八字基础模块
from mingli.bazi import (
    BaZiResult,
    get_bazi,
)

# 小六壬速断模块
from mingli.liuren import (
    LIU_REN,
    get_liuren_pan,
)

# 梅花易数模块
from mingli.meihua import (
    MeiHuaInput,
    get_meihua_pan,
    get_trigrams,
)

# 奇门遁甲模块
from mingli.qimen import (
    get_qimen_pan,
    rotate_to_start,
    get_xun_and_kong,
    is_門迫,
)

# 紫微斗数模块
from mingli.ziwei import (
    get_ziwei_pan,
)

# 调度引擎与模块注册中心
from mingli.engine import (
    calculate_all,
    register_module,
    unregister_module,
    get_registered_modules,
)

# 渲染器
from mingli.renderers import (
    render_terminal,
    render_markdown,
    render_json,
)

# CLI 与运行入口
from mingli.cli import (
    main_cli,
    run_all,
    parse_datetime,
    parse_arguments,
)

__version__ = "3.8.0"

__all__ = [
    # 核心调度
    "calculate_all",
    "register_module",
    "unregister_module",
    "get_registered_modules",
    
    # 渲染器
    "render_terminal",
    "render_markdown",
    "render_json",
    
    # CLI 入口
    "main_cli",
    "run_all",
    "parse_datetime",
    "parse_arguments",
    
    # 独立模块功能
    "BaZiResult",
    "get_bazi",
    "LIU_REN",
    "get_liuren_pan",
    "MeiHuaInput",
    "get_meihua_pan",
    "get_trigrams",
    "get_qimen_pan",
    "get_ziwei_pan",
    "CITY_LONGITUDES",
    "get_longitude",
    "get_longitude_online",
    "calculate_eot",
    "get_true_solar_time",
]
