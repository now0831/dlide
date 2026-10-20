"""1주차 애니메이션 (manim). 렌더: python -m manim -qm anim_scenes.py <Scene>"""
from itertools import permutations
import math
from manim import *

FONT = "Malgun Gothic"
NAVY, ACCENT, TEAL, GOLD, GRAY = "#1F3A5F", "#E4572E", "#2A9D8F", "#F4A261", "#8D99AE"
PURPLE, SLATE = "#9B5DE5", "#577590"
PALETTE = [ACCENT, GOLD, NAVY, TEAL, PURPLE, SLATE]
COL = dict(zip("ABCD", PALETTE))

config.background_color = WHITE


def T(s, size=36, color=NAVY, weight=NORMAL):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


def node(label, color, r=0.38, size=30):
    c = Circle(radius=r, fill_color=color, fill_opacity=1, stroke_color=WHITE, stroke_width=4)
    return VGroup(c, T(label, size, WHITE, BOLD).move_to(c))


def ring_pos(n, radius, center=ORIGIN, start=PI / 2):
    return [center + radius * np.array([math.cos(start - TAU * i / n), math.sin(start - TAU * i / n), 0]) for i in range(n)]


class Rotation(Scene):
    """회전하여 일치하면 같은 원형 배열"""
    def construct(self):
        title = T("원 모양 배열: 회전해도 같은 배열", 40, weight=BOLD).to_edge(UP)
        circ = Circle(radius=1.8, stroke_color=GRAY, stroke_width=6)
        pos = ring_pos(4, 1.8)
        nodes = VGroup(*[node(ch, COL[ch]).move_to(p) for ch, p in zip("ABCD", pos)])
        wheel = VGroup(circ, nodes).shift(LEFT * 3.2)
        self.play(FadeIn(title), Create(circ))
        self.play(LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.2))

        readings = ["A B C D", "D A B C", "C D A B", "B C D A"]
        table_title = T("위에서부터 시계 방향 읽기", 26, GRAY).move_to(RIGHT * 2.4 + UP * 2.0)
        rows = VGroup()
        self.play(FadeIn(table_title))
        for k, rd in enumerate(readings):
            row = VGroup(*[T(ch, 34, COL[ch], BOLD) for ch in rd.split()]).arrange(RIGHT, buff=0.35)
            row.move_to(RIGHT * 2.4 + UP * (1.2 - k * 0.8))
            rows.add(row)
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.6)
            if k < 3:
                # 시계 방향으로 한 칸씩 (글자는 똑바로 유지)
                targets = [nodes[(j + 1) % 4].get_center() for j in range(4)]
                self.play(*[n.animate(path_arc=-PI / 2).move_to(t) for n, t in zip(nodes, targets)], run_time=1.0)
        brace = Brace(rows, RIGHT, color=ACCENT)
        lab = T("모두 같은\n원형 배열", 28, ACCENT, BOLD).next_to(brace, RIGHT)
        self.play(GrowFromCenter(brace), FadeIn(lab))
        concl = T("일렬 배열 4가지  →  원형 배열 1가지", 34, NAVY, BOLD).to_edge(DOWN, buff=0.5)
        self.play(Write(concl))
        self.wait(1.5)


