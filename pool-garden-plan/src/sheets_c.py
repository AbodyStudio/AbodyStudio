"""Variante C - pompe immergée dans le puisard : planches VC-01 à VC-04.

Author: AbodyStudio Limited - https://abodystudio.com/
"""
import math

import sheets as SH
from sheets import S, frame, table, band_north, tree, rect_uv, pool_xy, U_ANG
from model import *  # noqa: F401,F403
import variant_b as B
import variant_c as C
import sheets_b as SB
from sheets_b import (Iso, iso_box, iso_cyl, iso_tube, iso_valve, _poly, place_callouts, valve, check, gauge, filter_sym, pump_sym,
                      legend_lines, rot_view, draw_cascade_plan, draw_post_plan, route, CASC_V, CASC_MID)
from variant_c import PIT, CAGE, PUMP_C, STUB_Z, OUT_STUB_Y, SK_STUB_Y, CABLE_Y, RV, AL, CAB, R as RC
from variant_b import POST, COFFRET, CASCADE, SLOT, FILTER, CASC_BACK

SB.TUBE.update({
    "t0": ("#3c4a55", "T0 refoulement de la pompe"),
    "t1": ("#8a5a2b", "Tube 1 → jardin"),
    "t2": ("#1b8a5a", "Tube 2 → cascade → bassin"),
    "sk": ("#1683a8", "Skimmers → puisard"),
})
TUBE = SB.TUBE

VC_SHEETS = [
    ("VC-01", "Pompe immergée dans le puisard", "Vue rapprochée : pompe, cage, tubes 1 et 2", "s.é."),
    ("VC-02", "Puisard et cage de la pompe", "Plan, coupes et détail de la cage", "1/20 - 1/10 - 1/5"),
    ("VC-03", "Tubes 1 et 2, filtre et électricité", "Tracés, regard de vannes, coffre du filtre, TBTS 24 V", "1/200 - 1/20 - 1/10"),
    ("VC-04", "Pompe de forage 24 V", "Élévation, détail, boîtier AL, coupe et exigences", "1/10 - 1/5 - 1/2"),
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
    for (yy, r_, cl) in ((OUT_STUB_Y, 0.035, "#3c4a55"), (SK_STUB_Y, 0.03, "#1683a8"), (CABLE_Y, 0.022, "#2a86d8")):
        iso_cyl(s, I, "a", (yy, STUB_Z), r_, -0.01, 0.04, body="#9aa6ae", cap=cl, n=20, w=0.2)
    # pipes outside the wall rising to the cut (behind the wall in this view: dashed)
    for (yy, kind, d) in ((OUT_STUB_Y, "t0", 0.063), (SK_STUB_Y, "sk", 0.050)):
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
    for (yy, kind) in ((OUT_STUB_Y, "t0"), (SK_STUB_Y, "sk")):
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
    x_, y_ = I(px, sl1, pa)
    s.circ(x_, y_, RC["orifice"]["d"] / 2 * I.S, "k w2 fs")
    iso_tube(s, I, [(px, sl1 + 0.02, pa + 0.03), (px, sl1 + 0.08, pa + 0.03), (0.16, SK_STUB_Y, STUB_Z + 0.02), (0.04, SK_STUB_Y, STUB_Z)], "sk", 0.045, arrows=False)
    for (yy, d) in ((OUT_STUB_Y, 0.04), (SK_STUB_Y, 0.05)):
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
        ("EM", (px, pc["sleeve"][1], pa - 0.03), f"Embout à 2 entrées, diaphragme Ø{RC['orifice']['d'] * 1000:.0f} mm"),
        ("FS", (0.16, SK_STUB_Y, STUB_Z + 0.02), "Flexible et raccord rapide côté skimmers"),
        ("FR", (px - 0.06, pc["y0"] - 0.10, pa - 0.02), f"Flexible de refoulement {pc['outlet']} et raccord rapide"),
        ("T0", (wall0 - 0.12, OUT_STUB_Y, -2.40), "Tube T0 Ø63 vers le regard de vannes RV"),
        ("SK", (wall0 - 0.12, SK_STUB_Y, -2.40), "Arrivée des skimmers SK1-SK2 (Ø50)"),
        ("BE", (px + 0.06, pc["y0"] + 0.25, PIT["floor"] + 0.02), "Berceau inox, selles sur plots caoutchouc"),
        ("BC", (0.10, CABLE_Y + 0.08, STUB_Z + 0.12), "Boucle de câble (1 m de mou pour sortir la pompe)"),
        ("FO", (wall0 / 2, CABLE_Y, -2.45), "Fourreau Ø40 noyé dans le voile → boîtier AL"),
        ("PU", (x1, y0 + 0.15, PIT["floor"]), f"Puisard {CAGE['L']:.2f} × {CAGE['W']:.2f} × {PIT['depth']:.2f}, fond {PIT['floor']:+.2f}"),
        ("CS", (x1, y1 + 0.20, PIT["floor"] - 0.10), "Caisson BA 0.20 + membrane continue du bassin"),
        ("RA", (0.75, 3.60, ZF), f"Fond du bassin {ZF:+.2f} (grand fond, 1.80 m d'eau)"),
    ]


