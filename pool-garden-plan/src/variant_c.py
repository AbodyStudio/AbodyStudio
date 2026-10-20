"""Variante C - pompe au puisard du grand fond, deux tubes (schéma du propriétaire).

Owner's brief: no technical room, no filter, nothing else - one pump and two tubes:
tube 1 takes the water out to the garden, tube 2 sends it to the cascade, from where it falls
back into the pool. The pump lies horizontally in a pit at the deepest point of the pool, under a
breathable stainless cage flush with the floor.

Safety change kept from v2.1.0: the owner's 1 HP 220 V borehole pump cannot be placed in the pool
water (volume 0 allows only SELV, <= 12 V AC or 30 V DC). The pump in the pit has the same shape
and length (4", 1.50 m) with a 24 V DC motor, fed by the AL box on a post outside the zones.
What remains besides the pump and the two tubes: the cage, a 0.40 x 0.40 valve box (tee + V1 + V2)
and the AL box (protection, 24 V safety supply, 12 V for the lights).

Author: AbodyStudio Limited - https://abodystudio.com/
"""
import math

import model as M
from model import LV, POOL, FINISH, WALL, SLAB, Q, FLOOR_DEEP, HA
import variant_b as B
from variant_b import hw, kloss, vel, area, PIPE, G, RHO, SLOT, CASCADE, NE_A2, SE_A2, CASC_BACK, COFFRET, plen, OPS

VERSION = "2.2.0"
INDICE = "H"
SUBTITLE = "Variante C : pompe au puisard, deux tubes"
Q_C = 9.0                # flow to the cascade (m3/h)
Q_GARDEN = 6.0           # flow to the garden, V1 partly closed (m3/h)
U_DC = 24.0              # SELV, ripple-free DC (<= 30 V allowed in volume 0)
ETA = 0.40               # wire-to-water efficiency of a small DC pump (hypothesis)
RHO_CU = 0.0225          # ohm.mm2/m, copper at service temperature
DROP_MAX = 0.05          # voltage drop limit at the rated point

# pit at the deepest point, pool-local x from the NW wall, y from the SW wall
PIT = dict(x0=0.0, x1=0.50, y0=1.55, y1=3.45, depth=0.35)
PIT["floor"] = FLOOR_DEEP - PIT["depth"]
CAGE = dict(L=PIT["y1"] - PIT["y0"], W=PIT["x1"] - PIT["x0"], hole=0.008, pitch=0.012, plate=0.003)
CAGE["open_ratio"] = 0.9069 * (CAGE["hole"] / CAGE["pitch"]) ** 2          # 60 deg staggered holes
# 4" borehole-type pump (the owner's pump shape) at 24 V DC, lying horizontally along y:
# brass discharge head + 1-1/4" outlet at the SW end, stainless multi-stage pump end, perforated inlet between two
# brass rings, motor; proportions taken from the owner's photo; cooling sleeve over inlet + motor
PUMP_C = dict(D=0.10, head_L=0.06, stages_L=0.63, inlet_L=0.12, motor_L=0.69, outlet="1-1/4\"", outlet_id=0.0352,
              sleeve_D=0.15, cradle=0.05, y0=1.70, x=0.25, head=3.0, flow=Q_C, cable_s=4.0)
PUMP_C["L"] = PUMP_C["head_L"] + PUMP_C["stages_L"] + PUMP_C["inlet_L"] + PUMP_C["motor_L"]
PUMP_C["y_inlet"] = PUMP_C["y0"] + PUMP_C["head_L"] + PUMP_C["stages_L"]
PUMP_C["y_motor"] = PUMP_C["y_inlet"] + PUMP_C["inlet_L"]
PUMP_C["y1"] = PUMP_C["y0"] + PUMP_C["L"]
PUMP_C["sleeve"] = (PUMP_C["y_inlet"] - 0.02, PUMP_C["y1"] + 0.10)
PUMP_C["axis"] = PIT["floor"] + PUMP_C["cradle"] + PUMP_C["sleeve_D"] / 2
PUMP_C["top"] = PUMP_C["axis"] + PUMP_C["sleeve_D"] / 2
STUB_Z = PIT["floor"] + 0.12            # fixed stubs through the pit / NW wall
OUT_STUB_Y, CABLE_Y = 1.62, 1.85        # T0 outlet; the flat cable leaves the body near the head
B.PIPE[40] = PUMP_C["outlet_id"]

