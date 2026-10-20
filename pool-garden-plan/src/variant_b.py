"""Variante B - piscine sans local technique : hydraulique intégrée au bassin.

Same pool as the original study (dimensions, levels, depth profile, structure);
the conventional technical room and pipework are replaced by an integrated
pump chamber at the deep end, one pump, a compact cartridge filter, a
three-way selector, a concealed cascade return and a controlled garden line.

Author: AbodyStudio Limited - https://abodystudio.com/
"""
import math

import model as M
from model import LV, POOL, POOL_L, POOL_W, FINISH, WALL, SLAB, Q, PUMP_FLOW, WATER_DEEP, FLOOR_DEEP, FLOOR_SHALLOW

VERSION = "2.0.0"
INDICE = "F"
SUBTITLE = "Variante B : sans local technique"

G = 9.81
RHO = 1000.0

# ---------------------------------------------------------------------------
# Equipment envelopes (typical catalogue sizes - adapt to the model purchased)
# ---------------------------------------------------------------------------
PUMP = dict(L=0.62, W=0.26, H=0.33, P2=0.55, P1=0.75, port=63, flow=PUMP_FLOW, head=9.0)
FILTER = dict(D=0.36, H=0.86, area=13.9, area_ft2=150, port=50,   # cartridge 13.9 m2 (150 ft2) - max envelope
              dp_clean=1.0, dp_rise=5.0)                         # mCE: clean loss at 12 m3/h, cleaning threshold rise
SAND = dict(D=0.60, dp_clean=2.0, dp_rise=5.0)                   # original sand filter + 6-way valve (same method)
GRILLE = dict(L=0.80, W=0.60, open_ratio=0.40, slot=8)             # anti-entrapment intake grille (mm slots)
SUMP_DEPTH = 0.40
UNBLOCKABLE = (0.457, 0.584)                                     # 18 x 23 in (ANSI/APSP-16 / VGB definition)
SLOT = dict(width=0.60, gap=0.006, level=LV["water"] + 0.40)     # cascade sheet outlet
CASCADE = dict(y0=2.60, y1=4.40, top=LV["coping"] + 0.60, thick=0.40)
INLETS_Y = [2.90, 4.10]                                          # concealed inlets in the SE wall, under the cascade
INLET_LEVEL = LV["water"] - 0.30
SKIMMERS_Y = [1.25, 3.75]                                        # both original skimmers kept (1 per 25 m2 of water)
SKIMMER_Y = SKIMMERS_Y[1]

# vault (dry pump chamber) - interior 1.10 (u) x 1.30 (v) x 1.00 high, shares the pool NW wall
V_IN_A, V_IN_B, V_IN_H = 1.10, 1.30, 1.00
V_WALL, V_BASE = 0.20, 0.20
_wall_out = POOL["u0"] - FINISH - WALL            # outer face of the pool NW wall (u)
_vc = (POOL["v0"] + POOL["v1"]) / 2
VAULT = dict(
    u_in1=_wall_out, u_in0=_wall_out - V_IN_A, u_out0=_wall_out - V_IN_A - V_WALL,
    v_in0=_vc - V_IN_B / 2, v_in1=_vc + V_IN_B / 2, v_out0=_vc - V_IN_B / 2 - V_WALL, v_out1=_vc + V_IN_B / 2 + V_WALL,
    floor=-0.80 - V_IN_H, top=-0.80, deck=-0.72,
)
VAULT["base_under"] = VAULT["floor"] - V_BASE
HATCH = dict(a0=0.05, a1=0.80, b0=0.05, b1=1.25)   # clear opening 0.75 x 1.20, vault-local (a from NW inner face, b from SW)
SUMP = dict(x0=0.0, x1=0.60, y0=2.10, y1=2.90)       # pool-local: x from NW wall, y from SW wall
POST = dict(u=3.40, v=22.90)                         # garden control post (borne de contrôle)

PIPE = {63: 0.0536, 50: 0.0426}   # PVC PN16 internal diameters (m)
SUMP_OUT = FLOOR_DEEP - SUMP_DEPTH + 0.10     # axis of the sump outlet (m)
Q_GARDEN = 6.0                                # throttled flow to the garden (m3/h)
SUMP_SHARE = 0.50                             # sump grille 50 %, each skimmer 25 %


def filt_loss(f, q=PUMP_FLOW, state="avg"):
    """Filter loss (mCE): clean value + half the cleaning threshold on average, full threshold when due."""
    k = {"clean": 0.0, "avg": 0.5, "dirty": 1.0}[state]
    return (f["dp_clean"] + k * f["dp_rise"]) * (q / PUMP_FLOW) ** 2


def area(d):
    return math.pi * d * d / 4


def vel(q_m3h, dn):
    return q_m3h / 3600 / area(PIPE[dn])


