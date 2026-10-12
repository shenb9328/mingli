# -*- coding: utf-8 -*-
"""
MingLi - 渲染器子包
提供 Terminal、Markdown、JSON 等多种渲染模式输出。
用户可自行添加新的渲染器（如 HTML、图片、卡片等）。
"""

from mingli.renderers.terminal import render_terminal
from mingli.renderers.markdown import render_markdown
from mingli.renderers.json_render import render_json

__all__ = [
    "render_terminal",
    "render_markdown",
    "render_json",
]
