"""Build the pool & garden plan set: HTML page, standalone SVG sheets, zip.

Author: AbodyStudio Limited - https://abodystudio.com/
Usage: python3 build.py   (bump VERSION in src/model.py for every update)
"""
import html
import unicodedata
import json
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

import sheets  # noqa: E402
from model import (AUTHOR, DATE, INDICE, LV, POOL_L, POOL_W, PROJECT, Q, SHEETS, VERSION,  # noqa: E402
                   FLOOR_DEEP, FLOOR_SHALLOW, PARCEL_AREA, HOUSE, POOL, TECH, DECK, FRONT_GARDEN,
                   SLOPE_PCT, dqe, u_drive, u_nw, STAIR, NW_GARDEN_EDGE, edge_lengths)

FA_DIR = os.environ.get("FA_DIR", "/tmp/fa/package/svgs")
ICONS = {
    "solid": ["person-swimming", "ruler-combined", "map-location-dot", "camera", "compass-drafting", "layer-group",
              "list-check", "calculator", "calendar-days", "shield-halved", "language", "triangle-exclamation",
              "expand", "compress", "faucet-drip", "bolt", "helmet-safety", "envelope", "globe", "seedling",
              "circle-check", "rotate-left", "house", "water", "trowel-bricks"],
    "brands": ["whatsapp"],
}

SVG_CSS = """
.sheet{display:block;width:100%;height:auto}
.sh-bg{fill:var(--sheet)}
.k{stroke:var(--ink);fill:none;stroke-linecap:round;stroke-linejoin:round}
.red{stroke:var(--new);fill:none;stroke-linejoin:round}
.demo{stroke:var(--demo);fill:none;stroke-dasharray:2 1}
.w1{stroke-width:.18}.w2{stroke-width:.3}.w3{stroke-width:.5}.w4{stroke-width:.75}
.dash{stroke-dasharray:1.6 1}.axis{stroke-dasharray:7 1.2 1 1.2}.fence{stroke-dasharray:3 1 .6 1}
.parcel{stroke:var(--parcel)}
.pipe{stroke:var(--water);stroke-width:.7}
.arrow{marker-end:url(#ar)}
.fk{fill:var(--ink)}.fs{fill:var(--sheet)}.fh{fill:var(--head)}.fred{fill:var(--new)}
.fw{fill:var(--water-f)}.flt{fill:var(--light-f)}.fpv{fill:var(--paved-f)}.fch{fill:var(--chick-f)}
.fhx{fill:url(#hx)}.fcc{fill:url(#cc)}.fea{fill:url(#ea)}.fea2{fill:url(#ea);opacity:.55}.fgr{fill:url(#gr)}
.fst{fill:url(#st)}.fgz{fill:url(#gz)}.ftl{fill:url(#tl)}
.tree{fill:var(--tree-f)}.shrub{fill:var(--tree-f)}.op{opacity:.85}
.pat{stroke:var(--hatch);stroke-width:.15;fill:none}.patf{fill:var(--hatch)}.patk{fill:var(--ink)}
.patg{stroke:var(--green);stroke-width:.22;fill:none}.patt{stroke:var(--hatch);stroke-width:.12;fill:none}
.t{fill:var(--ink);font-family:"Archivo Narrow","Arial Narrow",Arial,sans-serif;font-size:3.2px}
.lab{font-size:3px}.b{font-weight:700}.dimt{font-size:2.9px}.lvl{font-size:2.7px}
.borne{font-size:2.8px;fill:var(--parcel)}.tiny{font-size:1.9px;fill:var(--ink-2)}.tiny2{font-size:2.55px}
.cl{font-size:2.4px;letter-spacing:.25px;fill:var(--ink-2);font-weight:600}.cs{font-size:2.8px}
.cb{font-size:3.2px;font-weight:700}.ct{font-size:4.6px;font-weight:700;letter-spacing:.15px}
.ar{font-family:"Cairo",sans-serif;font-size:4.4px;font-weight:600}
.mute{fill:var(--ink-2)}.red-t{fill:var(--new)}.demo-t{fill:var(--demo-ink)}.road{font-style:italic}
"""

LIGHT_SVG_VARS = (":root,svg{--sheet:#ffffff;--ink:#14212b;--ink-2:#5b6b76;--new:#c8372d;--parcel:#c8372d;"
                  "--water:#1683a8;--water-f:#cdebf5;--light-f:#fff2b8;--paved-f:#eceff1;--chick-f:#f6efe2;"
                  "--tree-f:#e3efd9;--green:#4f7f35;--hatch:#7d8b95;--head:#e8eef2;--demo:#d9a400;--demo-ink:#8a6a00}")


def icon_sprite():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;width:0;height:0" aria-hidden="true">']
    for style, names in ICONS.items():
        for n in names:
            p = os.path.join(FA_DIR, style, n + ".svg")
            raw = open(p).read()
            vb = raw.split('viewBox="')[1].split('"')[0]
            inner = raw.split(">", 1)[1].rsplit("</svg>", 1)[0]
            inner = inner.replace("<!--", "<!--").split("-->")[-1]
            out.append(f'<symbol id="i-{n}" viewBox="{vb}">{inner}</symbol>')
    out.append(sheets.DEFS.replace("<defs>", "<defs>").replace("</defs>", "</defs>"))
    out.append("</svg>")
    return "".join(out)


