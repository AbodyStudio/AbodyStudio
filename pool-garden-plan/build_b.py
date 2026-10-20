"""Construit la variante B (piscine sans local technique) : page HTML, planches SVG, archive zip.

Même bassin que l'indice E (v1.3.1) ; seul le système hydraulique change.
Author: AbodyStudio Limited - https://abodystudio.com/
Usage : python3 build_b.py
"""
import os
import re
import shutil
import sys
import unicodedata
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

import model  # noqa: E402
import variant_b as B  # noqa: E402

DATE = "20/10/2026"
model.VERSION, model.INDICE, model.DATE = B.VERSION, B.INDICE, DATE

import sheets as SH  # noqa: E402
import sheets_b as SB  # noqa: E402
import build  # noqa: E402
from build import esc, fr, nf, money, hm, ic, NB  # noqa: E402
from model import Q, LV, POOL_L, POOL_W, PUMP_FLOW, WATER_SHALLOW, WATER_DEEP, AUTHOR, CONTRACTOR, hu  # noqa: E402
from variant_b import R, PUMP, FILTER, VAULT, HATCH, SUMP, SUMP_DEPTH, GRILLE, SLOT, CASCADE, INLET_LEVEL, V_IN_A, V_IN_B, V_IN_H  # noqa: E402

VERSION, INDICE = B.VERSION, B.INDICE
ZIP_NAME = f"AbodyStudio_Gharsa-Foquiya_Piscine-Sans-Local-Technique_v{VERSION}.zip"

# ---------------------------------------------------------------------------
# Wiring: variant sheets, estimate, cartouche
# ---------------------------------------------------------------------------
SH.SHEETS = SB.VB_SHEETS
SH.VARIANT = SB.HOOKS
SH.FRAME_SUB = B.SUBTITLE
build.SHEETS = SB.VB_SHEETS
build.dqe = B.dqe_b
build.ICONS["solid"] += ["arrow-down", "filter", "plug", "ban", "scale-balanced", "toolbox", "gauge-high", "droplet", "circle-plus", "lock", "recycle"]

C = B.compare()
OC = B.ops_costs()
SP = B.scope_split()
H_ORIG = C["head_orig"]
H_NEW = R["design_head"]


def n0(x):
    return money(round(x))


def pct(a, b):
    return f"{(b - a) / a * 100:+.0f}{NB}%".replace("-", "−")


def sgn(x):
    return (f"+{money(round(x))}" if x >= 0 else f"−{money(round(-x))}")


# ---------------------------------------------------------------------------
# Content overrides (French)
# ---------------------------------------------------------------------------

def facts():
    rows = [
        ("Bassin (inchangé)", f"{nf(POOL_L)} × {nf(POOL_W)} m - 50 m²"),
        ("Profondeur d'eau", f"{nf(WATER_SHALLOW)} m → {nf(WATER_DEEP)} m"),
        ("Volume d'eau", f"{hu(Q['water_vol']).replace('.', ',')} m³"),
        ("Local technique", "aucun - fosse sous trappe"),
        ("Pompe", f"{PUMP_FLOW} m³/h - HMT {nf(H_NEW)} mCE"),
        ("Filtre", f"cartouche {nf(FILTER['area'], 1)} m²"),
    ]
    return "".join(f"<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>" for a, b in rows)


build.facts = facts

L = R["L"]
P_ = R["pipes_new"]
build.HYD = [
    ("Pompe", f"{PUMP_FLOW} m³/h à {PUMP['head']:.0f} mCE, vitesse variable, préfiltre intégré, 230 V, montée à sec dans la fosse, {nf(LV['water'] - VAULT['floor'] - 0.15)} m sous le plan d'eau (aspiration en charge)"),
    ("Filtre à cartouche", f"{nf(FILTER['area'], 1)} m² ({FILTER['area_ft2']} ft²) : {nf(R['filter_rate'])} m³/h par m², sans contre-lavage. Enveloppe maximale Ø 0,40 × 0,90 m"),
    ("Aspiration", f"Puisard sous grille 800 × 600 au grand fond ({B.SUMP_SHARE * 100:.0f} %) et 2 skimmers ({(1 - B.SUMP_SHARE) / 2 * 100:.0f} % chacun) : vannes VA, VS1, VS2"),
    ("Refoulement", "Sélecteur V1 (A1 : 2 buses dissimulées), V2 (A2 : cascade), V3 cadenassée (B : rejet au jardin)"),
    ("Canalisations", f"PVC pression PN16 : {nf(P_['d63'], 1)} ml Ø63 et {nf(P_['d50'], 1)} ml Ø50, plus {nf(P_['pehd'], 1)} ml de PEHD Ø50 vers le verger. Essai de pression 24 h avant remblai"),
    ("Fosse technique", f"{nf(V_IN_A)} × {nf(V_IN_B)} × {nf(V_IN_H)} m intérieur, sèche, sous trappe à carreler {nf(HATCH['a1'] - HATCH['a0'])} × {nf(HATCH['b1'] - HATCH['b0'])} m classe A15 à clé ; siphon à clapet, flotteur, ventilation"),
    ("Rejet", "Circuit B vers la borne de contrôle : clapet, casse-vide au point haut ±0,00, robinet de prélèvement, vanne 3 voies vers le verger ou le puits perdu"),
    ("Traitement", "Chlore (diffuseur flottant ou dosage manuel) et correction du pH. Pas d'électrolyseur au sel : l'eau rejetée doit pouvoir aller au verger"),
]
build.ELEC = [
    ("Alimentation", f"Depuis le TGBT vers le coffret piscine CP posé en façade, à {nf(model.POOL['v0'] - B.COFFRET['v'])} m de l'eau, hors volumes ; câble 3G2,5 et câble TBTS sous gaines TPC distinctes jusqu'à la fosse"),
    ("Coffret CP", "Sectionneur Q0 cadenassable, parafoudre, DDR 30 mA type A, disjoncteurs Q1 à Q5, contacteur KM1 2 pôles, horloge, transformateurs de sécurité 12 V (projecteurs) et 24 V CC (sécurités)"),
    ("Fosse (volume 1)", "Seul le moteur de la pompe est en 230 V. Fosse fermée à clé ; l'ouverture de la trappe (contact CT) ou le flotteur FL ouvre KM1 : la pompe est coupée sur ses 2 pôles"),
    ("Éclairage", "3 projecteurs LED 12 V 30 W (TBTS). Les bornes de jardin à moins de 3,50 m du bassin passent en TBTS 12 V"),
    ("Liaison équipotentielle", "Ferraillages du bassin et de la fosse, cadre de trappe, lame inox, échelle et carcasse du moteur reliés à la LEL et au piquet de terre"),
    ("Conformité", "Concept établi sur les principes de la NF C 15-100 section 702 / CEI 60364-7-702, non vérifié : à valider et réceptionner par un électricien qualifié"),
]