def hw(q_m3h, dn, length, c=150):
    """Hazen-Williams friction loss (m) for PVC."""
    qs = q_m3h / 3600
    return 10.67 * length * qs ** 1.852 / (c ** 1.852 * PIPE[dn] ** 4.87)


def kloss(k, q_m3h, dn):
    v = vel(q_m3h, dn)
    return k * v * v / (2 * G)


# ---------------------------------------------------------------------------
# Hydraulic calculation (design point and the three operating modes)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Layout inside the vault (vault-local a from the NW inner face towards the pool, b from the SW inner face)
# ---------------------------------------------------------------------------
VLAY = dict(
    filter=(0.30, 0.80),                     # centre
    pump=(0.23, 0.85, 0.18, 0.44),           # a0, a1 (prefilter end), b0, b1
    plinth=0.06,
    riser=(0.97, 0.31), skim_in=(0.97, 1.30), skim1_in=(0.97, 0.0), vs2=(0.97, 0.85), vs1=(0.97, 0.12),
    header_b=1.15, header_a=(0.20, 0.80),
    A1_out=(0.55, 1.30), A2_out=(0.75, 1.30), B_out=(0.0, 1.15),
    cable_in=(0.0, 0.15), vents=[(0.0, 0.45), (0.0, 0.85)], drain=(0.14, 0.50), float=(0.08, 0.59),
    z_suction=-1.45, z_A1=-1.45, z_A2=-1.30, z_B=-1.30,
)


def vu(a, b):
    """vault-local (a, b) -> site (u, v)"""
    return (VAULT["u_in0"] + a, VAULT["v_in0"] + b)


# trench axes (site u, v)
NE_A1, NE_A2 = POOL["v1"] + 0.50, POOL["v1"] + 0.38
SE_A1, SE_A2 = POOL["u1"] + 0.50, POOL["u1"] + 0.38
CASC_BACK = POOL["u1"] + CASCADE["thick"]
_e1, _e2 = vu(*VLAY["A1_out"]), vu(*VLAY["A2_out"])
_vo = VAULT["v_in1"] + V_WALL
ROUTES = dict(
    A1=[(_e1[0], _vo), (_e1[0], NE_A1), (SE_A1, NE_A1), (SE_A1, POOL["v0"] + INLETS_Y[0])],
    A1_stubs=[[(SE_A1, POOL["v0"] + y), (POOL["u1"], POOL["v0"] + y)] for y in INLETS_Y],
    A2=[(_e2[0], _vo), (_e2[0], NE_A2), (SE_A2, NE_A2), (SE_A2, POOL["v0"] + (CASCADE["y0"] + CASCADE["y1"]) / 2),
        (CASC_BACK - 0.08, POOL["v0"] + (CASCADE["y0"] + CASCADE["y1"]) / 2)],
    B=[(VAULT["u_out0"], VAULT["v_in0"] + VLAY["B_out"][1]), (POST["u"], VAULT["v_in0"] + VLAY["B_out"][1]), (POST["u"], POST["v"])],
    B_out=[(POST["u"], POST["v"]), (POST["u"], M.SOAKAWAY["v"]), (M.SOAKAWAY["u"] + M.SOAKAWAY["r"], M.SOAKAWAY["v"])],
    SK=[(POOL["u0"] - FINISH - WALL - 0.30, POOL["v0"] + SKIMMER_Y), (vu(*VLAY["skim_in"])[0], POOL["v0"] + SKIMMER_Y), vu(*VLAY["skim_in"])],
    SK1=[(POOL["u0"] - FINISH - WALL - 0.30, POOL["v0"] + SKIMMERS_Y[0]), (vu(*VLAY["skim1_in"])[0], POOL["v0"] + SKIMMERS_Y[0]), vu(*VLAY["skim1_in"])],
    CABLE=[(M.HOUSE["u0"] + 0.45, M.HOUSE["v1"]), (M.HOUSE["u0"] + 0.45, M.HOUSE["v1"] + 0.50), (4.10, M.HOUSE["v1"] + 0.50),
           (4.10, VAULT["v_in0"] + VLAY["cable_in"][1]), (VAULT["u_out0"], VAULT["v_in0"] + VLAY["cable_in"][1])],
)
COFFRET = dict(u=M.HOUSE["u0"] + 0.45, v=M.HOUSE["v1"], w=0.60)


