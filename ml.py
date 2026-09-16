# =====================================================================
# suanshu_system.py
# 术数综合排盘系统（终端美化版：八字 + 小六壬 + 梅花易数 + 奇门遁甲）
# =====================================================================

import datetime
import sys
import io
import json
import math
import unicodedata
from lunar_python import Solar, Lunar


# =====================================================================
# 0. 城市经度数据与真太阳时计算模块
# =====================================================================

CITY_LONGITUDES = {
    # 直辖市
    "北京": 116.40, "上海": 121.47, "天津": 117.20, "重庆": 106.55,
    # 浙江
    "杭州": 120.16, "宁波": 121.54, "温州": 120.70, "绍兴": 120.58, "湖州": 120.09, "嘉兴": 120.75, "金华": 119.64, "衢州": 118.87, "台州": 121.42, "丽水": 119.92, "舟山": 122.21,
    # 四川
    "成都": 104.06, "绵阳": 104.73, "自贡": 104.78, "攀枝花": 101.72, "泸州": 105.44, "德阳": 104.38, "广元": 105.83, "遂宁": 105.57, "内江": 105.06, "乐山": 103.76, "南充": 106.08, "眉山": 103.83, "宜宾": 104.62, "广安": 106.63, "达州": 107.50, "雅安": 103.00, "巴中": 106.77, "资阳": 104.65, "阿坝": 102.22, "甘孜": 101.96, "凉山": 102.26,
    # 广东
    "广州": 113.26, "深圳": 114.06, "珠海": 113.52, "汕头": 116.69, "韶关": 113.59, "佛山": 113.11, "江门": 113.06, "湛江": 110.38, "茂名": 110.92, "肇庆": 112.47, "惠州": 114.41, "梅州": 116.12, "汕尾": 115.36, "河源": 114.70, "阳江": 111.98, "清远": 113.04, "东莞": 113.75, "中山": 113.38, "潮州": 116.62, "揭阳": 116.37, "云浮": 112.04,
    # 江苏
    "南京": 118.78, "无锡": 120.30, "徐州": 117.18, "常州": 119.95, "苏州": 120.62, "南通": 120.86, "连云港": 119.16, "淮安": 119.02, "盐城": 120.13, "扬州": 119.42, "镇江": 119.44, "泰州": 119.90, "宿迁": 118.30,
    # 福建
    "福州": 119.30, "厦门": 118.10, "莆田": 119.00, "三明": 117.61, "泉州": 118.58, "漳州": 117.66, "南平": 118.17, "龙岩": 117.02, "宁德": 119.52,
    # 山东
    "济南": 117.00, "青岛": 120.33, "淄博": 118.05, "枣庄": 117.57, "东营": 118.49, "烟台": 121.39, "潍坊": 119.10, "济宁": 116.59, "泰安": 117.13, "威海": 122.10, "日照": 119.46, "莱芜": 117.67, "临沂": 118.35, "德州": 116.29, "聊城": 115.97, "滨州": 118.03, "菏泽": 115.48,
    # 湖北
    "武汉": 114.31, "黄石": 115.09, "十堰": 110.79, "宜昌": 111.30, "襄阳": 112.14, "鄂州": 114.89, "荆门": 112.20, "孝感": 113.92, "荆州": 112.24, "黄冈": 114.87, "咸宁": 114.32, "随州": 113.37, "恩施": 109.48, "仙桃": 113.45, "潜江": 112.89, "天门": 113.16, "神农架": 110.67,
    # 湖南
    "长沙": 113.00, "株洲": 113.16, "湘潭": 112.91, "衡阳": 112.61, "邵阳": 111.46, "岳阳": 113.09, "常德": 111.69, "张家界": 110.48, "益阳": 112.33, "郴州": 113.01, "永州": 111.63, "怀化": 109.97, "娄底": 112.00, "湘西": 109.73,
    # 河南
    "郑州": 113.65, "开封": 114.35, "洛阳": 112.44, "平顶山": 113.29, "安阳": 114.35, "鹤壁": 114.17, "新乡": 113.85, "焦作": 113.21, "濮阳": 115.02, "许昌": 113.82, "漯河": 114.02, "三门峡": 111.19, "南阳": 112.53, "商丘": 115.65, "信阳": 114.05, "周口": 114.63, "驻马店": 114.02, "济源": 112.60,
    # 河北
    "石家庄": 114.48, "唐山": 118.02, "秦皇岛": 119.57, "邯郸": 114.47, "邢台": 114.48, "保定": 115.48, "张家口": 114.88, "承德": 117.93, "沧州": 116.83, "廊坊": 116.70, "衡水": 115.72,
    # 山西
    "太原": 112.53, "大同": 113.30, "阳泉": 113.57, "长治": 113.11, "晋城": 112.85, "朔州": 112.43, "晋中": 112.75, "运城": 111.00, "忻州": 112.73, "临汾": 111.52, "吕梁": 111.13,
    # 陕西
    "西安": 108.95, "铜川": 109.11, "宝鸡": 107.15, "咸阳": 108.70, "渭南": 109.50, "延安": 109.47, "汉中": 107.02, "榆林": 109.72, "安康": 109.02, "商洛": 109.93,
    # 安徽
    "合肥": 117.27, "芜湖": 118.38, "蚌埠": 117.38, "淮南": 117.00, "马鞍山": 118.51, "淮北": 116.80, "铜陵": 117.82, "安庆": 117.03, "黄山": 118.31, "滁州": 118.32, "阜阳": 115.81, "宿州": 116.98, "六安": 116.51, "亳州": 115.78, "池州": 117.48, "宣城": 118.76,
    # 江西
    "南昌": 115.89, "景德镇": 117.22, "萍乡": 113.85, "九江": 115.97, "新余": 114.93, "鹰潭": 117.03, "赣州": 114.94, "吉安": 114.97, "宜春": 114.38, "抚州": 116.35, "上饶": 117.97,
    # 广西
    "南宁": 108.33, "柳州": 109.40, "桂林": 110.28, "梧州": 111.34, "北海": 109.12, "防城港": 108.35, "钦州": 108.62, "贵港": 109.60, "玉林": 110.14, "百色": 106.62, "贺州": 111.55, "河池": 108.06, "来宾": 109.24, "崇左": 107.36,
    # 海南
    "海口": 110.35, "三亚": 109.51, "三沙": 112.33, "儋州": 109.57,
    # 贵州
    "贵阳": 106.71, "六盘水": 104.83, "遵义": 106.90, "安顺": 105.92, "铜仁": 109.19, "黔西南": 104.91, "毕节": 105.28, "黔东南": 107.97, "黔南": 107.51,
    # 云南
    "昆明": 102.73, "曲靖": 103.79, "玉溪": 102.54, "保山": 99.16, "昭通": 103.71, "丽江": 100.23, "普洱": 100.97, "临沧": 100.08, "楚雄": 101.54, "红河": 103.39, "文山": 104.24, "西双版纳": 100.80, "大理": 100.24, "德宏": 98.58, "怒江": 98.85, "迪庆": 99.70,
    # 西藏
    "拉萨": 91.11, "日喀则": 88.88, "昌都": 97.18, "林芝": 94.36, "山南": 91.76, "那曲": 92.06, "阿里": 80.10,
    # 甘肃
    "兰州": 103.82, "嘉峪关": 98.27, "金昌": 102.19, "白银": 104.17, "天水": 105.72, "武威": 102.64, "张掖": 100.46, "平凉": 106.67, "酒泉": 98.51, "庆阳": 107.63, "定西": 104.62, "陇南": 104.92, "临夏": 103.21, "甘南": 102.91,
    # 青海
    "西宁": 101.74, "海东": 102.10, "海北": 100.90, "黄南": 102.01, "海南州": 100.62, "果洛": 100.24, "玉树": 97.02, "海西": 97.37,
    # 宁夏
    "银川": 106.27, "石嘴山": 106.39, "吴忠": 106.20, "固原": 106.28, "中卫": 105.18,
    # 新疆
    "乌鲁木齐": 87.68, "克拉玛依": 84.87, "吐鲁番": 89.18, "哈密": 93.51, "昌吉": 87.30, "博尔塔拉": 82.07, "巴音郭楞": 86.15, "阿克苏": 80.26, "克孜勒苏": 76.17, "喀什": 75.99, "和田": 79.92, "伊犁": 81.31, "塔城": 82.98, "阿勒泰": 88.13, "石河子": 86.04,
    # 内蒙古
    "呼和浩特": 111.67, "包头": 109.84, "乌海": 106.82, "赤峰": 118.96, "通辽": 122.26, "鄂尔多斯": 109.99, "呼伦贝尔": 119.77, "巴彦淖尔": 107.42, "乌兰察布": 113.11, "兴安盟": 122.07, "锡林郭勒": 116.09, "阿拉善": 105.70,
    # 辽宁
    "沈阳": 123.38, "大连": 121.62, "鞍山": 122.99, "抚顺": 123.98, "本溪": 123.77, "丹东": 124.37, "锦州": 121.15, "营口": 122.23, "阜新": 121.65, "辽阳": 123.17, "盘锦": 122.06, "铁岭": 123.84, "朝阳": 120.45, "葫芦岛": 120.85,
    # 吉林
    "长春": 125.35, "吉林市": 126.57, "吉林": 126.57, "四平": 124.37, "辽源": 125.14, "通化": 125.94, "白山": 126.42, "松原": 124.82, "白城": 122.84, "延边": 129.51,
    # 黑龙江
    "哈尔滨": 126.63, "齐齐哈尔": 123.97, "鸡西": 130.97, "鹤岗": 130.27, "双鸭山": 131.16, "大庆": 125.03, "伊春": 128.90, "佳木斯": 130.37, "七台河": 131.00, "牡丹江": 129.60, "黑河": 127.49, "绥化": 126.98, "大兴安岭": 124.71,
    # 港澳台
    "香港": 114.17, "澳门": 113.54, "台北": 121.50, "台中": 120.67, "高雄": 120.30
}