def draw_principle(s, x0, y0, w, h):
    """Whole path, not to scale: pit -> T0 -> RV (3-way) -> tube 2 -> filter in the cascade wall -> pool ; tube 1 -> borne -> garden."""
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
    # T0 up the NW wall to RV
    rvx, rvy = xr + 14, wl - 9
    s.pl([(xr - 2, yd + 3.2), (xr + 4, yd + 3.2), (xr + 4, rvy + 4), (rvx, rvy + 4)], "t0" and "k w4")
    s.add(f'<polyline points="{xr - 2:.2f},{yd + 3.2:.2f} {xr + 4:.2f},{yd + 3.2:.2f} {xr + 4:.2f},{rvy + 4:.2f} {rvx - 3:.2f},{rvy + 4:.2f}" style="fill:none;stroke:{TUBE["t0"][0]};stroke-width:1.6;stroke-linejoin:round"/>')
    s.rect(rvx - 3, rvy - 1, 10, 9, "k w2 fs")
    s.pl([(rvx - 1, rvy + 1.5), (rvx + 5, rvy + 1.5), (rvx + 2, rvy + 6.5)], "k w2 fs", True)
    s.t(rvx - 4.5, rvy + 5, "RV", "t tiny2 b", "end")
    s.t(rvx + 2, rvy + 12, "vanne 3 voies", "t tiny")
    # tube 2 : RV -> along the pool (under the deck) -> cascade cabinet -> lip -> pool
    cx = xl - 22
    s.add(f'<polyline points="{rvx + 2:.2f},{rvy - 1:.2f} {rvx + 2:.2f},{y0 + 4:.2f} {cx + 8:.2f},{y0 + 4:.2f} {cx + 8:.2f},{wl - 18:.2f}" style="fill:none;stroke:{TUBE["t2"][0]};stroke-width:1.6;stroke-linejoin:round"/>')
    s.rect(cx, wl - 22, 16, 22, "red w3 fs")
    filter_sym(s, cx + 6, wl - 11, 6, 15, lab=None)
    s.t(cx + 6, wl - 11 + 1, "F", "t tiny2 b")
    s.rect(cx + 16, wl - 16, 6, 12, "red w3 fcc")
    s.add(f'<polyline points="{cx + 12:.2f},{wl - 10:.2f} {cx + 19:.2f},{wl - 10:.2f} {cx + 19:.2f},{wl - 13:.2f} {cx + 22:.2f},{wl - 13:.2f}" style="fill:none;stroke:{TUBE["t2"][0]};stroke-width:1.2"/>')
    s.add(f'<path d="M{cx + 22:.2f} {wl - 13:.2f} q 2.4 0.6 2.8 13" style="fill:none;stroke:#1683a8;stroke-width:.8"/>')
    s.t(cx + 8, wl + 5, "COFFRE DU FILTRE", "t tiny2 b red-t")
    s.t(cx + 8, wl + 9, "dans le mur de cascade", "t tiny")
    s.t(cx + 30, wl - 15.5, "cascade", "t tiny2 b", "start")
    s.t((rvx + cx) / 2, y0 + 2.2, "TUBE 2 : vers la cascade, l'eau revient au bassin", "t tiny2 b", "middle")
    # tube 1 : RV -> borne (vacuum breaker at the high point) -> garden
    bx = x0 + w - 20
    s.add(f'<polyline points="{rvx + 7:.2f},{rvy + 4:.2f} {bx - 4:.2f},{rvy + 4:.2f} {bx - 4:.2f},{wl - 22:.2f} {bx + 2:.2f},{wl - 22:.2f} {bx + 2:.2f},{yd + 6:.2f}" style="fill:none;stroke:{TUBE["t1"][0]};stroke-width:1.6;stroke-linejoin:round;stroke-dasharray:3 1"/>')
    s.circ(bx - 1, wl - 24.5, 1.6, "k w2 fs")
    s.t(bx - 1, wl - 27.5, "casse-vide ±0.00", "t tiny", "middle")
    s.rect(bx - 6, wl - 26, 11, 22, "k w2 dash")
    s.t(bx, wl - 19, "BORNE", "t tiny2 b")
    s.t(bx + 4, yd + 9, "→ verger / puits perdu", "t tiny2", "end")
    s.t(bx + 5.5, (wl + yd) / 2, "TUBE 1 : vers le jardin", "t tiny2 b", "middle", -90)
    # electrical
    s.rect(xr + 22, ys + 6, 12, 7, "k w2 fs")
    s.t(xr + 28, ys + 10.8, "AL", "t tiny2 b")
    s.t(xr + 36, ys + 10.8, "24 V CC", "t tiny", "start")
    _dc_line(s, [(xr + 22, ys + 12), (xr + 1, ys + 12), (xr + 1, yd + 1.5), (xr - 4, yd + 1.5)], 0.7)
    s.t(xr - 1, ys + 22, "câble TBTS", "t tiny", "end")
    s.line((x0, wl - 4), (xl, wl - 4), "k w1")
    s.line((xr, wl - 4), (x0 + w, wl - 4), "k w1")


