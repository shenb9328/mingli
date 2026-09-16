#!/usr/bin/env python3
# =====================================================================
# ml_markdown.py
# 术数综合排盘系统（Markdown 格式导出入口）
# =====================================================================

import sys
import os

# 确保能正确导入同一目录下的 ml 模块
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from ml import main_cli

def main():
    sys.exit(main_cli(args=sys.argv[1:], default_format="markdown"))

if __name__ == '__main__':
    main()
