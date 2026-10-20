"""Variante B - planches VB-01 à VB-10 (piscine sans local technique).

Same SVG builder, frame and conventions as sheets.py (A3, mm, Moroccan cartouche).
Author: AbodyStudio Limited - https://abodystudio.com/
"""
import math

import sheets as SH
from sheets import S, frame, table, band_north, north, tree, UV, rect_uv, pool_xy, U_ANG, W, H, BAND
from model import *  # noqa: F401,F403
import model as M
import variant_b as B
from variant_b import (VAULT, VLAY, ROUTES, SUMP, SUMP_DEPTH, SUMP_OUT, GRILLE, CASCADE, SLOT, HATCH, POST, INLETS_Y, INLET_LEVEL,
                       SKIMMERS_Y, FILTER, PUMP, R, COFFRET, vu, V_WALL, V_BASE, V_IN_A, V_IN_B, V_IN_H, CASC_BACK, NE_A1, NE_A2, SE_A1, SE_A2)

VB_SHEETS = [
    ("VB-01", "Principe : existant et proposé", "Même bassin, système hydraulique entièrement repensé", "1/200"),
    ("VB-02", "Plan général du bassin", "Puisard, skimmers, fosse sous trappe, cascade, réseaux", "1/50"),
    ("VB-03", "Schéma hydraulique", "Pompe, filtre, sélecteur A / B / C, rejet contrôlé", "sans échelle"),
    ("VB-04", "Coupes A-A et B-B", "Coupe longitudinale et coupe transversale au puisard", "1/50"),
    ("VB-05", "Fosse technique intégrée", "Plan d'équipement et coupes de la fosse", "1/10 - 1/20"),
    ("VB-06", "Détail de la cascade", "Lame d'eau, chambre de répartition, buses dissimulées", "1/10 - 1/20"),
    ("VB-07", "Rejet contrôlé vers le jardin", "Circuit B, borne de contrôle, conditions de rejet", "1/100 - 1/10"),
    ("VB-08", "Structure et étanchéité", "Grand fond, puisard, voile commun, fosse", "1/20"),
    ("VB-09", "Concept de sécurité électrique", "Volumes, coffret, unifilaire, liaisons", "1/100 - s.é."),
    ("VB-10", "Nomenclature des équipements", "Composants, spécifications, coûts, entretien", "-"),
    ("PL-01", "Plan de masse", "Implantation sur le plan topographique", "1/250"),
    ("PL-02", "Plan d'aménagement des abords", "Piscine, plage, jardins, allée et poulailler", "1/100"),
    ("PL-05", "Détails béton armé et nomenclature des aciers", "Paroi, radier, chaînage, margelle (inchangés)", "1/20"),
]

U0, V0 = POOL["u0"], POOL["v0"]
CASC_V = (V0 + CASCADE["y0"], V0 + CASCADE["y1"])
CASC_MID = V0 + (CASCADE["y0"] + CASCADE["y1"]) / 2
HATCH_UV = (vu(HATCH["a0"], HATCH["b0"]), vu(HATCH["a1"], HATCH["b1"]))
PAD = (POOL["u0"] - WALK - 1.20, VAULT["v_out0"] - 0.10, POOL["u0"] - WALK, VAULT["v_out1"] + 0.10)   # paved pad around the hatch
SUMP_UV = (U0 + SUMP["x0"], V0 + SUMP["y0"], U0 + SUMP["x1"], V0 + SUMP["y1"])
SEC_A_Y = 2.70     # A-A cut, pool-local y
SEC_B_X = 0.30     # B-B cut, pool-local x


def nf(x, d=2):
    return f"{x:.{d}f}"


def money(x):
    return f"{x:,.0f}".replace(",", " ")


# --------------------------------------------------------------------------
# Symbols
# --------------------------------------------------------------------------

def valve(s, x, y, horiz=True, r=1.6, c="k w2 fs", lab=None, lab_dy=-2.4, lab_a="middle"):
    """Ball valve: two triangles touching at the centre."""
    if horiz:
        s.pl([(x - r, y - r * 0.75), (x - r, y + r * 0.75), (x + r, y - r * 0.75), (x + r, y + r * 0.75)], c, True)
    else:
        s.pl([(x - r * 0.75, y - r), (x + r * 0.75, y - r), (x - r * 0.75, y + r), (x + r * 0.75, y + r)], c, True)
    s.circ(x, y, 0.35, "k w1 fk")
    if lab:
        s.t(x + (0 if lab_a == "middle" else (r + 0.8) * (1 if lab_a == "start" else -1)), y + lab_dy, lab, "t tiny2 b", lab_a)


def check(s, x, y, d=1, horiz=True, r=1.6, lab=None, lab_dy=-2.4):
    """Check valve: triangle pointing in the flow direction + bar."""
    if horiz:
        s.pl([(x - r * d, y - r * 0.75), (x - r * d, y + r * 0.75), (x + r * d, y)], "k w2 fs", True)
        s.line((x + r * d, y - r * 0.8), (x + r * d, y + r * 0.8), "k w3")
    else:
        s.pl([(x - r * 0.75, y - r * d), (x + r * 0.75, y - r * d), (x, y + r * d)], "k w2 fs", True)
        s.line((x - r * 0.8, y + r * d), (x + r * 0.8, y + r * d), "k w3")
    if lab:
        s.t(x, y + lab_dy, lab, "t tiny2 b")


def pump_sym(s, x, y, r=4.0, d=1, lab="P"):
    s.circ(x, y, r, "k w3 fs")
    s.pl([(x - r * 0.55 * d, y - r * 0.6), (x - r * 0.55 * d, y + r * 0.6), (x + r * 0.75 * d, y)], "k w2 fk", True)
    if lab:
        s.t(x, y + r + 3.4, lab, "t tiny2 b")


def gauge(s, x, y, r=1.4):
    s.circ(x, y, r, "k w2 fs")
    s.line((x, y), (x + r * 0.6, y - r * 0.6), "k w1")


def filter_sym(s, x, y, w=12, h=22, lab="F"):
    s.rect(x - w / 2, y - h / 2, w, h, "k w3 fs")
    s.arc((x - w / 2, y - h / 2), w / 2, 2.6, 0, 1, (x + w / 2, y - h / 2), "k w3 fs")
    for i in range(1, 4):
        xx = x - w / 2 + i * w / 4
        s.line((xx, y - h / 2 + 2), (xx, y + h / 2 - 2), "k w1 dash")
    if lab:
        s.t(x, y + h / 2 + 3.6, lab, "t tiny2 b")


def callout(s, x, y, txt, sheet=None, r=3.2):
    s.circ(x, y, r, "k w2 fs")
    if sheet:
        s.line((x - r, y), (x + r, y), "k w1")
        s.t(x, y - 0.6, txt, "t tiny2 b")
        s.t(x, y + 2.5, sheet, "t tiny")
    else:
        s.t(x, y + 1.0, txt, "t cb")


def sec_mark(s, a, b, name):
    s.line(a, b, "k w1 axis")
    for p in (a, b):
        s.circ(p[0], p[1], 2.4, "k w2 fs")
        s.t(p[0], p[1] + 1.1, name, "t cb")


def legend_lines(s, x, y, items, w=86, title="LÉGENDE DES RÉSEAUX"):
    s.rect(x - 2, y - 1, w, len(items) * 5.0 + 7, "k w1 fs")
    s.t(x, y + 3.4, title, "t cl", "start")
    for i, (c_, txt) in enumerate(items):
        yy = y + 8.0 + i * 5.0
        if c_.startswith("box:"):
            s.rect(x, yy - 2.0, 9, 3.6, "k w1 " + c_[4:])
        else:
            s.line((x, yy), (x + 9, yy), c_)
        s.t(x + 12, yy + 1.0, txt, "t cs", "start")


NET = [("pipe-s w3", "Aspiration PVC PN16 Ø63 / Ø50"), ("pipe-a1 w3", "Circuit A1 : buses dissimulées Ø63"),
       ("pipe-a2 w3", "Circuit A2 : cascade Ø63"), ("pipe-b w3", "Circuit B : rejet jardin Ø50 / PEHD"),
       ("elec w3", "Câbles 230 V et TBTS sous gaine"), ("pipe-d w2", "Drains")]


# --------------------------------------------------------------------------
# Common drawing pieces (plan, site u-v)
# --------------------------------------------------------------------------

def draw_vault_plan(s, P, detail=False, c_wall="red w2 dash", c_in="k w1 dash"):
    vl = VAULT
    s.pl([P(*p) for p in rect_uv(vl["u_out0"], vl["v_out0"], vl["u_in1"], vl["v_out1"])], c_wall, True)
    s.pl([P(*p) for p in rect_uv(vl["u_in0"], vl["v_in0"], vl["u_in1"], vl["v_in1"])], c_in, True)


def draw_hatch_plan(s, P, pad=True):
    if pad:
        s.pl([P(*p) for p in rect_uv(*PAD)], "k w2 fpv", True)
    (ua, va), (ub, vb) = HATCH_UV
    s.pl([P(*p) for p in rect_uv(ua, va, ub, vb)], "red w3 fs", True)
    s.line(P(ua, va), P(ub, vb), "k w1 dash")
    s.line(P(ua, vb), P(ub, va), "k w1 dash")


def draw_cascade_plan(s, P):
    s.pl([P(*p) for p in rect_uv(POOL["u1"], CASC_V[0], CASC_BACK, CASC_V[1])], "red w3 fcc", True)
    s.line(P(POOL["u1"] - 0.06, CASC_V[0] + 0.60), P(POOL["u1"] - 0.06, CASC_V[1] - 0.60), "red w4")


def draw_post_plan(s, P, size=0.60, depth=0.40):
    s.pl([P(*p) for p in rect_uv(POST["u"] - size / 2, POST["v"] - depth / 2, POST["u"] + size / 2, POST["v"] + depth / 2)], "red w3 fs", True)


def draw_sump_plan(s, P, slots=True):
    u0, v0, u1, v1 = SUMP_UV
    s.pl([P(*p) for p in rect_uv(u0, v0, u1, v1)], "k w3 fs", True)
    if slots:
        n = 14
        for i in range(1, n):
            vv = v0 + i * (v1 - v0) / n
            s.line(P(u0 + 0.03, vv), P(u1 - 0.03, vv), "k w1")


def route(s, P, pts, c):
    s.pl([P(*p) for p in pts], c)


def draw_networks(s, P, cable=True, b=True, w="w3"):
    route(s, P, ROUTES["SK"], f"pipe-s {w}")
    route(s, P, ROUTES["SK1"], f"pipe-s {w}")
    route(s, P, ROUTES["A1"], f"pipe-a1 {w}")
    for st in ROUTES["A1_stubs"]:
        route(s, P, st, f"pipe-a1 {w}")
    route(s, P, ROUTES["A2"], f"pipe-a2 {w}")
    if b:
        route(s, P, ROUTES["B"], f"pipe-b {w}")
    if cable:
        route(s, P, ROUTES["CABLE"], f"elec {w}")


# --------------------------------------------------------------------------
# Hooks for PL-01 / PL-02 (no technical room)
# --------------------------------------------------------------------------

def _pl01(s, P):
    s.pl([P(*p) for p in rect_uv(POOL["u1"], CASC_V[0], CASC_BACK, CASC_V[1])], "red w2 fcc", True)
    s.pl([P(*p) for p in rect_uv(*PAD)], "red w1 fpv", True)
    x, y = P(POST["u"], POST["v"])
    s.circ(x, y, 0.8, "red w2 fs")


def _pl02(s, P):
    draw_vault_plan(s, P)
    draw_hatch_plan(s, P)
    draw_cascade_plan(s, P)
    draw_post_plan(s, P)
    draw_sump_plan(s, P, slots=False)


def _pl02_lab(s, P, lab):
    lab(PAD[0] - 0.60, (PAD[1] + PAD[3]) / 2 - 0.25, "Trappe de la fosse", "t lab red-t", 0, "end")
    lab(PAD[0] - 0.60, (PAD[1] + PAD[3]) / 2 + 0.15, "technique (VB-05)", "t lab red-t", 0, "end")
    lab(CASC_BACK + 0.25, CASC_MID - 0.15, "Cascade", "t lab red-t", 0, "start")
    lab(CASC_BACK + 0.25, CASC_MID + 0.25, "(VB-06)", "t lab red-t", 0, "start")
    lab(POST["u"] - 0.45, POST["v"] + 0.12, "Borne de rejet (VB-07)", "t lab red-t", 0, "end")


HOOKS = dict(pl01=_pl01, pl02=_pl02, pl02_lab=_pl02_lab)


# ==========================================================================
# VB-01  Principe : existant / proposé  1/200
# ==========================================================================

def _panel_base(s, P):
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], 9.0, HOUSE["u1"], HOUSE["v1"])], "k w3 fhx", True)
    s.pl([P(*p) for p in rect_uv(STAIR["u0"], STAIR["v0"], STAIR["u1"], STAIR["v1"])], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], FRONT_GARDEN[0], HOUSE["u1"], FRONT_GARDEN[1])], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], DECK[0], HOUSE["u1"], DECK[1])], "k w1 fpv", True)
    dpoly = [(u_se(9), 9), (u_se(34), 34), (u_drive(34), 34), (u_drive(9), 9)]
    s.pl([P(*p) for p in dpoly], "k w1 fgr", True)
    s.pl([P(u_se(9), 9), P(u_se(34), 34)], "k w3 parcel")
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - WALK, POOL["v0"] - WALK, POOL["u1"] + WALK, POOL["v1"] + WALK)], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w3 fw", True)
    x, y = P(SOAKAWAY["u"], SOAKAWAY["v"])
    s.circ(x, y, SOAKAWAY["r"] * s.k, "k w2 fst")
    for (u, v) in [(7.6, 26.6), (11.6, 26.9), (15.6, 26.6), (2.0, 27.0)]:
        x, y = P(u, v)
        tree(s, x, y, 4.2)


def _panel_orig(s, P):
    s.pl([P(*p) for p in rect_uv(TECH["u0"], TECH["v0"], TECH["u1"], TECH["v1"])], "red w3 fcc", True)
    X0, Y0 = POOL["u0"], POOL["v0"]
    ent = [TECH["v0"] + 0.45, TECH["v0"] + 0.75, TECH["v0"] + 1.05, TECH["v0"] + 1.35]
    tu = TECH["u1"]
    srcs = [(X0, Y0 + FITTINGS["skimmers"][0][1]), (X0 + FITTINGS["drains"][0][0], Y0 + 2.5),
            (X0, Y0 + FITTINGS["vacuum"][0][1]), (X0, Y0 + FITTINGS["skimmers"][1][1])]
    for i, (u, v) in enumerate(srcs):
        uj = tu + 0.55 + 0.32 * i
        s.pl([P(*p) for p in [(u, v), (uj, v), (uj, ent[i]), (tu - TECH_WALL, ent[i])]], "pipe-s w2")
    rv, ru = POOL["v1"] + 0.36, POOL["u0"] - 0.36
    ring = [(tu - TECH_WALL, TECH["v0"] + 1.65), (ru - 0.9, TECH["v0"] + 1.65), (ru - 0.9, rv), (POOL["u1"] + 0.36, rv), (POOL["u1"] + 0.36, Y0 + 3.5)]
    s.pl([P(*p) for p in ring], "pipe-a1 w2")
    for (x, y) in FITTINGS["returns"]:
        if y >= POOL_W:
            s.line(P(X0 + x, rv), P(X0 + x, POOL["v1"]), "pipe-a1 w2")
        else:
            s.line(P(POOL["u1"] + 0.36, Y0 + y), P(POOL["u1"], Y0 + y), "pipe-a1 w2")
    bu = TECH["u0"] + 0.5
    s.pl([P(bu, TECH["v1"]), P(bu, SOAKAWAY["v"]), P(SOAKAWAY["u"] - SOAKAWAY["r"], SOAKAWAY["v"])], "pipe-b w2")
    eu = HOUSE["u0"] + 0.45
    s.pl([P(eu, HOUSE["v1"]), P(eu, FRONT_GARDEN[0] + 0.7), P(4.15, FRONT_GARDEN[0] + 0.7), P(4.15, TECH["v0"] + 0.30), P(tu, TECH["v0"] + 0.30)], "elec w2")


def _panel_new(s, P):
    draw_hatch_plan(s, P)
    draw_vault_plan(s, P, c_wall="red w2 dash")
    draw_cascade_plan(s, P)
    draw_sump_plan(s, P, slots=False)
    draw_post_plan(s, P)
    draw_networks(s, P, w="w2")
    route(s, P, ROUTES["B_out"], "pipe-b w2")


