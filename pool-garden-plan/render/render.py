"""Render the 3D gallery views (two finish proposals) with headless Chromium + three.js.

Author: AbodyStudio Limited - https://abodystudio.com/
Usage: python3 render/render.py  ->  assets/renders/<proposal>-<view>.webp
"""
import base64
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from PIL import Image  # noqa: E402
from model import (AWNING, BORNES_UV, DECK, FITTINGS, FLOOR_BREAK, FLOOR_SHALLOW, FRONT_GARDEN, HOUSE,  # noqa: E402
                   LIGHT_DEPTH, LV, NW_GARDEN_EDGE, POOL, POOL_STAIR, PROFILE, SHOWER, STAIR, STEP, TECH, WALK,
                   BREAK_X, u_drive, u_nw, u_se)

CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
OUT = os.path.join(ROOT, "assets", "renders")
W, H = 1600, 1000

PROPOSALS = {
    "a": dict(name="Proposition A - pierre beige et turquoise", wall="#e2cda6", plinth="#c39f72", coping="#efe4cf",
              deck="#d8c4a2", mosaic="#2aa9c6", frieze="#16708a", water="#1fb0cf", frame="#2a2a2a",
              rail="#b8bcc0", cushion="#f4efe6", wood="#8a6a4a", lawn="#6f9c3d"),
    "b": dict(name="Proposition B - blanc et bleu profond", wall="#f7f7f4", plinth="#6b6f73", coping="#f4f3ef",
              deck="#a3a6a8", mosaic="#1d5689", frieze="#0f3557", water="#1f6fa6", frame="#3a3f44",
              rail="#30353a", cushion="#e8ecef", wood="#5b4636", lawn="#6a9640"),
}

SUN_DAY = (0.82, 0.57)       # morning sun from the east (lights the facade and the pool)
SUN_DUSK = (-0.43, -0.90)    # low sun from WSW, behind the villa

VIEWS = [
    ("aerienne", "Vue aérienne depuis le verger", dict(pos=(11.5, 13.0, 41.0), target=(11.2, -0.6, 15.5), fov=40)),
    ("allee", "Depuis le jardin côté allée", dict(pos=(19.8, 1.25, 25.6), target=(8.5, -0.5, 16.2), fov=58)),
    ("plage", "Depuis la plage solarium", dict(pos=(5.75, 1.0, 17.75), target=(14.5, -0.8, 21.8), fov=60)),
    ("toit", "Depuis le toit-terrasse (même point que la photo)", dict(pos=(11.5, 5.6, 13.0), target=(11.5, -1.2, 27.0), fov=64)),
    ("verger", "Depuis le verger, face à la villa", dict(pos=(13.5, 0.95, 31.5), target=(11.5, 0.6, 14.0), fov=52)),
    ("nuit", "Ambiance du soir", dict(pos=(4.0, 6.0, 35.5), target=(11.5, 0.2, 14.5), fov=44, night=True)),
]