def get_longitude_online(city_name):
    """
    尝试在线获取城市经度
    """
    try:
        from geopy.geocoders import Nominatim
        # 设置超时时间为 2 秒，避免网络卡死
        geolocator = Nominatim(user_agent="suanshu_system")
        location = geolocator.geocode(city_name, timeout=2)
        if location:
            return location.longitude
    except Exception:
        pass
    return None

def get_longitude(city_name):
    """
    结合在线和离线库获取经度，如果在线失败则使用离线预设，最后使用杭州兜底
    """
    name = city_name.strip()
    
    # 1. 尝试在线查询
    lon = get_longitude_online(name)
    if lon is not None:
        return lon, f"{name} (在线获取)"
        
    # 2. 在线失败或无网络，尝试本地字典匹配
    # 尝试去除常见的行政区划后缀进行匹配
    dict_name = name
    for suffix in ["市", "地区", "县", "区", "自治州", "盟"]:
        if dict_name.endswith(suffix) and len(dict_name) > len(suffix):
            dict_name = dict_name[:-len(suffix)]
            break

    if dict_name in CITY_LONGITUDES:
        return CITY_LONGITUDES[dict_name], f"{name} (离线预设)"
        
    # 3. 如果没查到，尝试直接解析为输入数字经度
    try:
        val = float(name)
        if 0 <= val <= 180:
            return val, f"东经 {val}°"
    except ValueError:
        pass
        
    return None, None

