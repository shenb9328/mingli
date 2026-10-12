# 🧩 MingLi 模块化架构与新功能扩展指南

本项目已完成全量模块化解耦重构，将原本单文件脚本解耦为高内聚、易扩展的标准 Python 包结构。每个功能模块职责单一、独立可测试，并支持灵活添加新术数算法与渲染格式。

---

## 📁 模块目录结构

```
mingli/
├── __init__.py            # 顶层统一导出（所有模块 API 均可在此直接导入）
├── solar.py               # 1. 城市经度数据库、均时差 (EOT) 与真太阳时换算
├── bazi.py                # 2. 四柱八字基础排盘（干支历法、藏干、农历）
├── liuren.py              # 3. 小六壬模块（月日时三传与六神速断）
├── meihua.py              # 4. 梅花易数模块（先天八卦、本/互/变卦、动爻）
├── qimen.py               # 5. 时家奇门遁甲模块（拆补法定局、转盘九星八门八神）
├── ziwei.py               # 6. 紫微斗数模块（五行局、十四主星、生年四化、吉凶煞星、大限）
├── engine.py              # 7. 核心调度引擎与模块注册中心（支持动态注册新模块）
├── cli.py                 # 8. 命令行工具与交互模式（参数解析、容错时间提取）
└── renderers/             # 9. 多格式渲染器子包
    ├── __init__.py        # 渲染器导出入口
    ├── utils.py           # 宽字符等宽对齐与格式化辅助工具
    ├── terminal.py        # 终端 ANSI 彩色与九宫格边框渲染
    ├── markdown.py        # Markdown 渲染（兼容飞书、GitHub、语雀）
    └── json_render.py     # 结构化 JSON 纯数据输出
```

---

## 🚀 独立模块使用示例

你可以按需仅导入你需要的独立模块：

### 1. 单独计算真太阳时
```python
import datetime
from mingli.solar import get_true_solar_time, get_longitude

lon, name = get_longitude("成都")
true_dt, lon_offset, eot_offset = get_true_solar_time(datetime.datetime.now(), lon)
print("真太阳时:", true_dt)
```

### 2. 单独排八字
```python
import datetime
from mingli.bazi import get_bazi

bazi = get_bazi(datetime.datetime.now())
print("四柱:", bazi.eight_char_str)
```

### 3. 单独起梅花易数或小六壬
```python
import datetime
from mingli.meihua import get_meihua_pan
from mingli.liuren import get_liuren_pan

mh = get_meihua_pan(datetime.datetime.now())
print("梅花本卦:", mh["本卦"], "变卦:", mh["变卦"])

lr = get_liuren_pan(datetime.datetime.now())
print("小六壬当前落宫:", lr["当前"])
```

### 4. 单独算奇门遁甲
```python
import datetime
from mingli.bazi import get_bazi
from mingli.qimen import get_qimen_pan

dt = datetime.datetime.now()
bazi = get_bazi(dt)
qm = get_qimen_pan(dt, bazi)
print("奇门局制:", qm["ju_str"], "值符:", qm["zhifu"])
```

---

## ➕ 如何添加新的术数排盘功能

### 方式一：注册动态扩展模块（推荐，无需修改核心代码）

使用 `mingli.register_module`，可以在外部或新脚本中注册你的自定义模块。`calculate_all` 运行后会自动调用并把结果整合到总输出中：

```python
from mingli import register_module, calculate_all

# 定义你的新功能计算函数
def my_ziwei_pan(context):
    """
    context 包含：
      - context['dt']: 公历 datetime
      - context['true_dt']: 真太阳时 datetime
      - context['bazi']: BaZiResult 实例
      - context['city_info']: 城市时差字典
    """
    bazi = context['bazi']
    return {
        "ming_gong": "子",
        "shen_gong": "午",
        "description": f"日干 {bazi.day_gz[0]}，命盘已生成"
    }

# 注册模块
register_module("ziwei", my_ziwei_pan)

# 调用总调度
result = calculate_all(city_name="北京")
print(result["ziwei"])
```

### 方式二：作为内置模块集成

如果你想长期内置新的术数（例如紫微斗数 `mingli/ziwei.py`）：
1. 在 `mingli/` 目录下新建 `ziwei.py`，实现计算逻辑；
2. 在 `mingli/__init__.py` 中将其导出；
3. 在 `mingli/engine.py` 的 `calculate_all` 中添加一行调用（或通过 `register_module` 默认载入）；
4. （可选）在 `mingli/renderers/` 中增加对应的格式化渲染展示。

---

## 🛡️ 兼容性说明与备份

- 根目录的 [`ml.py`](file:///home/shenb/.gemini/antigravity-cli/scratch/mingli/ml.py) 已转换为调度门面，全面保持原有 API 与命令行参数向后兼容。
- 原单文件备份保存在：
  - 本地文件：`ml.py.bak`
  - Git 分支：`backup/before-modularization`
