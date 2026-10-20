"""PDF 페이지를 PNG로 렌더링 (한글 텍스트 추출이 깨지는 교과서용).
사용: python -I render_pdf.py <pdf> <out_dir> [--pages 4-12] [--dpi 100]
"""
import argparse, os
import pymupdf

ap = argparse.ArgumentParser()
ap.add_argument("pdf"); ap.add_argument("out")
ap.add_argument("--pages", help="1부터 시작, 예: 4-12 또는 3,5,7")
ap.add_argument("--dpi", type=int, default=100)
a = ap.parse_args()

doc = pymupdf.open(a.pdf)
if a.pages:
    pages = []
    for part in a.pages.split(","):
        if "-" in part:
            s, e = part.split("-"); pages += range(int(s), int(e) + 1)
        else:
            pages.append(int(part))
else:
    pages = range(1, len(doc) + 1)
os.makedirs(a.out, exist_ok=True)
for p in pages:
    if 1 <= p <= len(doc):
        doc[p - 1].get_pixmap(dpi=a.dpi).save(os.path.join(a.out, f"p{p:03d}.png"))
print(f"{len(doc)} pages total, rendered {len(list(pages))} -> {a.out}")
