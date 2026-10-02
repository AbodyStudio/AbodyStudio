"""Site data, design parameters and computed quantities.

Author: AbodyStudio Limited - https://abodystudio.com/
Every dimension of the plan set is derived from this file, so a change here
(and a new version number) regenerates drawings, quantities and estimate.
"""
import math

VERSION = "1.3.0"
INDICE = "D"
DATE = "02/10/2026"

AUTHOR = {
    "name": "AbodyStudio Limited",
    "web": "abodystudio.com",
    "url": "https://abodystudio.com/",
    "email": "Support@abodystudio.com",
    "whatsapp": "+212 663 033 383",
}

CONTRACTOR = {
    "name": "ABOUDI BTP Group",
    "form": "SARL au capital de 100 000 MAD",
    "address": "Bd Moulay Ismail, Résidence Volubilis, Bloc C, 1er étage, N° 53 - Tanger-Médina",
    "tribunal": "Tanger",
    "rc": "168595",
    "ice": "003823697000094",
    "activity": "Construction tous corps d'état (TCE), bâtiment et travaux publics (BTP)",
    "manager": "Mohamed EL MRABET",
    "phones": "+212 717 783 570 / +212 663 033 383",
    "emails": "contact@aboudibtp.com / aboudibtpgroup@gmail.com",
}

PROJECT = {
    "title_fr": "Construction d'une piscine et aménagement des abords",
    "title_en": "Pool construction and garden layout",
    "province": "Province de Tanger-Assilah",
    "commune": "Commune Sahel Chamali",
    "lieu": "Douar Ghanem",
    "terrain": "Gharsa Foquiya",
    "surface": 1551,
    "topo": "Plan topographique 1/500 - Sahraoui Topo sarl",
}

# --------------------------------------------------------------------------
# Survey: parcel boundary (Lambert Nord Maroc), from the topographic plan
# --------------------------------------------------------------------------
BORNES = [
    ("B1", 444635.44, 535118.44), ("B2", 444656.08, 535098.12),
    ("B3", 444651.13, 535089.43), ("B4", 444618.71, 535065.08),
    ("B5", 444615.17, 535065.79), ("B6", 444612.30, 535067.07),
    ("B7", 444608.24, 535070.62), ("B8", 444601.20, 535078.40),
    ("B9", 444598.04, 535080.77), ("B10", 444596.87, 535083.96),
    ("B11", 444599.84, 535084.34),
]

# Local axes aligned with the house: u runs along the facade (NW -> SE,
# bearing 134.6 deg, parallel to boundary B1-B2), v runs from the road
# towards the pool (bearing 44.6 deg). Origin at B8.
BEARING_U = 134.6
_T = math.radians(BEARING_U)
EU = (math.sin(_T), math.cos(_T))
EV = (math.sin(_T - math.pi / 2), math.cos(_T - math.pi / 2))
ORIGIN = (444601.20, 535078.40)


def to_uv(X, Y):
    dx, dy = X - ORIGIN[0], Y - ORIGIN[1]
    return (dx * EU[0] + dy * EU[1], dx * EV[0] + dy * EV[1])


def to_xy(u, v):
    return (ORIGIN[0] + u * EU[0] + v * EV[0], ORIGIN[1] + u * EU[1] + v * EV[1])


BORNES_UV = [(n, *to_uv(x, y)) for n, x, y in BORNES]


def polygon_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


PARCEL_AREA = polygon_area([(x, y) for _, x, y in BORNES])


def edge_lengths():
    out = []
    for i in range(len(BORNES)):
        a, b = BORNES[i], BORNES[(i + 1) % len(BORNES)]
        out.append((a[0], b[0], math.hypot(b[1] - a[1], b[2] - a[2])))
    return out


def _uvb(name):
    for n, u, v in BORNES_UV:
        if n == name:
            return (u, v)


def u_nw(v):
    """u of the NW boundary (B11-B1) at depth v."""
    (u1, v1), (u2, v2) = _uvb("B11"), _uvb("B1")
    return u1 + (v - v1) * (u2 - u1) / (v2 - v1)


def u_se(v):
    """u of the SE boundary (B4-B3) at depth v."""
    (u1, v1), (u2, v2) = _uvb("B4"), _uvb("B3")
    return u1 + (v - v1) * (u2 - u1) / (v2 - v1)


