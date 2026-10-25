# -*- coding: utf-8 -*-
"""
MingLi - 命令行工具与调度入口
提供日期时间智能解析、CLI 命令行参数解析、交互模式与统一执行。
"""

import sys
import re
import datetime
import argparse

from mingli.engine import calculate_all
from mingli.solar import get_longitude
from mingli.renderers import render_terminal, render_markdown, render_json


def parse_datetime(user_input):
    """
    智能解析各种中英文格式的日期时间字符串（支持10位数字YYMMDDHHMM、两位数年份、中文年月日时分秒、前缀剥离等）
    """
    if not user_input:
        return None
    s = user_input.strip()
    # 剥离 "排盘"、"时间"、"日期"、"时刻"、"公历"、"阳历" 等常见前缀
    s = re.sub(r"^(排盘|起盘|测算|算卦|排八字)[,，\s]*", "", s).strip()
    s = re.sub(r"^(时间|时刻|日期|公历|阳历)[:：\s]*", "", s).strip()
    
    if not s or s.lower() in ("now", "当前", "现在"):
        return None

    # 1. 纯数字简写格式 (如 2509090928 -> 2025-09-09 09:28)
    if re.fullmatch(r"\d{10}", s):
        try:
            return datetime.datetime.strptime("20" + s, "%Y%m%d%H%M")
        except ValueError:
            pass
    if re.fullmatch(r"\d{12}", s):
        try:
            return datetime.datetime.strptime("20" + s, "%Y%m%d%H%M%S")
        except ValueError:
            pass
    if re.fullmatch(r"\d{6}", s):
        try:
            return datetime.datetime.strptime("20" + s, "%Y%m%d")
        except ValueError:
            pass

    # 2. 尝试标准 strptime 格式
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
        "%Y.%m.%d %H:%M:%S",
        "%Y.%m.%d %H:%M",
        "%Y.%m.%d",
        "%Y年%m月%d日 %H:%M:%S",
        "%Y年%m月%d日 %H:%M",
        "%Y年%m月%d日",
        "%Y%m%d%H%M%S",
        "%Y%m%d %H%M%S",
        "%Y%m%d",
    ]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            pass

    # 3. 强大的正则容错提取（支持2位/4位年，中文年/月/日/点/时/分/秒，单双位数均可）
    pattern = r"(\d{2,4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})[日号]?(?:[\sT]*(\d{1,2})(?:[点时:](\d{1,2})(?:[分:](\d{1,2})[秒]?)?|[点时]))?"
    m = re.search(pattern, s)
    if m:
        y, mon, d = m.group(1), m.group(2), m.group(3)
        year = int(y)
        if len(y) == 2:
            year += 2000 if year < 70 else 1900
        h = m.group(4)
        minute = m.group(5)
        sec = m.group(6)
        hour = int(h) if h is not None else 0
        minute = int(minute) if minute is not None else 0
        second = int(sec) if sec is not None else 0
        try:
            return datetime.datetime(year, int(mon), int(d), hour, minute, second)
        except ValueError:
            pass

    return None


def extract_city_and_time(user_input, default_city="杭州"):
    """
    从综合输入串中同时解析城市地点与时间
    如: '排盘，24年7月9日14点3分，地点张掖' -> (datetime(2024, 7, 9, 14, 3), '张掖')
    """
    if not user_input:
        return None, default_city
    s = user_input.strip()
    s = re.sub(r"^(排盘|起盘|测算|算卦|排八字)[,，\s]*", "", s).strip()
    
    city = None
    city_m = re.search(r"(?:地点|城市|方位|地区)[：:\s]*([^\s,，]+)", s)
    if city_m:
        city = city_m.group(1).strip()
        s = s[:city_m.start()] + s[city_m.end():]
        s = s.strip(" ,，")
        
    dt = parse_datetime(s)
    return dt, city or default_city