VC01_BOX = (24, 24, 206, 168)


def vc01():
    s = S("c1")
    s.t(24, 16, "VUE RAPPROCHÉE DU PUISARD - écorché, sans échelle (cage représentée soulevée, voiles avant transparents)", "t cl", "start")
    I = draw_pit_iso(s, 50, VC01_BOX)
    items = pit_items()
    place_callouts(s, I, items, bounds=(22, 20, 208, 172), dist=17, r=2.6)
    s.t(214, 22, "VOTRE SCHÉMA, SANS 220 V DANS L'EAU", "t cl red-t", "start")
    for i, t_ in enumerate(["Pompe couchée au point le plus bas, sous une cage",
                            "métallique ajourée : l'eau entre par la cage, la pompe",
                            "l'envoie par le tube 1 (jardin) ou le tube 2 (cascade).",
                            "La pompe de forage 1 HP 220 V ne peut pas être dans",
                            "l'eau du bassin : en volume 0, seule la TBTS est admise",
                            f"(≤ 12 V CA ou 30 V CC). La pompe est donc en {C.U_DC:.0f} V CC,",
                            "alimentée par une source de sécurité hors volumes.",
                            "Votre pompe de forage reste utilisable dans le puits."]):
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
    s.title = "VC-01 Pompe immergée"
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
        s.circ(Y(sl1), zc, RC["orifice"]["d"] / 2 * k * 0.5, "k w1")
    return exit_pt