def calculate_eot(dt):
    """
    计算给定日期时间的均时差 (Equation of Time)
    :param dt: datetime对象
    :return: 均时差（分钟）
    """
    day_of_year = dt.timetuple().tm_yday
    # 计算 B 参数 (度)
    B = (360 / 365) * (day_of_year - 1)
    B_rad = math.radians(B)
    
    # Spencer (1971) 近似公式计算均时差
    eot = 229.2 * (
        0.000075 + 
        0.001868 * math.cos(B_rad) - 
        0.032077 * math.sin(B_rad) - 
        0.014615 * math.cos(2 * B_rad) - 
        0.04089 * math.sin(2 * B_rad)
    )
    return eot

def get_true_solar_time(dt, longitude):
    """
    根据输入的北京时间和当地经度，计算真太阳时
    :param dt: 输入的标准北京时间 (datetime)
    :param longitude: 当地经度 (float)
    :return: (真太阳时 datetime, 经度时差分钟, 均时差分钟)
    """
    # 经度时差修正：与120°E相比，每差1度相差4分钟
    lon_offset = 4.0 * (longitude - 120.0)
    # 天体均时差修正
    eot_offset = calculate_eot(dt)
    
    total_offset_min = lon_offset + eot_offset
    true_dt = dt + datetime.timedelta(seconds=int(total_offset_min * 60))
    return true_dt, lon_offset, eot_offset


# =====================================================================
# 1. 八字基础模块
# =====================================================================

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


# =====================================================================
# 2. 小六壬模块
# =====================================================================

LIU_REN = ["大安", "留连", "速喜", "赤口", "小吉", "空亡"]

