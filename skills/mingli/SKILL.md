---
name: mingli
description: 中国传统术数综合排盘引擎技能（四柱八字真太阳时、时家奇门遁甲、紫微斗数、梅花易数、小六壬）。当用户下达“排盘”或请求术数推演时触发。
version: 1.0.0
author: shenb
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mingli, paipan, bazi, qimen, ziwei, meihua, liuren, astrology]
---

# ☯️ 命理综合排盘智能体技能 (MingLi Agent Skill)

本技能专为各类自主智能体（Hermes Agent、Antigravity、Claude Code、OpenCode、微信/飞书/Telegram 机器人等）设计，提供严谨、极速的中国传统术数全盘计算。

一次调用即可同时输出：
1. **四柱八字**：真太阳时（均时差 EOT + 经纬度校正）、干支藏干、十神基底；
2. **正统小六壬**：月日时三传速断（大安、留连、速喜、赤口、小吉、空亡）；
3. **梅花易数**：先天八卦、本卦/互卦/变卦、动爻生克；
4. **时家奇门遁甲**：转盘拆补法、九宫八神九星八门九宫格；
5. **紫微斗数**：水二/木三/金四/土五/火六五行局、命身宫、生年四化、十二宫、十四主星庙旺平利陷、辅星六吉六煞、大限流年与核心格局判定。

---

## 🛠️ 新环境一键安装指南 (Quick Setup)

在任何全新的服务器、VPS 或智能体运行环境中，执行以下两步即可完成安装：

### 1. 基础环境与依赖
```bash
# 1. 克隆代码仓库（建议存放在用户家目录）
cd ~
git clone https://github.com/shenb9328/mingli.git
# 或使用 SSH: git clone git@github.com:shenb9328/mingli.git

# 2. 安装 Python 核心计算依赖
pip3 install lunar-python geopy
# Debian/Ubuntu 若提示 PEP 668 环境限制，可加: --break-system-packages

# 3. 创建全局可执行快捷命令
mkdir -p ~/.local/bin
cat << 'EOF' > ~/.local/bin/mingli
#!/usr/bin/env bash
exec /usr/bin/python3 ~/mingli/ml.py "$@"
EOF
chmod +x ~/.local/bin/mingli
```

### 2. 注入各智能体框架

- **Hermes Agent (newvps / 微信 / TG 网关)**：
  ```bash
  mkdir -p ~/.hermes/skills/productivity/mingli ~/.hermes/skills/mingli
  cp ~/mingli/skills/mingli/SKILL.md ~/.hermes/skills/productivity/mingli/SKILL.md
  cp ~/mingli/skills/mingli/SKILL.md ~/.hermes/skills/mingli/SKILL.md
  systemctl --user restart hermes-gateway
  ```
- **Antigravity CLI / Sidecar**：
  ```bash
  mkdir -p ~/.gemini/config/skills/mingli
  cp ~/mingli/skills/mingli/SKILL.md ~/.gemini/config/skills/mingli/SKILL.md
  ```
- **Claude Code / OpenCode / Codex**：
  直接引用仓库中的 `skills/mingli/SKILL.md` 即可。

---

## 🎯 触发条件与用户指令模式 (Triggers & Command Patterns)

智能体在接收到用户发送的包含 **“排盘”**、**“起盘”**、**“排八字”**、**“测算”** 等消息时立即激活本技能：

| 用户输入模式 | 识别意图与规则 | 对应底层执行命令 |
| :--- | :--- | :--- |
| **仅输入“排盘”** | 默认使用**当前系统时间（北京时间）**，默认地点为**杭州** | `python3 ~/mingli/ml.py -c 杭州` |
| **简写 10 位时间：`排盘，2509090928`** | 解析为 10 位数字 `YYMMDDHHMM`（即 2025年9月9日 09:28:00），默认地点为**杭州** | `python3 ~/mingli/ml.py "2025-09-09 09:28:00" -c 杭州` |
| **自然语言时间+地点：`排盘，24年7月9日14点3分，地点张掖`** | 1. 提取公历时间：`2024-07-09 14:03:00`<br>2. 提取城市：`张掖`<br>3. **利用 AI 查询该地经度**（张掖约东经 `100.46`） | `python3 ~/mingli/ml.py "2024-07-09 14:03:00" -c "张掖" --lon 100.46` |

---

## ⚡ 绝对忠实输出原则 (CRITICAL - HARDLINE RULE)

所有接入本技能的 AI 智能体必须无条件遵守以下规约：

1. **严禁 AI 二次加工**：
   除在必要时利用 AI 检索目标城市的地理经纬度以外，**严禁用 AI 对排盘结果进行任何形式的擅自解读、吉凶推演、命理断语、增删润色或总结说明**！
2. **100% 忠实原样输出**：
   调用命令行工具执行完毕后，必须将程序运行输出的标准输出文本（stdout）**原封不动、完整无缺地**直接发送给用户。

---

## 📖 CLI 命令行参数速查手册

```bash
python3 ~/mingli/ml.py [time_string] [options]
```

- `time_string`：排盘时间，支持格式：
  - 标准格式：`"2026-09-16 16:00:00"`
  - 10 位简写：`"2509090928"`（2025年9月9日 9点28分）
  - 中文自然语言：`"24年7月9日14点3分"` 或 `"排盘，24年7月9日14点3分，地点张掖"`
- `-c, --city <城市名>`：测算城市（内置全国 120+ 城市离线数据库，默认：杭州）
- `--lon, --longitude <经度>`：显式指定测算地东经经度（用于精确修正天文均时差与真太阳时）
- `-g, --gender <男|女>`：测算人性别（默认：男；影响紫微斗数与大限走向）
- `-f, --format <terminal|markdown|json>`：
  - `terminal`（默认）：输出适合等宽文本终端与即时聊天消息的 3x3 矩阵框图
  - `markdown`：输出结构化 Markdown 表格与文字列表
  - `json`：输出全量结构化 JSON 数据（用于二次开发或 API 转发）
- `-m, --markdown`：快捷输出 Markdown 格式
- `-j, --json`：快捷输出 JSON 格式
