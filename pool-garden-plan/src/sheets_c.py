"""Variante C - pompe au puisard, deux tubes : planches VC-01 à VC-08 (dossier complet, indice H).

Author: AbodyStudio Limited - https://abodystudio.com/
"""
import math

import sheets as SH
from sheets import S, frame, table, band_north, tree, rect_uv, pool_xy, U_ANG
from model import *  # noqa: F401,F403
import model as M
import variant_b as B
import variant_c as C
import sheets_b as SB
from sheets_b import (Iso, iso_box, iso_cyl, iso_tube, _poly, place_callouts, valve, check, gauge, pump_sym, callout, sec_mark,
                      rot_view, draw_cascade_plan, route, _earth, _offset_poly, _brk, money, CASC_V, CASC_MID)
from variant_c import PIT, CAGE, PUMP_C, STUB_Z, OUT_STUB_Y, CABLE_Y, RV, AL, OUTLET, ROUTES, WALL_OUT, R as RC
from variant_b import COFFRET, CASCADE, SLOT, CASC_BACK, NE_A2, SE_A2

SB.TUBE.update({
    "t0": ("#3c4a55", "T0 refoulement de la pompe"),
    "t1": ("#8a5a2b", "Tube 1 → jardin"),
    "t2": ("#1b8a5a", "Tube 2 → cascade → bassin"),
})
TUBE = SB.TUBE

VC_SHEETS = [
    ("VC-01", "Pompe immergée dans le puisard", "Vue rapprochée : pompe, cage, tubes 1 et 2", "s.é."),
    ("VC-02", "Plan général du bassin", "Puisard et cage, regard de vannes, cascade, réseaux", "1/50"),
    ("VC-03", "Coupes A-A et B-B", "Coupe longitudinale, coupe dans l'axe de la pompe, aciers", "1/50"),
    ("VC-04", "Puisard et cage de la pompe", "Plan, coupes et détail de la cage", "1/20 - 1/10 - 1/5"),
    ("VC-05", "Pompe de forage 24 V", "Élévation, détail, boîtier AL, coupe et exigences", "1/10 - 1/5 - 1/2"),
    ("VC-06", "Tubes 1 et 2, regard de vannes, cascade", "Tracés, coupe de la cascade, regard RV, pertes de charge", "1/200 - 1/20 - 1/10"),
    ("VC-07", "Sécurité électrique", "Volumes, boîtier AL, unifilaire, liaisons", "1/100 - s.é."),
    ("VC-08", "Nomenclature et coûts", "Composants, coûts, exploitation, options", "-"),
    ("PL-01", "Plan de masse", "Implantation sur le plan topographique", "1/250"),
    ("PL-02", "Plan d'aménagement des abords", "Piscine, plage, jardins, allée et poulailler", "1/100"),
    ("PL-05", "Détails béton armé et nomenclature des aciers", "Paroi, radier, chaînage, margelle (inchangés)", "1/20"),
]
ZF = FLOOR_DEEP
fin = FINISH


def _dc_line(s, pts, w=0.9):
    s.add(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in pts)}" style="fill:none;stroke:#7b3fb0;stroke-width:{w};stroke-dasharray:2.4 .8 .6 .8;stroke-linejoin:round;stroke-linecap:round"/>')


# ==========================================================================
# Axonometric close-up of the pit (pool-local a = x from the NW wall, b = y from the SW wall)
# ==========================================================================

ISO_EXT = dict(xa=-0.50, xb=0.85, ya=1.25, yb=3.75, zb=-3.30, zt=-2.30)


def fit_iso(S_, box):
    """ox, oy so that the pit view fits centred in box = (x0, y0, x1, y1)."""
    e = ISO_EXT
    I = Iso(0, 0, S_, z0=e["zt"])
    pts = [I(a, b, z) for a in (e["xa"], e["xb"]) for b in (e["ya"], e["yb"]) for z in (e["zb"], ZF + 0.34)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return ((box[0] + box[2]) / 2 - (min(xs) + max(xs)) / 2, (box[1] + box[3]) / 2 - (min(ys) + max(ys)) / 2)


def draw_pit_iso(s, S_, box):
    ox, oy = fit_iso(S_, box)
    e = ISO_EXT
    I = Iso(ox, oy, S_, z0=e["zt"])
    x0, x1, y0, y1 = PIT["x0"], PIT["x1"], PIT["y0"], PIT["y1"]
    zpf = PIT["floor"]
    zt = e["zt"]                     # cut level of the walls in the view
    yA, yB = e["ya"], e["yb"]        # extent of the pool shown
    xB = e["xb"]
    wall0 = -(fin + WALL)
    zslab = ZF - fin - SLAB
    zpit_s = zpf - fin - 0.20
    # earth / backfill behind the NW wall (cut face) and the wall itself
    iso_box(s, I, e["xa"], yA, e["zb"], wall0, yB, zt, top="#e7e1d6", fa="#d9d1c3", fb="#cfc6b6")
    iso_box(s, I, wall0, yA, zslab, 0.0, yB, zt, top="#c9d1d6", fa="#e7f3f8", fb="#bfc8ce")
    # pool floor (top face) with the pit opening, and its slab edges at the front
    _poly(s, [I(0, yA, ZF), I(xB, yA, ZF), I(xB, yB, ZF), I(0, yB, ZF)], "#dceef5")
    _poly(s, [I(x0, y0, ZF), I(x1, y0, ZF), I(x1, y1, ZF), I(x0, y1, ZF)], "#ffffff")
    _poly(s, [I(xB, yA, ZF), I(xB, yB, ZF), I(xB, yB, zslab), I(xB, yA, zslab)], "#c9d1d6")
    _poly(s, [I(0, yB, ZF), I(xB, yB, ZF), I(xB, yB, zslab), I(0, yB, zslab)], "#bfc8ce")
    for i in range(1, 9):
        xx = i * xB / 9
        if not (x0 - 1e-6 <= xx <= x1 + 1e-6):
            s.line(I(xx, yA, ZF), I(xx, yB, ZF), "k w1")
    # pit interior: back faces (x = 0 and y = y0), floor
    _poly(s, [I(0, y0, ZF), I(0, y1, ZF), I(0, y1, zpf), I(0, y0, zpf)], "#bfe2ef")
    _poly(s, [I(0, y0, ZF), I(x1, y0, ZF), I(x1, y0, zpf), I(0, y0, zpf)], "#a9d6e8")
    _poly(s, [I(0, y0, zpf), I(x1, y0, zpf), I(x1, y1, zpf), I(0, y1, zpf)], "#d3ecf5")
    # stubs through the NW wall: outlet T0, skimmers, cable conduit
    for (yy, r_, cl) in ((OUT_STUB_Y, 0.035, "#3c4a55"), (CABLE_Y, 0.022, "#2a86d8")):
        iso_cyl(s, I, "a", (yy, STUB_Z), r_, -0.01, 0.04, body="#9aa6ae", cap=cl, n=20, w=0.2)
    # pipes outside the wall rising to the cut (behind the wall in this view: dashed)
    for (yy, kind, d) in ((OUT_STUB_Y, "t0", 0.063),):
        pts = [I(0.0, yy, STUB_Z), I(wall0 - 0.12, yy, STUB_Z), I(wall0 - 0.12, yy, zt)]
        s.add(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in pts)}" style="fill:none;stroke:{TUBE[kind][0]};stroke-width:{d * S_:.2f};stroke-linejoin:round;opacity:.45"/>')
    s.add(f'<polyline points="{_pts([I(0.0, CABLE_Y, STUB_Z), I(wall0 / 2, CABLE_Y, STUB_Z), I(wall0 / 2, CABLE_Y, zt)])}" style="fill:none;stroke:{BLUE[1]};stroke-width:.9;stroke-linejoin:round;opacity:.55"/>')
    # cage frame (rim) on the floor, drawn under the pump so that the pump stays readable (x-ray view)
    _poly(s, [I(x0 - 0.03, y0 - 0.03, ZF + 0.002), I(x1 + 0.03, y0 - 0.03, ZF + 0.002), I(x1 + 0.03, y1 + 0.03, ZF + 0.002), I(x0 - 0.03, y1 + 0.03, ZF + 0.002)], "none", stroke="var(--ink)", w=0.8)
    # cradle + borehole-type pump lying along y, inside its cooling sleeve
    draw_borehole_iso(s, I)
    # front cut of the pit box (x = x1 face and y = y1 face): section of the caisson
    _poly(s, [I(x1, y0 - 0.20, ZF), I(x1, y1 + 0.20, ZF), I(x1, y1 + 0.20, zpit_s), I(x1, y0 - 0.20, zpit_s)], "none", stroke="#5b6b76", w=0.25, extra=";stroke-dasharray:1.4 .9")
    _poly(s, [I(-0.0, y1, ZF), I(x1, y1, ZF), I(x1, y1, zpf), I(0, y1, zpf)], "none", stroke="#5b6b76", w=0.25, extra=";stroke-dasharray:1.4 .9")
    _poly(s, [I(x1, y0 - 0.20, zpf - fin), I(x1, y1 + 0.20, zpf - fin), I(x1, y1 + 0.20, zpit_s), I(x1, y0 - 0.20, zpit_s)], "url(#cc)", stroke="var(--ink)", w=0.3)
    _poly(s, [I(-0.0, y1 + 0.20, zpf - fin), I(x1 + 0.20, y1 + 0.20, zpf - fin), I(x1 + 0.20, y1 + 0.20, zpit_s), I(0, y1 + 0.20, zpit_s)], "url(#cc)", stroke="var(--ink)", w=0.3)
    s.line(I(x1, y0, ZF), I(x1, y0, zpf), "memb")
    s.line(I(0, y1, ZF), I(0, y1, zpf), "memb")
    # cage lifted for the view
    zl = ZF + 0.32
    for (xx, yy) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        s.line(I(xx, yy, ZF), I(xx, yy, zl), "k w1 dash")
    _poly(s, [I(x0, y0, zl), I(x1, y0, zl), I(x1, y1, zl), I(x0, y1, zl)], "#b8c2c9", stroke="var(--ink)", w=0.5, extra=";fill-opacity:.55")
    _poly(s, [I(x1, y0, zl), I(x1, y1, zl), I(x1, y1, zl - 0.03), I(x1, y0, zl - 0.03)], "#8e9aa3", w=0.3)
    _poly(s, [I(x0, y1, zl), I(x1, y1, zl), I(x1, y1, zl - 0.03), I(x0, y1, zl - 0.03)], "#7d8b95", w=0.3)
    nx, ny = 7, 30
    s.line(I(x0, (y0 + y1) / 2, zl), I(x1, (y0 + y1) / 2, zl), "k w2")
    for i in range(nx):
        for j in range(ny):
            xx = x0 + (i + 0.5 + (0.5 if j % 2 else 0)) * (x1 - x0) / (nx + 0.5)
            yy = y0 + (j + 0.5) * (y1 - y0) / ny
            x_, y_ = I(xx, yy, zl)
            s.add(f'<ellipse cx="{x_:.2f}" cy="{y_:.2f}" rx="0.62" ry="0.36" style="fill:#3c4a55;opacity:.75"/>')
    # water level hint and break lines on the cut walls
    for (yy, kind) in ((OUT_STUB_Y, "t0"),):
        x_, y_ = I(wall0 - 0.12, yy, zt)
        s.line((x_ - 2.6, y_ + 1.0), (x_ + 2.6, y_ - 1.0), "k w2")
    x_, y_ = I(wall0 / 2, CABLE_Y, zt)
    s.line((x_ - 2.0, y_ + 0.8), (x_ + 2.0, y_ - 0.8), "k w2")
    return I


# --------------------------------------------------------------------------
# The pump drawn like the owner's photo: polished stainless body and motor, brass head and rings,
# yellow band, white plates, perforated inlet, blue flat cable strapped along the body.
# Shade bands: (angle from, angle to, colour) around the axis; visible half in the axonometric = -45..135 deg
# --------------------------------------------------------------------------
STEEL = [(-45, -25, "#8c98a1"), (-25, 5, "#c0c9d0"), (5, 24, "#edf1f4"), (24, 40, "#9ba7b0"),
         (40, 72, "#f8fafb"), (72, 100, "#cbd3d9"), (100, 120, "#aab5bd"), (120, 135, "#838f98")]
MESH = [(-45, -20, "#7d8a93"), (-20, 30, "#b3bec6"), (30, 80, "#dfe5e9"), (80, 135, "#99a5ae")]
BRASS = [(-45, -20, "#8a6420"), (-20, 14, "#c4973c"), (14, 40, "#f2d68e"), (40, 58, "#b5862d"),
         (58, 96, "#e9c76f"), (96, 135, "#9a7225")]
YELLOW = [(-45, -15, "#c99a12"), (-15, 30, "#f2c230"), (30, 82, "#ffdb52"), (82, 135, "#d6a618")]
DARK = [(-45, 20, "#1f272d"), (20, 80, "#4a565e"), (80, 135, "#283137")]
BLUE = ("#1d5f9e", "#2a86d8", "#9ad0f6")      # flat cable: edge, body, highlight
INK = "var(--ink)"
CABLE_T = 100                                   # angle of the cable on the body (upper side, seen in the views)


