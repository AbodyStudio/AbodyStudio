"""Variante C - pompe immergée dans le puisard du grand fond (schéma du propriétaire).

Owner's layout: the pump lies horizontally in a pit at the deepest point of the pool, under a
breathable stainless cage flush with the floor; it sends the water either outside (tube 1, garden)
or to the cascade (tube 2, back to the pool).
Safety change: the owner's 1 HP 220 V borehole pump cannot be placed in the pool water (volume 0
allows only SELV, <= 12 V AC or 30 V DC). The pump in the pit is a 24 V DC submersible pump fed by a
safety source in the pool panel, outside the zones.

Author: AbodyStudio Limited - https://abodystudio.com/
"""
import math

import model as M
from model import LV, POOL, FINISH, WALL, SLAB, Q, FLOOR_DEEP
import variant_b as B
from variant_b import hw, kloss, vel, area, PIPE, G, RHO, SLOT, CASCADE, NE_A2, SE_A2, CASC_BACK, POST, COFFRET, plen, filt_loss, FILTER, OPS

SUBTITLE = "Variante C : pompe immergée dans le puisard"
Q_C = 9.0                # design flow (m3/h)
Q_GARDEN = 6.0
U_DC = 24.0              # SELV, ripple-free DC (<= 30 V allowed in volume 0)
ETA = 0.40               # wire-to-water efficiency of a small DC pump (hypothesis)
RHO_CU = 0.0225          # ohm.mm2/m, copper at service temperature
DROP_MAX = 0.05          # DC pump with speed controller, at the worst point (filter due for cleaning)

# pit at the deepest point, pool-local x from the NW wall, y from the SW wall
PIT = dict(x0=0.0, x1=0.50, y0=1.55, y1=3.45, depth=0.35)
PIT["floor"] = FLOOR_DEEP - PIT["depth"]
CAGE = dict(L=PIT["y1"] - PIT["y0"], W=PIT["x1"] - PIT["x0"], hole=0.008, pitch=0.012, plate=0.003)
CAGE["open_ratio"] = 0.9069 * (CAGE["hole"] / CAGE["pitch"]) ** 2          # 60 deg staggered holes
# 4" borehole-type pump (the owner's pump shape) at 24 V DC, lying horizontally along y:
# brass discharge head + 1-1/4" outlet at the SW end, stainless multi-stage pump end, perforated inlet between two
# brass rings, motor; proportions taken from the owner's photo; cooling sleeve over inlet + motor
PUMP_C = dict(D=0.10, head_L=0.06, stages_L=0.63, inlet_L=0.12, motor_L=0.69, outlet="1-1/4\"", outlet_id=0.0352,
              sleeve_D=0.15, cradle=0.05, y0=1.70, x=0.25, head=6.0, flow=Q_C, cable_s=6.0)
PUMP_C["L"] = PUMP_C["head_L"] + PUMP_C["stages_L"] + PUMP_C["inlet_L"] + PUMP_C["motor_L"]
PUMP_C["y_inlet"] = PUMP_C["y0"] + PUMP_C["head_L"] + PUMP_C["stages_L"]
PUMP_C["y_motor"] = PUMP_C["y_inlet"] + PUMP_C["inlet_L"]
PUMP_C["y1"] = PUMP_C["y0"] + PUMP_C["L"]
PUMP_C["sleeve"] = (PUMP_C["y_inlet"] - 0.02, PUMP_C["y1"] + 0.10)
PUMP_C["axis"] = PIT["floor"] + PUMP_C["cradle"] + PUMP_C["sleeve_D"] / 2
PUMP_C["top"] = PUMP_C["axis"] + PUMP_C["sleeve_D"] / 2
STUB_Z = PIT["floor"] + 0.12            # fixed stubs through the pit / NW wall
OUT_STUB_Y, SK_STUB_Y, CABLE_Y = 1.62, 3.38, 1.85     # the flat cable leaves the body near the head
B.PIPE[40] = PUMP_C["outlet_id"]

