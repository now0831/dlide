---
name: lecture-slides
description: 차시별 강의자료(pptx) 제작. 교과서 PDF를 읽고, manim 애니메이션과 자유 라이선스 비유 사진을 넣은 슬라이드를 만든다. "N주차 만들어줘", "강의자료 만들어", "슬라이드 만들어" 요청 시 사용. 인자: 차시 번호 (예: 2)
---

# 강의자료 제작 스킬

프로젝트 루트(`dlide/`)의 `CLAUDE.md`, `00_guide/style.md`가 **내용과 스타일의 기준**이다. 이 스킬은 **제작 절차와 도구**를 담는다. 둘이 충돌하면 CLAUDE.md가 우선.

완성 예시: `lectures/week01/` (anim_scenes.py, make_slides.py) → `output/week01_순열.pptx`

## 0. 준비
- 인자로 받은 차시 번호 N → 작업 폴더 `lectures/weekNN/` (없으면 생성, `outline.md` 템플릿 복사)
- `CLAUDE.md`, `00_guide/style.md`, `lectures/weekNN/outline.md` 읽기
- outline이 비어 있으면: 교과서 목차 기준으로 이번 차시 범위를 제안하고 사용자 확인 후 진행
- 필요한 패키지 확인 (없으면 설치): `python -m pip install -q pymupdf python-pptx matplotlib manim pillow av`

## 1. 교과서 읽기
교과서 PDF는 한글 텍스트 추출이 깨짐 → **페이지를 이미지로 렌더링해서 Read로 본다.**
```
python -I .claude/skills/lecture-slides/scripts/render_pdf.py "<pdf>" <scratchpad>/textbook --pages 4-12 --dpi 100
```
- 개념 정의, 공식, 예제, 문제 번호와 쪽수를 메모 (`lectures/weekNN/notes.md`)
- 내용과 순서는 교과서를 따름. 공대 1학년 대상이므로 공학 예시를 추가

## 2. 슬라이드 설계
아래 흐름으로 12~16장 구성 (style.md 우선):
표지 → 학습목표 → [개념마다: 비유 사진 슬라이드 → 공학 동기 → 정의(애니) → 공식 유도(애니)] → 예제(애니) → 공학 적용(애니) → 정리 → 확인 문제(정답은 발표자 노트)

- **말투: 모든 제목과 bullet을 명사로 끝맺음** ("~다/~요" 금지)
- 슬라이드당 bullet 최대 4개
- 개념마다 비유 사진 1장 이상, 그래프와 도식은 manim 애니메이션

## 3. manim 애니메이션
- `lectures/weekNN/anim_scenes.py` 작성. 공통 요소는 `from anim_kit import *` (스크립트 폴더를 sys.path에 추가):
  ```python
  import sys; sys.path.insert(0, r"<dlide>/.claude/skills/lecture-slides/scripts")
  from anim_kit import *   # manim + T(), node(), ring_pos(), 팔레트(NAVY, ACCENT, TEAL, GOLD, GRAY, PALETTE)
  ```
- **LaTeX 없음** → `MathTex`, `Tex`, `DecimalNumber`, `include_numbers=True`, `LogBase` 사용 금지. 모든 글자는 `T()`(맑은 고딕 Text). 축 눈금 숫자는 `T()`로 직접 배치
- 위첨자/아래첨자는 유니코드(², ⁸, ₙ, ᵣ) 사용 가능
- 배경 흰색, 장면당 10~15초, 마지막 장면이 결론이 되게 (포스터 이미지로 쓰임)
- 화면 밖으로 잘리는 글자 주의: 가로 ±6.5, 세로 ±3.6 안쪽
- 렌더 (scratchpad에 출력):
  ```
  python -I -m manim -qm --disable_caching --media_dir <scratchpad>/manim_media anim_scenes.py <Scene>
  ```