class Grouping(Scene):
    """4! = 24가지 일렬 배열을 4개씩 묶어 6가지 원순열"""
    def construct(self):
        title = T("원순열의 수: 일렬 배열을 회전 묶음으로 나누기", 36, weight=BOLD).to_edge(UP)
        self.play(FadeIn(title))
        groups = {}
        for p in permutations("ABCD"):
            s = "".join(p); i = s.index("A")
            groups.setdefault(s[i:] + s[:i], []).append(s)
        allperms = [s for g in groups.values() for s in g]
        # 1) 24개를 섞인 순서(사전순)로 먼저 보여주기
        lex = sorted(allperms)
        mobs = {s: Text(s, font="Consolas", font_size=26, color=NAVY) for s in lex}
        grid = VGroup(*[mobs[s] for s in lex]).arrange_in_grid(rows=4, cols=6, buff=(0.55, 0.45)).shift(DOWN * 0.2)
        self.play(LaggedStart(*[FadeIn(m) for m in grid], lag_ratio=0.04), run_time=2)
        cnt = T("일렬 배열 4! = 24가지", 30, GRAY).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(cnt)); self.wait(0.5)
        # 2) 회전 묶음별로 재배치
        targets = []
        for gi, (key, mem) in enumerate(groups.items()):
            for mi, s in enumerate(mem):
                targets.append((s, LEFT * 4.6 + RIGHT * mi * 1.55 + UP * (2.0 - gi * 0.78), PALETTE[gi]))
        self.play(*[mobs[s].animate.move_to(p).set_color(c) for s, p, c in targets], run_time=2)
        boxes, labels = VGroup(), VGroup()
        for gi, key in enumerate(groups):
            y = 2.0 - gi * 0.78
            b = RoundedRectangle(width=6.0, height=0.62, corner_radius=0.12, stroke_color=PALETTE[gi], fill_color=PALETTE[gi], fill_opacity=0.12).move_to(LEFT * 2.3 + UP * y)
            arr = Arrow(RIGHT * 0.9 + UP * y, RIGHT * 2.1 + UP * y, color=PALETTE[gi], buff=0, stroke_width=5)
            lb = T(f"원형 {gi + 1}", 28, PALETTE[gi], BOLD).next_to(arr, RIGHT)
            boxes.add(b); labels.add(VGroup(arr, lb))
        self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.1))
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.2) for l in labels], lag_ratio=0.15))
        res = T("24 ÷ 4 = 6     일반화: n! ÷ n = (n−1)!", 32, ACCENT, BOLD).to_edge(DOWN, buff=0.5)
        self.play(Transform(cnt, res))
        self.wait(1.5)


class FixedSeat(Scene):
    """한 자리를 고정하면 나머지는 일렬 배열"""
    def construct(self):
        title = T("한 자리 고정: 나머지는 일렬 배열 문제", 38, weight=BOLD).to_edge(UP)
        self.play(FadeIn(title))
        R = 2.0; c0 = LEFT * 2.8 + DOWN * 0.4
        circ = Circle(radius=R, stroke_color=GRAY, stroke_width=6).move_to(c0)
        pos = ring_pos(5, R, c0)
        seats = VGroup(*[Circle(radius=0.42, stroke_color=GRAY, stroke_width=4).move_to(p) for p in pos])
        self.play(Create(circ), LaggedStart(*[Create(s) for s in seats], lag_ratio=0.1))
        a = node("A", ACCENT, 0.42, 30).move_to(pos[0])
        pin = T("고정", 26, ACCENT, BOLD).next_to(a, UP, buff=0.1)
        self.play(GrowFromCenter(a), FadeIn(pin))
        self.play(Indicate(a, color=ACCENT))
        expr = VGroup().move_to(RIGHT * 3.2 + UP * 0.8)
        names = ["B", "C", "D", "E"]
        choices = ["4", "3", "2", "1"]
        terms = VGroup()
        for i, (nm, ch) in enumerate(zip(names, choices)):
            q = node("?", GRAY, 0.42, 30).move_to(pos[i + 1])
            tag = T(f"{ch}가지", 24, TEAL, BOLD).next_to(q, (pos[i + 1] - c0) / R, buff=0.15)
            self.play(FadeIn(q), FadeIn(tag), run_time=0.5)
            terms.add(T(ch, 44, TEAL, BOLD))
        eq = VGroup(terms[0], T("×", 40, GRAY), terms[1], T("×", 40, GRAY), terms[2], T("×", 40, GRAY), terms[3]).arrange(RIGHT, buff=0.25)
        eq.move_to(RIGHT * 3.3 + UP * 0.6)
        self.play(Write(eq))
        res = T("= 4! = 24", 44, ACCENT, BOLD).next_to(eq, DOWN, buff=0.5)
        self.play(Write(res))
        gen = T("n개 원순열 = (n−1)개 일렬 배열 = (n−1)!", 30, NAVY, BOLD).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(gen, shift=UP * 0.2))
        self.wait(1.5)