U0, V0 = POOL["u0"], POOL["v0"]
RV = dict(u=U0 - 1.10, v=V0 + 2.15, a=0.50, depth=0.45)    # valve box in the NW paving
RV["bottom"] = LV["deck_edge"] - RV["depth"]
AL = dict(u=U0 - 3.60, v=V0 + 2.75, top=0.40)                                      # SELV supply box on a post, outside volume 2
CAB = dict(u0=CASC_BACK, u1=CASC_BACK + 0.60, v0=V0 + CASCADE["y0"] + 0.30, v1=V0 + CASCADE["y1"] - 0.30,
           top=CASCADE["top"], bottom=-1.10)                                       # filter cabinet behind the cascade

ROUTES = dict(
    T0=[(U0 - FINISH - WALL - 0.10, V0 + OUT_STUB_Y), (RV["u"], V0 + OUT_STUB_Y), (RV["u"], RV["v"])],
    T2=[(RV["u"], RV["v"]), (RV["u"], NE_A2), (SE_A2, NE_A2), (SE_A2, (CAB["v0"] + CAB["v1"]) / 2), ((CAB["u0"] + CAB["u1"]) / 2, (CAB["v0"] + CAB["v1"]) / 2)],
    T1=[(RV["u"], RV["v"]), (POST["u"], RV["v"]), (POST["u"], POST["v"])],
    T1_out=[(POST["u"], POST["v"]), (POST["u"], M.SOAKAWAY["v"]), (M.SOAKAWAY["u"] + M.SOAKAWAY["r"], M.SOAKAWAY["v"])],
    SK=[(U0 - FINISH - WALL - 0.25, V0 + 1.25), (U0 - FINISH - WALL - 0.25, V0 + 3.75)],
    CABLE=[(COFFRET["u"], COFFRET["v"]), (COFFRET["u"], COFFRET["v"] + 0.50), (AL["u"], COFFRET["v"] + 0.50), (AL["u"], AL["v"])],
    DC=[(AL["u"], AL["v"]), (U0 - FINISH - WALL - 0.10, AL["v"]), (U0 - FINISH - WALL - 0.10, V0 + CABLE_Y)],
)


def lengths():
    rise = (-1.20) - STUB_Z
    return dict(
        hose=0.80,
        t0=plen(ROUTES["T0"]) + rise + 0.30,
        t2=plen(ROUTES["T2"]) + 0.30 + (SLOT["level"] - (-1.20)),
        t1=plen(ROUTES["T1"]) + (0.0 - (-1.20)) + 0.30,
        t1_out=plen(ROUTES["T1_out"]) + 1.0,
        sk=2 * ((LV["water"] - 0.30) - STUB_Z) + plen(ROUTES["SK"]) + 0.6,
        cable=plen(ROUTES["CABLE"]) + 2 * 0.60,
        conduit=plen(ROUTES["DC"]) + (-1.00 - STUB_Z) + 0.60,
        pump_cable=plen(ROUTES["DC"]) + (-1.00 - STUB_Z) + 0.60 + (AL["top"] + 1.00) + 1.00,
    )


L = lengths()


def tdh(mode="2", q=Q_C, state="avg"):
    rows = []
    rows.append(("Entrée : cage + crépine à diaphragme (équilibrée avec les skimmers)", skimmer_branch(SK_SHARE * q)))
    rows.append((f"Sortie {PUMP_C['outlet']} + flexible ({L['hose']:.2f} m) + raccord rapide + coude", hw(q, 40, L["hose"]) + kloss(0.5 + 0.9, q, 40)))
    rows.append((f"Tube T0 Ø63 ({L['t0']:.2f} m) + 3 coudes, puisard → regard RV", hw(q, 63, L["t0"]) + kloss(2.7, q, 63)))
    rows.append(("Vanne 3 voies V-C du regard RV", kloss(2.0, q, 63)))
    if mode == "2":
        rows.append((f"Tube 2 Ø63 ({L['t2']:.2f} m) + 6 coudes, RV → coffre de la cascade", hw(q, 63, L["t2"]) + kloss(5.4, q, 63)))
        rows.append((f"Filtre à cartouche {FILTER['area']:.1f} m² ({'moyenne' if state == 'avg' else 'au seuil' if state == 'dirty' else 'propre'}) + 2 vannes", filt_loss(FILTER, q, state) + kloss(0.4, q, 63)))
        v_slot = q / 3600 / (SLOT["width"] * SLOT["gap"])
        rows.append(("Chambre de répartition + lame 600 × 6 mm", kloss(1.5, q, 63) + v_slot ** 2 / (2 * G)))
        rows.append((f"Hauteur statique : lame à {SLOT['level'] - LV['water']:.2f} m au-dessus de l'eau", SLOT["level"] - LV["water"]))
    else:
        rows.append((f"Tube 1 Ø50 jusqu'à la borne ({L['t1']:.2f} m) + clapet + 4 coudes", hw(q, 50, L["t1"]) + kloss(2.0 + 3.6, q, 50)))
        rows.append(("Point haut du casse-vide (±0,00) au-dessus de l'eau", 0.0 - LV["water"]))
    return rows, sum(v for _, v in rows)