_B4, _B3 = _uvb("B4"), _uvb("B3")
_SE_LEN = math.hypot(_B3[0] - _B4[0], _B3[1] - _B4[1])
SE_DIR = ((_B3[0] - _B4[0]) / _SE_LEN, (_B3[1] - _B4[1]) / _SE_LEN)
SE_IN = (-SE_DIR[1], SE_DIR[0])          # inward normal (towards NW)
DRIVE_W = 3.00


def u_drive(v):
    """u of the inner edge of the 3.00 m driveway (parallel to SE fence)."""
    p = (_B4[0] + SE_IN[0] * DRIVE_W, _B4[1] + SE_IN[1] * DRIVE_W)
    return p[0] + (v - p[1]) * SE_DIR[0] / SE_DIR[1]


# --------------------------------------------------------------------------
# Design (owner's dimensions) - local u/v metres
# --------------------------------------------------------------------------
FACADE = 12.00            # owner's dimension
HOUSE_DEPTH = 10.00       # assumed - to verify on site
STAIR_W = 1.00            # existing roof stair along the SE wall (to verify)
STAIR_LEN = 5.20
BACK_GARDEN = 3.00        # owner's dimension (minimum, to the road boundary)
SE_STRIP_MIN = 1.00       # owner's 1.00 - 1.50 m planted strip next to the driveway
FRONT_GARDEN_W = 2.00     # owner's dimensions, from the facade towards the pool
DECK_W = 2.50
WALK = 0.50               # pool walkway = 50 x 50 coping
POOL_LEN = 10.00
POOL_WID = 5.00
SIDE_GARDEN_NW = 8.00


def _road_v(u):
    """v of the road-side boundary (B4..B11 polyline) at abscissa u."""
    pts = [(u_, v_) for n, u_, v_ in BORNES_UV if n in ("B4", "B5", "B6", "B7", "B8", "B9")]
    pts.sort()
    for (u1, v1), (u2, v2) in zip(pts, pts[1:]):
        if u1 <= u <= u2:
            return v1 + (u - u1) * (v2 - v1) / (u2 - u1)
    return pts[0][1] if u < pts[0][0] else pts[-1][1]


def _ceil05(x):
    return math.ceil(x * 20 - 1e-9) / 20


def _floor05(x):
    return math.floor(x * 20 + 1e-9) / 20


def _place_house():
    # u first (driveway constraint at the back end of the stair), then v.
    v0 = 3.40
    for _ in range(5):
        v1 = v0 + HOUSE_DEPTH
        stair_back = v1 - STAIR_LEN
        u1 = _floor05(u_drive(stair_back) - SE_STRIP_MIN - STAIR_W)
        u0 = u1 - FACADE
        worst = max(_road_v(u0 + k * FACADE / 40) for k in range(41))
        v0 = _ceil05(worst + BACK_GARDEN)
    return u0, u1, v0, v0 + HOUSE_DEPTH


_hu0, _hu1, _hv0, _hv1 = _place_house()
HOUSE = dict(u0=_hu0, u1=_hu1, v0=_hv0, v1=_hv1)
STAIR = dict(u0=_hu1, u1=_hu1 + STAIR_W, v0=_hv1 - STAIR_LEN, v1=_hv1)
_uc = (_hu0 + _hu1) / 2
AWNING = dict(uc=_hu0 + 4.80, r=2.40, depth=1.80)     # existing curved slab overhang (dashed)
FRONT_GARDEN = (_hv1, _hv1 + FRONT_GARDEN_W)
DECK = (FRONT_GARDEN[1], FRONT_GARDEN[1] + DECK_W)
POOL = dict(u0=_uc - POOL_LEN / 2, u1=_uc + POOL_LEN / 2,
            v0=DECK[1] + WALK, v1=DECK[1] + WALK + POOL_WID)
_pvc = (POOL["v0"] + POOL["v1"]) / 2
TECH = dict(u0=POOL["u0"] - 3.55 - 2.40, u1=POOL["u0"] - 3.55, v0=_pvc - 1.00, v1=_pvc + 1.00)
TECH_WALL = 0.20
SOAKAWAY = dict(u=TECH["u0"] + 1.60, v=POOL["v1"] + 7.80, r=0.60)
NW_GARDEN_EDGE = POOL["u0"] - SIDE_GARDEN_NW
CHICKEN_V = (FRONT_GARDEN[0] + 0.60, POOL["v1"] + 6.60)
SHOWER = dict(u=HOUSE["u1"] + 0.90, v=DECK[0] + 1.25, s=1.20)
FENCE_OFFSET = 1.00                   # optional safety fence, outside the walkway
# access stair on the left (SE) end of the facade, from the villa (+-0.00) down to the deck (-0.75),
# its landing joins the foot of the existing roof stair
POOL_STAIR = dict(u0=_hu1 - 1.40, u1=_hu1, landing=0.80, n=5, rise=0.15, tread=0.30)