class Example(Scene):
    """부모가 이웃하는 6명 원순열 = 4! × 2! = 48"""
    def construct(self):
        title = T("예제: 부모가 이웃하는 원형 식탁", 38, weight=BOLD).to_edge(UP)
        self.play(FadeIn(title))
        R = 1.9; c0 = LEFT * 3.3 + DOWN * 0.3
        circ = Circle(radius=R, stroke_color=GRAY, stroke_width=6).move_to(c0)
        pos6 = ring_pos(6, R, c0)
        labels = ["부", "모", "C1", "C2", "C3", "C4"]
        cols = [ACCENT, GOLD, NAVY, NAVY, NAVY, NAVY]
        ppl = [node(l, c, 0.42, 24 if len(l) > 1 else 30).move_to(p) for l, c, p in zip(labels, cols, pos6)]
        self.play(Create(circ), LaggedStart(*[GrowFromCenter(p) for p in ppl], lag_ratio=0.1))
        # 1) 부모를 하나로 묶기
        bundle = RoundedRectangle(width=1.9, height=1.0, corner_radius=0.45, stroke_color=ACCENT, stroke_width=5)
        pos5 = ring_pos(5, R, c0)
        step1 = T("① 부모를 한 묶음으로", 30, ACCENT, BOLD).move_to(RIGHT * 2.8 + UP * 2.0)
        self.play(FadeIn(step1))
        pair = VGroup(ppl[0], ppl[1])
        self.play(pair.animate.arrange(RIGHT, buff=0.05).move_to(pos5[0]),
                  *[ppl[i].animate.move_to(pos5[i - 1]) for i in range(2, 6)], run_time=1.5)
        bundle.move_to(pair)
        self.play(Create(bundle))
        e1 = T("5개 원순열: (5−1)! = 24", 32, NAVY).next_to(step1, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(Write(e1))
        # 2) 묶음 안 자리 바꾸기
        step2 = T("② 묶음 안 자리 바꿈", 30, ACCENT, BOLD).next_to(e1, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(FadeIn(step2))
        self.play(Swap(ppl[0], ppl[1]), run_time=0.8)
        self.play(Swap(ppl[0], ppl[1]), run_time=0.8)
        e2 = T("2! = 2", 32, NAVY).next_to(step2, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(Write(e2))
        res = T("24 × 2 = 48", 48, ACCENT, BOLD).next_to(e2, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(Write(res), Circumscribe(res, color=ACCENT))
        self.wait(1.5)


class Bits(Scene):
    """8비트: 각 자리 2가지, 2^8 = 256"""
    def construct(self):
        title = T("중복순열: 각 자리 선택이 독립적으로 반복", 38, weight=BOLD).to_edge(UP)
        self.play(FadeIn(title))
        boxes = VGroup(*[RoundedRectangle(width=1.1, height=1.1, corner_radius=0.15, stroke_color=NAVY, stroke_width=4) for _ in range(8)]).arrange(RIGHT, buff=0.3).shift(UP * 0.8)
        self.play(LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.08))
        counter_lab = T("가능한 경우의 수", 28, GRAY).move_to(DOWN * 1.2 + LEFT * 2.5)
        counter = T("1", 52, ACCENT, BOLD).next_to(counter_lab, RIGHT, buff=0.5)
        prod = T("", 30, NAVY)
        self.play(FadeIn(counter_lab), FadeIn(counter))
        bits = "10110010"
        total = 1
        for i, b in enumerate(bits):
            box = boxes[i]
            d0 = T("0", 44, NAVY, BOLD).move_to(box)
            d1 = T("1", 44, NAVY, BOLD).move_to(box)
            self.play(FadeIn(d0), run_time=0.15)
            self.play(Transform(d0, d1), run_time=0.15)
            final = T(b, 44, WHITE if b == "1" else NAVY, BOLD).move_to(box)
            self.play(box.animate.set_fill(NAVY if b == "1" else WHITE, 1), Transform(d0, final), run_time=0.2)
            tag = T("2가지", 22, ACCENT).next_to(box, DOWN, buff=0.15)
            total *= 2
            new_c = T(f"{total}", 52, ACCENT, BOLD).move_to(counter, aligned_edge=LEFT)
            new_p = T(" × ".join(["2"] * (i + 1)), 30, NAVY).move_to(DOWN * 2.2)
            self.play(FadeIn(tag), Transform(counter, new_c), Transform(prod, new_p), run_time=0.35)
        res = T("2를 8번 곱함 = 2⁸ = 256        일반화: ₙΠᵣ = nʳ", 34, ACCENT, BOLD).to_edge(DOWN, buff=0.4)
        self.play(Write(res))
        self.wait(1.5)


class Growth(Scene):
    """자릿수에 따른 경우의 수 nʳ의 폭발적 증가 (로그 눈금)"""
    def construct(self):
        title = T("비밀번호 공간의 크기: 자릿수에 따른 지수적 증가", 34, weight=BOLD).to_edge(UP)
        self.play(FadeIn(title))
        ax = Axes(x_range=[0, 8.5, 1], y_range=[0, 15, 2], x_length=8.5, y_length=4.9,
                  axis_config=dict(color=GRAY, stroke_width=3, include_tip=False)).shift(LEFT * 1.6 + DOWN * 0.4)
        ylab = {0: "1", 2: "100", 4: "1만", 6: "100만", 8: "1억", 10: "100억", 12: "1조", 14: "100조"}
        yl = VGroup(*[T(v, 20, GRAY).next_to(ax.c2p(0, k), LEFT, buff=0.15) for k, v in ylab.items()])
        xl = VGroup(*[T(str(r), 22, GRAY).next_to(ax.c2p(r, 0), DOWN, buff=0.15) for r in range(1, 9)])
        xt = T("자릿수 r", 24, NAVY).next_to(ax.x_axis, DOWN, buff=0.6)
        yt = T("경우의 수 (로그 눈금)", 22, NAVY).next_to(ax.c2p(0, 15), UP, buff=0.1).align_to(yl, LEFT)
        self.play(Create(ax), FadeIn(yl), FadeIn(xl), FadeIn(xt), FadeIn(yt))
        series = [(2, GRAY, "비트 (n=2)"), (10, TEAL, "숫자 (n=10)"), (62, ACCENT, "영문+숫자 (n=62)")]
        legend = VGroup()
        for n, c, name in series:
            pts = [ax.c2p(r, r * math.log10(n)) for r in range(1, 9)]
            line = VMobject(color=c, stroke_width=6).set_points_as_corners(pts)
            dots = VGroup(*[Dot(p, color=c, radius=0.07) for p in pts])
            item = VGroup(Line(ORIGIN, RIGHT * 0.5, color=c, stroke_width=6), T(name, 22, c, BOLD)).arrange(RIGHT, buff=0.15)
            legend.add(item)
            self.play(Create(line), LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.1), run_time=1.6)
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 4.8 + UP * 1.6)
        self.play(FadeIn(legend))
        otp = DashedLine(ax.c2p(0, 6), ax.c2p(8.3, 6), color=TEAL, stroke_width=3)
        otp_dot = Dot(ax.c2p(6, 6), color=TEAL, radius=0.13)
        otp_t = T("OTP 6자리 = 100만", 24, TEAL, BOLD).move_to(RIGHT * 4.8 + DOWN * 0.3)
        self.play(Create(otp), GrowFromCenter(otp_dot), FadeIn(otp_t))
        top = Dot(ax.c2p(8, 8 * math.log10(62)), color=ACCENT, radius=0.13)
        top_t = T("영문+숫자 8자리\n≈ 218조", 24, ACCENT, BOLD).move_to(RIGHT * 4.8 + DOWN * 1.5)
        self.play(GrowFromCenter(top), FadeIn(top_t), Flash(top, color=ACCENT))
        self.wait(1.5)