SK_SHARE = 0.30          # target share of the flow taken by the skimmers


def skimmer_branch(qs):
    """Loss in the skimmer branch at qs (m3/h): basket + Ø50 line + elbows + quick coupling."""
    return 0.10 * (qs / 3.0) ** 2 + hw(qs, 50, L["sk"] / 2) + kloss(0.5 + 4 * 0.9 + 0.5, qs, 50)


def orifice():
    """Diaphragm on the bottom intake so that the skimmers take SK_SHARE of the flow."""
    qb = (1 - SK_SHARE) * Q_C / 3600
    dh = skimmer_branch(SK_SHARE * Q_C)
    cd = 0.62
    a_o = qb / (cd * math.sqrt(2 * G * dh))
    return dict(dh=dh, d=math.sqrt(4 * a_o / math.pi), qb=qb * 3600)


def calc():
    r = {}
    r["L"] = L
    r["turnover"] = Q["water_vol"] / Q_C
    r["tdh_2"] = tdh("2")
    r["tdh_2_dirty"] = tdh("2", state="dirty")[1]
    r["tdh_2_clean"] = tdh("2", state="clean")[1]
    r["tdh_1"] = tdh("1", q=Q_GARDEN)
    r["orifice"] = orifice()
    ga = CAGE["L"] * CAGE["W"]
    r["cage_open"] = ga * CAGE["open_ratio"]
    r["v_cage"] = Q_C / 3600 / r["cage_open"]
    r["v_cage_all"] = Q_C / 3600 / r["cage_open"]
    r["unblockable"] = max(CAGE["L"], CAGE["W"]) >= B.UNBLOCKABLE[1] and min(CAGE["L"], CAGE["W"]) >= B.UNBLOCKABLE[0]
    r["v_t0"] = vel(Q_C, 63)
    r["v_hose"] = vel(Q_C, 40)
    r["v_sleeve"] = Q_C / 3600 / (math.pi / 4 * (PUMP_C["sleeve_D"] ** 2 - PUMP_C["D"] ** 2))
    r["v_t1"] = vel(Q_GARDEN, 50)
    r["slot_q_per_m"] = Q_C / 3.6 / SLOT["width"]
    r["sheet_ok"] = Q_C >= B.Q_SHEET_MIN
    h = r["tdh_2"][1]
    r["p_hyd"] = RHO * G * Q_C / 3600 * h
    r["p1"] = r["p_hyd"] / ETA
    r["p1_dirty"] = RHO * G * Q_C / 3600 * r["tdh_2_dirty"] / ETA
    r["i_dc"] = r["p1_dirty"] / U_DC
    # DC cable: the pump's own cable runs in the conduit from the pit to the supply box AL
    s_min = 2 * L["pump_cable"] * r["i_dc"] * RHO_CU / (DROP_MAX * U_DC)
    s = next(x for x in (2.5, 4, 6, 10, 16) if x >= s_min)
    drop = 2 * L["pump_cable"] * r["i_dc"] * RHO_CU / s
    i_avg = r["p1"] / U_DC
    r["cable"] = dict(s_min=s_min, s=s, drop=drop, drop_pct=drop / U_DC * 100, drop_avg_pct=2 * L["pump_cable"] * i_avg * RHO_CU / s / U_DC * 100, i_avg=i_avg)
    PUMP_C["head"] = math.ceil(r["tdh_2_dirty"])
    PUMP_C["cable_s"] = s
    r["drain_h"] = Q["water_vol"] / Q_GARDEN
    # quantities
    pl, pw, pd = CAGE["L"] + 0.40, CAGE["W"] + 0.40, PIT["depth"] + 0.20
    r["c_pit"] = pl * pw * pd - CAGE["L"] * CAGE["W"] * PIT["depth"]
    r["c_cab"] = 2 * ((CAB["u1"] - CAB["u0"]) + (CAB["v1"] - CAB["v0"])) * (CAB["top"] - CAB["bottom"]) * 0.12 + (CAB["u1"] - CAB["u0"]) * (CAB["v1"] - CAB["v0"]) * 0.10
    r["pit_surf"] = CAGE["L"] * CAGE["W"] + 2 * (CAGE["L"] + CAGE["W"]) * PIT["depth"]
    r["trench"] = 0.4 * 0.6 * (plen(ROUTES["T2"]) + plen(ROUTES["T1"]) + plen(ROUTES["T1_out"]) + plen(ROUTES["CABLE"]) + plen(ROUTES["DC"])) + 1.0
    r["pipes"] = dict(d63=L["t0"] + L["t2"], d50=L["sk"] + L["t1"] + L["hose"], pehd=L["t1_out"])
    return r