def scene_data(prop, view):
    house, pool = HOUSE, POOL
    lawn_nw = [(NW_GARDEN_EDGE, FRONT_GARDEN[0]), (pool["u0"] - WALK, FRONT_GARDEN[0]), (pool["u0"] - WALK, 26.5), (NW_GARDEN_EDGE, 26.5)]
    lawn_se = [(house["u1"], house["v0"]), (u_drive(house["v0"]), house["v0"]), (u_drive(26.5), 26.5),
               (pool["u1"] + WALK, 26.5), (pool["u1"] + WALK, DECK[1]), (house["u1"], DECK[1])]
    lawn_ne = [(pool["u0"] - WALK, pool["v1"] + WALK), (pool["u1"] + WALK, pool["v1"] + WALK), (pool["u1"] + WALK, 26.5), (pool["u0"] - WALK, 26.5)]
    drive = [(u_se(0.9), 0.9), (u_se(42.0), 42.0), (u_drive(42.0), 42.0), (u_drive(0.9), 0.9)]
    chicken = [(u_nw(14.0) + 0.3, 14.0), (NW_GARDEN_EDGE, 14.0), (NW_GARDEN_EDGE, 30.0), (u_nw(30.0) + 0.3, 30.0)]
    b = {n: (u, v) for n, u, v in BORNES_UV}
    trees = [(2, 35.5, 1.1), (8.5, 36, 1.0), (12, 32, 1.15), (17, 31, 1.0), (21, 34, 1.1), (4, 40, 1.0), (9, 39, 1.2),
             (14, 38, 1.0), (19, 40, 1.1), (0, 46, 1.0), (6, 45, 1.1), (11, 44, 1.0), (16, 45, 1.15), (21, 46, 1.0),
             (1, 28, 0.9), (20, 28.5, 0.9), (-1, 9, 1.0), (2, 6, 1.1), (3, 11, 0.9), (24, 44, 1.0), (7, 49, 1.0), (15, 50, 1.1)]
    return dict(
        width=W, height=H, proposal=PROPOSALS[prop], view=dict(view, night=view.get("night", False)),
        sun=SUN_DUSK if view.get("night") else SUN_DAY,
        lv=LV, house=house, stair=STAIR, pool=pool, deck=DECK, front=FRONT_GARDEN, walk=WALK, tech=TECH,
        pstair=POOL_STAIR, profile=[list(p) for p in PROFILE], step=STEP, lights=FITTINGS["lights"],
        light_depth=LIGHT_DEPTH, break_x=BREAK_X, floor_break=FLOOR_BREAK, floor_shallow=FLOOR_SHALLOW,
        awning=AWNING, shower=SHOWER,
        bornes=[(u, v) for n, u, v in BORNES_UV],
        lawns=[lawn_nw, lawn_se, lawn_ne], drive=drive, chicken=chicken,
        backyard=[(house["u0"], 0.5), (house["u1"], 0.4), (house["u1"], house["v0"]), (house["u0"], house["v0"])],
        coop=dict(u0=u_nw(26.4) + 0.5, u1=u_nw(26.4) + 2.5, v0=26.4, v1=28.4),
        hedge=[(u_drive(v) - 0.45, v) for v in [14.2 + k for k in range(12)]],
        bollards=[(u_drive(v) - 1.1, v) for v in (15.0, 19.0, 23.0)] + [(house["u0"] + 0.4, FRONT_GARDEN[1] - 0.4),
                                                                      (pool["u0"] - 1.2, pool["v1"] + 1.0), (pool["u1"] + 1.2, pool["v1"] + 1.0)],
        trees=trees, olives=[(-9.0, 8.0, 3.2), (-12.0, 30.0, 3.5), (31.0, 12.0, 3.0), (-6.0, 50.0, 3.0)],
        se_fence=[b["B4"], b["B3"]], nw_fence=[b["B11"], b["B1"]],
        neighbours=[(-32.0, -18.0, 18.0, 30.0, 4.0), (34.0, 44.0, 68.0, 76.0, 3.5)],
        windows=[dict(u=7.2, w=1.4, y=0.9, h=1.4), dict(u=AWNING["uc"], w=1.1, y=0.0, h=2.2),
                 dict(u=13.0, w=1.4, y=0.9, h=1.4), dict(u=15.6, w=1.2, y=0.9, h=1.4)],
    )


def render(prop, key, view):
    data = scene_data(prop, view)
    page = os.path.join(HERE, f"_tmp_{prop}_{key}.html")
    with open(page, "w") as fh:
        fh.write('<!doctype html><html><body style="margin:0"><canvas id="c"></canvas><pre id="out"></pre>'
                 f'<script>window.SCENE={json.dumps(data)};</script>'
                 f'<script src="file://{HERE}/three.min.js"></script><script src="file://{HERE}/scene.js"></script></body></html>')
    res = subprocess.run([CHROME, "--headless", "--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                          "--allow-file-access-from-files", "--virtual-time-budget=60000", "--dump-dom", f"file://{page}"],
                         capture_output=True, text=True, timeout=300)
    os.remove(page)
    m = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", res.stdout)
    if not m:
        raise RuntimeError(f"no image for {prop}-{key}: {res.stderr[-800:]}")
    img = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert("RGB")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{prop}-{key}.webp")
    img.save(path, "WEBP", quality=82)
    print("rendered", path, os.path.getsize(path))


if __name__ == "__main__":
    only = sys.argv[1:]
    for prop in PROPOSALS:
        for key, label, view in VIEWS:
            if only and f"{prop}-{key}" not in only:
                continue
            render(prop, key, view)