build.SPECS = [
    ("trowel-bricks", "Lot 1 - Terrassements", [
        "Mêmes terrassements que l'indice E pour le bassin. La fouille du grand fond est élargie côté NO pour la fosse, et surcreusée de 0,60 m au droit du puisard.",
        f"Fouilles en tranchée réduites à {nf(R['trench'], 1)} m³ : une seule tranchée le long du côté NE pour A1 et A2, une pour le circuit B et une pour les câbles.",
        f"Gros béton dosé à 200 kg/m³ sous la fosse ({nf(R['lean_fill'], 2)} m³), coulé du fond de fouille du bassin jusqu'à {nf(VAULT['base_under'])} : la fosse a la même assise que le bassin.",
        "Remblai seulement après l'essai d'étanchéité et l'essai de pression des canalisations.",
    ]),
    ("helmet-safety", "Lot 2 - Béton armé", [
        "Bassin identique à l'indice E (radier, voiles, chaînage, escalier, aciers repères 1 à 13).",
        f"Caisson du puisard {nf(SUMP['x1'] - SUMP['x0'])} × {nf(SUMP['y1'] - SUMP['y0'])} × {nf(SUMP_DEPTH)} m coulé avec le radier, cadres HA12 (repère 17), fourreau de sortie posé avant coulage.",
        f"Fosse : radier et voiles BA de 0,20 m (repères 14 et 15), attentes HA10 scellées dans le voile du bassin (repère 16), linteau sous margelle. Béton fosse + puisard : {nf(R['c_vault'] + R['c_sump'])} m³.",
        "Mur de cascade : noyau BA de 0,20 m sur le voile SE (repère 18), niche réservée pour la chambre de répartition.",
    ]),
    ("water", "Lot 3 - Étanchéité", [
        "Bassin : enduit hydrofuge + ciment flexible 2 couches, continu dans le puisard et remonté sur la face mouillée de la cascade jusqu'à l'arase. La mosaïque est une finition, elle n'étanche pas.",
        "Fosse sous le niveau de l'eau : revêtement cristallin 2 couches en face intérieure et membrane bitumineuse en face extérieure, drain au pied.",
        "Joints hydrogonflants à toutes les reprises ; fourreaux à collerette et bague hydrogonflante à toutes les traversées.",
        "Essai d'étanchéité du bassin pendant 7 jours, fosse vide et sèche : toute venue d'eau dans la fosse est visible.",
    ]),
    ("faucet-drip", "Lot 4 - Hydraulique", [
        "Pompe, filtre à cartouche, nourrices et sélecteur montés à sec dans la fosse, sur raccords union, tous accessibles par la trappe.",
        "Grille 800 × 600 vissée sur le puisard : plus grande qu'un corps, elle ne peut pas être obstruée par une personne.",
        "Buses RA1-RA2 sous la cascade, orientées vers le puisard : l'eau traverse tout le bassin, du petit bain vers le grand fond.",
        "Borne de contrôle maçonnée dans le jardin NO pour le circuit B, V3 cadenassée hors rejet.",
    ]),
]

build.SEQ = [
    ("Préparation", "Relevé et implantation à partir de la façade, comme à l'indice E. Laisser le chlore de la piscine Intex se dissiper 3 à 4 jours, puis la vider dans le verger."),
    ("Terrassement", "Fouille du bassin, élargie côté NO pour la fosse ; surcreusement du puisard. Contrôle du fond de forme."),
    ("Fondation", "Hérisson, béton de propreté, lit du drain périphérique ; fond du caisson du puisard."),
    ("Radier et puisard", "Ferraillage du radier et du caisson, cadre de la grille, fourreau de sortie du puisard, aciers en L des voiles. <b>Point d'arrêt :</b> réception du ferraillage. Coulage en une fois."),
    ("Voiles", "Joint hydrogonflant, voiles et chaînage avec les skimmers, les buses RA1-RA2, les niches des projecteurs et les attentes de la fosse (repère 16)."),
    ("Fosse et cascade", "Gros béton jusqu'au niveau du radier de la fosse ; radier, voiles et linteau de la fosse ; noyau du mur de cascade."),
    ("Canalisations", "Aspiration puisard noyée dans le gros béton, lignes A1, A2, B et skimmers. <b>Point d'arrêt :</b> essai de pression 24 h avant de recouvrir."),
    ("Cure", "21 à 28 jours. Pendant ce temps : gaines électriques, puits perdu, escalier d'accès, borne de contrôle."),
    ("Étanchéité", "Bassin, puisard et face de la cascade ; cristallin intérieur et membrane extérieure de la fosse. <b>Point d'arrêt :</b> essai d'étanchéité de 7 jours, puis remblai."),
    ("Finitions", "Mosaïque et joint époxy, margelles, dallage et trappe carrelée, parement et chapeau de la cascade, chambre et lame inox."),
    ("Équipements", "Pompe, filtre, nourrices, coffret en façade, contact de trappe et flotteur. L'électricien vérifie le DDR, la coupure à l'ouverture de la trappe et la liaison équipotentielle."),
    ("Essais", "Essai de chaque position du sélecteur (A, B, A+B, C, E), réglage de V1 pour la lame, essai du casse-vide de la borne."),
    ("Jardins et mise en eau", "Jardins, éclairage, clôtures ; remplissage par camion-citerne, équilibrage de l'eau, remise au propriétaire de la procédure plastifiée et des clés."),
]

build.GANTT = [
    ("Préparation et implantation", 1, 1), ("Dépose de la piscine Intex", 1, 1), ("Terrassement, fondation, puisard", 2, 1.5),
    ("Radier et caisson du puisard", 3, 1), ("Voiles et chaînage", 4, 1.5), ("Fosse et noyau de la cascade", 5, 1.5),
    ("Canalisations et essai de pression", 5, 1.5), ("Cure du béton", 5.5, 3.5), ("Enduit, membrane, cristallin", 9, 1),
    ("Essai d'étanchéité et remblai", 10, 1), ("Mosaïque, margelles, trappe, cascade", 11, 2), ("Plage, caniveau, escalier d'accès", 12, 1.5),
    ("Électricité et équipements", 11, 2.5), ("Jardins, borne de rejet, clôtures", 13, 2), ("Mise en eau et essais", 14, 1),
]