def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def lengths():
    """Pipe runs measured on the routes drawn on VB-02 / VB-07 / VB-09 (m), verticals added."""
    inside = 0.40                                   # manifold to wall, inside the vault
    a1_main = plen(ROUTES["A1"]) + (INLETS_Y[1] - INLETS_Y[0]) * 0      # far inlet reached on the main line
    a1 = a1_main + sum(plen(s) for s in ROUTES["A1_stubs"]) + 2 * (INLET_LEVEL - VLAY["z_A1"]) + inside
    a2 = plen(ROUTES["A2"]) + (SLOT["level"] - 0.05 - VLAY["z_A2"]) + inside
    return dict(
        suction=0.45 + ((VAULT["floor"] + 0.15) - SUMP_OUT) + 0.40,
        skimmer=plen(ROUTES["SK"]) + plen(ROUTES["SK1"]) + 2 * 0.35,
        a1=a1, a2=a2,
        b_post=plen(ROUTES["B"]) + (0.0 - VLAY["z_B"]) + inside,
        b_out=plen(ROUTES["B_out"]) + 1.0,
        cable=plen(ROUTES["CABLE"]) + 2 * 0.60 + 1.0,
    )


def _common(q, state="avg", skimmer=True):
    """Suction + prefilter + filter + selector rows (shared by every mode)."""
    L = lengths()
    qs = SUMP_SHARE * q if skimmer else q   # share of the flow taken by the sump grille
    rows = [
        (f"Aspiration : grille + puisard + Ø63 ({nf_(L['suction'])} m) + 2 coudes + vanne VA",
         hw(qs, 63, L["suction"]) + kloss(0.5 + 1.8 + 0.15, qs, 63)),
        ("Préfiltre de la pompe (panier propre)", 0.30 * (q / PUMP_FLOW) ** 2),
        (f"Filtre à cartouche {nf_(FILTER['area'], 1)} m² ({'moyenne entre deux nettoyages' if state == 'avg' else 'au seuil de nettoyage' if state == 'dirty' else 'propre'})",
         filt_loss(FILTER, q, state)),
    ]
    return rows


def _branch_a1(q):
    L = lengths()
    v_in = (q / 2) / 3600 / area(0.025)
    return [(f"Circuit A1 Ø63 ({nf_(L['a1'])} m) + 7 coudes + vanne V1", hw(q, 63, L["a1"]) + kloss(6.3 + 1.15, q, 63)),
            ("2 buses dissimulées (orifice Ø25)", v_in ** 2 / (2 * G)),
            ("Hauteur statique (buses sous le plan d'eau)", 0.0)]


def _branch_a2(q):
    L = lengths()
    v_slot = q / 3600 / (SLOT["width"] * SLOT["gap"])
    return [(f"Circuit A2 Ø63 ({nf_(L['a2'])} m) + 8 coudes + vanne V2", hw(q, 63, L["a2"]) + kloss(7.2 + 1.15, q, 63)),
            ("Chambre de répartition + lame 600 × 6 mm", kloss(1.5, q, 63) + v_slot ** 2 / (2 * G)),
            (f"Hauteur statique : lame à {nf_(SLOT['level'] - LV['water'])} m au-dessus de l'eau", SLOT["level"] - LV["water"])]


def tdh(mode, q=PUMP_FLOW, state="avg"):
    """Total dynamic head (mCE) with the itemised losses, for selector position A, B, AB or C."""
    L = lengths()
    if mode == "C":
        rows = _common(q, state, skimmer=False)
        rows.append((f"Circuit B Ø50 jusqu'à la borne ({nf_(L['b_post'])} m) + 4 coudes + clapet + vanne V3",
                     hw(q, 50, L["b_post"]) + kloss(3.6 + 2.0 + 1.15, q, 50)))
        rows.append(("Point haut du casse-vide (±0,00) au-dessus du plan d'eau", 0.0 - LV["water"]))
        return rows, sum(v for _, v in rows)
    rows = _common(q, state)
    if mode == "A":
        rows += _branch_a1(q)
    elif mode == "B":
        rows += _branch_a2(q)
    else:   # A + B together: V1 throttled so that the cascade keeps a continuous sheet
        qb = q_ab_cascade(q)
        rows += [(f"{n} - {nf_(qb, 1)} m³/h (V1 réglée)" if i == 0 else n, v) for i, (n, v) in enumerate(_branch_a2(qb))]
    return rows, sum(v for _, v in rows)


def split_ab(q=PUMP_FLOW):
    """Flow (m3/h) through A1 when V1 and V2 are both fully open."""
    lo, hi = 0.0, q
    for _ in range(60):
        qa = (lo + hi) / 2
        ha = sum(v for _, v in _branch_a1(qa))
        hb = sum(v for _, v in _branch_a2(q - qa))
        lo, hi = (qa, hi) if ha < hb else (lo, qa)
    return (lo + hi) / 2


SHEET_MIN = 3.1      # L/s per metre of sheet - usual minimum for an unbroken sheet (15 US gpm per foot)
Q_SHEET_MIN = SHEET_MIN * SLOT["width"] * 3.6     # m3/h for the 600 mm slot


