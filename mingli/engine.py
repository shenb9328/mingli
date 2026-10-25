# -*- coding: utf-8 -*-
"""
MingLi - 核心调度引擎与模块注册中心
负责组织调用各个独立的术数计算模块，并提供开放的模块注册接口（方便添加紫微斗数、六爻、大六壬等新模块）。
"""

import datetime
from mingli.solar import get_longitude, get_true_solar_time
from mingli.bazi import get_bazi
from mingli.liuren import get_liuren_pan
from mingli.meihua import MeiHuaInput, get_meihua_pan
from mingli.qimen import get_qimen_pan
from mingli.ziwei import get_ziwei_pan

# 用户自定义扩展模块注册表
_CUSTOM_MODULES = {}


def register_module(name, handler):
    """
    注册自定义术数/排盘计算模块。
    
    :param name: 模块名称（如 'ziwei', 'liuyao' 等）
    :param handler: 计算函数，签名应支持：
                    handler(context) 或 handler(true_dt=..., bazi=..., **kwargs)
                    context 包含字段:
                      - 'dt': 标准公历 datetime
                      - 'true_dt': 当地真太阳时 datetime
                      - 'bazi': BaZiResult 实例
                      - 'city_info': 城市经纬度时差信息字典
    """
    _CUSTOM_MODULES[name] = handler


def unregister_module(name):
    """
    注销自定义模块
    """
    return _CUSTOM_MODULES.pop(name, None)


def get_registered_modules():
    """
    获取当前已注册的自定义模块字典
    """
    return dict(_CUSTOM_MODULES)


def calculate_all(dt=None, city_name="杭州", longitude=None, gender="男", enabled_modules=None):
    """
    核心调度计算引擎：统一调用各个独立算法模块，产出全量结构化排盘数据。
    
    :param dt: 输入的公历时间 (datetime)，默认为当前北京时间
    :param city_name: 测算城市名称，默认杭州
    :param longitude: 自定义经度（如指定则跳过城市库检索）
    :param gender: 测算人性别 ("男" 或 "女")，默认 "男"
    :param enabled_modules: 指定启用的模块列表（可选），默认运行全部内置与已注册扩展模块
    :return: 包含所有排盘结果要素的字典
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).replace(tzinfo=None)

    # 1. 解析城市经度与真太阳时
    if longitude is not None:
        city_display = f"{city_name} (自定义经度)" if city_name else f"东经 {longitude:.2f}°"
    else:
        lon_found, city_disp = get_longitude(city_name)
        if lon_found is None:
            longitude = 120.16
            city_display = "杭州 (未识别城市，默认兜底)"
        else:
            longitude = lon_found
            city_display = city_disp

    true_dt, lon_offset, eot_offset = get_true_solar_time(dt, longitude)

    city_info = {
        "city": city_display,
        "longitude": longitude,
        "lon_offset_min": round(lon_offset, 2),
        "eot_offset_min": round(eot_offset, 2),
        "total_offset_min": round(lon_offset + eot_offset, 2)
    }

    # 2. 八字基础模块（核心历法基石）
    bazi = get_bazi(true_dt)

    output = {
        "city_info": city_info,
        "bazi": {
            "solar_time": dt.strftime('%Y-%m-%d %H:%M:%S'),
            "true_solar_time": true_dt.strftime('%Y-%m-%d %H:%M:%S'),
            "lunar_time": bazi.lunar_time,
            "eight_char_str": bazi.eight_char_str,
            "pillars": {
                "year": bazi.year_gz,
                "month": bazi.month_gz,
                "day": bazi.day_gz,
                "time": bazi.time_gz
            }
        }
    }

    # 3. 小六壬模块（正统农历月日时三传速断）
    if enabled_modules is None or "liuren" in enabled_modules:
        output["liuren"] = get_liuren_pan(true_dt, bazi)

    # 4. 梅花易数模块
    if enabled_modules is None or "meihua" in enabled_modules:
        mh_input = MeiHuaInput(
            year_zhi=bazi.year_zhi,
            month=bazi.lunar_month,
            day=bazi.lunar_day,
            hour_zhi=bazi.time_zhi
        )
        output["meihua"] = get_meihua_pan(true_dt, input_obj=mh_input)

    # 5. 奇门遁甲模块
    if enabled_modules is None or "qimen" in enabled_modules:
        output["qimen"] = get_qimen_pan(true_dt, bazi)

    # 6. 紫微斗数模块
    if enabled_modules is None or "ziwei" in enabled_modules:
        output["ziwei"] = get_ziwei_pan(
            dt=dt, city_name=city_name, longitude=longitude,
            gender=gender, true_dt=true_dt, bazi=bazi
        )

    # 7. 执行已注册的用户扩展模块
    context = {
        "dt": dt,
        "true_dt": true_dt,
        "bazi": bazi,
        "city_info": city_info
    }
    for mod_name, handler in _CUSTOM_MODULES.items():
        if enabled_modules is not None and mod_name not in enabled_modules:
            continue
        try:
            # 兼容两种函数传参方式
            try:
                res = handler(context)
            except TypeError:
                res = handler(true_dt=true_dt, bazi=bazi, dt=dt, city_info=city_info)
            output[mod_name] = res
        except Exception as e:
            output[mod_name] = {"error": str(e)}

    return output
