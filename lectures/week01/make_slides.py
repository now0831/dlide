"""1주차 슬라이드 생성: manim 영상(anim/) + 비유 사진(01_source/이미지_도표) + 정적 그림"""
import os, json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ANIM = os.path.join(HERE, "anim")
IMG = os.path.join(ROOT, "01_source", "이미지_도표")
FIG = os.path.join(HERE, "fig")
os.makedirs(FIG, exist_ok=True)
OUT = os.path.join(ROOT, "output", "week01_순열.pptx")
CREDITS = json.load(open(os.path.join(IMG, "credits.json"), encoding="utf-8"))

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

NAVY = "#1F3A5F"; ACCENT = "#E4572E"; TEAL = "#2A9D8F"; GOLD = "#F4A261"; GRAY = "#8D99AE"; LIGHT = "#EEF2F7"
COLORS = [ACCENT, GOLD, NAVY, TEAL, "#9B5DE5", "#577590"]


def save(fig, name):
    p = os.path.join(FIG, name)
    fig.savefig(p, dpi=200, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return p


def ring(ax, cx, cy, labels, r=1.0, colors=None, node_r=0.28, fs=16):
    ax.add_patch(Circle((cx, cy), r, fill=False, lw=2.5, ec=GRAY))
    n = len(labels)
    for i, lab in enumerate(labels):
        a = math.pi / 2 - 2 * math.pi * i / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        ax.add_patch(Circle((x, y), node_r, fc=colors[i] if colors else NAVY, ec="white", lw=1.5, zorder=3))
        ax.text(x, y, lab, ha="center", va="center", color="white", fontsize=fs, fontweight="bold", zorder=4)


def setup(ax, xlim, ylim):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.axis("off")


def fig_ring_network():
    fig, ax = plt.subplots(figsize=(6, 6))
    setup(ax, (-1.9, 1.9), (-1.9, 1.9))
    labels = ["S1", "S2", "S3", "S4", "S5", "S6"]
    n = len(labels)
    pts = [(1.5 * math.cos(math.pi/2 - 2*math.pi*i/n), 1.5 * math.sin(math.pi/2 - 2*math.pi*i/n)) for i in range(n)]
    for i in range(n):
        ax.add_patch(FancyArrowPatch(pts[i], pts[(i+1) % n], arrowstyle="-", lw=3, color=GRAY))
    for (x, y), lab in zip(pts, labels):
        ax.add_patch(FancyBboxPatch((x-0.3, y-0.2), 0.6, 0.4, boxstyle="round,pad=0.04", fc=NAVY, ec="white", zorder=3))
        ax.text(x, y, lab, ha="center", va="center", color="white", fontsize=15, fontweight="bold", zorder=4)
    ax.text(0, 0, "링(Ring)\n네트워크", ha="center", va="center", fontsize=18, color=NAVY, fontweight="bold")
    return save(fig, "ring_network.png")


def fig_summary():
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    titles = [("순열", r"$_nP_r = n!\,/\,(n-r)!$"), ("원순열", r"$(n-1)!$"), ("중복순열", r"$_n\Pi_r = n^r$")]
    for ax in axes:
        setup(ax, (-1.8, 1.8), (-1.9, 1.6))
    for i, ch in enumerate("ABCD"):
        axes[0].add_patch(Circle((-1.2 + i * 0.8, 0.3), 0.32, fc=COLORS[i], ec="white"))
        axes[0].text(-1.2 + i * 0.8, 0.3, ch, ha="center", va="center", color="white", fontsize=14, fontweight="bold")
    ring(axes[1], 0, 0.2, list("ABCD"), colors=COLORS[:4], r=0.9, node_r=0.3, fs=14)
    for i, ch in enumerate("AABA"):
        axes[2].add_patch(Circle((-1.2 + i * 0.8, 0.3), 0.32, fc=COLORS["AB".index(ch)], ec="white"))
        axes[2].text(-1.2 + i * 0.8, 0.3, ch, ha="center", va="center", color="white", fontsize=14, fontweight="bold")
    for ax, (t, f), d in zip(axes, titles, ["서로 다른 것, 일렬", "회전하면 같은 것", "같은 것 반복 허용"]):
        ax.text(0, 1.45, t, ha="center", fontsize=18, color=NAVY, fontweight="bold")
        ax.text(0, -1.25, f, ha="center", fontsize=16, color=ACCENT, fontweight="bold")
        ax.text(0, -1.8, d, ha="center", fontsize=12, color=GRAY)
    return save(fig, "summary.png")


def crop_to(name, w, h):
    """사진을 슬라이드 칸 비율(w:h)로 가운데 자르기"""
    im = Image.open(os.path.join(IMG, name)).convert("RGB")
    W, H = im.size; target = w / h
    if W / H > target:
        nw = int(H * target); box = ((W - nw) // 2, 0, (W - nw) // 2 + nw, H)
    else:
        nh = int(W / target); box = (0, (H - nh) // 2, W, (H - nh) // 2 + nh)
    p = os.path.join(FIG, f"crop_{w:.1f}x{h:.1f}_{os.path.basename(name)}")
    im.crop(box).save(p, quality=90)
    return p


figs = dict(ring=fig_ring_network(), summary=fig_summary())

# ---------------- PPTX ----------------
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
FONT = "맑은 고딕"


def rgb(h):
    h = h.lstrip("#"); return RGBColor(int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16))


def text(slide, x, y, w, h, s, size=20, color=NAVY, bold=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(s if isinstance(s, list) else [s]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.space_after = Pt(10)
        for r in p.runs:
            r.font.size = Pt(size); r.font.name = FONT; r.font.bold = bold; r.font.color.rgb = rgb(color)
    return tb


def bullets(slide, x, y, w, h, items, size=20):
    return text(slide, x, y, w, h, ["•  " + it for it in items], size=size)


def header(slide, title, tag=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
    bar.fill.solid(); bar.fill.fore_color.rgb = rgb(NAVY); bar.line.fill.background()
    if tag:
        text(slide, 0.6, 0.35, 6, 0.4, tag, size=13, color=ACCENT, bold=True)
    text(slide, 0.6, 0.65, 12, 0.9, title, size=30, bold=True)


def footer(slide, n):
    text(slide, 0.6, 7.0, 8, 0.3, "확률과 통계 · 1주차 순열과 조합", size=10, color=GRAY)
    text(slide, 12.0, 7.0, 0.8, 0.3, str(n), size=10, color=GRAY)


def pic(slide, path, x, y, w=None, h=None):
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)


def photo(slide, name, x, y, w, h):
    """비유 사진 + 하단 출처 표기"""
    pic(slide, crop_to(name, w, h), x, y, w, h)
    text(slide, x, y + h + 0.02, w, 0.3, CREDITS[name], size=9, color=GRAY)


def movie(slide, scene, x, y, w):
    """manim 영상 삽입 (클릭 재생, 포스터는 마지막 장면)"""
    h = w * 9 / 16
    slide.shapes.add_movie(os.path.join(ANIM, scene + ".mp4"), Inches(x), Inches(y), Inches(w), Inches(h),
                           poster_frame_image=os.path.join(ANIM, scene + "_poster.png"), mime_type="video/mp4")
    text(slide, x, y + h + 0.02, w, 0.3, "▶ 클릭하여 애니메이션 재생", size=10, color=GRAY)


def box(slide, x, y, w, h, title, body, color=ACCENT, size=24):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = rgb(LIGHT); s.line.color.rgb = rgb(color); s.line.width = Pt(2)
    s.adjustments[0] = 0.08
    text(slide, x + 0.25, y + 0.15, w - 0.5, 0.5, title, size=16, color=color, bold=True)
    text(slide, x + 0.25, y + 0.65, w - 0.5, h - 0.8, body, size=size, bold=True)


def analogy_tag(slide):
    t = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.9), Inches(0.4), Inches(1.8), Inches(0.5))
    t.fill.solid(); t.fill.fore_color.rgb = rgb(GOLD); t.line.fill.background()
    tf = t.text_frame; tf.text = "일상 속 비유"
    r = tf.paragraphs[0].runs[0]; r.font.size = Pt(14); r.font.bold = True; r.font.name = FONT; r.font.color.rgb = rgb("#FFFFFF")


n = 0
def new():
    global n; n += 1
    return prs.slides.add_slide(BLANK)

# 1 표지
s = new()
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = rgb(NAVY); bg.line.fill.background()
text(s, 0.9, 2.2, 6, 0.6, "확률과 통계 · 1주차", size=20, color=GOLD, bold=True)
text(s, 0.9, 2.9, 6, 1.2, "여러 가지 순열", size=48, color="#FFFFFF", bold=True)
text(s, 0.9, 4.1, 6, 0.6, "원순열과 중복순열", size=24, color="#DDE3EA")
pic(s, crop_to("비유_회전목마.jpg", 5.6, 7.5), 7.733, 0, 5.6, 7.5)

# 2 인트로 영상 (AI 생성, 전체 화면)
s = new()
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = rgb("#000000"); bg.line.fill.background()
s.shapes.add_movie(os.path.join(IMG, "ai_flow", "intro_회전목마_자물쇠.mp4"), 0, 0, prs.slide_width, prs.slide_height,
                   poster_frame_image=os.path.join(IMG, "ai_flow", "intro_poster.png"), mime_type="video/mp4")
text(s, 0.4, 7.05, 8, 0.3, "▶ 클릭하여 재생 · " + CREDITS["ai_flow/intro_회전목마_자물쇠.mp4"], size=10, color="#DDE3EA")
s.notes_slide.notes_text_frame.text = "도입 질문\n회전목마가 돌아도 변하지 않는 것: 말들의 순서\n자물쇠 다이얼: 같은 숫자의 반복 가능\n→ 오늘의 두 주제, 원순열과 중복순열"

# 3 학습목표
s = new(); header(s, "학습목표"); footer(s, n)
bullets(s, 0.8, 1.9, 7.4, 2.4, ["원순열의 뜻과 그 수 (n−1)!의 유도",
                                "중복순열의 뜻과 그 수 nʳ의 계산",
                                "링 네트워크, 디지털 비밀번호 등 공학 문제에의 적용"], size=20)
photo(s, "ai_flow/AI_학습목표.jpg", 8.5, 1.6, 4.3, 2.4)
pic(s, figs["summary"], 0.8, 4.3, w=8.2)

# 3 비유: 회전목마
s = new(); header(s, "회전목마의 말 배치", "개념 1 · 원순열"); analogy_tag(s); footer(s, n)
photo(s, "비유_회전목마.jpg", 0.6, 1.6, 6.6, 4.95)
bullets(s, 7.5, 1.9, 5.5, 4.5, ["회전목마가 한 바퀴 도는 동안 바뀌는 것: 말의 위치",
                                "바뀌지 않는 것: 말들의 앞뒤 순서",
                                "따라서 회전만 다른 배치는 같은 배치",
                                "기준점(시작점)이 없는 배열 = 원순열"], size=19)

# 4 동기: 링 네트워크
s = new(); header(s, "공학 속 원형 배열: 링 네트워크", "개념 1 · 원순열"); footer(s, n)
photo(s, "ai_flow/AI_링센서.jpg", 0.6, 1.6, 6.6, 3.7)
bullets(s, 7.5, 1.8, 5.5, 2.8, ["센서 6개를 원형 통신 링에 연결하는 상황",
                                "전체 회전 시에도 이웃 관계는 동일",
                                "회전만 다른 배치는 같은 배치로 취급",
                                "핵심 질문: 서로 다른 배치의 개수"], size=18)
pic(s, figs["ring"], 9.4, 4.4, h=2.5)

# 5 원순열 정의 (애니)
s = new(); header(s, "원순열: 회전하여 일치하면 같은 배열", "개념 1 · 원순열"); footer(s, n)
movie(s, "Rotation", 0.6, 1.5, 8.4)
box(s, 9.3, 1.9, 3.5, 2.6, "원순열의 정의", "서로 다른 것을 원 모양으로 배열하는 순열", size=20)

# 6 원순열 수 유도 (애니)
s = new(); header(s, "원순열의 수: 일렬 배열 ÷ 회전 중복", "개념 1 · 원순열"); footer(s, n)
movie(s, "Grouping", 0.6, 1.5, 8.4)
bullets(s, 9.3, 1.8, 3.7, 2.2, ["일렬 배열의 수: n!", "같은 원형 배열: n개씩 중복"], size=17)
box(s, 9.3, 3.9, 3.5, 1.7, "원순열의 수", "n!/n = (n−1)!")

# 7 한 자리 고정 (애니)
s = new(); header(s, "다른 관점: 한 자리 고정", "개념 1 · 원순열"); footer(s, n)
movie(s, "FixedSeat", 0.6, 1.5, 8.4)
bullets(s, 9.3, 1.8, 3.7, 4.5, ["회전 자유도 제거를 위한 기준점 고정",
                                "나머지 n−1개의 일렬 배열 문제로 환원",
                                "회전목마의 '1번 말' 지정과 같은 원리"], size=19)

# 8 예제 (사진 + 애니)
s = new(); header(s, "예제: 부모가 이웃하는 원형 식탁", "예제 1"); footer(s, n)
photo(s, "ai_flow/AI_원탁토론.jpg", 0.6, 1.6, 3.9, 2.9)
text(s, 0.6, 4.9, 3.9, 1.8, ["부모를 포함한 6명 가족", "원형 식탁 착석", "부모가 이웃하는 방법의 수"], size=17, color=NAVY)
movie(s, "Example", 4.8, 1.5, 8.0)

# 9 비유: 번호 자물쇠
s = new(); header(s, "번호 자물쇠의 비밀번호", "개념 2 · 중복순열"); analogy_tag(s); footer(s, n)
photo(s, "비유_번호자물쇠.jpg", 0.6, 1.6, 6.6, 4.95)
bullets(s, 7.5, 1.9, 5.5, 4.5, ["다이얼 3개, 각 다이얼 0~9의 10가지",
                                "같은 숫자 반복 가능 (예: 777)",
                                "각 다이얼의 독립적 선택: 10 × 10 × 10",
                                "가능한 비밀번호: 10³ = 1000개"], size=19)

# 10 중복순열 (애니)
s = new(); header(s, "중복순열: 같은 것의 반복 선택 허용", "개념 2 · 중복순열"); footer(s, n)
movie(s, "Bits", 0.6, 1.5, 8.4)
box(s, 9.3, 1.9, 3.5, 2.9, "중복순열의 수", "n개에서 중복 허용 r개 택하기\nₙΠᵣ = nʳ", color=TEAL, size=20)

# 11 비유: 주사위
s = new(); header(s, "주사위를 여러 번 던지기", "개념 2 · 중복순열"); analogy_tag(s); footer(s, n)
photo(s, "비유_주사위.jpg", 0.6, 1.6, 6.6, 4.95)
bullets(s, 7.5, 1.9, 5.5, 4.5, ["주사위 1번: 6가지 눈",
                                "같은 눈의 반복 가능 → 중복순열",
                                "3번 던질 때 눈의 순서쌍: 6³ = 216",
                                "실험 반복 횟수 r에 따른 지수적 증가"], size=19)

# 12 공학 적용 (애니)
s = new(); header(s, "공학 적용: 비밀번호 공간의 크기", "개념 2 · 중복순열"); footer(s, n)
movie(s, "Growth", 0.6, 1.5, 8.4)
bullets(s, 9.3, 1.5, 3.8, 2.8, ["OTP 6자리 숫자: 10⁶ = 100만",
                                "8비트: 2⁸ = 256",
                                "영문+숫자 8자리: 62⁸ ≈ 2.2×10¹⁴",
                                "자릿수 증가에 따른 지수적 증가"], size=15)
photo(s, "ai_flow/AI_OTP.jpg", 9.3, 4.5, 3.6, 2.0)

# 13 요약
s = new(); header(s, "정리: 세 가지 순열 비교"); footer(s, n)
pic(s, figs["summary"], 0.6, 1.7, w=8.3)
photo(s, "ai_flow/AI_주사위.jpg", 9.2, 1.7, 3.6, 2.4)
bullets(s, 0.8, 4.9, 12, 1.5, ["원순열: 회전하여 같은 것 제거 → n으로 나눔",
                               "중복순열: 각 자리의 독립적 선택 → n을 r번 곱함"], size=20)

# 14 확인 문제
s = new(); header(s, "확인 문제"); footer(s, n)
photo(s, "비유_관람차.jpg", 0.6, 1.6, 4.2, 3.15)
box(s, 5.2, 1.6, 7.5, 1.9, "문제 1  원순열", "서로 다른 8색으로 관람차 8칸 색칠하는 방법의 수", color=NAVY, size=20)
box(s, 5.2, 3.8, 7.5, 1.9, "문제 2  중복순열", "0~9 숫자 4자리 PIN의 개수", color=TEAL, size=20)
s.notes_slide.notes_text_frame.text = "정답\n문제 1: (8−1)! = 5040\n문제 2: 10⁴ = 10000"

prs.save(OUT)
print("saved", OUT, n, "slides")
