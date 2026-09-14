import sys
import os
import json
import subprocess
import datetime
import unicodedata

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

GUA = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤"
}

def get_trigrams(gua_name):
    for (upper, lower), name in HEXAGRAM_NAME.items():
        if name == gua_name:
            return f"（上{GUA[upper]}下{GUA[lower]}）"
    return ""

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

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ml_py = os.path.join(dir_path, "ml.py")
    
    args = sys.argv[1:]
    
    # Check if a date/time was provided (non-city argument)
    temp_args = list(args)
    if "--city" in temp_args:
        idx = temp_args.index("--city")
        temp_args = temp_args[:idx] + temp_args[idx+2:]
    elif "-c" in temp_args:
        idx = temp_args.index("-c")
        temp_args = temp_args[:idx] + temp_args[idx+2:]
        
    if not temp_args:
        # No date/time provided, append current time in Beijing Time (UTC+8) to force JSON mode in ml.py
        tz_utc8 = datetime.timezone(datetime.timedelta(hours=8))
        now_str = datetime.datetime.now(tz_utc8).strftime("%Y-%m-%d %H:%M:%S")
        args.append(now_str)
        
    cmd = [sys.executable, ml_py] + args
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        stdout = res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running ml.py: {e.stderr}", file=sys.stderr)
        sys.exit(1)
        
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from ml.py output:\n{stdout}", file=sys.stderr)
        sys.exit(1)
        
    # Extract values
    city_display = data['city_info']['city']
    longitude = data['city_info']['longitude']
    
    solar_time_str = data['bazi']['solar_time']
    try:
        dt_solar = datetime.datetime.strptime(solar_time_str, "%Y-%m-%d %H:%M:%S")
        title_time = dt_solar.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        title_time = solar_time_str
        
    true_solar_time_str = data['bazi']['true_solar_time']
    try:
        dt_true = datetime.datetime.strptime(true_solar_time_str, "%Y-%m-%d %H:%M:%S")
        true_solar_time = dt_true.strftime("%H:%M")
    except ValueError:
        true_solar_time = true_solar_time_str
        
    lunar_time = data['bazi']['lunar_time']
    
    # 1. Output Header
    print(f"**当前时刻（{title_time} · 北京时间）地点：{city_display.split(' ')[0]}排盘结果**\n")
    print("---")
    print("\n**基本信息**")
    print(f"- **公历**：{solar_time_str}（北京时间）")
    print(f"- **真太阳时**：{true_solar_time}")
    print(f"- **农历**：{lunar_time}")
    print(f"- **测算方位**：{city_display} 东经 {longitude:.2f}°\n")
    print("---")
    
    # 2. Bazi Table (Wrapped in text code block)
    print("\n**八字四柱**")
    print("```text")
    print("柱    天干地支")
    print("────  ────────")
    print(f"年柱  {data['bazi']['pillars']['year']}")
    print(f"月柱  {data['bazi']['pillars']['month']}")
    print(f"日柱  {data['bazi']['pillars']['day']}")
    print(f"时柱  {data['bazi']['pillars']['time']}")
    print("```\n")
    print("---")
    
    # 3. Xiao Liuren
    liuren = data['liuren']
    print("\n**小六壬**")
    print(f"- **局数**：{liuren['局数']}")
    print(f"- **当前落宫**：{liuren['当前']}\n")
    print("```text")
    print("宫位  名称")
    print("────  ────")
    for k in sorted(liuren['六宫'].keys(), key=int):
        print(f"{pad_string(k, 6)}{liuren['六宫'][k]}")
    print("```\n")
    print("---")
    
    # 4. Meihua
    mh = data['meihua']
    move_str = ["一", "二", "三", "四", "五", "六"][int(mh['动爻'])-1]
    print("\n**梅花易数**")
    print(f"- **本卦**：{mh['本卦']}{get_trigrams(mh['本卦'])}")
    print(f"- **互卦**：{mh['互卦']}{get_trigrams(mh['互卦'])}")
    print(f"- **变卦**：{mh['变卦']}{get_trigrams(mh['变卦'])}")
    print(f"- **动爻**：{move_str}爻\n")
    print("---")
    
    # 5. Qimen
    qm = data['qimen']
    print("\n**奇门遁甲**")
    print(f"- **局制**：{qm['ju_str']}")
    print(f"- **值符**：{qm['zhifu']}")
    print(f"- **值使**：{qm['zhishi']}")
    print(f"- **日空**：{'、'.join(qm['day_kong']) if qm['day_kong'] else '无'}")
    print(f"- **时空**：{'、'.join(qm['time_kong']) if qm['time_kong'] else '无'}")
    print(f"- **驿马**：{qm['yima']}\n")
    
    print("```text")
    print("宫位  九星  八神  八门  天干   备注")
    print("────  ────  ────  ────  ─────  ────")
    for p_no in sorted(qm['palaces'].keys(), key=int):
        p_data = qm['palaces'][p_no]
        if p_no == "5" or p_data['msg'] == "-":
            god, star, door = "—", "—", "—"
        else:
            parts = p_data['msg'].split('/')
            god, star, door = parts[0], parts[1], parts[2]
            
        stems = p_data['stems']
        
        remarks = []
        if p_data['kong']:
            remarks.append(p_data['kong'])
        if p_data['status']:
            remarks.append(p_data['status'])
        remarks_str = "、".join(remarks)
        
        col_no = pad_string(p_no, 6)
        col_star = pad_string(star, 6)
        col_god = pad_string(god, 6)
        col_door = pad_string(door, 6)
        col_stems = pad_string(stems, 7)
        col_remarks = remarks_str
        
        print(f"{col_no}{col_star}{col_god}{col_door}{col_stems}{col_remarks}")
    print("```")

if __name__ == '__main__':
    main()