U0, V0 = POOL["u0"], POOL["v0"]
WALL_OUT = U0 - FINISH - WALL
RV = dict(u=U0 - 1.10, v=V0 + OUT_STUB_Y, a=0.40, depth=0.55)    # small valve box (tee + V1 + V2), lid flush with the ground
RV["top"] = LV["deck_edge"]
RV["bottom"] = RV["top"] - RV["depth"]
RV["z_pipe"] = RV["top"] - 0.34          # T0, tee and tube 2 ; tube 1 leaves 0.12 lower
RV["z_t1"] = RV["z_pipe"] - 0.12
AL = dict(u=U0 - 3.60, v=V0 + 2.75, top=0.40, w=0.30, h=0.40)    # the only electrical box, on a post outside volume 2
OUTLET = dict(u=M.SOAKAWAY["u"] + M.SOAKAWAY["r"], v=M.SOAKAWAY["v"], z=-1.20)   # tube 1 ends in the soakaway (orchard)
T1_U = 3.40                             # tube 1 runs along the orchard edge

ROUTES = dict(
    T0=[(WALL_OUT - 0.10, V0 + OUT_STUB_Y), (RV["u"], V0 + OUT_STUB_Y)],
    T2=[(RV["u"], RV["v"]), (RV["u"], NE_A2), (SE_A2, NE_A2), (SE_A2, V0 + (CASCADE["y0"] + CASCADE["y1"]) / 2),
        (CASC_BACK - 0.08, V0 + (CASCADE["y0"] + CASCADE["y1"]) / 2)],
    T1=[(RV["u"], RV["v"]), (T1_U, RV["v"]), (T1_U, OUTLET["v"]), (OUTLET["u"], OUTLET["v"])],
    CABLE=[(COFFRET["u"], COFFRET["v"]), (COFFRET["u"], COFFRET["v"] + 0.50), (AL["u"], COFFRET["v"] + 0.50), (AL["u"], AL["v"])],
    DC=[(AL["u"], AL["v"]), (WALL_OUT - 0.10, AL["v"]), (WALL_OUT - 0.10, V0 + CABLE_Y)],
    LIGHT=[(AL["u"], AL["v"]), (AL["u"], V0 - 0.40), (U0 + M.FITTINGS["lights"][-1][0], V0 - 0.40)],
)


def lengths():
    rise_rv = RV["z_pipe"] - STUB_Z
    return dict(
        hose=0.80,
        t0=plen(ROUTES["T0"]) + rise_rv + 0.30,
        t2=plen(ROUTES["T2"]) + 0.30 + (SLOT["level"] - RV["z_pipe"]),
        t1=plen(ROUTES["T1"]) + abs(OUTLET["z"] - RV["z_pipe"]) + 0.30,
        cable=plen(ROUTES["CABLE"]) + 2 * 0.60,
        conduit=plen(ROUTES["DC"]) + (-1.00 - STUB_Z) + 0.60,
        pump_cable=plen(ROUTES["DC"]) + (-1.00 - STUB_Z) + 0.60 + (AL["top"] + 1.00) + 1.00,
        light=plen(ROUTES["LIGHT"]) + 3 * 0.60 + 2.0,
    )


L = lengths()


def entry_loss(q):
    """Cage (negligible) + cooling sleeve + inlet screen of the pump."""
    v_s = q / 3600 / (math.pi / 4 * (PUMP_C["sleeve_D"] ** 2 - PUMP_C["D"] ** 2))
    return 0.10 * (q / Q_C) ** 2 + 1.5 * v_s ** 2 / (2 * G)