def q_ab_cascade(q=PUMP_FLOW):
    """Flow kept in A2 (cascade) in position A+B: free split, raised to the sheet minimum by throttling V1."""
    return max(q - split_ab(q), Q_SHEET_MIN)


def nf_(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


def calc():
    r = {}
    L = lengths()
    r["L"] = L
    q = PUMP_FLOW
    r["turnover_h"] = Q["water_vol"] / q
    r["tdh_A"] = tdh("A")
    r["tdh_B"] = tdh("B")
    r["tdh_AB"] = tdh("AB")
    r["q_a_in_ab"] = PUMP_FLOW - q_ab_cascade()
    r["q_ab_free_b"] = PUMP_FLOW - split_ab()
    r["tdh_C"] = tdh("C", q=Q_GARDEN)
    r["design_head"] = max(r["tdh_A"][1], r["tdh_B"][1])
    r["head_dirty"] = max(tdh("A", state="dirty")[1], tdh("B", state="dirty")[1])
    r["head_clean"] = min(tdh("A", state="clean")[1], tdh("B", state="clean")[1])
    r["drain_hours"] = Q["water_vol"] / Q_GARDEN
    r["suction_lift_end"] = (VAULT["floor"] + 0.15) - SUMP_OUT
    r["v_suction"] = vel(SUMP_SHARE * q, 63)
    r["v_trunk"] = vel(q, 63)
    r["v_b"] = vel(Q_GARDEN, 50)
    r["v_header"] = vel(q, 63)
    r["v_skimmer"] = vel((1 - SUMP_SHARE) / 2 * q, 50)
    # intake grille
    ga = GRILLE["L"] * GRILLE["W"]
    r["grille_open"] = ga * GRILLE["open_ratio"]
    r["v_grille"] = (SUMP_SHARE * q) / 3600 / r["grille_open"]
    r["v_grille_all"] = q / 3600 / r["grille_open"]
    r["v_grille_half"] = q / 3600 / (r["grille_open"] / 2)
    r["unblockable"] = GRILLE["L"] >= UNBLOCKABLE[1] and GRILLE["W"] >= UNBLOCKABLE[0]
    # cascade slot
    r["slot_v"] = q / 3600 / (SLOT["width"] * SLOT["gap"])
    r["slot_q_per_m"] = q / 3.6 / SLOT["width"]     # L/s per m of sheet
    # filter
    r["filter_rate"] = q / FILTER["area"]
    # hydraulic and electrical power at the design point
    eta = 0.40
    r["eta"] = eta
    r["p_hyd"] = RHO * G * q / 3600 * r["design_head"]
    r["p1_est"] = r["p_hyd"] / eta
    # vault quantities
    vlt = VAULT
    ext_a = V_IN_A + V_WALL
    ext_b = V_IN_B + 2 * V_WALL
    r["vault_ext"] = (ext_a, ext_b)
    r["vault_area"] = ext_a * ext_b
    wall_h = vlt["top"] - vlt["base_under"]
    walls_len = ext_b + 2 * V_IN_A                       # NW wall + SW and NE walls (the pool wall is shared)
    r["c_vault"] = walls_len * wall_h * V_WALL + ext_a * ext_b * V_BASE + 0.30 * ext_b * 0.15
    # sump box under the slab edge (net extra concrete)
    s_l, s_w = (SUMP["x1"] - SUMP["x0"]) + 0.40, (SUMP["y1"] - SUMP["y0"]) + 0.40
    r["c_sump"] = s_l * s_w * (SUMP_DEPTH + 0.20) - (SUMP["x1"] - SUMP["x0"]) * (SUMP["y1"] - SUMP["y0"]) * SUMP_DEPTH
    r["c_cascade"] = (CASCADE["y1"] - CASCADE["y0"]) * (CASCADE["top"] - LV["beam_top"]) * 0.20
    # lean-concrete fill below the vault, down to the excavation (1:2 batter beyond 0.50 m working space)
    exc_bottom = FLOOR_DEEP - FINISH - SLAB - M.BLIND - M.HERISSON
    work_edge = _wall_out - 0.50
    fill = 0.0
    n = 60
    for i in range(n):
        u = vlt["u_out0"] + (i + 0.5) * ext_a / n
        bottom = exc_bottom if u >= work_edge else exc_bottom + (work_edge - u) * 2.0
        fill += max(vlt["base_under"] - bottom, 0) * ext_a / n
    r["lean_fill"] = fill * ext_b
    r["vault_wp_in"] = (2 * (V_IN_A + V_IN_B)) * V_IN_H + V_IN_A * V_IN_B
    r["vault_wp_out"] = walls_len * wall_h + ext_a * ext_b
    r["sump_surf"] = (SUMP["x1"] - SUMP["x0"]) * (SUMP["y1"] - SUMP["y0"]) + 2 * ((SUMP["x1"] - SUMP["x0"]) + (SUMP["y1"] - SUMP["y0"])) * SUMP_DEPTH
    # rebar for the variant elements (kg)
    w10 = M.HA[10]
    w12 = M.HA[12]
    r["rebar_b"] = [
        dict(pos=14, desc="Fosse - voiles 2 faces HA10 e=15 (V + H)", d=10, n=int(walls_len / 0.15) * 2 + int(wall_h / 0.15) * 2 * 3, L=round((wall_h + walls_len / 3) / 1.0, 2)),
        dict(pos=15, desc="Fosse - radier 2 nappes HA10 e=15", d=10, n=2 * (int(ext_a / 0.15) + 1 + int(ext_b / 0.15) + 1), L=round((ext_a + ext_b) / 2, 2)),
        dict(pos=16, desc="Fosse - attentes dans le voile du bassin HA10 e=15", d=10, n=2 * 2 * int(wall_h / 0.15), L=0.90),
        dict(pos=17, desc="Puisard - cadres et chevêtres HA12", d=12, n=8, L=1.60),
        dict(pos=18, desc="Mur de cascade - noyau HA10 e=20, 2 faces", d=10, n=2 * int((CASCADE["y1"] - CASCADE["y0"]) / 0.20) + 8, L=0.95),
    ]
    for b in r["rebar_b"]:
        b["kg"] = b["n"] * b["L"] * M.HA[b["d"]]
        b["shape"] = "-"
    r["steel_b"] = sum(b["kg"] for b in r["rebar_b"])
    # trench / excavation for the new networks (0.40 x 0.60)
    tr_len = L["a1"] - 2.0 + L["b_post"] + L["b_out"] + L["cable"]
    r["trench"] = 0.4 * 0.6 * tr_len + 1.0      # + local over-dig for the sump
    # original (v1.3.1) technical room quantities, for the comparison
    t = M.TECH
    tw, td = t["u1"] - t["u0"], t["v1"] - t["v0"]
    r["tech_room"] = dict(area=tw * td, concrete=tw * td * 0.15 * 2 + 2 * ((tw - 0.2) + (td - 0.2)) * 1.95 * 0.20,
                          exc=(tw + 1.0) * (td + 1.0 + 0.9) * 0.95)
    r["pipes_new"] = dict(d63=L["suction"] + L["a1"] + L["a2"], d50=L["skimmer"] + L["b_post"], pehd=L["b_out"])
    return r


R = calc()


# ---------------------------------------------------------------------------
# Estimate (DQE) - variant B, same unit-price basis as v1.3.1
# ---------------------------------------------------------------------------

def dqe_b():
    lots, options = M.dqe()
    out = []
    p = R["pipes_new"]
    for code, fr, en, items in lots:
        items = list(items)
        if code == "1":
            items = [it if it[0] != "1.05" else ("1.05", "Fouilles en tranchée (canalisations A1, A2, B, câble) et surcreusement du puisard", it[2], "m³", round(R["trench"], 1), it[5]) for it in items]
            items = [it if it[0] != "1.09" else (it[0], it[1], it[2], it[3], round(it[4] + 5), it[5]) for it in items]
            items.append(("1.12", "Gros béton de remplissage sous la fosse technique, dosé à 200 kg/m³", "Lean-concrete fill under the vault", "m³", round(R["lean_fill"], 1), 900))
        if code == "2":
            items = [it for it in items if it[0] != "2.06"]
            items.append(("2.06", "Fosse technique intégrée et puisard : béton B25 + hydrofuge (radier, voiles, linteau sous margelle, caisson du puisard)", "Integrated vault and sump concrete", "m³", round(R["c_vault"] + R["c_sump"], 2), 1700))
            items.append(("2.07", "Acier HA FeE500 pour fosse, puisard et noyau du mur de cascade (repères 14 à 18)", "Rebar for vault, sump and cascade core", "kg", round(R["steel_b"], -1), 14))
        if code == "3":
            items.append(("3.07", "Étanchéité de la fosse : revêtement cristallin 2 couches en face intérieure + bandes et colliers", "Vault internal crystalline waterproofing", "m²", round(R["vault_wp_in"], 1), 160))
            items.append(("3.08", "Étanchéité extérieure de la fosse (membrane bitumineuse + protection) et drain", "Vault external tanking", "m²", round(R["vault_wp_out"], 1), 140))
            items.append(("3.09", "Puisard : enduit hydrofuge + membrane ciment flexible 2 couches (continuité avec le bassin)", "Sump lining", "m²", round(R["sump_surf"], 1), 190))
        if code == "4":
            items = [
                ("4.01", "Skimmers grande meurtrière à sceller, côté grand fond (les deux de l'indice E conservés, raccordés à la fosse)", "Skimmers", "U", 2, 1100),
                ("4.02", "Grille d'aspiration de fond anti-coincement 800 × 600 mm, fentes ≤ 8 mm, cadre à sceller (puisard)", "Anti-entrapment sump grille", "U", 1, 3200),
                ("4.03", "Buses de refoulement dissimulées au pied de la cascade", "Concealed return inlets", "U", 2, 180),
                ("4.04", "Fourreaux à collerette + bagues hydrogonflantes pour traversées (puisard, skimmers, fosse, cascade)", "Puddle-flange sleeves", "U", 9, 250),
                ("4.05", "Canalisations PVC pression PN16 Ø63 collées (aspiration, circuits A1 et A2)", "PVC Ø63 pipework", "ml", round(p["d63"]), 65),
                ("4.06", "Canalisations PVC pression PN16 Ø50 (skimmer, circuit B jusqu'à la borne)", "PVC Ø50 pipework", "ml", round(p["d50"]), 55),
                ("4.07", f"Pompe de piscine {PUMP_FLOW} m³/h à {PUMP['head']:.0f} mCE, préfiltre intégré, vitesse variable, 230 V, IPX5, montée à sec dans la fosse", "Pool pump", "U", 1, 8500),
                ("4.08", f"Filtre à cartouche {FILTER['area']:.1f} m² ({FILTER['area_ft2']} ft²), purgeur + manomètre, enveloppe ≤ Ø0.40 × h 0.90 + cartouche de rechange", "Cartridge filter + spare", "U", 1, 7500),
                ("4.09", "Nourrices : aspiration 3 vannes (VA, VS1, VS2) + sélecteur 3 vannes (V1, V2, V3 cadenassable), raccords union, étiquetage", "Suction and selector manifolds", "Ft", 1, 2900),
                ("4.10", "Trappe de visite à carreler 1 200 × 750 mm, alu/inox, classe A15, verrouillable, vérins, joint", "Tile-insert lockable hatch", "U", 1, 4500),
                ("4.11", "Fosse : siphon de sol + clapet anti-retour vers le drain périphérique, 2 manchons de ventilation Ø100 avec grilles, procédure plastifiée sous la trappe", "Vault drain, ventilation, procedure", "Ft", 1, 1400),
                ("4.12", "Mur de cascade : noyau BA, parement et chapeau pierre, lame d'eau inox 600 mm avec chambre de répartition", "Cascade wall with slot outlet", "Ft", 1, 7500),
                ("4.13", "Borne de contrôle de rejet : borne maçonnée verrouillable, vanne 3 voies, robinet de prélèvement, casse-vide", "Garden discharge control post", "Ft", 1, 2800),
                ("4.14", "Conduite de rejet PEHD Ø50 vers verger / puits perdu", "PE discharge line", "ml", round(p["pehd"]), 45),
                ("4.15", "Essai de mise en pression des canalisations 24 h", "24 h pressure test", "Ft", 1, 400),
                ("4.16", "Échelle inox 316L 4 marches (grand fond 1.80 m)", "Ladder", "U", 1, 3200),
                ("4.17", "Kit d'entretien (épuisette, balai, manche, tuyau, trousse d'analyse, diffuseur flottant)", "Maintenance kit", "Ft", 1, 1600),
            ]
        if code == "5":
            items = [
                ("5.01", "Alimentation depuis le coffret : câble U1000 R2V 3G2,5 mm² + câble de commande TBTS sous TPC Ø40", "Supply and SELV control cables", "ml", round(R["L"]["cable"]), 80),
                ("5.02", "Coffret piscine en façade de villa (hors volumes) : sectionneur cadenassable, DDR 30 mA type A, disjoncteurs, contacteur, horloge, transformateur TBTS 24 V, parafoudre", "Pool panel on the villa wall", "Ft", 1, 4600),
                ("5.03", "Projecteur LED 12 V 30 W + niche + presse-étoupe", "12 V LED pool light", "U", 3, 1400),
                ("5.04", "Transformateur de sécurité 12 V 300 VA (dans le coffret)", "12 V safety transformer", "U", 1, 1100),
                ("5.05", "Liaison équipotentielle : ferraillages bassin et fosse, grille, cadre de trappe, échelle, moteur + piquet de terre", "Equipotential bonding", "Ft", 1, 1300),
                ("5.06", "Sécurités de la fosse : contact de trappe et flotteur anti-inondation en TBTS, coupant la pompe", "Hatch interlock and flood float", "Ft", 1, 900),
                ("5.07", "Éclairage extérieur : bornes et spots LED IP65, câblage compris ; à moins de 3.50 m du bassin en TBTS 12 V", "Garden lights", "U", 14, 380),
            ]
        if code == "6":
            items = [it for it in items]
        out.append((code, fr, en, items))
    opts = ("O", "Options (non comprises dans le total)", "Options", [
        ("OPT.1", "Électrolyseur au sel : déconseillé ici, l'eau salée ne doit pas aller au verger (circuit B)", "Salt chlorinator - not recommended", "U", 1, 13500),
        ("OPT.2", "Pompe à chaleur 12 kW (à poser en façade, hors volumes)", "Heat pump", "U", 1, 28000),
        ("OPT.3", "Clôture de sécurité amovible h 1.20 m + portillon auto-fermant", "Safety fence", "ml", 36, 400),
        ("OPT.4", "Couverture de sécurité à barres", "Safety bar cover", "U", 1, 12000),
        ("OPT.5", "Panneaux photovoltaïques 2 kWc pour la filtration", "Solar PV", "Ft", 1, 22000),
        ("OPT.6", "Robot nettoyeur électrique (alimentation TBTS, prise hors volumes)", "Robot cleaner", "U", 1, 7000),
    ])
    return out, opts


def totals(lots):
    return sum(it[4] * it[5] for _, _, _, items in lots for it in items)


# scope that differs between the two systems (same unit prices)
SCOPE_ORIG = ["1.05", "1.09", "2.06", "4.01", "4.02", "4.03", "4.04", "4.05", "4.06", "4.07", "4.08", "4.09", "5.01", "5.02", "5.04", "5.05"]


def scope_compare():
    orig, _ = M.dqe()
    new, _ = dqe_b()
    io = {it[0]: it for _, _, _, items in orig for it in items}
    inew = {it[0]: it for _, _, _, items in new for it in items}
    o_rows = [(k, io[k][1], io[k][3], io[k][4], io[k][5], io[k][4] * io[k][5]) for k in SCOPE_ORIG]
    n_keys = ["1.05", "1.09", "1.12", "2.06", "2.07", "3.07", "3.08", "3.09"] + [k for k in inew if k.startswith("4.") and k not in ("4.16", "4.17")] + ["5.01", "5.02", "5.04", "5.05", "5.06"]
    n_rows = [(k, inew[k][1], inew[k][3], inew[k][4], inew[k][5], inew[k][4] * inew[k][5]) for k in n_keys]
    return o_rows, n_rows


def energy(head, hours=None):
    if hours is None:
        hours = 184 * 10 + 181 * 3
    p1 = RHO * G * PUMP_FLOW / 3600 * head / R["eta"]
    return p1, p1 * hours / 1000, hours


def tdh_original():
    """Same method applied to the original v1.3.1 layout (tech room 3.55 m away, sand filter + 6-way valve)."""
    rows = []
    q = PUMP_FLOW
    rows.append(("Aspiration : 4 lignes Ø50 (6 à 9 m) + nourrice, débit partagé", hw(q / 3, 50, 8.0) + kloss(4.0, q / 3, 50)))
    rows.append(("Préfiltre de la pompe", 0.30))
    rows.append(("Filtre à sable Ø600 + vanne 6 voies (moyenne entre deux lavages)", filt_loss(SAND)))
    rows.append(("Nourrice de refoulement + vannes", kloss(1.5, q, 63)))
    rows.append(("Boucle de refoulement Ø63 (20 m) + 10 coudes", hw(q, 63, 20.0) + kloss(9.0, q, 63)))
    rows.append(("4 buses (débit partagé)", ((q / 4) / 3600 / area(0.025)) ** 2 / (2 * G)))
    return rows, sum(v for _, v in rows)


# ---------------------------------------------------------------------------
# Operating cost - same hypotheses for both systems (all visible on the page)
# ---------------------------------------------------------------------------
OPS = dict(
    days_summer=184, h_summer=10, days_winter=181, h_winter=3,   # filtration hours
    tariff=1.30,                     # MAD/kWh (ONEE residential band, hypothesis)
    water_price=30,                  # MAD/m3, tanker water (same unit price as item 7.01)
    backwash_m3=0.8, backwash_n=32,  # sand: 12 m3/h x 3 min backwash + 1 min rinse; weekly in season + monthly off season
    clean_m3=0.10, clean_n=8,        # cartridge: hose cleaning every 4 to 6 weeks
    cartridge_price=1500, cartridge_years=2,
    sand_price=800, sand_years=5,    # 100 kg of filter sand + labour
    backwash_min=15, clean_min=30,   # owner time per operation
)


def ops_costs():
    o = OPS
    hours = o["days_summer"] * o["h_summer"] + o["days_winter"] * o["h_winter"]
    _, h_orig = tdh_original()
    p_new = RHO * G * PUMP_FLOW / 3600 * R["design_head"] / R["eta"]
    p_old = RHO * G * PUMP_FLOW / 3600 * h_orig / R["eta"]
    rows = []
    e_new, e_old = p_new * hours / 1000, p_old * hours / 1000
    rows.append(("Énergie de filtration", f"{hours} h/an", e_old, e_new, "kWh/an", e_old * o["tariff"], e_new * o["tariff"]))
    w_old = o["backwash_m3"] * o["backwash_n"]
    w_new = o["clean_m3"] * o["clean_n"]
    rows.append(("Eau de lavage (contre-lavages / nettoyages)", "", w_old, w_new, "m³/an", w_old * o["water_price"], w_new * o["water_price"]))
    rows.append(("Média filtrant (sable / cartouche)", "", None, None, "", o["sand_price"] / o["sand_years"], o["cartridge_price"] / o["cartridge_years"]))
    t_old = o["backwash_n"] * o["backwash_min"] / 60
    t_new = o["clean_n"] * o["clean_min"] / 60
    rows.append(("Temps d'entretien du filtre", "", t_old, t_new, "h/an", 0.0, 0.0))
    tot_old = sum(r[5] for r in rows)
    tot_new = sum(r[6] for r in rows)
    return dict(hours=hours, p_new=p_new, p_old=p_old, rows=rows, tot_old=tot_old, tot_new=tot_new, h_orig=h_orig)


# items that exist only because the brief asks for them (architectural return + garden circuit)
ADDED = {"4.12": "Mur de cascade (retour architectural)", "4.13": "Borne de contrôle du rejet", "4.14": "Conduite PEHD vers le verger"}


def scope_split():
    o_rows, n_rows = scope_compare()
    so = sum(r[5] for r in o_rows)
    sn = sum(r[5] for r in n_rows)
    added = sum(r[5] for r in n_rows if r[0] in ADDED)
    cascade_steel = [b for b in R["rebar_b"] if b["pos"] == 18][0]["kg"] * 14
    added += cascade_steel
    return dict(orig=so, new=sn, added=added, like=sn - added, cascade_steel=cascade_steel)


def compare():
    """Key quantities of both systems, computed from the two models."""
    L = R["L"]
    _, h_orig = tdh_original()
    t = R["tech_room"]
    orig_lots, _ = M.dqe()
    new_lots, _ = dqe_b()
    io = {it[0]: it for _, _, _, items in orig_lots for it in items}
    inew = {it[0]: it for _, _, _, items in new_lots for it in items}
    return dict(
        pipes_orig=io["4.05"][4], pipes_new=R["pipes_new"]["d63"] + R["pipes_new"]["d50"], pehd=R["pipes_new"]["pehd"],
        exc_orig=io["1.05"][4], exc_new=inew["1.05"][4],
        conc_orig=t["concrete"], conc_new=R["c_vault"] + R["c_sump"], lean=R["lean_fill"],
        head_orig=h_orig, head_new=R["design_head"], footprint_orig=t["area"], footprint_new=R["vault_area"],
        total_orig=totals(orig_lots), total_new=totals(new_lots),
    )


if __name__ == "__main__":
    print("lengths", {k: round(v, 2) for k, v in R["L"].items()})
    for m in ("A", "B", "C"):
        rows, t = R["tdh_" + m]
        print("mode", m, round(t, 2), [(n[:30], round(v, 2)) for n, v in rows])
    o_rows, o_t = tdh_original()
    print("original TDH", round(o_t, 2))
    for k in ("v_suction", "v_trunk", "v_b", "v_skimmer", "grille_open", "v_grille", "v_grille_all", "v_grille_half", "slot_v", "slot_q_per_m", "filter_rate", "design_head", "p_hyd", "p1_est",
              "c_vault", "c_sump", "c_cascade", "lean_fill", "vault_wp_in", "vault_wp_out", "sump_surf", "steel_b", "trench", "vault_area"):
        print(k, round(R[k], 3))
    print("unblockable", R["unblockable"], "tech room", {k: round(v, 2) for k, v in R["tech_room"].items()}, "pipes", R["pipes_new"])
    print("energy new", [round(x, 1) for x in energy(R["design_head"])], "orig", [round(x, 1) for x in energy(o_t)])
    lots, _ = dqe_b()
    lo, _ = M.dqe()
    print("total new HT", round(totals(lots)), "orig HT", round(totals(lo)))
    o_rows, n_rows = scope_compare()
    print("scope orig", round(sum(r[5] for r in o_rows)), "scope new", round(sum(r[5] for r in n_rows)))
    print("split", {k: round(v) for k, v in scope_split().items()})
    oc = ops_costs()
    print("ops", round(oc["tot_old"]), round(oc["tot_new"]), [(r[0][:20], r[2], r[3], round(r[5]), round(r[6])) for r in oc["rows"]])
    print("AB", round(R["q_a_in_ab"], 2), round(R["tdh_AB"][1], 2), "dirty", round(R["head_dirty"], 2), "clean", round(R["head_clean"], 2), "lift", round(R["suction_lift_end"], 2))
    print({k: round(v, 2) for k, v in compare().items()})