R = calc()

ITEMS = [   # code, designation, unit, qty, unit price (DH HT) - same price basis as the estimate
    ("1.05", "Fouilles en tranchée (tubes 1 et 2, skimmers, câble) et surcreusement du puisard", "m³", round(R["trench"], 1), 70),
    ("1.09", "Drain périphérique PVC Ø100 perforé + géotextile, raccordé au puits perdu (indice E)", "ml", round(M.Q["perim_out"] + 14), 90),
    ("2.06", f"Caisson du puisard {CAGE['L'] + 0.40:.2f} × {CAGE['W'] + 0.40:.2f} × {PIT['depth'] + 0.20:.2f} hors tout et coffre du filtre : béton B25 + hydrofuge", "m³", round(R["c_pit"] + R["c_cab"], 2), 1700),
    ("2.07", "Acier HA FeE500 : caisson du puisard, coffre du filtre, noyau du mur de cascade", "kg", 80, 14),
    ("3.09", "Puisard : enduit hydrofuge + membrane ciment flexible 2 couches (continuité avec le bassin)", "m²", round(R["pit_surf"], 1), 190),
    ("4.01", "Skimmers grande meurtrière (les deux de l'indice E), raccordés au puisard", "U", 2, 1100),
    ("4.02", f"Cage inox 316L perforée {CAGE['L'] * 1000:.0f} × {CAGE['W'] * 1000:.0f} en 2 panneaux (tôle 3 mm, trous Ø8), cadre scellé, vis inviolables", "U", 1, 5200),
    ("4.03", f"Pompe de forage 4\" immergée TBTS {U_DC:.0f} V CC, longueur {PUMP_C['L']:.2f} m (moteur sans balais + contrôleur), {Q_C:.0f} m³/h à {PUMP_C['head']:.0f} mCE, inox, pose horizontale admise, câble 2 × {PUMP_C['cable_s']:g} mm² de {math.ceil(L['pump_cable'])} m", "U", 1, 9500),
    ("4.04", "Kit de pose : chemise de refroidissement Ø150, berceau inox, embout à 2 entrées + diaphragme, 2 flexibles, 2 raccords rapides inox, anneaux de levage", "Ft", 1, 2800),
    ("4.05", "Fourreaux à collerette + bagues hydrogonflantes (sortie puisard, skimmers, fourreau câble, cascade)", "U", 6, 250),
    ("4.06", "Canalisations PVC pression PN16 Ø63 (T0, tube 2)", "ml", round(R["pipes"]["d63"]), 65),
    ("4.07", "Canalisations PVC pression PN16 Ø50 (skimmers, tube 1 jusqu'à la borne, flexible)", "ml", round(R["pipes"]["d50"]), 55),
    ("4.08", "Regard de vannes RV 0.50 × 0.50 à carreler : vanne 3 voies V-C, vanne d'isolement, purge, étiquettes", "Ft", 1, 2600),
    ("4.09", "Coffre du filtre dans le mur de cascade : parement, couvercle pierre verrouillable, fond drainant", "Ft", 1, 3500),
    ("4.10", f"Filtre à cartouche {FILTER['area']:.1f} m², manomètre, purgeur + cartouche de rechange", "U", 1, 7500),
    ("4.11", "Mur de cascade : noyau BA, parement et chapeau pierre, lame inox 600 mm avec chambre (tube 2)", "Ft", 1, 7500),
    ("4.12", "Borne de contrôle du tube 1 : clapet, casse-vide au point haut, robinet de prélèvement, raccord rapide", "Ft", 1, 2800),
    ("4.13", "Conduite PEHD Ø50 vers le verger / puits perdu", "ml", round(R["pipes"]["pehd"]), 45),
    ("4.14", "Essai de mise en pression des canalisations 24 h", "Ft", 1, 400),
    ("5.01", "Câble 230 V U1000 R2V 3G2,5 coffret → boîtier AL, sous TPC Ø63 + grillage avertisseur", "ml", round(L["cable"]), 80),
    ("5.02", "Coffret piscine en façade (hors volumes) : sectionneur cadenassable, DDR 30 mA type A, disjoncteurs, horloge, parafoudre", "Ft", 1, 4200),
    ("5.03", f"Alimentation de sécurité 230 V / {U_DC:.0f} V CC 500 W dans le boîtier AL (transformateur de sécurité NF EN 61558-2-6) + commande", "U", 1, 2800),
    ("5.04", f"Boîtier AL IP65 sur poteau à {U0 - AL['u']:.2f} m du bassin (hors volumes) + fourreau Ø40 noyé jusqu'au puisard", "Ft", 1, 1600),
    ("5.06", "Transformateur de sécurité 12 V 300 VA pour les projecteurs P1-P3", "U", 1, 1100),
    ("5.05", "Liaison équipotentielle : ferraillages, cage, lame inox, échelle + piquet de terre", "Ft", 1, 1300),
]