POOL_L = POOL_LEN
POOL_W = POOL_WID

# Levels (m) - reference +-0.00 = finished ground floor of the existing villa
LV = dict(
    rdc=0.00,
    tn=-0.80,             # natural ground at the pool (to confirm on site)
    coping=-0.70,         # top of coping = pool reference
    deck_edge=-0.71,
    deck_low=-0.75,       # deck falls 1.5 % towards the channel drain
    channel=-0.76,
    water=-0.85,
    beam_top=-0.77,
    roof=3.20,
    parapet=3.80,
)
WATER_SHALLOW = 0.55     # owner's request: children's zone
WATER_BREAK = 1.20       # slope break (ligne de rupture de pente)
WATER_DEEP = 1.80
FLOOR_SHALLOW = LV["water"] - WATER_SHALLOW     # -1.40
FLOOR_BREAK = LV["water"] - WATER_BREAK         # -2.05
FLOOR_DEEP = LV["water"] - WATER_DEEP           # -2.65
FINISH = 0.03            # render + membrane + mosaic
SLAB = 0.20
BLIND = 0.08
HERISSON = 0.20
WALL = 0.20
COVER = 0.04

# floor profile along the pool, x from the NW (deep) wall
DEEP_FLAT = 1.20         # deep flat 0.00 - 1.20 (main drains)
BREAK_X = 3.00           # steep slope 1.20 - 3.00 (1:3), gentle slope 3.00 - 7.50 (1:7)
SLOPE_END = 7.50         # shallow flat 7.50 - 10.00 at 0.55
PROFILE = [(0.0, FLOOR_DEEP), (DEEP_FLAT, FLOOR_DEEP), (BREAK_X, FLOOR_BREAK), (SLOPE_END, FLOOR_SHALLOW), (POOL_LEN, FLOOR_SHALLOW)]

STEP = dict(x0=POOL_LEN - 2 * 0.35, width=2.00, n_tread=2, tread=0.35, rise=(LV["coping"] - FLOOR_SHALLOW) / 3)
PUMP_FLOW = 12           # m3/h at 10 mCE
FILTER_D = 0.60          # m
CHLORINATOR = 60         # m3 class
LIGHT_DEPTH = 0.45       # light axis below water level

# fittings, pool-local coordinates: x from NW wall (0..10), y from SW wall (0..5)
FITTINGS = {
    "skimmers": [(0.0, 1.25), (0.0, 3.75)],
    "drains": [(0.60, 2.00), (0.60, 3.00)],
    "returns": [(10.0, 3.50), (8.25, 5.0), (5.00, 5.0), (1.75, 5.0)],
    "vacuum": [(0.0, 2.50)],
    "lights": [(1.75, 0.0), (4.25, 0.0), (6.50, 0.0)],
    "ladder": [(0.80, 0.0)],
}


def floor_depth(x):
    """Finished floor level (m, relative to +-0.00) at distance x from NW wall."""
    for (x1, z1), (x2, z2) in zip(PROFILE, PROFILE[1:]):
        if x1 <= x <= x2:
            return z1 + (x - x1) / (x2 - x1) * (z2 - z1)
    return FLOOR_SHALLOW if x > PROFILE[-1][0] else FLOOR_DEEP


def avg_floor():
    n = 400
    return sum(floor_depth(POOL_L * (i + 0.5) / n) for i in range(n)) / n


SLOPE_GENTLE = (FLOOR_SHALLOW - FLOOR_BREAK) / (SLOPE_END - BREAK_X) * 100
SLOPE_STEEP = (FLOOR_BREAK - FLOOR_DEEP) / (BREAK_X - DEEP_FLAT) * 100
SLOPE_PCT = SLOPE_GENTLE

# --------------------------------------------------------------------------
# Quantities
# --------------------------------------------------------------------------
HA = {6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888}