def tdh(mode="2", q=None, level=None):
    """Total head (mCE). mode 2: cascade at Q_C; mode 1: garden at Q_GARDEN.
    level: pool water level for mode 1 (None = full pool; 'end' = pool almost empty, water at the pit floor)."""
    q = q or (Q_C if mode == "2" else Q_GARDEN)
    rows = [("Entrée : cage, chemise et crépine de la pompe", entry_loss(q)),
            (f"Sortie {PUMP_C['outlet']} + flexible ({L['hose']:.2f} m) + raccord rapide + coude", hw(q, 40, L["hose"]) + kloss(0.5 + 0.9, q, 40)),
            (f"Tube T0 Ø63 ({L['t0']:.2f} m) + 3 coudes, puisard → regard RV", hw(q, 63, L["t0"]) + kloss(2.7, q, 63))]
    if mode == "2":
        rows.append(("Té + vanne V2 du regard RV", kloss(1.5, q, 63)))
        rows.append((f"Tube 2 Ø63 ({L['t2']:.2f} m) + 6 coudes, RV → cascade", hw(q, 63, L["t2"]) + kloss(5.4, q, 63)))
        v_slot = q / 3600 / (SLOT["width"] * SLOT["gap"])
        rows.append(("Chambre de répartition + lame 600 × 6 mm", kloss(1.5, q, 63) + v_slot ** 2 / (2 * G)))
        rows.append((f"Hauteur statique : lame à {SLOT['level'] - LV['water']:.2f} m au-dessus de l'eau", SLOT["level"] - LV["water"]))
    else:
        rows.append(("Té + vanne V1 du regard RV (V1 ouverte)", kloss(1.5, q, 50)))
        rows.append((f"Tube 1 PEHD Ø50 ({L['t1']:.2f} m) + 4 coudes, RV → puits perdu", hw(q, 50, L["t1"]) + kloss(3.6, q, 50)))
        if level == "end":
            rows.append((f"Hauteur statique en fin de vidange : eau au fond du puisard ({PIT['floor']:+.2f}) → tube en RV ({RV['z_pipe']:+.2f})", RV["z_pipe"] - PIT["floor"]))
        else:
            rows.append((f"Niveau : sortie au puits perdu ({OUTLET['z']:+.2f}) sous le plan d'eau ({LV['water']:+.2f})", OUTLET["z"] - LV["water"]))
    return rows, sum(v for _, v in rows)