def _pts(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def _arc(I, px, pa, r, y, t0, t1, n=8):
    return [I(px + r * math.cos(math.radians(t0 + (t1 - t0) * k / n)), y,
              pa + r * math.sin(math.radians(t0 + (t1 - t0) * k / n))) for k in range(n + 1)]


def metal_iso(s, I, px, pa, r, ya, yb, pal=STEEL, cap=None, w=0.16):
    """Shaded cylinder along b (pool y) from ya to yb: bands, silhouettes, near rim, optional end face at yb."""
    for (ta, tb, col) in pal:
        _poly(s, _arc(I, px, pa, r, ya, ta, tb, 4) + _arc(I, px, pa, r, yb, ta, tb, 4)[::-1], col, stroke=col, w=0.05)
    for t in (-45, 135):
        s.add(f'<polyline points="{_pts([_arc(I, px, pa, r, ya, t, t, 1)[0], _arc(I, px, pa, r, yb, t, t, 1)[0]])}" style="fill:none;stroke:{INK};stroke-width:{w}"/>')
    s.add(f'<polyline points="{_pts(_arc(I, px, pa, r, ya, -45, 135, 18))}" style="fill:none;stroke:{INK};stroke-width:{w}"/>')
    if cap:
        _poly(s, _arc(I, px, pa, r, yb, 0, 360, 32)[:-1], cap, stroke=INK, w=w)


def patch_iso(s, I, px, pa, r, ta, tb, ya, yb, fill, stroke="none", w=0.1):
    """Label or plate stuck on the body (angles ta..tb, from ya to yb)."""
    rr = r * 1.004
    _poly(s, _arc(I, px, pa, rr, ya, ta, tb, 6) + _arc(I, px, pa, rr, yb, ta, tb, 6)[::-1], fill, stroke=stroke, w=w)


def ring_iso(s, I, px, pa, r, y, col="#5b6b76", w=0.18, t0=-45, t1=135):
    s.add(f'<polyline points="{_pts(_arc(I, px, pa, r, y, t0, t1, 18))}" style="fill:none;stroke:{col};stroke-width:{w}"/>')


def blue_cable(s, pts, w=0.9):
    """Blue flat submersible cable, as in the photo (screen points)."""
    p = _pts(pts)
    for col, ww in ((BLUE[0], w + 0.35), (BLUE[1], w), (BLUE[2], w * 0.28)):
        s.add(f'<polyline points="{p}" style="fill:none;stroke:{col};stroke-width:{ww:.2f};stroke-linejoin:round;stroke-linecap:round"/>')


def draw_borehole_iso(s, I):
    pc = PUMP_C
    px, pa, r = pc["x"], pc["axis"], pc["D"] / 2
    zpf = PIT["floor"]
    y0, yh, yi, ym, y1 = pc["y0"], pc["y0"] + pc["head_L"], pc["y_inlet"], pc["y_motor"], pc["y1"]
    sl0, sl1 = pc["sleeve"]
    # cradle: two rails and three saddles
    for xx in (px - 0.06, px + 0.06):
        iso_box(s, I, xx - 0.012, y0 + 0.05, zpf, xx + 0.012, sl1 - 0.05, zpf + pc["cradle"] - 0.02, top="#9aa6ae", fa="#7d8b95", fb="#6b7a84", w=0.12)
    for yy in (y0 + 0.25, (yi + y1) / 2, y1 - 0.12):
        iso_box(s, I, px - 0.09, yy - 0.012, zpf + pc["cradle"] - 0.02, px + 0.09, yy + 0.012, pa - r * 0.6, top="#3c4a55", fa="#3c4a55", fb="#2c3840", w=0.1)
    # outlet: hose T0 -> black barbed adapter -> brass nipple 1-1/4"
    iso_tube(s, I, [(px, y0 - 0.075, pa), (px - 0.07, y0 - 0.10, pa - 0.02), (0.05, OUT_STUB_Y, STUB_Z)], "t0", 0.040, arrows=False)
    metal_iso(s, I, px, pa, 0.019, y0 - 0.075, y0 - 0.035, DARK)
    for k in range(3):
        ring_iso(s, I, px, pa, 0.0195, y0 - 0.068 + k * 0.011, "#0e1316", 0.25)
    metal_iso(s, I, px, pa, 0.024, y0 - 0.035, y0, BRASS)
    for k in range(4):
        ring_iso(s, I, px, pa, 0.024, y0 - 0.030 + k * 0.007, "#7a561a", 0.12)
    # brass discharge head, stainless collar with two lifting lugs
    metal_iso(s, I, px, pa, r, y0, y0 + 0.035, BRASS)
    ring_iso(s, I, px, pa, r, y0 + 0.012, "#7a561a", 0.14)
    metal_iso(s, I, px, pa, r, y0 + 0.035, yh, STEEL)
    for t in (55, 125):
        x_, y_ = I(px + r * 1.18 * math.cos(math.radians(t)), y0 + 0.048, pa + r * 1.18 * math.sin(math.radians(t)))
        s.add(f'<circle cx="{x_:.2f}" cy="{y_:.2f}" r="0.75" style="fill:#c0c9d0;stroke:{INK};stroke-width:.14"/>')
    # stainless pump end (stages) with its plate, yellow band and safety label
    metal_iso(s, I, px, pa, r, yh, yi, STEEL)
    patch_iso(s, I, px, pa, r, 30, 112, yh + 0.03, yh + 0.12, "#f3f5f6", "#8c98a1", 0.08)
    patch_iso(s, I, px, pa, r, 30, 112, yh + 0.03, yh + 0.045, "#3c4a55")
    for k in range(4):
        ring_iso(s, I, px, pa, r * 1.006, yh + 0.058 + k * 0.016, "#9aa6ae", 0.1, 38, 104)
    metal_iso(s, I, px, pa, r * 1.004, yh + 0.28, yh + 0.315, YELLOW, w=0.1)
    patch_iso(s, I, px, pa, r * 1.006, 52, 92, yh + 0.288, yh + 0.307, "#1f272d")
    patch_iso(s, I, px, pa, r, 40, 104, yh + 0.44, yh + 0.53, "#ffffff", "#e4572e", 0.16)
    patch_iso(s, I, px, pa, r, 40, 104, yh + 0.44, yh + 0.455, "#e4572e")
    # inlet: grooves, brass ring, perforated screen, brass ring
    metal_iso(s, I, px, pa, r, yi, yi + 0.025, STEEL)
    for k in range(3):
        ring_iso(s, I, px, pa, r, yi + 0.006 + k * 0.006, "#4b5963", 0.14)
    metal_iso(s, I, px, pa, r * 1.04, yi + 0.025, yi + 0.037, BRASS, w=0.12)
    metal_iso(s, I, px, pa, r, yi + 0.037, ym - 0.012, MESH)
    for j in range(6):
        yy = yi + 0.043 + j * (ym - 0.012 - yi - 0.049) / 5
        for t in range(-30 + (6 if j % 2 else 0), 130, 12):
            x_, y_ = I(px + r * math.cos(math.radians(t)), yy, pa + r * math.sin(math.radians(t)))
            s.add(f'<ellipse cx="{x_:.2f}" cy="{y_:.2f}" rx="0.34" ry="0.24" style="fill:#2c3840"/>')
    metal_iso(s, I, px, pa, r * 1.04, ym - 0.012, ym, BRASS, w=0.12)
    # motor: two bolts, plate, groove near the end, end face
    metal_iso(s, I, px, pa, r, ym, y1, STEEL, cap="#cfd7dc")
    for t in (25, 100):
        x_, y_ = I(px + r * math.cos(math.radians(t)), ym + 0.025, pa + r * math.sin(math.radians(t)))
        s.add(f'<circle cx="{x_:.2f}" cy="{y_:.2f}" r="0.45" style="fill:#5b6b76;stroke:{INK};stroke-width:.1"/>')
    patch_iso(s, I, px, pa, r, 34, 108, ym + 0.08, ym + 0.28, "#eef1f3", "#8c98a1", 0.08)
    for k in range(7):
        ring_iso(s, I, px, pa, r * 1.006, ym + 0.10 + k * 0.024, "#9aa6ae", 0.1, 42, 100)
    for dy in (0.0, 0.006):
        ring_iso(s, I, px, pa, r, y1 - 0.20 + dy, "#5b6b76", 0.16)
    x_, y_ = I(px, y1, pa)
    s.circ(x_, y_, 0.9, "k w1 fs")
    # blue flat cable: from the motor head, along the inlet and the pump end, off the body at the conduit
    rc = r * 1.03
    on_body = [I(px + rc * math.cos(math.radians(CABLE_T)), yy, pa + rc * math.sin(math.radians(CABLE_T)))
               for yy in (ym + 0.01, CABLE_Y)]
    lift = I(px - 0.03, CABLE_Y - 0.02, pa + r + 0.05)
    loop = I(0.10, CABLE_Y + 0.08, STUB_Z + 0.12)
    blue_cable(s, on_body + [lift, loop, I(0.03, CABLE_Y, STUB_Z + 0.02)])
    for yy in (yh + 0.20, yh + 0.40, yh + 0.58, yi + 0.012):
        ring_iso(s, I, px, pa, r * 1.05, yy, "#3c4a55", 0.35, 60, 135)
    # cooling sleeve (transparent), cable gland at its front, end cap with the skimmer hose and the diaphragm
    rs = pc["sleeve_D"] / 2
    e0 = _arc(I, px, pa, rs, sl0, 0, 360, 28)[:-1]
    e1 = _arc(I, px, pa, rs, sl1, 0, 360, 28)[:-1]
    from sheets_b import _hull
    _poly(s, _hull(e0 + e1), "#7cc3dc", stroke="#1683a8", w=0.3, extra=";fill-opacity:.16;stroke-dasharray:1.2 .7")
    ring_iso(s, I, px, pa, rs, sl0, "#1683a8", 0.35)
    x_, y_ = I(px + rs * math.cos(math.radians(CABLE_T)), sl0, pa + rs * math.sin(math.radians(CABLE_T)))
    s.add(f'<circle cx="{x_:.2f}" cy="{y_:.2f}" r="0.8" style="fill:#2c3840;stroke:{INK};stroke-width:.12"/>')
    _poly(s, e1, "#7cc3dc", stroke="#1683a8", w=0.35, extra=";fill-opacity:.35")
    for k in range(-3, 4):
        a_, b_ = I(px + k * rs / 4, sl1, pa - rs * math.sqrt(1 - (k / 4) ** 2)), I(px + k * rs / 4, sl1, pa + rs * math.sqrt(1 - (k / 4) ** 2))
        s.line(a_, b_, "k w1")
    for (yy, d) in ((OUT_STUB_Y, 0.04),):
        x_, y_ = I(0.06, yy, STUB_Z + 0.01)
        s.rect(x_ - 1.4, y_ - 1.8, 2.8, 3.6, "k w2 fs")
        s.line((x_ - 1.4, y_ - 1.8), (x_ + 1.4, y_ + 1.8), "k w1")


def pit_items():
    x0, x1, y0, y1 = PIT["x0"], PIT["x1"], PIT["y0"], PIT["y1"]
    pc = PUMP_C
    px, pa, r = pc["x"], pc["axis"], pc["D"] / 2
    yh = pc["y0"] + pc["head_L"]
    zl = ZF + 0.32
    wall0 = -(fin + WALL)
    cz = pa + r * math.sin(math.radians(CABLE_T))
    cx = px + r * math.cos(math.radians(CABLE_T))
    return [
        ("CG", (x1 - 0.05, (y0 + y1) / 2 + 0.3, zl), f"Cage inox 316L perforée {CAGE['L'] * 1000:.0f} × {CAGE['W'] * 1000:.0f}, 2 panneaux, trous Ø8 (soulevée)"),
        ("CA", (x1 + 0.03, y1, ZF), "Cadre scellé au radier, vis inviolables : cage au ras du fond"),
        ("TE", (px, pc["y0"] + 0.02, pa + r), f"Tête laiton, sortie {pc['outlet']}, anneaux de levage"),
        ("RC", (px, pc["y0"] - 0.055, pa + 0.019), "Raccord cannelé + mamelon laiton (comme sur la photo)"),
        ("ET", (px + r, yh + 0.20, pa), f"Corps inox 4\" (Ø{pc['D'] * 1000:.0f}) : plaque, bande jaune, étiquette"),
        ("CB", (cx, yh + 0.47, cz + 0.004), f"Câble plat bleu 2 × {pc['cable_s']:g} mm² (TBTS), colliers inox"),
        ("AS", (px + r, (pc["y_inlet"] + pc["y_motor"]) / 2, pa - r * 0.3), "Crépine perforée entre deux bagues laiton (aspiration)"),
        ("MO", (px + r * 0.9, (pc["y_motor"] + pc["y1"]) / 2, pa - r * 0.4), f"Moteur {C.U_DC:.0f} V CC immergé (pompe totale {pc['L']:.2f} m)"),
        ("CH", (px + pc["sleeve_D"] / 2, pc["sleeve"][1] - 0.15, pa), f"Chemise de refroidissement Ø{pc['sleeve_D'] * 1000:.0f} (eau le long du moteur)"),
        ("EM", (px, pc["sleeve"][1], pa - 0.03), "Embout à grille : l'eau du puisard entre dans la chemise"),
        ("FR", (px - 0.06, pc["y0"] - 0.10, pa - 0.02), f"Flexible de refoulement {pc['outlet']} et raccord rapide"),
        ("T0", (wall0 - 0.12, OUT_STUB_Y, -2.40), "Tube T0 Ø63 vers le regard RV (té, V1, V2)"),
        ("BE", (px + 0.06, pc["y0"] + 0.25, PIT["floor"] + 0.02), "Berceau inox, selles sur plots caoutchouc"),
        ("BC", (0.10, CABLE_Y + 0.08, STUB_Z + 0.12), "Boucle de câble (1 m de mou pour sortir la pompe)"),
        ("FO", (wall0 / 2, CABLE_Y, -2.45), "Fourreau Ø40 noyé dans le voile → boîtier AL"),
        ("PU", (x1, y0 + 0.15, PIT["floor"]), f"Puisard {CAGE['L']:.2f} × {CAGE['W']:.2f} × {PIT['depth']:.2f}, fond {PIT['floor']:+.2f}"),
        ("CS", (x1, y1 + 0.20, PIT["floor"] - 0.10), "Caisson BA 0.20 + membrane continue du bassin"),
        ("RA", (0.75, 3.60, ZF), f"Fond du bassin {ZF:+.2f} (grand fond, 1.80 m d'eau)"),
    ]


def draw_principle(s, x0, y0, w, h):
    """Whole path, not to scale: pit -> T0 -> RV (tee, V1, V2) -> tube 2 -> cascade -> pool ; tube 1 -> soakaway / orchard."""
    wl = y0 + 18
    xl, xr = x0 + 44, x0 + w - 70      # pool: shallow (SE, cascade) on the left, deep (NW, pit) on the right
    yd, ys = y0 + h - 8, y0 + 34
    s.pl([(xl, wl), (xl, ys), (xl + (xr - xl) * 0.25, ys), (xr - (xr - xl) * 0.25, yd), (xr - 12, yd), (xr - 12, yd + 6), (xr - 2, yd + 6), (xr - 2, yd), (xr, yd), (xr, wl)], "k w1 fw", True)
    s.pl([(xl, wl - 4), (xl, ys), (xl + (xr - xl) * 0.25, ys), (xr - (xr - xl) * 0.25, yd), (xr - 12, yd), (xr - 12, yd + 6), (xr - 2, yd + 6), (xr - 2, yd), (xr, yd), (xr, wl - 4)], "k w4")
    s.line((xl, wl), (xr, wl), "k w2")
    for i in range(10):
        s.add(f'<ellipse cx="{xr - 11 + i:.2f}" cy="{yd + 0.3:.2f}" rx="0.3" ry="0.2" style="fill:var(--ink)"/>')
    s.line((xr - 12, yd), (xr - 2, yd), "k w3")
    s.add(f'<rect x="{xr - 11.5:.2f}" y="{yd + 2.4:.2f}" width="9" height="1.8" rx=".9" style="fill:#c3cdd4;stroke:var(--ink);stroke-width:.3"/>')
    s.t(xr - 7, yd + 10, "PUISARD + POMPE 24 V", "t tiny2 b")
    s.t((xl + xr) / 2, wl + 9, "BASSIN", "t lab b red-t")
    # T0 up the NW wall to the valve box RV
    rvx, rvy = xr + 12, wl - 10
    s.add(f'<polyline points="{xr - 2:.2f},{yd + 3.2:.2f} {xr + 4:.2f},{yd + 3.2:.2f} {xr + 4:.2f},{rvy + 6:.2f} {rvx:.2f},{rvy + 6:.2f}" style="fill:none;stroke:{TUBE["t0"][0]};stroke-width:1.6;stroke-linejoin:round"/>')
    s.rect(rvx - 1, rvy - 1, 14, 11, "k w2 fs")
    s.add(f'<polyline points="{rvx:.2f},{rvy + 6:.2f} {rvx + 3:.2f},{rvy + 6:.2f} {rvx + 3:.2f},{rvy - 1:.2f}" style="fill:none;stroke:{TUBE["t2"][0]};stroke-width:1.4"/>')
    s.add(f'<polyline points="{rvx + 3:.2f},{rvy + 6:.2f} {rvx + 13:.2f},{rvy + 6:.2f}" style="fill:none;stroke:{TUBE["t1"][0]};stroke-width:1.4"/>')
    valve(s, rvx + 3, rvy + 2, horiz=False, r=1.3)
    valve(s, rvx + 8.5, rvy + 6, r=1.3)
    s.t(rvx + 5, rvy + 3, "V2", "t tiny2 b", "start")
    s.t(rvx + 8.5, rvy + 9.6, "V1", "t tiny2 b")
    s.t(rvx - 2.5, rvy + 3.5, "RV", "t tiny2 b", "end")
    s.t(rvx + 6, rvy + 14, "té + 2 vannes", "t tiny")
    # tube 2 : RV -> along the pool (under the deck) -> cascade wall -> lip -> pool
    s.add(f'<polyline points="{rvx + 3:.2f},{rvy - 1:.2f} {rvx + 3:.2f},{y0 + 4:.2f} {xl - 4:.2f},{y0 + 4:.2f} {xl - 4:.2f},{wl - 13:.2f}" style="fill:none;stroke:{TUBE["t2"][0]};stroke-width:1.6;stroke-linejoin:round"/>')
    s.rect(xl - 8, wl - 16, 8, 20, "red w3 fcc")
    s.line((xl - 4, wl - 13), (xl + 1.5, wl - 13), "red w4")
    s.add(f'<path d="M{xl + 1.5:.2f} {wl - 13:.2f} q 2.4 0.6 2.8 13" style="fill:none;stroke:#1683a8;stroke-width:.8"/>')
    s.t(xl - 10, wl - 4, "CASCADE", "t tiny2 b red-t", "end")
    s.t(xl - 10, wl, "lame 600 × 6 mm", "t tiny", "end")
    s.t((rvx + xl) / 2, y0 + 2.2, "TUBE 2 : vers la cascade, l'eau retombe dans le bassin", "t tiny2 b", "middle")
    # tube 1 : RV -> garden (orchard, soakaway)
    bx = x0 + w - 18
    s.add(f'<polyline points="{rvx + 13:.2f},{rvy + 6:.2f} {bx:.2f},{rvy + 6:.2f} {bx:.2f},{yd + 2:.2f}" style="fill:none;stroke:{TUBE["t1"][0]};stroke-width:1.6;stroke-linejoin:round;stroke-dasharray:3 1"/>')
    s.circ(bx, yd + 5, 3.2, "k w2 fst")
    s.t(bx, yd + 11.5, "puits perdu / verger", "t tiny2", "middle")
    s.t(bx + 3.5, (wl + yd) / 2, "TUBE 1 : vers le jardin", "t tiny2 b", "middle", -90)
    # electrical: one box AL (24 V DC for the pump, 12 V for the lights), fed in 230 V from the villa
    s.rect(xr + 22, ys + 8, 12, 7, "k w2 fs")
    s.t(xr + 28, ys + 12.8, "AL", "t tiny2 b")
    s.t(xr + 36, ys + 10.6, "24 V CC", "t tiny", "start")
    s.t(xr + 36, ys + 13.4, "12 V", "t tiny", "start")
    s.line((xr + 28, ys + 15), (xr + 28, ys + 26), "elec w2")
    s.t(xr + 29.5, ys + 25, "230 V villa", "t tiny", "start")
    _dc_line(s, [(xr + 22, ys + 12), (xr + 1, ys + 12), (xr + 1, yd + 1.5), (xr - 4, yd + 1.5)], 0.7)
    s.t(xr - 1, ys + 22, "câble 24 V", "t tiny", "end")
    s.line((x0, wl - 4), (xl - 8, wl - 4), "k w1")
    s.line((xr, wl - 4), (x0 + w, wl - 4), "k w1")


VC01_BOX = (24, 24, 206, 168)


def vc01():
    s = S("c1")
    s.t(24, 16, "VUE RAPPROCHÉE DU PUISARD - écorché, sans échelle (cage représentée soulevée, voiles avant transparents)", "t cl", "start")
    I = draw_pit_iso(s, 50, VC01_BOX)
    items = pit_items()
    place_callouts(s, I, items, bounds=(22, 20, 208, 172), dist=17, r=2.6)
    s.t(214, 22, "VOTRE SCHÉMA : UNE POMPE, DEUX TUBES", "t cl red-t", "start")
    for i, t_ in enumerate(["Pompe couchée au point le plus bas, sous une cage",
                            "métallique ajourée : l'eau entre par la cage. Tube 1 :",
                            "dehors, vers le jardin. Tube 2 : vers la cascade, l'eau",
                            "retombe dans le bassin. Ni local, ni filtre, ni skimmer.",
                            "Votre pompe 1 HP 220 V ne peut pas être dans l'eau :",
                            f"en volume 0, seule la TBTS est admise. Même forme, en {C.U_DC:.0f} V CC,",
                            f"alimentée par le boîtier AL à {POOL['u0'] - AL['u']:.2f} m du bassin.",
                            "Votre pompe 220 V reste utilisable dans le puits."]):
        s.t(214, 28 + i * 4.3, t_, "t tiny2", "start", size=2.3)
    rows = [(str(i + 1), t_) for i, (_, _, t_) in enumerate(items)]
    s.t(214, 66, "REPÈRES DE LA VUE", "t cl", "start")
    table(s, 214, 68, ("N°", "Élément"), rows, (7, 92), rh=4.1, size=2.2, align="ll")
    s.t(24, 178, "PRINCIPE DES DEUX TUBES - sans échelle", "t cl", "start")
    draw_principle(s, 24, 186, 288, 92)
    _sub = SH.FRAME_SUB
    SH.FRAME_SUB = C.SUBTITLE
    frame(s, "VC-01")
    SH.FRAME_SUB = _sub
    s.title = "VC-01 Pompe au puisard"
    return s


# ==========================================================================
# 2D pump views (side / top), shared by VC-02, VC-04 and the page figure; same look as the photo
# ==========================================================================

# shade bands across the diameter: (from, to) as fractions of the radius, -1 = upper edge on the sheet
STEEL2 = [(-1.0, -0.80, "#8c98a1"), (-0.80, -0.50, "#dfe5e9"), (-0.50, -0.22, "#f8fafb"), (-0.22, -0.02, "#c3ccd3"),
          (-0.02, 0.14, "#9ba7b0"), (0.14, 0.48, "#e3e8ec"), (0.48, 0.80, "#bcc6cd"), (0.80, 1.0, "#86929b")]
MESH2 = [(-1.0, -0.6, "#8c98a1"), (-0.6, 0.0, "#dfe5e9"), (0.0, 0.6, "#b3bec6"), (0.6, 1.0, "#7d8a93")]
BRASS2 = [(-1.0, -0.70, "#9a7225"), (-0.70, -0.30, "#f2d68e"), (-0.30, 0.10, "#c4973c"), (0.10, 0.50, "#e9c76f"), (0.50, 1.0, "#8a6420")]
YELLOW2 = [(-1.0, -0.6, "#d6a618"), (-0.6, 0.2, "#ffdb52"), (0.2, 1.0, "#e0b020")]
DARK2 = [(-1.0, -0.4, "#4a565e"), (-0.4, 0.4, "#2a3339"), (0.4, 1.0, "#161c20")]


def bands2(s, xa, xb, zc, r, pal=STEEL2, w=0.3):
    for (f0, f1, col) in pal:
        s.add(f'<rect x="{xa:.2f}" y="{zc + f0 * r:.2f}" width="{xb - xa:.2f}" height="{(f1 - f0) * r:.2f}" style="fill:{col};stroke:{col};stroke-width:.04"/>')
    s.add(f'<rect x="{xa:.2f}" y="{zc - r:.2f}" width="{xb - xa:.2f}" height="{2 * r:.2f}" style="fill:none;stroke:var(--ink);stroke-width:{w}"/>')


def pump_side(s, Y, zc, k, sleeve=True, brk=None, cable=True, cable_off=-1.0, text=None):
    """Borehole-type pump seen from the side (or from above), drawn like the owner's photo.
    Y(y) -> screen x, zc = screen y of the axis, k = mm per m.
    brk = (ya, yb): motor portion removed from the view (break lines); Y must already skip it.
    cable_off: where the flat cable runs, as a fraction of the radius (-1 = upper edge, side view).
    text: write '24 V CC' on the yellow band (large scales only). Returns the screen point where the cable leaves the body."""
    pc = PUMP_C
    r = pc["D"] / 2 * k
    u = k / 200                                   # 1 at 1/5
    lw = max(0.35 * u, 0.18)
    y0, yh, yi, ym, y1 = pc["y0"], pc["y0"] + pc["head_L"], pc["y_inlet"], pc["y_motor"], pc["y1"]
    if text is None:
        text = k >= 150
    vis = lambda a, b: not brk or b <= brk[0] or a >= brk[1]
    # barbed hose adapter (black), brass nipple 1-1/4"
    ra, rn = 0.019 * k, 0.024 * k
    bands2(s, Y(y0 - 0.075), Y(y0 - 0.035), zc, ra, DARK2, lw)
    for i in range(3):
        xx = Y(y0 - 0.072 + i * 0.012)
        s.add(f'<path d="M{xx:.2f} {zc - ra:.2f} l {0.008 * k:.2f} {-0.003 * k:.2f} l 0 {2 * ra + 0.006 * k:.2f} l {-0.008 * k:.2f} {-0.003 * k:.2f}" style="fill:#1f272d;stroke:var(--ink);stroke-width:{lw * 0.6:.2f}"/>')
    bands2(s, Y(y0 - 0.035), Y(y0), zc, rn, BRASS2, lw)
    for i in range(1, 7):
        xx = Y(y0 - 0.035) + i * (Y(y0) - Y(y0 - 0.035)) / 7
        s.line((xx, zc - rn), (xx, zc + rn), "k w1")
    # brass discharge head, stainless collar with two lifting lugs
    bands2(s, Y(y0), Y(y0 + 0.035), zc, r, BRASS2, lw)
    for f in (-0.55, 0.55):
        s.line((Y(y0) + 0.3, zc + f * r), (Y(y0 + 0.035) - 0.3, zc + f * r), "k w1")
    for t in (-1, 1):
        s.add(f'<rect x="{Y(y0 + 0.040):.2f}" y="{(zc - r - 0.014 * k) if t < 0 else (zc + r):.2f}" width="{0.016 * k:.2f}" height="{0.014 * k:.2f}" rx="{0.004 * k:.2f}" style="fill:#c0c9d0;stroke:var(--ink);stroke-width:{lw * 0.7:.2f}"/>')
    bands2(s, Y(y0 + 0.035), Y(yh), zc, r, STEEL2, lw)
    # pump end (stages): plate, yellow band, safety label
    bands2(s, Y(yh), Y(yi), zc, r, STEEL2, lw)
    s.add(f'<rect x="{Y(yh + 0.03):.2f}" y="{zc - 0.62 * r:.2f}" width="{0.09 * k:.2f}" height="{1.17 * r:.2f}" style="fill:#f3f5f6;stroke:#8c98a1;stroke-width:{lw * 0.5:.2f}"/>')
    s.add(f'<rect x="{Y(yh + 0.03):.2f}" y="{zc - 0.62 * r:.2f}" width="{0.015 * k:.2f}" height="{1.17 * r:.2f}" style="fill:#3c4a55"/>')
    for i in range(4):
        xx = Y(yh + 0.058 + i * 0.016)
        s.line((xx, zc - 0.5 * r), (xx, zc + 0.45 * r), "k w1")
    bands2(s, Y(yh + 0.28), Y(yh + 0.315), zc, r * 1.004, YELLOW2, lw * 0.6)
    if text:
        s.t((Y(yh + 0.28) + Y(yh + 0.315)) / 2 + 0.9 * u, zc, f"{C.U_DC:.0f} V CC", "t tiny2 b", "middle", -90, size=2.4 * u)
    else:
        s.add(f'<rect x="{Y(yh + 0.288):.2f}" y="{zc - 0.45 * r:.2f}" width="{0.019 * k:.2f}" height="{0.9 * r:.2f}" style="fill:#1f272d"/>')
    s.add(f'<rect x="{Y(yh + 0.44):.2f}" y="{zc - 0.55 * r:.2f}" width="{0.09 * k:.2f}" height="{1.05 * r:.2f}" style="fill:#ffffff;stroke:#e4572e;stroke-width:{max(0.3 * u, 0.15):.2f}"/>')
    s.add(f'<rect x="{Y(yh + 0.44):.2f}" y="{zc - 0.55 * r:.2f}" width="{0.016 * k:.2f}" height="{1.05 * r:.2f}" style="fill:#e4572e"/>')
    tx, ty, th = Y(yh + 0.47), zc - 0.15 * r, 0.25 * r
    s.add(f'<path d="M{tx:.2f} {ty:.2f} l {th:.2f} {th * 0.55:.2f} l {-th:.2f} {th * 0.55:.2f} z" style="fill:#ffd94d;stroke:#1f272d;stroke-width:{max(0.15 * u, 0.08):.2f}"/>')
    # inlet: grooves, brass ring, perforated screen, brass ring
    bands2(s, Y(yi), Y(yi + 0.025), zc, r, STEEL2, lw)
    for i in range(3):
        xx = Y(yi + 0.006 + i * 0.006)
        s.line((xx, zc - r), (xx, zc + r), "k w2")
    bands2(s, Y(yi + 0.025), Y(yi + 0.037), zc, r * 1.04, BRASS2, lw)
    bands2(s, Y(yi + 0.037), Y(ym - 0.012), zc, r, MESH2, lw)
    nx = max(3, int((ym - 0.012 - yi - 0.037) / 0.009))
    for i in range(nx):
        xx = Y(yi + 0.037) + (i + 0.5) * (Y(ym - 0.012) - Y(yi + 0.037)) / nx
        ny = 9
        for j in range(ny):
            off = 0.5 if i % 2 else 0
            yy = zc - r + (j + 0.5 + off * 0.5) * 2 * r / (ny + 0.5)
            s.add(f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="{max(0.0028 * k, 0.12):.2f}" style="fill:#2c3840"/>')
    bands2(s, Y(ym - 0.012), Y(ym), zc, r * 1.04, BRASS2, lw)
    # motor: bolts, plate, groove near the end, end cap
    parts = [(ym, brk[0]), (brk[1], y1)] if brk else [(ym, y1)]
    for (a_, b_) in parts:
        bands2(s, Y(a_), Y(b_), zc, r, STEEL2, lw)
    for f in (-0.55, 0.55):
        s.add(f'<circle cx="{Y(ym + 0.025):.2f}" cy="{zc + f * r:.2f}" r="{max(0.004 * k, 0.25):.2f}" style="fill:#5b6b76;stroke:var(--ink);stroke-width:{lw * 0.4:.2f}"/>')
    if vis(ym + 0.08, ym + 0.28):
        s.add(f'<rect x="{Y(ym + 0.08):.2f}" y="{zc - 0.6 * r:.2f}" width="{0.20 * k:.2f}" height="{1.15 * r:.2f}" style="fill:#eef1f3;stroke:#8c98a1;stroke-width:{lw * 0.5:.2f}"/>')
        for i in range(7):
            xx = Y(ym + 0.10 + i * 0.024)
            s.line((xx, zc - 0.48 * r), (xx, zc + 0.42 * r), "k w1")
    if vis(y1 - 0.20, y1 - 0.19):
        for dy in (0.0, 0.006):
            s.line((Y(y1 - 0.20 + dy), zc - r), (Y(y1 - 0.20 + dy), zc + r), "k w2")
    s.add(f'<rect x="{Y(y1) - 0.012 * k:.2f}" y="{zc - r * 0.92:.2f}" width="{0.014 * k:.2f}" height="{r * 1.84:.2f}" rx="{0.006 * k:.2f}" style="fill:#aab5bd;stroke:var(--ink);stroke-width:{lw * 0.7:.2f}"/>')
    if brk:
        for xx in (Y(brk[0]), Y(brk[1]) if Y(brk[1]) != Y(brk[0]) else Y(brk[0])):
            s.add(f'<path d="M{xx:.2f} {zc - r - 1.5:.2f} q 1.2 {r * 0.5:.2f} 0 {r + 1.5:.2f} q -1.2 {r * 0.5:.2f} 0 {r + 1.5:.2f}" style="fill:var(--sheet);stroke:var(--ink);stroke-width:.35"/>')
    # blue flat cable along the body, from the motor head to where it leaves the pump
    exit_pt = (Y(CABLE_Y), zc + cable_off * r)
    if cable:
        cz = zc + cable_off * r - (max(0.005 * k, 0.35) if cable_off <= -1 else 0)
        blue_cable(s, [(Y(ym + 0.01), cz), (Y(CABLE_Y), cz)], max(0.010 * k, 0.6))
        for yy in (yh + 0.20, yh + 0.40, yh + 0.58, yi + 0.012):
            s.add(f'<rect x="{Y(yy) - 0.004 * k:.2f}" y="{cz - max(0.007 * k, 0.5):.2f}" width="{0.008 * k:.2f}" height="{2 * max(0.007 * k, 0.5):.2f}" style="fill:#3c4a55"/>')
        exit_pt = (Y(CABLE_Y), cz)
    # cooling sleeve (transparent, in front), cable gland at its front, end cap with the diaphragm
    if sleeve:
        sl0, sl1 = pc["sleeve"]
        rs = pc["sleeve_D"] / 2 * k
        s.add(f'<rect x="{Y(sl0):.2f}" y="{zc - rs:.2f}" width="{Y(sl1) - Y(sl0):.2f}" height="{2 * rs:.2f}" style="fill:#7cc3dc;fill-opacity:.16;stroke:#1683a8;stroke-width:{lw:.2f};stroke-dasharray:1.4 .8"/>')
        s.add(f'<rect x="{Y(sl0) - 0.004 * k:.2f}" y="{zc - rs:.2f}" width="{0.008 * k:.2f}" height="{2 * rs:.2f}" style="fill:#1683a8;opacity:.55"/>')
        s.rect(Y(sl1) - 0.6, zc - rs, 1.2, 2 * rs, "k w2 fs")
        for j in range(1, 6):
            s.line((Y(sl1) - 0.6, zc - rs + j * rs / 3), (Y(sl1) + 0.6, zc - rs + j * rs / 3), "k w1")
    return exit_pt


def vc04():
    s = S("c4p")
    x0, x1, y0, y1 = PIT["x0"], PIT["x1"], PIT["y0"], PIT["y1"]
    zpf = PIT["floor"]
    wall0 = -(fin + WALL)
    pc = PUMP_C
    px, pa = pc["x"], pc["axis"]
    zslab = ZF - fin - SLAB
    zps = zpf - fin - 0.20
    # ---- plan 1/20 : y to the right, x downwards (pool interior at the bottom)
    K = 50
    PX = lambda y: 28 + (y - 1.25) * K
    PY = lambda x: 40 + (x + 0.45) * K
    s.add('<defs><clipPath id="c4pp"><rect x="24" y="30" width="132" height="80"/></clipPath></defs><g clip-path="url(#c4pp)">')
    s.rect(PX(1.25), PY(wall0 - 0.25), 2.5 * K, 0.25 * K, "k w1 fgr")
    s.rect(PX(1.25), PY(wall0), 2.5 * K, WALL * K, "k w3 fcc")
    s.rect(PX(1.25), PY(-fin), 2.5 * K, (1.20 + fin) * K, "k w1 fw")
    s.rect(PX(y0 - 0.20), PY(0), (y1 - y0 + 0.40) * K, (x1 + 0.20) * K, "k w1 dash")
    s.rect(PX(y0), PY(x0), (y1 - y0) * K, (x1 - x0) * K, "k w3 fs")
    s.rect(PX(y0 - 0.03), PY(x0), (y1 - y0 + 0.06) * K, (x1 - x0 + 0.03) * K, "k w1")
    ex, ez = pump_side(s, PX, PY(px), K, cable_off=-0.2)
    for (yy, d, kind) in ((OUT_STUB_Y, 0.063, "t0"),):
        s.add(f'<line x1="{PX(yy):.2f}" y1="{PY(wall0 - 0.25):.2f}" x2="{PX(yy):.2f}" y2="{PY(0.06):.2f}" style="stroke:{TUBE[kind][0]};stroke-width:{d * K:.2f}"/>')
    s.add(f'<polyline points="{PX(OUT_STUB_Y):.2f},{PY(0.06):.2f} {PX(OUT_STUB_Y):.2f},{PY(px - 0.04):.2f} {PX(pc["y0"] - 0.06):.2f},{PY(px):.2f}" style="fill:none;stroke:{TUBE["t0"][0]};stroke-width:2;stroke-linejoin:round"/>')
    s.add(f'<line x1="{PX(CABLE_Y):.2f}" y1="{PY(wall0 - 0.25):.2f}" x2="{PX(CABLE_Y):.2f}" y2="{PY(0.0):.2f}" style="stroke:#c9d1d6;stroke-width:{0.04 * K:.2f}"/>')
    blue_cable(s, [(PX(CABLE_Y), PY(wall0 - 0.25)), (PX(CABLE_Y), PY(0.03)), (PX(CABLE_Y) + 3, PY(0.10)), (ex, ez)], 0.7)
    s.add("</g>")
    for t_, (xx, yy), a in (("T0 → RV", (PX(OUT_STUB_Y) + 1.5, PY(wall0 - 0.28)), "end"), 
                            ("câble → AL", (PX(CABLE_Y) - 1.0, PY(wall0 - 0.28)), "start"), ("BASSIN", (PX(2.50), PY(0.80)), "middle")):
        s.t(xx, yy, t_, "t tiny2 b", a)
    s.dim((PX(y0), PY(x1 + 0.03)), (PX(y1), PY(x1 + 0.03)), -4, f"{y1 - y0:.2f}", size=2.4)
    s.dim((PX(y1 + 0.14), PY(x0)), (PX(y1 + 0.14), PY(x1)), 0, f"{x1 - x0:.2f}", size=2.4)
    s.dim((PX(pc["y0"]), PY(px - 0.12)), (PX(pc["y1"]), PY(px - 0.12)), 0, f"{pc['L']:.2f}", size=2.4)
    s.t(90, 26, "PLAN DU PUISARD (cage déposée)  1/20", "t ct")
    # ---- long section 1/20 along the pump axis, looking NW
    AX = lambda y: 172 + (y - 1.25) * K
    AZ = lambda z: 42 + (-2.50 - z) * K
    s.add('<defs><clipPath id="c4pa"><rect x="168" y="32" width="140" height="68"/></clipPath></defs><g clip-path="url(#c4pa)">')
    s.rect(AX(1.25), AZ(zslab), 2.5 * K, (zslab - (zps - 0.40)) * K, "k w1 fea")
    s.rect(AX(1.25), AZ(ZF - fin), 2.5 * K, SLAB * K, "k w3 fcc")
    s.rect(AX(y0 - 0.20), AZ(ZF - fin), (y1 - y0 + 0.40) * K, (ZF - fin - zps) * K, "k w3 fcc")
    s.rect(AX(y0 - 0.20), AZ(zps), (y1 - y0 + 0.40) * K, (BLIND + HERISSON) * K, "k w1 fst")
    s.rect(AX(1.25), AZ(-2.50), 2.5 * K, (-2.50 - ZF) * K, "k w1 fw")
    s.rect(AX(y0), AZ(ZF), (y1 - y0) * K, PIT["depth"] * K, "k w1 fw")
    s.line((AX(1.25), AZ(ZF)), (AX(y0), AZ(ZF)), "memb")
    s.pl([(AX(y0), AZ(ZF)), (AX(y0), AZ(zpf)), (AX(y1), AZ(zpf)), (AX(y1), AZ(ZF))], "memb")
    s.line((AX(y1), AZ(ZF)), (AX(3.75), AZ(ZF)), "memb")
    s.rect(AX(y0 - 0.03), AZ(ZF + 0.003), (y1 - y0 + 0.06) * K, 0.8, "k w2 fk")
    for yy in (pc["y0"] + 0.25, (pc["y_inlet"] + pc["y1"]) / 2, pc["y1"] - 0.12):
        s.rect(AX(yy) - 0.6, AZ(pa - pc["sleeve_D"] / 2), 1.2, (pa - pc["sleeve_D"] / 2 - zpf) * K, "k w1 fk")
    s.rect(AX(pc["y0"] + 0.05), AZ(zpf + 0.02), (pc["sleeve"][1] - pc["y0"] - 0.10) * K, 0.02 * K, "k w1 fs")
    ex, ez = pump_side(s, AX, AZ(pa), K)
    blue_cable(s, [(ex, ez), (ex - 1.5, ez - 3.5), (ex - 5, ez - 3), (AX(CABLE_Y) - 4, AZ(STUB_Z)), (AX(CABLE_Y), AZ(STUB_Z))], 0.6)
    s.add(f'<polyline points="{AX(pc["y0"] - 0.06):.2f},{AZ(pa):.2f} {AX(OUT_STUB_Y):.2f},{AZ(STUB_Z):.2f}" style="fill:none;stroke:{TUBE["t0"][0]};stroke-width:2;stroke-linejoin:round"/>')
    for yy in (OUT_STUB_Y,):
        s.circ(AX(yy), AZ(STUB_Z), 1.6, "k w2 fs")
    s.circ(AX(CABLE_Y), AZ(STUB_Z), 1.0, "k w2 fs")
    s.add("</g>")
    for z, t_, yy in ((ZF, f"{ZF:+.2f}", 3.62), (zpf, f"{zpf:+.2f}", 3.62)):
        s.level(AX(yy), AZ(z), t_, side="r", section=True)
    s.dim((AX(1.32), AZ(ZF)), (AX(1.32), AZ(zpf)), 0, f"{PIT['depth']:.2f}", size=2.4)
    s.t(172, AZ(zps - 0.40) + 6, f"Niveaux : fond du bassin {ZF:+.2f} - fond du puisard {zpf:+.2f} - axe de la pompe {pa:+.2f} - sorties {STUB_Z:+.2f}", "t tiny2", "start", size=2.2)
    s.t(239, 26, "COUPE SUIVANT L'AXE DE LA POMPE  1/20", "t ct")
    # ---- cross section 1/10 through the inlet, looking NE
    K2 = 100
    BX = lambda x: 30 + (x + 0.62) * K2
    BZ = lambda z: 132 + (-2.50 - z) * K2
    s.add('<defs><clipPath id="c4pb"><rect x="24" y="124" width="150" height="88"/></clipPath></defs><g clip-path="url(#c4pb)">')
    s.rect(BX(-0.62), BZ(-2.50), (wall0 + 0.62) * K2, 1.30 * K2, "k w1 fgr")
    s.rect(BX(wall0), BZ(-2.50), WALL * K2, (-2.50 - zslab) * K2, "k w3 fcc")
    s.rect(BX(wall0), BZ(zslab), (x1 + 0.20 - wall0 + 0.40) * K2, (zslab - (zps - 0.40)) * K2, "k w1 fea")
    s.rect(BX(wall0), BZ(ZF - fin), (1.05 - wall0) * K2, SLAB * K2, "k w3 fcc")
    s.rect(BX(wall0), BZ(ZF - fin), (x1 + 0.20 - wall0) * K2, (ZF - fin - zps) * K2, "k w3 fcc")
    s.rect(BX(-fin), BZ(-2.52), (1.05 + fin) * K2, (-2.52 - ZF) * K2, "k w1 fw")
    s.rect(BX(x0), BZ(ZF), (x1 - x0) * K2, PIT["depth"] * K2, "k w1 fw")
    s.pl([(BX(-fin), BZ(-2.50)), (BX(-fin), BZ(zpf)), (BX(x1), BZ(zpf)), (BX(x1), BZ(ZF)), (BX(1.05), BZ(ZF))], "memb")
    s.rect(BX(x0 - 0.03), BZ(ZF + 0.003), (x1 - x0 + 0.06) * K2, 0.8, "k w2 fk")
    s.circ(BX(px), BZ(pa), pc["sleeve_D"] / 2 * K2, "k w1 dash")
    s.circ(BX(px), BZ(pa), pc["D"] / 2 * K2, "k w2 fs")
    s.add(f'<circle cx="{BX(px):.2f}" cy="{BZ(pa):.2f}" r="{pc["D"] / 2 * K2:.2f}" style="fill:#d9e0e5;stroke:var(--ink);stroke-width:.35"/>')
    ccx = BX(px + pc["D"] / 2 * 1.08 * math.cos(math.radians(CABLE_T)))
    s.add(f'<rect x="{ccx - 0.9:.2f}" y="{BZ(pa) - pc["D"] / 2 * K2 - 1.5:.2f}" width="1.8" height="0.9" rx=".3" style="fill:{BLUE[1]};stroke:{BLUE[0]};stroke-width:.2"/>')
    s.rect(BX(px - 0.09), BZ(pa - pc["sleeve_D"] / 2), 0.18 * K2, (pa - pc["sleeve_D"] / 2 - zpf) * K2, "k w1 fhx")
    s.add(f'<polyline points="{BX(0.05):.2f},{BZ(STUB_Z):.2f} {BX(wall0 - 0.12):.2f},{BZ(STUB_Z):.2f} {BX(wall0 - 0.12):.2f},{BZ(-2.48):.2f}" style="fill:none;stroke:{TUBE["t0"][0]};stroke-width:6.3;stroke-linejoin:round;opacity:.9"/>')
    s.rect(BX(wall0) - 0.6, BZ(STUB_Z) - 4.4, WALL * K2 + 1.2, 8.8, "k w1 dash")
    blue_cable(s, [(BX(wall0 / 2), BZ(-2.48)), (BX(wall0 / 2), BZ(STUB_Z - 0.08)), (BX(0.02), BZ(STUB_Z - 0.08))], 0.8)
    s.add("</g>")
    for t_, (xx, yy), a in (("T0 Ø63 (vers RV)", (BX(wall0 - 0.12) - 4.5, BZ(-2.62)), "end"), ("fourreau Ø40 + câble plat", (BX(wall0 / 2) + 1, BZ(-2.62)), "start"),
                            ("cage au ras du fond", (BX(0.55), BZ(ZF) - 1.5), "start"), ("pompe Ø100 dans sa", (BX(px + 0.03), BZ(pa) - 14), "middle"),
                            ("chemise Ø150", (BX(px + 0.03), BZ(pa) - 10), "middle")):
        s.t(xx, yy, t_, "t tiny2 b", a)
    s.dim((BX(x0), BZ(zpf) + 5), (BX(x1), BZ(zpf) + 5), 0, f"{x1 - x0:.2f}", size=2.4)
    s.t(94, 120, "COUPE TRANSVERSALE  1/10", "t ct")
    # ---- cage detail 1/5
    D = 200
    cx0, cy0 = 182, 120
    s.rect(cx0, cy0, 0.20 * D, 0.13 * D, "k w2 fs")
    for i in range(16):
        for j in range(11):
            xx = cx0 + 2.4 + i * CAGE["pitch"] * D + (CAGE["pitch"] * D / 2 if j % 2 else 0)
            yy = cy0 + 2.4 + j * CAGE["pitch"] * D * 0.866
            if xx < cx0 + 0.20 * D - 1.5 and yy < cy0 + 0.13 * D - 1.5:
                s.circ(xx, yy, CAGE["hole"] / 2 * D, "k w1")
    s.rect(cx0 - 0.03 * D, cy0 - 0.03 * D, 0.03 * D, 0.16 * D, "k w2 fhx")
    s.circ(cx0 + 0.02 * D, cy0 + 0.02 * D, 1.2, "k w2 fs")
    s.dim((cx0 + 2.4, cy0 + 0.13 * D + 4), (cx0 + 2.4 + CAGE["pitch"] * D, cy0 + 0.13 * D + 4), 0, f"{CAGE['pitch'] * 1000:.0f}", size=2.3)
    s.t(cx0 + 0.10 * D, cy0 - 3.0, "DÉTAIL DE LA CAGE  1/5", "t cl", "middle")
    for i, t_ in enumerate(["Tôle inox 316L ép. 3 mm, trous Ø8", "en quinconce au pas de 12 mm", f"vide {CAGE['open_ratio'] * 100:.0f} %, 2 panneaux", "cadre cornière 30 × 30 scellé,",
                            "vis inox inviolables (clé spéciale)"]):
        s.t(cx0 + 0.20 * D + 4, cy0 + 2 + i * 4.3, t_, "t tiny2", "start", size=2.3)
    # ---- calculation table
    rows = [("Débit de la pompe", f"{C.Q_C:.0f} m³/h - recyclage en {RC['turnover']:.1f} h"),
            ("Passage libre de la cage", f"{CAGE['L']:.2f} × {CAGE['W']:.2f} × {CAGE['open_ratio']:.2f} = {RC['cage_open']:.3f} m²"),
            ("Vitesse au travers de la cage", f"{RC['v_cage']:.4f} m/s (limite usuelle 0.5 m/s)"),
            ("Cage plus grande qu'un corps", f"≥ 457 × 584 mm : {'oui' if RC['unblockable'] else 'non'}"),
            ("Vitesse le long du moteur", f"{RC['v_sleeve']:.2f} m/s dans la chemise (mini usuel 0.08 m/s)"),
            ("HMT tube 2 (cascade)", f"{RC['tdh_2'][1]:.2f} mCE à {C.Q_C:.0f} m³/h"),
            ("HMT tube 1 (jardin, début / fin de vidange)", f"{RC['tdh_1'][1]:.2f} / {RC['tdh_1_end'][1]:.2f} mCE à {C.Q_GARDEN:.0f} m³/h"),
            ("Pompe retenue", f"{C.Q_C:.0f} m³/h à {pc['head']} mCE et {C.Q_GARDEN:.0f} m³/h à {pc['head_1']} mCE, {C.U_DC:.0f} V CC, {pc['L']:.2f} m"),
            ("Puissance absorbée (cascade / nominale)", f"{RC['p1']:.0f} / {RC['p1_max']:.0f} W (rendement {C.ETA:.2f})"),
            ("Courant à 24 V (moyen / maxi)", f"{RC['cable']['i_avg']:.1f} / {RC['i_dc']:.1f} A"),
            ("Câble du moteur", f"2 × {RC['cable']['s']:g} mm², {C.L['pump_cable']:.1f} m : chute {RC['cable']['drop_avg_pct']:.1f} / {RC['cable']['drop_pct']:.1f} %")]
    s.t(176, 160, "CALCUL DU PUISARD ET DE LA POMPE", "t cl", "start")
    table(s, 176, 162, ("Grandeur", "Valeur"), rows, (58, 78), rh=4.4, size=2.2, align="ll")
    notes = ["Cage vissée au ras du fond : rien ne dépasse, pas de prise pour les pieds.",
             "Entretien : couper le boîtier AL (I0 cadenassé), déposer la cage à la clé, défaire le raccord",
             "rapide à la perche, remonter la pompe par ses anneaux ; le câble coulisse dans le fourreau.",
             "Membrane du bassin continue dans le puisard, angles en gorge 5 × 5."]
    s.t(24, 222, "NOTES", "t cl", "start")
    for i, t_ in enumerate(notes):
        s.t(24, 228 + i * 4.3, t_, "t tiny2", "start", size=2.3)
    _sub = SH.FRAME_SUB
    SH.FRAME_SUB = C.SUBTITLE
    frame(s, "VC-04")
    SH.FRAME_SUB = _sub
    s.title = "VC-04 Puisard et cage"
    return s


# ==========================================================================
# VC-04  La pompe de forage TBTS 24 V : élévation 1/10 entière, détail 1/5, boîtier AL, coupe 1/2, exigences
# ==========================================================================

def draw_al_box(s, x, y, k=100):
    """SELV supply box AL, drawn like the white control box of the photo (0.30 x 0.40 x 0.16 m)."""
    w, h = 0.30 * k, 0.40 * k
    s.rect(x + w * 0.35, y + h, w * 0.30, 0.06 * k, "k w1 fhx")                 # post
    s.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="1.6" style="fill:#f4f6f7;stroke:var(--ink);stroke-width:.4"/>')
    s.add(f'<rect x="{x + 1.4:.2f}" y="{y + 1.4:.2f}" width="{w - 2.8:.2f}" height="{h - 2.8:.2f}" rx="1.0" style="fill:#fbfcfc;stroke:#9aa6ae;stroke-width:.25"/>')
    for (xx, yy) in ((x + 2.6, y + 2.6), (x + w - 2.6, y + 2.6), (x + 2.6, y + h - 2.6), (x + w - 2.6, y + h - 2.6)):
        s.add(f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r=".6" style="fill:#cfd7dc;stroke:var(--ink);stroke-width:.15"/>')
    # label plate with the lightning sign
    s.add(f'<rect x="{x + 4:.2f}" y="{y + 12:.2f}" width="{w * 0.52:.2f}" height="{h * 0.36:.2f}" style="fill:#fff7d6;stroke:#9aa6ae;stroke-width:.2"/>')
    s.add(f'<path d="M{x + 7.4:.2f} {y + 14:.2f} l 2.4 4.2 l -4.8 0 z" style="fill:#ffd94d;stroke:#1f272d;stroke-width:.2"/>')
    for i in range(5):
        s.line((x + 11, y + 15 + i * 1.9), (x + 4 + w * 0.52 - 1.2, y + 15 + i * 1.9), "k w1")
    # red rocker switch and indicator
    s.add(f'<rect x="{x + w - 9.5:.2f}" y="{y + 7:.2f}" width="5.6" height="8" rx=".6" style="fill:#1f272d;stroke:var(--ink);stroke-width:.2"/>')
    s.add(f'<rect x="{x + w - 8.7:.2f}" y="{y + 7.8:.2f}" width="4" height="6.4" rx=".4" style="fill:#d63031"/>')
    s.add(f'<circle cx="{x + w - 6.7:.2f}" cy="{y + 21:.2f}" r="1.5" style="fill:#2ecc71;stroke:var(--ink);stroke-width:.2"/>')
    # glands: 230 V in (from CP), 24 V out (blue flat cable to the pump)
    for (xx, col) in ((x + w * 0.30, "#5b6b76"), (x + w * 0.70, BLUE[1])):
        s.add(f'<rect x="{xx - 2.0:.2f}" y="{y + h:.2f}" width="4" height="2.4" style="fill:#9aa6ae;stroke:var(--ink);stroke-width:.2"/>')
    s.add(f'<path d="M{x + w * 0.30:.2f} {y + h + 2.4:.2f} q 0 6 -6 9" style="fill:none;stroke:#5b6b76;stroke-width:1.2;stroke-linecap:round"/>')
    blue_cable(s, [(x + w * 0.70, y + h + 2.4), (x + w * 0.70, y + h + 6), (x + w * 0.70 + 4, y + h + 9), (x + w * 0.70 + 12, y + h + 9)], 1.0)
    return [("interrupteur marche / arrêt", (x + w - 4.5, y + 9)), ("voyant de marche", (x + w - 5.2, y + 21)),
            ("transformateur de sécurité + contrôleur", (x + w * 0.5, y + h * 0.75)),
            ("entrée 230 V depuis le TGBT (3G2.5)", (x + w * 0.30, y + h + 1.2)), ("câble plat bleu 24 V CC → pompe", (x + w * 0.70 + 10, y + h + 9))]


def vc05():
    s = S("c5")
    pc = PUMP_C
    y0, yh, yi, ym, y1 = pc["y0"], pc["y0"] + pc["head_L"], pc["y_inlet"], pc["y_motor"], pc["y1"]
    sl0, sl1 = pc["sleeve"]
    # ---- 1/10 : the whole pump, lying as in the pit
    K1 = 100
    Y1 = lambda y: 32 + (y - (y0 - 0.085)) * K1
    z1 = 38
    s.t(24, 18, f"ÉLÉVATION 1/10 : LA POMPE ENTIÈRE ({pc['L']:.2f} m), COUCHÉE COMME DANS LE PUISARD", "t cl", "start")
    for yy in (y0 + 0.25, (yi + y1) / 2, y1 - 0.12):
        s.rect(Y1(yy) - 1.2, z1 + pc["sleeve_D"] / 2 * K1, 2.4, 2.6, "k w1 fhx")
    s.rect(Y1(y0 + 0.05), z1 + pc["sleeve_D"] / 2 * K1 + 2.6, (sl1 - y0 - 0.10) * K1, 1.0, "k w1 fs")
    ex, ez = pump_side(s, Y1, z1, K1)
    blue_cable(s, [(ex, ez), (ex - 3, ez - 4), (ex - 9, ez - 6)], 0.9)
    s.t(ex - 10, ez - 6.6, "câble → fourreau → AL", "t tiny", "end")
    s.dim((Y1(sl0), z1 - 11), (Y1(sl1), z1 - 11), 0, f"chemise {sl1 - sl0:.2f}", size=2.3)
    s.dim((Y1(y0), z1 + 15), (Y1(ym), z1 + 15), 0, f"pompe {ym - y0:.2f}", size=2.4)
    s.dim((Y1(ym), z1 + 15), (Y1(y1), z1 + 15), 0, f"moteur {y1 - ym:.2f}", size=2.4)
    s.dim((Y1(y0), z1 + 22), (Y1(y1), z1 + 22), 0, f"{pc['L']:.2f} (longueur totale, comme votre pompe)", size=2.6)
    # ---- AL box 1/10
    s.t(214, 18, "BOÎTIER AL  1/10 (sur poteau, hors volumes)", "t cl", "start")
    pts = draw_al_box(s, 220, 24)
    for i, (txt, (xx, yy)) in enumerate(pts):
        ly = 27 + i * 7.6
        s.add(f'<polyline points="{xx:.2f},{yy:.2f} {262:.2f},{ly:.2f} {264:.2f},{ly:.2f}" style="fill:none;stroke:var(--ink);stroke-width:.18"/>')
        s.circ(xx, yy, 0.45, "k w1 fk")
        s.t(265, ly + 0.8, txt, "t tiny2", "start", size=2.2)
    s.t(265, 27 + 5 * 7.6 + 0.8, f"IP65, fermé à clé, à {POOL['u0'] - AL['u']:.2f} m du bassin", "t tiny2 b", "start", size=2.2)
    # ---- 1/5 detail: head, body and inlet, like the photo
    K = 200
    Y = lambda y: 30 + (y - (y0 - 0.085)) * K
    zc = 110
    xcut = Y(ym + 0.16)
    s.t(24, 72, "DÉTAIL 1/5 : TÊTE, CORPS ET CRÉPINE (même aspect que la pompe de la photo)", "t cl", "start")
    s.add(f'<defs><clipPath id="c4d"><rect x="24" y="84" width="{xcut - 24:.2f}" height="44"/></clipPath></defs><g clip-path="url(#c4d)">')
    ex, ez = pump_side(s, Y, zc, K)
    blue_cable(s, [(ex, ez), (ex - 4, ez - 5), (ex - 10, ez - 7)], 2.0)
    s.add("</g>")
    rs = pc["sleeve_D"] / 2 * K
    s.add(f'<path d="M{xcut:.2f} {zc - rs - 2:.2f} l 1.6 {rs * 0.6:.2f} l -3.2 {rs * 0.5:.2f} l 1.6 {rs * 0.9 + 4:.2f}" style="fill:none;stroke:var(--ink);stroke-width:.35"/>')
    r = pc["D"] / 2 * K
    cz = zc - r - 1.0
    marks = [(Y(y0 - 0.055), zc - 0.019 * K, "raccord cannelé (comme celui de la photo)"),
             (Y(y0 - 0.018), zc - 0.024 * K, f"mamelon laiton {pc['outlet']}"),
             (Y(y0 + 0.017), zc - r, "tête de refoulement laiton"),
             (Y(y0 + 0.048), zc - r - 2.8, "anneaux de levage"),
             (Y(yh + 0.075), zc - 0.62 * r, "plaque signalétique"),
             (Y(yh + 0.20), zc - 0.3 * r, "corps inox 4\" : étages de la pompe"),
             (Y(yh + 0.30), zc - 0.7 * r, f"bande jaune ({C.U_DC:.0f} V CC)"),
             (Y(yh + 0.36), cz, f"câble plat bleu 2 × {pc['cable_s']:g} mm²"),
             (Y(yh + 0.40), cz, "colliers inox du câble"),
             (Y(yh + 0.49), zc - 0.55 * r, "étiquette de sécurité"),
             (Y(sl0), zc - rs, "passe-câble étanche de la chemise"),
             (Y(yi + 0.031), zc - r * 1.04, "bagues laiton"),
             (Y(yi + 0.07), zc - 0.6 * r, "crépine perforée : l'eau entre ici"),
             (Y(sl0 + 0.20), zc - rs, "chemise de refroidissement (transparente)"),
             (Y(ym + 0.10), zc - 0.3 * r, f"moteur {C.U_DC:.0f} V CC (suite sur l'élévation 1/10)")]
    for i, (xx, yy, txt) in enumerate(marks):
        n = str(i + 1)
        s.line((xx, yy), (xx, 86.4), "k w1")
        s.circ(xx, yy, 0.45, "k w1 fk")
        s.circ(xx, 84.2, 2.2, "k w2 fw")
        s.t(xx, 85.1, n, "t tiny2 b", "middle", size=2.4)
        ly = 82 + i * 4.1
        s.circ(254.6, ly - 0.8, 1.7, "k w1 fw")
        s.t(254.6, ly, n, "t tiny b", "middle", size=1.9)
        s.t(257.6, ly, txt, "t tiny2", "start", size=2.15)
    yd = zc + rs + 6
    ch = [y0, yh, yi, ym]
    labs = [f"{pc['head_L']:.2f}", f"{pc['stages_L']:.2f}", f"{pc['inlet_L']:.2f}"]
    for (a_, b_), lb in zip(zip(ch, ch[1:]), labs):
        s.dim((Y(a_), yd), (Y(b_), yd), 0, lb, size=2.5)
    s.t(Y(ym) + 3, yd + 0.9, "→ moteur 0.69", "t tiny2", "start", size=2.3)
    s.dim((Y(y0 - 0.075) - 4, zc - r), (Y(y0 - 0.075) - 4, zc + r), 0, f"Ø{pc['D'] * 1000:.0f}", size=2.3)
    # ---- cross section 1/2 through the inlet
    K2 = 500
    cx, cy = 66, 194
    rs2, rp = pc["sleeve_D"] / 2 * K2, pc["D"] / 2 * K2
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{rs2:.2f}" style="fill:#7cc3dc;fill-opacity:.16;stroke:#1683a8;stroke-width:.4;stroke-dasharray:1.6 .9"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{rp:.2f}" style="fill:#dfe5e9;stroke:var(--ink);stroke-width:.45"/>')
    for i in range(36):
        t = 2 * math.pi * i / 36
        s.add(f'<circle cx="{cx + (rp - 1.4) * math.cos(t):.2f}" cy="{cy + (rp - 1.4) * math.sin(t):.2f}" r=".55" style="fill:#2c3840"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{rp * 0.62:.2f}" style="fill:#c3cdd4;stroke:var(--ink);stroke-width:.3"/>')
    s.circ(cx, cy, 2.0, "k w2 fk")
    ca = math.radians(CABLE_T)
    ccx, ccy = cx + (rp + 1.8) * math.cos(ca), cy - (rp + 1.8) * math.sin(ca)
    s.add(f'<rect x="{ccx - 4.5:.2f}" y="{ccy - 1.5:.2f}" width="9" height="3" rx="1.2" transform="rotate({90 - CABLE_T} {ccx:.2f} {ccy:.2f})" style="fill:{BLUE[1]};stroke:{BLUE[0]};stroke-width:.3"/>')
    s.circ(ccx - 1.8, ccy + 0.2, 0.9, "k w1 fs")
    s.circ(ccx + 1.8, ccy - 0.2, 0.9, "k w1 fs")
    s.rect(cx - 0.09 * K2 / 2, cy + rs2, 0.09 * K2, 8, "k w1 fhx")
    for txt, (xx, yy), (qx, qy) in [(f"chemise Ø{pc['sleeve_D'] * 1000:.0f}", (cx + rs2 * 0.7, cy - rs2 * 0.7), (cx + 46, cy - 34)),
                                   (f"crépine perforée Ø{pc['D'] * 1000:.0f}", (cx + rp * 0.7, cy + rp * 0.7), (cx + 46, cy + 18)),
                                   ("câble plat bleu", (ccx + 3, ccy - 1), (cx + 46, cy - 24)),
                                   ("arbre", (cx, cy), (cx + 46, cy + 2)),
                                   ("eau de refroidissement", (cx + (rp + 9) * 0.766, cy + (rp + 9) * 0.643), (cx + 46, cy + 34))]:
        s.line((xx, yy), (qx - 1, qy - 1), "k w1")
        s.t(qx, qy, txt, "t tiny2", "start" if qx > cx else "middle", size=2.4)
    s.t(66, 150, "COUPE PAR LA CRÉPINE  1/2", "t cl", "middle")
    # ---- requirements table
    rows = [("Type", "pompe de forage 4\" immergée, multicellulaire, moteur sans balais"),
            ("Tension", f"{C.U_DC:.0f} V CC (TBTS ≤ 30 V CC) - contrôleur dans le boîtier AL, hors volumes"),
            ("Points de fonctionnement", f"{C.Q_C:.0f} m³/h à {pc['head']} mCE (cascade) et {C.Q_GARDEN:.0f} m³/h à {pc['head_1']} mCE (fin de vidange)"),
            ("Puissance / courant", f"{RC['p1']:.0f} W en cascade, {RC['p1_max']:.0f} W nominal - {RC['i_dc']:.1f} A à {C.U_DC:.0f} V"),
            ("Dimensions maximales", f"Ø{pc['D'] * 1000:.0f} × {pc['L']:.2f} m, sortie {pc['outlet']}"),
            ("Pose", "horizontale admise par le fabricant (butée), sur berceau, dans sa chemise"),
            ("Refroidissement", f"chemise Ø{pc['sleeve_D'] * 1000:.0f} : {RC['v_sleeve']:.2f} m/s le long du moteur (mini usuel 0.08)"),
            ("Matériaux", "inox 316 (eau chlorée), tête laiton ou inox, joints pour eau de piscine"),
            ("Protections", "thermique du moteur, marche à sec et blocage par le contrôleur"),
            ("Câble", f"plat bleu 2 × {pc['cable_s']:g} mm², {math.ceil(C.L['pump_cable'])} m d'un seul tenant jusqu'au boîtier AL")]
    s.t(142, 152, "CARACTÉRISTIQUES EXIGÉES", "t cl", "start")
    table(s, 142, 154, ("Critère", "Exigence"), rows, (36, 134), rh=4.5, size=2.3, align="ll")
    cmp_rows = [("Forme", "4\" inox, tête laiton, crépine", "identique"), ("Longueur", "≈ 1.50 m", f"{pc['L']:.2f} m"),
                ("Sortie", "1-1/4\" + raccord cannelé", "identique"), ("Tension", "220 V", f"{C.U_DC:.0f} V CC"),
                ("Puissance", "1 HP (0.75 kW)", f"{RC['p1_max']:.0f} W nominal"), ("Câble", "plat bleu", f"plat bleu 2 × {pc['cable_s']:g} mm²"),
                ("Coffret", "boîtier blanc 220 V", "boîtier AL 24 V CC (TBTS)")]
    s.t(142, 211, "VOTRE POMPE (PHOTO) ET LA POMPE DU PUISARD", "t cl", "start")
    table(s, 142, 213, ("", "Pompe de la photo", "Pompe du puisard"), cmp_rows, (30, 64, 76), rh=4.4, size=2.3, align="lll")
    notes = ["La pompe de la photo (220 V) ne doit pas être placée dans le bassin : un défaut d'isolement dans l'eau peut être mortel.",
             "Elle reste utilisable dans le puits du terrain. La pompe du puisard a la même forme et la même longueur, en 24 V CC.",
             f"Les pompes de forage sont faites pour de grandes hauteurs : le modèle 24 V choisi doit avoir ses points {C.Q_C:.0f} m³/h à {pc['head']} mCE",
             f"et {C.Q_GARDEN:.0f} m³/h à {pc['head_1']} mCE sur sa courbe, et accepter la pose horizontale : à vérifier sur la fiche du fabricant avant l'achat."]
    s.t(24, 256, "À SAVOIR", "t cl red-t", "start")
    for i, t_ in enumerate(notes):
        s.t(24, 262 + i * 4.6, t_, "t tiny2", "start", size=2.4)
    _sub = SH.FRAME_SUB
    SH.FRAME_SUB = C.SUBTITLE
    frame(s, "VC-05")
    SH.FRAME_SUB = _sub
    s.title = "VC-05 Pompe de forage 24 V"
    return s


def pump_figure():
    s = S("pumpfig")
    pc = PUMP_C
    K = 160
    Y = lambda y: 12 + (y - (pc["y0"] - 0.085)) * K
    zc = 22
    ex, ez = pump_side(s, Y, zc, K)
    blue_cable(s, [(ex, ez), (ex - 4, ez - 5), (ex - 12, ez - 7)], 1.5)
    s.dim((Y(pc["y0"]), zc + 18), (Y(pc["y1"]), zc + 18), 0, f"longueur {pc['L']:.2f} m", size=4.6)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="4 6 290 46" class="sheet conn" role="img" aria-label="Pompe de forage 24 V, élévation, 1.50 m">'
            + "\n".join(s.o) + "</svg>")


# ==========================================================================
# Shared plan pieces (site u-v) and helpers for the whole variant C package
# ==========================================================================

U0, V0 = POOL["u0"], POOL["v0"]
SEC_A_Y = 2.70                 # A-A cut, pool-local y (through the pit and the cascade)
SEC_B_X = PUMP_C["x"]          # B-B cut, pool-local x (pump axis)
NET_C = [("t0", "T0 Ø63 : pompe → regard RV"), ("t2", "Tube 2 Ø63 : RV → cascade"), ("t1", "Tube 1 PEHD Ø50 : RV → jardin"),
         ("elec", "230 V : villa → boîtier AL"), ("selv", "TBTS : 24 V pompe, 12 V projecteurs"), ("drain", "Drain périphérique")]


def _frame(s, num, title):
    _sub = SH.FRAME_SUB
    SH.FRAME_SUB = C.SUBTITLE
    frame(s, num)
    SH.FRAME_SUB = _sub
    s.title = title
    return s


def tube(s, pts, kind, w=0.9, op=1.0):
    col = TUBE[kind][0]
    dash = ";stroke-dasharray:2.4 .9" if kind == "t1" else ""
    s.add(f'<polyline points="{_pts(pts)}" style="fill:none;stroke:{col};stroke-width:{w:.2f};stroke-linejoin:round;stroke-linecap:round;opacity:{op}{dash}"/>')


def legend_c(s, x, y, items=None, w=86, title="LÉGENDE DES RÉSEAUX"):
    items = items or NET_C
    s.rect(x - 2, y - 1, w, len(items) * 5.0 + 7, "k w1 fs")
    s.t(x, y + 3.4, title, "t cl", "start")
    for i, (k_, txt) in enumerate(items):
        yy = y + 8.0 + i * 5.0
        if k_ in TUBE:
            tube(s, [(x, yy), (x + 9, yy)], k_, 1.1)
        elif k_ == "drain":
            s.line((x, yy), (x + 9, yy), "pipe-d w2")
        elif k_.startswith("box:"):
            s.rect(x, yy - 2.0, 9, 3.6, "k w1 " + k_[4:])
        else:
            s.line((x, yy), (x + 9, yy), f"{k_} w3" if k_ in ("elec", "selv") else k_)
        s.t(x + 12, yy + 1.0, txt, "t cs", "start")


def draw_pit_plan(s, P, holes=True, pump=True):
    u0, v0, u1, v1 = U0 + PIT["x0"], V0 + PIT["y0"], U0 + PIT["x1"], V0 + PIT["y1"]
    s.pl([P(*p) for p in rect_uv(u0, v0 - 0.03, u1 + 0.03, v1 + 0.03)], "k w1", True)
    s.pl([P(*p) for p in rect_uv(u0, v0, u1, v1)], "k w3 fs", True)
    if holes:
        for i in range(5):
            for j in range(19):
                x_, y_ = P(u0 + 0.05 + i * 0.10, v0 + 0.05 + j * 0.10)
                s.circ(x_, y_, max(0.012 * s.k, 0.16), "k w1 fk")
    if pump:
        pc = PUMP_C
        s.pl([P(*p) for p in rect_uv(U0 + pc["x"] - pc["D"] / 2, V0 + pc["y0"], U0 + pc["x"] + pc["D"] / 2, V0 + pc["y1"])], "k w1 dash", True)


def draw_rv_plan(s, P, c="red w3 fs"):
    a = RV["a"] / 2
    s.pl([P(*p) for p in rect_uv(RV["u"] - a, RV["v"] - a, RV["u"] + a, RV["v"] + a)], c, True)


def draw_al_plan(s, P):
    x_, y_ = P(AL["u"], AL["v"])
    w_, h_ = max(AL["w"] * s.k, 2.4), max(0.16 * s.k, 1.4)
    s.rect(x_ - w_ / 2, y_ - h_ / 2, w_, h_, "k w2 fk")


# ==========================================================================
# VC-02  Plan général du bassin  1/50 (villa at the top, driveway on the left, as VB-02 / PL-03)
# ==========================================================================

def vc02():
    s = S("c2")
    UMIN, VMIN, VMAX = 3.95, 16.85, 25.20
    P, k = rot_view(300, 22, UMIN, VMIN, 50)
    s.k = k
    UMAX = UMIN + (300 - 22) / k
    Lp = lambda x, y: P(*pool_xy(x, y))
    y_b = 22 + (VMAX - VMIN) * k
    s.add(f'<defs><clipPath id="c2v"><rect x="22" y="22" width="278" height="{y_b - 22:.2f}"/></clipPath></defs><g clip-path="url(#c2v)">')
    s.pl([P(*p) for p in rect_uv(UMIN, VMIN, UMAX, VMAX)], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], VMIN, HOUSE["u1"], DECK[1])], "k w1 ftl", True)
    s.pl([Lp(-WALK, -WALK), Lp(POOL_L + WALK, -WALK), Lp(POOL_L + WALK, POOL_W + WALK), Lp(-WALK, POOL_W + WALK)], "k w2 fs", True)
    for i in range(int(POOL_L / 0.5) + 1):
        s.line(Lp(i * 0.5, -WALK), Lp(i * 0.5, 0), "k w1")
        s.line(Lp(i * 0.5, POOL_W), Lp(i * 0.5, POOL_W + WALK), "k w1")
    for i in range(int(POOL_W / 0.5) + 1):
        s.line(Lp(-WALK, i * 0.5), Lp(0, i * 0.5), "k w1")
        if not (CASCADE["y0"] - 1e-6 < i * 0.5 < CASCADE["y1"] + 1e-6):
            s.line(Lp(POOL_L, i * 0.5), Lp(POOL_L + WALK, i * 0.5), "k w1")
    s.pl([Lp(POOL_L, CASCADE["y0"]), Lp(POOL_L + WALK + 0.30, CASCADE["y0"]), Lp(POOL_L + WALK + 0.30, CASCADE["y1"]), Lp(POOL_L, CASCADE["y1"])], "k w1 fgz", True)
    s.pl([Lp(-0.23, -0.23), Lp(POOL_L + 0.23, -0.23), Lp(POOL_L + 0.23, POOL_W + 0.23), Lp(-0.23, POOL_W + 0.23)], "k w1 dash", True)
    draw_cascade_plan(s, P)
    s.pl([Lp(0, 0), Lp(POOL_L, 0), Lp(POOL_L, POOL_W), Lp(0, POOL_W)], "red w4 fw", True)
    for x in (DEEP_FLAT, SLOPE_END):
        s.line(Lp(x, 0), Lp(x, POOL_W), "k w1 dash")
    s.line(Lp(BREAK_X, 0), Lp(BREAK_X, POOL_W), "k w3 dash")
    for i in range(STEP["n_tread"] + 1):
        xx = POOL_L - i * STEP["tread"]
        s.line(Lp(xx, 0), Lp(xx, STEP["width"]), "k w2")
    s.line(Lp(STEP["x0"], STEP["width"]), Lp(POOL_L, STEP["width"]), "k w2")
    draw_pit_plan(s, P)
    # networks
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - 0.53, POOL["v0"] - 0.53, POOL["u1"] + 0.53, POOL["v1"] + 0.53)], "pipe-d w1", True)
    tube(s, [Lp(PUMP_C["x"], PUMP_C["y0"] - 0.06), Lp(0.05, OUT_STUB_Y)] + [P(*p) for p in ROUTES["T0"]], "t0", 1.3)
    tube(s, [P(*p) for p in ROUTES["T2"]], "t2", 1.3)
    tube(s, [P(*p) for p in ROUTES["T1"]], "t1", 1.3)
    s.pl([P(*p) for p in ROUTES["DC"]] + [Lp(0.03, CABLE_Y)], "selv w3")
    s.pl([P(*p) for p in ROUTES["LIGHT"]], "selv w3")
    for (x, y) in FITTINGS["lights"]:
        s.line(P(U0 + x, V0 - 0.40), P(U0 + x, V0), "selv w3")
    draw_rv_plan(s, P)
    s.add("</g>")
    for (x, y) in FITTINGS["lights"]:
        a_, b_ = Lp(x - 0.12, 0), Lp(x + 0.12, 0)
        s.arc(a_, 0.12 * k, 0.12 * k, 0, 1, b_, "k w2 flt")
    for (x, y) in FITTINGS["ladder"]:
        s.pl([Lp(x - 0.25, 0), Lp(x + 0.25, 0), Lp(x + 0.25, 0.45), Lp(x - 0.25, 0.45)], "k w1 fs", True)
        for j in range(3):
            s.line(Lp(x - 0.25, (j + 0.5) * 0.15), Lp(x + 0.25, (j + 0.5) * 0.15), "k w1")
    # tags
    def tag(x, y, t_, a="middle", c="t lab b"):
        s.t(x, y, t_, c, a)
    for i, (x, y) in enumerate(FITTINGS["lights"]):
        x_, y_ = Lp(x, 0.45)
        tag(x_, y_ + 1.0, f"P{i + 1}")
    x_, y_ = Lp(FITTINGS["ladder"][0][0], 0.70)
    tag(x_, y_ + 1.0, "ECH")
    x_, y_ = Lp(PIT["x1"] + 0.08, (PIT["y0"] + PIT["y1"]) / 2)
    tag(x_ - 0.6, y_ + 1.0, "PU", "end")
    x_, y_ = P(RV["u"], RV["v"] - RV["a"] / 2)
    tag(x_, y_ - 1.6, "RV", "middle", "t lab b red-t")
    x_, y_ = P((POOL["u1"] + CASC_BACK) / 2, CASC_V[0])
    tag(x_, y_ - 1.6, "CAS", "middle", "t lab b red-t")
    x_, y_ = P((WALL_OUT + RV["u"]) / 2 + 0.05, V0 + OUT_STUB_Y)
    tag(x_, y_ + 4.0, "T0", "middle", "t lab b")
    x_, y_ = P(10.5, NE_A2)
    s.t(x_, y_ + 4.6, "tube 2 Ø63 → cascade", "t tiny2 b", "middle")
    x_, y_ = P(4.60, RV["v"])
    s.t(x_, y_ - 1.4, "tube 1 → verger", "t tiny2 b", "middle")
    x_, y_ = P(5.05, AL["v"])
    s.t(x_, y_ - 1.4, "câble 24 V → AL", "t tiny2", "middle")
    x_, y_ = P(9.0, V0 - 0.40)
    s.t(x_, y_ - 4.2, "câbles 12 V des projecteurs (depuis AL)", "t tiny2", "middle")
    # depth info
    x_, y_ = Lp(BREAK_X - 0.12, 2.5)
    s.t(x_, y_, f"rupture de pente - prof. {WATER_BREAK:.2f}", "t tiny2 b", "middle", -90)
    x_, y_ = Lp(7.90, 3.55)
    s.t(x_, y_, f"ZONE ENFANTS - prof. {WATER_SHALLOW:.2f}", "t lab b")
    for x, txt in [(1.05, f"fond {FLOOR_DEEP:+.2f}"), (BREAK_X + 0.35, f"fond {FLOOR_BREAK:+.2f}"), (SLOPE_END + 0.35, f"fond {FLOOR_SHALLOW:+.2f}")]:
        x_, y_ = Lp(x, 4.45)
        s.level(x_, y_, txt, "l")
    x_, y_ = Lp(5.4, 1.30)
    s.t(x_, y_, "BASSIN 10.00 × 5.00 - plan d'eau 50 m² (inchangé)", "t lab b red-t")
    s.t(x_, y_ + 6.0, f"Volume {hu(Q['water_vol'])} m³ - profil et structure de l'indice E", "t lab red-t")
    x_, y_ = P(11.5, 17.35)
    s.t(x_, y_, "Plage solarium (inchangée)", "t lab mute")
    # dimensions
    vb = POOL["v1"] + WALK
    chain = [CASC_BACK, POOL["u1"], U0, U0 - WALK, RV["u"]]
    for a_, b_ in zip(chain, chain[1:]):
        s.dim(P(a_, vb), P(b_, vb), -7, f"{a_ - b_:.2f}")
    x_, y_ = P((POOL["u0"] + POOL["u1"]) / 2, vb)
    s.t(x_, y_ + 15.5, f"Tube 2 Ø63 en tranchée le long du côté NE, axe {RV['z_pipe']:+.2f} - essai de pression 24 h avant remblai", "t lab")
    ys = [0, CASCADE["y0"], CASCADE["y1"], POOL_W]
    for a_, b_ in zip(ys, ys[1:]):
        s.dim(P(POOL["u1"] + WALK, V0 + a_), P(POOL["u1"] + WALK, V0 + b_), -10, f"{b_ - a_:.2f}", size=2.6)
    xn = 2.25
    yn = [0, PIT["y0"], PIT["y1"], POOL_W]
    for a_, b_ in zip(yn, yn[1:]):
        s.dim(Lp(xn, a_), Lp(xn, b_), 0, f"{b_ - a_:.2f}", size=2.6)
    s.dim(Lp(PIT["x0"], PIT["y0"]), Lp(PIT["x1"], PIT["y0"]), -3, f"{PIT['x1'] - PIT['x0']:.2f}", size=2.6)
    s.dim(P(RV["u"] - 0.40, V0), P(RV["u"] - 0.40, RV["v"]), 0, f"{RV['v'] - V0:.2f}", size=2.6)
    # section marks + callouts
    sec_mark(s, P(UMAX - 0.12, V0 + SEC_A_Y), P(UMIN + 0.20, V0 + SEC_A_Y), "A")
    sec_mark(s, P(U0 + SEC_B_X, VMIN + 0.60), P(U0 + SEC_B_X, VMAX - 0.35), "B")
    sec_mark(s, P(POOL["u1"] - 0.70, CASC_MID), P(CASC_BACK + 0.22, CASC_MID), "C")
    x_, y_ = Lp(0.95, PIT["y1"] + 0.45)
    callout(s, x_, y_, "D1", "VC-04")
    x_, y_ = Lp(POOL_L - 0.60, POOL_W - 0.35)
    callout(s, x_, y_, "D2", "VC-06")
    x_, y_ = P(RV["u"] - 0.80, RV["v"] + 0.60)
    callout(s, x_, y_, "D3", "VC-06")
    band_north(s, 180 - U_ANG)
    # legend, network legend, levels, notes
    lg = [("PU", f"Puisard {CAGE['L']:.2f} × {CAGE['W']:.2f} × {PIT['depth']:.2f} (fond {PIT['floor']:+.2f}) sous cage inox perforée au ras du fond, pompe 24 V couchée (VC-04)"),
          ("T0", "Sortie de la pompe Ø63 à travers le voile NO, jusqu'au regard RV"),
          ("RV", f"Regard {RV['a']:.2f} × {RV['a']:.2f}, couvercle au ras du sol : té, vanne V1 (tube 1) et vanne V2 (tube 2)"),
          ("CAS", f"Mur de cascade {CASCADE['y1'] - CASCADE['y0']:.2f} × {CASCADE['thick']:.2f}, arase {CASCADE['top']:+.2f}, lame 600 × 6 mm à {SLOT['level']:+.2f} (tube 2)"),
          ("AL", f"Boîtier électrique sur poteau, à {U0 - AL['u']:.2f} m du bassin, hors de ce plan (VC-07)"),
          ("P1-P3, ECH", "Projecteurs LED 12 V et échelle inox 316L (inchangés)")]
    s.t(24, 196, "REPÈRES", "t cl", "start")
    table(s, 24, 198, ("Repère", "Désignation"), lg, (20, 136), rh=4.6, size=2.5)
    legend_c(s, 186, 195, w=76)
    lv = [("Margelle / plan d'eau", f"{LV['coping']:+.2f} / {LV['water']:+.2f}"), ("Arase cascade / lame d'eau", f"{CASCADE['top']:+.2f} / {SLOT['level']:+.2f}"),
          ("Couvercle du regard RV", f"{RV['top']:+.2f}"), ("Tubes dans RV (T0, tube 2)", f"{RV['z_pipe']:+.2f}"),
          ("Fond du bassin (grand fond)", f"{FLOOR_DEEP:+.2f}"), ("Axe de la pompe", f"{PUMP_C['axis']:+.2f}"), ("Fond du puisard", f"{PIT['floor']:+.2f}")]
    s.t(186, 236, "NIVEAUX (±0.00 = sol fini RDC)", "t cl", "start")
    table(s, 186, 238, ("Élément", "Niveau"), lv, (88, 34), rh=4.3, size=2.5, align="lr")
    notes = ["Même bassin que l'indice E : dimensions, implantation, niveaux, profil du fond, structure, finitions.",
             "Supprimés : local technique, filtre, bondes BF1-BF2, prise balai, skimmers SK1-SK2, buses R1-R4.",
             "Ajoutés : puisard + cage + pompe 24 V, regard RV, mur de cascade, boîtier AL.",
             "Pièces à sceller posées avant coulage ; tranchées remblayées après l'essai de pression 24 h."]
    s.t(24, 236, "NOTES", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(24, 242 + i * 4.6, n, "t tiny2", "start")
    return _frame(s, "VC-02", "VC-02 Plan général")


# ==========================================================================
# VC-03  Coupes A-A (longitudinale) et B-B (dans l'axe de la pompe)  1/50, aciers
# ==========================================================================

def vc03():
    s = S("c3")
    k = 20
    fin = FINISH
    pc = PUMP_C
    zb_deep = FLOOR_DEEP - fin - SLAB - BLIND - HERISSON
    pit_floor = PIT["floor"]
    pit_struct = pit_floor - fin - 0.20
    zb_pit = pit_struct - BLIND - HERISSON
    sx0, sx1 = PIT["x0"], PIT["x1"]
    # ---------------- A-A : pool-local x, looking SW (towards the villa), NW on the right
    XMIN, XMAX = -2.20, 11.15
    XR = 292
    X = lambda x: XR - (x - XMIN) * k
    Z = lambda z: 34 + (0.15 - z) * k
    wall_o = -(fin + WALL)
    _earth(s, X, Z, XMIN, XMAX, LV["tn"], zb_pit - 0.30)
    for (xa, xb_) in ((POOL_L + fin + WALL, POOL_L + fin + WALL + 0.45), (wall_o - 0.45, wall_o)):
        s.pl([(X(xa), Z(LV["tn"])), (X(xb_), Z(LV["tn"])), (X(xb_), Z(FLOOR_DEEP - 0.5 if xa < 0 else FLOOR_SHALLOW - 0.5)), (X(xa), Z(FLOOR_DEEP - 0.5 if xa < 0 else FLOOR_SHALLOW - 0.5))], "k w1 fgr", True)
    prof = list(PROFILE)
    xl, xr_ = wall_o, POOL_L + fin + WALL

    def band(off_top, off_bot, cls):
        top = [(xl, prof[0][1] - off_top)] + [(x, z - off_top) for x, z in prof] + [(xr_, prof[-1][1] - off_top)]
        bot = [(xr_, prof[-1][1] - off_bot)] + [(x, z - off_bot) for x, z in reversed(prof)] + [(xl, prof[0][1] - off_bot)]
        s.pl([(X(a), Z(b)) for a, b in top + bot], cls, True)
    band(fin + SLAB + BLIND, fin + SLAB + BLIND + HERISSON, "k w1 fst")
    band(fin + SLAB, fin + SLAB + BLIND, "k w1 fs")
    band(fin, fin + SLAB, "k w3 fcc")
    s.pl([(X(wall_o), Z(FLOOR_DEEP - fin - SLAB)), (X(sx1 + 0.20 + fin), Z(FLOOR_DEEP - fin - SLAB)), (X(sx1 + 0.20 + fin), Z(zb_pit)), (X(wall_o), Z(zb_pit))], "k w1 fst", True)
    s.pl([(X(wall_o), Z(FLOOR_DEEP - fin)), (X(sx1 + 0.20 + fin), Z(FLOOR_DEEP - fin)), (X(sx1 + 0.20 + fin), Z(pit_struct)), (X(wall_o), Z(pit_struct))], "k w3 fcc", True)
    for xa in (wall_o, POOL_L + fin):
        zbot = (prof[0][1] if xa < 0 else prof[-1][1]) - fin
        s.rect(min(X(xa), X(xa + WALL)), Z(LV["beam_top"]), WALL * k, (LV["beam_top"] - zbot) * k, "k w3 fcc")
    for xa in (-WALK - 0.03, POOL_L - 0.03):
        s.rect(min(X(xa), X(xa + 0.53)), Z(LV["coping"]), 0.53 * k, 0.07 * k, "k w2 fs")
    # cascade (cut at y = 2.70)
    s.pl([(X(POOL_L), Z(CASCADE["top"])), (X(POOL_L + CASCADE["thick"]), Z(CASCADE["top"])), (X(POOL_L + CASCADE["thick"]), Z(LV["beam_top"])), (X(POOL_L), Z(LV["beam_top"]))], "red w3 fcc", True)
    s.pl([(X(POOL_L - 0.08), Z(SLOT["level"])), (X(POOL_L + 0.05), Z(SLOT["level"]))], "red w4")
    s.add(f'<path d="M{X(POOL_L - 0.08):.2f} {Z(SLOT["level"]):.2f} q {0.10 * k:.2f} {0.05 * k:.2f} {0.13 * k:.2f} {(SLOT["level"] - LV["water"]) * k:.2f}" class="red w2"/>')
    # water, pit, steps, lights, ladder
    wpts = [(0, LV["water"])] + [(x, z) for x, z in prof] + [(POOL_L, LV["water"])]
    s.pl([(X(a), Z(b)) for a, b in wpts], "k w1 fw", True)
    s.pl([(X(sx0), Z(FLOOR_DEEP)), (X(sx1), Z(FLOOR_DEEP)), (X(sx1), Z(pit_floor)), (X(sx0), Z(pit_floor))], "k w1 fw", True)
    s.line((X(sx0), Z(FLOOR_DEEP)), (X(sx1), Z(FLOOR_DEEP)), "k w4")
    sp = [(POOL_L, LV["coping"] - STEP["rise"])]
    for i in range(STEP["n_tread"]):
        xa = POOL_L - STEP["tread"] * (i + 1)
        z1 = LV["coping"] - STEP["rise"] * (i + 1)
        sp += [(xa, z1), (xa, z1 - STEP["rise"])]
    s.pl([(X(a), Z(b)) for a, b in sp + [(POOL_L, FLOOR_SHALLOW)]], "k w1")
    for (x, y) in FITTINGS["lights"]:
        s.circ(X(x), Z(LV["water"] - LIGHT_DEPTH), 1.4, "k w1 flt")
    s.rect(X(FITTINGS["ladder"][0][0] + 0.25), Z(LV["coping"]), 0.5 * k, 1.2 * k, "k w1 dash")
    # pump cut through the motor, cradle
    s.add(f'<circle cx="{X(pc["x"]):.2f}" cy="{Z(pc["axis"]):.2f}" r="{pc["sleeve_D"] / 2 * k:.2f}" style="fill:#7cc3dc;fill-opacity:.2;stroke:#1683a8;stroke-width:.3;stroke-dasharray:1 .6"/>')
    s.add(f'<circle cx="{X(pc["x"]):.2f}" cy="{Z(pc["axis"]):.2f}" r="{pc["D"] / 2 * k:.2f}" style="fill:#c3ccd3;stroke:var(--ink);stroke-width:.3"/>')
    s.rect(X(pc["x"] + 0.09), Z(pit_floor + pc["cradle"]), 0.18 * k, pc["cradle"] * k, "k w1 fk")
    # T0 and the valve box beyond (y = 1.62)
    tube(s, [(X(0.02), Z(STUB_Z)), (X(wall_o - 0.12), Z(STUB_Z)), (X(wall_o - 0.12), Z(RV["z_pipe"])), (X(RV["u"] - U0), Z(RV["z_pipe"]))], "t0", 1.26, 0.55)
    a = RV["a"] / 2
    s.pl([(X(RV["u"] - U0 - a - 0.06), Z(RV["top"])), (X(RV["u"] - U0 + a + 0.06), Z(RV["top"])), (X(RV["u"] - U0 + a + 0.06), Z(RV["bottom"] - 0.06)), (X(RV["u"] - U0 - a - 0.06), Z(RV["bottom"] - 0.06))], "k w1 dash", True)
    s.line((X(RV["u"] - U0 - a - 0.06), Z(RV["top"])), (X(RV["u"] - U0 + a + 0.06), Z(RV["top"])), "red w3")
    # tube 2 rising in the cascade (beyond, at y = 3.50)
    tube(s, [(X(CASC_BACK - 0.08 - U0), Z(RV["z_pipe"])), (X(CASC_BACK - 0.08 - U0), Z(SLOT["level"] - 0.01)), (X(POOL_L + fin + 0.11), Z(SLOT["level"] - 0.01))], "t2", 1.26, 0.55)
    s.line((X(XMIN), Z(LV["tn"])), (X(-WALK - 0.03), Z(LV["tn"])), "k w2")
    s.line((X(POOL_L + 0.5), Z(LV["tn"])), (X(XMAX), Z(LV["tn"])), "k w2")
    for z, txt, xx, sd in [(LV["water"], f"{LV['water']:+.2f} eau", 4.0, "r"), (LV["coping"], f"{LV['coping']:+.2f}", 9.0, "r"),
                           (FLOOR_DEEP, f"{FLOOR_DEEP:+.2f}", 1.45, "r"), (pit_floor, f"{pit_floor:+.2f} puisard", -0.80, "r"),
                           (FLOOR_SHALLOW, f"{FLOOR_SHALLOW:+.2f}", 8.2, "r"), (CASCADE["top"], f"{CASCADE['top']:+.2f} arase", POOL_L + 0.20, "l"),
                           (SLOT["level"], f"{SLOT['level']:+.2f} lame", POOL_L - 0.35, "l"), (RV["top"], f"{RV['top']:+.2f} RV", -1.75, "r")]:
        s.level(X(xx), Z(z), txt, side=sd, section=True)
    s.dim((X(1.35), Z(LV["water"])), (X(1.35), Z(FLOOR_DEEP)), 0, f"{WATER_DEEP:.2f}")
    s.dim((X(sx1 + 0.08), Z(FLOOR_DEEP)), (X(sx1 + 0.08), Z(pit_floor)), 0, f"{PIT['depth']:.2f}", size=2.4)
    chain = [RV["u"] - U0, wall_o, 0, sx1, POOL_L, POOL_L + CASCADE["thick"]]
    zz = Z(zb_pit - 0.30) + 5
    for a_, b_ in zip(chain, chain[1:]):
        s.dim((X(a_), zz), (X(b_), zz), 0, f"{abs(b_ - a_):.2f}")
    s.t(X(pc["x"]), Z(pit_floor - 0.62), "PU", "t tiny2 b")
    s.t(X(RV["u"] - U0), Z(RV["top"] + 0.22), "RV (au-delà)", "t tiny2 b red-t")
    s.t(X(wall_o - 0.12) + 1.5, Z(-1.75), "T0 (au-delà)", "t tiny2", "start")
    s.t(X(POOL_L + 0.20), Z(CASCADE["top"] + 0.32), "CAS", "t tiny2 b red-t")
    s.t(X(POOL_L + 0.20) - 2.5, Z(-0.95) + 1, "tube 2 (au-delà)", "t tiny2", "end")
    s.t(X(POOL_L / 2), 22, f"COUPE A-A  (longitudinale à {SEC_A_Y:.2f} du bord SO, vue vers la villa)  1/50", "t ct", "middle")
    s.t(X(0.25), zz + 7, "GRAND FOND - PUISARD (côté NO)", "t tiny2 b", "middle")
    s.t(X(POOL_L - 1.25), zz + 7, "PETIT BAIN - CASCADE (côté allée)", "t tiny2 b", "middle")
    # ---------------- B-B : across the pool at the pump axis, looking NW, v to the right
    VMIN = POOL["v0"] - 2.40
    Xb = lambda v: 24 + (v - VMIN) * k
    Zb = lambda z: 150 + (0.15 - z) * k
    vmax = POOL["v1"] + 1.60
    pv0, pv1 = POOL["v0"], POOL["v1"]
    s.pl([(Xb(VMIN), Zb(LV["tn"])), (Xb(vmax), Zb(LV["tn"])), (Xb(vmax), Zb(zb_pit - 0.30)), (Xb(VMIN), Zb(zb_pit - 0.30))], "k w1 fea", True)
    s.rect(Xb(pv0 - WALL - fin - 0.45), Zb(LV["tn"]), (POOL_W + 2 * (WALL + fin + 0.45)) * k, (LV["tn"] - (FLOOR_DEEP - fin - SLAB)) * k, "k w1 fgr")
    s.rect(Xb(pv0 - WALL - fin - 0.45), Zb(FLOOR_DEEP - fin - SLAB), (POOL_W + 2 * (WALL + fin + 0.45)) * k, (BLIND + HERISSON) * k, "k w1 fst")
    s.rect(Xb(pv0 - WALL - fin), Zb(FLOOR_DEEP - fin), (POOL_W + 2 * (WALL + fin)) * k, SLAB * k, "k w3 fcc")
    sy0, sy1 = pv0 + PIT["y0"], pv0 + PIT["y1"]
    s.rect(Xb(sy0 - 0.20 - fin), Zb(FLOOR_DEEP - fin - SLAB), (sy1 - sy0 + 0.40 + 2 * fin) * k, (FLOOR_DEEP - fin - SLAB - zb_pit) * k, "k w1 fst")
    s.rect(Xb(sy0 - 0.20 - fin), Zb(FLOOR_DEEP - fin), (sy1 - sy0 + 0.40 + 2 * fin) * k, (FLOOR_DEEP - fin - pit_struct) * k, "k w3 fcc")
    for vv in (pv0 - WALL - fin, pv1 + fin):
        s.rect(Xb(vv), Zb(LV["beam_top"]), WALL * k, (LV["beam_top"] - (FLOOR_DEEP - fin)) * k, "k w3 fcc")
    s.rect(Xb(pv0), Zb(LV["water"]), POOL_W * k, (LV["water"] - FLOOR_DEEP) * k, "k w1 fw")
    s.rect(Xb(sy0), Zb(FLOOR_DEEP), (sy1 - sy0) * k, PIT["depth"] * k, "k w1 fw")
    s.line((Xb(sy0), Zb(FLOOR_DEEP)), (Xb(sy1), Zb(FLOOR_DEEP)), "k w4")
    for vv in (pv0 - WALK, pv1 - 0.03):
        s.rect(Xb(vv), Zb(LV["coping"]), 0.53 * k, 0.07 * k, "k w2 fs")
    s.pl([(Xb(VMIN), Zb(LV["deck_low"])), (Xb(pv0 - WALK), Zb(LV["deck_edge"])), (Xb(pv0 - WALK), Zb(LV["deck_edge"] - 0.12)), (Xb(VMIN), Zb(LV["deck_low"] - 0.12))], "k w1 fs", True)
    # the pump lying in the pit (side view), its hose to T0 and its cable to the conduit (on the NW wall, behind)
    Yb = lambda y: Xb(pv0 + y)
    for yy in (pc["y0"] + 0.25, (pc["y_inlet"] + pc["y1"]) / 2, pc["y1"] - 0.12):
        s.rect(Yb(yy) - 0.4, Zb(pc["axis"] - pc["sleeve_D"] / 2), 0.8, (pc["axis"] - pc["sleeve_D"] / 2 - pit_floor) * k, "k w1 fk")
    ex, ez = pump_side(s, Yb, Zb(pc["axis"]), k)
    tube(s, [(Yb(pc["y0"] - 0.075), Zb(pc["axis"])), (Yb(OUT_STUB_Y), Zb(STUB_Z))], "t0", 0.8)
    s.circ(Yb(OUT_STUB_Y), Zb(STUB_Z), 0.9, "k w2 fs")
    blue_cable(s, [(ex, ez), (ex - 0.6, ez - 1.2), (Yb(CABLE_Y), Zb(STUB_Z))], 0.4)
    s.circ(Yb(CABLE_Y), Zb(STUB_Z), 0.6, "k w1 fs")
    for vv in (pv0 - WALL - fin - 0.30, pv1 + WALL + fin + 0.30):
        s.circ(Xb(vv), Zb(FLOOR_DEEP - fin - SLAB + 0.05), 0.9, "pipe-d w2")
    s.add(f'<circle cx="{Xb(NE_A2):.2f}" cy="{Zb(RV["z_pipe"]):.2f}" r="1.26" style="fill:#ffffff;stroke:{TUBE["t2"][0]};stroke-width:.6"/>')
    s.line((Xb(pv1 + 0.5), Zb(LV["tn"])), (Xb(vmax), Zb(LV["tn"])), "k w2")
    for z, txt, vv, sd in [(LV["water"], f"{LV['water']:+.2f}", pv0 + 0.6, "r"), (FLOOR_DEEP, f"{FLOOR_DEEP:+.2f}", pv0 + 0.55, "r"),
                           (pit_floor, f"{pit_floor:+.2f}", sy1 + 0.1, "r"), (LV["deck_low"], f"{LV['deck_low']:+.2f} plage", VMIN + 0.4, "r"),
                           (LV["tn"], f"{LV['tn']:+.2f} TN", pv1 + 0.9, "r")]:
        s.level(Xb(vv), Zb(z), txt, side=sd, section=True)
    zz = Zb(zb_pit - 0.30) + 5
    ch = [pv0, sy0, sy1, pv1]
    for a_, b_ in zip(ch, ch[1:]):
        s.dim((Xb(a_), zz), (Xb(b_), zz), 0, f"{b_ - a_:.2f}")
    s.dim((Yb(pc["y0"]), Zb(pc["axis"]) - 6), (Yb(pc["y1"]), Zb(pc["axis"]) - 6), 0, f"pompe {pc['L']:.2f}", size=2.4)
    s.t(Xb(pv0 + 2.5), Zb(-1.55), "pompe 24 V couchée sous la cage", "t tiny2", "middle")
    s.t(Xb(pv1 + 0.95), Zb(-1.62), "tube 2", "t tiny2", "middle")
    s.t(Xb((VMIN + vmax) / 2), 138, "COUPE B-B  (dans l'axe de la pompe, vue vers le voile NO)  1/50", "t ct", "middle")
    # ---- hatch legend + key plan (right of B-B)
    lg = [("k w2 fcc", "Béton armé B25 + hydrofuge"), ("k w1 fst", "Hérisson 40/80"), ("k w1 fgr", "Gravier drainant 15/25"),
          ("k w1 fea", "Terrain en place"), ("k w1 fw", "Eau")]
    s.t(222, 146, "HACHURES", "t cl", "start")
    for i, (c_, t_) in enumerate(lg):
        s.rect(222, 149 + i * 6, 9, 4.2, c_)
        s.t(234, 152.4 + i * 6, t_, "t cs", "start")
    kp, kk = (300, 192), 4.0
    KP = lambda u, v: (kp[0] - (u - 2.4) * kk, kp[1] + (v - POOL["v0"] + 0.8) * kk)
    s.t(222, 186, "PLAN DE REPÉRAGE  1/250", "t cl", "start")
    s.pl([KP(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w2 fw", True)
    s.pl([KP(*p) for p in rect_uv(U0 + PIT["x0"], V0 + PIT["y0"], U0 + PIT["x1"], V0 + PIT["y1"])], "k w2 fs", True)
    s.pl([KP(*p) for p in rect_uv(POOL["u1"], CASC_V[0], CASC_BACK, CASC_V[1])], "red w2 fcc", True)
    x_, y_ = KP(RV["u"], RV["v"])
    s.rect(x_ - 0.8, y_ - 0.8, 1.6, 1.6, "red w1 fs")
    x_, y_ = KP(AL["u"], AL["v"])
    s.rect(x_ - 0.8, y_ - 0.8, 1.6, 1.6, "k w1 fk")
    s.t(x_, y_ + 4.2, "AL", "t tiny")
    for (a_, b_, nm) in (((RV["u"] - 0.6, V0 + SEC_A_Y), (CASC_BACK + 0.6, V0 + SEC_A_Y), "A"), ((U0 + SEC_B_X, V0 - 0.6), (U0 + SEC_B_X, POOL["v1"] + 0.6), "B")):
        pa, pb = KP(*a_), KP(*b_)
        s.line(pa, pb, "k w1 axis")
        for pp in (pa, pb):
            s.circ(pp[0], pp[1], 1.8, "k w1 fs")
            s.t(pp[0], pp[1] + 0.9, nm, "t tiny2 b")
    x_, y_ = KP((POOL["u0"] + POOL["u1"]) / 2, POOL["v0"] - 0.9)
    s.t(x_, y_, "villa", "t tiny mute")
    # ---- rebar of the variant + notes
    rb = [(str(b["pos"]), b["desc"], f"HA{b['d']}", str(b["n"]), f"{b['L']:.2f}", f"{b['kg']:.1f}") for b in RC["rebar"]]
    rb.append(("", "Total variante (en plus de la nomenclature PL-05)", "", "", "", f"{RC['steel']:.1f}"))
    s.t(170, 242, "ACIERS DE LA VARIANTE C (FeE500)", "t cl", "start")
    table(s, 170, 244, ("Rep.", "Désignation", "Ø", "Nb", "L (m)", "kg"), rb, (9, 88, 10, 9, 11, 14), rh=4.4, size=2.3)
    pl_, pw_, pd_ = RC["caisson"]
    notes = ["Le bassin de l'indice E est conservé : radier, voiles, chaînage, profil du fond.",
             f"Seul ajout sous le radier : le caisson du puisard {pl_:.2f} × {pw_:.2f} × {pd_:.2f}, coulé avec le radier.",
             "Ouverture du radier bordée de chevêtres HA12 (repère 16) ; cage posée au ras du fond.",
             "Membrane du bassin continue dans le puisard ; une seule sortie (T0) et un fourreau",
             "de câble traversent le voile NO, par fourreaux à collerette posés avant coulage.",
             f"Béton du caisson : {RC['c_pit']:.2f} m³ ; surface étanchée du puisard : {RC['pit_surf']:.2f} m².",
             "Prédimensionnement BAEL 91 mod. 99 à faire vérifier et viser par un BET agréé (RPS 2000)."]
    s.t(24, 242, "NOTES", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(24, 248 + i * 4.6, n, "t tiny2", "start")
    return _frame(s, "VC-03", "VC-03 Coupes")


# ==========================================================================
# VC-06  Tracés 1/200, coupe de la cascade 1/20, regard RV 1/10, positions des vannes, pertes de charge
# ==========================================================================

def vc06():
    s = S("c6")
    # ---- routes 1/200 (rotated like PL-02: villa at the top, NW on the right)
    UMIN, VMIN = 1.2, 12.6
    P, k = rot_view(118, 24, UMIN, VMIN, 200)
    s.k = k
    s.add('<defs><clipPath id="c6p"><rect x="22" y="22" width="96" height="98"/></clipPath></defs><g clip-path="url(#c6p)">')
    s.pl([P(*p) for p in rect_uv(UMIN, VMIN, 21.0, 32.6)], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], VMIN, HOUSE["u1"], HOUSE["v1"])], "k w2 fhx", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - WALK, POOL["v0"] - WALK, POOL["u1"] + WALK, POOL["v1"] + WALK)], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w2 fw", True)
    s.pl([P(*p) for p in rect_uv(U0 + PIT["x0"], V0 + PIT["y0"], U0 + PIT["x1"], V0 + PIT["y1"])], "k w2 fs", True)
    draw_cascade_plan(s, P)
    x_, y_ = P(SOAKAWAY["u"], SOAKAWAY["v"])
    s.circ(x_, y_, SOAKAWAY["r"] * k, "k w1 fst")
    tube(s, [P(*p) for p in ROUTES["T0"]], "t0", 0.9)
    tube(s, [P(*p) for p in ROUTES["T2"]], "t2", 0.9)
    tube(s, [P(*p) for p in ROUTES["T1"]], "t1", 0.9)
    s.pl([P(*p) for p in ROUTES["DC"]], "selv w2")
    s.pl([P(*p) for p in ROUTES["LIGHT"]], "selv w1")
    s.pl([P(*p) for p in ROUTES["CABLE"]], "elec w2")
    draw_rv_plan(s, P, "red w2 fs")
    draw_al_plan(s, P)
    s.add("</g>")
    for t_, (u, v), a in (("puisard", (POOL["u0"] + 0.30, POOL["v0"] + 3.4), "start"), ("RV", (RV["u"] - 0.4, RV["v"] - 0.5), "start"), ("AL", (AL["u"] - 0.5, AL["v"] + 0.4), "start"),
                          ("cascade", (CASC_BACK + 0.3, CASC_V[1] + 0.9), "end"), ("TGBT villa", (COFFRET["u"], COFFRET["v"] - 0.5), "middle"),
                          ("tube 2", ((POOL["u0"] + POOL["u1"]) / 2, POOL["v1"] + 1.5), "middle"), ("tube 1", (ROUTES["T1"][1][0] + 0.4, 27.5), "end"),
                          ("puits perdu", (SOAKAWAY["u"], SOAKAWAY["v"] - 1.3), "middle")):
        x_, y_ = P(u, v)
        s.t(x_, y_, t_, "t tiny2 b", a)
    s.t(70, 20, "TRACÉS  1/200", "t cl", "middle")
    # ---- cascade C-C 1/20 : tube 2 rises in the wall to the distribution chamber
    K = 50
    FX = lambda u: 132 + (u - (POOL["u1"] - 0.30)) * K
    FZ = lambda z: 30 + (0.02 - z) * K
    core0, core1 = POOL["u1"] + FINISH, POOL["u1"] + FINISH + WALL
    zb_slab = FLOOR_SHALLOW - FINISH - SLAB
    s.add('<defs><clipPath id="c6c"><rect x="126" y="26" width="86" height="94"/></clipPath></defs><g clip-path="url(#c6c)">')
    s.rect(FX(core1), FZ(LV["tn"]), 0.80 * K, (LV["tn"] + 1.95) * K, "k w1 fea")
    s.rect(FX(core1), FZ(LV["beam_top"]), 0.45 * K, (LV["beam_top"] - zb_slab) * K, "k w1 fgr")
    s.rect(FX(POOL["u1"] - 0.30), FZ(FLOOR_SHALLOW - FINISH), (core1 - POOL["u1"] + 0.30) * K, SLAB * K, "k w3 fcc")
    s.rect(FX(POOL["u1"] - 0.30), FZ(zb_slab), (core1 + 0.45 - POOL["u1"] + 0.30) * K, BLIND * K, "k w1 fs")
    s.rect(FX(core0), FZ(CASCADE["top"] - 0.05), WALL * K, (CASCADE["top"] - 0.05 - (FLOOR_SHALLOW - FINISH)) * K, "k w3 fcc")
    s.rect(FX(core1), FZ(CASCADE["top"] - 0.05), (CASC_BACK - core1) * K, (CASCADE["top"] - 0.05 - LV["beam_top"]) * K, "k w2 fea2")
    s.rect(FX(POOL["u1"] - 0.03), FZ(CASCADE["top"]), (CASCADE["thick"] + 0.06) * K, 0.05 * K, "k w2 fs")
    s.rect(FX(POOL["u1"]), FZ(LV["coping"] + 0.05), FINISH * K, (LV["coping"] + 0.05 - FLOOR_SHALLOW) * K, "k w1 fs")
    s.line((FX(POOL["u1"]), FZ(CASCADE["top"] - 0.05)), (FX(POOL["u1"]), FZ(FLOOR_SHALLOW)), "memb")
    s.line((FX(POOL["u1"] - 0.30), FZ(FLOOR_SHALLOW)), (FX(POOL["u1"]), FZ(FLOOR_SHALLOW)), "memb")
    s.pl([(FX(POOL["u1"] - 0.30), FZ(LV["water"])), (FX(POOL["u1"]), FZ(LV["water"])), (FX(POOL["u1"]), FZ(FLOOR_SHALLOW)), (FX(POOL["u1"] - 0.30), FZ(FLOOR_SHALLOW))], "k w1 fw", True)
    bz0, bz1 = SLOT["level"] - 0.08, SLOT["level"] + 0.07
    s.pl([(FX(core0), FZ(bz1)), (FX(core0 + 0.11), FZ(bz1)), (FX(core0 + 0.11), FZ(bz0)), (FX(core0), FZ(bz0))], "k w3 fs", True)
    s.pl([(FX(core0 + 0.11), FZ(bz1 + 0.01)), (FX(core0 + 0.11), FZ(bz1)), (FX(POOL["u1"] - 0.08), FZ(SLOT["level"] + 0.003)), (FX(POOL["u1"] - 0.08), FZ(SLOT["level"] - 0.003))], "k w2 fs")
    s.pl([(FX(core0 + 0.11), FZ(bz0)), (FX(POOL["u1"] - 0.08), FZ(SLOT["level"] - 0.010))], "k w2")
    s.add(f'<path d="M{FX(POOL["u1"] - 0.08):.2f} {FZ(SLOT["level"]):.2f} q {-0.10 * K:.2f} {0.03 * K:.2f} {-0.13 * K:.2f} {(SLOT["level"] - LV["water"]) * K:.2f}" class="pipe-s w4"/>')
    ru = CASC_BACK - 0.08
    tube(s, [(FX(ru), FZ(RV["z_pipe"])), (FX(ru), FZ(SLOT["level"] - 0.01)), (FX(core0 + 0.11), FZ(SLOT["level"] - 0.01))], "t2", 0.063 * K)
    s.circ(FX(ru), FZ(RV["z_pipe"]), 0.063 * K / 2 + 0.4, "k w2 fs")
    s.rect(FX(core1 - 0.01), FZ(SLOT["level"] + 0.04), 0.02 * K, 0.10 * K, "k w2 fk")
    s.rect(FX(core1 + 0.45), FZ(LV["tn"] + 0.05), 0.40 * K, 0.05 * K, "k w1 fgz")
    s.add("</g>")
    for z, t_, x_, sd in [(CASCADE["top"], f"{CASCADE['top']:+.2f} arase", CASC_BACK + 0.04, "r"), (SLOT["level"], f"{SLOT['level']:+.2f} lame", POOL["u1"] - 0.27, "r"),
                          (LV["water"], f"{LV['water']:+.2f} eau", POOL["u1"] - 0.27, "r"), (FLOOR_SHALLOW, f"{FLOOR_SHALLOW:+.2f} fond", POOL["u1"] - 0.27, "r"),
                          (RV["z_pipe"], f"{RV['z_pipe']:+.2f} tube 2", CASC_BACK + 0.15, "r")]:
        s.level(FX(x_), FZ(z), t_, side=sd, section=True)
    for txt, (u, z), (qx, qy) in [("chambre de répartition inox + lame 600 × 6 mm", (core0 + 0.05, bz1 - 0.02), (128, 125)),
                                  ("tube 2 Ø63 arrive de la tranchée et remonte dans le mur", (ru, -0.75), (128, 130.5))]:
        s.line((FX(u), FZ(z)), (qx + 52, qy - 1.6), "k w1")
        s.circ(FX(u), FZ(z), 0.45, "k w1 fk")
        s.t(qx, qy, txt, "t tiny2", "start", size=2.2)
    s.t(169, 20, "COUPE C-C : CASCADE (sans filtre)  1/20", "t cl", "middle")
    # ---- valve box RV 1/10 : tee, V2 on tube 2, V1 on tube 1
    K2 = 100
    RX = lambda d: 262 + d * K2
    RZ = lambda z: 30 + (-0.66 - z) * K2
    a = RV["a"] / 2
    s.rect(RX(-0.44), RZ(LV["deck_edge"]), 0.88 * K2, (RV["depth"] + 0.12) * K2, "k w1 fea")
    s.rect(RX(-a), RZ(RV["top"]), 2 * a * K2, RV["depth"] * K2, "k w1 fs")
    s.rect(RX(-a - 0.06), RZ(RV["top"]), 0.06 * K2, (RV["depth"] + 0.06) * K2, "k w2 fcc")
    s.rect(RX(a), RZ(RV["top"]), 0.06 * K2, (RV["depth"] + 0.06) * K2, "k w2 fcc")
    s.rect(RX(-a), RZ(RV["bottom"]), 2 * a * K2, 0.06 * K2, "k w1 fgr")
    s.rect(RX(-a - 0.06), RZ(RV["top"]) - 0.6, (2 * a + 0.12) * K2, 2.2, "red w2 fs")
    zz, z1 = RV["z_pipe"], RV["z_t1"]
    tube(s, [(RX(-0.44), RZ(zz)), (RX(-0.03), RZ(zz))], "t0", 6.3)
    tube(s, [(RX(0.03), RZ(zz)), (RX(0.44), RZ(zz))], "t2", 6.3)
    tube(s, [(RX(0.0), RZ(zz) + 3.2), (RX(0.0), RZ(z1)), (RX(0.44), RZ(z1))], "t1", 5.0)
    s.rect(RX(-0.035), RZ(zz) - 3.6, 0.07 * K2, 7.2, "k w2 fs")
    s.t(RX(0), RZ(zz) + 0.9, "té", "t tiny", "middle")
    valve(s, RX(0.16), RZ(zz), r=3.0)
    s.line((RX(0.16), RZ(zz)), (RX(0.16), RZ(zz) - 7), "k w3")
    s.line((RX(0.16), RZ(zz) - 7), (RX(0.26), RZ(zz) - 7), "red w4")
    valve(s, RX(0.20), RZ(z1), r=2.4)
    s.line((RX(0.20), RZ(z1)), (RX(0.20), RZ(z1) - 5), "k w3")
    s.line((RX(0.20), RZ(z1) - 5), (RX(0.29), RZ(z1) - 5), "red w4")
    for t_, (xx, yy), a_ in (("T0 (pompe)", (RX(-0.42), RZ(zz) + 6.8), "start"), ("tube 2", (RX(0.43), RZ(zz) - 4.5), "end"),
                             ("tube 1", (RX(0.43), RZ(z1) + 6.2), "end"), ("V2", (RX(0.145), RZ(zz) - 6.4), "end"), ("V1", (RX(0.30), RZ(z1) - 4.2), "start"),
                             ("couvercle au ras du sol", (RX(0), RZ(RV["top"]) - 2.6), "middle")):
        s.t(xx, yy, t_, "t tiny2 b", a_)
    s.level(RX(-0.40), RZ(RV["top"]), f"{RV['top']:+.2f}", side="l", section=True)
    s.dim((RX(-a), RZ(RV["bottom"]) + 9), (RX(a), RZ(RV["bottom"]) + 9), 0, f"{RV['a']:.2f}", size=2.4)
    s.dim((RX(-a - 0.10), RZ(RV["top"])), (RX(-a - 0.10), RZ(RV["bottom"])), 0, f"{RV['depth']:.2f}", size=2.4)
    s.t(262, 20, "REGARD DE VANNES RV  1/10", "t cl", "middle")
    s.t(262, RZ(RV["bottom"]) + 15, "V2 → tube 2 → cascade  -  V1 → tube 1 → jardin", "t tiny2", "middle", size=2.3)
    # ---- valve positions
    y0 = 134
    pos = [("Cascade (usage normal)", "fermée", "ouverte", "marche (horloge)", "tube 2 → cascade → bassin", f"{C.Q_C:.0f} m³/h", f"{RC['tdh_2'][1]:.2f} mCE"),
           ("Jardin / vidange", "ouverte, réglée", "fermée", "marche", "tube 1 → verger, puits perdu", f"{C.Q_GARDEN:.0f} m³/h", f"{RC['tdh_1'][1]:.2f} → {RC['tdh_1_end'][1]:.2f} mCE"),
           ("Arrêt, entretien", "fermée", "fermée", "arrêt (AL coupé)", "-", "0", "-")]
    s.t(24, y0 - 4, "POSITIONS DES VANNES V1 ET V2", "t cl", "start")
    table(s, 24, y0, ("Usage", "V1 (tube 1)", "V2 (tube 2)", "Pompe", "L'eau va vers", "Débit", "HMT"), pos, (40, 26, 22, 28, 54, 18, 34), rh=4.6, size=2.3, align="llllllr")
    rows = [(n, f"{v:.2f}") for n, v in RC["tdh_2"][0]] + [("HMT tube 2 (cascade)", f"{RC['tdh_2'][1]:.2f}")]
    s.t(24, 160, f"PERTES DE CHARGE - TUBE 2 À {C.Q_C:.0f} m³/h (mCE)", "t cl", "start")
    table(s, 24, 162, ("Poste", "mCE"), rows, (118, 16), rh=4.2, size=2.2, align="lr")
    r1 = RC["tdh_1"][0][:-1]
    rows1 = [(n, f"{v:.2f}") for n, v in r1] + [(RC["tdh_1"][0][-1][0], f"{RC['tdh_1'][0][-1][1]:+.2f}"), ("HMT tube 1, bassin plein", f"{RC['tdh_1'][1]:.2f}"),
                                                (RC["tdh_1_end"][0][-1][0].replace("Hauteur statique en fin de vidange : ", "Fin de vidange : "), f"{RC['tdh_1_end'][0][-1][1]:+.2f}"),
                                                ("HMT tube 1, fin de vidange", f"{RC['tdh_1_end'][1]:.2f}")]
    s.t(170, 160, f"PERTES DE CHARGE - TUBE 1 À {C.Q_GARDEN:.0f} m³/h (mCE)", "t cl", "start")
    table(s, 170, 162, ("Poste", "mCE"), rows1, (126, 16), rh=4.2, size=2.2, align="lr")
    notes = ["Sans filtre : la pompe brasse l'eau et la renvoie par la cascade, elle ne la nettoie pas. Les débris restent dans le bassin",
             "et l'eau se trouble plus vite : chlore et pH à surveiller, épuisette chaque jour, brosse sur la cage. Options possibles plus tard",
             "sans toucher au bassin : filtre à cartouche sur le tube 2 dans le mur de cascade, ou robot sans fil à filtre intégré (VC-08).",
             f"V1 reste fermée hors vidange : la sortie du puits perdu ({OUTLET['z']:+.2f}) est plus basse que l'eau ({LV['water']:+.2f}), le tube 1 se viderait",
             "seul par gravité. Vidange au verger seulement si chlore libre < 0.1 mg/L et pH 6.5 à 8.5 ; pas d'électrolyseur au sel.",
             f"Vidange complète par le tube 1 : {RC['drain_h']:.1f} h à {C.Q_GARDEN:.0f} m³/h, la pompe étant au point le plus bas ; de mai à octobre seulement (PL-05).",
             "La cascade aère l'eau : le pH monte et l'évaporation augmente. Lame inox reliée à la liaison équipotentielle (VC-07)."]
    s.t(24, 218, "NOTES", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(24, 224 + i * 4.5, n, "t tiny2", "start", size=2.35)
    return _frame(s, "VC-06", "VC-06 Tubes, regard, cascade")


# ==========================================================================
# VC-07  Sécurité électrique : volumes 1/100, boîtier AL, unifilaire, mesures
# ==========================================================================

def vc07():
    s = S("c7")
    P, k = rot_view(232, 22, -0.5, 12.4, 100)
    s.k = k
    s.add('<defs><clipPath id="c7p"><rect x="22" y="22" width="210" height="146"/></clipPath></defs><g clip-path="url(#c7p)">')
    s.pl([P(*p) for p in rect_uv(-0.5, 12.4, 20.5, 27.0)], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], 12.4, HOUSE["u1"], HOUSE["v1"])], "k w3 fhx", True)
    s.pl([P(*p) for p in rect_uv(STAIR["u0"], 12.4, STAIR["u1"], STAIR["v1"])], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], DECK[0], HOUSE["u1"], DECK[1])], "k w1 ftl", True)
    s.pl(_offset_poly(P, POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"], 3.5), "z2", True)
    s.pl(_offset_poly(P, POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"], 2.0), "z1", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - WALK, POOL["v0"] - WALK, POOL["u1"] + WALK, POOL["v1"] + WALK)], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w3 fw", True)
    s.pl([P(*p) for p in rect_uv(U0 + PIT["x0"], V0 + PIT["y0"], U0 + PIT["x1"], V0 + PIT["y1"])], "k w2 fs", True)
    draw_cascade_plan(s, P)
    draw_rv_plan(s, P, "k w1 fs")
    s.pl([P(*p) for p in ROUTES["CABLE"]], "elec w4")
    s.pl([P(*p) for p in ROUTES["DC"]] + [P(U0 + 0.05, V0 + CABLE_Y)], "selv w4")
    s.pl([P(*p) for p in ROUTES["LIGHT"]], "selv w3")
    for (x, y) in FITTINGS["lights"]:
        s.line(P(U0 + x, V0 - 0.40), P(U0 + x, POOL["v0"]), "selv w3")
        c_ = P(U0 + x, POOL["v0"])
        s.circ(c_[0], c_[1], 1.2, "k w1 flt")
    lel = (AL["u"] - 0.70, AL["v"] + 0.70)
    sw_, ne_ = POOL["v0"] - 0.25, POOL["v1"] + 0.25
    s.pl([P(*lel), P(WALL_OUT - 0.30, lel[1]), P(WALL_OUT - 0.30, sw_), P(U0 + FITTINGS["ladder"][0][0], sw_), P(U0 + FITTINGS["ladder"][0][0], POOL["v0"])], "pe")
    s.pl([P(WALL_OUT - 0.30, lel[1]), P(WALL_OUT - 0.30, ne_), P(POOL["u1"] + 0.25, ne_), P(POOL["u1"] + 0.25, CASC_MID)], "pe")
    s.pl([P(WALL_OUT - 0.30, V0 + 2.5), P(U0 + PIT["x1"], V0 + 2.5)], "pe")
    x_, y_ = P(*lel)
    s.circ(x_, y_, 1.4, "k w2 fs")
    s.line((x_ - 1.0, y_), (x_ + 1.0, y_), "k w1")
    s.line((x_, y_ - 1.0), (x_, y_ + 1.0), "k w1")
    s.add("</g>")
    x_, y_ = P(AL["u"], AL["v"])
    s.rect(x_ - 2.4, y_ - 1.6, 4.8, 3.2, "red w3 fs")
    s.t(x_, y_ + 1.0, "AL", "t tiny2 b red-t")

    def lab(u, v, t_, c="t tiny2", a="middle"):
        x_, y_ = P(u, v)
        s.t(x_, y_, t_, c, a)
    lab(11.55, 20.75, f"VOLUME 0 - bassin : pompe {C.U_DC:.0f} V CC et projecteurs 12 V (TBTS)", "t tiny2 b red-t")
    lab(11.55, POOL["v1"] + 1.15, "VOLUME 1 (2.00 m)", "t tiny2 b")
    lab(11.55, POOL["v1"] + 2.85, "VOLUME 2 (de 2.00 à 3.50 m)", "t tiny2 b")
    lab(AL["u"], AL["v"] - 0.55, "boîtier AL - hors volumes", "t tiny2 b red-t")
    lab(AL["u"], AL["v"] - 0.95, f"poteau à {U0 - AL['u']:.2f} m du bassin", "t tiny2 red-t")
    lab(COFFRET["u"] + 0.15, COFFRET["v"] + 1.2, "TGBT villa : départ 16 A", "t tiny2 b", "start")
    lab(3.45, 16.0, "3G2.5 230 V", "t tiny2", "start")
    lab(4.6, AL["v"] + 0.40, f"24 V CC - 2 × {PUMP_C['cable_s']:g} mm²", "t tiny2", "middle")
    lab(9.6, V0 - 0.70, "12 V projecteurs", "t tiny2", "middle")
    lab(lel[0] - 0.25, lel[1] + 0.45, "LEL + piquet", "t tiny2 b", "start")
    lab(U0 + 0.25, V0 + 3.9, "puisard", "t tiny2 b", "start")
    s.dim(P(AL["u"], AL["v"] + 1.6), P(U0, AL["v"] + 1.6), 0, f"{U0 - AL['u']:.2f}", size=2.5)
    s.dim(P(9.0, POOL["v1"]), P(9.0, POOL["v1"] + 2.0), 0, "2.00", size=2.5)
    s.dim(P(9.0, POOL["v1"] + 2.0), P(9.0, POOL["v1"] + 3.5), 0, "1.50", size=2.5)
    s.t(127, 18.5, "VOLUMES DE SÉCURITÉ ET CHEMINEMENTS  1/100", "t ct")
    band_north(s, 180 - U_ANG)
    items = [("box:z1", "Volume 1 : 2.00 m autour du bassin"), ("box:z2", "Volume 2 : de 2.00 à 3.50 m"), ("elec", "230 V : TGBT → boîtier AL"),
             ("selv", f"TBTS : pompe {C.U_DC:.0f} V CC, projecteurs 12 V"), ("pe", "Liaison équipotentielle (LEL)"), ("box:red w3 fs", "Boîtier AL sur poteau")]
    legend_c(s, 238, 26, items, w=74, title="LÉGENDE")
    # ---- single-line diagram of the AL box
    y0 = 188
    s.t(22, 177, "SCHÉMA UNIFILAIRE DE PRINCIPE (boîtier AL)", "t cl", "start")
    s.rect(22, y0 - 4, 22, 8, "k w2 fs")
    s.t(33, y0 + 1, "TGBT villa", "t tiny2 b")
    s.t(33, y0 + 7.4, "départ 16 A", "t tiny")
    s.line((44, y0), (58, y0), "elec w3")
    s.t(51, y0 - 2, "3G2.5", "t tiny")
    s.rect(56, y0 - 7, 150, 56, "red w2 dash")
    s.t(204, y0 + 47, "BOÎTIER AL - IP65, fermé à clé, hors volumes", "t tiny2 b red-t", "end")
    s.circ(62, y0, 1.6, "k w2 fs")
    s.t(62, y0 - 3, "I0", "t tiny2 b")
    s.t(62, y0 + 5.6, "cadenassable", "t tiny")
    s.line((63.6, y0), (68, y0), "k w2")
    s.rect(68, y0 - 3.5, 17, 7, "k w2 fs")
    s.t(76.5, y0 + 1, "DDR 30 mA", "t tiny2 b")
    s.t(76.5, y0 + 6.4, "type A", "t tiny")
    s.line((85, y0), (200, y0), "k w4")
    s.line((89, y0), (89, y0 + 6), "k w2")
    s.rect(86.5, y0 + 6, 5, 4, "k w2 fs")
    s.t(93, y0 + 9.5, "parafoudre", "t tiny", "start")
    feeders = [(106, "Q1 2P 6 A", "T1", "M", f"Pompe {C.U_DC:.0f} V CC", "alim. sécurité + contrôleur"),
               (136, "Q2 2P 2 A", "T2", "L", "P1-P3 12 V 30 W", "transfo 300 VA"),
               (162, "Q3 2P 10 A", "T3", "L", "Éclairage jardin", "TBTS si < 3.50 m"),
               (186, "Q4 2P 16 A", None, "PC", "Prise 16 A IP55", "poteau AL")]
    for x, q, dev, load, l1, l2 in feeders:
        s.line((x, y0), (x, y0 + 8), "k w2")
        _brk(s, x, y0 + 12, q)
        yy = y0 + 16
        if dev:
            s.line((x, yy), (x, yy + 3), "k w2")
            s.circ(x, yy + 5, 2.0, "k w2")
            s.circ(x, yy + 8, 2.0, "k w2")
            s.t(x + 3, yy + 7.6, dev, "t tiny2 b", "start")
            s.line((x, yy + 10), (x, yy + 14), "selv w3" if dev != "T3" else "k w2")
        else:
            s.line((x, yy), (x, yy + 14), "k w2")
        s.circ(x, yy + 17, 3.0, "k w2 fs")
        s.t(x, yy + 18.1, load, "t tiny2 b")
        s.t(x, yy + 24.5, l1, "t tiny2", "middle")
        s.t(x, yy + 28, l2, "t tiny", "middle")
    s.rect(95, y0 + 18.5, 7, 4, "k w2 fs")
    s.t(98.5, y0 + 21.6, "H", "t tiny2 b")
    s.line((102, y0 + 20.5), (106, y0 + 20.5), "k w1")
    s.t(98.5, y0 + 26, "horloge", "t tiny", "middle")
    s.rect(22, y0 + 58, 30, 9, "k w2 fs")
    s.t(37, y0 + 63.5, "LEL + piquet", "t tiny2 b")
    s.line((52, y0 + 62.5), (204, y0 + 62.5), "pe")
    s.t(128, y0 + 66.5, "ferraillages du bassin et du puisard - cadre et cage inox - lame de la cascade - échelle - PE du boîtier AL", "t tiny", "middle")
    mz = [("Alimentation", "départ dédié 16 A au TGBT de la villa, câble 3G2,5 sous TPC jusqu'au boîtier AL."),
          ("Boîtier AL", f"IP65, fermé à clé, sur poteau à {U0 - AL['u']:.2f} m du bassin : hors des volumes 0, 1 et 2."),
          ("Protection", "DDR 30 mA type A en tête, un disjoncteur par départ, parafoudre."),
          ("Pompe", f"{C.U_DC:.0f} V CC par une alimentation de sécurité (NF EN 61558-2-6) : TBTS, seule tension admise dans l'eau."),
          ("Câble pompe", f"câble plat 2 × {PUMP_C['cable_s']:g} mm² d'un seul tenant jusqu'à AL, sans boîte de jonction, sous fourreau."),
          ("Projecteurs", "12 V par transformateur de sécurité dans AL ; bornes de jardin à < 3.50 m en 12 V."),
          ("Isolement", "I0 cadenassable : couper AL avant toute intervention dans le puisard."),
          ("Liaisons", "LEL : ferraillages, cadre et cage inox, lame de la cascade, échelle, piquet de terre."),
          ("Pompe 220 V", "votre pompe 1 HP 220 V ne va jamais dans le bassin : elle reste au puits du terrain.")]
    s.t(214, 177, "MESURES RETENUES", "t cl", "start")
    for i, (a_, b_) in enumerate(mz):
        yy = 183 + i * 8.6
        s.t(214, yy, a_, "t tiny2 b", "start")
        words, line, lines = b_.split(" "), "", []
        for w_ in words:
            if len(line) + len(w_) > 54:
                lines.append(line)
                line = w_
            else:
                line = (line + " " + w_).strip()
        lines.append(line)
        for j, l_ in enumerate(lines[:2]):
            s.t(236, yy + j * 3.5, l_, "t tiny", "start", size=2.3)
    s.rect(214, 262, 98, 22, "red w3 fs")
    s.t(216.5, 267.5, "CONFORMITÉ : NON VÉRIFIÉE", "t tiny2 b red-t", "start")
    for i, l_ in enumerate(["Concept établi sur les principes de la NF C 15-100 section 702 /",
                            "CEI 60364-7-702. À faire valider puis réceptionner par un électricien",
                            "qualifié, avec les fiches des matériels réellement achetés."]):
        s.t(216.5, 272.5 + i * 3.8, l_, "t tiny", "start", size=2.35)
    return _frame(s, "VC-07", "VC-07 Sécurité électrique")


# ==========================================================================
# VC-08  Nomenclature des équipements, coûts, exploitation, options
# ==========================================================================

def vc08():
    s = S("c8")
    lots, opts = C.dqe_c()
    it = {i[0]: i for _, _, _, items in lots for i in items}
    amt = lambda *codes: sum(it[c][4] * it[c][5] for c in codes)
    p = RC["pipes"]
    pc = PUMP_C
    rows = [
        ("P", "Pompe de forage 24 V CC", "1", f"4\" Ø100 × {pc['L']:.2f} m, {C.Q_C:.0f} m³/h à {pc['head']} mCE et {C.Q_GARDEN:.0f} m³/h à {pc['head_1']} mCE, inox", "Puisard, sous la cage", "Cascade, vidange", amt("4.02"), "Contrôle annuel, crépine rincée"),
        ("CG", "Cage inox 316L", "1", f"{CAGE['L'] * 1000:.0f} × {CAGE['W'] * 1000:.0f}, trous Ø8 au pas de 12, 2 panneaux, vis inviolables", "Grand fond, au ras du fond", "Protection, passage de l'eau", amt("4.01"), "Brosser la cage chaque semaine"),
        ("KP", "Kit de pose de la pompe", "1", "chemise Ø150, berceau, flexible 1-1/4\", raccord rapide, perche", "Puisard", "Refroidissement, dépose", amt("4.03"), "-"),
        ("RV", "Regard de vannes", "1", f"{RV['a']:.2f} × {RV['a']:.2f} × {RV['depth']:.2f}, té Ø63, V1, V2, raccords union", f"NO, à {U0 - RV['u']:.2f} m du bassin", "Choix tube 1 / tube 2", amt("4.07"), "Manœuvrer V1 et V2 chaque mois"),
        ("CAS", "Mur de cascade + lame", "1", "1.80 × 0.40, lame 600 × 6 mm, chambre inox 316L", "Petit bain, côté allée", "Retour par le tube 2", amt("4.08"), "Détartrer la fente 2 fois par an"),
        ("T0, T2", "Canalisations PVC PN16 Ø63", f"{p['d63']:.0f} ml", "collées, essai 24 h", "Tranchée NE", "Refoulement", amt("4.05"), "-"),
        ("T1", "Tube 1 PEHD Ø50", f"{p['pehd']:.0f} ml", "PN10, sortie à grille dans le puits perdu", "Jardin NO", "Vidange vers le verger", amt("4.06"), "-"),
        ("FC", "Fourreaux à collerette", "3", "bague hydrogonflante", "Voile NO, cascade", "Étanchéité", amt("4.04"), "-"),
        ("AL", "Boîtier AL sur poteau", "1", "IP65 à clé : I0, DDR 30 mA A, disjoncteurs, horloge, parafoudre", f"Jardin NO, à {U0 - AL['u']:.2f} m", "Protection, commande", amt("5.02"), "Test du DDR chaque mois"),
        ("T1 24 V", "Alimentation de sécurité 24 V CC", "1", "NF EN 61558-2-6, avec le contrôleur de la pompe", "Boîtier AL", "TBTS de la pompe", amt("5.03"), "-"),
        ("T2 12 V", "Transformateur de sécurité 12 V", "1", "230 / 12 V, 300 VA", "Boîtier AL", "Projecteurs", amt("5.05"), "-"),
        ("P1-P3", "Projecteurs LED", "3", "12 V 30 W + niche + presse-étoupe", "Voile SO", "Éclairage du bassin", amt("5.04"), "Joint neuf à chaque ouverture"),
        ("C1", "Câble 230 V", f"{C.L['cable']:.0f} ml", "U1000 R2V 3G2.5 sous TPC Ø63", "Tranchée", "Alimentation de AL", amt("5.01"), "-"),
        ("FO", "Fourreaux et câbles 12 V", f"{C.L['conduit'] + C.L['light']:.0f} ml", "TPC Ø40 : câble de la pompe, câbles 12 V", "Tranchées", "Cheminements TBTS", amt("5.06"), "-"),
        ("LEL", "Liaison équipotentielle", "1", "ferraillages, cadre et cage, lame, échelle, piquet", "Bassin et puisard", "Sécurité électrique", amt("5.07"), "Contrôle de continuité 1 fois par an"),
        ("ECH", "Échelle inox 316L", "1", "4 marches", "Grand fond", "Sortie du bassin", amt("4.10"), "Serrage des fixations"),
        ("KIT", "Kit d'entretien", "1", "épuisette, brosse, trousse d'analyse, diffuseur flottant", "Remise", "Entretien", amt("4.11"), "-"),
    ]
    tot = sum(r[6] for r in rows)
    trs = [(a, b_, c, d, e, f, money(g), h) for a, b_, c, d, e, f, g, h in rows]
    trs.append(("", "TOTAL ÉQUIPEMENTS (DH HT)", "", "prix unitaires du devis, lots 4 et 5", "", "", money(tot), ""))
    s.t(18, 18, "NOMENCLATURE DES ÉQUIPEMENTS - VARIANTE C (coûts estimés, DH HT, mêmes prix unitaires que le devis)", "t cl", "start")
    table(s, 18, 20, ("Rep.", "Composant", "Qté", "Spécification", "Emplacement", "Fonction", "Coût est.", "Entretien"), trs,
          (15, 40, 11, 80, 32, 33, 18, 66), rh=4.55, size=2.25, align="llrlllrl")
    orig, _ = M.dqe()
    io = {i[0]: i for _, _, _, items in orig for i in items}
    rem = [("2.06", "Local technique 2.40 × 2.00"), ("4.01", "Skimmers SK1-SK2"), ("4.02", "Bondes de fond BF1-BF2"), ("4.03", "Buses R1-R4"),
           ("4.04", "Prise balai PB"), ("4.06", "Nourrices du local technique"), ("4.08", "Filtre à sable Ø600 + vanne 6 voies")]
    rr = [(c_, t_, money(io[c_][4] * io[c_][5])) for c_, t_ in rem]
    rr.append(("", "Total supprimé (DH HT)", money(sum(io[c_][4] * io[c_][5] for c_, _ in rem))))
    y2 = 20 + 4.55 * (len(trs) + 1) + 9
    s.t(18, y2 - 2, "SUPPRIMÉS PAR RAPPORT À L'INDICE E", "t cl", "start")
    table(s, 18, y2, ("Art.", "Ouvrage", "Montant"), rr, (12, 70, 24), rh=4.4, size=2.3, align="llr")
    cc = C.compare()
    d = lambda a_, b_: f"{b_ - a_:+,.0f}".replace(",", " ")
    rows2 = [("Total général HT du devis", money(cc["total_e"]), money(cc["total_b"]), money(cc["total_c"]), d(cc["total_e"], cc["total_c"])),
             (f"Énergie ({cc['hours']} h de pompe par an, kWh)", money(cc["e_e"]), money(cc["e_b"]), money(cc["e_c"]), d(cc["e_e"], cc["e_c"])),
             ("Exploitation calculée (DH / an)", money(cc["ops_e"]), money(cc["ops_b"]), money(cc["ops_c"]), d(cc["ops_e"], cc["ops_c"])),
             ("Un remplissage complet (camion-citerne)", money(RC["refill"]), money(RC["refill"]), money(RC["refill"]), "")]
    s.t(132, y2 - 2, "COÛTS - MÊME BASE DE PRIX, MÊMES HYPOTHÈSES (DH HT)", "t cl", "start")
    table(s, 132, y2, ("Poste", "Indice E", "Var. B", "Var. C", "C - E"), rows2, (66, 22, 22, 22, 20), rh=4.6, size=2.3, align="lrrrr")
    s.t(132, y2 + 4.6 * 5 + 5, "La variante C coûte moins cher surtout parce qu'elle n'a pas de filtre : l'exploitation ne compte que l'électricité.", "t tiny2", "start", size=2.3)
    s.t(132, y2 + 4.6 * 5 + 9.4, "Sans filtre, l'eau se trouble plus vite : chaque remplissage complet coûte le montant de la dernière ligne.", "t tiny2", "start", size=2.3)
    y3 = y2 + 4.4 * 9 + 12
    orow = [(c_, d_, money(q * pu)) for c_, d_, en, u, q, pu in opts[3][:3]]
    s.t(18, y3 - 2, "OPTIONS CONSEILLÉES (non comprises dans le total) - à ajouter plus tard sans toucher au bassin", "t cl red-t", "start")
    table(s, 18, y3, ("Art.", "Option", "DH HT"), orow, (16, 232, 22), rh=4.6, size=2.3, align="llr")
    y4 = y3 + 4.6 * 4 + 14
    care = [("Chaque jour", "épuisette sur la surface (pas de skimmer) ; cascade en marche à l'horloge, quelques heures par jour."),
            ("Chaque semaine", "brosser la cage du puisard et les parois ; mesurer le chlore libre (1 à 3 mg/L) et le pH (7.2 à 7.6)."),
            ("Chaque mois", "manœuvrer V1 et V2 ; tester le DDR du boîtier AL ; détartrer la lame de la cascade si besoin."),
            ("Eau trouble", "chlore choc, puis vidange par le tube 1 et remplissage si l'eau ne s'éclaircit pas (sans filtre, pas de floculant)."),
            ("Avant une vidange", "arrêter le chlore 5 à 7 jours : chlore libre < 0.1 mg/L et pH 6.5 à 8.5 avant d'ouvrir V1 vers le verger."),
            ("Chaque année", "couper AL (I0 cadenassé), déposer la cage, sortir la pompe par ses anneaux, rincer sa crépine.")]
    s.t(18, y4 - 2, "SANS FILTRE : L'ENTRETIEN À PRÉVOIR", "t cl", "start")
    table(s, 18, y4, ("Quand", "Quoi"), care, (30, 240), rh=4.6, size=2.3, align="ll")
    return _frame(s, "VC-08", "VC-08 Nomenclature et coûts")


# ==========================================================================
# Hooks for PL-01 / PL-02 (no technical room)
# ==========================================================================

def _pl01(s, P):
    s.pl([P(*p) for p in rect_uv(POOL["u1"], CASC_V[0], CASC_BACK, CASC_V[1])], "red w2 fcc", True)
    x_, y_ = P(RV["u"], RV["v"])
    s.rect(x_ - 0.6, y_ - 0.6, 1.2, 1.2, "red w2 fs")
    x_, y_ = P(AL["u"], AL["v"])
    s.circ(x_, y_, 0.8, "red w2 fs")


def _pl02(s, P):
    draw_cascade_plan(s, P)
    draw_pit_plan(s, P, holes=False, pump=False)
    draw_rv_plan(s, P)
    draw_al_plan(s, P)


def _pl02_lab(s, P, lab):
    lab(RV["u"] - 0.55, RV["v"] + 0.12, "Regard de vannes RV (VC-06)", "t lab red-t", 0, "end")
    lab(AL["u"] - 0.45, AL["v"] + 0.12, "Boîtier AL (VC-07)", "t lab red-t", 0, "end")
    lab(CASC_BACK + 0.25, CASC_MID - 0.15, "Cascade", "t lab red-t", 0, "start")
    lab(CASC_BACK + 0.25, CASC_MID + 0.25, "(VC-06)", "t lab red-t", 0, "start")


HOOKS = dict(pl01=_pl01, pl02=_pl02, pl02_lab=_pl02_lab)


def pit_figure():
    s = S("pitfig")
    I = draw_pit_iso(s, 50, VC01_BOX)
    place_callouts(s, I, pit_items(), bounds=(22, 20, 208, 172), dist=17, r=2.6)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="18 16 194 160" class="sheet iso" role="img" aria-label="Puisard et pompe immergée, vue rapprochée">'
            + "\n".join(s.o) + "</svg>")


def principle_figure():
    s = S("prfig")
    draw_principle(s, 4, 8, 288, 92)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 296 108" class="sheet conn" role="img" aria-label="Principe des tubes 1 et 2">'
            + "\n".join(s.o) + "</svg>")


SHEET_FUNCS = [vc01, vc02, vc03, vc04, vc05, vc06, vc07, vc08, SH.pl01, SH.pl02, SH.pl05]