def vc02():
    s = S("c2")
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
    s.add('<defs><clipPath id="c2p"><rect x="24" y="30" width="132" height="80"/></clipPath></defs><g clip-path="url(#c2p)">')
    s.rect(PX(1.25), PY(wall0 - 0.25), 2.5 * K, 0.25 * K, "k w1 fgr")
    s.rect(PX(1.25), PY(wall0), 2.5 * K, WALL * K, "k w3 fcc")
    s.rect(PX(1.25), PY(-fin), 2.5 * K, (1.20 + fin) * K, "k w1 fw")
    s.rect(PX(y0 - 0.20), PY(0), (y1 - y0 + 0.40) * K, (x1 + 0.20) * K, "k w1 dash")
    s.rect(PX(y0), PY(x0), (y1 - y0) * K, (x1 - x0) * K, "k w3 fs")
    s.rect(PX(y0 - 0.03), PY(x0), (y1 - y0 + 0.06) * K, (x1 - x0 + 0.03) * K, "k w1")
    ex, ez = pump_side(s, PX, PY(px), K, cable_off=-0.2)
    for (yy, d, kind) in ((OUT_STUB_Y, 0.063, "t0"), (SK_STUB_Y, 0.050, "sk")):
        s.add(f'<line x1="{PX(yy):.2f}" y1="{PY(wall0 - 0.25):.2f}" x2="{PX(yy):.2f}" y2="{PY(0.06):.2f}" style="stroke:{TUBE[kind][0]};stroke-width:{d * K:.2f}"/>')
    s.add(f'<polyline points="{PX(OUT_STUB_Y):.2f},{PY(0.06):.2f} {PX(OUT_STUB_Y):.2f},{PY(px - 0.04):.2f} {PX(pc["y0"] - 0.06):.2f},{PY(px):.2f}" style="fill:none;stroke:{TUBE["t0"][0]};stroke-width:2;stroke-linejoin:round"/>')
    s.add(f'<polyline points="{PX(SK_STUB_Y):.2f},{PY(0.06):.2f} {PX(SK_STUB_Y):.2f},{PY(px - 0.04):.2f} {PX(pc["sleeve"][1]):.2f},{PY(px):.2f}" style="fill:none;stroke:{TUBE["sk"][0]};stroke-width:2.2;stroke-linejoin:round"/>')
    s.add(f'<line x1="{PX(CABLE_Y):.2f}" y1="{PY(wall0 - 0.25):.2f}" x2="{PX(CABLE_Y):.2f}" y2="{PY(0.0):.2f}" style="stroke:#c9d1d6;stroke-width:{0.04 * K:.2f}"/>')
    blue_cable(s, [(PX(CABLE_Y), PY(wall0 - 0.25)), (PX(CABLE_Y), PY(0.03)), (PX(CABLE_Y) + 3, PY(0.10)), (ex, ez)], 0.7)
    s.add("</g>")
    for t_, (xx, yy), a in (("T0 → RV", (PX(OUT_STUB_Y) + 1.5, PY(wall0 - 0.28)), "end"), ("SK1-SK2", (PX(SK_STUB_Y), PY(wall0 - 0.28)), "middle"),
                            ("câble → AL", (PX(CABLE_Y) - 1.0, PY(wall0 - 0.28)), "start"), ("BASSIN", (PX(2.50), PY(0.80)), "middle")):
        s.t(xx, yy, t_, "t tiny2 b", a)
    s.dim((PX(y0), PY(x1 + 0.03)), (PX(y1), PY(x1 + 0.03)), -4, f"{y1 - y0:.2f}", size=2.4)
    s.dim((PX(y1 + 0.14), PY(x0)), (PX(y1 + 0.14), PY(x1)), 0, f"{x1 - x0:.2f}", size=2.4)
    s.dim((PX(pc["y0"]), PY(px - 0.12)), (PX(pc["y1"]), PY(px - 0.12)), 0, f"{pc['L']:.2f}", size=2.4)
    s.t(90, 26, "PLAN DU PUISARD (cage déposée)  1/20", "t ct")
    # ---- long section 1/20 along the pump axis, looking NW
    AX = lambda y: 172 + (y - 1.25) * K
    AZ = lambda z: 42 + (-2.50 - z) * K
    s.add('<defs><clipPath id="c2a"><rect x="168" y="32" width="140" height="68"/></clipPath></defs><g clip-path="url(#c2a)">')
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
    s.add(f'<polyline points="{AX(pc["sleeve"][1]):.2f},{AZ(pa):.2f} {AX(SK_STUB_Y):.2f},{AZ(STUB_Z):.2f}" style="fill:none;stroke:{TUBE["sk"][0]};stroke-width:2.2;stroke-linejoin:round"/>')
    for yy in (OUT_STUB_Y, SK_STUB_Y):
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
    s.add('<defs><clipPath id="c2b"><rect x="24" y="124" width="150" height="88"/></clipPath></defs><g clip-path="url(#c2b)">')
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
    o = RC["orifice"]
    rows = [("Débit de la pompe", f"{C.Q_C:.0f} m³/h - recyclage en {RC['turnover']:.1f} h"),
            ("Passage libre de la cage", f"{CAGE['L']:.2f} × {CAGE['W']:.2f} × {CAGE['open_ratio']:.2f} = {RC['cage_open']:.3f} m²"),
            ("Vitesse au travers de la cage", f"{RC['v_cage']:.4f} m/s (limite usuelle 0.5 m/s)"),
            ("Cage plus grande qu'un corps", f"≥ 457 × 584 mm : {'oui' if RC['unblockable'] else 'non'}"),
            ("Vitesse le long du moteur", f"{RC['v_sleeve']:.2f} m/s dans la chemise (mini usuel 0.08 m/s)"),
            ("Partage fond / skimmers", f"{(1 - C.SK_SHARE) * 100:.0f} / {C.SK_SHARE * 100:.0f} % : diaphragme Ø{o['d'] * 1000:.0f} mm"),
            ("HMT tube 2 (moyenne / filtre au seuil)", f"{RC['tdh_2'][1]:.2f} / {RC['tdh_2_dirty']:.2f} mCE"),
            ("Pompe retenue", f"{C.Q_C:.0f} m³/h à {pc['head']} mCE, {C.U_DC:.0f} V CC, 4\", {pc['L']:.2f} m"),
            ("Puissance absorbée (moyenne / maxi)", f"{RC['p1']:.0f} / {RC['p1_dirty']:.0f} W (rendement {C.ETA:.2f})"),
            ("Courant à 24 V (moyen / maxi)", f"{RC['cable']['i_avg']:.1f} / {RC['i_dc']:.1f} A"),
            ("Câble du moteur", f"2 × {RC['cable']['s']:g} mm², {C.L['pump_cable']:.1f} m : chute {RC['cable']['drop_avg_pct']:.1f} / {RC['cable']['drop_pct']:.1f} %")]
    s.t(176, 160, "CALCUL DU PUISARD ET DE LA POMPE", "t cl", "start")
    table(s, 176, 162, ("Grandeur", "Valeur"), rows, (58, 78), rh=4.4, size=2.2, align="ll")
    notes = ["Cage vissée au ras du fond : rien ne dépasse, pas de prise pour les pieds.",
             "Entretien : couper l'alimentation AL, déposer la cage à la clé, défaire les deux raccords",
             "rapides à la perche, remonter la pompe par ses anneaux ; le câble coulisse dans le fourreau.",
             "Membrane du bassin continue dans le puisard, angles en gorge 5 × 5."]
    s.t(24, 222, "NOTES", "t cl", "start")
    for i, t_ in enumerate(notes):
        s.t(24, 228 + i * 4.3, t_, "t tiny2", "start", size=2.3)
    _sub = SH.FRAME_SUB
    SH.FRAME_SUB = C.SUBTITLE
    frame(s, "VC-02")
    SH.FRAME_SUB = _sub
    s.title = "VC-02 Puisard et cage"
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
            ("entrée 230 V depuis CP (3G2.5)", (x + w * 0.30, y + h + 1.2)), ("câble plat bleu 24 V CC → pompe", (x + w * 0.70 + 10, y + h + 9))]