def quantities():
    q = {}
    L, W = POOL_L, POOL_W
    Lr, Wr = L + 2 * FINISH, W + 2 * FINISH
    Le, We = Lr + 2 * WALL, Wr + 2 * WALL
    q["Lr"], q["Wr"], q["Le"], q["We"] = Lr, Wr, Le, We
    fa = avg_floor()
    q["avg_floor"] = fa

    # water
    avg_depth = LV["water"] - fa
    steps_profile = STEP["tread"] * sum(STEP["rise"] * k for k in range(1, STEP["n_tread"] + 1))
    q["steps_vol"] = steps_profile * STEP["width"]
    q["water_area"] = L * W
    q["water_vol"] = L * W * avg_depth - q["steps_vol"]
    q["avg_water_depth"] = avg_depth

    # earthworks
    bottom_off = FINISH + SLAB + BLIND + HERISSON
    exc_depth = LV["tn"] - (fa - bottom_off)
    q["exc_depth_avg"] = exc_depth
    q["exc_depth_max"] = LV["tn"] - (FLOOR_DEEP - bottom_off)
    base = (Le + 1.0) * (We + 1.0)
    batter = 0.5 * exc_depth            # 1 horizontal : 2 vertical
    top = (Le + 1.0 + 2 * batter) * (We + 1.0 + 2 * batter)
    mid = (Le + 1.0 + batter) * (We + 1.0 + batter)
    q["exc_pool"] = exc_depth / 6 * (base + 4 * mid + top)
    q["exc_base"] = base
    q["exc_top"] = (Le + 1.0 + 2 * batter, We + 1.0 + 2 * batter)
    q["topsoil_area"] = top
    tech_ext = (TECH["u1"] - TECH["u0"] + 1.0) * (TECH["v1"] - TECH["v0"] + 1.0 + 0.9)
    q["exc_trench"] = tech_ext * 1.0 + 0.4 * 0.6 * 60
    q["herisson"] = base * HERISSON + (TECH["u1"] - TECH["u0"]) * (TECH["v1"] - TECH["v0"]) * 0.15
    q["blinding"] = (Le + 0.2) * (We + 0.2) * BLIND + 0.5
    q["footprint"] = Le * We
    shell_below_tn = Le * We * (LV["tn"] - (fa - FINISH - SLAB))
    void = q["exc_pool"] - base * HERISSON - Le * We * BLIND - shell_below_tn
    perim_out = 2 * (Le + We)
    q["perim_out"] = perim_out
    q["fill_gravel"] = perim_out * 0.40 * (exc_depth - HERISSON - BLIND - 0.10)
    q["fill_site"] = max(void - q["fill_gravel"], 0)
    q["spoil"] = (q["exc_pool"] + q["exc_trench"] - q["fill_site"]) * 1.25

    # concrete
    q["c_slab"] = Le * We * SLAB
    Lc, Wc = Lr + WALL, Wr + WALL
    h_deep = LV["beam_top"] - (FLOOR_DEEP - FINISH)
    h_shal = LV["beam_top"] - (FLOOR_SHALLOW - FINISH)
    h_long = LV["beam_top"] - (fa - FINISH)
    q["h_deep"], q["h_shal"], q["h_long"] = h_deep, h_shal, h_long
    wall_area = 2 * Lc * h_long + Wc * (h_deep + h_shal)
    q["wall_area"] = wall_area
    q["c_walls"] = wall_area * WALL
    q["c_steps"] = q["steps_vol"]
    q["c_total"] = q["c_slab"] + q["c_walls"] + q["c_steps"]

    # finishes
    walls_in = 2 * L * ((LV["coping"] - 0.05) - fa) + W * (((LV["coping"] - 0.05) - FLOOR_DEEP) + ((LV["coping"] - 0.05) - FLOOR_SHALLOW))
    steps_extra = 1.45
    q["surf_in"] = L * W + walls_in + steps_extra
    q["mosaic"] = q["surf_in"] * 1.08
    q["fillets"] = 2 * (L + W) + 4 * 1.5 + 6
    q["coping_ml"] = 2 * (L + W) + 4 * WALK
    q["coping_pcs"] = int(round(q["coping_ml"] / 0.5))
    q["waterstop"] = 2 * (Lr + Wr) + 4 * WALL

    # deck & garden
    q["deck"] = (HOUSE["u1"] - HOUSE["u0"]) * (DECK[1] - DECK[0]) + SHOWER["s"] ** 2
    q["channel"] = HOUSE["u1"] - HOUSE["u0"]

    # rebar schedule
    rb = []

    def bar(pos, desc, d, n, length, shape):
        kg = n * length * HA[d]
        rb.append(dict(pos=pos, desc=desc, d=d, n=n, L=length, shape=shape, kg=kg))

    nl = int(We / 0.15) + 1
    nt = int(Le / 0.15) + 1
    ll = Le - 0.08 + 0.50
    lt = We - 0.08 + 0.50
    bar(1, "Radier - nappe inf., sens long, e=15", 10, nl, ll, "U")
    bar(2, "Radier - nappe inf., sens transv., e=15", 10, nt, lt, "U")
    bar(3, "Radier - nappe sup., sens long, e=15", 10, nl, ll, "U")
    bar(4, "Radier - nappe sup., sens transv., e=15", 10, nt, lt, "U")
    bar(5, "Chaises de calage, 4 u/m²", 8, int(Le * We * 4), 0.60, "Z")
    n_in = int(2 * (Lr + Wr) / 0.15)
    n_out = int(2 * (Le + We) / 0.15)
    lv = 0.45 + (h_long + SLAB - 0.09) + 0.15
    bar(6, "Voiles - verticales en L ancrées au radier, face eau, e=15", 12, n_in, lv, "L")
    bar(7, "Voiles - verticales en L ancrées au radier, face terre, e=15", 12, n_out, lv, "L")
    rows = (h_long - 0.25) / 0.20
    perim_c = 2 * (Lc + Wc)
    bar(8, "Voiles - horizontales 2 faces, e=20 (recouvrement 50 Ø)", 10, int(round(2 * rows)), perim_c * 1.10, "-")
    bar(9, "Équerres d'angle 2 faces, e=20", 10, int(4 * 2 * round(h_long / 0.20)), 1.20, "L")
    bar(10, "Chaînage - filants 4 HA12", 12, 4, perim_c + 1.20 + 4 * 0.60, "-")
    bar(11, "Chaînage - cadres 12×17, e=15", 6, int(perim_c / 0.15), 0.72, "O")
    bar(12, "Escalier - nappe suivant profil, e=20", 10, 2 * 11, 2.80, "S")
    bar(13, "Renforts autour des pièces à sceller", 12, 10 * 4, 1.00, "-")
    q["rebar"] = rb
    q["steel"] = sum(r["kg"] for r in rb)

    # structural sanity checks (principle, to be validated by a licensed BET)
    h = h_deep
    m_ser = 10 * h ** 3 / 6                      # kN.m/m, full pool, no backfill
    as_ = math.pi * 0.006 ** 2 / 0.15            # HA12 e=15, m2 per m
    z = 0.9 * (WALL - COVER - 0.006)
    q["m_ser"] = m_ser
    q["sigma_s"] = m_ser / (as_ * z) / 1000      # MPa
    weight = q["c_total"] * 25 + q["coping_ml"] * 0.5 * 0.05 * 22
    q["shell_weight"] = weight
    q["float_head"] = weight / (Le * We * 10)

    # hydraulics
    q["turnover_h"] = 4.5
    q["flow"] = q["water_vol"] / q["turnover_h"]
    q["filter_d"] = FILTER_D
    q["filter_rate"] = PUMP_FLOW / (math.pi * FILTER_D ** 2 / 4)
    return q


