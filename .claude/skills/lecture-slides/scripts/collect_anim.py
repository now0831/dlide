"""manim 결과 mp4를 작업 폴더로 복사하고 포스터(마지막 프레임)와 점검용 시트 생성.
사용: python -I collect_anim.py <manim_720p30_dir> <dest_anim_dir> [--sheet check.png] [--only Scene1 Scene2]
"""
import argparse, os, shutil, sys
import av
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dest")
ap.add_argument("--sheet"); ap.add_argument("--only", nargs="*")
a = ap.parse_args()

os.makedirs(a.dest, exist_ok=True)
names = sorted(f[:-4] for f in os.listdir(a.src) if f.endswith(".mp4"))
if a.only:
    names = [n for n in names if n in a.only]
tiles = []
for n in names:
    dst = os.path.join(a.dest, n + ".mp4")
    shutil.copy2(os.path.join(a.src, n + ".mp4"), dst)
    frames = [f.to_image() for f in av.open(dst).decode(video=0)]
    frames[-1].save(os.path.join(a.dest, n + "_poster.png"))
    tiles += [frames[len(frames) // 2].resize((640, 360)), frames[-1].resize((640, 360))]
    print(f"{n}: {len(frames) / 30:.1f}s")
if a.sheet and tiles:
    g = Image.new("RGB", (1280, 360 * len(names)), "white")
    for i, t in enumerate(tiles):
        g.paste(t, ((i % 2) * 640, (i // 2) * 360))
    g.save(a.sheet)
    print("sheet (왼쪽: 중간 장면, 오른쪽: 마지막 장면) ->", a.sheet)