def get_liuren_pan(dt=None):
    if dt is None:
        dt = datetime.datetime.now()

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


# =====================================================================
# 3. 梅花易数模块
# =====================================================================

ZHI_NUM = {
    "子": 1, "丑": 2, "寅": 3, "卯": 4,
    "辰": 5, "巳": 6, "午": 7, "未": 8,
    "申": 9, "酉": 10, "戌": 11, "亥": 12
}

GUA = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤"
}

GUA_ATTR = {
    1: "天", 2: "泽", 3: "火", 4: "雷",
    5: "风", 6: "水", 7: "山", 8: "地"
}

GUA_LINES = {
    1: (1,1,1), 2: (1,1,0), 3: (1,0,1), 4: (1,0,0),
    5: (0,1,1), 6: (0,1,0), 7: (0,0,1), 8: (0,0,0)
}

LINES_TO_GUA = {v: k for k, v in GUA_LINES.items()}

HEXAGRAM_NAME = {
    (1,1):"乾为天",(1,2):"天泽履",(1,3):"天火同人",(1,4):"天雷无妄",
    (1,5):"天风姤",(1,6):"天水讼",(1,7):"天山遁",(1,8):"天地否",
    (2,1):"泽天夬",(2,2):"兑为泽",(2,3):"泽火革",(2,4):"泽雷随",
    (2,5):"泽风大过",(2,6):"泽水困",(2,7):"泽山咸",(2,8):"泽地萃",
    (3,1):"火天大有",(3,2):"火泽睽",(3,3):"离为火",(3,4):"火雷噬嗑",
    (3,5):"火风鼎",(3,6):"火水未济",(3,7):"火山旅",(3,8):"火地晋",
    (4,1):"雷天大壮",(4,2):"雷泽归妹",(4,3):"雷火丰",(4,4):"震为雷",
    (4,5):"雷风恒",(4,6):"雷水解",(4,7):"雷山小过",(4,8):"雷地豫",
    (5,1):"风天小畜",(5,2):"风泽中孚",(5,3):"风火家人",(5,4):"风雷益",
    (5,5):"巽为风",(5,6):"风水涣",(5,7):"风山渐",(5,8):"风地观",
    (6,1):"水天需",(6,2):"水泽节",(6,3):"水火既济",(6,4):"水雷屯",
    (6,5):"水风井",(6,6):"坎为水",(6,7):"水山蹇",(6,8):"水地比",
    (7,1):"山天大畜",(7,2):"山泽损",(7,3):"山火贲",(7,4):"山雷颐",
    (7,5):"山风蛊",(7,6):"山水蒙",(7,7):"艮为山",(7,8):"山地剥",
    (8,1):"地天泰",(8,2):"地泽临",(8,3):"地火明夷",(8,4):"地雷复",
    (8,5):"地风升",(8,6):"地水师",(8,7):"地山谦",(8,8):"坤为地"
}


class MeiHuaInput:
    def __init__(self, year_zhi, month, day, hour_zhi):
        self.year_zhi = year_zhi   
        self.month = month         
        self.day = day             
        self.hour_zhi = hour_zhi   


def _calc_gua(mh: MeiHuaInput):
    y = ZHI_NUM[mh.year_zhi]
    h = ZHI_NUM[mh.hour_zhi]

    base = mh.month + mh.day + y

    upper = base % 8 or 8
    lower = (base + h) % 8 or 8
    move = (base + h) % 6 or 6

    return upper, lower, move


def _build_lines(upper, lower):
    return GUA_LINES[lower] + GUA_LINES[upper]


def _change(lines, move):
    new = list(lines)
    new[move - 1] = 1 - new[move - 1]
    return tuple(new)


def _mutual(lines):
    return (
        lines[1], lines[2], lines[3],
        lines[2], lines[3], lines[4]
    )


def _to_name(upper, lower):
    return HEXAGRAM_NAME[(upper, lower)]