def parse_arguments(args=None, default_format="terminal"):
    """
    构建标准命令行参数解析器
    """
    parser = argparse.ArgumentParser(
        description="术数综合排盘系统（八字 + 小六壬 + 梅花易数 + 奇门遁甲）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""使用示例:
  python3 ml.py                           # 当前时间排盘（终端表格）
  python3 ml.py "2026-09-16 16:00:00"     # 指定时间排盘
  python3 ml.py -c 北京                   # 指定测算城市
  python3 ml.py --lon 104.06              # 直接指定经度
  python3 ml.py -f markdown               # 输出 Markdown 排版
  python3 ml.py -f json                   # 输出 JSON 格式
  python3 ml.py -i                        # 进入交互式排盘
"""
    )
    parser.add_argument("time_pos", nargs="*", default=None, help="排盘时间 (如 '2026-09-16 16:00:00')")
    parser.add_argument("-t", "--time", dest="time_opt", default=None, help="排盘时间 (显式指定参数)")
    parser.add_argument("-c", "--city", dest="city", default="杭州", help="排盘城市名称 (默认: 杭州)")
    parser.add_argument("-g", "--gender", dest="gender", choices=["男", "女"], default="男", help="测算人性别: 男 (默认), 女")
    parser.add_argument("--lon", "--longitude", dest="longitude", type=float, default=None, help="直接指定测算地经度 (如 120.16)")
    parser.add_argument("-f", "--format", dest="format", choices=["terminal", "markdown", "json"], default=default_format, help="输出格式: terminal (默认), markdown, json")
    parser.add_argument("-m", "--markdown", dest="markdown_flag", action="store_true", help="快捷开关: 输出 Markdown 格式")
    parser.add_argument("-j", "--json", dest="json_flag", action="store_true", help="快捷开关: 输出 JSON 格式")
    parser.add_argument("-i", "--interactive", dest="interactive", action="store_true", help="进入交互模式引导输入")
    return parser.parse_args(args)


def run_all(dt=None, city_name="杭州", json_mode=False):
    """
    兼容历史接口
    """
    data = calculate_all(dt=dt, city_name=city_name)
    if json_mode:
        print(render_json(data))
    else:
        print(render_terminal(data))
    return data


def main_cli(args=None, default_format="terminal"):
    """
    CLI 统一主入口
    """
    parsed = parse_arguments(args, default_format=default_format)
    
    # 格式优先级判定
    out_format = parsed.format
    if parsed.markdown_flag:
        out_format = "markdown"
    elif parsed.json_flag:
        out_format = "json"
        
    city_name = parsed.city
    longitude = parsed.longitude
    dt = None
    
    if parsed.interactive:
        user_time_str = input("请输入排盘时间 (格式: YYYY-MM-DD HH:MM:SS，直接回车使用当前系统时间): ").strip()
        if user_time_str:
            dt = parse_datetime(user_time_str)
            if dt is None:
                print("时间格式解析失败，将使用当前系统时间。")
                
        temp_city = input("请输入出生/排盘城市名称 (如: 北京、成都、杭州，直接回车默认杭州): ").strip()
        if temp_city:
            city_name = temp_city
            
        lon_chk, _ = get_longitude(city_name)
        if lon_chk is None:
            custom_lon_str = input(f"未在预设数据库中找到城市 '{city_name}'。请输入其经度（如 104.06，直接回车默认使用杭州经度 120.16）: ").strip()
            if custom_lon_str:
                try:
                    longitude = float(custom_lon_str)
                except ValueError:
                    city_name = "杭州"
            else:
                city_name = "杭州"
    else:
        # 非交互模式
        time_str = None
        if parsed.time_opt:
            time_str = parsed.time_opt.strip()
        elif parsed.time_pos:
            time_str = " ".join(parsed.time_pos).strip()
            
        if time_str:
            extracted_dt, extracted_city = extract_city_and_time(time_str, default_city=city_name)
            dt = extracted_dt
            if parsed.city == "杭州" and extracted_city != "杭州":
                city_name = extracted_city
            clean_token = re.sub(r"^(排盘|起盘|测算|算卦|排八字)[,，\s]*", "", time_str).strip()
            if dt is None and clean_token and clean_token not in ("排盘", "起盘", "算卦", "排八字", "now", "当前", "现在") and out_format == "terminal":
                print(f"提示: 时间格式 '{time_str}' 无法解析，已使用当前系统时间。")
                
    data = calculate_all(dt=dt, city_name=city_name, longitude=longitude, gender=parsed.gender)
    
    if out_format == "markdown":
        print(render_markdown(data))
    elif out_format == "json":
        print(render_json(data))
    else:
        print(render_terminal(data))
        
    return 0