def vc04():
    s = S("c4")
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
            ("Point de fonctionnement", f"{C.Q_C:.0f} m³/h à {pc['head']} mCE ({RC['tdh_2_dirty']:.2f} mCE filtre au seuil)"),
            ("Puissance / courant", f"{RC['p1']:.0f} W moyen, {RC['p1_dirty']:.0f} W maxi - {RC['i_dc']:.1f} A à {C.U_DC:.0f} V"),
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
                ("Puissance", "1 HP (0.75 kW)", f"{RC['p1_dirty']:.0f} W maxi"), ("Câble", "plat bleu", f"plat bleu 2 × {pc['cable_s']:g} mm²"),
                ("Coffret", "boîtier blanc 220 V", "boîtier AL 24 V CC (TBTS)")]
    s.t(142, 211, "VOTRE POMPE (PHOTO) ET LA POMPE DU PUISARD", "t cl", "start")
    table(s, 142, 213, ("", "Pompe de la photo", "Pompe du puisard"), cmp_rows, (30, 64, 76), rh=4.4, size=2.3, align="lll")
    notes = ["La pompe de la photo (220 V) ne doit pas être placée dans le bassin : un défaut d'isolement dans l'eau peut être mortel.",
             "Elle reste utilisable dans le puits du terrain. La pompe du puisard a la même forme et la même longueur, en 24 V CC.",
             f"Les pompes de forage sont faites pour de grandes hauteurs : le modèle 24 V choisi doit avoir son point {C.Q_C:.0f} m³/h à {pc['head']} mCE",
             "sur sa courbe et accepter la pose horizontale : à vérifier sur la fiche du fabricant avant l'achat."]
    s.t(24, 256, "À SAVOIR", "t cl red-t", "start")
    for i, t_ in enumerate(notes):
        s.t(24, 262 + i * 4.6, t_, "t tiny2", "start", size=2.4)
    _sub = SH.FRAME_SUB
    SH.FRAME_SUB = C.SUBTITLE
    frame(s, "VC-04")
    SH.FRAME_SUB = _sub
    s.title = "VC-04 Pompe de forage 24 V"
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
# VC-03  Tracés 1/200, coffre du filtre 1/20, regard RV 1/10, schéma électrique TBTS
# ==========================================================================