def total_items():
    return sum(q * pu for _, _, _, q, pu in ITEMS)


def compare():
    sp = B.scope_split()
    b_rows = B.scope_compare()[1]
    c_total = total_items()
    c_added = sum(q * pu for code, _, _, q, pu in ITEMS if code in ("4.11", "4.12", "4.13"))
    hours = OPS["days_summer"] * OPS["h_summer"] + OPS["days_winter"] * OPS["h_winter"]
    e_c = R["p1"] * hours / 1000
    oc_b = B.ops_costs()
    ops_c = e_c * OPS["tariff"] + OPS["clean_m3"] * OPS["clean_n"] * OPS["water_price"] + OPS["cartridge_price"] / OPS["cartridge_years"]
    return dict(orig=sp["orig"], b=sp["new"], c=c_total, c_added=c_added, c_like=c_total - c_added, b_like=sp["like"],
                e_c=e_c, e_b=oc_b["rows"][0][3], ops_b=oc_b["tot_new"], ops_c=ops_c, ops_e=oc_b["tot_old"])


if __name__ == "__main__":
    print("lengths", {k: round(v, 2) for k, v in L.items()})
    for m in ("2", "1"):
        rows, t = R["tdh_" + m]
        print("mode", m, round(t, 2), [(n[:28], round(v, 2)) for n, v in rows])
    print("dirty", round(R["tdh_2_dirty"], 2), "clean", round(R["tdh_2_clean"], 2))
    print("orifice", {k: round(v, 4) for k, v in R["orifice"].items()})
    print("cage open", round(R["cage_open"], 3), "v", round(R["v_cage"], 4), "unblock", R["unblockable"])
    print("p_hyd", round(R["p_hyd"]), "p1", round(R["p1"]), "p1 dirty", round(R["p1_dirty"]), "I", round(R["i_dc"], 1))
    print("cable", R["cable"], "pump cable L", round(L["pump_cable"], 2))
    print("pump", PUMP_C, "pit", PIT)
    print("total C", total_items(), compare())