def vb01():
    s = S("b1")
    k = 1000 / 200
    for x0, title, new in ((22, "ORIGINAL - indice E (v1.3.1)", False), (168, "VARIANTE B - indice F (v2.0.0)", True)):
        umin, umax, vmin, vmax = -0.6, 22.4, 11.0, 32.6
        V = UV(x0, 30, umin, vmax, 200)
        P = V
        s.k = V.k
        pw, ph = (umax - umin) * k, (vmax - vmin) * k
        cid = f"b1c{int(new)}"
        s.add(f'<defs><clipPath id="{cid}"><rect x="{x0}" y="30" width="{pw:.2f}" height="{ph:.2f}"/></clipPath></defs>')
        s.rect(x0, 30, pw, ph, "k w2")
        s.t(x0 + pw / 2, 25.5, title, "t ct")
        cx, cy = x0 + pw / 2, 30 + ph / 2
        s.flip("rot", cx, cy)
        s.add(f'<g clip-path="url(#{cid})">')
        _panel_base(s, P)
        (_panel_new if new else _panel_orig)(s, P)
        s.add("</g>")

        def lab(u, v, txt, c="t tiny2", a="middle"):
            x_, y_ = P(u, v)
            s.t(x_, y_, txt, c, a)
        lab((HOUSE["u0"] + HOUSE["u1"]) / 2, 11.9, "VILLA EXISTANTE", "t tiny2 b")
        lab((POOL["u0"] + POOL["u1"]) / 2, (POOL["v0"] + POOL["v1"]) / 2 + 0.2, "BASSIN 10.00 × 5.00" + (" (inchangé)" if new else ""), "t tiny2 b red-t")
        lab(SOAKAWAY["u"], SOAKAWAY["v"] + 1.3, "Puits perdu", "t tiny2")
        if new:
            lab(PAD[0] - 0.2, (PAD[1] + PAD[3]) / 2 - 0.3, "Fosse sous trappe", "t tiny2 b red-t", "end")
            lab(PAD[0] - 0.2, (PAD[1] + PAD[3]) / 2 + 0.65, f"{nf(R['vault_ext'][0])} × {nf(R['vault_ext'][1])} (enterrée)", "t tiny2 red-t", "end")
            lab(CASC_BACK + 0.3, CASC_MID + 0.2, "Cascade", "t tiny2 b red-t", "start")
            lab(POST["u"], POST["v"] + 1.3, "Borne de rejet", "t tiny2 red-t")
            lab((POOL["u0"] + POOL["u1"]) / 2, NE_A1 + 0.95, "A1 + A2 dans une tranchée", "t tiny2")
            lab(4.0, 17.2, "Câble vers coffret", "t tiny2", "end")
        else:
            lab((TECH["u0"] + TECH["u1"]) / 2, TECH["v0"] - 0.6, "Local technique", "t tiny2 b red-t")
            lab((TECH["u0"] + TECH["u1"]) / 2, TECH["v1"] + 1.6, "2.40 × 2.00 à 3.55 m", "t tiny2 red-t")
            lab((POOL["u0"] + POOL["u1"]) / 2, POOL["v1"] + 1.15, "Boucle de refoulement + 4 buses", "t tiny2")
            lab(TECH["u1"] + 1.9, POOL["v0"] - 0.9, "4 aspirations", "t tiny2")
        s.flip()
    band_north(s, 180 - U_ANG)
    # ---- transformation diagram
    def box(x, y, w, h, t1, t2, c="k w2 fs", c1="t tiny2 b"):
        s.rect(x, y, w, h, c)
        s.t(x + w / 2, y + h / 2 - 0.8, t1, c1)
        if t2:
            s.t(x + w / 2, y + h / 2 + 3.4, t2, "t tiny2", size=2.3)
    y1 = 150
    s.t(22, y1 - 3, "ORIGINAL", "t cl", "start")
    row1 = [("BASSIN", "10.00 × 5.00 - 50,37 m³"), ("LOCAL TECHNIQUE EXTÉRIEUR", "2.40 × 2.00 semi-enterré, à 3.55 m"),
            ("ÉQUIPEMENTS CLASSIQUES", "sable Ø600, vanne 6 voies, 4 aspirations, 4 buses")]
    bw = (288 - 2 * 8) / 3
    for i, (a, b_) in enumerate(row1):
        x = 22 + i * (bw + 8)
        box(x, y1, bw, 12, a, b_, "k w2 fs")
        if i:
            s.t(x - 4, y1 + 7.2, "+", "t cb")
    s.line((166, y1 + 14), (166, y1 + 22), "red w3 arrow")
    s.t(170, y1 + 19.5, "MÊME BASSIN, SYSTÈME HYDRAULIQUE ENTIÈREMENT REPENSÉ", "t tiny2 b red-t", "start")
    y2 = y1 + 27
    s.t(22, y2 - 3, "VARIANTE B", "t cl", "start")
    row2 = [("BASSIN (inchangé)", "dimensions, niveaux, profil"), ("FOSSE INTÉGRÉE", "sèche, sous trappe A15"), ("UNE POMPE", f"{PUMP_FLOW} m³/h, préfiltre"),
            ("FILTRE À CARTOUCHE", f"{nf(FILTER['area'], 1)} m², sans contre-lavage"), ("2 CIRCUITS CONTRÔLÉS", "A retour - B jardin"),
            ("RETOUR ARCHITECTURAL", "cascade + 2 buses"), ("REJET JARDIN", "borne de contrôle")]
    bw2 = (288 - 6 * 4) / 7
    for i, (a, b_) in enumerate(row2):
        x = 22 + i * (bw2 + 4)
        box(x, y2, bw2, 12, a, b_, "red w2 fs", "t tiny2 b red-t")
    s.t(166, y2 + 20, "PAS DE LOCAL TECHNIQUE EXTÉRIEUR", "t ct red-t")
    # ---- key figures (computed)
    c = B.compare()
    oc = B.ops_costs()
    sp = B.scope_split()
    pct = lambda a, b_: f"{(b_ - a) / a * 100:+.0f} %"
    rows = [
        ("Local technique hors œuvre (emprise)", f"{nf(c['footprint_orig'])} m²", "aucun", "-100 %"),
        ("Fosse enterrée sous dallage (emprise)", "-", f"{nf(c['footprint_new'])} m²", ""),
        ("Hauteur manométrique moyenne", f"{nf(c['head_orig'])} mCE", f"{nf(c['head_new'])} mCE", pct(c["head_orig"], c["head_new"])),
        ("Canalisations PVC (hors PEHD de rejet)", f"{c['pipes_orig']:.0f} ml", f"{nf(c['pipes_new'], 1)} ml", pct(c["pipes_orig"], c["pipes_new"])),
        ("Fouilles en tranchée et local", f"{nf(c['exc_orig'], 1)} m³", f"{nf(c['exc_new'], 1)} m³", pct(c["exc_orig"], c["exc_new"])),
        ("Béton armé des ouvrages techniques", f"{nf(c['conc_orig'])} m³", f"{nf(c['conc_new'])} m³ + {nf(c['lean'])} gros béton", ""),
        ("Eau de lavage du filtre", f"{nf(oc['rows'][1][2], 1)} m³/an", f"{nf(oc['rows'][1][3], 1)} m³/an", pct(oc["rows"][1][2], oc["rows"][1][3])),
        ("Coût du périmètre modifié (DH HT)", money(sp["orig"]), money(sp["new"]), pct(sp["orig"], sp["new"])),
        ("  dont cascade, borne et PEHD demandés", "-", money(sp["added"]), ""),
        ("Coût d'exploitation calculé (DH/an)", money(oc["tot_old"]), money(oc["tot_new"]), pct(oc["tot_old"], oc["tot_new"])),
    ]
    s.t(22, 214, "CHIFFRES CLÉS - CALCULÉS SUR LES DEUX MODÈLES (voir dossier, § comparaison)", "t cl", "start")
    table(s, 22, 216, ("Indicateur", "Original (E)", "Variante B (F)", "Écart"), rows, (70, 30, 50, 18), rh=4.6, size=2.5, align="lrrr")
    keep = ["Bassin 10.00 × 5.00, implantation et niveaux", "Profondeur 0.55 → 1.80, profil du fond",
            f"Volume d'eau {hu(Q['water_vol'])} m³", "Structure BA, radier, voiles, chaînage", "Margelles, plage, escalier, éclairage 12 V",
            "Lot 6 jardins et lot 7 mise en eau"]
    s.t(222, 214, "CE QUI NE CHANGE PAS", "t cl", "start")
    for i, t_ in enumerate(keep):
        s.t(222, 221 + i * 5, "- " + t_, "t cs", "start")
    s.t(222, 255, "CE QUI DISPARAÎT", "t cl", "start")
    for i, t_ in enumerate(["Local technique 2.40 × 2.00 et sa porte", "Bondes BF1-BF2, prise balai, buses R1-R4",
                            "Filtre à sable, vanne 6 voies, contre-lavages"]):
        s.t(222, 262 + i * 5, "- " + t_, "t cs", "start")
    frame(s, "VB-01")
    s.title = "VB-01 Principe"
    return s


# ==========================================================================
# VB-02  Plan général du bassin  1/50 (same reading direction as PL-03:
# villa at the top, driveway on the left). Drawn directly in sheet space.
# ==========================================================================

def rot_view(xr, yt, umin, vmin, sc):
    k = 1000 / sc
    return (lambda u, v: (xr - (u - umin) * k, yt + (v - vmin) * k)), k