def calc():
    r = {}
    r["L"] = L
    r["turnover"] = Q["water_vol"] / Q_C
    r["tdh_2"] = tdh("2")
    r["tdh_1"] = tdh("1")
    r["tdh_1_end"] = tdh("1", level="end")
    ga = CAGE["L"] * CAGE["W"]
    r["cage_open"] = ga * CAGE["open_ratio"]
    r["v_cage"] = Q_C / 3600 / r["cage_open"]
    r["unblockable"] = max(CAGE["L"], CAGE["W"]) >= B.UNBLOCKABLE[1] and min(CAGE["L"], CAGE["W"]) >= B.UNBLOCKABLE[0]
    r["v_t0"] = vel(Q_C, 63)
    r["v_hose"] = vel(Q_C, 40)
    r["v_sleeve"] = Q_C / 3600 / (math.pi / 4 * (PUMP_C["sleeve_D"] ** 2 - PUMP_C["D"] ** 2))
    r["v_t1"] = vel(Q_GARDEN, 50)
    r["slot_q_per_m"] = Q_C / 3.6 / SLOT["width"]
    r["sheet_ok"] = Q_C >= B.Q_SHEET_MIN
    # pump: two duty points, rounded up with 0.3 m margin
    PUMP_C["head"] = math.ceil(r["tdh_2"][1] + 0.3)
    PUMP_C["head_1"] = math.ceil(r["tdh_1_end"][1] + 0.3)
    h = r["tdh_2"][1]
    r["p_hyd"] = RHO * G * Q_C / 3600 * h
    r["p1"] = r["p_hyd"] / ETA                                   # cascade, average running power
    r["p1_max"] = RHO * G * Q_C / 3600 * PUMP_C["head"] / ETA    # at the rated point
    r["i_dc"] = r["p1_max"] / U_DC
    # the pump's own flat cable runs in the conduit from the pit to the AL box, in one piece
    s_min = 2 * L["pump_cable"] * r["i_dc"] * RHO_CU / (DROP_MAX * U_DC)
    s = next(x for x in (2.5, 4, 6, 10, 16) if x >= s_min)
    i_avg = r["p1"] / U_DC
    drop = 2 * L["pump_cable"] * r["i_dc"] * RHO_CU / s
    r["cable"] = dict(s_min=s_min, s=s, drop=drop, drop_pct=drop / U_DC * 100,
                      drop_avg_pct=2 * L["pump_cable"] * i_avg * RHO_CU / s / U_DC * 100, i_avg=i_avg)
    PUMP_C["cable_s"] = s
    r["drain_h"] = Q["water_vol"] / Q_GARDEN
    r["refill"] = Q["water_vol"] * OPS["water_price"]
    # quantities
    pl, pw, pd = CAGE["L"] + 0.40, CAGE["W"] + 0.40, PIT["depth"] + 0.20
    r["caisson"] = (pl, pw, pd)
    r["c_pit"] = pl * pw * pd - CAGE["L"] * CAGE["W"] * PIT["depth"]
    r["pit_surf"] = CAGE["L"] * CAGE["W"] + 2 * (CAGE["L"] + CAGE["W"]) * PIT["depth"]
    trench_len = plen(ROUTES["T2"]) + plen(ROUTES["T1"]) + plen(ROUTES["CABLE"]) + plen(ROUTES["DC"]) + plen(ROUTES["LIGHT"]) - 6.0
    r["trench"] = 0.4 * 0.6 * trench_len + 1.0                   # T0/DC share the trench near the wall; + over-dig of the pit
    r["pipes"] = dict(d63=L["t0"] + L["t2"], pehd=L["t1"])
    r["rebar"] = [
        dict(pos=14, desc="Puisard - radier du caisson HA10 e=15, 2 nappes", d=10, n=2 * (int(pw / 0.15) + 1 + int(pl / 0.15) + 1), L=(pl + pw) / 2 + 0.30),
        dict(pos=15, desc="Puisard - voiles du caisson, U HA10 e=15", d=10, n=int(2 * (pl + pw) / 0.15), L=2 * pd + 0.40),
        dict(pos=16, desc="Puisard - chevêtres autour de l'ouverture du radier HA12", d=12, n=8, L=CAGE["L"] + 0.80),
        dict(pos=17, desc="Mur de cascade - noyau HA10 e=20, 2 faces", d=10, n=2 * int((CASCADE["y1"] - CASCADE["y0"]) / 0.20) + 8, L=0.95),
    ]
    for b in r["rebar"]:
        b["kg"] = b["n"] * b["L"] * HA[b["d"]]
    r["steel"] = sum(b["kg"] for b in r["rebar"])
    return r


R = calc()


# ---------------------------------------------------------------------------
# Estimate (DQE) - variant C, same unit-price basis as v1.3.1 (indice E)
# ---------------------------------------------------------------------------

