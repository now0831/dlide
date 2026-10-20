"""manim 공통 요소: 팔레트, 한글 텍스트, 원형 노드. LaTeX 없이 동작."""
import math
from manim import *  # noqa: F401,F403

FONT = "Malgun Gothic"
NAVY, ACCENT, TEAL, GOLD, GRAY = "#1F3A5F", "#E4572E", "#2A9D8F", "#F4A261", "#8D99AE"
PURPLE, SLATE = "#9B5DE5", "#577590"
PALETTE = [ACCENT, GOLD, NAVY, TEAL, PURPLE, SLATE]

config.background_color = WHITE


def T(s, size=36, color=NAVY, weight=NORMAL):
    """한글 텍스트 (MathTex 대신 사용)"""
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


def node(label, color, r=0.38, size=30):
    """색 원 + 흰 글자"""
    c = Circle(radius=r, fill_color=color, fill_opacity=1, stroke_color=WHITE, stroke_width=4)
    return VGroup(c, T(label, size, WHITE, BOLD).move_to(c))


def ring_pos(n, radius, center=ORIGIN, start=PI / 2):
    """원 위 n개 위치 (맨 위에서 시계 방향)"""
    return [center + radius * np.array([math.cos(start - TAU * i / n), math.sin(start - TAU * i / n), 0]) for i in range(n)]