def vb02():
    s = S("b2")
    UMIN, VMIN, VMAX = 3.95, 16.85, 25.20
    P, k = rot_view(300, 22, UMIN, VMIN, 50)
    s.k = k
    UMAX = UMIN + (300 - 22) / k
    L = lambda x, y: P(*pool_xy(x, y))
    y_b = 22 + (VMAX - VMIN) * k
    s.add(f'<defs><clipPath id="b2v"><rect x="22" y="22" width="278" height="{y_b - 22:.2f}"/></clipPath></defs><g clip-path="url(#b2v)">')
    s.pl([P(*p) for p in rect_uv(UMIN, VMIN, UMAX, VMAX)], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], VMIN, HOUSE["u1"], DECK[1])], "k w1 ftl", True)
    # coping (interrupted at the cascade)
    s.pl([L(-WALK, -WALK), L(POOL_L + WALK, -WALK), L(POOL_L + WALK, POOL_W + WALK), L(-WALK, POOL_W + WALK)], "k w2 fs", True)
    for i in range(int(POOL_L / 0.5) + 1):
        s.line(L(i * 0.5, -WALK), L(i * 0.5, 0), "k w1")
        s.line(L(i * 0.5, POOL_W), L(i * 0.5, POOL_W + WALK), "k w1")
    for i in range(int(POOL_W / 0.5) + 1):
        s.line(L(-WALK, i * 0.5), L(0, i * 0.5), "k w1")
        if not (CASCADE["y0"] - 1e-6 < i * 0.5 < CASCADE["y1"] + 1e-6):
            s.line(L(POOL_L, i * 0.5), L(POOL_L + WALK, i * 0.5), "k w1")
    s.pl([L(POOL_L, CASCADE["y0"]), L(POOL_L + WALK + 0.30, CASCADE["y0"]), L(POOL_L + WALK + 0.30, CASCADE["y1"]), L(POOL_L, CASCADE["y1"])], "k w1 fgz", True)
    s.pl([L(-0.23, -0.23), L(POOL_L + 0.23, -0.23), L(POOL_L + 0.23, POOL_W + 0.23), L(-0.23, POOL_W + 0.23)], "k w1 dash", True)
    draw_hatch_plan(s, P)
    draw_vault_plan(s, P)
    draw_cascade_plan(s, P)
    # water, depth zones, steps, sump
    s.pl([L(0, 0), L(POOL_L, 0), L(POOL_L, POOL_W), L(0, POOL_W)], "red w4 fw", True)
    for x in (DEEP_FLAT, SLOPE_END):
        s.line(L(x, 0), L(x, POOL_W), "k w1 dash")
    s.line(L(BREAK_X, 0), L(BREAK_X, POOL_W), "k w3 dash")
    for i in range(STEP["n_tread"] + 1):
        xx = POOL_L - i * STEP["tread"]
        s.line(L(xx, 0), L(xx, STEP["width"]), "k w2")
    s.line(L(STEP["x0"], STEP["width"]), L(POOL_L, STEP["width"]), "k w2")
    draw_sump_plan(s, P)
    # networks
    draw_networks(s, P)
    su = vu(*VLAY["riser"])
    ym = V0 + (SUMP["y0"] + SUMP["y1"]) / 2
    s.pl([L(0.10, ym - V0), P(su[0], ym), P(su[0], su[1])], "pipe-s w3 dash")
    dr = vu(*VLAY["drain"])
    s.pl([P(*dr), P(dr[0], VAULT["v_out1"] + 0.25), P(VAULT["u_out0"] - 0.35, VAULT["v_out1"] + 0.25), P(VAULT["u_out0"] - 0.35, POOL["v1"] + 0.53)], "pipe-d w2")
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - 0.53, POOL["v0"] - 0.53, POOL["u1"] + 0.53, POOL["v1"] + 0.53)], "pipe-d w1", True)
    s.add("</g>")
    # fittings
    for y in SKIMMERS_Y:
        s.pl([L(-0.42, y - 0.30), L(0, y - 0.30), L(0, y + 0.30), L(-0.42, y + 0.30)], "k w2 fs", True)
        s.line(L(0, y - 0.25), L(0, y + 0.25), "k w4")
    for y in INLETS_Y:
        s.pl([L(POOL_L, y - 0.09), L(POOL_L, y + 0.09), L(POOL_L - 0.22, y)], "k w1 fk", True)
    for (x, y) in FITTINGS["lights"]:
        a_, b_ = L(x - 0.12, 0), L(x + 0.12, 0)
        s.arc(a_, 0.12 * k, 0.12 * k, 0, 1, b_, "k w2 flt")
    for (x, y) in FITTINGS["ladder"]:
        s.pl([L(x - 0.25, 0), L(x + 0.25, 0), L(x + 0.25, 0.45), L(x - 0.25, 0.45)], "k w1 fs", True)
        for j in range(3):
            s.line(L(x - 0.25, (j + 0.5) * 0.15), L(x + 0.25, (j + 0.5) * 0.15), "k w1")
    # tags
    def tag(x, y, t_, a="middle", c="t lab b"):
        s.t(x, y, t_, c, a)
    for i, y in enumerate(SKIMMERS_Y):
        x_, y_ = L(-0.42, y)
        tag(x_ + 1.2, y_ + 1.0, f"SK{i + 1}", "start")
    for i, y in enumerate(INLETS_Y):
        x_, y_ = L(POOL_L - 0.25, y)
        tag(x_ + 1.0, y_ + 1.0, f"RA{i + 1}", "start")
    for i, (x, y) in enumerate(FITTINGS["lights"]):
        x_, y_ = L(x, 0.45)
        tag(x_, y_ + 1.0, f"P{i + 1}")
    x_, y_ = L(FITTINGS["ladder"][0][0], 0.70)
    tag(x_, y_ + 1.0, "ECH")
    x_, y_ = L(SUMP["x1"] + 0.06, (SUMP["y0"] + SUMP["y1"]) / 2)
    tag(x_ - 0.6, y_ + 1.0, "PG", "end")
    x_, y_ = P((HATCH_UV[0][0] + HATCH_UV[1][0]) / 2, (HATCH_UV[0][1] + HATCH_UV[1][1]) / 2)
    tag(x_, y_ - 2.0, "TR", "middle", "t lab b red-t")
    x_, y_ = P((PAD[0] + PAD[2]) / 2, PAD[3])
    tag(x_, y_ + 4.4, "FT", "middle", "t lab b red-t")
    x_, y_ = P((POOL["u1"] + CASC_BACK) / 2, CASC_V[0])
    tag(x_, y_ - 1.6, "CAS", "middle", "t lab b red-t")
    x_, y_ = P(VAULT["u_out0"] - 0.40, ROUTES["B"][0][1])
    tag(x_, y_ - 1.4, "B", "middle", "t lab b")
    x_, y_ = P(ROUTES["CABLE"][2][0], 18.6)
    s.t(x_ - 1.2, y_, "câble 230 V + TBTS vers coffret (VB-09)", "t tiny2", "end", -90)
    # depth info
    x_, y_ = L(BREAK_X - 0.12, 2.5)
    s.t(x_, y_, f"rupture de pente - prof. {WATER_BREAK:.2f}", "t tiny2 b", "middle", -90)
    x_, y_ = L(7.90, 3.55)
    s.t(x_, y_, f"ZONE ENFANTS - prof. {WATER_SHALLOW:.2f}", "t lab b")
    for x, txt in [(0.95, f"fond {FLOOR_DEEP:+.2f}"), (BREAK_X + 0.35, f"fond {FLOOR_BREAK:+.2f}"), (SLOPE_END + 0.35, f"fond {FLOOR_SHALLOW:+.2f}")]:
        x_, y_ = L(x, 4.45)
        s.level(x_, y_, txt, "l")
    x_, y_ = L(5.4, 1.30)
    s.t(x_, y_, "BASSIN 10.00 × 5.00 - plan d'eau 50 m² (inchangé)", "t lab b red-t")
    s.t(x_, y_ + 6.0, f"Volume {hu(Q['water_vol'])} m³ - profil et structure de l'indice E", "t lab red-t")
    x_, y_ = P(11.5, 17.35)
    s.t(x_, y_, "Plage solarium (inchangée)", "t lab mute")
    # dimensions
    vb = POOL["v1"] + WALK
    chain = [CASC_BACK, POOL["u1"], U0, U0 - WALK, PAD[0]]
    for a_, b_ in zip(chain, chain[1:]):
        s.dim(P(a_, vb), P(b_, vb), -7, f"{a_ - b_:.2f}")
    x_, y_ = P((POOL["u0"] + POOL["u1"]) / 2, vb)
    s.t(x_, y_ + 15.5, "A1 (buses) et A2 (cascade) Ø63 dans la même tranchée - fils d'eau -1.45 / -1.30 - essai 24 h avant remblai", "t lab")
    ys = [0, CASCADE["y0"], INLETS_Y[0], INLETS_Y[1], CASCADE["y1"], POOL_W]
    for a_, b_ in zip(ys, ys[1:]):
        s.dim(P(POOL["u1"] + WALK, V0 + a_), P(POOL["u1"] + WALK, V0 + b_), -10, f"{b_ - a_:.2f}", size=2.6)
    xn = 2.25
    yn = [0, SKIMMERS_Y[0], SUMP["y0"], SUMP["y1"], SKIMMERS_Y[1], POOL_W]
    for a_, b_ in zip(yn, yn[1:]):
        s.dim(L(xn, a_), L(xn, b_), 0, f"{b_ - a_:.2f}", size=2.6)
    s.dim(L(SUMP["x0"], SUMP["y0"]), L(SUMP["x1"], SUMP["y0"]), -3, f"{SUMP['x1'] - SUMP['x0']:.2f}", size=2.6)
    s.dim(P(PAD[0], VAULT["v_out0"]), P(PAD[0], VAULT["v_out1"]), 4, f"{VAULT['v_out1'] - VAULT['v_out0']:.2f}", size=2.6)
    s.dim(P(PAD[0], PAD[1]), P(PAD[0], PAD[3]), 8, f"{PAD[3] - PAD[1]:.2f}", size=2.6)
    # section marks + callouts
    sec_mark(s, P(UMAX - 0.12, V0 + SEC_A_Y), P(UMIN + 0.20, V0 + SEC_A_Y), "A")
    sec_mark(s, P(U0 + SEC_B_X, VMIN + 0.60), P(U0 + SEC_B_X, VMAX - 0.35), "B")
    sec_mark(s, P(POOL["u1"] - 0.70, CASC_MID), P(CASC_BACK + 0.22, CASC_MID), "C")
    x_, y_ = P(VAULT["u_out0"] - 0.15, VAULT["v_out1"] + 0.85)
    callout(s, x_, y_, "D1", "VB-05")
    x_, y_ = L(POOL_L - 0.60, POOL_W - 0.35)
    callout(s, x_, y_, "D2", "VB-06")
    x_, y_ = L(0.85, SUMP["y1"] + 0.45)
    callout(s, x_, y_, "D3", "VB-08")
    band_north(s, 180 - U_ANG)
    # legend, network legend, levels, notes
    lg = [("PG", f"Puisard {SUMP['x1'] - SUMP['x0']:.2f} × {SUMP['y1'] - SUMP['y0']:.2f} × {SUMP_DEPTH:.2f} (fond {FLOOR_DEEP - SUMP_DEPTH:+.2f}), grille anti-coincement 800 × 600, fentes ≤ 8 mm"),
          ("SK1-SK2", "Skimmers de l'indice E conservés, raccordés à la fosse (vannes VS1, VS2)"),
          ("RA1-RA2", f"Buses dissimulées sous la cascade, axe {INLET_LEVEL:+.2f}, orientées vers le grand fond"),
          ("CAS", f"Mur de cascade {CASCADE['y1'] - CASCADE['y0']:.2f} × {CASCADE['thick']:.2f}, arase {CASCADE['top']:+.2f}, lame 600 × 6 mm à {SLOT['level']:+.2f} (circuit A2)"),
          ("FT", f"Fosse technique sèche {V_IN_A:.2f} × {V_IN_B:.2f} × {V_IN_H:.2f} int., fond {VAULT['floor']:+.2f}, sous dallage {VAULT['deck']:+.2f}"),
          ("TR", f"Trappe à carreler {HATCH['a1'] - HATCH['a0']:.2f} × {HATCH['b1'] - HATCH['b0']:.2f}, classe A15, verrouillée à clé, contact d'ouverture"),
          ("B", "Circuit B Ø50 vers la borne de contrôle du rejet (VB-07)"),
          ("P1-P3, ECH", "Projecteurs LED 12 V et échelle inox 316L (inchangés)")]
    s.t(24, 196, "REPÈRES", "t cl", "start")
    table(s, 24, 198, ("Repère", "Désignation"), lg, (20, 136), rh=4.6, size=2.5)
    legend_lines(s, 186, 195, NET, w=76)
    lv = [("Margelle / plan d'eau", f"{LV['coping']:+.2f} / {LV['water']:+.2f}"), ("Dallage de la trappe", f"{VAULT['deck']:+.2f}"),
          ("Arase cascade / lame d'eau", f"{CASCADE['top']:+.2f} / {SLOT['level']:+.2f}"), ("Axe des buses RA1-RA2", f"{INLET_LEVEL:+.2f}"),
          ("Fond de la fosse FT", f"{VAULT['floor']:+.2f}"), ("Fond du bassin (grand fond)", f"{FLOOR_DEEP:+.2f}"), ("Fond du puisard PG", f"{FLOOR_DEEP - SUMP_DEPTH:+.2f}")]
    s.t(186, 247, "NIVEAUX (±0.00 = sol fini RDC)", "t cl", "start")
    table(s, 186, 249, ("Élément", "Niveau"), lv, (88, 34), rh=4.3, size=2.5, align="lr")
    notes = ["Même bassin que l'indice E : dimensions, implantation, niveaux, profil du fond, structure, finitions.",
             "Supprimés : local technique, bondes BF1-BF2, prise balai PB, buses R1-R4.",
             "Ajoutés : puisard PG, fosse FT sous trappe TR, mur de cascade CAS, buses RA1-RA2.",
             "Pièces à sceller posées avant coulage ; tranchées remblayées après l'essai de pression 24 h."]
    s.t(24, 246, "NOTES", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(24, 252 + i * 4.6, n, "t tiny2", "start")
    frame(s, "VB-02")
    s.title = "VB-02 Plan général"
    return s


# ==========================================================================
# VB-03  Schéma hydraulique (sans échelle) + positions du sélecteur + HMT
# ==========================================================================

def vb03():
    s = S("b3")
    s.t(24, 15.5, "SCHÉMA DE PRINCIPE - SANS ÉCHELLE", "t cl", "start")
    # ---- pool (schematic section)
    wl, xl, xr = 50, 30, 116
    floor = [(xl, 74), (60, 74), (84, 88), (98, 96), (104, 96)]
    s.pl([(xl, wl)] + floor + [(104, 104), (114, 104), (114, 96), (xr, 96), (xr, wl)], "k w1 fw", True)
    s.pl([(xl, 40)] + floor + [(104, 104), (114, 104), (114, 96), (xr, 96), (xr, 40)], "k w4")
    s.line((xl, wl), (xr, wl), "k w2")
    for i in range(9):
        s.line((105 + i, 96.2), (105 + i, 97.4), "k w1")
    s.line((104, 96.8), (114, 96.8), "k w3")
    s.t(73, 64, "BASSIN", "t lab b red-t")
    s.t(73, 69, f"{hu(Q['water_vol'])} m³", "t lab red-t")
    s.t(109, 110, "PG", "t lab b")
    s.t(109, 114.5, "grille 800 × 600", "t tiny2")
    # cascade on the shallow (SE) end, inlets under it
    s.rect(xl - 7, 32, 7, 18, "red w3 fcc")
    s.line((xl, 38), (xl + 2.2, 38), "red w4")
    s.add(f'<path d="M{xl + 2.2} 38 q 2.4 0.8 2.6 {wl - 38}" class="red w2"/>')
    s.t(xl + 4.5, 35, "CAS", "t lab b red-t", "start")
    s.pl([(xl, 58.5), (xl, 61.5), (xl + 3, 60)], "k w1 fk", True)
    s.t(xl + 4, 61.2, "RA1-RA2", "t tiny2 b", "start")
    # skimmers on the deep (NW) wall
    for y_, nm in ((44, "SK1"), (51, "SK2")):
        s.rect(xr, y_ - 2.2, 6, 4.4, "k w2 fs")
    s.t(xr + 3, 39, "SK1-SK2", "t tiny2 b")
    # ---- vault
    vx0, vx1, vy0, vy1 = 132, 248, 32, 128
    s.rect(vx0, vy0, vx1 - vx0, vy1 - vy0, "red w3 dash")
    s.t(vx0 + 2, vy0 + 5, "FOSSE TECHNIQUE INTÉGRÉE (sèche, sous trappe TR, fond -1.80)", "t tiny2 b red-t", "start")
    cx = 146
    # suction collector
    s.line((xr + 6, 44), (cx, 44), "pipe-s w4")
    s.line((xr + 6, 51), (cx, 51), "pipe-s w4")
    s.pl([(114, 100), (124, 100), (cx, 100)], "pipe-s w4")
    s.line((cx, 44), (cx, 100), "pipe-s w4")
    valve(s, 138, 44, lab="VS1", lab_dy=-2.4)
    valve(s, 138, 51, lab="VS2", lab_dy=4.6)
    valve(s, 138, 100, lab="VA", lab_dy=-2.4)
    s.t(138, 107, "grille / puisard", "t tiny")
    # prefilter + pump
    s.line((cx, 100), (152, 100), "pipe-s w4")
    s.rect(152, 95.5, 6, 9, "k w2 fs")
    s.t(155, 93.5, "PF", "t tiny2 b")
    pump_sym(s, 163.5, 100, 5, lab=f"P - {PUMP_FLOW} m³/h")
    # to filter
    s.pl([(163.5, 95), (163.5, 76), (178, 76)], "k w4")
    gauge(s, 170, 72.5)
    s.line((170, 74), (170, 76), "k w1")
    filter_sym(s, 186, 84, 14, 26, lab="F - cartouche")
    gauge(s, 186, 66.5)
    s.t(190, 66, "M", "t tiny2 b", "start")
    s.pl([(186, 68), (186, 60), (212, 60)], "k w4")
    # selector header
    hx = 212
    s.line((hx, 44), (hx, 112), "k w4")
    for y_, nm, c_ in ((44, "V1", "pipe-a1"), (70, "V2", "pipe-a2"), (104, "V3", "pipe-b")):
        s.line((hx, y_), (vx1, y_), f"{c_} w4")
        valve(s, 222, y_, lab=nm, lab_dy=-2.4)
    s.rect(226.5, 100.5, 3.4, 2.8, "k w1 fs")
    s.arc((227.2, 100.5), 1.0, 1.0, 0, 1, (229.2, 100.5), "k w1")
    s.t(228.2, 110, "cadenassée", "t tiny")
    s.t(hx + 2, 116, "SÉLECTEUR", "t tiny2 b", "start")
    # A1 / A2 back to the pool
    s.pl([(vx1, 44), (vx1 + 4, 44), (vx1 + 4, 27), (xl - 12, 27), (xl - 12, 60), (xl, 60)], "pipe-a1 w4")
    s.pl([(vx1, 70), (vx1 + 7, 70), (vx1 + 7, 22), (xl - 3.5, 22), (xl - 3.5, 32)], "pipe-a2 w4")
    s.t(190, 20.6, "A2 - cascade (lame 600 × 6)", "t tiny2 b")
    s.t(80, 30.6, "A1 - buses dissimulées RA1-RA2", "t tiny2 b")
    # B to the control post
    px0, px1, py0, py1 = 258, 310, 62, 128
    s.rect(px0, py0, px1 - px0, py1 - py0, "k w2 dash")
    s.t((px0 + px1) / 2, py0 - 2, "BORNE DE CONTRÔLE (VB-07)", "t tiny2 b")
    s.line((vx1, 104), (px0, 104), "pipe-b w4")
    check(s, 264, 104, 1, lab="CL")
    s.pl([(266, 104), (270, 104), (270, 74), (278, 74), (278, 104), (288, 104)], "pipe-b w4")
    s.circ(274, 71, 2.0, "k w2 fs")
    s.line((274, 69), (274, 66.5), "k w1")
    s.t(274, 65.5, "CV ±0.00", "t tiny2 b")
    s.line((282, 104), (282, 110), "k w2")
    valve(s, 282, 112.5, horiz=False, r=1.3)
    s.t(284.5, 115.5, "RP", "t tiny2 b", "start")
    s.pl([(288, 104), (294, 104)], "pipe-b w4")
    s.pl([(291, 101), (297, 101), (294, 106)], "k w2 fs", True)
    s.t(294, 99, "V4", "t tiny2 b")
    s.line((297, 104), (304, 104), "pipe-b w4")
    s.circ(305.5, 104, 1.5, "k w2 fs")
    s.t(306, 98.5, "tuyau", "t tiny2", "middle")
    s.line((294, 106), (294, 136), "pipe-b w4")
    s.t(292, 141, "PEHD Ø50 → verger / puits perdu", "t tiny2", "end")
    # vault drain, interlocks
    s.pl([(196, vy1 - 3), (196, 136)], "pipe-d w3")
    s.rect(193, vy1 - 6, 6, 3, "k w2 fs")
    s.t(201, vy1 - 3.5, "SF", "t tiny2 b", "start")
    check(s, 196, 131, 1, horiz=False, r=1.3)
    s.t(198, 140, "clapet → drain périphérique → puits perdu", "t tiny2", "start")
    s.rect(236, vy1 - 9, 4, 4, "k w2 fs")
    s.t(242, vy1 - 5.5, "FL", "t tiny2 b", "start")
    s.rect(236, vy0 - 2, 6, 2, "k w2 fs")
    s.t(244, vy0 - 0.4, "CT", "t tiny2 b", "start")
    s.pl([(238, vy1 - 9), (238, vy1 - 13), (252, vy1 - 13), (252, 140)], "selv w2")
    s.pl([(239, vy0), (239, vy0 + 5), (252, vy0 + 5), (252, vy1 - 13)], "selv w2")
    s.t(252, 144.5, "TBTS vers coffret (VB-09)", "t tiny2")
    # ---- positions table
    F_, O_ = "F", "O"
    pos = [("A", "Filtration normale (buses)", O_, O_, O_, F_, "F*", "marche", f"{PUMP_FLOW} m³/h"),
           ("B", "Cascade seule", O_, O_, F_, O_, "F*", "marche", f"{PUMP_FLOW} m³/h"),
           ("A+B", "Buses + cascade (V1 réglée)", O_, O_, "R", O_, "F*", "marche", f"{R['q_a_in_ab']:.1f} + {PUMP_FLOW - R['q_a_in_ab']:.1f} m³/h"),
           ("C", "Rejet contrôlé au jardin", O_, F_, F_, F_, O_, "vitesse réduite", f"{B.Q_GARDEN:.0f} m³/h maxi"),
           ("E", "Entretien préfiltre / cartouche", F_, F_, F_, F_, "F*", "arrêt + consignation", "0")]
    s.t(24, 156, "POSITIONS DU SÉLECTEUR (O ouverte - F fermée - F* fermée et cadenassée - R réglée)", "t cl", "start")
    table(s, 24, 158, ("Pos.", "Usage", "VA", "VS1-2", "V1", "V2", "V3", "Pompe", "Débit"), pos, (11, 50, 10, 13, 10, 10, 10, 30, 32), rh=4.8, size=2.5)
    # ---- TDH table
    def mx(m, st):
        return B.tdh(m, q=B.Q_GARDEN if m == "C" else PUMP_FLOW, state=st)[1]
    rows = []
    for m, nm in (("A", "A - buses"), ("B", "B - cascade"), ("AB", "A+B"), ("C", "C - jardin")):
        q_ = B.Q_GARDEN if m == "C" else PUMP_FLOW
        rows.append((nm, f"{q_:.0f}", f"{mx(m, 'clean'):.2f}", f"{mx(m, 'avg'):.2f}", f"{mx(m, 'dirty'):.2f}"))
    _, h0 = B.tdh_original()
    rows.append(("Indice E (même méthode)", f"{PUMP_FLOW}", "", f"{h0:.2f}", ""))
    s.t(24, 194, "HAUTEUR MANOMÉTRIQUE TOTALE CALCULÉE (mCE) - détail des pertes dans le dossier", "t cl", "start")
    table(s, 24, 196, ("Mode", "Q (m³/h)", "Filtre propre", "Moyenne", "Filtre au seuil"), rows, (52, 20, 26, 22, 26), rh=4.6, size=2.5)
    s.t(24, 228, f"Pompe retenue : {PUMP_FLOW} m³/h à {PUMP['head']:.0f} mCE, vitesse variable, préfiltre intégré, 230 V, IPX5.", "t cs b", "start")
    s.t(24, 233, f"Vitesses : aspiration puisard {R['v_suction']:.2f} m/s - skimmers {R['v_skimmer']:.2f} m/s - collecteur Ø63 {R['v_header']:.2f} m/s -", "t tiny2", "start")
    s.t(24, 237.5, f"refoulement Ø63 {R['v_trunk']:.2f} m/s - circuit B Ø50 {R['v_b']:.2f} m/s - grille {R['v_grille']:.3f} m/s (limite usuelle 0.5 m/s).", "t tiny2", "start")
    s.t(24, 242, f"Filtre {FILTER['area']:.1f} m² : {R['filter_rate']:.2f} m³/h par m² - recyclage du bassin en {Q['water_vol'] / PUMP_FLOW:.1f} h.", "t tiny2", "start")
    # ---- operating notes
    notes = ["Les équipements sont sous le niveau de l'eau : avant d'ouvrir",
             "le préfiltre ou le filtre, passer en position E (VA, VS1, VS2,",
             "V1, V2 fermées), sinon la fosse se remplit.",
             "V3 reste cadenassée hors rejet : clé chez le propriétaire.",
             "Position C : contrôler d'abord à la borne chlore libre < 0.1 mg/L",
             "et pH 6.5 à 8.5 (VB-07). Skimmers fermés pendant la baisse",
             "du niveau.",
             "Le casse-vide CV (point haut ±0.00) empêche le siphonnage",
             "du bassin vers le verger, situé plus bas. Le clapet CL",
             "interdit tout retour d'eau du jardin.",
             "Vidange complète : hauteur d'aspiration finale 1.30 m,",
             "pompe auto-amorçante exigée (fiche fabricant).",
             "Cascade (B, A+B) : plus d'évaporation, pH qui monte :",
             "usage d'agrément, pas en continu."]
    s.t(214, 156, "CONDUITE ET SÉCURITÉ", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(214, 162 + i * 4.4, n, "t tiny2", "start")
    legend_lines(s, 214, 228 + 0, [("pipe-s w3", "Aspiration"), ("pipe-a1 w3", "Circuit A1"), ("pipe-a2 w3", "Circuit A2"),
                                   ("pipe-b w3", "Circuit B (rejet)"), ("k w3", "Refoulement pompe - filtre"), ("selv w2", "Sécurités TBTS")], w=98, title="TRAITS")
    s.t(24, 252, "SYMBOLES", "t cl", "start")
    sx = 26
    for i, (fn, txt) in enumerate([(lambda x, y: valve(s, x, y), "Vanne 1/4 de tour"), (lambda x, y: check(s, x, y), "Clapet anti-retour"),
                                   (lambda x, y: pump_sym(s, x, y, 2.6, lab=None), "Pompe"), (lambda x, y: gauge(s, x, y), "Manomètre"),
                                   (lambda x, y: s.circ(x, y, 1.8, "k w2 fs"), "Casse-vide CV")]):
        xx = sx + (i % 3) * 62
        yy = 259 + (i // 3) * 8
        fn(xx + 2, yy)
        s.t(xx + 7, yy + 1.0, txt, "t tiny2", "start")
    frame(s, "VB-03")
    s.title = "VB-03 Schéma hydraulique"
    return s


# ==========================================================================
# VB-04  Coupes A-A (longitudinale) et B-B (transversale au puisard)  1/50
# ==========================================================================

def _earth(s, X, Z, x0, x1, z_top, z_bot):
    s.pl([(X(x0), Z(z_top)), (X(x1), Z(z_top)), (X(x1), Z(z_bot)), (X(x0), Z(z_bot))], "k w1 fea", True)


def vb04():
    s = S("b4")
    k = 20
    fin = FINISH
    zb_deep = FLOOR_DEEP - fin - SLAB - BLIND - HERISSON
    sump_floor = FLOOR_DEEP - SUMP_DEPTH
    sump_struct = sump_floor - fin - 0.20
    zb_sump = sump_struct - BLIND - HERISSON
    # ---------------- A-A : pool-local x, looking SW (towards the villa), NW on the right
    XMIN, XMAX = -2.20, 11.15
    XR = 292
    X = lambda x: XR - (x - XMIN) * k
    Z = lambda z: 34 + (0.15 - z) * k
    vw_out, vw_in = VAULT["u_out0"] - U0, VAULT["u_in0"] - U0          # vault NW faces (pool-local x)
    wall_o = -(fin + WALL)
    _earth(s, X, Z, XMIN, XMAX, LV["tn"], zb_sump - 0.30)
    # gravel backfill SE + under the deck
    s.pl([(X(POOL_L + fin + WALL), Z(LV["tn"])), (X(POOL_L + fin + WALL + 0.45), Z(LV["tn"])), (X(POOL_L + fin + WALL + 0.45), Z(FLOOR_SHALLOW - 0.5)), (X(POOL_L + fin + WALL), Z(FLOOR_SHALLOW - 0.5))], "k w1 fgr", True)
    # lean concrete under the vault (to the pool excavation bottom)
    s.pl([(X(vw_out), Z(VAULT["base_under"])), (X(wall_o), Z(VAULT["base_under"])), (X(wall_o), Z(zb_deep)), (X(vw_out), Z(zb_deep))], "k w2 fcc2", True)
    # layers under the pool slab (profile), sump box
    prof = list(PROFILE)
    xl, xr_ = wall_o, POOL_L + fin + WALL
    def band(off_top, off_bot, cls):
        top = [(xl, prof[0][1] - off_top)] + [(x, z - off_top) for x, z in prof] + [(xr_, prof[-1][1] - off_top)]
        bot = [(xr_, prof[-1][1] - off_bot)] + [(x, z - off_bot) for x, z in reversed(prof)] + [(xl, prof[0][1] - off_bot)]
        s.pl([(X(a), Z(b)) for a, b in top + bot], cls, True)
    band(fin + SLAB + BLIND, fin + SLAB + BLIND + HERISSON, "k w1 fst")
    band(fin + SLAB, fin + SLAB + BLIND, "k w1 fs")
    band(fin, fin + SLAB, "k w3 fcc")
    sx0, sx1 = SUMP["x0"], SUMP["x1"]
    s.pl([(X(sx0 - 0.20 - fin), Z(FLOOR_DEEP - fin - SLAB)), (X(sx1 + 0.20 + fin), Z(FLOOR_DEEP - fin - SLAB)), (X(sx1 + 0.20 + fin), Z(zb_sump)), (X(sx0 - 0.20 - fin), Z(zb_sump))], "k w1 fst", True)
    s.pl([(X(sx0 - 0.20 - fin), Z(FLOOR_DEEP - fin)), (X(sx1 + 0.20 + fin), Z(FLOOR_DEEP - fin)), (X(sx1 + 0.20 + fin), Z(sump_struct)), (X(sx0 - 0.20 - fin), Z(sump_struct))], "k w3 fcc", True)
    # pool walls
    for xa in (wall_o, POOL_L + fin):
        zbot = (prof[0][1] if xa < 0 else prof[-1][1]) - fin
        s.rect(min(X(xa), X(xa + WALL)), Z(LV["beam_top"]), WALL * k, (LV["beam_top"] - zbot) * k, "k w3 fcc")
    # vault: base, NW wall, lintel under the coping, hatch
    s.pl([(X(vw_out), Z(VAULT["floor"])), (X(wall_o), Z(VAULT["floor"])), (X(wall_o), Z(VAULT["base_under"])), (X(vw_out), Z(VAULT["base_under"]))], "k w3 fcc", True)
    s.pl([(X(vw_out), Z(VAULT["top"])), (X(vw_in), Z(VAULT["top"])), (X(vw_in), Z(VAULT["floor"])), (X(vw_out), Z(VAULT["floor"]))], "k w3 fcc", True)
    lint0 = vw_in + HATCH["a1"] + 0.03
    s.pl([(X(lint0), Z(-0.80)), (X(wall_o), Z(-0.80)), (X(wall_o), Z(-0.95)), (X(lint0), Z(-0.95))], "k w3 fcc", True)
    ha0, ha1 = vw_in + HATCH["a0"], vw_in + HATCH["a1"]
    s.pl([(X(ha0), Z(VAULT["deck"])), (X(ha1), Z(VAULT["deck"])), (X(ha1), Z(-0.82)), (X(ha0), Z(-0.82))], "red w3 fs", True)
    s.line((X(ha0), Z(-0.77)), (X(ha1), Z(-0.77)), "k w1")
    # pad paving + coping + deck SE
    s.rect(X(-WALK), Z(VAULT["deck"]), (-WALK - (vw_out - 0.20)) * k, 0.10 * k, "k w1 fpv")
    for xa in (-WALK - 0.03, POOL_L - 0.03):
        s.rect(min(X(xa), X(xa + 0.53)), Z(LV["coping"]), 0.53 * k, 0.07 * k, "k w2 fs")
    # cascade (cut at y = 2.70)
    s.pl([(X(POOL_L), Z(CASCADE["top"])), (X(POOL_L + CASCADE["thick"]), Z(CASCADE["top"])), (X(POOL_L + CASCADE["thick"]), Z(LV["beam_top"])), (X(POOL_L), Z(LV["beam_top"]))], "red w3 fcc", True)
    s.pl([(X(POOL_L - 0.08), Z(SLOT["level"])), (X(POOL_L + 0.05), Z(SLOT["level"]))], "red w4")
    s.add(f'<path d="M{X(POOL_L - 0.08):.2f} {Z(SLOT["level"]):.2f} q {0.10 * k:.2f} {0.05 * k:.2f} {0.13 * k:.2f} {(SLOT["level"] - LV["water"]) * k:.2f}" class="red w2"/>')
    # water + steps beyond
    wpts = [(0, LV["water"])] + [(x, z) for x, z in prof] + [(POOL_L, LV["water"])]
    s.pl([(X(a), Z(b)) for a, b in wpts], "k w1 fw", True)
    s.pl([(X(sx0), Z(FLOOR_DEEP)), (X(sx1), Z(FLOOR_DEEP)), (X(sx1), Z(sump_floor)), (X(sx0), Z(sump_floor))], "k w1 fw", True)
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
    # equipment in the vault (seen towards SW): pump, filter (cut), riser
    va = lambda a: X(vw_in + a)
    pa0, pa1, _, _ = VLAY["pump"]
    zf = VAULT["floor"]
    s.rect(va(pa1), Z(zf + VLAY["plinth"]), (pa1 - pa0) * k, VLAY["plinth"] * k, "k w1 fs")
    s.rect(va(pa1), Z(zf + VLAY["plinth"] + PUMP["H"]), (pa1 - pa0) * k, PUMP["H"] * k, "k w2 fs")
    fa, _ = VLAY["filter"]
    s.rect(va(fa + FILTER["D"] / 2), Z(zf + FILTER["H"] + 0.04), FILTER["D"] * k, FILTER["H"] * k, "k w2 fs")
    ra, _ = VLAY["riser"]
    s.pl([(X(sx0 + 0.05), Z(SUMP_OUT)), (va(ra), Z(SUMP_OUT)), (va(ra), Z(VLAY["z_suction"])), (va(pa1), Z(VLAY["z_suction"]))], "pipe-s w4")
    valve(s, va(ra), Z(VAULT["floor"] + 0.12), horiz=False, r=1.1)
    # TN, levels, labels
    s.line((X(XMIN), Z(LV["tn"])), (X(-WALK - 1.25), Z(LV["tn"])), "k w2")
    s.line((X(POOL_L + 0.5), Z(LV["tn"])), (X(XMAX), Z(LV["tn"])), "k w2")
    for z, txt, xx, sd in [(LV["water"], f"{LV['water']:+.2f} eau", 4.0, "r"), (LV["coping"], f"{LV['coping']:+.2f}", 9.0, "r"),
                           (FLOOR_DEEP, f"{FLOOR_DEEP:+.2f}", 1.45, "r"), (sump_floor, f"{sump_floor:+.2f} puisard", 0.30, "r"),
                           (FLOOR_SHALLOW, f"{FLOOR_SHALLOW:+.2f}", 8.2, "r"), (VAULT["floor"], f"{VAULT['floor']:+.2f} fosse", -0.75, "r"),
                           (CASCADE["top"], f"{CASCADE['top']:+.2f} arase", POOL_L + 0.20, "l"), (SLOT["level"], f"{SLOT['level']:+.2f} lame", POOL_L - 0.35, "l"),
                           (VAULT["deck"], f"{VAULT['deck']:+.2f}", -1.60, "r"), (zb_deep, f"{zb_deep:+.2f} fond de fouille", -1.10, "r")]:
        s.level(X(xx), Z(z), txt, side=sd, section=True)
    s.dim((X(0.15), Z(LV["water"])), (X(0.15), Z(FLOOR_DEEP)), 0, f"{WATER_DEEP:.2f}")
    s.dim((X(vw_in + 0.10), Z(VAULT["top"])), (X(vw_in + 0.10), Z(VAULT["floor"])), 0, f"{V_IN_H:.2f}")
    s.dim((X(vw_in + 0.50), Z(LV["water"])), (X(vw_in + 0.50), Z(VAULT["floor"] + 0.15)), 0, f"{LV['water'] - VAULT['floor'] - 0.15:.2f}")
    chain = [vw_out, vw_in, wall_o, 0, POOL_L, POOL_L + CASCADE["thick"]]
    zz = Z(zb_sump - 0.30) + 5
    for a_, b_ in zip(chain, chain[1:]):
        s.dim((X(a_), zz), (X(b_), zz), 0, f"{abs(b_ - a_):.2f}")
    s.t(X(vw_in + 0.55), Z(-1.05), "FOSSE FT", "t tiny2 b red-t")
    s.t(X(vw_in + 0.55), Z(-1.20), "P + F", "t tiny2")
    s.t(X(-0.90), Z(-0.50), "Trappe TR", "t tiny2 b red-t")
    s.t(X(0.30), Z(sump_floor - 0.62), "PG", "t tiny2 b")
    s.t(X(-0.85), Z(-2.55), "gros béton", "t tiny2")
    s.t(X(POOL_L + 0.20), Z(CASCADE["top"] + 0.32), "CAS", "t tiny2 b red-t")
    s.t(X(POOL_L / 2), 22, "COUPE A-A  (longitudinale à 2.70 du bord SO, vue vers la villa)  1/50", "t ct", "middle")
    s.t(X(0.75), zz + 7, "GRAND FOND - FOSSE (côté NO)", "t tiny2 b", "middle")
    s.t(X(POOL_L - 1.25), zz + 7, "PETIT BAIN - CASCADE (côté allée)", "t tiny2 b", "middle")
    # ---------------- B-B : across the pool at x = 0.30, looking NW (towards the vault), v to the right
    VMIN = POOL["v0"] - 2.40
    Xb = lambda v: 24 + (v - VMIN) * k
    Zb = lambda z: 150 + (0.15 - z) * k
    vmax = POOL["v1"] + 1.60
    pv0, pv1 = POOL["v0"], POOL["v1"]
    s.pl([(Xb(VMIN), Zb(LV["tn"])), (Xb(vmax), Zb(LV["tn"])), (Xb(vmax), Zb(zb_sump - 0.30)), (Xb(VMIN), Zb(zb_sump - 0.30))], "k w1 fea", True)
    s.rect(Xb(pv0 - WALL - fin - 0.45), Zb(LV["tn"]), (POOL_W + 2 * (WALL + fin + 0.45)) * k, (LV["tn"] - (FLOOR_DEEP - fin - SLAB)) * k, "k w1 fgr")
    s.rect(Xb(pv0 - WALL - fin - 0.45), Zb(FLOOR_DEEP - fin - SLAB), (POOL_W + 2 * (WALL + fin + 0.45)) * k, (BLIND + HERISSON) * k, "k w1 fst")
    s.rect(Xb(pv0 - WALL - fin), Zb(FLOOR_DEEP - fin), (POOL_W + 2 * (WALL + fin)) * k, SLAB * k, "k w3 fcc")
    sy0, sy1 = pv0 + SUMP["y0"], pv0 + SUMP["y1"]
    s.rect(Xb(sy0 - 0.20 - fin), Zb(FLOOR_DEEP - fin - SLAB), (sy1 - sy0 + 0.40 + 2 * fin) * k, (FLOOR_DEEP - fin - SLAB - zb_sump) * k, "k w1 fst")
    s.rect(Xb(sy0 - 0.20 - fin), Zb(FLOOR_DEEP - fin), (sy1 - sy0 + 0.40 + 2 * fin) * k, (FLOOR_DEEP - fin - sump_struct) * k, "k w3 fcc")
    for vv in (pv0 - WALL - fin, pv1 + fin):
        s.rect(Xb(vv), Zb(LV["beam_top"]), WALL * k, (LV["beam_top"] - (FLOOR_DEEP - fin)) * k, "k w3 fcc")
    s.rect(Xb(pv0), Zb(LV["water"]), POOL_W * k, (LV["water"] - FLOOR_DEEP) * k, "k w1 fw")
    s.rect(Xb(sy0), Zb(FLOOR_DEEP), (sy1 - sy0) * k, SUMP_DEPTH * k, "k w1 fw")
    s.line((Xb(sy0), Zb(FLOOR_DEEP)), (Xb(sy1), Zb(FLOOR_DEEP)), "k w4")
    for vv in (pv0 - WALK, pv1 - 0.03):
        s.rect(Xb(vv), Zb(LV["coping"]), 0.53 * k, 0.07 * k, "k w2 fs")
    s.pl([(Xb(VMIN), Zb(LV["deck_low"])), (Xb(pv0 - WALK), Zb(LV["deck_edge"])), (Xb(pv0 - WALK), Zb(LV["deck_edge"] - 0.12)), (Xb(VMIN), Zb(LV["deck_low"] - 0.12))], "k w1 fs", True)
    # skimmer mouths on the NW wall (beyond), vault behind (hidden)
    for y in SKIMMERS_Y:
        s.rect(Xb(pv0 + y - 0.25), Zb(LV["water"] + 0.08), 0.5 * k, 0.18 * k, "k w2 fs")
    s.rect(Xb(VAULT["v_out0"]), Zb(VAULT["top"]), (VAULT["v_out1"] - VAULT["v_out0"]) * k, (VAULT["top"] - VAULT["base_under"]) * k, "red w2 dash")
    s.rect(Xb(VAULT["v_in0"]), Zb(VAULT["top"]), (VAULT["v_in1"] - VAULT["v_in0"]) * k, V_IN_H * k, "k w1 dash")
    s.circ(Xb((sy0 + sy1) / 2), Zb(SUMP_OUT), 0.7, "pipe-s w3")
    # trench pipes A1 / A2 (cut)
    for vv, zz_, c_ in ((NE_A2, VLAY["z_A2"], "pipe-a2"), (NE_A1, VLAY["z_A1"], "pipe-a1")):
        s.circ(Xb(vv), Zb(zz_), 0.9, f"{c_} w3")
    for vv in (pv0 - WALL - fin - 0.30, pv1 + WALL + fin + 0.30):
        s.circ(Xb(vv), Zb(FLOOR_DEEP - fin - SLAB + 0.05), 0.9, "pipe-d w2")
    s.line((Xb(pv1 + 0.5), Zb(LV["tn"])), (Xb(vmax), Zb(LV["tn"])), "k w2")
    for z, txt, vv, sd in [(LV["water"], f"{LV['water']:+.2f}", pv0 + 0.6, "r"), (FLOOR_DEEP, f"{FLOOR_DEEP:+.2f}", pv0 + 0.9, "r"),
                           (sump_floor, f"{sump_floor:+.2f}", sy1 + 0.1, "r"), (LV["deck_low"], f"{LV['deck_low']:+.2f} plage", VMIN + 0.4, "r"),
                           (LV["tn"], f"{LV['tn']:+.2f} TN", pv1 + 0.9, "r"), (VAULT["floor"], f"{VAULT['floor']:+.2f} fosse (au-delà)", VAULT["v_in0"] + 0.1, "r")]:
        s.level(Xb(vv), Zb(z), txt, side=sd, section=True)
    zz = Zb(zb_sump - 0.30) + 5
    ch = [pv0, sy0, sy1, pv1]
    for a_, b_ in zip(ch, ch[1:]):
        s.dim((Xb(a_), zz), (Xb(b_), zz), 0, f"{b_ - a_:.2f}")
    s.dim((Xb(sy1 + 0.25), Zb(FLOOR_DEEP)), (Xb(sy1 + 0.25), Zb(sump_floor)), 0, f"{SUMP_DEPTH:.2f}")
    s.t(Xb(pv0 + 0.9), Zb(LV["water"] + 0.30), "SK1", "t tiny2 b")
    s.t(Xb(pv0 + SKIMMERS_Y[1] + 0.6), Zb(LV["water"] + 0.30), "SK2", "t tiny2 b")
    s.t(Xb((VAULT["v_in0"] + VAULT["v_in1"]) / 2), Zb(-1.35), "fosse FT (derrière le voile)", "t tiny2 red-t")
    s.t(Xb(pv1 + 0.95), Zb(-1.62), "A1 - A2", "t tiny2", "middle")
    s.t(Xb((VMIN + vmax) / 2), 138, "COUPE B-B  (transversale au puisard, vue vers la fosse)  1/50", "t ct", "middle")
    # ---- hatch legend + notes (right of B-B)
    lg = [("k w2 fcc", "Béton armé B25 + hydrofuge"), ("k w2 fcc2", "Gros béton dosé à 200 kg/m³"), ("k w1 fst", "Hérisson 40/80"),
          ("k w1 fgr", "Gravier drainant 15/25"), ("k w1 fea", "Terrain en place"), ("k w1 fw", "Eau")]
    s.t(222, 146, "HACHURES", "t cl", "start")
    for i, (c_, t_) in enumerate(lg):
        s.rect(222, 149 + i * 6, 9, 4.2, c_)
        s.t(234, 152.4 + i * 6, t_, "t cs", "start")
    # key plan
    kp, kk = (300, 196), 4.0
    KP = lambda u, v: (kp[0] - (u - 4.6) * kk, kp[1] + (v - POOL["v0"] + 0.8) * kk)
    s.t(222, 192, "PLAN DE REPÉRAGE  1/250", "t cl", "start")
    s.pl([KP(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w2 fw", True)
    s.pl([KP(*p) for p in rect_uv(VAULT["u_out0"], VAULT["v_out0"], VAULT["u_in1"], VAULT["v_out1"])], "red w2 fs", True)
    s.pl([KP(*p) for p in rect_uv(POOL["u1"], CASC_V[0], CASC_BACK, CASC_V[1])], "red w2 fcc", True)
    for (a_, b_, nm) in (((PAD[0] - 0.4, V0 + SEC_A_Y), (CASC_BACK + 0.6, V0 + SEC_A_Y), "A"), ((U0 + SEC_B_X, V0 - 0.6), (U0 + SEC_B_X, POOL["v1"] + 0.6), "B")):
        pa, pb = KP(*a_), KP(*b_)
        s.line(pa, pb, "k w1 axis")
        for pp in (pa, pb):
            s.circ(pp[0], pp[1], 1.8, "k w1 fs")
            s.t(pp[0], pp[1] + 0.9, nm, "t tiny2 b")
    x_, y_ = KP((POOL["u0"] + POOL["u1"]) / 2, POOL["v0"] - 0.9)
    s.t(x_, y_, "villa", "t tiny mute")
    notes = ["Le bassin de l'indice E est conservé : radier, voiles, chaînage, profil du fond.",
             "S'ajoutent le caisson du puisard sous le radier et la fosse accolée au voile NO.",
             f"Fosse : radier 0.20 sur gros béton coulé jusqu'au fond de fouille du bassin ({zb_deep:+.2f}) :",
             "même assise que le bassin, pas de tassement différentiel.",
             "Voile NO commun : étanchéité du bassin côté eau, revêtement cristallin côté fosse (VB-08).",
             f"Pompe {LV['water'] - VAULT['floor'] - 0.15:.2f} m sous le plan d'eau : aspiration en charge, pas d'amorçage en service.",
             "Seule canalisation sous l'ouvrage : la sortie du puisard, noyée dans le gros béton, éprouvée avant coulage.",
             "Buses RA1-RA2 et chambre de la cascade : coupe C-C (VB-06)."]
    s.t(24, 236, "NOTES", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(24, 242 + i * 4.8, n, "t tiny2", "start")
    frame(s, "VB-04")
    s.title = "VB-04 Coupes"
    return s


# ==========================================================================
# VB-05  Fosse technique intégrée : plan 1/10, coupes A'-A' et B'-B' 1/20
# ==========================================================================

def vb05():
    s = S("b5")
    K = 100
    xp = lambda a: 178 - (a + 0.24) * K          # a towards the pool = to the left (as VB-02)
    yp = lambda b: 34 + (b + 0.24) * K
    Pp = lambda a, b: (xp(a), yp(b))

    def rr(a0, b0, a1, b1, c):
        s.pl([Pp(a0, b0), Pp(a1, b0), Pp(a1, b1), Pp(a0, b1)], c, True)
    s.add(f'<defs><clipPath id="b5p"><rect x="20" y="30" width="162" height="186"/></clipPath></defs><g clip-path="url(#b5p)">')
    rr(-0.40, -0.40, 1.40, 1.70, "k w1 fpv")
    rr(-0.20, -0.20, 1.10, 0.0, "k w3 fcc")
    rr(-0.20, 1.30, 1.10, 1.50, "k w3 fcc")
    rr(-0.20, 0.0, 0.0, 1.30, "k w3 fcc")
    rr(1.10, -0.40, 1.30, 1.70, "k w3 fcc")
    rr(1.30, -0.40, 1.33, 1.70, "k w1 fs")
    rr(1.33, -0.40, 1.40, 1.70, "k w1 fw")
    rr(0.0, 0.0, 1.10, 1.30, "k w2 fs")
    # hatch (above) + coping edge
    rr(HATCH["a0"], HATCH["b0"], HATCH["a1"], HATCH["b1"], "red w2 dash")
    s.line(Pp(HATCH["a0"], HATCH["b0"]), Pp(HATCH["a1"], HATCH["b1"]), "red w1 dash")
    s.line(Pp(HATCH["a0"], HATCH["b1"]), Pp(HATCH["a1"], HATCH["b0"]), "red w1 dash")
    s.line(Pp(0.83, -0.40), Pp(0.83, 1.70), "k w1 axis")
    # sleeves through the walls
    for (a, b, horiz, w) in [(VLAY["A1_out"][0], 1.40, False, 0.10), (VLAY["A2_out"][0], 1.40, False, 0.10), (0.97, 1.40, False, 0.09), (0.97, -0.10, False, 0.09),
                             (-0.10, VLAY["B_out"][1], True, 0.09), (-0.10, VLAY["cable_in"][1], True, 0.07), (-0.10, VLAY["vents"][0][1], True, 0.13), (-0.10, VLAY["vents"][1][1], True, 0.13)]:
        if horiz:
            rr(-0.20, b - w / 2, 0.0, b + w / 2, "k w2 fs")
        else:
            rr(a - w / 2, b - 0.10, a + w / 2, b + 0.10, "k w2 fs")
    # equipment
    pa0, pa1, pb0, pb1 = VLAY["pump"]
    rr(pa0 - 0.05, pb0 - 0.05, pa1 + 0.05, pb1 + 0.05, "k w1 dash")
    rr(pa0, pb0 + 0.02, 0.55, pb1 - 0.02, "k w2 fs")
    for i in range(1, 7):
        aa = pa0 + i * (0.55 - pa0) / 7
        s.line(Pp(aa, pb0 + 0.03), Pp(aa, pb1 - 0.03), "k w1")
    rr(0.55, pb0, 0.69, pb1, "k w2 fs")
    pc = Pp(0.775, (pb0 + pb1) / 2)
    s.circ(pc[0], pc[1], 0.085 * K, "k w2 fs")
    s.circ(pc[0], pc[1], 0.065 * K, "k w1 dash")
    fa, fb = VLAY["filter"]
    fc = Pp(fa, fb)
    s.circ(fc[0], fc[1], FILTER["D"] / 2 * K, "k w3 fs")
    s.circ(fc[0], fc[1], 0.12 * K, "k w1 dash")
    gauge(s, *Pp(fa + 0.13, fb - 0.13), 1.6)
    ra, rb = VLAY["riser"]
    s.line(Pp(0.97, 1.40), Pp(0.97, rb), "pipe-s w4")
    s.line(Pp(0.97, -0.10), Pp(0.97, rb), "pipe-s w4")
    s.line(Pp(0.97, rb), Pp(0.86, rb), "pipe-s w4")
    rc = Pp(ra, rb)
    s.circ(rc[0], rc[1], 0.035 * K, "pipe-s w3 fs")
    valve(s, *Pp(0.97, VLAY["vs2"][1]), horiz=False, r=2.0)
    valve(s, *Pp(0.97, VLAY["vs1"][1]), horiz=False, r=2.0)
    s.pl([Pp(0.60, (pb0 + pb1) / 2), Pp(0.60, fb), Pp(fa + FILTER["D"] / 2, fb)], "k w4")
    hb = VLAY["header_b"]
    s.pl([Pp(fa, fb + FILTER["D"] / 2), Pp(fa, hb)], "k w4")
    s.line(Pp(VLAY["header_a"][0], hb), Pp(VLAY["header_a"][1], hb), "k w4")
    for a_, c_ in ((VLAY["A1_out"][0], "pipe-a1"), (VLAY["A2_out"][0], "pipe-a2")):
        s.line(Pp(a_, hb), Pp(a_, 1.70), f"{c_} w4")
        valve(s, *Pp(a_, 1.225), horiz=False, r=1.8)
    s.line(Pp(VLAY["header_a"][0], hb), Pp(-0.40, hb), "pipe-b w4")
    valve(s, *Pp(0.10, hb), horiz=True, r=1.8)
    s.line(Pp(0.0, VLAY["cable_in"][1]), Pp(pa0, VLAY["cable_in"][1]), "elec w3")
    s.line(Pp(pa0, VLAY["cable_in"][1]), Pp(pa0, pb0 + 0.06), "elec w3")
    s.line(Pp(-0.40, VLAY["cable_in"][1]), Pp(-0.20, VLAY["cable_in"][1]), "elec w3")
    da, db = VLAY["drain"]
    rr(da - 0.06, db - 0.06, da + 0.06, db + 0.06, "k w2 fs")
    for i in range(1, 4):
        s.line(Pp(da - 0.06, db - 0.06 + i * 0.03), Pp(da + 0.06, db - 0.06 + i * 0.03), "k w1")
    fla, flb = VLAY["float"]
    rr(fla - 0.03, flb - 0.03, fla + 0.03, flb + 0.03, "k w2 fk")
    rr(HATCH["a0"] + 0.01, 0.62, HATCH["a0"] + 0.05, 0.70, "k w2 fs")
    s.line(Pp(0.52, 0.555), Pp(0.22, 0.53), "k w1 arrow")
    s.add("</g>")
    # tags
    tg = [("P", (0.39, (pb0 + pb1) / 2)), ("PF", (0.775, pb1 + 0.07)), ("F", (fa, fb + 0.02)), ("M", (fa + 0.20, fb - 0.13)),
          ("VA", (1.04, rb + 0.06)), ("VS1", (1.05, VLAY["vs1"][1])), ("VS2", (1.05, VLAY["vs2"][1])),
          ("V1", (VLAY["A1_out"][0] + 0.06, 1.225)), ("V2", (VLAY["A2_out"][0] + 0.06, 1.225)), ("V3", (0.10, hb - 0.06)),
          ("SF", (da + 0.10, db + 0.02)), ("FL", (fla + 0.07, flb + 0.02)), ("CT", (HATCH["a0"] + 0.09, 0.66)),
          ("VT1", (-0.10, VLAY["vents"][0][1] - 0.09)), ("VT2", (-0.10, VLAY["vents"][1][1] - 0.09))]
    for t_, (a_, b_) in tg:
        x_, y_ = Pp(a_, b_)
        s.t(x_, y_ + 1.0, t_, "t tiny2 b", "middle" if a_ > 0 else "middle")
    for t_, (a_, b_), an in (("A1 → buses", (VLAY["A1_out"][0] + 0.02, 1.63), "end"), ("A2 → cascade", (VLAY["A2_out"][0] - 0.02, 1.63), "start"),
                             ("← SK2", (0.95, 1.63), "end"), ("← SK1", (0.95, -0.36), "end"), ("B → borne", (-0.22, hb + 0.07), "start"),
                             ("230 V → coffret", (-0.22, VLAY["cable_in"][1] - 0.05), "start")):
        x_, y_ = Pp(a_, b_)
        s.t(x_, y_, t_, "t tiny2", "end" if an == "start" else "start")
    x_, y_ = Pp(1.36, 0.65)
    s.t(x_, y_, "BASSIN", "t tiny2 b red-t", "middle", -90)
    x_, y_ = Pp(0.45, 0.03)
    s.t(x_, y_ + 0.6, "trappe 0.75 × 1.20 (au-dessus)", "t tiny red-t", "middle")
    x_, y_ = Pp(0.36, 0.555)
    s.t(x_, y_ - 1.0, "pente 1 % vers SF", "t tiny", "middle")
    # plan dimensions
    s.dim(Pp(1.10, -0.20), Pp(0.0, -0.20), -4, f"{V_IN_A:.2f}")
    s.dim(Pp(0.0, -0.20), Pp(-0.20, -0.20), -4, f"{V_WALL:.2f}")
    s.dim(Pp(1.30, -0.20), Pp(1.10, -0.20), -4, f"{WALL:.2f}")
    s.dim(Pp(-0.20, 0.0), Pp(-0.20, 1.30), 9, f"{V_IN_B:.2f}")
    s.dim(Pp(HATCH["a1"], 1.50), Pp(HATCH["a0"], 1.50), 6, f"{HATCH['a1'] - HATCH['a0']:.2f}", size=2.5)
    s.dim(Pp(pa1, pb0 - 0.03), Pp(pa0, pb0 - 0.03), 2, f"{pa1 - pa0:.2f}", size=2.4)
    s.t(100, 26, "PLAN DE LA FOSSE  1/10", "t ct")
    # ---------------- A'-A' : along a at b = riser line, looking SW (pool on the left), 1/20
    k = 50
    xa = lambda a: 310 - (a + 0.30) * k
    za = lambda z: 32 + (-0.50 - z) * k
    zf, zt = VAULT["floor"], VAULT["top"]
    s.add(f'<defs><clipPath id="b5a"><rect x="200" y="28" width="112" height="98"/></clipPath></defs><g clip-path="url(#b5a)">')
    s.pl([(xa(-0.30), za(LV["tn"] + 0.05)), (xa(-0.20), za(LV["tn"] + 0.05)), (xa(-0.20), za(-2.40)), (xa(-0.30), za(-2.40))], "k w1 fea", True)
    s.rect(xa(1.10), za(-2.00), 1.30 * k, 0.40 * k, "k w1 fcc2")
    s.rect(xa(1.10), za(zf), 1.30 * k, 0.20 * k, "k w3 fcc")
    s.rect(xa(0.0), za(zt), 0.20 * k, (zt - (-2.00)) * k, "k w3 fcc")
    s.rect(xa(1.30), za(LV["beam_top"]), 0.20 * k, (LV["beam_top"] + 2.40) * k, "k w3 fcc")
    s.rect(xa(1.33), za(LV["beam_top"]), 0.03 * k, (LV["beam_top"] + 2.40) * k, "k w1 fs")
    s.pl([(xa(1.33), za(LV["water"])), (xa(1.80), za(LV["water"])), (xa(1.80), za(-2.40)), (xa(1.33), za(-2.40))], "k w1 fw", True)
    s.rect(xa(1.10), za(-0.80), 0.32 * k, 0.15 * k, "k w3 fcc")
    s.rect(xa(1.36), za(LV["coping"]), 0.53 * k, 0.07 * k, "k w2 fs")
    s.rect(xa(-0.02), za(VAULT["deck"]), 0.04 * k, 0.10 * k, "k w1 fs")
    s.rect(xa(-0.30), za(VAULT["deck"]), 0.30 * k, 0.08 * k, "k w1 fpv")
    s.pl([(xa(-0.02), za(VAULT["deck"])), (xa(0.82), za(VAULT["deck"])), (xa(0.82), za(-0.82)), (xa(-0.02), za(-0.82))], "red w3 fs", True)
    s.line((xa(-0.02), za(-0.80)), (xa(0.82), za(-0.80)), "k w1")
    s.line((xa(0.02), za(VAULT["deck"])), (xa(0.02) - 0.75 * k * math.cos(math.radians(70)), za(VAULT["deck"]) - 0.75 * k * math.sin(math.radians(70))), "red w2 dash")
    s.line((xa(-0.20), za(-0.85)), (xa(-0.20), za(-2.00)), "k w4")
    s.line((xa(-0.20), za(-2.00)), (xa(1.10), za(-2.00)), "k w4")
    for (x0_, z0_, x1_, z1_) in [(0.02, zf + 0.02, 1.08, zf + 0.02), (0.02, zt, 0.02, zf), (1.08, -0.95, 1.08, zf)]:
        s.line((xa(x0_), za(z0_)), (xa(x1_), za(z1_)), "pipe-d w2")
    s.rect(xa(pa1 + 0.05), za(zf + VLAY["plinth"]), (pa1 - pa0 + 0.10) * k, VLAY["plinth"] * k, "k w1 fs")
    zb = zf + VLAY["plinth"]
    s.rect(xa(0.55), za(zb + 0.26), (0.55 - pa0) * k, 0.24 * k, "k w2 fs")
    s.rect(xa(0.69), za(zb + PUMP["H"]), 0.14 * k, PUMP["H"] * k, "k w2 fs")
    s.rect(xa(pa1), za(zb + PUMP["H"] - 0.02), (pa1 - 0.69) * k, (PUMP["H"] - 0.02) * k, "k w2 fs")
    s.rect(xa(pa1 + 0.01), za(zb + PUMP["H"] + 0.02), (pa1 - 0.69 + 0.02) * k, 0.04 * k, "k w2 fs")
    s.pl([(xa(0.62), za(zb + PUMP["H"])), (xa(0.62), za(-1.20))], "k w4")
    s.circ(xa(0.62), za(-1.20), 1.2, "k w2 fs")
    zs = VLAY["z_suction"] - 0.10
    s.pl([(xa(ra), za(-2.40)), (xa(ra), za(zs)), (xa(pa1), za(zs))], "pipe-s w4")
    valve(s, xa(ra), za(zf + 0.14), horiz=False, r=1.4)
    s.circ(xa(ra), za(VLAY["z_A2"]), 1.3, "pipe-s w3 fs")
    s.t(xa(ra) - 2.0, za(VLAY["z_A2"]) + 1.0, "SK1", "t tiny2 b", "end")
    s.line((xa(ra), za(VLAY["z_A2"]) + 1.3), (xa(ra), za(zs)), "pipe-s w3")
    s.rect(xa(0.0), za(-0.90), 0.20 * k, 0.07 * k, "k w2 fs")
    s.add("</g>")
    for z, txt, a_, sd in [(LV["water"], f"{LV['water']:+.2f}", 1.62, "r"), (VAULT["deck"], f"{VAULT['deck']:+.2f}", -0.18, "l"), (zf, f"{zf:+.2f}", 0.90, "r"),
                           (LV["coping"], f"{LV['coping']:+.2f}", 1.20, "r")]:
        s.level(xa(a_), za(z), txt, side=sd, section=True)
    s.dim((xa(0.10), za(zt)), (xa(0.10), za(zf)), 0, f"{V_IN_H:.2f}", size=2.5)
    s.dim((xa(1.50), za(LV["water"])), (xa(1.50), za(zs)), 0, f"{LV['water'] - zs:.2f}", size=2.5)
    s.t(xa(0.30), za(-1.30), "P", "t tiny2 b")
    s.t(xa(pa1 - 0.07), za(zb + PUMP["H"] + 0.10), "PF", "t tiny2 b")
    s.t(xa(ra) - 2.2, za(zf + 0.14) + 1, "VA", "t tiny2 b", "end")
    s.t(xa(ra) + 2.0, za(-2.30), "vers PG", "t tiny2", "start")
    s.t(xa(0.40), za(-0.62), "TR", "t tiny2 b red-t")
    s.t(xa(-0.25), za(-2.30), "gros béton", "t tiny", "end")
    s.t(255, 26, "COUPE A'-A'  1/20", "t ct")
    # ---------------- B'-B' : along b at a = 0.30 (filter), looking NW (b to the right), 1/20
    xb = lambda b: 206 + (b + 0.30) * k
    zb_ = lambda z: 140 + (-0.50 - z) * k
    s.add(f'<defs><clipPath id="b5b"><rect x="200" y="134" width="112" height="90"/></clipPath></defs><g clip-path="url(#b5b)">')
    s.rect(xb(-0.30), zb_(-0.80), 1.90 * k, 1.60 * k, "k w1 fea")
    s.rect(xb(-0.20), zb_(-2.00), 1.70 * k, 0.40 * k, "k w1 fcc2")
    s.rect(xb(-0.20), zb_(zf), 1.70 * k, 0.20 * k, "k w3 fcc")
    for b0_ in (-0.20, 1.30):
        s.rect(xb(b0_), zb_(zt), 0.20 * k, (zt + 2.0) * k, "k w3 fcc")
    s.rect(xb(0.0), zb_(zt), 1.30 * k, V_IN_H * k, "k w1 fs")
    s.pl([(xb(0.0), zb_(VAULT["deck"])), (xb(1.30), zb_(VAULT["deck"])), (xb(1.30), zb_(-0.82)), (xb(0.0), zb_(-0.82))], "red w3 fs", True)
    for b0_ in (-0.30, 1.50):
        s.rect(xb(b0_), zb_(VAULT["deck"]), 0.10 * k if b0_ > 1 else 0.10 * k, 0.08 * k, "k w1 fpv")
    s.rect(xb(fb - FILTER["D"] / 2), zb_(zf + 0.04 + FILTER["H"]), FILTER["D"] * k, FILTER["H"] * k, "k w2 fs")
    s.rect(xb(fb - 0.12), zb_(zf + 0.04 + FILTER["H"] - 0.08), 0.24 * k, (FILTER["H"] - 0.16) * k, "k w1 dash")
    s.rect(xb(fb - FILTER["D"] / 2 - 0.02), zb_(zf + 0.04), (FILTER["D"] + 0.04) * k, 0.04 * k, "k w1 fs")
    s.rect(xb(pb0), zb_(zf + VLAY["plinth"] + 0.26), (pb1 - pb0) * k, 0.24 * k, "k w2 fhx")
    s.circ(xb(hb), zb_(VLAY["z_B"]), 1.6, "k w3 fs")
    s.pl([(xb(fb + FILTER["D"] / 2), zb_(-1.45)), (xb(hb), zb_(-1.45)), (xb(hb), zb_(VLAY["z_B"]) + 1.6)], "k w4")
    for b_, z_, r_ in ((VLAY["cable_in"][1], -0.95, 1.0), (VLAY["vents"][0][1], -0.95, 2.4), (VLAY["vents"][1][1], -0.93, 2.4)):
        s.circ(xb(b_), zb_(z_), r_, "k w1 fs")
    s.line((xb(VLAY["vents"][0][1]), zb_(-0.95) + 2.4), (xb(VLAY["vents"][0][1]), zb_(zf + 0.12)), "k w1 dash")
    s.rect(xb(db - 0.06), zb_(zf + 0.01), 0.12 * k, 0.10 * k, "k w2 fs")
    s.line((xb(db), zb_(zf - 0.09)), (xb(db), zb_(-2.10)), "pipe-d w3")
    s.rect(xb(flb - 0.03), zb_(zf + 0.12), 0.06 * k, 0.06 * k, "k w2 fk")
    s.add("</g>")
    for t_, (b_, z_) in (("F", (fb, -1.30)), ("P (coupé)", (0.31, -1.75 + 0.42)), ("V3 / B", (hb, VLAY["z_B"] - 0.12)), ("230 V", (VLAY["cable_in"][1], -1.06)),
                         ("VT1", (VLAY["vents"][0][1] + 0.10, -1.06)), ("VT2", (VLAY["vents"][1][1], -1.04)), ("SF", (db + 0.13, zf + 0.05)), ("FL", (flb, zf + 0.25))):
        s.t(xb(b_), zb_(z_), t_, "t tiny2 b")
    s.dim((xb(0.0), zb_(zt) - 6), (xb(1.30), zb_(zt) - 6), 0, f"{V_IN_B:.2f}", size=2.5)
    s.dim((xb(1.40), zb_(zt)), (xb(1.40), zb_(zf)), 0, f"{V_IN_H:.2f}", size=2.5)
    s.t(255, 132, "COUPE B'-B'  1/20", "t ct")
    # ---- equipment table + notes
    rows = [("P", f"Pompe {PUMP_FLOW} m³/h à {PUMP['head']:.0f} mCE, VS, 230 V, IPX5", f"≤ {PUMP['L']:.2f} × {PUMP['W']:.2f} × {PUMP['H']:.2f}, socle 0.06"),
            ("PF", "Préfiltre intégré (panier)", "couvercle sous la trappe"),
            ("F", f"Filtre à cartouche {FILTER['area']:.1f} m²", "≤ Ø0.40 × h 0.90, purgeur"),
            ("M", "Manomètre 0 - 2.5 bar", "sur le filtre"),
            ("VA / VS1-2", "Vannes puisard Ø63 / skimmers Ø50", "ligne a = 0.97"),
            ("V1 / V2", "Sélecteur : A1 buses / A2 cascade Ø63", "sorties voile NE"),
            ("V3", "Sélecteur : B rejet Ø50, cadenassable", "sortie voile NO"),
            ("SF", "Siphon de sol à clapet anti-retour", "→ drain périphérique"),
            ("FL / CT", "Flotteur et contact de trappe TBTS 24 V", "coupent la pompe"),
            ("VT1-VT2", "Ventilation Ø100 basse / haute", "→ grilles en massif")]
    s.t(192, 232, "ÉQUIPEMENTS DE LA FOSSE", "t cl", "start")
    table(s, 192, 234, ("Repère", "Désignation", "Enveloppe / position"), rows, (17, 58, 44), rh=4.6, size=2.4)
    notes = ["Fosse sèche : aucun appareil 230 V dans l'eau du bassin. Seul le moteur",
             "de la pompe est en 230 V, dans la fosse fermée à clé (VB-09).",
             "Commandes VA, VS1, VS2, V1 à V3, préfiltre et cartouche sous la trappe,",
             "ou à 0.17 m de son bord (sous la margelle).",
             "Pompe montée sur raccords union : dépose verticale par la trappe.",
             "Cartouche : levée verticale de 0.70 m, trappe ouverte.",
             "Avant d'ouvrir PF ou F : position E (VB-03) - procédure sous la trappe.",
             "Ventilation naturelle VT1 / VT2 : chaleur du moteur et humidité.",
             "Aucun produit chimique stocké dans la fosse.",
             "Dimensions intérieures = encombrement maximal des équipements",
             "+ passage de main : à recontrôler sur les fiches des modèles achetés."]
    s.t(22, 229, "NOTES", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(22, 234.5 + i * 4.55, n, "t tiny2", "start")
    frame(s, "VB-05")
    s.title = "VB-05 Fosse technique"
    return s


# ==========================================================================
# VB-06  Détail de la cascade : coupe C-C 1/10, élévation et plan 1/20
# ==========================================================================

def vb06():
    s = S("b6")
    K = 100
    xc = lambda x: 24 + (x - 9.70) * K
    zc = lambda z: 30 + (0.02 - z) * K
    th = CASCADE["thick"]
    core0, core1 = POOL_L + FINISH, POOL_L + FINISH + WALL
    s.add(f'<defs><clipPath id="b6c"><rect x="22" y="26" width="122" height="168"/></clipPath></defs><g clip-path="url(#b6c)">')
    zb_slab = FLOOR_SHALLOW - FINISH - SLAB
    s.rect(xc(core1), zc(LV["tn"]), 0.80 * K, (LV["tn"] + 1.70) * K, "k w1 fea")
    s.rect(xc(core1), zc(LV["beam_top"]), 0.45 * K, (LV["beam_top"] - zb_slab) * K, "k w1 fgr")
    s.rect(xc(9.70), zc(FLOOR_SHALLOW - FINISH), (core1 - 9.70) * K, SLAB * K, "k w3 fcc")
    s.rect(xc(9.70), zc(zb_slab), (core1 + 0.45 - 9.70) * K, BLIND * K, "k w1 fs")
    s.rect(xc(core0), zc(CASCADE["top"] - 0.05), WALL * K, (CASCADE["top"] - 0.05 - (FLOOR_SHALLOW - FINISH)) * K, "k w3 fcc")
    s.rect(xc(core1), zc(CASCADE["top"] - 0.05), (POOL_L + th - core1) * K, (CASCADE["top"] - 0.05 - LV["beam_top"]) * K, "k w2 fea2")
    s.rect(xc(POOL_L - 0.03), zc(CASCADE["top"]), (th + 0.06) * K, 0.05 * K, "k w2 fs")
    s.rect(xc(POOL_L), zc(LV["coping"] + 0.05), FINISH * K, (LV["coping"] + 0.05 - FLOOR_SHALLOW) * K, "k w1 fs")
    s.line((xc(POOL_L), zc(CASCADE["top"] - 0.05)), (xc(POOL_L), zc(FLOOR_SHALLOW)), "memb")
    s.line((xc(9.70), zc(FLOOR_SHALLOW)), (xc(POOL_L), zc(FLOOR_SHALLOW)), "memb")
    s.pl([(xc(9.70), zc(LV["water"])), (xc(POOL_L), zc(LV["water"])), (xc(POOL_L), zc(FLOOR_SHALLOW)), (xc(9.70), zc(FLOOR_SHALLOW))], "k w1 fw", True)
    bz0, bz1 = SLOT["level"] - 0.08, SLOT["level"] + 0.07
    s.pl([(xc(core0), zc(bz1)), (xc(core0 + 0.11), zc(bz1)), (xc(core0 + 0.11), zc(bz0)), (xc(core0), zc(bz0))], "k w3 fs", True)
    s.pl([(xc(core0 + 0.11), zc(bz1 + 0.01)), (xc(core0 + 0.11), zc(bz1)), (xc(POOL_L - 0.08), zc(SLOT["level"] + 0.003)), (xc(POOL_L - 0.08), zc(SLOT["level"] - 0.003))], "k w2 fs")
    s.pl([(xc(core0 + 0.11), zc(bz0)), (xc(POOL_L - 0.08), zc(SLOT["level"] - 0.010))], "k w2")
    s.add(f'<path d="M{xc(POOL_L - 0.08):.2f} {zc(SLOT["level"]):.2f} q {-0.10 * K:.2f} {0.03 * K:.2f} {-0.13 * K:.2f} {(SLOT["level"] - LV["water"]) * K:.2f}" class="pipe-s w4"/>')
    ra = SE_A2 - POOL["u0"]
    s.pl([(xc(ra), zc(-1.70)), (xc(ra), zc(VLAY["z_A2"])), (xc(ra), zc(SLOT["level"] - 0.01)), (xc(core0 + 0.11), zc(SLOT["level"] - 0.01))], "pipe-a2 w4")
    s.rect(xc(core1 - 0.01), zc(SLOT["level"] + 0.04), 0.02 * K, 0.10 * K, "k w2 fk")
    s.circ(xc(SE_A1 - POOL["u0"]), zc(VLAY["z_A1"]), 3.2, "pipe-a1 w3 fs")
    s.pl([(xc(POOL_L - 0.02), zc(INLET_LEVEL + 0.05)), (xc(core1), zc(INLET_LEVEL + 0.05)), (xc(core1), zc(INLET_LEVEL - 0.05)), (xc(POOL_L - 0.02), zc(INLET_LEVEL - 0.05))], "k w1 dash")
    s.pl([(xc(core1), zc(INLET_LEVEL)), (xc(SE_A1 - POOL["u0"]), zc(INLET_LEVEL)), (xc(SE_A1 - POOL["u0"]), zc(VLAY["z_A1"]) - 3.2)], "pipe-a1 w2 dash")
    s.rect(xc(core1 + 0.45), zc(LV["tn"] + 0.05), 0.40 * K, 0.05 * K, "k w1 fgz")
    s.add("</g>")
    for z, txt, x_, sd in [(CASCADE["top"], f"{CASCADE['top']:+.2f} arase", POOL_L + th + 0.02, "r"), (SLOT["level"], f"{SLOT['level']:+.2f} lame", 9.74, "r"),
                           (LV["water"], f"{LV['water']:+.2f} eau", 9.74, "r"), (INLET_LEVEL, f"{INLET_LEVEL:+.2f} axe RA2", 9.74, "r"),
                           (FLOOR_SHALLOW, f"{FLOOR_SHALLOW:+.2f} fond", 9.74, "r"), (LV["beam_top"], f"{LV['beam_top']:+.2f}", POOL_L + th + 0.15, "r")]:
        s.level(xc(x_), zc(z), txt, side=sd, section=True)
    s.dim((xc(POOL_L), zc(CASCADE["top"]) - 6), (xc(POOL_L + th), zc(CASCADE["top"]) - 6), 0, f"{th:.2f}", size=2.5)
    s.dim((xc(POOL_L - 0.08), zc(SLOT["level"]) - 9), (xc(POOL_L), zc(SLOT["level"]) - 9), 0, "0.08", size=2.4)
    s.dim((xc(9.76), zc(SLOT["level"]) + 4), (xc(9.76), zc(LV["water"]) - 1), 0, f"{SLOT['level'] - LV['water']:.2f}", size=2.5)
    s.dim((xc(POOL_L + th + 0.30), zc(CASCADE["top"])), (xc(POOL_L + th + 0.30), zc(LV["coping"])), 0, f"{CASCADE['top'] - LV['coping']:.2f}", size=2.5)
    labs = [((core0 + 0.05, bz1 - 0.02), ["Chambre de répartition inox 316L", "600 mm, pente 2 % vers la lame"]),
            ((POOL_L - 0.05, SLOT["level"]), ["Lame d'eau : fente 600 × 6 mm", "nez de 0.08 en surplomb"]),
            ((POOL_L + th - 0.08, -0.30), ["Parement et chapeau pierre", "arase arrondie"]),
            ((ra, -0.95), ["A2 Ø63 : remontée dans le parement", "fourreau à collerette"]),
            ((core0 + 0.10, -1.05), ["Noyau BA 0.20 sur le voile", "du bassin (repère 18)"]),
            ((POOL_L, -1.25), ["Étanchéité du bassin remontée", "jusqu'à l'arase (face mouillée)"]),
            ((SE_A1 - POOL["u0"], VLAY["z_A1"]), ["A1 Ø63 vers RA1-RA2", "(tranchée, au-delà)"])]
    for i, ((xx, zz), lines) in enumerate(labs):
        qy = 52 + i * 19
        s.label((xc(xx), zc(zz)), (146, qy), lines[0], "start", "t tiny2")
        s.t(150.6, qy + 4.4, lines[1], "t tiny2", "start")
    s.t(90, 22, "COUPE C-C  1/10", "t ct")
    # ---------------- front elevation from the pool 1/20
    k = 50
    xe = lambda y: 190 + (y - 2.30) * k
    ze = lambda z: 30 + (-0.02 - z) * k
    s.rect(xe(2.30), ze(LV["coping"]), 2.40 * k, (LV["coping"] - FLOOR_SHALLOW) * k, "k w1 ftl")
    s.rect(xe(2.30), ze(LV["water"]), 2.40 * k, (LV["water"] - FLOOR_SHALLOW) * k, "k w1 fw")
    s.rect(xe(CASCADE["y0"]), ze(CASCADE["top"]), (CASCADE["y1"] - CASCADE["y0"]) * k, (CASCADE["top"] - LV["water"]) * k, "red w3 fst")
    s.rect(xe(CASCADE["y0"] - 0.03), ze(CASCADE["top"]), (CASCADE["y1"] - CASCADE["y0"] + 0.06) * k, 0.05 * k, "k w2 fs")
    for y0_, y1_ in ((2.30, CASCADE["y0"]), (CASCADE["y1"], 4.70)):
        s.rect(xe(y0_), ze(LV["coping"]), (y1_ - y0_) * k, 0.07 * k, "k w2 fs")
    ly0, ly1 = 3.50 - SLOT["width"] / 2, 3.50 + SLOT["width"] / 2
    s.rect(xe(ly0), ze(SLOT["level"]), SLOT["width"] * k, (SLOT["level"] - LV["water"]) * k, "pipe-s w1 fw")
    s.line((xe(ly0), ze(SLOT["level"])), (xe(ly1), ze(SLOT["level"])), "k w4")
    for y_ in INLETS_Y:
        s.circ(xe(y_), ze(INLET_LEVEL), 1.4, "k w2 fs")
        s.circ(xe(y_), ze(INLET_LEVEL), 0.5, "k w1 fk")
    s.line((xe(2.30), ze(LV["water"])), (xe(4.70), ze(LV["water"])), "k w2")
    ch = [CASCADE["y0"], ly0, ly1, CASCADE["y1"]]
    for a_, b_ in zip(ch, ch[1:]):
        s.dim((xe(a_), ze(CASCADE["top"])), (xe(b_), ze(CASCADE["top"])), 4, f"{b_ - a_:.2f}", size=2.4)
    ch = [CASCADE["y0"], INLETS_Y[0], INLETS_Y[1], CASCADE["y1"]]
    for a_, b_ in zip(ch, ch[1:]):
        s.dim((xe(a_), ze(FLOOR_SHALLOW)), (xe(b_), ze(FLOOR_SHALLOW)), -4, f"{b_ - a_:.2f}", size=2.4)
    s.t(xe(INLETS_Y[0]), ze(INLET_LEVEL) + 4.6, "RA1", "t tiny2 b")
    s.t(xe(INLETS_Y[1]), ze(INLET_LEVEL) + 4.6, "RA2", "t tiny2 b")
    s.t(250, 22, "ÉLÉVATION CÔTÉ BASSIN  1/20", "t ct")
    # ---------------- plan 1/20
    xq = xe
    yq = lambda x: 122 + (x - 9.55) * k
    s.rect(xq(2.30), yq(9.55), 2.40 * k, 0.45 * k, "k w1 fw")
    s.rect(xq(2.30), yq(POOL_L), 2.40 * k, 0.50 * k, "k w1 fs")
    s.rect(xq(CASCADE["y0"]), yq(POOL_L), (CASCADE["y1"] - CASCADE["y0"]) * k, th * k, "red w3 fcc")
    s.rect(xq(CASCADE["y0"]), yq(POOL_L + th), (CASCADE["y1"] - CASCADE["y0"]) * k, (0.80 - th) * k, "k w1 fgz")
    s.rect(xq(ly0), yq(POOL_L + 0.03), SLOT["width"] * k, 0.11 * k, "k w1 dash")
    s.line((xq(ly0), yq(POOL_L - 0.08)), (xq(ly1), yq(POOL_L - 0.08)), "red w4")
    s.circ(xq(3.50), yq(SE_A2 - POOL["u0"]), 1.6, "pipe-a2 w3 fs")
    s.line((xq(2.30), yq(SE_A1 - POOL["u0"])), (xq(4.70), yq(SE_A1 - POOL["u0"])), "pipe-a1 w3")
    for y_ in INLETS_Y:
        s.line((xq(y_), yq(SE_A1 - POOL["u0"])), (xq(y_), yq(POOL_L)), "pipe-a1 w2")
        s.pl([(xq(y_) - 0.6, yq(POOL_L)), (xq(y_) + 0.6, yq(POOL_L)), (xq(y_), yq(POOL_L - 0.10))], "k w1 fk", True)
    s.t(xq(2.45), yq(9.75), "BASSIN", "t tiny2 b", "start")
    s.t(xq(3.05), yq(POOL_L + 0.62), "massif planté", "t tiny2", "middle")
    s.t(xq(4.62), yq(SE_A1 - POOL["u0"]) - 1, "A1", "t tiny2 b", "end")
    s.t(xq(3.50) + 2.4, yq(SE_A2 - POOL["u0"]) + 1, "A2", "t tiny2 b", "start")
    s.t(250, 116, "PLAN  1/20", "t ct")
    # ---- sheet calculation + notes
    q_ls = PUMP_FLOW / 3.6
    rows = [("Débit en position B", f"{PUMP_FLOW} m³/h = {q_ls:.2f} L/s"),
            ("Largeur de lame / fente", f"{SLOT['width']:.2f} m / {SLOT['gap'] * 1000:.0f} mm"),
            ("Débit linéique en position B", f"{R['slot_q_per_m']:.2f} L/s par m"),
            ("Minimum usuel pour une lame continue", f"{B.SHEET_MIN:.1f} L/s par m ({B.Q_SHEET_MIN:.1f} m³/h)"),
            ("Vitesse de sortie de la fente", f"{R['slot_v']:.2f} m/s"),
            ("Hauteur de chute", f"{SLOT['level'] - LV['water']:.2f} m"),
            ("Position A+B : partage libre / retenu", f"{R['q_ab_free_b']:.1f} / {PUMP_FLOW - R['q_a_in_ab']:.1f} m³/h sur la cascade"),
            ("Perte de charge chambre + lame", f"{B._branch_a2(PUMP_FLOW)[1][1]:.2f} mCE")]
    s.t(196, 196, "LAME D'EAU - CALCUL", "t cl", "start")
    table(s, 196, 198, ("Grandeur", "Valeur"), rows, (64, 52), rh=4.6, size=2.45)
    notes = ["Lame et chambre en inox 316L livrées en un bloc ; le débit minimal donné par",
             "le fabricant remplace la valeur usuelle retenue ici (15 gpm par pied).",
             f"En A+B, V1 est réglée pour garder au moins {B.Q_SHEET_MIN:.1f} m³/h sur la cascade.",
             "La face mouillée du mur reçoit l'étanchéité du bassin jusqu'à l'arase.",
             "Fourreau à collerette pour A2 dans le noyau ; la chambre se vide à l'arrêt.",
             f"Mur limité à {CASCADE['top'] - LV['coping']:.2f} m au-dessus de la margelle, arase arrondie,",
             "en zone de 0.55 m d'eau : « Plongeon interdit » reste affiché.",
             "La cascade aère l'eau : le pH monte et l'évaporation augmente.",
             "Buses RA1-RA2 dissimulées dans l'ombre de la lame, orientées vers PG.",
             "Lame inox reliée à la liaison équipotentielle (VB-09)."]
    s.t(24, 200, "NOTES", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(24, 206 + i * 4.6, n, "t tiny2", "start")
    frame(s, "VB-06")
    s.title = "VB-06 Cascade"
    return s


# ==========================================================================
# VB-07  Rejet contrôlé vers le jardin : plan 1/100, borne 1/10, conditions
# ==========================================================================

def vb07():
    s = S("b7")
    UMIN, VMIN = -1.80, 17.60
    P, k = rot_view(132, 24, UMIN, VMIN, 100)
    s.k = k
    s.add(f'<defs><clipPath id="b7p"><rect x="20" y="22" width="114" height="150"/></clipPath></defs><g clip-path="url(#b7p)">')
    s.pl([P(*p) for p in rect_uv(UMIN, VMIN, 9.5, 33.0)], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(NW_GARDEN_EDGE - 3.5, CHICKEN_V[0], NW_GARDEN_EDGE, CHICKEN_V[1])], "k w2 dash fch", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - WALK, POOL["v0"] - WALK, 9.5, POOL["v1"] + WALK)], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"], POOL["v0"], 9.5, POOL["v1"])], "red w3 fw", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], VMIN, 9.5, DECK[1])], "k w1 ftl", True)
    draw_hatch_plan(s, P)
    draw_vault_plan(s, P)
    draw_post_plan(s, P)
    x, y = P(SOAKAWAY["u"], SOAKAWAY["v"])
    s.circ(x, y, SOAKAWAY["r"] * k, "k w2 fst")
    for (u, v) in [(7.6, 26.6), (5.0, 29.5), (8.0, 31.5), (2.0, 27.0), (0.2, 30.6)]:
        x, y = P(u, v)
        tree(s, x, y, 2.6)
    route(s, P, ROUTES["B"], "pipe-b w4")
    route(s, P, ROUTES["B_out"], "pipe-b w4")
    s.add("</g>")
    def lab(u, v, t_, c="t tiny2", a="middle"):
        x_, y_ = P(u, v)
        s.t(x_, y_, t_, c, a)
    lab((POOL["u0"] + 9.5) / 2 + 0.3, (POOL["v0"] + POOL["v1"]) / 2, "BASSIN", "t tiny2 b red-t")
    lab(POST["u"] - 0.45, POST["v"] + 0.15, "BORNE", "t tiny2 b red-t", "start")
    lab(SOAKAWAY["u"], SOAKAWAY["v"] + 1.25, "Puits perdu Ø1.20", "t tiny2 b")
    lab(SOAKAWAY["u"], SOAKAWAY["v"] + 1.75, "(verger)", "t tiny2")
    x_, y_ = P(NW_GARDEN_EDGE + 0.35, 24.0)
    s.t(x_, y_, "limite du parc à poules", "t tiny2 mute", "middle", -90)
    lab(PAD[0] - 0.2, PAD[1] - 0.4, "fosse FT", "t tiny2 b red-t", "end")
    lab(POST["u"] + 0.15, 27.5, "PEHD Ø50", "t tiny2", "end")
    lab(4.20, ROUTES["B"][0][1] - 0.30, "B PVC Ø50", "t tiny2")
    lab(6.0, 18.3, "plage", "t tiny2 mute")
    ch = [U0, VAULT["u_out0"], POST["u"]]
    for a_, b_ in zip(ch, ch[1:]):
        s.dim(P(a_, POOL["v1"] + 0.8), P(b_, POOL["v1"] + 0.8), -3, f"{a_ - b_:.2f}", size=2.4)
    s.dim(P(POST["u"] - 0.6, POST["v"]), P(POST["u"] - 0.6, SOAKAWAY["v"]), 0, f"{SOAKAWAY['v'] - POST['v']:.2f}", size=2.4)
    s.t(77, 20, "TRACÉ DU CIRCUIT B  1/100", "t ct")
    band_north(s, 180 - U_ANG)
    # ---------------- control post 1/10 (section through the post)
    K = 100
    zt = 0.0
    xp = lambda d: 214 + d * K
    zp = lambda z: 34 + (0.12 - z) * K
    tn = LV["tn"]
    s.add(f'<defs><clipPath id="b7b"><rect x="146" y="26" width="166" height="160"/></clipPath></defs><g clip-path="url(#b7b)">')
    s.rect(xp(-0.62), zp(tn), 1.24 * K, (tn + 1.55) * K, "k w1 fea")
    s.rect(xp(-0.45), zp(tn), 0.90 * K, 0.12 * K, "k w2 fcc")
    s.rect(xp(-0.30), zp(zt + 0.04), 0.60 * K, (zt + 0.04 - tn) * K, "k w3 fs")
    s.rect(xp(-0.30), zp(zt + 0.04), 0.60 * K, 0.04 * K, "k w2 fcc")
    s.rect(xp(-0.30), zp(zt + 0.04), 0.07 * K, (zt + 0.04 - tn) * K, "k w2 fcc")
    s.rect(xp(0.23), zp(zt + 0.04), 0.07 * K, (zt + 0.04 - tn) * K, "k w2 fcc")
    s.rect(xp(-0.62), zp(-1.40), 1.24 * K, 0.20 * K, "k w1 fgr")
    zB = VLAY["z_B"]
    s.pl([(xp(-0.62), zp(zB)), (xp(-0.12), zp(zB)), (xp(-0.12), zp(-0.12))], "pipe-b w4")
    check(s, xp(-0.12), zp(-0.30), 1, horiz=False, r=2.0)
    s.pl([(xp(-0.12), zp(-0.12)), (xp(-0.12), zp(-0.06)), (xp(0.04), zp(-0.06)), (xp(0.04), zp(-0.35))], "pipe-b w4")
    s.circ(xp(-0.04), zp(-0.06) - 3.2, 2.4, "k w2 fs")
    s.line((xp(-0.04), zp(-0.06)), (xp(-0.04), zp(-0.06) - 0.8), "k w2")
    s.line((xp(0.04), zp(-0.20)), (xp(0.14), zp(-0.20)), "k w2")
    valve(s, xp(0.165), zp(-0.20), r=1.6)
    s.line((xp(0.19), zp(-0.20)), (xp(0.19), zp(-0.25)), "k w2")
    s.pl([(xp(0.04) - 2.2, zp(-0.35)), (xp(0.04) + 2.2, zp(-0.35)), (xp(0.04), zp(-0.35) + 3.4)], "k w2 fs", True)
    s.pl([(xp(0.04) + 2.2, zp(-0.35) + 1.7), (xp(0.30), zp(-0.35) + 1.7)], "pipe-b w4")
    s.circ(xp(0.33), zp(-0.35) + 1.7, 1.8, "k w2 fs")
    s.pl([(xp(0.04), zp(-0.35) + 3.4), (xp(0.04), zp(-1.10)), (xp(0.62), zp(-1.10))], "pipe-b w4")
    s.add("</g>")
    for txt, (d, z), q in [("CL clapet anti-retour", (-0.12, -0.30), (150, 70)), ("CV casse-vide, point haut ±0.00", (-0.04, 0.02), (150, 40)),
                           ("RP robinet de prélèvement", (0.165, -0.20), (270, 52)), ("V4 vanne 3 voies", (0.04, -0.37), (270, 62)),
                           ("Raccord rapide tuyau d'arrosage", (0.33, -0.33), (270, 74)), ("PEHD Ø50 → verger / puits perdu", (0.45, -1.10), (270, 120)),
                           ("B PVC Ø50 depuis la fosse (V3)", (-0.45, zB), (150, 150)), ("Borne maçonnée 0.60 × 0.40", (0.27, -0.55), (270, 92)),
                           ("porte inox à clé, chapeau BA", (0.27, -0.55), None)]:
        if q:
            a = "start" if q[0] > 200 else "end"
            s.label((xp(d), zp(z)), (q[0] + (0 if a == "start" else 42), q[1]), txt, a, "t tiny2")
        else:
            s.t(272.6, 96.5, txt, "t tiny2", "start")
    s.level(xp(0.30) + 3, zp(zt + 0.04), "+0.04 chapeau", side="r", section=True)
    s.level(xp(-0.50), zp(tn), f"{tn:+.2f} TN", side="l", section=True)
    s.dim((xp(-0.30), zp(zt + 0.04) - 5), (xp(0.30), zp(zt + 0.04) - 5), 0, "0.60", size=2.5)
    s.dim((xp(0.45), zp(zt + 0.04)), (xp(0.45), zp(tn)), 0, f"{zt + 0.04 - tn:.2f}", size=2.5)
    s.t(229, 20, "BORNE DE CONTRÔLE - COUPE  1/10", "t ct")
    # ---- discharge conditions
    rows = [("Chlore libre", "< 0.1 mg/L", "trousse DPD au robinet RP", "arrêter le chlore 5 à 7 jours, ou neutraliser, puis recontrôler"),
            ("pH", "6.5 à 8.5", "trousse ou bandelette", "corriger le pH avant le rejet"),
            ("Sel", "aucun électrolyseur au sel", "équipement du bassin", "eau salée : jamais au verger (puits perdu ou évacuation autorisée)"),
            ("Algicide, floculant, cuivre", "aucun ajout récent", "carnet d'entretien", "attendre le délai du fabricant, ou puits perdu"),
            ("Débit", f"≤ {B.Q_GARDEN:.0f} m³/h, V3 réglée", "manomètre, durée", f"vidange complète {hu(Q['water_vol'])} m³ = {R['drain_hours']:.1f} h de pompage"),
            ("Sol", "pas de flaque ni de ruissellement", "visuel pendant le rejet", "arrêter et reprendre le lendemain ; répartir sur plusieurs jours"),
            ("Destination", "verger NO / NE seulement", "-", "jamais vers le chemin public ni chez les voisins"),
            ("Saison", "vidange totale de mai à octobre", "-", "bassin vide en saison des pluies : risque de soulèvement (PL-05)")]
    s.t(22, 196, "CONDITIONS DE REJET AU JARDIN (position C du sélecteur)", "t cl", "start")
    table(s, 22, 198, ("Paramètre", "Seuil", "Contrôle", "Si non conforme"), rows, (40, 52, 46, 150), rh=4.8, size=2.45)
    notes = [f"Le circuit B part du sélecteur après le filtre : l'eau rejetée est filtrée. Le verger est plus bas que le bassin : le casse-vide CV (±0.00, {0 - LV['water']:.2f} m au-dessus du plan d'eau) coupe tout siphonnage à l'arrêt de la pompe.",
             "V3 reste fermée et cadenassée hors rejet. Le clapet CL interdit tout retour d'eau ou de terre vers la fosse. Valeurs de seuil usuelles : à adapter aux règles locales en vigueur."]
    for i, n in enumerate(notes):
        s.t(22, 249 + i * 5.0, n, "t tiny2", "start")
    frame(s, "VB-07")
    s.title = "VB-07 Rejet jardin"
    return s


# ==========================================================================
# VB-08  Structure et étanchéité : coupe au puisard et à la fosse 1/20
# ==========================================================================

def vb08():
    s = S("b8")
    k = 50
    fin = FINISH
    X = lambda x: 176 - (x + 1.75) * k          # pool-local x, NW (vault) on the right as VB-04
    Z = lambda z: 30 + (-0.52 - z) * k
    vw_out, vw_in = VAULT["u_out0"] - U0, VAULT["u_in0"] - U0
    wall_o = -(fin + WALL)
    zf, zt, zbu = VAULT["floor"], VAULT["top"], VAULT["base_under"]
    sump_floor = FLOOR_DEEP - SUMP_DEPTH
    sump_struct = sump_floor - fin - 0.20
    zb_deep = FLOOR_DEEP - fin - SLAB - BLIND - HERISSON
    zb_sump = sump_struct - BLIND - HERISSON
    x_end = 1.20
    s.add(f'<defs><clipPath id="b8c"><rect x="22" y="26" width="156" height="166"/></clipPath></defs><g clip-path="url(#b8c)">')
    s.rect(X(x_end), Z(LV["tn"]), (x_end + 1.75) * k, (LV["tn"] - zb_sump + 0.3) * k, "k w1 fea")
    s.rect(X(wall_o), Z(zbu), (vw_out - wall_o) * -k, (zbu - zb_deep) * k, "k w2 fcc2")
    s.rect(X(x_end), Z(FLOOR_DEEP - fin - SLAB), (x_end - wall_o) * k, (BLIND + HERISSON) * k, "k w1 fst")
    s.rect(X(SUMP["x1"] + 0.23), Z(FLOOR_DEEP - fin - SLAB), (SUMP["x1"] + 0.23 - wall_o) * k, (FLOOR_DEEP - fin - SLAB - zb_sump) * k, "k w1 fst")
    s.rect(X(x_end), Z(FLOOR_DEEP - fin), (x_end - wall_o) * k, SLAB * k, "k w3 fcc")
    s.rect(X(SUMP["x1"] + 0.23), Z(FLOOR_DEEP - fin), (SUMP["x1"] + 0.23 - wall_o) * k, (FLOOR_DEEP - fin - sump_struct) * k, "k w3 fcc")
    s.rect(X(SUMP["x1"]), Z(FLOOR_DEEP), (SUMP["x1"] - SUMP["x0"]) * k, SUMP_DEPTH * k, "k w1 fw")
    s.rect(X(x_end), Z(LV["water"]), (x_end - 0.0) * k, (LV["water"] - FLOOR_DEEP) * k, "k w1 fw")
    s.rect(X(0.0), Z(LV["beam_top"]), WALL * k, (LV["beam_top"] - (FLOOR_DEEP - fin)) * k, "k w3 fcc")
    s.rect(X(wall_o), Z(zf), (vw_out - wall_o) * -k, (zf - zbu) * k, "k w3 fcc")
    s.rect(X(vw_in), Z(zt), V_WALL * k, (zt - zbu) * k, "k w3 fcc")
    s.rect(X(wall_o), Z(zt), (vw_in - wall_o) * -k, (zt - zf) * k, "k w1 fs")
    lint0 = vw_in + HATCH["a1"] + 0.03
    s.rect(X(wall_o), Z(-0.80), (lint0 - wall_o) * -k, 0.15 * k, "k w3 fcc")
    s.rect(X(0.03), Z(LV["coping"]), 0.53 * k, 0.07 * k, "k w2 fs")
    s.pl([(X(vw_in + HATCH["a0"] - 0.07), Z(VAULT["deck"])), (X(vw_in + HATCH["a1"]), Z(VAULT["deck"])), (X(vw_in + HATCH["a1"]), Z(-0.82)), (X(vw_in + HATCH["a0"] - 0.07), Z(-0.82))], "red w3 fs", True)
    s.rect(X(vw_out), Z(VAULT["deck"]), 0.25 * k, 0.10 * k, "k w1 fpv")
    # waterproofing layers
    s.pl([(X(0.0), Z(LV["coping"] - 0.02)), (X(0.0), Z(FLOOR_DEEP)), (X(SUMP["x0"]), Z(FLOOR_DEEP)), (X(SUMP["x0"]), Z(sump_floor)), (X(SUMP["x1"]), Z(sump_floor)),
          (X(SUMP["x1"]), Z(FLOOR_DEEP)), (X(x_end), Z(FLOOR_DEEP))], "memb")
    s.pl([(X(wall_o - 0.015), Z(zt - 0.02)), (X(wall_o - 0.015), Z(zf + 0.015)), (X(vw_in - 0.015), Z(zf + 0.015)), (X(vw_in - 0.015), Z(zt - 0.02))], "k w2 dash")
    s.pl([(X(vw_out - 0.02), Z(VAULT["deck"] - 0.10)), (X(vw_out - 0.02), Z(zbu - 0.02)), (X(wall_o), Z(zbu - 0.02))], "k w4")
    s.rect(X(vw_out - 0.03), Z(-0.95), 0.20 * k, (-0.95 - zbu) * k, "k w1 fgr")
    # rebar (section dots + bars)
    def bars_v(x0, z0, z1, n):
        for i in range(n):
            z = z0 + (z1 - z0) * (i + 0.5) / n
            s.circ(X(x0), Z(z), 0.45, "k w1 fk")
    for xx in (wall_o + 0.04, -0.04):
        s.line((X(xx), Z(LV["beam_top"] - 0.04)), (X(xx), Z(FLOOR_DEEP - fin - SLAB + 0.04)), "red w2")
    for xx in (vw_out + 0.04, vw_in - 0.04):
        s.line((X(xx), Z(zt - 0.04)), (X(xx), Z(zbu + 0.04)), "red w2")
    for zz in (zf - 0.04, zbu + 0.04):
        s.line((X(vw_out + 0.04), Z(zz)), (X(wall_o - 0.04), Z(zz)), "red w2")
    for zz in (FLOOR_DEEP - fin - 0.04, FLOOR_DEEP - fin - SLAB + 0.04):
        s.line((X(x_end), Z(zz)), (X(SUMP["x1"] + 0.03), Z(zz)), "red w2")
    s.pl([(X(SUMP["x1"] + 0.19), Z(FLOOR_DEEP - fin - 0.04)), (X(SUMP["x1"] + 0.19), Z(sump_struct + 0.04)), (X(SUMP["x0"] - 0.19), Z(sump_struct + 0.04)), (X(SUMP["x0"] - 0.19), Z(FLOOR_DEEP - fin - 0.04))], "red w2")
    s.pl([(X(wall_o - 0.06), Z(zf - 0.04)), (X(wall_o + 0.10), Z(zf - 0.04)), (X(wall_o + 0.10), Z(zf + 0.40))], "red w3")
    s.pl([(X(wall_o - 0.06), Z(-1.10)), (X(wall_o + 0.10), Z(-1.10))], "red w3")
    bars_v(wall_o + 0.04, FLOOR_DEEP, LV["beam_top"], 8)
    # waterstops + sleeves
    for (xx, zz) in ((wall_o - 0.01, zf - 0.02), (vw_in - 0.10, zf - 0.01)):
        s.rect(X(xx) - 1.0, Z(zz) - 1.0, 2.0, 2.0, "k w1 fk")
    s.pl([(X(SUMP["x0"] + 0.05), Z(SUMP_OUT)), (X(VLAY["riser"][0] + vw_in), Z(SUMP_OUT)), (X(VLAY["riser"][0] + vw_in), Z(zf + 0.15))], "pipe-s w4")
    for (xx, zz, horiz) in ((wall_o - 0.06, SUMP_OUT, False), (VLAY["riser"][0] + vw_in, zf - 0.10, True)):
        if horiz:
            s.line((X(xx) - 3, Z(zz)), (X(xx) + 3, Z(zz)), "k w4")
        else:
            s.line((X(xx), Z(zz) - 3), (X(xx), Z(zz) + 3), "k w4")
    s.add("</g>")
    # numbered callouts
    calls = [((0.0, -1.70), "Étanchéité du bassin : ciment flexible 2 couches + bandes d'angle"),
             ((SUMP["x0"] + 0.30, sump_floor), "Puisard : même membrane continue, angles en gorge 5 × 5"),
             ((SUMP["x0"] + 0.30, FLOOR_DEEP + 0.01), "Cadre de grille scellé, collier d'étanchéité sous la membrane"),
             ((SUMP["x1"] + 0.10, sump_struct + 0.10), "Caisson du puisard BA 0.20, cadres HA12 (repère 17)"),
             ((wall_o + 0.10, -1.30), "Voile commun BA 0.20 : pas de modification d'armature (indice E)"),
             ((vw_in + 0.55, zf + 0.01), "Fosse : cristallin 2 couches en face intérieure"),
             ((vw_out - 0.02, -1.40), "Fosse : membrane bitumineuse extérieure + gravier drainant"),
             ((wall_o - 0.01, zf - 0.02), "Joint hydrogonflant aux reprises radier / voiles"),
             ((wall_o + 0.10, zf + 0.20), "Attentes HA10 e=15 scellées dans le voile (repère 16)"),
             ((vw_in + 0.55, zbu - 0.40), "Gros béton jusqu'au fond de fouille du bassin"),
             ((VLAY["riser"][0] + vw_in, zf - 0.10), "Fourreaux à collerette + bague hydrogonflante"),
             ((vw_in + 0.40, VAULT["deck"]), "Trappe A15 sur cornière scellée, joint à lèvre")]
    calls.sort(key=lambda c: -c[0][1])
    for i, ((xx, zz), txt) in enumerate(calls):
        x_, y_ = X(xx), Z(zz)
        qx, qy = 184, 34 + i * 7.6
        s.line((x_, y_), (qx - 2.6, qy), "k w1")
        s.circ(x_, y_, 0.5, "k w1 fk")
        callout(s, qx, qy, str(i + 1), r=2.4)
        s.t(qx + 4, qy + 1.0, txt, "t tiny2", "start")
    for z, txt, xx, sd in [(LV["water"], f"{LV['water']:+.2f}", 0.90, "r"), (FLOOR_DEEP, f"{FLOOR_DEEP:+.2f}", 1.05, "r"), (sump_floor, f"{sump_floor:+.2f}", 0.65, "r"),
                           (zf, f"{zf:+.2f}", vw_in + 0.85, "r"), (zb_deep, f"{zb_deep:+.2f}", -0.80, "r"), (zb_sump, f"{zb_sump:+.2f}", 0.75, "r")]:
        s.level(X(xx), Z(z), txt, side=sd, section=True)
    s.t(100, 22, "COUPE AU PUISARD ET À LA FOSSE (à 2.50 du bord SO)  1/20", "t ct")
    # ---- tables
    lay = [("Membrane ciment flexible", "ÉTANCHÉITÉ du bassin", "faces mouillées, puisard, face de la cascade"),
           ("Enduit hydrofuge 2 couches", "support régulier", "sous la membrane"),
           ("Béton B25 + hydrofuge", "structure (non considérée étanche)", "radier, voiles, caisson, fosse"),
           ("Mosaïque + joint époxy", "FINITION (non étanche)", "sur la membrane"),
           ("Cristallin 2 couches", "ÉTANCHÉITÉ de la fosse (côté sec)", "faces intérieures de la fosse"),
           ("Membrane bitumineuse", "ÉTANCHÉITÉ de la fosse (côté terre)", "faces extérieures + sous-face"),
           ("Joints et fourreaux", "continuité aux reprises / traversées", "toutes reprises et traversées")]
    s.t(22, 200, "STRATÉGIE D'ÉTANCHÉITÉ - QUELLE COUCHE ÉTANCHE", "t cl", "start")
    table(s, 22, 202, ("Couche", "Rôle", "Où"), lay, (44, 52, 58), rh=4.5, size=2.4)
    rb = [(str(b["pos"]), b["desc"], f"HA{b['d']}", str(b["n"]), f"{b['L']:.2f}", f"{b['kg']:.1f}") for b in R["rebar_b"]]
    rb.append(("", "Total variante (en plus de la nomenclature PL-05)", "", "", "", f"{R['steel_b']:.1f}"))
    s.t(182, 200, "ACIERS DE LA VARIANTE (FeE500)", "t cl", "start")
    table(s, 182, 202, ("Rep.", "Désignation", "Ø", "Nb", "L (m)", "kg"), rb, (9, 74, 10, 8, 11, 14), rh=4.5, size=2.3)
    s.t(22, 245, f"Béton de la fosse et du puisard : {R['c_vault'] + R['c_sump']:.2f} m³ B25 + hydrofuge - gros béton : {R['lean_fill']:.2f} m³ - surfaces : cristallin {R['vault_wp_in']:.2f} m², membrane extérieure {R['vault_wp_out']:.2f} m², puisard {R['sump_surf']:.2f} m².", "t tiny2", "start")
    notes = ["Le voile NO reste un voile de bassin : il est calculé à l'indice E pour la poussée de l'eau sans remblai, cas qui devient permanent sur la hauteur de la fosse.",
             "Le puisard abaisse localement le radier de 0.40 : caisson armé coulé avec le radier, sans reprise sous l'eau.",
             "La fosse ne s'appuie pas sur le remblai : radier sur gros béton descendu au fond de fouille du bassin, attentes dans le voile commun.",
             "Prédimensionnement BAEL 91 mod. 99 à faire vérifier et viser par un BET agréé (RPS 2000 version 2011 à appliquer)."]
    for i, n in enumerate(notes):
        s.t(22, 252 + i * 4.8, n, "t tiny2", "start")
    frame(s, "VB-08")
    s.title = "VB-08 Structure et étanchéité"
    return s


# ==========================================================================
# VB-09  Concept de sécurité électrique : volumes 1/100, unifilaire, mesures
# ==========================================================================

def _offset_poly(P, u0, v0, u1, v1, d, n=8):
    pts = []
    for (cu, cv, a0) in ((u1, v1, 0), (u0, v1, 90), (u0, v0, 180), (u1, v0, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append(P(cu + d * math.cos(a), cv + d * math.sin(a)))
    return pts


def _brk(s, x, y, lab, sub=None):
    """Circuit-breaker symbol on a vertical line at (x, y)."""
    s.line((x, y - 4), (x, y - 1.6), "k w2")
    s.line((x, y - 1.6), (x + 1.6, y + 1.6), "k w2")
    s.line((x - 0.8, y - 2.4), (x + 0.8, y - 0.8), "k w2")
    s.line((x, y + 1.6), (x, y + 4), "k w2")
    s.t(x + 2.4, y + 0.6, lab, "t tiny2 b", "start")
    if sub:
        s.t(x + 2.4, y + 3.6, sub, "t tiny", "start")


def vb09():
    s = S("b9")
    P, k = rot_view(232, 22, -0.5, 12.4, 100)
    s.k = k
    s.add(f'<defs><clipPath id="b9p"><rect x="22" y="22" width="210" height="146"/></clipPath></defs><g clip-path="url(#b9p)">')
    s.pl([P(*p) for p in rect_uv(-0.5, 12.4, 20.5, 27.0)], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], 12.4, HOUSE["u1"], HOUSE["v1"])], "k w3 fhx", True)
    s.pl([P(*p) for p in rect_uv(STAIR["u0"], 12.4, STAIR["u1"], STAIR["v1"])], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], DECK[0], HOUSE["u1"], DECK[1])], "k w1 ftl", True)
    s.pl(_offset_poly(P, POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"], 3.5), "z2", True)
    s.pl(_offset_poly(P, POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"], 2.0), "z1", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - WALK, POOL["v0"] - WALK, POOL["u1"] + WALK, POOL["v1"] + WALK)], "k w1 fs", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w3 fw", True)
    draw_hatch_plan(s, P)
    draw_vault_plan(s, P)
    draw_cascade_plan(s, P)
    route(s, P, ROUTES["CABLE"], "elec w4")
    cu, cv = COFFRET["u"], COFFRET["v"]
    lv = POOL["v0"] - 0.40
    s.pl([P(cu + 0.20, cv), P(cu + 0.20, lv), P(U0 + FITTINGS["lights"][-1][0], lv)], "selv w3")
    for (x, y) in FITTINGS["lights"]:
        s.line(P(U0 + x, lv), P(U0 + x, POOL["v0"]), "selv w3")
        c_ = P(U0 + x, POOL["v0"])
        s.circ(c_[0], c_[1], 1.2, "k w1 flt")
    lel = vu(0.30, 0.10)
    sw_, ne_ = POOL["v0"] - 0.25, POOL["v1"] + 0.25
    s.pl([P(*lel), P(lel[0], sw_), P(U0 + FITTINGS["ladder"][0][0], sw_), P(U0 + FITTINGS["ladder"][0][0], POOL["v0"])], "pe")
    s.pl([P(*lel), P(lel[0], ne_), P(POOL["u1"] + 0.25, ne_), P(POOL["u1"] + 0.25, CASC_MID)], "pe")
    s.pl([P(*lel), P(HATCH_UV[0][0], HATCH_UV[0][1])], "pe")
    s.pl([P(*lel), P(cu - 0.60, lel[1]), P(cu - 0.60, cv + 0.30)], "pe")
    s.pl([P(cu - 0.15, cv), P(cu + 0.45, cv), P(cu + 0.45, cv + 0.25), P(cu - 0.15, cv + 0.25)], "red w3 fs", True)
    x_, y_ = P(cu - 0.60, cv + 0.30)
    s.circ(x_, y_, 1.4, "k w2 fs")
    s.line((x_ - 1.0, y_), (x_ + 1.0, y_), "k w1")
    s.line((x_, y_ - 1.0), (x_, y_ + 1.0), "k w1")
    for (u, v) in [(POOL["u0"] - 1.2, POOL["v1"] + 1.0), (POOL["u1"] + 1.2, POOL["v1"] + 1.0)]:
        x_, y_ = P(u, v)
        s.circ(x_, y_, 1.0, "k w1 fk")
    s.add("</g>")
    def lab(u, v, t_, c="t tiny2", a="middle"):
        x_, y_ = P(u, v)
        s.t(x_, y_, t_, c, a)
    lab(11.55, 20.75, "VOLUME 0 - bassin : seulement P1-P3 en TBTS 12 V", "t tiny2 b red-t")
    lab(11.55, POOL["v1"] + 1.15, "VOLUME 1 (2.00 m)", "t tiny2 b")
    lab(11.55, POOL["v1"] + 2.85, "VOLUME 2 (de 2.00 à 3.50 m)", "t tiny2 b")
    lab(cu, cv - 0.35, "CP coffret piscine - hors volumes", "t tiny2 b red-t")
    lab(PAD[0] - 0.15, PAD[3] + 0.55, "FT : moteur 230 V en volume 1", "t tiny2 b red-t", "start")
    lab(PAD[0] - 0.15, PAD[3] + 0.95, "fosse fermée à clé, contact CT", "t tiny2 red-t", "start")
    lab(POOL["u0"] - 1.25, POOL["v1"] + 1.45, "borne : TBTS 12 V", "t tiny", "middle")
    lab(POOL["u1"] + 1.25, POOL["v1"] + 1.45, "borne : TBTS 12 V", "t tiny", "middle")
    lab(4.05, 16.0, "3G2.5 + TBTS", "t tiny2", "start")
    lab(cu + 0.45, 16.3, "12 V", "t tiny2", "end")
    lab(lel[0] - 0.35, lel[1] - 0.45, "LEL", "t tiny2 b", "start")
    s.dim(P(cu + 0.20, cv), P(cu + 0.20, POOL["v0"]), -4, f"{POOL['v0'] - cv:.2f}", size=2.5)
    s.dim(P(9.0, POOL["v1"]), P(9.0, POOL["v1"] + 2.0), 0, "2.00", size=2.5)
    s.dim(P(9.0, POOL["v1"] + 2.0), P(9.0, POOL["v1"] + 3.5), 0, "1.50", size=2.5)
    s.t(127, 18.5, "VOLUMES DE SÉCURITÉ ET CHEMINEMENTS  1/100", "t ct")
    band_north(s, 180 - U_ANG)
    # legend right of the plan
    items = [("box:z1", "Volume 1 : 2.00 m autour du bassin"), ("box:z2", "Volume 2 : de 2.00 à 3.50 m"), ("elec w3", "230 V pompe (3G2.5 sous TPC)"),
             ("selv w3", "TBTS : projecteurs 12 V, sécurités 24 V"), ("pe", "Liaison équipotentielle (LEL)"), ("box:red w3 fs", "Coffret CP sur la façade")]
    legend_lines(s, 238, 26, items, w=74, title="LÉGENDE")
    # ---- single-line diagram
    y0 = 186
    s.t(22, 177, "SCHÉMA UNIFILAIRE DE PRINCIPE (coffret CP)", "t cl", "start")
    s.rect(22, y0 - 4, 20, 8, "k w2 fs")
    s.t(32, y0 + 1, "TGBT villa", "t tiny2 b")
    s.line((42, y0), (50, y0), "k w2")
    s.circ(52, y0, 1.6, "k w2 fs")
    s.t(52, y0 - 3, "Q0", "t tiny2 b")
    s.t(52, y0 + 5.6, "sectionneur", "t tiny")
    s.t(52, y0 + 8.0, "cadenassable", "t tiny")
    s.line((53.6, y0), (60, y0), "k w2")
    s.rect(59, y0 - 3.5, 17, 7, "k w2 fs")
    s.t(67.5, y0 + 1, "DDR 30 mA", "t tiny2 b")
    s.t(67.5, y0 + 6.4, "type A", "t tiny")
    s.line((76, y0), (200, y0), "k w4")
    s.line((80, y0), (80, y0 + 6), "k w2")
    s.rect(77.5, y0 + 6, 5, 4, "k w2 fs")
    s.t(84, y0 + 9.5, "parafoudre", "t tiny", "start")
    feeders = [(96, "Q1 2P 10 A", "KM1", "M", "Pompe 0.75 kW", "fosse FT"),
               (122, "Q2 2P 2 A", "T1", "L", "P1-P3 12 V 30 W", "transfo 300 VA"),
               (148, "Q3 2P 2 A", "T2", "S", "TBTS 24 V CC", "CT + FL + AU → KM1"),
               (172, "Q4 2P 16 A", None, "PC", "Prise 16 A IP55", "façade, hors volumes"),
               (196, "Q5 2P 10 A", "T3", "L", "Éclairage jardin", "TBTS si < 3.50 m")]
    for x, q, dev, load, l1, l2 in feeders:
        s.line((x, y0), (x, y0 + 8), "k w2")
        _brk(s, x, y0 + 12, q)
        yy = y0 + 16
        if dev == "KM1":
            s.line((x, yy), (x, yy + 4), "k w2")
            s.line((x - 2, yy + 4), (x + 2, yy + 4), "k w3")
            s.line((x - 2, yy + 5.4), (x + 2, yy + 5.4), "k w3")
            s.t(x + 3, yy + 5.6, "KM1 2P", "t tiny2 b", "start")
            s.line((x, yy + 5.4), (x, yy + 14), "k w2")
        elif dev in ("T1", "T2", "T3"):
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
    s.pl([(148, y0 + 47), (148, y0 + 50), (100, y0 + 50), (100, y0 + 21.4), (98, y0 + 21.4)], "selv w2")
    s.t(124, y0 + 53.5, "chaîne de sécurité TBTS : ouverture de la trappe (CT), flotteur (FL) ou arrêt d'urgence (AU) → KM1 ouvre les 2 pôles", "t tiny", "middle")
    s.rect(22, y0 + 58, 30, 9, "k w2 fs")
    s.t(37, y0 + 63.5, "LEL + piquet", "t tiny2 b")
    s.line((52, y0 + 62.5), (200, y0 + 62.5), "pe")
    s.t(126, y0 + 66.5, "ferraillages bassin et fosse - cadre de trappe - lame inox - échelle - carcasse moteur - PE du coffret", "t tiny", "middle")
    # ---- safety concept (right)
    mz = [("Alimentation", "depuis le TGBT, coffret CP sur la façade à 5.00 m de l'eau, hors volumes."),
          ("Protection", "DDR 30 mA type A en tête de tous les circuits piscine, un disjoncteur par départ."),
          ("Isolement", "Q0 cadenassable pour la consignation ; KM1 coupe les 2 pôles de la pompe."),
          ("Fosse", "matériel 230 V accessible seulement par la trappe à clé ; son ouverture (CT) coupe la pompe."),
          ("TBTS", "projecteurs 12 V (T1) ; sécurités CT / FL en 24 V CC (T2) ; bornes à < 3.50 m en 12 V."),
          ("Séparation", "230 V et TBTS dans des gaines distinctes ; aucune boîte de jonction en volumes 0 et 1."),
          ("Liaisons", "LEL reliant toutes les masses et éléments conducteurs du bassin et de la fosse."),
          ("Cheminement", "TPC sous dallage, grillage avertisseur ; entrée en fosse par presse-étoupe en partie haute."),
          ("Pompe", "jamais immergée : fosse sèche, drainée (SF), flotteur FL ; IPX5 et norme pompe à vérifier.")]
    s.t(212, 177, "MESURES RETENUES", "t cl", "start")
    for i, (a_, b_) in enumerate(mz):
        yy = 183 + i * 8.6
        s.t(212, yy, a_, "t tiny2 b", "start")
        words, line, lines = b_.split(" "), "", []
        for w_ in words:
            if len(line) + len(w_) > 54:
                lines.append(line)
                line = w_
            else:
                line = (line + " " + w_).strip()
        lines.append(line)
        for j, l_ in enumerate(lines[:2]):
            s.t(232, yy + j * 3.5, l_, "t tiny", "start", size=2.3)
    s.rect(212, 262, 99, 22, "red w3 fs")
    s.t(214.5, 267.5, "CONFORMITÉ : NON VÉRIFIÉE", "t tiny2 b red-t", "start")
    for i, l_ in enumerate(["Concept établi sur les principes de la NF C 15-100 section 702 /",
                            "CEI 60364-7-702. À faire valider puis réceptionner par un électricien",
                            "qualifié, avec les fiches des matériels réellement achetés."]):
        s.t(214.5, 272.5 + i * 3.8, l_, "t tiny", "start", size=2.35)
    frame(s, "VB-09")
    s.title = "VB-09 Sécurité électrique"
    return s


# ==========================================================================
# VB-10  Nomenclature des équipements
# ==========================================================================

def vb10():
    s = S("b10")
    lots, _ = B.dqe_b()
    it = {i[0]: i for _, _, _, items in lots for i in items}
    amt = lambda *codes: sum(it[c][4] * it[c][5] for c in codes)
    p = R["pipes_new"]
    rows = [
        ("P", "Pompe de filtration", "1", f"{PUMP_FLOW} m³/h à {PUMP['head']:.0f} mCE, VS, 230 V, IPX5, préfiltre, auto-amorçante", "Fosse FT, sur socle", "Circulation, vidange", amt("4.07"), "Panier PF chaque semaine ; joint du couvercle 1 fois/an"),
        ("F", "Filtre à cartouche + rechange", "1", f"{FILTER['area']:.1f} m² ({FILTER['area_ft2']} ft²), ≤ Ø0.40 × h 0.90, purgeur, manomètre", "Fosse FT", "Filtration", amt("4.08"), "Lavage au jet à +0.5 bar ; cartouche tous les 2 ans"),
        ("PG", "Grille anti-coincement", "1", f"800 × 600, fentes ≤ 8 mm, {R['v_grille']:.3f} m/s au passage", "Puisard, grand fond", "Aspiration de fond", amt("4.02"), "Contrôle de la grille et des vis à chaque vidange"),
        ("SK1-2", "Skimmers", "2", "grande meurtrière à sceller, panier + volet", "Voile NO", "Aspiration de surface", amt("4.01"), "Paniers 2 fois par semaine en saison"),
        ("VA...V3", "Nourrices et sélecteur", "1", "6 vannes 1/4 de tour PVC, raccords union, V3 cadenassable, étiquettes", "Fosse FT", "Positions A / B / A+B / C / E", amt("4.09"), "Manœuvrer chaque mois ; graisse silicone"),
        ("RA1-2", "Buses dissimulées", "2", f"orifice Ø25, axe {INLET_LEVEL:+.2f}, orientées vers PG", "Voile SE, sous la cascade", "Retour A1", amt("4.03"), "Contrôle de l'orientation au printemps"),
        ("CAS", "Mur de cascade + lame", "1", "1.80 × 0.40, lame 600 × 6 mm, chambre inox 316L", "Petit bain, côté allée", "Retour A2 architectural", amt("4.12"), "Détartrer la fente 2 fois par an"),
        ("TR", "Trappe à carreler", "1", "1 200 × 750, classe A15, à clé, vérins, joint", "Dallage NO", "Accès à la fosse", amt("4.10"), "Vérins et joint : contrôle annuel"),
        ("SF, VT", "Siphon, ventilation", "1", "siphon à clapet anti-retour, 2 manchons Ø100, procédure", "Fosse FT", "Drainage, aération", amt("4.11"), "Nettoyer le siphon au printemps"),
        ("B", "Borne de contrôle", "1", "CL, CV à ±0.00, RP, V4 3 voies, raccord rapide", "Jardin NO", "Rejet contrôlé", amt("4.13"), "Vérifier le casse-vide avant chaque rejet"),
        ("PVC", "Canalisations PVC PN16", f"{p['d63'] + p['d50']:.0f} ml", f"Ø63 ({p['d63']:.0f} ml) et Ø50 ({p['d50']:.0f} ml), collées, essai 24 h", "Tranchées", "Réseaux", amt("4.05", "4.06"), "-"),
        ("PEHD", "Conduite de rejet", f"{p['pehd']:.0f} ml", "PEHD Ø50", "Jardin NO", "Rejet", amt("4.14"), "-"),
        ("FC", "Fourreaux à collerette", "9", "bague hydrogonflante", "Traversées", "Étanchéité", amt("4.04"), "-"),
        ("CP", "Coffret piscine", "1", "Q0, parafoudre, DDR 30 mA A, Q1-Q5, KM1, horloge, T2 24 V", "Façade villa, 5.00 m", "Protection, commande", amt("5.02"), "Bouton test du DDR chaque mois"),
        ("T1", "Transformateur de sécurité", "1", "230 / 12 V, 300 VA", "Coffret CP", "Éclairage TBTS", amt("5.04"), "-"),
        ("P1-P3", "Projecteurs LED", "3", "12 V 30 W + niche + presse-étoupe", "Voile SO", "Éclairage du bassin", amt("5.03"), "Joint neuf à chaque ouverture"),
        ("FL, CT", "Sécurités de fosse", "1", "flotteur + contact de trappe en TBTS 24 V", "Fosse FT", "Coupure de la pompe", amt("5.06"), "Essai à chaque ouverture de la trappe"),
        ("LEL", "Liaison équipotentielle", "1", "ferraillages, trappe, lame, échelle, moteur, piquet de terre", "Bassin et fosse", "Sécurité électrique", amt("5.05"), "Contrôle de continuité 1 fois par an"),
        ("C1", "Câbles pompe et TBTS", f"{R['L']['cable']:.0f} ml", "U1000 R2V 3G2.5 + câble TBTS sous TPC Ø40", "Tranchée", "Alimentation", amt("5.01"), "-"),
        ("ECH", "Échelle inox 316L", "1", "4 marches", "Grand fond", "Sortie du bassin", amt("4.16"), "Serrage des fixations"),
        ("KIT", "Kit d'entretien", "1", "épuisette, balai, plaque d'aspiration skimmer, analyse", "Remise", "Entretien", amt("4.17"), "-"),
    ]
    tot = sum(r[6] for r in rows)
    trs = [(a, b_, c, d, e, f, money(g), h) for a, b_, c, d, e, f, g, h in rows]
    trs.append(("", "TOTAL ÉQUIPEMENTS (DH HT)", "", "prix unitaires du devis, lots 4 et 5", "", "", money(tot), ""))
    s.t(18, 18, "NOMENCLATURE DES ÉQUIPEMENTS - VARIANTE B (coûts estimés, DH HT, mêmes prix unitaires que le devis)", "t cl", "start")
    table(s, 18, 20, ("Rep.", "Composant", "Qté", "Spécification", "Emplacement", "Fonction", "Coût est.", "Entretien"), trs,
          (14, 38, 11, 76, 34, 34, 18, 70), rh=4.55, size=2.25, align="llrlllrl")
    # removed / kept
    orig, _ = M.dqe()
    io = {i[0]: i for _, _, _, items in orig for i in items}
    rem = [("2.06", "Local technique 2.40 × 2.00"), ("4.02", "Bondes de fond BF1-BF2"), ("4.03", "Buses R1-R4"), ("4.04", "Prise balai PB"),
           ("4.06", "Nourrices du local technique"), ("4.08", "Filtre à sable Ø600 + vanne 6 voies")]
    rr = [(c, t_, money(io[c][4] * io[c][5])) for c, t_ in rem]
    rr.append(("", "Total supprimé (DH HT)", money(sum(io[c][4] * io[c][5] for c, _ in rem))))
    y2 = 20 + 4.55 * (len(trs) + 1) + 9
    s.t(18, y2 - 2, "SUPPRIMÉS PAR RAPPORT À L'INDICE E", "t cl", "start")
    table(s, 18, y2, ("Art.", "Ouvrage", "Montant"), rr, (12, 70, 24), rh=4.4, size=2.3, align="llr")
    keep = ["Pompe : même débit, même prix (hauteur demandée 9 au lieu de 10 mCE).",
            "Skimmers SK1-SK2, projecteurs P1-P3, échelle : conservés à l'identique.",
            "Coffret : déplacé du local technique vers la façade, complété (KM1, TBTS 24 V).",
            "Ajoutés : puisard + grille, fosse et trappe, cascade, borne et circuit B.",
            "Comparaison complète des coûts et des quantités : dossier, § comparaison."]
    s.t(132, y2 - 2, "CONSERVÉS / AJOUTÉS", "t cl", "start")
    for i, n in enumerate(keep):
        s.t(132, y2 + 4 + i * 4.8, n, "t tiny2", "start")
    # cost comparison (same unit prices) and operating cost (same hypotheses)
    sp = B.scope_split()
    c = B.compare()
    oc = B.ops_costs()
    d = lambda a_, b_: f"{b_ - a_:+,.0f}".replace(",", " ")
    rows = [("Périmètre modifié (lots 1 à 5, articles concernés)", money(sp["orig"]), money(sp["new"]), d(sp["orig"], sp["new"])),
            ("  dont cascade, borne et PEHD (demandés, sans équivalent E)", "-", money(sp["added"]), ""),
            ("  à périmètre égal (sans ces ajouts)", money(sp["orig"]), money(sp["like"]), d(sp["orig"], sp["like"])),
            ("Total général HT du devis", money(c["total_orig"]), money(c["total_new"]), d(c["total_orig"], c["total_new"]))]
    y3 = y2 + 4.4 * 9 + 10
    s.t(18, y3 - 2, "INVESTISSEMENT - MÊME BASE DE PRIX (DH HT)", "t cl", "start")
    table(s, 18, y3, ("Poste", "Indice E", "Variante B", "Écart"), rows, (92, 24, 24, 22), rh=4.6, size=2.3, align="lrrr")
    orows = [(r[0], money(r[5]), money(r[6]), d(r[5], r[6])) for r in oc["rows"] if r[5] or r[6]]
    orows.append(("Total d'exploitation calculé (DH / an)", money(oc["tot_old"]), money(oc["tot_new"]), d(oc["tot_old"], oc["tot_new"])))
    s.t(186, y3 - 2, "EXPLOITATION - HYPOTHÈSES IDENTIQUES (DH / an)", "t cl", "start")
    table(s, 186, y3, ("Poste", "Indice E", "Var. B", "Écart"), orows, (60, 20, 20, 20), rh=4.6, size=2.3, align="lrrr")
    o = B.OPS
    hyp = [f"Hypothèses : {oc['hours']} h de filtration par an, {o['tariff']:.2f} DH/kWh, rendement global {R['eta']:.2f}, HMT moyennes {c['head_orig']:.2f} / {c['head_new']:.2f} mCE,",
           f"contre-lavage {o['backwash_m3']} m³ × {o['backwash_n']} par an, eau à {o['water_price']} DH/m³, sable {o['sand_price']} DH tous les {o['sand_years']} ans, cartouche {o['cartridge_price']} DH tous les {o['cartridge_years']} ans.",
           "La variante coûte plus cher à construire ; elle économise un local hors œuvre, des canalisations, l'eau de contre-lavage et un peu d'énergie."]
    for i, n in enumerate(hyp):
        s.t(18, y3 + 4.6 * 5 + 8 + i * 4.6, n, "t tiny2", "start")
    frame(s, "VB-10")
    s.title = "VB-10 Nomenclature"
    return s


SHEET_FUNCS = [vb01, vb02, vb03, vb04, vb05, vb06, vb07, vb08, vb09, vb10, SH.pl01, SH.pl02, SH.pl05]