- 영상 복사 + 포스터 생성 + 점검용 프레임 시트:
  ```
  python -I .claude/skills/lecture-slides/scripts/collect_anim.py <scratchpad>/manim_media/videos/anim_scenes/720p30 lectures/weekNN/anim --sheet <scratchpad>/anim_check.png
  ```
  → `anim_check.png`를 Read로 보고 겹침과 잘림을 확인한 뒤 고쳐서 다시 렌더

## 4. 비유 사진 (인터넷 검색)
**자유 이용 라이선스만 사용** (CC0, PDM, CC BY, CC BY-SA). Openverse API 사용.
```
# 검색 + 후보 다운로드 + 후보 시트
python -I .claude/skills/lecture-slides/scripts/find_images.py search <scratchpad>/img "carousel" "combination lock" --n 6
# → <scratchpad>/img/sheet.png 를 Read로 보고 고르기
# 선택 사진을 프로젝트로 복사 + 출처 기록 (credits.md, credits.json에 누적)
python -I .claude/skills/lecture-slides/scripts/find_images.py pick <scratchpad>/img 01_source/이미지_도표 \
    carousel_cb8246cd.jpg=비유_회전목마.jpg:원순열 dice_188a9a60.jpg=비유_주사위.jpg:중복순열
```
- 검색어는 영어. 일상에서 바로 떠오르는 장면 위주로 고른다 (사람 얼굴이 크게 나오거나, 브랜드 로고가 주인공이거나, 글자가 많은 사진은 피함)
- 이미 `01_source/이미지_도표/`에 있는 사진은 재사용

## 5. 슬라이드 생성
`lectures/weekNN/make_slides.py` 작성. 헬퍼는 `slidekit` 사용:
```python
import sys; sys.path.insert(0, r"<dlide>/.claude/skills/lecture-slides/scripts")
from slidekit import Deck
d = Deck(root=r"<dlide>", week=N, course_label="확률과 통계 · N주차 <주제>", anim_dir=..., fig_dir=...)
s = d.cover("확률과 통계 · N주차", "제목", "부제", photo="비유_회전목마.jpg")
s = d.slide("제목", tag="개념 1 · 원순열")         # 헤더 + 푸터 + 쪽번호
d.bullets(s, x, y, w, h, [...], size=20)
d.box(s, x, y, w, h, "박스 제목", "본문", color=d.ACCENT)
d.photo(s, "비유_회전목마.jpg", x, y, w, h)         # 비율 맞춰 자르기 + 출처 자동 표기
d.analogy_tag(s)                                     # "일상 속 비유" 배지
d.movie(s, "Rotation", x, y, w)                      # anim/Rotation.mp4 + 포스터, 클릭 재생
d.notes(s, "정답 ...")
d.save("output/weekNN_<주제>.pptx")
```
- 레이아웃 기준 (13.333 x 7.5 in): 영상 `movie(s, name, 0.6, 1.5, 8.4)` + 오른쪽 열 x=9.3, w≈3.6. 사진 슬라이드: 사진 (0.6, 1.6, 6.6, 4.95) + bullets x=7.5, w=5.5, size 19

## 6. 점검 (필수)
```
powershell -File .claude/skills/lecture-slides/scripts/export_check.ps1 -Pptx "output/weekNN_<주제>.pptx" -Out <scratchpad>/render
```
- PowerPoint로 슬라이드를 PNG로 내보내고 `grid.png`를 생성. **사용자가 PowerPoint를 켜 둔 경우 종료하지 않음** (스크립트가 처리)
- `grid.png`를 Read로 보고 점검: 글자 넘침, 어색한 줄바꿈, 겹침, 명사 종결 위반, 출처 누락 → 고쳐서 다시 생성

## 7. 마무리
- `output/weekNN_<주제>.pptx` 저장, 작업 파일은 `lectures/weekNN/`에
- 사용자에게 보고: 슬라이드 구성 표, 애니메이션 목록, 사용 사진과 라이선스, 점검하지 못한 부분
- 사용자 피드백은 `CLAUDE.md`의 "누적 피드백"에 규칙으로 추가