def dqe_c():
    lots, _ = M.dqe()
    out = []
    p = R["pipes"]
    pl, pw, pd = R["caisson"]
    for code, fr, en, items in lots:
        items = list(items)
        if code == "1":
            items = [it if it[0] != "1.05" else ("1.05", "Fouilles en tranchée (tubes 1 et 2, câbles) et surcreusement du puisard", it[2], "m³", round(R["trench"], 1), it[5]) for it in items]
        if code == "2":
            items = [it for it in items if it[0] != "2.06"]
            items.append(("2.06", f"Caisson du puisard {pl:.2f} × {pw:.2f} × {pd:.2f} hors tout : béton B25 + hydrofuge, coulé avec le radier", "Pump pit concrete", "m³", round(R["c_pit"], 2), 1700))
            items.append(("2.07", "Acier HA FeE500 pour le caisson du puisard et le noyau du mur de cascade (repères 14 à 17)", "Rebar for pit and cascade core", "kg", round(R["steel"], -1), 14))
        if code == "3":
            items.append(("3.07", "Puisard : enduit hydrofuge + membrane ciment flexible 2 couches (continuité avec le bassin)", "Pit lining", "m²", round(R["pit_surf"], 1), 190))
        if code == "4":
            items = [
                ("4.01", f"Cage inox 316L perforée {CAGE['L'] * 1000:.0f} × {CAGE['W'] * 1000:.0f} en 2 panneaux (tôle 3 mm, trous Ø8 au pas de 12), cadre scellé au ras du fond, vis inviolables", "Stainless pit cage", "U", 1, 5200),
                ("4.02", f"Pompe de forage 4\" immergée TBTS {U_DC:.0f} V CC, Ø{PUMP_C['D'] * 1000:.0f} × {PUMP_C['L']:.2f} m, {Q_C:.0f} m³/h à {PUMP_C['head']} mCE et {Q_GARDEN:.0f} m³/h à {PUMP_C['head_1']} mCE, pose horizontale admise, inox, contrôleur, câble plat 2 × {PUMP_C['cable_s']:g} mm² de {math.ceil(L['pump_cable'])} m", "24 V DC borehole pump", "U", 1, 8500),
                ("4.03", "Kit de pose : chemise de refroidissement Ø150, berceau inox, flexible 1-1/4\", raccord rapide inox, anneaux et perche de levage", "Pump installation kit", "Ft", 1, 2400),
                ("4.04", "Fourreaux à collerette + bagues hydrogonflantes (sortie T0, fourreau du câble, entrée de la cascade)", "Puddle-flange sleeves", "U", 3, 250),
                ("4.05", "Canalisations PVC pression PN16 Ø63 collées (T0 et tube 2)", "PVC Ø63 pipework", "ml", round(p["d63"]), 65),
                ("4.06", "Tube 1 : PEHD Ø50 PN10 du regard RV au puits perdu (verger), sortie à grille", "PE tube 1", "ml", round(p["pehd"]), 45),
                ("4.07", f"Regard de vannes RV {RV['a']:.2f} × {RV['a']:.2f} × {RV['depth']:.2f}, couvercle au ras du sol : té Ø63, vannes 1/4 de tour V1 (tube 1) et V2 (tube 2), raccords union, purge", "Valve box", "Ft", 1, 1900),
                ("4.08", "Mur de cascade : noyau BA, parement et chapeau pierre, lame inox 600 mm avec chambre de répartition (tube 2)", "Cascade wall with slot outlet", "Ft", 1, 7500),
                ("4.09", "Essai de mise en pression des canalisations 24 h", "24 h pressure test", "Ft", 1, 400),
                ("4.10", "Échelle inox 316L 4 marches (grand fond 1.80 m)", "Ladder", "U", 1, 3200),
                ("4.11", "Kit d'entretien (épuisette de surface, brosse, manche, trousse d'analyse, diffuseur de chlore flottant)", "Maintenance kit", "Ft", 1, 1200),
            ]
        if code == "5":
            items = [
                ("5.01", "Alimentation 230 V depuis un départ dédié du TGBT : câble U1000 R2V 3G2,5 mm² sous TPC Ø63 + grillage avertisseur", "230 V supply cable", "ml", round(L["cable"]), 80),
                ("5.02", f"Boîtier AL IP65 fermé à clé sur poteau, à {U0 - AL['u']:.2f} m du bassin (hors volumes) : interrupteur, DDR 30 mA type A, disjoncteurs, horloge, parafoudre", "AL box on a post", "Ft", 1, 4800),
                ("5.03", f"Alimentation de sécurité 230 V / {U_DC:.0f} V CC (transformateur de sécurité NF EN 61558-2-6) dans le boîtier AL", "24 V DC safety supply", "U", 1, 2800),
                ("5.04", "Projecteur LED 12 V 30 W + niche + presse-étoupe", "12 V LED pool light", "U", 3, 1400),
                ("5.05", "Transformateur de sécurité 12 V 300 VA (dans le boîtier AL)", "12 V safety transformer", "U", 1, 1100),
                ("5.06", "Fourreaux TPC Ø40 (câble de la pompe, câbles 12 V des projecteurs) et câbles 12 V", "Conduits and 12 V cables", "ml", round(L["conduit"] + L["light"]), 45),
                ("5.07", "Liaison équipotentielle : ferraillages, cadre et cage inox, lame de la cascade, échelle + piquet de terre", "Equipotential bonding", "Ft", 1, 1300),
                ("5.08", "Éclairage extérieur : bornes et spots LED IP65, câblage compris ; à moins de 3.50 m du bassin en TBTS 12 V", "Garden lights", "U", 14, 380),
            ]
        out.append((code, fr, en, items))
    opts = ("O", "Options (non comprises dans le total)", "Options", [
        ("OPT.1", "Filtre à cartouche 13.9 m² dans le mur de cascade, sur le tube 2 (coffre, couvercle pierre, cartouche de rechange) : l'eau reste claire", "Cartridge filter on tube 2", "Ft", 1, 11000),
        ("OPT.2", "Robot nettoyeur sans fil à filtre intégré (batterie rechargée hors volumes) : aspire le fond et filtre l'eau sans aucun tuyau", "Cordless robot cleaner", "U", 1, 8000),
        ("OPT.3", "Deux skimmers raccordés au puisard (écrémage de la surface)", "Two skimmers to the pit", "Ft", 1, 3700),
        ("OPT.4", "Pompe à chaleur 12 kW (hors volumes)", "Heat pump", "U", 1, 28000),
        ("OPT.5", "Clôture de sécurité amovible h 1.20 m + portillon auto-fermant", "Safety fence", "ml", 36, 400),
        ("OPT.6", "Couverture de sécurité à barres", "Safety bar cover", "U", 1, 12000),
    ])
    return out, opts


