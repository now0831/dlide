"""Openverse에서 자유 라이선스 이미지 검색/선택.

search: python -I find_images.py search <work_dir> "query 1" "query 2" [--n 6]
        -> <work_dir>/raw/*.jpg, meta.json, sheet.png (후보 미리보기)
pick:   python -I find_images.py pick <work_dir> <dest_dir> raw_name.jpg=새이름.jpg:용도 ...
        -> dest_dir에 복사, credits.md / credits.json 누적 기록
"""
import argparse, json, os, sys, urllib.parse, urllib.request
from PIL import Image, ImageDraw

LICENSES = "cc0,pdm,by,by-sa"  # 자유 이용 라이선스만
UA = {"User-Agent": "Mozilla/5.0 (lecture-material)"}
FIELDS = ("title", "creator", "creator_url", "license", "license_version", "license_url", "foreign_landing_url", "source")


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


def search(work, queries, n):
    raw = os.path.join(work, "raw"); os.makedirs(raw, exist_ok=True)
    mp = os.path.join(work, "meta.json")
    meta = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    for q in queries:
        url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
            dict(q=q, license=LICENSES, page_size=n, mature="false"))
        results = json.loads(get(url))["results"]
        key = q.replace(" ", "_")
        for r in results[:n]:
            name = f"{key}_{r['id'][:8]}.jpg"
            try:
                open(os.path.join(raw, name), "wb").write(get(r["url"]))
                Image.open(os.path.join(raw, name)).verify()
                meta[name] = {k: r.get(k) for k in FIELDS}
                print("ok  ", name, r["license"], (r.get("title") or "")[:40])
            except Exception as e:
                print("fail", name, e)
                if os.path.exists(os.path.join(raw, name)):
                    os.remove(os.path.join(raw, name))
    json.dump(meta, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    files = sorted(f for f in os.listdir(raw) if f in meta)
    W, H, cols = 320, 240, 4
    g = Image.new("RGB", (W * cols, (H + 20) * ((len(files) + cols - 1) // cols)), "white"); dr = ImageDraw.Draw(g)
    for i, f in enumerate(files):
        im = Image.open(os.path.join(raw, f)).convert("RGB"); im.thumbnail((W, H))
        x, y = (i % cols) * W, (i // cols) * (H + 20)
        g.paste(im, (x, y)); dr.text((x + 4, y + H + 4), f[:48], fill="black")
    g.save(os.path.join(work, "sheet.png"))
    print("sheet ->", os.path.join(work, "sheet.png"))


def lic_label(m):
    if m["license"] in ("cc0", "pdm"):
        return m["license"].upper()
    return f"CC {m['license'].upper()} {m['license_version']}"


def pick(work, dest, specs):
    meta = json.load(open(os.path.join(work, "meta.json"), encoding="utf-8"))
    os.makedirs(dest, exist_ok=True)
    cj = os.path.join(dest, "credits.json"); cm = os.path.join(dest, "credits.md")
    credits = json.load(open(cj, encoding="utf-8")) if os.path.exists(cj) else {}
    if not os.path.exists(cm):
        open(cm, "w", encoding="utf-8").write("# 이미지 출처 (자유 이용 라이선스)\n\n| 파일 | 용도 | 원제목 | 작성자 | 라이선스 | 원본 |\n|---|---|---|---|---|---|\n")
    for spec in specs:
        src, rest = spec.split("=", 1)
        dst, use = (rest.split(":", 1) + [""])[:2]
        m = meta[src]
        Image.open(os.path.join(work, "raw", src)).convert("RGB").save(os.path.join(dest, dst), quality=92)
        credits[dst] = f"사진: {m['creator']} / {lic_label(m)} / {m['source']}"
        with open(cm, "a", encoding="utf-8") as f:
            f.write(f"| {dst} | {use} | {m['title']} | {m['creator']} | [{lic_label(m)}]({m['license_url']}) | [{m['source']}]({m['foreign_landing_url']}) |\n")
        print(dst, "|", credits[dst])
    json.dump(credits, open(cj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("work"); s.add_argument("queries", nargs="+"); s.add_argument("--n", type=int, default=6)
    p = sub.add_parser("pick"); p.add_argument("work"); p.add_argument("dest"); p.add_argument("specs", nargs="+")
    a = ap.parse_args()
    search(a.work, a.queries, a.n) if a.cmd == "search" else pick(a.work, a.dest, a.specs)