def vc03():
    s = S("c3")
    # ---- routes 1/200 (rotated like PL-02: villa at the top, NW on the right)
    UMIN, VMIN = 1.2, 12.6
    P, k = rot_view(118, 24, UMIN, VMIN, 200)
    s.k = k
    s.add('<defs><clipPath id="c3p"><rect x="22" y="22" width="96" height="96"/></clipPath></defs><g clip-path="url(#c3p)">')
    s.pl([P(*p) for p in rect_uv(UMIN, VMIN, 21.0, 32.6)], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], VMIN, HOUSE["u1"], HOUSE["v1"])], "k w2 fhx", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - WALK, POOL["v0"] - WALK, POOL["u1"] + WALK, POOL["v1"] + WALK)], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w2 fw", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"] + PIT["x0"], POOL["v0"] + PIT["y0"], POOL["u0"] + PIT["x1"], POOL["v0"] + PIT["y1"])], "k w2 fs", True)
    draw_cascade_plan(s, P)
    s.pl([P(*p) for p in rect_uv(CAB["u0"], CAB["v0"], CAB["u1"], CAB["v1"])], "red w2 fs", True)
    s.pl([P(*p) for p in rect_uv(RV["u"] - RV["a"] / 2, RV["v"] - RV["a"] / 2, RV["u"] + RV["a"] / 2, RV["v"] + RV["a"] / 2)], "red w2 fs", True)
    draw_post_plan(s, P)
    x_, y_ = P(AL["u"], AL["v"])
    s.rect(x_ - 1.2, y_ - 1.2, 2.4, 2.4, "k w2 fk")
    x_, y_ = P(SOAKAWAY["u"], SOAKAWAY["v"])
    s.circ(x_, y_, SOAKAWAY["r"] * k, "k w1 fst")
    for key, cls in (("T0", "t0"), ("T2", "t2"), ("T1", "t1"), ("T1_out", "t1")):
        pts = [P(*p) for p in C.ROUTES[key]]
        s.add(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in pts)}" style="fill:none;stroke:{TUBE[cls][0]};stroke-width:.9;stroke-linejoin:round{";stroke-dasharray:2 .8" if cls == "t1" else ""}"/>')
    _dc_line(s, [P(*p) for p in C.ROUTES["DC"]], 0.6)
    s.add(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in (P(*p) for p in C.ROUTES["CABLE"]))}" style="fill:none;stroke:#7b3fb0;stroke-width:.6"/>')
    s.add("</g>")
    for t_, (u, v), a in (("puisard", (POOL["u0"] + 0.30, POOL["v0"] + 3.4), "start"), ("RV", (RV["u"] - 0.4, RV["v"] - 0.5), "start"), ("AL", (AL["u"] - 0.5, AL["v"] + 0.4), "start"),
                          ("borne", (POST["u"] - 0.5, POST["v"] + 0.6), "start"), ("coffre filtre", (CAB["u1"] + 0.3, CAB["v1"] + 0.9), "end"), ("CP", (COFFRET["u"], COFFRET["v"] - 0.5), "middle"),
                          ("tube 2", ((POOL["u0"] + POOL["u1"]) / 2, POOL["v1"] + 1.5), "middle"), ("tube 1", (POST["u"] + 0.4, 27.5), "end"), ("puits perdu", (SOAKAWAY["u"], SOAKAWAY["v"] - 1.3), "middle")):
        x_, y_ = P(u, v)
        s.t(x_, y_, t_, "t tiny2 b", a)
    s.t(70, 20, "TRACÉS  1/200", "t cl", "middle")
    # ---- filter cabinet behind the cascade 1/20 (section along u, looking NE)
    K = 50
    FX = lambda u: 132 + (u - (POOL["u1"] - 0.25)) * K
    FZ = lambda z: 30 + (0.05 - z) * K
    s.add('<defs><clipPath id="c3c"><rect x="126" y="26" width="84" height="86"/></clipPath></defs><g clip-path="url(#c3c)">')
    s.rect(FX(POOL["u1"] - 0.25), FZ(LV["water"]), 0.25 * K, 0.70 * K, "k w1 fw")
    s.rect(FX(CAB["u1"]), FZ(LV["deck_low"]), 0.50 * K, 0.95 * K, "k w1 fea")
    s.rect(FX(POOL["u1"] + fin), FZ(CASCADE["top"] - 0.05), WALL * K, (CASCADE["top"] - 0.05 + 1.60) * K, "k w3 fcc")
    s.rect(FX(POOL["u1"] + fin + WALL), FZ(CASCADE["top"] - 0.05), (CASC_BACK - POOL["u1"] - fin - WALL) * K, (CASCADE["top"] - 0.05 - LV["beam_top"]) * K, "k w2 fea2")
    s.rect(FX(CAB["u0"]), FZ(CAB["top"] - 0.05), (CAB["u1"] - CAB["u0"]) * K, (CAB["top"] - 0.05 - CAB["bottom"]) * K, "k w1 fs")
    s.rect(FX(CAB["u1"]), FZ(CAB["top"] - 0.05), 0.10 * K, (CAB["top"] - 0.05 - CAB["bottom"] + 0.10) * K, "k w3 fcc")
    s.rect(FX(CAB["u0"]), FZ(CAB["bottom"]), (CAB["u1"] - CAB["u0"] + 0.10) * K, 0.10 * K, "k w3 fcc")
    s.rect(FX(POOL["u1"] - 0.03), FZ(CAB["top"]), (CAB["u1"] - POOL["u1"] + 0.16) * K, 0.05 * K, "k w2 fs")
    fu = (CAB["u0"] + CAB["u1"]) / 2
    s.rect(FX(fu - FILTER["D"] / 2 + 0.03), FZ(CAB["bottom"] + 0.08 + FILTER["H"] - 0.12), (FILTER["D"] - 0.06) * K, (FILTER["H"] - 0.12) * K, "k w2 fs")
    s.add(f'<polyline points="{FX(CAB["u1"] + 0.6):.2f},{FZ(-1.20):.2f} {FX(fu):.2f},{FZ(-1.20):.2f} {FX(fu):.2f},{FZ(CAB["bottom"] + 0.10):.2f}" style="fill:none;stroke:{TUBE["t2"][0]};stroke-width:3.15;stroke-linejoin:round"/>')
    s.add(f'<polyline points="{FX(fu - 0.08):.2f},{FZ(-0.28):.2f} {FX(POOL["u1"] + fin + 0.11):.2f},{FZ(-0.28):.2f} {FX(POOL["u1"] + fin + 0.11):.2f},{FZ(SLOT["level"]):.2f}" style="fill:none;stroke:{TUBE["t2"][0]};stroke-width:3.15;stroke-linejoin:round"/>')
    s.rect(FX(POOL["u1"] + fin), FZ(SLOT["level"] + 0.07), 0.11 * K, 0.15 * K, "k w2 fs")
    s.line((FX(POOL["u1"] + fin), FZ(SLOT["level"])), (FX(POOL["u1"] - 0.08), FZ(SLOT["level"])), "k w3")
    s.add(f'<path d="M{FX(POOL["u1"] - 0.08):.2f} {FZ(SLOT["level"]):.2f} q {-0.08 * K:.2f} {0.03 * K:.2f} {-0.10 * K:.2f} {(SLOT["level"] - LV["water"]) * K:.2f}" style="fill:none;stroke:#1683a8;stroke-width:.8"/>')
    gauge(s, FX(fu + 0.08), FZ(-0.30), 1.4)
    s.add("</g>")
    for z, t_ in ((CAB["top"], f"{CAB['top']:+.2f}"), (LV["water"], f"{LV['water']:+.2f}"), (CAB["bottom"], f"{CAB['bottom']:+.2f}")):
        s.level(FX(CAB["u1"] + 0.14), FZ(z), t_, side="r", section=True)
    for t_, (xx, yy) in (("F", (FX(fu), FZ(-0.70))), ("tube 2", (FX(CAB["u1"] + 0.35), FZ(-1.26))), ("lame", (FX(POOL["u1"] - 0.15), FZ(SLOT["level"]) - 2))):
        s.t(xx, yy, t_, "t tiny2 b")
    s.t(168, 20, "COFFRE DU FILTRE (mur de cascade)  1/20", "t cl", "middle")
    # ---- valve box RV 1/10
    K2 = 100
    RX = lambda d: 262 + d * K2
    RZ = lambda z: 30 + (-0.66 - z) * K2
    s.rect(RX(-0.40), RZ(LV["deck_edge"]), 0.80 * K2, 0.62 * K2, "k w1 fea")
    s.rect(RX(-0.25), RZ(LV["deck_edge"]), 0.50 * K2, RV["depth"] * K2, "k w1 fs")
    s.rect(RX(-0.31), RZ(LV["deck_edge"]), 0.06 * K2, (RV["depth"] + 0.06) * K2, "k w2 fcc")
    s.rect(RX(0.25), RZ(LV["deck_edge"]), 0.06 * K2, (RV["depth"] + 0.06) * K2, "k w2 fcc")
    s.rect(RX(-0.25), RZ(RV["bottom"]), 0.50 * K2, 0.06 * K2, "k w1 fgr")
    s.rect(RX(-0.31), RZ(LV["deck_edge"]) - 0.6, 0.62 * K2, 2.2, "red w2 fs")
    zz = -1.00
    s.add(f'<polyline points="{RX(-0.40):.2f},{RZ(zz):.2f} {RX(-0.05):.2f},{RZ(zz):.2f}" style="fill:none;stroke:{TUBE["t0"][0]};stroke-width:6.3"/>')
    s.add(f'<polyline points="{RX(0.05):.2f},{RZ(zz):.2f} {RX(0.40):.2f},{RZ(zz):.2f}" style="fill:none;stroke:{TUBE["t2"][0]};stroke-width:6.3"/>')
    s.add(f'<polyline points="{RX(0.0):.2f},{RZ(zz) + 3:.2f} {RX(0.0):.2f},{RZ(-1.22):.2f} {RX(0.40):.2f},{RZ(-1.22):.2f}" style="fill:none;stroke:{TUBE["t1"][0]};stroke-width:5;stroke-linejoin:round"/>')
    s.pl([(RX(-0.05), RZ(zz) - 3.2), (RX(-0.05), RZ(zz) + 3.2), (RX(0.05), RZ(zz) - 3.2), (RX(0.05), RZ(zz) + 3.2)], "k w2 fs", True)
    s.line((RX(0), RZ(zz)), (RX(0), RZ(zz) - 7), "k w3")
    s.line((RX(0), RZ(zz) - 7), (RX(0.10), RZ(zz) - 7), "red w4")
    for t_, (xx, yy), a in (("T0", (RX(-0.38), RZ(zz) - 4.5), "start"), ("tube 2", (RX(0.38), RZ(zz) - 4.5), "end"), ("tube 1", (RX(0.38), RZ(-1.22) + 6), "end"),
                            ("V-C", (RX(0.12), RZ(zz) - 6.2), "start"), ("couvercle à carreler", (RX(0), RZ(LV["deck_edge"]) - 2.6), "middle")):
        s.t(xx, yy, t_, "t tiny2 b", a)
    s.level(RX(-0.36), RZ(LV["deck_edge"]), f"{LV['deck_edge']:+.2f}", side="l", section=True)
    s.t(262, 20, "REGARD DE VANNES RV  1/10", "t cl", "middle")
    # ---- electrical + hydraulic single line
    y0 = 128
    s.t(24, y0 - 4, "SCHÉMA ÉLECTRIQUE TBTS ET POSITIONS DE LA VANNE V-C", "t cl", "start")
    s.rect(24, y0, 26, 10, "k w2 fs")
    s.t(37, y0 + 4.2, "TGBT villa", "t tiny2 b")
    s.t(37, y0 + 8.0, "230 V", "t tiny")
    s.line((50, y0 + 5), (58, y0 + 5), "k w2")
    s.rect(58, y0, 44, 10, "red w2 fs")
    s.t(80, y0 + 4.2, "Coffret CP (façade, hors volumes)", "t tiny2 b")
    s.t(80, y0 + 8.0, "Q0 cadenassable, DDR 30 mA type A, 16 A", "t tiny")
    s.line((102, y0 + 5), (122, y0 + 5), "elec w3")
    s.t(112, y0 + 3.4, "3G2.5", "t tiny")
    s.rect(122, y0, 50, 10, "k w2 fs")
    s.t(147, y0 + 4.2, f"AL : alimentation de sécurité {C.U_DC:.0f} V CC", "t tiny2 b")
    s.t(147, y0 + 8.0, f"poteau à {POOL['u0'] - AL['u']:.2f} m du bassin, hors volumes", "t tiny")
    _dc_line(s, [(172, y0 + 5), (196, y0 + 5)], 1.0)
    s.t(184, y0 + 3.4, f"2 × {RC['cable']['s']:g} mm²", "t tiny")
    s.rect(196, y0, 40, 10, "k w2 fs")
    s.t(216, y0 + 4.2, "Pompe P dans le puisard", "t tiny2 b")
    s.t(216, y0 + 8.0, f"{C.U_DC:.0f} V CC, {RC['p1_dirty']:.0f} W maxi", "t tiny")
    s.t(24, y0 + 17, "La source TBTS (transformateur de sécurité) est hors des volumes 0, 1 et 2 : dans l'eau, seuls 24 V CC arrivent à la pompe et 12 V aux projecteurs.", "t tiny2", "start", size=2.3)
    s.t(24, y0 + 21.5, "Liaison équipotentielle : ferraillages, cadre et cage inox, lame de la cascade, échelle. Conformité non vérifiée : à valider par un électricien qualifié.", "t tiny2", "start", size=2.3)
    pos = [("1 - Tube 1", "jardin (verger / puits perdu)", "par la borne : casse-vide, prélèvement", f"{C.Q_GARDEN:.0f} m³/h", f"{RC['tdh_1'][1]:.2f} mCE"),
           ("2 - Tube 2", "cascade → bassin (filtration)", "par le filtre F du coffre", f"{C.Q_C:.0f} m³/h", f"{RC['tdh_2'][1]:.2f} mCE"),
           ("Entretien", "pompe arrêtée, AL coupé", "V-C fermée, vanne d'isolement fermée", "0", "-")]
    table(s, 24, y0 + 27, ("Position V-C", "L'eau va vers", "Passage", "Débit", "HMT moy."), pos, (26, 52, 56, 18, 20), rh=4.6, size=2.3, align="lllrr")
    rows = [(n, f"{v:.2f}") for n, v in RC["tdh_2"][0]] + [("HMT moyenne tube 2", f"{RC['tdh_2'][1]:.2f}"), ("HMT filtre au seuil de nettoyage", f"{RC['tdh_2_dirty']:.2f}")]
    s.t(24, y0 + 54, "PERTES DE CHARGE - TUBE 2 (mCE)", "t cl", "start")
    table(s, 24, y0 + 56, ("Poste", "mCE"), rows, (130, 16), rh=4.2, size=2.2, align="lr")
    notes = ["Tube 1 : V-C vers le jardin uniquement après contrôle à la borne",
             "(chlore libre < 0.1 mg/L, pH 6.5 à 8.5, pas de sel).",
             "Tube 2 : la cascade tourne pendant toute la filtration : plus",
             "d'aération et d'évaporation, pH à surveiller.",
             "Vidange complète par le tube 1 : la pompe est au point bas,",
             f"le bassin se vide jusqu'au puisard ({RC['drain_h']:.1f} h à {C.Q_GARDEN:.0f} m³/h).",
             "Le coffre du filtre ne contient que de l'eau : aucun appareil",
             "électrique hors de la pompe 24 V et des projecteurs 12 V."]
    s.t(184, y0 + 54, "NOTES", "t cl", "start")
    for i, t_ in enumerate(notes):
        s.t(184, y0 + 60 + i * 4.3, t_, "t tiny2", "start", size=2.3)
    _sub = SH.FRAME_SUB
    SH.FRAME_SUB = C.SUBTITLE
    frame(s, "VC-03")
    SH.FRAME_SUB = _sub
    s.title = "VC-03 Tubes, filtre, électricité"
    return s


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


SHEET_FUNCS = [vc01, vc02, vc03, vc04]