GL = dict(build.GLOSS)
for k in ("Local technique", "Filtre à sable", "Bonde de fond", "Prise balai", "Nourrice (collecteur)"):
    GL.pop(k, None)
GL.update({
    "Fosse technique intégrée": "حفرة تقنية مدمجة",
    "Trappe de visite": "فتحة تفتيش",
    "Puisard": "حوض تجميع",
    "Grille anti-coincement": "شبكة مانعة للانحشار",
    "Cascade / lame d'eau": "شلال / شفرة مائية",
    "Filtre à cartouche": "فلتر خرطوشة",
    "Sélecteur (vannes)": "صمامات التوجيه",
    "Clapet anti-retour": "صمام عدم الرجوع",
    "Casse-vide": "كاسر الفراغ",
    "Rejet contrôlé": "تصريف مراقب",
})
build.GLOSS = list(GL.items())

build.VERIFY = build.VERIFY + [
    "Fiches des matériels réellement achetés : courbe de la pompe (12 m³/h à 9 mCE au moins), auto-amorçage, IPX5 ; encombrement du filtre (≤ Ø 0,40 × 0,90 m) ; débit minimal de la lame ; classe A15 de la trappe.",
    "Nappe : le sondage du grand fond dit aussi si la fosse sera dans l'eau en hiver. Si oui, le BET vérifie la fosse au soulèvement et renforce l'étanchéité extérieure.",
    "Électricité : l'électricien valide le concept de la fosse (accès à clé, coupure à l'ouverture, DDR, TBTS, liaison équipotentielle) avant l'achat du coffret.",
    "Rejet au jardin : vérifier la capacité d'infiltration du verger par un essai à l'eau claire avant la première vidange.",
]


# ---------------------------------------------------------------------------
# New sections
# ---------------------------------------------------------------------------