Q = quantities()

# --------------------------------------------------------------------------
# Estimate (DQE) - unit prices in MAD HT, indicative 2026 Tanger region,
# editable in the page. Quantities come from Q.
# --------------------------------------------------------------------------


def r1(x):
    return round(x, 1)


def dqe():
    q = Q
    lots = [
        ("1", "Travaux préparatoires et terrassements", "Site preparation and earthworks", [
            ("1.01", "Installation de chantier, relevé de l'existant et implantation", "Site set-up, survey of existing house, setting out", "Ft", 1, 3000),
            ("1.02", "Vidange (eau vers le verger) et dépose de la piscine hors-sol et du coffret de filtration", "Drain and remove the above-ground pool and filter box", "Ft", 1, 1000),
            ("1.03", "Décapage de la terre végétale ép. 20 cm, mise en dépôt pour réemploi", "Strip 20 cm topsoil, stockpile for reuse", "m²", round(q["topsoil_area"]), 12),
            ("1.04", "Fouilles en pleine masse du bassin à l'engin, talus 1/2", "Machine excavation of the pool, 1:2 batter", "m³", r1(q["exc_pool"]), 45),
            ("1.05", "Fouilles en tranchée et local technique (canalisations, drains, câbles)", "Trenches and equipment-room dig", "m³", r1(q["exc_trench"]), 70),
            ("1.06", "Évacuation des déblais excédentaires (foisonnement 1.25)", "Haul away surplus spoil (bulking 1.25)", "m³", r1(q["spoil"]), 35),
            ("1.07", "Hérisson en pierres sèches 40/80 ép. 20 cm, compacté", "Dry stone sub-base 20 cm", "m³", r1(q["herisson"]), 250),
            ("1.08", "Béton de propreté dosé à 150 kg/m³ ép. 8 cm", "Blinding concrete 8 cm", "m³", r1(q["blinding"]), 800),
            ("1.09", "Drain périphérique PVC Ø100 perforé + géotextile, raccordé au puits perdu", "Perimeter drain Ø100 to soakaway", "ml", round(q["perim_out"] + 14), 90),
            ("1.10", "Remblai drainant gravier 15/25 contre parois, ép. 40 cm", "Drainage gravel against walls, 40 cm", "m³", r1(q["fill_gravel"]), 250),
            ("1.11", "Remblai en matériaux sélectionnés du site, compacté par couches de 20 cm", "Selected site fill, compacted in 20 cm layers", "m³", r1(q["fill_site"]), 60),
        ]),
        ("2", "Gros œuvre - béton armé", "Structure - reinforced concrete", [
            ("2.01", "Béton B25 (350 kg/m³ CPJ 45) + hydrofuge de masse pour radier, vibré", "B25 concrete + waterproofing admixture, floor slab", "m³", r1(q["c_slab"]), 1150),
            ("2.02", "Béton B25 + hydrofuge pour voiles et chaînage, coffrage compris", "B25 concrete, walls and ring beam incl. formwork", "m³", r1(q["c_walls"]), 1700),
            ("2.03", "Béton B25 pour escalier intérieur du bassin", "B25 concrete, pool steps", "m³", r1(q["c_steps"]), 1600),
            ("2.04", "Acier HA FeE500 façonné et posé (voir nomenclature)", "Rebar FeE500 cut, bent and fixed", "kg", round(q["steel"], -1), 14),
            ("2.05", "Joint hydrogonflant de reprise radier / voiles", "Swelling waterstop at slab/wall joint", "ml", r1(q["waterstop"]), 90),
            ("2.06", "Local technique semi-enterré 2.40 × 2.00 m (fondation, murs, dalle, enduits, porte, ventilation, siphon)", "Semi-buried equipment room, complete", "Ft", 1, 18000),
        ]),
        ("3", "Étanchéité et revêtements du bassin", "Waterproofing and pool finishes", [
            ("3.01", "Enduit hydrofuge 2 couches (gobetis + corps d'enduit) ép. 15 à 20 mm", "Two-coat waterproof render", "m²", r1(q["surf_in"]), 70),
            ("3.02", "Gorges (chanfreins 5 × 5 cm) aux angles rentrants", "Fillets at internal corners", "ml", r1(q["fillets"]), 35),
            ("3.03", "Étanchéité ciment flexible bi-composant 2 couches + bandes d'angle et colliers", "Flexible cementitious membrane, 2 coats + tapes", "m²", r1(q["surf_in"]), 120),
            ("3.04", "Mosaïque pâte de verre 25 × 25 mm, colle C2TE S1, joint époxy", "Glass mosaic 25 mm, C2TE S1 adhesive, epoxy grout", "m²", r1(q["mosaic"]), 300),
            ("3.05", "Margelles 50 × 50 pierre reconstituée, nez arrondi, antidérapantes", "Coping 50 × 50 cast stone, bullnose, non-slip", "ml", r1(q["coping_ml"]), 380),
            ("3.06", "Marquage des profondeurs 0.55 / 1.20 / 1.80, ligne contrastée de rupture de pente et « Plongeon interdit »", "Depth markers, slope-break line, no-diving signs", "Ft", 1, 700),
        ]),
        ("4", "Hydraulique et filtration", "Hydraulics and filtration", [
            ("4.01", "Skimmer grande meurtrière à sceller (béton), volet + panier", "Wide-mouth skimmer for concrete", "U", 2, 1100),
            ("4.02", "Bonde de fond anti-vortex à sceller", "Anti-vortex main drain", "U", 2, 600),
            ("4.03", "Buse de refoulement orientable", "Adjustable return inlet", "U", 4, 180),
            ("4.04", "Prise balai", "Vacuum point", "U", 1, 180),
            ("4.05", "Canalisations PVC pression PN16 Ø50 / Ø63 collées, raccords compris", "PVC PN16 pipework Ø50/Ø63", "ml", 70, 55),
            ("4.06", "Nourrices aspiration / refoulement + vannes à boisseau sphérique", "Suction / return manifolds + ball valves", "Ft", 1, 2500),
            ("4.07", f"Pompe de filtration {PUMP_FLOW} m³/h à 10 mCE, vitesse variable, 230 V", "Variable-speed pump", "U", 1, 8500),
            ("4.08", f"Filtre à sable Ø{FILTER_D * 1000:.0f} + vanne 6 voies + manomètre + charge filtrante", "Sand filter + 6-way valve + media", "U", 1, 6000),
            ("4.09", "Essai de mise en pression des canalisations 24 h", "24 h pipe pressure test", "Ft", 1, 400),
            ("4.10", "Échelle inox 316L 4 marches (grand fond 1.80 m)", "Stainless 316L ladder, 4 steps", "U", 1, 3200),
            ("4.11", "Kit d'entretien (épuisette, balai aspirateur, manche, tuyau, trousse d'analyse)", "Maintenance kit", "Ft", 1, 1500),
        ]),
        ("5", "Électricité", "Electrical", [
            ("5.01", "Alimentation depuis le TGBT : câble U1000 R2V 3G6 mm² sous TPC Ø63 + grillage avertisseur", "Supply cable from house panel in duct", "ml", 18, 80),
            ("5.02", "Coffret piscine : interrupteur général, DDR 30 mA type A, disjoncteurs, contacteur, horloge, parafoudre", "Pool panel with 30 mA RCD, breakers, timer", "Ft", 1, 3800),
            ("5.03", "Projecteur LED 12 V 30 W + niche + presse-étoupe", "12 V 30 W LED pool light + niche", "U", 3, 1400),
            ("5.04", "Transformateur de sécurité 12 V 300 VA", "12 V 300 VA safety transformer", "U", 1, 1100),
            ("5.05", "Liaison équipotentielle (ferraillage, échelle, pièces métalliques) + piquet de terre", "Equipotential bonding + earth rod", "Ft", 1, 1000),
            ("5.06", "Éclairage extérieur : bornes et spots LED IP65, câblage compris", "Garden bollards and spots IP65", "U", 14, 380),
        ]),
        ("6", "Aménagements extérieurs", "Garden and external works", [
            ("6.01", "Plage solarium : forme BA ép. 10 cm (treillis soudé) + grès cérame antidérapant R11 60 × 60", "Lounger deck: 10 cm RC base + R11 porcelain 60 × 60", "m²", r1(q["deck"]), 320),
            ("6.02", "Caniveau à grille en pied de jardin, raccordé au puits perdu", "Slot drain along the planted strip", "ml", r1(q["channel"]), 280),
            ("6.03", "Escalier d'accès à la piscine côté gauche (SE) : palier ±0.00 + 5 marches 15 × 30, l = 1.40 m, BA revêtu antidérapant, main courante", "Access stair to the pool, left side", "Ft", 1, 5500),
            ("6.04", "Bordures de jardin en béton", "Concrete garden edging", "ml", 60, 60),
            ("6.05", "Terre végétale d'apport + engazonnement (semis)", "Topsoil + seeded lawn", "m²", 157, 35),
            ("6.06", "Massifs plantés (lavande, romarin, agapanthe, gaura) 3 u/m²", "Planted beds, 3 plants/m²", "m²", 25, 110),
            ("6.07", "Haie de cyprès Totem h 1.50 m le long de l'allée", "Cypress hedge along the driveway", "U", 12, 150),
            ("6.08", "Arrosage goutte-à-goutte programmable", "Programmable drip irrigation", "Ft", 1, 3000),
            ("6.09", "Douche extérieure solaire + dalle + raccordement", "Solar outdoor shower + pad", "Ft", 1, 2800),
            ("6.10", "Puits perdu Ø1.20 m prof. 2.50 m rempli de pierres + regard", "Soakaway Ø1.20 × 2.50 m", "Ft", 1, 3000),
            ("6.11", "Clôture du parc à poules, grillage h 1.50 m + portillon", "Chicken-run mesh fence 1.50 m + gate", "ml", 22, 80),
            ("6.12", "Reprise de l'allée en gravier existante (recharge, bordures)", "Regrade and top up the gravel driveway", "m²", 111, 30),
        ]),
        ("7", "Mise en eau et mise en service", "Filling and commissioning", [
            ("7.01", "Eau par camion-citerne : essai d'étanchéité + remplissage final", "Tanker water: leak test + final fill", "m³", round(2 * q["water_vol"]), 30),
            ("7.02", "Mise en service : produits, équilibrage de l'eau, formation du propriétaire", "Start-up chemicals, water balance, owner handover", "Ft", 1, 1800),
        ]),
    ]
    options = ("O", "Options (non comprises dans le total)", "Options (not in the total)", [
        ("OPT.1", f"Électrolyseur au sel {CHLORINATOR} m³ + régulation pH", "Salt chlorinator + pH control", "U", 1, 13500),
        ("OPT.2", "Pompe à chaleur 12 kW (saison prolongée)", "12 kW heat pump", "U", 1, 28000),
        ("OPT.3", "Clôture de sécurité amovible h 1.20 m + portillon auto-fermant", "Removable safety fence 1.20 m + self-closing gate", "ml", 36, 400),
        ("OPT.4", "Couverture de sécurité à barres", "Safety bar cover", "U", 1, 12000),
        ("OPT.5", "Panneaux photovoltaïques 2 kWc pour la filtration", "2 kWp solar PV for the pump", "Ft", 1, 22000),
    ])
    return lots, options