def ic(n, cls="ic"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{n}"/></svg>'


def money(x):
    return f"{x:,.0f}".replace(",", " ")


def esc(s):
    return html.escape(str(s), quote=False)


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

def facts():
    q = Q
    rows = [
        ("Pool (water)", f"{POOL_L:.2f} × {POOL_W:.2f} m - 50 m²"),
        ("Water depth", f"1.20 m → 1.60 m (slope {SLOPE_PCT:.1f} %)"),
        ("Water volume", f"≈ {q['water_vol']:.0f} m³"),
        ("Filtration", f"{q['flow']:.0f} m³/h - turnover {q['turnover_h']} h"),
        ("Structure", f"RC B25, {q['c_total']:.1f} m³ - steel ≈ {q['steel']:.0f} kg"),
        ("Parcel", f"{PROJECT['surface']} m² - Lambert Nord Maroc"),
    ]
    return "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)


def fit_rows():
    q = Q
    sb = u_drive(STAIR["v0"]) - STAIR["u1"]
    sf = u_drive(HOUSE["v1"]) - STAIR["u1"]
    rows = [
        ("Facade → pool", "2.00 garden + 2.50 loungers + 0.50 walkway", f"{POOL['v0'] - HOUSE['v1']:.2f} m", "As given"),
        ("Pool vs facade", "10 m pool facing the 12 m facade", "1.00 m set-in each end", "As given"),
        ("Pool width", "5 m", "5.00 m", "As given"),
        ("Behind the house", "3 m garden", f"≥ 3.00 m to the road boundary", "As given"),
        ("Driveway side", "1–1.5 m garden + 3 m road", f"{sb:.2f} → {sf:.2f} m strip + 3.00 m driveway", "Strip tapers: the SE fence is not parallel to the house"),
        ("Other side of the pool", "8 m garden + chickens", f"8.00 m garden + {NW_GARDEN_EDGE - u_nw(POOL['v0']):.2f} m chicken run", "Chicken run takes the remaining width"),
        ("Beyond the pool", "-", f"{52.55 - POOL['v1']:.2f} m to the NE boundary", "Existing orchard kept"),
    ]
    return "".join(f"<tr><th>{a}</th><td>{b}</td><td class='num'>{c}</td><td>{d}</td></tr>" for a, b, c, d in rows)


SPECS = [
    ("trowel-bricks", "Lot 1 - Earthworks", [
        "Strip 20 cm of topsoil and stockpile it for the new beds and lawn.",
        f"Excavate {Q['exc_base']:.0f} m² at the base, {Q['exc_depth_avg']:.2f} m average depth ({Q['exc_depth_max']:.2f} m at the deep end), with 1:2 batters. The red clay must not stand vertical above 1.30 m.",
        "Keep the excavation dry: a sump in the deep corner and a small pump on site from October to April.",
        "Compact the formation, then lay the 20 cm stone hérisson and 8 cm of blinding concrete.",
        "Backfill only after the water test, with the pool full. Use a 40 cm band of 15/25 gravel against the walls, then selected site material compacted in 20 cm layers.",
    ]),
    ("helmet-safety", "Lot 2 - Reinforced concrete", [
        "B25 concrete at 350 kg/m³ of CPJ 45, water/cement ratio ≤ 0.50, with a waterproofing admixture. Vibrate with a poker. No added water on site.",
        "Pour the floor slab (20 cm, two layers of HA10 at 15 cm) in one go, with the L-shaped HA12 wall bars and both main drains already in place.",
        "Fix a swelling waterstop on the slab before the walls. Walls are 20 cm with HA12 at 15 vertical and HA10 at 20 horizontal, both faces, and a 20 × 25 ring beam.",
        "Set all fittings (skimmers, returns, vacuum point, light niches) in the formwork before pouring. Never core-drill afterwards.",
        "Cure wet for 7 days minimum (hessian and watering, twice a day in sun or wind). Wait 21–28 days before rendering.",
    ]),
    ("water", "Lot 3 - Waterproofing and finishes", [
        "Spatterdash, then a two-coat waterproof render (15–20 mm), with 5 × 5 cm fillets at every internal corner.",
        "Apply two coats of flexible two-component cementitious membrane, with reinforcing tape at the corners and sealing collars on every fitting.",
        "Water test: fill the pool for 7 days and log the level each morning. Keep a bucket of water on the steps to separate evaporation from leaks.",
        "Lay 25 × 25 mm glass mosaic with C2TE S1 adhesive and epoxy grout. Use a darker band at the waterline and mark the depths 1.20 / 1.60.",
        "Coping: 50 × 50 cast stone with a bullnose edge and a 3 cm overhang, laid on mortar. Leave a joint between the coping and the deck.",
    ]),
    ("seedling", "Lot 6 - Garden around the pool", [
        "Planted strip (2.00 m) against the facade, with 5 steps of 15 cm from the house door down to the deck. Lavender, rosemary, agapanthus and gaura on drip irrigation.",
        "Slot drain at the foot of the strip, so rain from the house side never runs into the pool. Route the roof downpipes to the soakaway, not to the deck.",
        "Sun-lounger deck (2.50 m), R11 anti-slip porcelain 60 × 60 on a 10 cm RC base, falling 1.5 % away from the pool.",
        "SE side garden with an outdoor shower near the steps, and a cypress hedge plus bollard lights along the driveway, as in the render.",
        "NW side: 8.00 m lawn with the equipment room, then the fenced chicken run (1.50 m mesh) along the boundary.",
    ]),
]

HYD = [
    ("Pump", "15 m³/h at 10 m head, variable speed, 230 V"),
    ("Sand filter", f"Ø 750 mm, 6-way valve - filtration rate {Q['filter_rate']:.0f} m/h (≤ 50)"),
    ("Suction", "2 skimmers + 2 main drains (1 line) + vacuum point → 4 separate Ø50 lines to the manifold, each with a valve"),
    ("Return", "Ø63 main → Ø50 branches → 4 return inlets aimed towards the skimmers"),
    ("Pipes", "PVC pressure PN16, glued. Pressure test 24 h before backfill, no drop allowed"),
    ("Equipment room", f"2.40 × 2.00 m outside, semi-buried. Pump below water level ({LV['water']:+.2f}) for flooded suction. Floor drain and ventilation"),
    ("Backwash / overflow", "To the soakaway (Ø1.20 × 2.50 m) in the orchard. If you choose a salt system, never send backwash to the citrus trees"),
    ("Treatment", "Chlorine to start; salt chlorinator 80 m³ + pH control as an option"),
]
ELEC = [
    ("Supply", "From the house main panel: U1000 R2V 3G6 mm² cable in red TPC Ø63 duct, 60 cm deep, warning mesh above"),
    ("Pool panel", "Main switch, 30 mA type A RCD, breakers for pump (16 A), lights (10 A), chlorinator and socket, contactor, timer, surge arrester"),
    ("Lights", "3 × LED 12 V 30 W, fed by a 300 VA safety transformer inside the equipment room"),
    ("Safety zones", "Equipment room and transformer 3.55 m from the water (outside zones 0, 1 and 2 of IEC 60364-7-702)"),
    ("Bonding", "Pool reinforcement, ladder and metal parts bonded together and to the earth rod"),
]

SEQ = [
    ("Prepare", "Topographer surveys the existing house corners and levels, and stakes out the pool from the facade. Check with the Commune Sahel Chamali whether a permit is needed. Let the Intex chlorine fade for 3–4 days, then empty it into the orchard."),
    ("Excavate", "Strip topsoil, excavate with batters, dig the sump. Inspect the formation; soft pockets are dug out and filled with stone."),
    ("Base", "Hérisson, blinding, perimeter drain bedding."),
    ("Slab", "Rebar, main drains, L-bars for the walls. <b>Hold point:</b> inspect the rebar before pouring. Pour, vibrate, cure."),
    ("Walls", "Waterstop, wall rebar, fittings, formwork, pour walls and ring beam. Build the equipment room shell at the same time."),
    ("Pipework", "Lay all lines to the equipment room. <b>Hold point:</b> 24 h pressure test before anything is covered."),
    ("Cure", "21–28 days of curing. Meanwhile: electrical duct, soakaway, garden steps."),
    ("Waterproof", "Render, fillets, flexible membrane. <b>Hold point:</b> 7-day water test, then backfill while the pool is full."),
    ("Finish", "Drain the test water to the orchard. Lay the mosaic and epoxy grout, coping, deck, slot drain."),
    ("Equip", "Pump, filter, panel, lights, ladder. Electrician checks the RCD trip and the bonding."),
    ("Garden", "Planted strip, lawn, hedge, lights, chicken-run fence, safety fence or cover."),
    ("Fill and start", "Fill by water tanker, start filtration, balance the water, owner handover."),
]

GANTT = [
    ("Preparation and set-out", 1, 1), ("Remove the Intex pool", 1, 1), ("Excavation and base", 2, 1.5),
    ("Floor slab", 3, 1), ("Walls and ring beam", 4, 1.5), ("Equipment room", 4, 2), ("Pipework and pressure test", 5, 1.5),
    ("Concrete curing", 5, 3.5), ("Render and membrane", 9, 1), ("Water test and backfill", 10, 1),
    ("Mosaic and coping", 11, 2), ("Deck, slot drain, steps", 12, 1.5), ("Electrical and equipment", 11, 2.5),
    ("Garden, lawn, fences", 13, 2), ("Fill and start-up", 14, 1),
]

GLOSS = [
    ("Piscine / bassin", "Swimming pool", "مسبح / حوض السباحة"),
    ("Radier", "Floor slab", "بلاطة القاعدة"),
    ("Voile", "Concrete wall", "جدار خرساني مسلح"),
    ("Chaînage", "Ring beam", "حزام خرساني"),
    ("Béton armé", "Reinforced concrete", "خرسانة مسلحة"),
    ("Béton de propreté", "Blinding concrete", "خرسانة النظافة"),
    ("Hérisson", "Stone sub-base", "طبقة الحجر المرصوص"),
    ("Fer HA / acier", "Rebar", "حديد التسليح"),
    ("Enrobage", "Concrete cover", "الغطاء الخرساني"),
    ("Joint hydrogonflant", "Swelling waterstop", "شريط منع التسرب"),
    ("Enduit hydrofuge", "Waterproof render", "تلبيس مقاوم للماء"),
    ("Étanchéité", "Waterproofing", "العزل المائي"),
    ("Mosaïque pâte de verre", "Glass mosaic", "فسيفساء زجاجية"),
    ("Margelle", "Coping", "حافة المسبح"),
    ("Plage", "Pool deck", "الممشى حول المسبح"),
    ("Skimmer", "Skimmer", "كاشطة سطحية (سكيمر)"),
    ("Bonde de fond", "Main drain", "مصرف القاع"),
    ("Buse de refoulement", "Return inlet", "فوهة الإرجاع"),
    ("Prise balai", "Vacuum point", "مأخذ المكنسة"),
    ("Projecteur", "Underwater light", "كشاف إنارة تحت الماء"),
    ("Local technique", "Equipment room", "الغرفة التقنية"),
    ("Filtre à sable", "Sand filter", "فلتر رملي"),
    ("Disjoncteur différentiel 30 mA", "30 mA RCD", "قاطع تفاضلي 30 ميلي أمبير"),
    ("Liaison équipotentielle", "Equipotential bonding", "ربط تساوي الجهد"),
    ("Drain périphérique", "Perimeter drain", "مصرف محيطي"),
    ("Puits perdu", "Soakaway", "بئر التصريف"),
    ("Caniveau", "Slot drain", "قناة تصريف"),
    ("Remblai", "Backfill", "الردم"),
    ("Terrain naturel (TN)", "Natural ground", "سطح الأرض الطبيعي"),
    ("Poulailler", "Chicken coop", "خمّ الدجاج"),
]

VERIFY = [
    "House depth (assumed 10.00 m), position of the roof stair, and the exact door position. The deck steps are set on the door.",
    "Ground levels: house floor ±0.00, natural ground at the pool (assumed −0.80), and the fall towards the orchard. A topographer's level survey fixes all of these in one visit.",
    "Soil: dig one trial pit 2.5 m deep where the deep end goes, after a rainy day. Water in the pit means the drain and relief valve are essential, and the BET may thicken the slab.",
    "Where the house electrical panel is, and whether its supply can take the pump plus an optional heat pump.",
    "Water source for filling (≈ 67 m³ twice): tanker trips or the well.",
    "Permit: check with the Commune Sahel Chamali / Agence Urbaine de Tanger before excavation.",
]


def dqe_html():
    lots, opt = dqe()
    out = []
    for code, fr, en, items in lots + [opt]:
        cls = " opt" if code == "O" else ""
        out.append(f'<tbody class="lot{cls}" data-lot="{code}"><tr class="lot-h"><th colspan="6">'
                   f'<span class="lot-n">{"Options" if code == "O" else "Lot " + code}</span> {esc(fr)} <span class="en">{esc(en)}</span></th></tr>')
        for n, dfr, den, unit, qty, pu in items:
            out.append(
                f'<tr data-q="{qty}"><td class="mono">{n}</td><td>{esc(dfr)}<span class="en">{esc(den)}</span></td>'
                f'<td class="c">{unit}</td><td class="num">{qty:g}</td>'
                f'<td class="num"><input id="pu-{n}" class="pu" type="number" min="0" step="10" value="{pu}" aria-label="Prix unitaire {n}"></td>'
                f'<td class="num amt">{money(qty * pu)}</td></tr>')
        out.append(f'<tr class="sub"><td colspan="5">{"Total options (not included)" if code == "O" else "Sous-total lot " + code}</td><td class="num sub-v">0</td></tr></tbody>')
    return "".join(out)


def gantt_html():
    weeks = 15
    head = "".join(f"<span>S{i}</span>" for i in range(1, weeks + 1))
    rows = []
    for name, start, dur in GANTT:
        left = (start - 1) / weeks * 100
        width = dur / weeks * 100
        rows.append(f'<div class="g-row"><span class="g-name">{esc(name)}</span><span class="g-track">'
                    f'<i style="left:{left:.2f}%;width:{width:.2f}%"></i></span></div>')
    return f'<div class="g-head"><span></span><span class="g-weeks">{head}</span></div>' + "".join(rows)


def sheet_figs(sheet_objs):
    out = []
    for (num, fr, en, sc), obj in zip(SHEETS, sheet_objs):
        out.append(f'''<figure class="plan" id="{num.lower()}">
<figcaption><span class="pl-n mono">{num}</span><span class="pl-t">{esc(fr)}<small>{esc(en)} - {sc}</small></span>
<button type="button" class="zoom" aria-pressed="false" aria-label="Enlarge {num}">{ic("expand")}<span>Enlarge</span></button></figcaption>
<div class="plan-scroll">{obj.svg(obj.title)}</div></figure>''')
    return "".join(out)


def page(sheet_objs):
    lots, opt = dqe()
    total = sum(i[4] * i[5] for _, _, _, items in lots for i in items)
    photos = [
        ("site-aerial-from-roof.webp", "Today, from the roof", "Intex pool on a levelled pad. Orchard and chicken area to the NW, gravel driveway along the black SE fence, open orchard beyond."),
        ("site-from-driveway.webp", "Today, from the driveway", "Existing villa with the roof stair on the driveway side and the old filter box. The new equipment room goes on the NW side."),
        ("site-terrace-and-pool.webp", "Front of the villa", "Raised front platform and stone wall, rebar starters for a future upper floor. The planted strip and deck steps replace this zone."),
        ("concept-render.webp", "Target ambience (render)", "Beige coping and deck, loungers facing the pool, lit driveway with cypress hedge. The plan follows your dimensions, not the render's proportions."),
    ]
    ph = "".join(f'<figure class="ph"><img src="img/{f}" alt="{esc(t)}" loading="lazy" width="1400" height="1050"><figcaption><b>{esc(t)}</b>{esc(d)}</figcaption></figure>' for f, t, d in photos)
    specs = "".join(f'<section class="spec"><h3>{ic(i)}{esc(t)}</h3><ul>' + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul></section>" for i, t, items in SPECS)
    hyd = "".join(f"<tr><th>{a}</th><td>{esc(b)}</td></tr>" for a, b in HYD)
    ele = "".join(f"<tr><th>{a}</th><td>{esc(b)}</td></tr>" for a, b in ELEC)
    seq = "".join(f"<li><b>{a}.</b> {b}</li>" for a, b in SEQ)
    gl = "".join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class="ar" lang="ar" dir="rtl">{c}</td></tr>' for a, b, c in GLOSS)
    ver = "".join(f"<li>{esc(v)}</li>" for v in VERIFY)
    idx = "".join(f'<li><a href="#{n.lower()}"><span class="mono">{n}</span> {esc(fr)}</a></li>' for n, fr, en, sc in SHEETS)
    return f"""<title>Gharsa Foquiya Pool &amp; Garden</title>
<meta name="description" content="Plan set for the pool and garden at Douar Ghanem, Tanger-Assilah - AbodyStudio Limited, v{VERSION}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Archivo+Narrow:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Cairo:wght@400;600&display=swap">
<style>
/* Layout: a bound plan set - sheet index on the left, the dossier in one reading column, drawings full width. */
:root{{
  --paper:#eef2f3; --sheet:#ffffff; --ink:#14212b; --ink-2:#5b6b76; --rule:#cfd8dd; --head:#e8eef2;
  --new:#c8372d; --parcel:#c8372d; --water:#1683a8; --water-f:#cdebf5; --light-f:#fff2b8; --paved-f:#eceff1;
  --chick-f:#f6efe2; --tree-f:#e3efd9; --green:#4f7f35; --hatch:#7d8b95; --demo:#d9a400; --demo-ink:#8a6a00;
  --accent:#c8372d; --chip:#ffffff;
  --f-disp:"Archivo","Arial",sans-serif; --f-body:"IBM Plex Sans",system-ui,sans-serif; --f-mono:"IBM Plex Mono",ui-monospace,monospace; --f-ar:"Cairo",sans-serif;
}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{
  --paper:#0a131a; --sheet:#0f1e29; --ink:#dbe6ee; --ink-2:#93a7b4; --rule:#26394a; --head:#16293a;
  --new:#ff7a6b; --parcel:#ff7a6b; --water:#5cc8e8; --water-f:#123a4e; --light-f:#4a4220; --paved-f:#172836;
  --chick-f:#2a2418; --tree-f:#1a2e1c; --green:#8dbb63; --hatch:#5f7685; --demo:#f2c94c; --demo-ink:#f2c94c;
  --accent:#ff7a6b; --chip:#132430; color-scheme:dark}}}}
:root[data-theme="dark"]{{
  --paper:#0a131a; --sheet:#0f1e29; --ink:#dbe6ee; --ink-2:#93a7b4; --rule:#26394a; --head:#16293a;
  --new:#ff7a6b; --parcel:#ff7a6b; --water:#5cc8e8; --water-f:#123a4e; --light-f:#4a4220; --paved-f:#172836;
  --chick-f:#2a2418; --tree-f:#1a2e1c; --green:#8dbb63; --hatch:#5f7685; --demo:#f2c94c; --demo-ink:#f2c94c;
  --accent:#ff7a6b; --chip:#132430; color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--paper);color:var(--ink);font:15px/1.6 var(--f-body);margin:0}}
.wrap{{max-width:1240px;margin:0 auto;padding-inline:clamp(16px,3vw,32px);padding-block:28px 64px}}
.mono,.num{{font-family:var(--f-mono);font-variant-numeric:tabular-nums}}
h1,h2,h3{{font-family:var(--f-disp);text-wrap:balance;line-height:1.15;margin:0}}
h1{{font-size:clamp(28px,4.4vw,46px);font-weight:800;letter-spacing:-.01em}}
h2{{font-size:clamp(21px,2.6vw,28px);font-weight:800;display:flex;gap:.5em;align-items:baseline}}
h2 .sn{{font-family:var(--f-mono);font-size:.55em;color:var(--accent);font-weight:500}}
h3{{font-size:17px;font-weight:700;display:flex;gap:.5em;align-items:center}}
p{{margin:0}} a{{color:inherit}}
.ic{{width:1em;height:1em;fill:currentColor;flex:none}}
.lead{{max-width:68ch;color:var(--ink-2);font-size:16.5px}}
.eyebrow{{font:600 12px/1 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);display:flex;gap:.6em;align-items:center}}
header.top{{display:grid;gap:18px;padding-bottom:22px;border-bottom:2px solid var(--ink)}}
.meta{{display:flex;flex-wrap:wrap;gap:6px 18px;font:500 12.5px/1.4 var(--f-mono);color:var(--ink-2)}}
.meta b{{color:var(--ink);font-weight:500}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0;margin:0;border:1px solid var(--rule);background:var(--sheet)}}
.facts div{{padding:12px 14px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);min-width:0}}
.facts dt{{font:600 11px/1.2 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}}
.facts dd{{margin:4px 0 0;font:600 15px/1.35 var(--f-disp)}}
.grid{{display:grid;grid-template-columns:220px minmax(0,1fr);gap:40px;margin-top:34px}}
nav.idx{{position:sticky;top:calc(env(safe-area-inset-top,0px) + 16px);align-self:start;font-size:13.5px}}
nav.idx ol{{list-style:none;margin:0;padding:0;display:grid;gap:2px}}
nav.idx a{{display:block;padding:5px 8px;text-decoration:none;border-left:2px solid transparent;color:var(--ink-2)}}
nav.idx a:hover,nav.idx a:focus-visible{{color:var(--ink);border-left-color:var(--accent);outline:none}}
nav.idx .sub{{padding-left:12px;font-size:12.5px}}
main{{display:grid;gap:56px;min-width:0}}
section.blk{{display:grid;gap:18px;min-width:0;scroll-margin-top:16px}}
.photos{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}
@media (max-width:560px){{.photos{{grid-template-columns:1fr}}}}
.ph{{margin:0;background:var(--sheet);border:1px solid var(--rule);display:grid;min-width:0}}
.ph img{{width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;display:block}}
.ph figcaption{{padding:10px 12px;font-size:13.5px;color:var(--ink-2);display:grid;gap:2px}}
.ph figcaption b{{color:var(--ink);font-family:var(--f-disp)}}
.tbl{{overflow-x:auto;border:1px solid var(--rule);background:var(--sheet)}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}}
thead th{{font:600 11.5px/1.3 var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);background:var(--head)}}
tbody th{{font-weight:600;white-space:nowrap}}
td.num,th.num{{text-align:right;white-space:nowrap}} td.c{{text-align:center}}
.note{{border-left:3px solid var(--accent);padding:10px 14px;background:var(--sheet);font-size:14px;display:flex;gap:10px;align-items:flex-start}}
.note .ic{{color:var(--accent);margin-top:4px}}
.plan{{margin:0;background:var(--sheet);border:1px solid var(--rule);min-width:0}}
.plan figcaption{{display:flex;align-items:center;gap:12px;padding:10px 12px;border-bottom:1px solid var(--rule)}}
.pl-n{{font-weight:600;color:var(--accent)}}
.pl-t{{display:grid;font:700 15px/1.25 var(--f-disp);flex:1;min-width:0}}
.pl-t small{{font:400 12.5px/1.3 var(--f-body);color:var(--ink-2)}}
.plan-scroll{{overflow-x:auto}}
.plan-scroll .sheet{{min-width:760px}}
.plan.big .plan-scroll .sheet{{min-width:1900px}}
button{{font:inherit;color:inherit}}
.zoom{{display:inline-flex;gap:6px;align-items:center;border:1px solid var(--rule);background:var(--chip);padding:6px 10px;cursor:pointer;font-size:13px}}
.zoom:hover,.zoom:focus-visible{{border-color:var(--ink);outline:none}}
.specs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}}
.spec{{background:var(--sheet);border:1px solid var(--rule);padding:16px 18px;display:grid;gap:10px;min-width:0}}
.spec h3 .ic{{color:var(--accent)}}
.spec ul{{margin:0;padding-left:1.1em;display:grid;gap:6px;font-size:14px}}
.two{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}}
.two h3{{margin-bottom:8px}}
ol.seq{{margin:0;padding:0;list-style:none;counter-reset:s;display:grid;gap:0;border-top:1px solid var(--rule)}}
ol.seq li{{counter-increment:s;display:grid;grid-template-columns:44px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--rule);font-size:14.5px}}
ol.seq li::before{{content:counter(s,decimal-leading-zero);font:500 13px/1.6 var(--f-mono);color:var(--accent)}}
.dqe td{{font-size:13.5px}} .dqe .en{{display:block;color:var(--ink-2);font-size:12px}}
.dqe .lot-h th{{background:var(--head);font:700 14px/1.3 var(--f-disp);white-space:normal}}
.dqe .lot-h .en{{display:inline;font:400 12.5px var(--f-body)}}
.lot-n{{font:600 11.5px var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-right:6px}}
.dqe .sub td{{font-weight:600;text-align:right;background:var(--sheet)}}
.dqe .opt td,.dqe .opt th{{color:var(--ink-2)}}
.pu{{width:92px;text-align:right;font:500 13px var(--f-mono);padding:4px 6px;border:1px solid var(--rule);background:var(--paper);color:var(--ink)}}
.pu:focus-visible{{outline:2px solid var(--accent);outline-offset:1px}}
.totals{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));border:1px solid var(--rule);background:var(--sheet)}}
.totals div{{padding:12px 14px;border-right:1px solid var(--rule)}}
.totals dt{{font:600 11px var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}}
.totals dd{{margin:2px 0 0;font:800 22px/1.2 var(--f-disp);font-variant-numeric:tabular-nums}}
.totals .ttc dd{{color:var(--accent)}}
.row{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}}
.reset{{display:inline-flex;gap:6px;align-items:center;border:1px solid var(--rule);background:var(--chip);padding:6px 10px;cursor:pointer;font-size:13px}}
.gantt{{background:var(--sheet);border:1px solid var(--rule);padding:12px;overflow-x:auto}}
.gantt-in{{min-width:680px;display:grid;gap:3px}}
.g-head,.g-row{{display:grid;grid-template-columns:210px 1fr;gap:10px;align-items:center}}
.g-weeks{{display:grid;grid-template-columns:repeat(15,1fr);font:500 11px var(--f-mono);color:var(--ink-2);text-align:center}}
.g-name{{font-size:13px}}
.g-track{{position:relative;height:16px;background:repeating-linear-gradient(90deg,transparent 0 calc(100%/15 - 1px),var(--rule) calc(100%/15 - 1px) calc(100%/15))}}
.g-track i{{position:absolute;top:3px;bottom:3px;background:var(--water)}}
.gl td.ar,.ar{{font-family:var(--f-ar);font-size:15.5px;text-align:right}}
ul.ver{{margin:0;padding-left:1.1em;display:grid;gap:8px;max-width:80ch}}
footer{{margin-top:56px;padding-top:18px;border-top:2px solid var(--ink);display:flex;flex-wrap:wrap;gap:8px 22px;font-size:13.5px;color:var(--ink-2)}}
footer span{{display:inline-flex;gap:7px;align-items:center}} footer b{{color:var(--ink)}}
@media (max-width:900px){{.grid{{grid-template-columns:1fr}} nav.idx{{position:static}} nav.idx ol{{grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}}}}
@media (prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
{SVG_CSS}
</style>
{icon_sprite()}
<div class="wrap">
<header class="top">
  <p class="eyebrow">{ic("compass-drafting")} Dossier d'exécution - Indice {INDICE} - v{VERSION}</p>
  <h1>Pool and garden plan set, Gharsa Foquiya</h1>
  <p class="lead">A 10 × 5 m reinforced-concrete pool, set 5.00 m in front of your existing villa and centred on its 12 m facade, with the gardens around it. The drawings follow Moroccan practice (French labels, title block, levels from ±0.00 at the ground floor). The explanations are in English.</p>
  <p class="meta"><span>{PROJECT['lieu']}, {PROJECT['commune']}, {PROJECT['province']}</span><span>Date <b>{DATE}</b></span><span>Author <b>{AUTHOR['name']}</b></span></p>
  <dl class="facts">{facts()}</dl>
</header>
<div class="grid">
<nav class="idx" aria-label="Contents"><ol>
  <li><a href="#site">Site and existing</a></li>
  <li><a href="#fit">Your dimensions on the survey</a></li>
  <li><a href="#plans">Drawings</a></li>
  {"".join(f'<li class="sub"><a href="#{n.lower()}"><span class="mono">{n}</span> {esc(en)}</a></li>' for n, fr, en, sc in SHEETS)}
  <li><a href="#spec">Specification</a></li>
  <li><a href="#hyd">Filtration and electrical</a></li>
  <li><a href="#seq">Construction sequence</a></li>
  <li><a href="#dqe">Cost estimate</a></li>
  <li><a href="#planning">Schedule</a></li>
  <li><a href="#gloss">Glossary FR / EN / AR</a></li>
  <li><a href="#verify">Check before you start</a></li>
</ol></nav>
<main>
<section class="blk" id="site">
  <h2><span class="sn">01</span>Site and existing</h2>
  <p class="lead">The parcel is {PROJECT['surface']} m² (survey by Sahraoui Topo, recomputed {PARCEL_AREA:.0f} m² from the 11 boundary points). It runs about 29 m along the NE side and 40–49 m deep from the 6 m public road on the SW. The villa sits near the road and the pool goes on its NE side, facing the orchard and the open view.</p>
  <div class="photos">{ph}</div>
</section>
<section class="blk" id="fit">
  <h2><span class="sn">02</span>Your dimensions on the survey</h2>
  <div class="tbl"><table><thead><tr><th>Zone</th><th>You gave</th><th class="num">In the plan</th><th>Note</th></tr></thead><tbody>{fit_rows()}</tbody></table></div>
  <p class="note">{ic("triangle-exclamation")}<span>The survey shows the parcel is 28.97 m wide on the NE side. Your side dimensions add up to about 22 m around the pool, so the extra width goes to the chicken run on the NW side. The villa's position is taken from your sketch and dimensions, so a topographer should pick up its corners before set-out. The pool is set out from the facade (5.00 m, 1.00 m in from each corner), so it lands in the right place even if the villa sits slightly differently on the parcel.</span></p>
</section>
<section class="blk" id="plans">
  <h2><span class="sn">03</span>Drawings</h2>
  <p class="lead">Five A3 sheets. Red is new construction, hatched grey is the existing villa, and the yellow dashes show the Intex pool that comes out. Tap <b>Enlarge</b> to read a sheet at full size. The same sheets are in the zip as SVG files, which print at A3 at the stated scales.</p>
  {sheet_figs(sheet_objs)}
</section>
<section class="blk" id="spec">
  <h2><span class="sn">04</span>Specification</h2>
  <div class="specs">{specs}</div>
</section>
<section class="blk" id="hyd">
  <h2><span class="sn">05</span>Filtration and electrical</h2>
  <div class="two">
    <div><h3>{ic("faucet-drip")}Hydraulics (Lot 4)</h3><div class="tbl"><table><tbody>{hyd}</tbody></table></div></div>
    <div><h3>{ic("bolt")}Electrical (Lot 5)</h3><div class="tbl"><table><tbody>{ele}</tbody></table></div></div>
  </div>
</section>
<section class="blk" id="seq">
  <h2><span class="sn">06</span>Construction sequence</h2>
  <ol class="seq">{seq}</ol>
</section>
<section class="blk" id="dqe">
  <h2><span class="sn">07</span>Cost estimate (devis quantitatif et estimatif)</h2>
  <p class="lead">Quantities come from the drawings. Unit prices are indicative for the Tanger region in 2026, in dirhams excluding VAT. Type your contractor's prices into any field and the totals update. Your edits stay in this browser only.</p>
  <dl class="totals"><div><dt>Total HT</dt><dd id="t-ht">{money(total)}</dd></div><div><dt>TVA 20 %</dt><dd id="t-tva">{money(total * .2)}</dd></div><div class="ttc"><dt>Total TTC (DH)</dt><dd id="t-ttc">{money(total * 1.2)}</dd></div></dl>
  <div class="row"><span class="meta">Options are listed at the end and are not counted in the totals.</span><button type="button" class="reset" id="reset">{ic("rotate-left")}Reset prices</button></div>
  <div class="tbl"><table class="dqe"><thead><tr><th>N°</th><th>Désignation des ouvrages</th><th class="c">U</th><th class="num">Qté</th><th class="num">P.U. HT</th><th class="num">Montant HT</th></tr></thead>{dqe_html()}</table></div>
</section>
<section class="blk" id="planning">
  <h2><span class="sn">08</span>Schedule</h2>
  <p class="lead">About 15 weeks. If you start in October, most of the concrete work falls in the rainy season, so keep the sump pump and tarps on site. That timing still has the pool ready in spring 2027, before the hot months.</p>
  <div class="gantt"><div class="gantt-in">{gantt_html()}</div></div>
</section>
<section class="blk" id="safety">
  <h2><span class="sn">09</span>Safety and upkeep</h2>
  <div class="two">
    <div class="spec"><h3>{ic("shield-halved")}Safety</h3><ul>
      <li>Children use the site, so fit the 1.20 m fence with a self-closing gate (shown on PL-02) or a bar cover, and add a door alarm on the house doors that open onto the pool.</li>
      <li>Twin anti-vortex main drains, non-slip coping and deck, depth marks and no-diving signs.</li>
      <li>Never empty the pool between November and April. With high groundwater the empty shell can lift (see PL-05).</li>
      <li>Keep chickens fenced at least 8 m from the water and chemicals in a locked box in the equipment room.</li>
    </ul></div>
    <div class="spec"><h3>{ic("water")}Water and upkeep</h3><ul>
      <li>pH 7.2–7.6. Free chlorine 1–3 mg/L, or salt 4 g/L with a chlorinator. TAC 80–120 mg/L.</li>
      <li>Filtration time in hours ≈ water temperature ÷ 2 in summer, 2–4 h a day in winter (active wintering).</li>
      <li>Backwash when the gauge rises 0.3–0.5 bar above clean. Change the sand every 5–6 years.</li>
      <li>Weekly: empty the baskets, brush the waterline, vacuum, test the water.</li>
    </ul></div>
  </div>
</section>
<section class="blk" id="gloss">
  <h2><span class="sn">10</span>Glossary for the site</h2>
  <div class="tbl"><table class="gl"><thead><tr><th>Français</th><th>English</th><th class="ar" lang="ar" dir="rtl">العربية</th></tr></thead><tbody>{gl}</tbody></table></div>
</section>
<section class="blk" id="verify">
  <h2><span class="sn">11</span>Check before you start</h2>
  <ul class="ver">{ver}</ul>
  <p class="note">{ic("helmet-safety")}<span>This is a construction plan and design brief. Concrete sizing follows BAEL 91 mod. 99 principles, with RPS 2000 (2011) to be applied. A licensed structural engineer (BET) should check and stamp the slab, walls and equipment room before work starts, and a qualified electrician should sign off the installation.</span></p>
</section>
</main>
</div>
<footer><span><b>{AUTHOR['name']}</b></span><span>{ic("globe")}<a href="{AUTHOR['url']}">{AUTHOR['web']}</a></span><span>{ic("envelope")}{AUTHOR['email']}</span><span>{ic("whatsapp")}WhatsApp {AUTHOR['whatsapp']}</span><span class="mono">v{VERSION} - {DATE}</span></footer>
</div>
<script>
(function(){{
  var fmt=function(n){{return Math.round(n).toLocaleString('fr-FR').replace(/\\u202f|\\u00a0/g,' ');}};
  var KEY='gf-pool-dqe-v{VERSION}';
  var inputs=[].slice.call(document.querySelectorAll('.pu'));
  var saved={{}};
  try{{saved=JSON.parse(localStorage.getItem(KEY)||'{{}}');}}catch(e){{saved={{}};}}
  inputs.forEach(function(i){{i.dataset.def=i.value; if(saved[i.id]!=null) i.value=saved[i.id];}});
  function calc(){{
    var ht=0;
    document.querySelectorAll('.dqe tbody.lot').forEach(function(tb){{
      var sub=0;
      tb.querySelectorAll('tr[data-q]').forEach(function(tr){{
        var q=parseFloat(tr.dataset.q)||0, pu=parseFloat(tr.querySelector('.pu').value)||0, a=q*pu;
        tr.querySelector('.amt').textContent=fmt(a); sub+=a;
      }});
      tb.querySelector('.sub-v').textContent=fmt(sub);
      if(!tb.classList.contains('opt')) ht+=sub;
    }});
    document.getElementById('t-ht').textContent=fmt(ht);
    document.getElementById('t-tva').textContent=fmt(ht*.2);
    document.getElementById('t-ttc').textContent=fmt(ht*1.2);
  }}
  function save(){{var o={{}}; inputs.forEach(function(i){{if(i.value!==i.dataset.def) o[i.id]=i.value;}}); try{{localStorage.setItem(KEY,JSON.stringify(o));}}catch(e){{}}}}
  inputs.forEach(function(i){{i.addEventListener('input',function(){{calc();save();}});}});
  document.getElementById('reset').addEventListener('click',function(){{inputs.forEach(function(i){{i.value=i.dataset.def;}}); try{{localStorage.removeItem(KEY);}}catch(e){{}} calc();}});
  calc();
  document.querySelectorAll('.zoom').forEach(function(b){{
    b.addEventListener('click',function(){{
      var f=b.closest('.plan'), on=f.classList.toggle('big');
      b.setAttribute('aria-pressed',on); b.querySelector('span').textContent=on?'Fit to width':'Enlarge';
      b.querySelector('use').setAttribute('href',on?'#i-compress':'#i-expand');
    }});
  }});
}})();
</script>
"""


def main():
    objs = [f() for f in sheets.SHEET_FUNCS]
    dist = os.path.join(ROOT, "dist", f"v{VERSION}")
    if os.path.isdir(dist):
        shutil.rmtree(dist)
    os.makedirs(os.path.join(dist, "img"))
    os.makedirs(os.path.join(dist, "plans-svg"))
    sheets.SVG_CSS = SVG_CSS
    body = page(objs)
    # artifact/body version (no document skeleton)
    with open(os.path.join(dist, "index.body.html"), "w") as fh:
        fh.write(body)
    # standalone document for the zip
    with open(os.path.join(dist, "index.html"), "w") as fh:
        fh.write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                 '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                 f'<meta name="author" content="{AUTHOR["name"]}"></head><body>\n' + body + "\n</body></html>\n")
    for f in os.listdir(os.path.join(ROOT, "assets", "photos")):
        shutil.copy(os.path.join(ROOT, "assets", "photos", f), os.path.join(dist, "img", f))
    for (num, fr, en, sc), o in zip(SHEETS, objs):
        svg = o.svg(o.title, standalone=True).replace("<style>", "<style>" + LIGHT_SVG_VARS)
        fonts = ('<style>@import url("https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@400;600;700'
                 '&amp;family=Cairo:wght@600&amp;display=swap");</style>')
        svg = svg.replace("<defs>", fonts + "<defs>", 1)
        slug = unicodedata.normalize("NFKD", fr.split(" - ")[0]).encode("ascii", "ignore").decode()
        name = f"{num}_{slug.replace(' ', '-').replace(chr(39), '')}.svg"
        with open(os.path.join(dist, "plans-svg", name), "w") as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
    readme = f"""Gharsa Foquiya - Pool & Garden plan set
Version {VERSION} (indice {INDICE}) - {DATE}
Author: {AUTHOR['name']} - {AUTHOR['url']} - {AUTHOR['email']} - WhatsApp {AUTHOR['whatsapp']}

index.html        Full plan set: site, drawings, specification, sequence, estimate, schedule, glossary
plans-svg/        Drawing sheets PL-01 to PL-05 (A3, print at 100 %)
img/              Site photos and concept render
"""
    with open(os.path.join(dist, "LISEZMOI.txt"), "w") as fh:
        fh.write(readme)
    rel = os.path.join(os.path.dirname(ROOT), "releases")
    os.makedirs(rel, exist_ok=True)
    zpath = os.path.join(rel, f"AbodyStudio_Gharsa-Foquiya_Pool-Garden-Plan_v{VERSION}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fn in os.walk(dist):
            for f in sorted(fn):
                if f == "index.body.html":
                    continue
                p = os.path.join(dp, f)
                z.write(p, os.path.join(f"Pool-Garden-Plan_v{VERSION}", os.path.relpath(p, dist)))
    print("built", dist, "zip", zpath, os.path.getsize(zpath))


if __name__ == "__main__":
    main()