def tbl(head, rows, num=()):
    th = "".join(f'<th class="num">{esc(h)}</th>' if i in num else f"<th>{esc(h)}</th>" for i, h in enumerate(head))
    body = []
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            tag = "th" if i == 0 else "td"
            cls = ' class="num"' if i in num else ""
            cells.append(f"<{tag}{cls}>{c if str(c).startswith('<') else esc(c)}</{tag}>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def sec_principle():
    orig = [("BASSIN", "10 × 5 m, 50,373 m³"), ("LOCAL TECHNIQUE EXTÉRIEUR", "2,40 × 2,00 m, à 3,55 m"), ("ÉQUIPEMENTS CLASSIQUES", "sable, vanne 6 voies, 4 aspirations, 4 buses")]
    new = [("BASSIN", "inchangé"), ("FOSSE INTÉGRÉE", "sèche, sous trappe"), ("UNE POMPE", f"{PUMP_FLOW} m³/h"), ("FILTRE COMPACT", f"cartouche {nf(FILTER['area'], 1)} m²"),
           ("2 CIRCUITS CONTRÔLÉS", "A retour, B jardin"), ("RETOUR ARCHITECTURAL", "cascade + buses"), ("REJET JARDIN", "borne de contrôle")]
    chip = lambda a, b, c="": f'<div class="chip{c}"><b>{esc(a)}</b><span>{esc(b)}</span></div>'
    return f'''<section class="blk" id="principe">
  <h2><span class="sn">03</span>Principe : même bassin, hydraulique repensée</h2>
  <p class="lead">{fr("Cette variante part du dossier de l'indice E sans toucher au bassin : dimensions, implantation, niveaux, profil du fond, structure et finitions restent les mêmes. Le local technique extérieur disparaît. La pompe, le filtre et les vannes vont dans une fosse sèche accolée au grand fond, sous une trappe carrelée au niveau du dallage.")}</p>
  <div class="flow"><p class="flow-l">Indice E</p><div class="chips">{"".join(chip(a, b) for a, b in orig)}</div>
  <p class="flow-a">{ic("arrow-down")}</p><p class="flow-l red">Variante B</p><div class="chips">{"".join(chip(a, b, " new") for a, b in new)}</div>
  <p class="flow-k">{ic("ban")} Pas de local technique extérieur</p></div>
  <div class="two">
    <div class="spec"><h3>{ic("shield-halved")}Pourquoi deux compartiments</h3><ul>
      <li>{fr("Une pompe 230 V ne peut pas être posée dans l'eau du bassin (volume 0). Le croquis d'origine (pompe dans une fente de 20 à 30 cm sur 2 m de profondeur) est donc séparé en deux.")}</li>
      <li>{fr(f"Le puisard, sous la grille, fait partie du bassin : {nf(SUMP['x1'] - SUMP['x0'])} × {nf(SUMP['y1'] - SUMP['y0'])} m sur {nf(SUMP_DEPTH)} m, étanché comme le bassin.")}</li>
      <li>{fr(f"La fosse est sèche, à côté du voile NO : {nf(V_IN_A)} × {nf(V_IN_B)} × {nf(V_IN_H)} m intérieur, dimensions tirées de l'encombrement maximal de la pompe, du filtre et des vannes, avec la place pour les mains.")}</li>
      <li>{fr(f"La pompe est {nf(LV['water'] - VAULT['floor'] - 0.15)} m sous le plan d'eau : elle est toujours en charge et ne se désamorce pas en service.")}</li>
    </ul></div>
    <div class="spec"><h3>{ic("circle-check")}Ce qui ne change pas</h3><ul>
      <li>{fr("Bassin 10,00 × 5,00 m centré sur la façade, à 5,00 m de la villa ; margelles à −0,70, eau à −0,85.")}</li>
      <li>{fr(f"Profondeur 0,55 → 1,80 m, rupture de pente à 1,20 m, volume {hu(Q['water_vol']).replace('.', ',')} m³.")}</li>
      <li>{fr("Radier, voiles et chaînage de l'indice E, escalier d'entrée, projecteurs, échelle, plage, jardins, escalier d'accès.")}</li>
      <li>{fr("Les deux skimmers SK1 et SK2 restent à leur place : un skimmer pour 25 m² de plan d'eau.")}</li>
    </ul></div>
  </div>
</section>'''


def loss_table(mode, title, q=PUMP_FLOW):
    rows, tot = B.tdh(mode, q=q)
    trs = "".join(f"<tr><td>{esc(n)}</td><td class='num'>{nf(v)}</td></tr>" for n, v in rows)
    return (f'<div class="loss"><h4>{esc(title)} <span class="mono">{nf(q, 0)}{NB}m³/h</span></h4><div class="tbl"><table><tbody>{trs}'
            f'<tr class="vol-tot"><th>HMT moyenne</th><td class="num">{nf(tot)}{NB}mCE</td></tr></tbody></table></div></div>')


def sec_calc():
    st = lambda m, s_: B.tdh(m, q=B.Q_GARDEN if m == "C" else PUMP_FLOW, state=s_)[1]
    data = [
        ("Volume d'eau", f"{hu(Q['water_vol']).replace('.', ',')} m³"),
        ("Débit de filtration", f"{PUMP_FLOW} m³/h : recyclage en {hm(Q['water_vol'] / PUMP_FLOW)}"),
        ("Grille du puisard", f"800 × 600 mm, {GRILLE['open_ratio'] * 100:.0f} % de vide : {nf(R['grille_open'], 3)} m² de passage"),
        ("Vitesse au passage de la grille", f"{nf(R['v_grille'], 3)} m/s ({nf(R['v_grille_all'], 3)} m/s skimmers fermés, {nf(R['v_grille_half'], 3)} m/s grille à moitié couverte), pour une limite usuelle de 0,5 m/s"),
        ("Grille non obstruable par un corps", f"plus grande que 457 × 584 mm (gabarit d'une personne couchée) : {'oui' if R['unblockable'] else 'non'}"),
        ("Vitesses dans les tuyaux", f"aspiration puisard {nf(R['v_suction'])} m/s, skimmers {nf(R['v_skimmer'])} m/s, collecteur et refoulement Ø63 {nf(R['v_trunk'])} m/s, circuit B {nf(R['v_b'])} m/s"),
        ("Lame d'eau 600 × 6 mm", f"{nf(R['slot_q_per_m'])} L/s par mètre en position B (minimum usuel {nf(B.SHEET_MIN, 1)} L/s/m), sortie {nf(R['slot_v'])} m/s"),
        ("Position A+B", f"partage libre {nf(R['q_ab_free_b'], 1)} m³/h sur la cascade, trop peu : V1 réglée pour garder {nf(PUMP_FLOW - R['q_a_in_ab'], 1)} m³/h"),
        ("Vidange complète par B", f"{nf(R['drain_hours'], 1)} h à {nf(B.Q_GARDEN, 0)} m³/h ; hauteur d'aspiration en fin de vidange {nf(R['suction_lift_end'])} m (pompe auto-amorçante)"),
        ("Point de fonctionnement retenu", f"{PUMP_FLOW} m³/h à {nf(R['head_dirty'])} mCE filtre au seuil de nettoyage : pompe de {PUMP['head']:.0f} mCE au moins"),
        ("Puissance", f"hydraulique {n0(R['p_hyd'])} W ; absorbée {n0(R['p1_est'])} W avec un rendement global de {nf(R['eta'])} (hypothèse)"),
    ]
    modes = [("A", "Position A - buses"), ("B", "Position B - cascade"), ("AB", "Position A+B"), ("C", "Position C - jardin")]
    losses = "".join(loss_table(m, t, B.Q_GARDEN if m == "C" else PUMP_FLOW) for m, t in modes)
    summary = [(t, f"{nf(st(m, 'clean'))}", f"{nf(st(m, 'avg'))}", f"{nf(st(m, 'dirty'))}") for m, t in modes]
    summary.append(("Indice E, même méthode", "", f"{nf(H_ORIG)}", ""))
    bore = [
        ("Usage prévu", "forage profond : petit débit, grande hauteur", "piscine : grand débit, faible hauteur"),
        ("Point demandé", "courbe non fournie, à demander au vendeur", f"{PUMP_FLOW} m³/h à {PUMP['head']:.0f} mCE"),
        ("Sortie", f"1-1/4\" NPT (DN32) : {nf(B.PUMP_FLOW / 3600 / (3.14159 * 0.032 ** 2 / 4))} m/s à {PUMP_FLOW} m³/h", f"Ø63 : {nf(R['v_trunk'])} m/s"),
        ("Préfiltre", "aucun : cheveux et feuilles vont dans la pompe et le filtre", "panier intégré"),
        ("Pose", "immergée : 230 V dans l'eau du bassin (volume 0)", "à sec, dans la fosse fermée"),
        ("Matériaux, connexion", "inox, fiche de type américain", "corps pour eau chlorée, câblée dans le coffret"),
        ("Verdict", "ne convient pas", "retenue"),
    ]
    filt = [
        ("Surface ou section", f"Ø{model.FILTER_D * 1000:.0f} mm : {nf(3.14159 * model.FILTER_D ** 2 / 4, 3)} m²", f"{nf(FILTER['area'], 1)} m² de cartouche"),
        ("Vitesse / taux de filtration", f"{nf(Q['filter_rate'], 1)} m/h", f"{nf(R['filter_rate'])} m³/h par m²"),
        ("Perte de charge moyenne (même méthode)", f"{nf(B.filt_loss(B.SAND))} mCE", f"{nf(B.filt_loss(FILTER))} mCE"),
        ("Lavage", f"contre-lavage {nf(B.OPS['backwash_m3'], 1)} m³ × {B.OPS['backwash_n']} par an", f"jet d'eau, {nf(B.OPS['clean_m3'], 2)} m³ × {B.OPS['clean_n']} par an"),
        ("Encombrement", "Ø 0,60 m + vanne 6 voies : demande un local", "≤ Ø 0,40 × 0,90 m : tient dans la fosse"),
        ("Consommable", f"sable : {money(B.OPS['sand_price'])} DH tous les {B.OPS['sand_years']} ans", f"cartouche : {money(B.OPS['cartridge_price'])} DH tous les {B.OPS['cartridge_years']} ans (une rechange fournie)"),
        ("Prix au devis", money(6000) + " DH HT", money(7500) + " DH HT avec la rechange"),
    ]
    return f'''<section class="blk" id="calc">
  <h2><span class="sn">05</span>Calculs hydrauliques</h2>
  <p class="lead">{fr("Pertes de charge calculées par Hazen-Williams (PVC, C = 150) et coefficients de singularités, sur les longueurs mesurées sur les plans. La perte du filtre est prise à sa valeur propre plus la moitié du seuil de nettoyage (0,5 bar), pour les deux systèmes.")}</p>
  {tbl(("Grandeur", "Valeur"), data)}
  <div class="losses">{losses}</div>
  <h3>{ic("gauge-high")}Hauteur manométrique totale (mCE)</h3>
  {tbl(("Mode", "Filtre propre", "Moyenne", "Filtre au seuil"), summary, num=(1, 2, 3))}
  <div class="two">
    <div><h3>{ic("ban")}La pompe de forage de la photo</h3>{tbl(("Critère", "Pompe de forage 1 HP", "Pompe retenue"), bore)}</div>
    <div><h3>{ic("filter")}Filtre à sable ou à cartouche</h3>{tbl(("Critère", "Sable (indice E)", "Cartouche (variante B)"), filt)}</div>
  </div>
</section>'''


def sec_compare():
    tr = OC["rows"]
    rows = [
        ("Local technique", "semi-enterré 2,40 × 2,00 m (4,80 m² hors œuvre) à 3,55 m du bassin, porte, ventilation", f"aucun ; fosse sèche {nf(R['vault_ext'][0])} × {nf(R['vault_ext'][1])} m ({nf(C['footprint_new'])} m²) sous le dallage, trappe carrelée", "−4,80 m² de construction"),
        ("Pompe", f"{PUMP_FLOW} m³/h à 10 mCE ; HMT moyenne {nf(H_ORIG)} mCE", f"{PUMP_FLOW} m³/h à {PUMP['head']:.0f} mCE ; HMT moyenne {nf(H_NEW)} mCE", pct(H_ORIG, H_NEW) + " de HMT"),
        ("Filtration", "sable Ø 600 + vanne 6 voies", f"cartouche {nf(FILTER['area'], 1)} m²", "même débit, pas de contre-lavage"),
        ("Canalisations", f"{C['pipes_orig']:.0f} ml PVC (devis E)", f"{nf(C['pipes_new'], 1)} ml PVC + {nf(C['pehd'], 1)} ml PEHD", pct(C["pipes_orig"], C["pipes_new"]) + " de PVC"),
        ("Vannes et organes", "4 vannes d'aspiration, vannes de refoulement, vanne 6 voies", "6 vannes 1/4 de tour, vanne 3 voies, 2 clapets, casse-vide", "un peu plus d'organes, tous dans la fosse"),
        ("Complexité de construction", "bâtiment séparé + 4 lignes d'aspiration et une boucle de refoulement", "ouvrage étanche sous le niveau de l'eau (double étanchéité), puisard, trappe, cascade", "plus technique au grand fond, plus simple ailleurs"),
        ("Terrassement en tranchée", f"{nf(C['exc_orig'], 1)} m³ (tranchées + local)", f"{nf(C['exc_new'], 1)} m³ (la fosse est dans la fouille du bassin)", pct(C["exc_orig"], C["exc_new"])),
        ("Béton des ouvrages techniques", f"{nf(C['conc_orig'])} m³ (local)", f"{nf(C['conc_new'])} m³ BA + {nf(C['lean'])} m³ de gros béton", pct(C["conc_orig"], C["conc_new"]) + " de BA"),
        ("Entretien du filtre", f"{B.OPS['backwash_n']} contre-lavages par an ({nf(tr[3][2], 0)} h)", f"{B.OPS['clean_n']} nettoyages de cartouche par an ({nf(tr[3][3], 0)} h)", "accès par la trappe au lieu d'une porte"),
        ("Impact visuel", "un volume bâti dans le jardin NO", "une trappe au niveau du dallage ; la cascade devient un élément d'architecture", "jardin NO libre"),
        ("Coût d'installation (DH HT)", f"{n0(SP['orig'])} (périmètre) - {n0(C['total_orig'])} (total)", f"{n0(SP['new'])} (périmètre) - {n0(C['total_new'])} (total)", f"{sgn(C['total_new'] - C['total_orig'])} DH HT ({pct(C['total_orig'], C['total_new'])})"),
        ("Coût d'exploitation (DH / an)", n0(OC["tot_old"]), n0(OC["tot_new"]), f"{sgn(OC['tot_new'] - OC['tot_old'])} DH / an"),
    ]
    o_rows, n_rows = B.scope_compare()
    det_o = "".join(f"<tr><td class='mono'>{c}</td><td>{esc(build.decfr(d))}</td><td class='num'>{esc(nf(q, 1) if q % 1 else money(q))} {u}</td><td class='num'>{money(a)}</td></tr>" for c, d, u, q, pu, a in o_rows)
    det_n = "".join(f"<tr{' class=add' if c in B.ADDED else ''}><td class='mono'>{c}</td><td>{esc(build.decfr(d))}</td><td class='num'>{esc(nf(q, 1) if q % 1 else money(q))} {u}</td><td class='num'>{money(a)}</td></tr>" for c, d, u, q, pu, a in n_rows)
    ops = "".join(f"<tr><th>{esc(r[0])}</th><td class='num'>{'' if r[2] is None else esc(nf(r[2], 1)) + ' ' + esc(r[4])}</td><td class='num'>{'' if r[3] is None else esc(nf(r[3], 1)) + ' ' + esc(r[4])}</td>"
                  f"<td class='num'>{money(round(r[5]))}</td><td class='num'>{money(round(r[6]))}</td></tr>" for r in tr)
    o = B.OPS
    like = SP["like"] - SP["orig"]
    pay = like / (OC["tot_old"] - OC["tot_new"]) if OC["tot_old"] > OC["tot_new"] else 0
    return f'''<section class="blk" id="comparaison">
  <h2><span class="sn">06</span>Comparaison indice E / variante B</h2>
  <p class="lead">{fr("Toutes les valeurs ci-dessous sont calculées sur les deux modèles, avec les mêmes prix unitaires et les mêmes hypothèses. Aucune économie n'est supposée.")}</p>
  {tbl(("Critère", "Original (indice E)", "Variante B (indice F)", "Écart"), rows)}
  <p class="note">{ic("scale-balanced")}<span>{fr(f"Le local technique n'est pas remplacé par rien : une fosse étanche sous le niveau de l'eau, sa trappe A15 et la double étanchéité coûtent presque autant que le local. À périmètre égal, la variante B coûte {money(round(like))} DH HT de plus que l'indice E. Avec la cascade, la borne et la conduite de rejet que vous avez demandées ({money(round(SP['added']))} DH HT), l'écart total est de {money(round(C['total_new'] - C['total_orig']))} DH HT. L'exploitation coûte {money(round(OC['tot_old'] - OC['tot_new']))} DH de moins par an, ce qui rembourse l'écart à périmètre égal en {nf(pay, 1)} ans. Les gains sont ailleurs : plus de bâtiment dans le jardin, des canalisations plus courtes, plus d'eau de contre-lavage, et un bassin plus silencieux.")}</span></p>
  <div class="two">
    <div><h3>{ic("calculator")}Périmètre modifié - indice E</h3><div class="tbl"><table class="dqe"><thead><tr><th>N°</th><th>Ouvrage</th><th class="num">Qté</th><th class="num">Montant</th></tr></thead><tbody>{det_o}
      <tr class="sub"><td colspan="3">Total</td><td class="num">{money(SP['orig'])}</td></tr></tbody></table></div></div>
    <div><h3>{ic("calculator")}Périmètre modifié - variante B</h3><div class="tbl"><table class="dqe"><thead><tr><th>N°</th><th>Ouvrage</th><th class="num">Qté</th><th class="num">Montant</th></tr></thead><tbody>{det_n}
      <tr class="sub"><td colspan="3">Total (dont ajouts demandés, en vert : {money(SP['added'])})</td><td class="num">{money(SP['new'])}</td></tr></tbody></table></div></div>
  </div>
  <h3>{ic("bolt")}Coût d'exploitation par an</h3>
  <div class="tbl"><table><thead><tr><th>Poste</th><th class="num">Quantité E</th><th class="num">Quantité B</th><th class="num">DH / an E</th><th class="num">DH / an B</th></tr></thead><tbody>{ops}
    <tr class="vol-tot"><th>Total</th><td></td><td></td><td class="num">{money(round(OC['tot_old']))}</td><td class="num">{money(round(OC['tot_new']))}</td></tr></tbody></table></div>
  <p class="mute small">{fr(f"Hypothèses communes : filtration {o['days_summer']} jours × {o['h_summer']} h et {o['days_winter']} jours × {o['h_winter']} h ({OC['hours']} h/an) ; électricité {nf(o['tariff'])} DH/kWh ; rendement global de la pompe {nf(R['eta'])} ; HMT moyennes {nf(H_ORIG)} et {nf(H_NEW)} mCE ; eau à {o['water_price']} DH/m³ (prix du camion-citerne, article 7.01) ; contre-lavage {nf(o['backwash_m3'], 1)} m³ (3 min de lavage + 1 min de rinçage à {PUMP_FLOW} m³/h), {o['backwash_n']} fois par an ; sable {o['sand_price']} DH tous les {o['sand_years']} ans ; cartouche {o['cartridge_price']} DH tous les {o['cartridge_years']} ans. Remplacez ces valeurs par vos prix réels : l'écart change, la méthode reste.")}</p>
</section>'''


def sec_equipment():
    rows = [
        ("Local technique 2,40 × 2,00", "supprimé", "remplacé par la fosse sous trappe", "-"),
        ("Filtre à sable + vanne 6 voies", "supprimé", "trop haut et trop large pour la fosse, contre-lavages", "-"),
        ("Bondes de fond BF1-BF2", "supprimées", "remplacées par le puisard et sa grille 800 × 600", "-"),
        ("Prise balai PB", "supprimée", "aspiration manuelle par la plaque du skimmer, ou robot (option)", "-"),
        ("Buses R1-R4 et boucle Ø63", "supprimées", "remplacées par RA1-RA2 et la cascade", "-"),
        ("Pompe 12 m³/h vitesse variable", "conservée", "même débit ; hauteur demandée 9 mCE au lieu de 10", "panier chaque semaine"),
        ("Skimmers SK1-SK2", "conservés", "écrémage de surface, 1 pour 25 m²", "paniers 2 fois par semaine"),
        ("Projecteurs P1-P3, échelle", "conservés", "inchangés", "joint de lampe à chaque ouverture"),
        ("Coffret piscine", "déplacé", "en façade, hors volumes ; ajout de KM1 et des sécurités 24 V", "test du DDR chaque mois"),
        ("Puisard + grille PG", "ajouté", "aspiration de fond sans risque de coincement", "contrôle à chaque vidange"),
        ("Fosse FT + trappe TR", "ajoutées", "loge les équipements, accès à clé", "vérins et joint chaque année"),
        ("Filtre à cartouche", "ajouté", "compact, sans contre-lavage", "lavage au jet, cartouche tous les 2 ans"),
        ("Cascade CAS + buses RA1-RA2", "ajoutées", "retour architectural (A1 + A2)", "détartrer la lame 2 fois par an"),
        ("Borne de contrôle + circuit B", "ajoutés", "rejet contrôlé vers le verger", "casse-vide vérifié avant chaque rejet"),
    ]
    return f'''<section class="blk" id="equip">
  <h2><span class="sn">07</span>Équipements supprimés, conservés et ajoutés</h2>
  {tbl(("Équipement", "Statut", "Pourquoi", "Entretien"), rows)}
  <p class="mute small">{fr("La nomenclature complète (quantités, spécifications, emplacements, coûts) est sur la planche VB-10.")}</p>
</section>'''


def sec_points():
    lay = [("Membrane ciment flexible 2 couches", "étanchéité du bassin", "faces mouillées, puisard, face de la cascade"),
           ("Enduit hydrofuge", "support régulier", "sous la membrane"),
           ("Béton B25 + hydrofuge", "structure, non considérée comme étanche", "radier, voiles, caisson, fosse"),
           ("Mosaïque + joint époxy", "finition, n'étanche pas", "sur la membrane"),
           ("Cristallin 2 couches", "étanchéité de la fosse, côté sec", "faces intérieures de la fosse"),
           ("Membrane bitumineuse + drain", "étanchéité de la fosse, côté terre", "faces extérieures et sous-face"),
           ("Joints hydrogonflants, fourreaux à collerette", "continuité", "reprises de bétonnage et traversées")]
    rej = [("Chlore libre", "< 0,1 mg/L", "arrêter le chlore 5 à 7 jours, ou neutraliser"),
           ("pH", "6,5 à 8,5", "corriger avant le rejet"),
           ("Sel, algicide, floculant, cuivre", "aucun", "puits perdu ou évacuation autorisée"),
           ("Débit", f"≤ {nf(B.Q_GARDEN, 0)} m³/h, sur plusieurs jours", "arrêter dès qu'une flaque se forme"),
           ("Destination", "verger NO / NE seulement", "jamais vers le chemin ni les voisins")]
    el = "".join(f"<li><b>{esc(a)}.</b> {esc(b)}</li>" for a, b in build.ELEC)
    return f'''<section class="blk" id="points">
  <h2><span class="sn">08</span>Étanchéité, électricité et rejet</h2>
  <h3>{ic("water")}Quelle couche étanche</h3>
  {tbl(("Couche", "Rôle", "Où"), lay)}
  <div class="two">
    <div class="spec"><h3>{ic("bolt")}Concept de sécurité électrique</h3><ul>{el}</ul>
      <p class="note">{ic("triangle-exclamation")}<span>{fr("Conformité non vérifiée. Ce concept reprend les principes de la NF C 15-100 section 702 et de la CEI 60364-7-702 ; un électricien qualifié doit le valider avec les fiches des matériels achetés, puis réceptionner l'installation.")}</span></p></div>
    <div class="spec"><h3>{ic("seedling")}Rejet contrôlé vers le jardin</h3>
      {tbl(("Paramètre", "Seuil", "Sinon"), rej)}
      <ul>
        <li>{fr("Le circuit B part après le filtre : l'eau rejetée est filtrée. Contrôle au robinet RP de la borne avant d'ouvrir V3.")}</li>
        <li>{fr(f"Le verger est plus bas que le bassin : sans casse-vide, le bassin se viderait seul par siphonnage. Le casse-vide est au point haut ±0,00, soit {nf(-LV['water'])} m au-dessus de l'eau.")}</li>
        <li>{fr("Vidange totale seulement de mai à octobre : un bassin vide en saison des pluies peut se soulever (voir PL-05).")}</li>
      </ul></div>
  </div>
</section>'''


EXTRA_CSS = """
.flow{display:grid;gap:10px;border:1px solid var(--rule);background:var(--panel);padding:14px 16px}
.flow-l{font:600 11.5px/1 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)} .flow-l.red{color:var(--accent)}
.chips{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:8px}
.chip{border:1px solid var(--ink);background:var(--sheet);padding:8px 10px;display:grid;gap:2px;min-width:0}
.chip b{font:700 12.5px/1.25 var(--f-disp)} .chip span{font-size:12.5px;color:var(--ink-2)}
.chip.new{border-color:var(--accent)} .chip.new b{color:var(--accent)}
.flow-a{font-size:20px;color:var(--accent);margin:0} .flow-k{font:800 17px/1.3 var(--f-disp);color:var(--accent);display:flex;gap:8px;align-items:center}
.losses{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:12px}
.loss{display:grid;gap:6px;min-width:0} .loss h4{margin:0;font:700 14px/1.3 var(--f-disp);display:flex;justify-content:space-between;gap:8px}
.loss td{font-size:13px}
tr.add td{background:#eef7ee}
"""


def page_b(objs):
    html_ = build.page(objs)

    def rep(a, b, n=1):
        nonlocal html_
        assert html_.count(a) == n, (a[:80], html_.count(a))
        html_ = html_.replace(a, b)
    rep("<title>Piscine et jardins Gharsa Foquiya</title>", "<title>Piscine sans local technique</title>")
    rep(f"Dossier d'exécution de la piscine et des jardins, Douar Ghanem, Tanger-Assilah - AbodyStudio Limited, v{VERSION}",
        f"Variante B de la piscine (sans local technique), Douar Ghanem, Tanger-Assilah - AbodyStudio Limited, v{VERSION}")
    rep("<h1>Piscine et jardins, terrain Gharsa Foquiya</h1>", "<h1>Piscine sans local technique, terrain Gharsa Foquiya</h1>")
    rep(f"Dossier d'exécution - indice {INDICE} - v{VERSION}</p>", f"Variante B - indice {INDICE} - v{VERSION}</p>")
    lead_old = fr("Bassin en béton armé de 10 × 5 m, implanté à 5,00 m devant la villa existante et centré sur sa façade de 12 m, avec l'aménagement des jardins autour. Plans établis selon l'usage marocain : cartouche, cotes en mètres, niveaux rapportés au ±0,00 du sol fini du rez-de-chaussée.")
    rep(lead_old, fr("Même bassin que l'indice E (v1.3.1) : 10 × 5 m, 5,00 m devant la villa, mêmes niveaux, même profil, même structure. Le système hydraulique est entièrement repensé : plus de local technique extérieur, une fosse sèche sous trappe au grand fond, une pompe, un filtre à cartouche, un retour par cascade et un rejet contrôlé vers le jardin."))
    rep(fr("Villa existante avec l'escalier extérieur côté allée et l'ancien coffret de filtration. Le nouveau local technique se place côté NO."),
        fr("Villa existante avec l'escalier extérieur côté allée et l'ancien coffret de filtration. Dans cette variante, aucun local technique : la fosse est sous le dallage, côté NO."))
    rep(fr("Six planches A3. En rouge : constructions neuves ; hachuré gris : villa existante ; tirets jaunes : piscine Intex à déposer. Touchez « Agrandir » pour lire une planche en pleine taille. Les mêmes planches sont dans le zip en fichiers SVG, imprimables en A3 à 100 % aux échelles indiquées."),
        fr("Treize planches A3 : VB-01 à VB-10 pour la variante, puis PL-01, PL-02 et PL-05 mis à jour. En rouge : ouvrages neufs ; tirets rouges : fosse enterrée sous le dallage. Touchez « Agrandir » pour lire une planche en pleine taille. Les mêmes planches sont dans le zip en fichiers SVG, imprimables en A3 à 100 % aux échelles indiquées."))
    # renumber the existing sections after the inserted ones
    sec_ids = ["spec", "hyd", "seq", "dqe", "planning", "safety", "gloss", "verify"]
    for i, sid in enumerate(sec_ids):
        html_ = re.sub(rf'(<section class="blk" id="{sid}">\s*<h2><span class="sn">)\d+(</span>)', rf"\g<1>{i + 9:02d}\2", html_)
    rep('<section class="blk" id="plans">\n  <h2><span class="sn">03</span>Plans</h2>', '<section class="blk" id="plans">\n  <h2><span class="sn">04</span>Plans</h2>')
    plans_end = html_.index('<section class="blk" id="spec">')
    html_ = html_[:plans_end] + sec_calc() + sec_compare() + sec_equipment() + sec_points() + html_[plans_end:]
    fit_start = html_.index('<section class="blk" id="plans">')
    html_ = html_[:fit_start] + sec_principle() + html_[fit_start:]
    rep('  <li><a href="#plans">Plans</a></li>', '  <li><a href="#principe">Principe de la variante</a></li>\n  <li><a href="#plans">Plans</a></li>')
    rep('  <li><a href="#spec">Descriptif technique</a></li>',
        '  <li><a href="#calc">Calculs hydrauliques</a></li>\n  <li><a href="#comparaison">Comparaison E / B</a></li>\n  <li><a href="#equip">Équipements</a></li>\n'
        '  <li><a href="#points">Étanchéité, électricité, rejet</a></li>\n  <li><a href="#spec">Descriptif technique</a></li>')
    # safety and maintenance texts that referred to the technical room / sand filter
    rep(fr("Deux bondes de fond anti-vortex, margelles et plage antidérapantes, marquage des profondeurs et « Plongeon interdit » (1,80 m ne suffit pas pour plonger)."),
        fr("Grille d'aspiration de 800 × 600 vissée sur le puisard : plus grande qu'un corps, elle ne peut pas retenir une personne. Margelles et plage antidérapantes, marquage des profondeurs et « Plongeon interdit » (1,80 m ne suffit pas pour plonger, la cascade n'est pas un plongeoir)."))
    rep(fr("Gardez les poules clôturées à au moins 8 m de l'eau, et les produits chimiques dans un coffre fermé à clé dans le local technique."),
        fr("Gardez les poules clôturées à au moins 8 m de l'eau. Produits chimiques dans un coffre fermé à clé dans la villa ou la remise, jamais dans la fosse (les vapeurs de chlore rongent le moteur). La trappe reste fermée à clé."))
    rep(fr("Contre-lavage quand le manomètre monte de 0,3 à 0,5 bar au-dessus de la pression du filtre propre. Sable à changer tous les 5 à 6 ans."),
        fr("Cartouche : la laver au jet quand le manomètre monte de 0,5 bar au-dessus de la pression du filtre propre ; la remplacer tous les 2 ans (une rechange est fournie). Avant d'ouvrir le préfiltre ou le filtre : position E, sinon la fosse se remplit."))
    rep(fr("pH 7,2 à 7,6. Chlore libre 1 à 3 mg/L, ou sel 4 g/L avec électrolyseur. TAC 80 à 120 mg/L."),
        fr("pH 7,2 à 7,6. Chlore libre 1 à 3 mg/L. TAC 80 à 120 mg/L. Pas d'électrolyseur au sel : l'eau doit pouvoir aller au verger. La cascade fait monter le pH : contrôlez-le plus souvent quand elle tourne."))
    rep(fr("Ce dossier est un plan d'exécution de principe. Le béton armé est prédimensionné selon les règles BAEL 91 mod. 99 ; le RPS 2000 (version 2011) reste à appliquer. Un bureau d'études agréé (BET) doit vérifier et viser le radier, les voiles et le local technique avant le démarrage, et un électricien qualifié doit réceptionner l'installation."),
        fr("Ce dossier est un plan d'exécution de principe. Le béton armé est prédimensionné selon les règles BAEL 91 mod. 99 ; le RPS 2000 (version 2011) reste à appliquer. Un bureau d'études agréé (BET) doit vérifier et viser le radier, les voiles, le puisard et la fosse avant le démarrage. Le concept électrique n'est pas vérifié pour la conformité : un électricien qualifié doit le valider puis réceptionner l'installation."))
    html_ = html_.replace("@media (prefers-reduced-motion:reduce)", EXTRA_CSS + "@media (prefers-reduced-motion:reduce)", 1)
    return html_


def main():
    objs = [f() for f in SB.SHEET_FUNCS]
    dist = os.path.join(ROOT, "dist", f"v{VERSION}")
    if os.path.isdir(dist):
        shutil.rmtree(dist)
    os.makedirs(os.path.join(dist, "img"))
    os.makedirs(os.path.join(dist, "plans-svg"))
    SH.SVG_CSS = build.SVG_CSS
    body = page_b(objs)
    with open(os.path.join(dist, "index.body.html"), "w") as fh:
        fh.write(body)
    with open(os.path.join(dist, "index.html"), "w") as fh:
        fh.write('<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
                 '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                 f'<meta name="author" content="{AUTHOR["name"]}"></head><body>\n' + body + "\n</body></html>\n")
    for f in os.listdir(os.path.join(ROOT, "assets", "photos")):
        shutil.copy(os.path.join(ROOT, "assets", "photos", f), os.path.join(dist, "img", f))
    gdir = os.path.join(ROOT, "assets", "gallery")
    for f in sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []:
        if f.lower().rsplit(".", 1)[-1] in ("png", "jpg", "jpeg", "webp"):
            shutil.copy(os.path.join(gdir, f), os.path.join(dist, "img", f))
    fonts = ('<style>@import url("https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@400;600;700'
             '&amp;family=Cairo:wght@600&amp;display=swap");</style>')
    for (num, fr_, en, sc), o in zip(SB.VB_SHEETS, objs):
        svg = o.svg(o.title, standalone=True).replace("<style>", "<style>" + build.LIGHT_SVG_VARS).replace("<defs>", fonts + "<defs>", 1)
        slug = unicodedata.normalize("NFKD", fr_.split(" - ")[0].split(" : ")[0]).encode("ascii", "ignore").decode()
        name = f"{num}_{slug.replace(' ', '-').replace(chr(39), '')}.svg"
        with open(os.path.join(dist, "plans-svg", name), "w") as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
    readme = f"""Gharsa Foquiya - Piscine - Variante B : sans local technique
Version {VERSION} (indice {INDICE}) - {DATE}
Même bassin que l'indice E (v1.3.1) ; système hydraulique entièrement repensé.
Conception : {AUTHOR['name']} - {AUTHOR['url']} - {AUTHOR['email']} - WhatsApp {AUTHOR['whatsapp']}
Exécution : {CONTRACTOR['name']} - {CONTRACTOR['form']} - RC {CONTRACTOR['rc']} {CONTRACTOR['tribunal']} - ICE {CONTRACTOR['ice']}
            {CONTRACTOR['address']} - Tél. {CONTRACTOR['phones']} - {CONTRACTOR['emails']}

index.html        Dossier : principe, plans, calculs hydrauliques, comparaison E / B, équipements,
                  étanchéité, électricité, rejet, descriptif, phasage, devis, planning, lexique
plans-svg/        Planches VB-01 à VB-10, PL-01, PL-02, PL-05 (format A3, imprimer à 100 %)
img/              Photos du site + cover.png et image1.png, image2.png... (galerie) :
                  déposez-les dans img/, ils s'affichent automatiquement à l'ouverture de index.html

Ouvrir index.html dans un navigateur (connexion internet pour les polices).
Concept électrique non vérifié pour la conformité : à valider par un électricien qualifié.
"""
    with open(os.path.join(dist, "LISEZMOI.txt"), "w") as fh:
        fh.write(readme)
    rel = os.path.join(os.path.dirname(ROOT), "releases")
    os.makedirs(rel, exist_ok=True)
    zpath = os.path.join(rel, ZIP_NAME)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fn in os.walk(dist):
            for f in sorted(fn):
                if f == "index.body.html":
                    continue
                p = os.path.join(dp, f)
                z.write(p, os.path.join(f"Piscine-Variante-B_v{VERSION}", os.path.relpath(p, dist)))
    print("built", dist, "zip", zpath, os.path.getsize(zpath))


if __name__ == "__main__":
    main()