def totals(lots):
    return sum(it[4] * it[5] for _, _, _, items in lots for it in items)


def ops_costs():
    """Running cost with the same hypotheses as the E / B comparison (same pump hours)."""
    o = OPS
    hours = o["days_summer"] * o["h_summer"] + o["days_winter"] * o["h_winter"]
    e = R["p1"] * hours / 1000
    return dict(hours=hours, energy=e, cost=e * o["tariff"])


def compare():
    """Whole-estimate totals and running costs of E, B and C (same prices, same hypotheses)."""
    oc_b = B.ops_costs()
    oc_c = ops_costs()
    lots_c, _ = dqe_c()
    lots_e, _ = M.dqe()
    lots_b, _ = B.dqe_b()
    return dict(total_e=totals(lots_e), total_b=totals(lots_b), total_c=totals(lots_c),
                e_e=oc_b["rows"][0][2], e_b=oc_b["rows"][0][3], e_c=oc_c["energy"],
                ops_e=oc_b["tot_old"], ops_b=oc_b["tot_new"], ops_c=oc_c["cost"], hours=oc_c["hours"])


if __name__ == "__main__":
    print("lengths", {k: round(v, 2) for k, v in L.items()})
    for k in ("tdh_2", "tdh_1", "tdh_1_end"):
        rows, t = R[k]
        print(k, round(t, 2), [(n[:30], round(v, 3)) for n, v in rows])
    print("pump", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in PUMP_C.items()})
    print("p1", round(R["p1"]), "p1 max", round(R["p1_max"]), "I", round(R["i_dc"], 1), "cable", {k: round(v, 2) for k, v in R["cable"].items()}, "L", round(L["pump_cable"], 2))
    print("cage", round(R["cage_open"], 3), round(R["v_cage"], 4), "sleeve", round(R["v_sleeve"], 3), "drain h", round(R["drain_h"], 1), "refill", round(R["refill"]))
    print("pit", round(R["c_pit"], 3), "surf", round(R["pit_surf"], 2), "steel", round(R["steel"], 1), "trench", round(R["trench"], 1), "pipes", {k: round(v, 1) for k, v in R["pipes"].items()})
    print({k: round(v) for k, v in compare().items()})