def get_meihua_pan(dt=None, input_obj=None):
    if dt is None:
        dt = datetime.datetime.now()

    if input_obj is None:
        solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lunar = solar.getLunar()
        input_obj = MeiHuaInput(
            year_zhi=lunar.getYearZhi(),   
            month=abs(lunar.getMonth()),
            day=lunar.getDay(),
            hour_zhi=lunar.getTimeZhi()
        )

    upper, lower, move = _calc_gua(input_obj)

    orig = _build_lines(upper, lower)
    chg = _change(orig, move)
    mut = _mutual(orig)

    mut_upper = LINES_TO_GUA[mut[3:6]]
    mut_lower = LINES_TO_GUA[mut[0:3]]

    chg_upper = LINES_TO_GUA[chg[3:6]]
    chg_lower = LINES_TO_GUA[chg[0:3]]

    orig_name = _to_name(upper, lower)
    mut_name = _to_name(mut_upper, mut_lower)
    chg_name = _to_name(chg_upper, chg_lower)

    return {
        "本卦": orig_name,
        "互卦": mut_name,
        "变卦": chg_name,
        "动爻": move,
        "上卦": GUA[upper],
        "下卦": GUA[lower]
    }


# =====================================================================
# 4. 奇门遁甲核心数理与总调度
# =====================================================================

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
    if palace_no == 5 or not door: return False
    d_el = DOOR_ELEMENT.get(door)
    p_el = PALACE_ELEMENT.get(palace_no)
    if d_el == "木" and p_el == "土": return True
    if d_el == "土" and p_el == "水": return True
    if d_el == "水" and p_el == "火": return True
    if d_el == "火" and p_el == "金": return True
    if d_el == "金" and p_el == "木": return True
    return False


def get_display_width(s):
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width


def pad_string(s, total_width):
    curr_width = get_display_width(s)
    padding = max(0, total_width - curr_width)
    return s + " " * padding