SHEETS = [
    ("PL-01", "Plan de masse", "Implantation sur le plan topographique", "1/250"),
    ("PL-02", "Plan d'aménagement des abords", "Piscine, plage, jardins, allée et poulailler", "1/100"),
    ("PL-03", "Plan du bassin - implantation des équipements", "Cotation du bassin et des pièces à sceller", "1/50"),
    ("PL-04", "Coupes A-A et B-B", "Coupe longitudinale et coupe villa - jardin - piscine", "1/50 - 1/100"),
    ("PL-05", "Détails béton armé et nomenclature des aciers", "Paroi, radier, chaînage, margelle", "1/20"),
    ("PL-06", "Réseaux, local technique et électricité", "Tracé des canalisations, local, synoptique, unifilaire", "1/100 - 1/25"),
]

if __name__ == "__main__":
    print("parcel area", round(PARCEL_AREA, 1))
    for n, u, v in BORNES_UV:
        print(n, round(u, 2), round(v, 2))
    for k, v in Q.items():
        if k != "rebar":
            print(k, round(v, 3) if isinstance(v, float) else v)
    for r in Q["rebar"]:
        print(r["pos"], r["d"], r["n"], round(r["L"], 2), round(r["kg"], 1), r["desc"])
    print("strip SE at house back", round(u_drive(HOUSE['v0']) - HOUSE['u1'], 2))
    print("strip SE at stair back", round(u_drive(STAIR['v0']) - STAIR['u1'], 2))
    print("strip SE at facade", round(u_drive(HOUSE['v1']) - STAIR['u1'], 2))
    print("pool SE end to drive", round(u_drive(POOL['v0']) - POOL['u1'], 2), round(u_drive(POOL['v1']) - POOL['u1'], 2))
    print("NW boundary from pool", round(POOL['u0'] - u_nw(POOL['v0']), 2))
    print("NE boundary from pool", round(52.55 - POOL['v1'], 2))
    print("house", HOUSE, "stair", STAIR)
    print("pool", POOL, "tech", TECH)
    print("back garden min", round(min(HOUSE['v0'] - _road_v(HOUSE['u0'] + k * 0.3) for k in range(41)), 2))
    print("chickens width", round(NW_GARDEN_EDGE - u_nw(POOL['v0']), 2))
    print("slope", round(SLOPE_PCT, 2))
    lots, opt = dqe()
    tot = 0
    for code, fr, en, items in lots:
        s = sum(i[4] * i[5] for i in items)
        tot += s
        print(code, fr, round(s))
    print("TOTAL HT", round(tot), "TTC", round(tot * 1.2))