def format_palace_block(p_no, name, data):
    """
    格式化单宫格子，统一宽度，便于对齐
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
        if "迫" in data['status']: status_append += "迫"
        if "驿马" in data['status']: status_append += "马"
        
        line1 = f" {god} {star}"
        line2 = f"   {door} {status_append}"
        line3 = f" {data['stems']} {data['kong']}"
        line4 = f"  [{name}]"
        
    return [line1, line2, line3, line4]


def run_all(dt=None, city_name="杭州", json_mode=False):
    if json_mode:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

    if dt is None:
        dt = datetime.datetime.now()

    # 解析经度和真太阳时
    longitude, city_display = get_longitude(city_name)
    if longitude is None:
        longitude = 120.16
        city_display = "杭州 (未识别城市，默认兜底)"

    true_dt, lon_offset, eot_offset = get_true_solar_time(dt, longitude)

    print("\n" + "=" * 66)
    print("                      术数综合排盘系统")
    print("=" * 66)

    # -----------------------
    # 时间及八字
    # -----------------------
    print("\n[ 核心时间与八字 ]")
    print(f" 公历北京时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" 测算城市方位: {city_display} (东经 {longitude:.2f}°)")
    print(f" 时差修正数据: 经度差修正({lon_offset:+.2f}分钟) | 均时差修正({eot_offset:+.2f}分钟) | 总修正({lon_offset+eot_offset:+.2f}分钟)")
    print(f" 当地真太阳时: {true_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    bazi = get_bazi(true_dt)
    print(f" 农历时间: {bazi.lunar_time}")
    print(f" 四柱八字: {bazi.eight_char_str}")
    print(f" 拆解四柱: 年柱({bazi.year_gz})  月柱({bazi.month_gz})  日柱({bazi.day_gz})  时柱({bazi.time_gz})")
    print("-" * 66)

    # -----------------------
    # 小六壬
    # -----------------------
    print("[ 小六壬时间起局 ]")
    liuren = get_liuren_pan(true_dt)
    print(f" 局数: {liuren['局数']}  |  当前落宫: {liuren['当前']}")
    lr_宫位串 = "  ".join([f"宫{k}({v})" for k, v in liuren["六宫"].items()])
    print(f" 六宫分布: {lr_宫位串}")
    print("-" * 66)

    # -----------------------
    # 梅花易数
    # -----------------------
    print("[ 梅花易数排盘 ]")
    mh_input = MeiHuaInput(
        year_zhi=bazi.year_zhi,
        month=bazi.lunar_month,
        day=bazi.lunar_day,
        hour_zhi=bazi.time_zhi
    )
    meihua = get_meihua_pan(true_dt, input_obj=mh_input)
    print(f" 本卦: {meihua['本卦']}   |   互卦: {meihua['互卦']}   |   变卦: {meihua['变卦']}   |   动爻: {meihua['动爻']}爻动")
    print("-" * 66)

    # -----------------------
    # 奇门遁甲推演
    # -----------------------
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
    ju_str = f"{dun_type}{num_chars[ju_number-1]}局"
    
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

    if json_mode:
        sys.stdout = old_stdout
        result_data = {
            "city_info": {
                "city": city_display,
                "longitude": longitude,
                "lon_offset_min": round(lon_offset, 2),
                "eot_offset_min": round(eot_offset, 2),
                "total_offset_min": round(lon_offset + eot_offset, 2)
            },
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
            },
            "liuren": liuren,
            "meihua": meihua,
            "qimen": {
                "ju_str": ju_str,
                "zhifu": f"{time_xun}{hidden_yi}落{PALACE_INFO[time_palace]['name']}",
                "zhishi": f"{zhishi_door}落{PALACE_INFO[zhishi_palace]['name']}",
                "day_kong": day_kong,
                "time_kong": time_kong,
                "yima": yima_branch,
                "palaces": palaces_output
            }
        }
        print(json.dumps(result_data, ensure_ascii=False, indent=2))
        return

    print("[ 奇门遁甲盘局 ]")
    print(f" 节气定局: {ju_str} | 值符: {time_xun}{hidden_yi}落{PALACE_INFO[time_palace]['name']} | 值使: {zhishi_door}落{PALACE_INFO[zhishi_palace]['name']}")
    print(f" 空亡方位: 日空({'-'.join(day_kong)}) 时空({'-'.join(time_kong)}) | 驿马星: {yima_branch}方")
    print()

    # -----------------------
    # 经典洛书九宫终端图形渲染
    # -----------------------
    # 构造标准九宫格方阵行数据（4, 9, 2 / 3, 5, 7 / 8, 1, 6）
    rows_palaces = [
        [4, 9, 2],
        [3, 5, 7],
        [8, 1, 6]
    ]
    
    border = "+" + "--------------------+" * 3
    print(border)
    
    for row in rows_palaces:
        # 获取当前行三个宫位格式化好的各4行文本
        p1 = format_palace_block(row[0], PALACE_INFO[row[0]]["name"], palaces_output[row[0]])
        p2 = format_palace_block(row[1], PALACE_INFO[row[1]]["name"], palaces_output[row[1]])
        p3 = format_palace_block(row[2], PALACE_INFO[row[2]]["name"], palaces_output[row[2]])
        
        # 逐行横向拼接打印
        for i in range(4):
            s1 = pad_string(p1[i], 18)
            s2 = pad_string(p2[i], 18)
            s3 = pad_string(p3[i], 18)
            print(f"| {s1} | {s2} | {s3} |")
        print(border)

    print("\n" + "=" * 66)


if __name__ == "__main__":
    args = sys.argv[1:]
    json_mode = False
    city_name = "杭州"
    
    # 解析 --city 或 -c 参数
    if "--city" in args:
        idx = args.index("--city")
        if idx + 1 < len(args):
            city_name = args[idx+1]
            args = args[:idx] + args[idx+2:]
    elif "-c" in args:
        idx = args.index("-c")
        if idx + 1 < len(args):
            city_name = args[idx+1]
            args = args[:idx] + args[idx+2:]
    
    if args:
        user_input = " ".join(args).strip()
        json_mode = True
    else:
        user_input = input("请输入排盘时间 (格式: YYYY-MM-DD HH:MM:SS，直接回车使用当前系统时间): ").strip()
        # 交互模式下询问城市
        temp_city = input("请输入出生/排盘城市名称 (如: 北京、成都、杭州，直接回车默认杭州): ").strip()
        if temp_city:
            city_name = temp_city
            
        # 验证或输入自定义经度
        lon, _ = get_longitude(city_name)
        if lon is None:
            custom_lon_str = input(f"未在预设数据库中找到城市 '{city_name}'。请输入其经度（如 104.06，直接回车默认使用杭州经度 120.16）: ").strip()
            if custom_lon_str:
                city_name = custom_lon_str
            else:
                city_name = "杭州"
    
    dt = None
    if user_input:
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d",
            "%Y年%m月%d日 %H:%M:%S",
            "%Y年%m月%d日 %H:%M",
            "%Y年%m月%d日"
        ]
        for fmt in formats:
            try:
                dt = datetime.datetime.strptime(user_input, fmt)
                break
            except ValueError:
                pass
        
        if dt is None:
            if not json_mode:
                print("时间格式解析失败，将使用当前系统时间。")
            
    run_all(dt, city_name, json_mode)