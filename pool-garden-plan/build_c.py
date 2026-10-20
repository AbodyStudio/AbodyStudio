"""Construit la variante C (pompe au puisard, deux tubes) : page HTML, planches SVG, archive zip.

Même bassin que l'indice E (v1.3.1). Ni local technique, ni filtre, ni skimmer : une pompe 24 V au
puisard du grand fond, sous une cage, et deux tubes (tube 1 vers le jardin, tube 2 vers la cascade).
Author: AbodyStudio Limited - https://abodystudio.com/
Usage : python3 build_c.py
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
import variant_c as VC  # noqa: E402

DATE = "20/10/2026"
model.VERSION, model.INDICE, model.DATE = VC.VERSION, VC.INDICE, DATE

import sheets as SH  # noqa: E402
import sheets_c as SC  # noqa: E402
import build  # noqa: E402
from build import esc, fr, nf, money, hm, ic, NB  # noqa: E402
from model import Q, LV, POOL_L, POOL_W, WATER_SHALLOW, WATER_DEEP, AUTHOR, CONTRACTOR, hu  # noqa: E402

VERSION, INDICE = VC.VERSION, VC.INDICE
ZIP_NAME = f"AbodyStudio_Gharsa-Foquiya_Piscine-Sans-Local-Technique_v{VERSION}.zip"
R, PC, CG, RV, AL = VC.R, VC.PUMP_C, VC.CAGE, VC.RV, VC.AL
L = VC.L
DIST_AL = model.POOL["u0"] - AL["u"]

# ---------------------------------------------------------------------------
# Wiring: variant sheets, estimate, cartouche
# ---------------------------------------------------------------------------
SH.SHEETS = SC.VC_SHEETS
SH.VARIANT = SC.HOOKS
SH.FRAME_SUB = VC.SUBTITLE
build.SHEETS = SC.VC_SHEETS
build.dqe = VC.dqe_c
build.ICONS["solid"] += ["arrow-down", "plug", "ban", "scale-balanced", "toolbox", "gauge-high", "droplet", "circle-plus", "lock", "recycle"]

CC = VC.compare()


def n0(x):
    return money(round(x))


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
        ("Local technique", "aucun"),
        ("Pompe", f"24 V au puisard - {nf(VC.Q_C, 0)} m³/h"),
        ("Tubes", "1 jardin - 2 cascade"),
    ]
    return "".join(f"<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>" for a, b in rows)


build.facts = facts

build.HYD = [
    ("Pompe", f"Pompe de forage 4\" en {VC.U_DC:.0f} V CC (TBTS), Ø{PC['D'] * 1000:.0f} × {nf(PC['L'])} m, même forme que la pompe du propriétaire, couchée dans le puisard du grand fond sous une cage inox perforée ; {nf(VC.Q_C, 0)} m³/h à {PC['head']} mCE (cascade) et {nf(VC.Q_GARDEN, 0)} m³/h à {PC['head_1']} mCE (fin de vidange)"),
    ("Puisard et cage", f"Puisard {nf(CG['L'])} × {nf(CG['W'])} × {nf(VC.PIT['depth'])} m au point le plus bas, fond {nf(VC.PIT['floor'])} ; cage inox 316L au ras du fond, trous Ø8 au pas de 12 mm ({CG['open_ratio'] * 100:.0f} % de vide), plus grande qu'un corps"),
    ("Tube 1", f"PEHD Ø50, {nf(L['t1'], 1)} m, du regard RV au puits perdu du verger : vidange et arrosage, vanne V1"),
    ("Tube 2", f"PVC PN16 Ø63, {nf(L['t2'], 1)} m, du regard RV au mur de cascade : la lame 600 × 6 mm renvoie l'eau au bassin, vanne V2"),
    ("Regard RV", f"{nf(RV['a'])} × {nf(RV['a'])} × {nf(RV['depth'])} m, couvercle au ras du sol, à {nf(model.POOL['u0'] - RV['u'])} m du bassin : té, V1, V2, raccords union"),
    ("Filtration", "Aucune : ni filtre ni skimmer, à la demande du propriétaire. Options sans toucher au bassin : filtre à cartouche sur le tube 2 dans le mur de cascade, ou robot sans fil à filtre intégré"),
    ("Traitement", "Chlore (diffuseur flottant ou dosage manuel) et correction du pH ; pas d'électrolyseur au sel : l'eau doit pouvoir aller au verger"),
    ("Canalisations", f"PVC PN16 Ø63 : {nf(R['pipes']['d63'], 1)} ml (T0 et tube 2) ; PEHD Ø50 : {nf(R['pipes']['pehd'], 1)} ml (tube 1). Essai de pression 24 h avant remblai"),
]
build.ELEC = [
    ("Alimentation", f"Départ dédié 16 A au TGBT de la villa, câble 3G2,5 sous TPC jusqu'au boîtier AL, {nf(L['cable'], 1)} m"),
    ("Boîtier AL", f"Le seul boîtier : IP65, fermé à clé, sur poteau à {nf(DIST_AL)} m du bassin, hors des volumes 0, 1 et 2 ; interrupteur I0 cadenassable, DDR 30 mA type A, disjoncteurs, horloge, parafoudre"),
    ("Pompe (volume 0)", f"{VC.U_DC:.0f} V CC par une alimentation de sécurité NF EN 61558-2-6 : TBTS, seule tension admise dans l'eau. Câble plat 2 × {PC['cable_s']:g} mm² d'un seul tenant jusqu'à AL, sans boîte de jonction ; chute de tension {nf(R['cable']['drop_pct'], 1)} %"),
    ("Éclairage", "3 projecteurs LED 12 V 30 W par transformateur de sécurité dans AL. Les bornes de jardin à moins de 3,50 m du bassin passent en TBTS 12 V"),
    ("Liaison équipotentielle", "Ferraillages du bassin et du puisard, cadre et cage inox, lame de la cascade et échelle reliés à la LEL et au piquet de terre"),
    ("Conformité", "Concept établi sur les principes de la NF C 15-100 section 702 / CEI 60364-7-702, non vérifié : à valider et réceptionner par un électricien qualifié"),
]

build.SPECS = [
    ("trowel-bricks", "Lot 1 - Terrassements", [
        "Mêmes terrassements que l'indice E pour le bassin, sans local technique. La fouille du grand fond est surcreusée au droit du puisard.",
        f"Fouilles en tranchée : {nf(R['trench'], 1)} m³ pour le tube 2 (côté NE), le tube 1 (vers le verger) et les câbles.",
        "Remblai seulement après l'essai d'étanchéité et l'essai de pression des canalisations.",
    ]),
    ("helmet-safety", "Lot 2 - Béton armé", [
        "Bassin identique à l'indice E (radier, voiles, chaînage, escalier, aciers repères 1 à 13).",
        f"Caisson du puisard {R['caisson'][0]:.2f} × {R['caisson'][1]:.2f} × {R['caisson'][2]:.2f} m coulé avec le radier ({nf(R['c_pit'])} m³), chevêtres HA12 autour de l'ouverture, cadre de la cage scellé.",
        "Fourreaux à collerette posés avant coulage : sortie T0 et fourreau du câble dans le voile NO.",
        "Mur de cascade : noyau BA de 0,20 m sur le voile SE (repère 17), fourreau du tube 2 vers la chambre de répartition.",
    ]),
    ("water", "Lot 3 - Étanchéité", [
        "Bassin : enduit hydrofuge + ciment flexible 2 couches, continu dans le puisard et remonté sur la face mouillée de la cascade jusqu'à l'arase. La mosaïque est une finition, elle n'étanche pas.",
        "Joints hydrogonflants à toutes les reprises ; bagues hydrogonflantes à toutes les traversées.",
        "Essai d'étanchéité du bassin pendant 7 jours avant remblai.",
    ]),
    ("faucet-drip", "Lot 4 - Hydraulique", [
        f"Pompe {VC.U_DC:.0f} V couchée sur son berceau dans sa chemise de refroidissement Ø150, raccord rapide sur la sortie : elle se sort par ses anneaux, à la perche, sans vider le bassin.",
        f"Cage inox 316L {CG['L'] * 1000:.0f} × {CG['W'] * 1000:.0f} vissée au ras du fond : rien ne dépasse et elle ne peut pas être obstruée par une personne.",
        "Regard RV au ras du sol côté NO : V2 ouverte = cascade, V1 ouverte = jardin. V1 reste fermée hors vidange.",
        "Pas de filtre ni de skimmer : options possibles plus tard (filtre sur le tube 2 dans le mur de cascade, robot sans fil).",
    ]),
]

build.SEQ = [
    ("Préparation", "Relevé et implantation à partir de la façade, comme à l'indice E. Laisser le chlore de la piscine Intex se dissiper 3 à 4 jours, puis la vider dans le verger."),
    ("Terrassement", "Fouille du bassin et surcreusement du puisard au grand fond. Contrôle du fond de forme."),
    ("Fondation", "Hérisson, béton de propreté, lit du drain périphérique ; fond du caisson du puisard."),
    ("Radier et puisard", "Ferraillage du radier et du caisson, chevêtres, cadre de la cage, aciers en L des voiles. <b>Point d'arrêt :</b> réception du ferraillage. Coulage en une fois."),
    ("Voiles", "Joint hydrogonflant, voiles et chaînage avec les fourreaux de T0 et du câble, les niches des projecteurs et l'attente du mur de cascade."),
    ("Cascade et tranchées", "Noyau du mur de cascade ; tranchées du tube 2 (côté NE), du tube 1 (verger) et des câbles ; regard RV."),
    ("Canalisations", "T0, té, V1, V2, tube 1 et tube 2. <b>Point d'arrêt :</b> essai de pression 24 h avant de recouvrir."),
    ("Cure", "21 à 28 jours. Pendant ce temps : fourreaux électriques, poteau et boîtier AL, puits perdu, escalier d'accès."),
    ("Étanchéité", "Bassin, puisard et face de la cascade. <b>Point d'arrêt :</b> essai d'étanchéité de 7 jours, puis remblai."),
    ("Finitions", "Mosaïque et joint époxy, margelles, dallage, couvercle du regard RV, parement et chapeau de la cascade, chambre et lame inox."),
    ("Équipements", f"Cage, chemise et pompe {VC.U_DC:.0f} V, boîtier AL. L'électricien vérifie le DDR, la TBTS et la liaison équipotentielle."),
    ("Essais", "Cascade (V2), puis jardin (V1) ; réglage de V1 pour le débit au verger ; essai de sortie de la pompe à la perche."),
    ("Jardins et mise en eau", "Jardins, éclairage, clôtures ; remplissage par camion-citerne, équilibrage de l'eau, remise au propriétaire de la procédure plastifiée et des clés."),
]

build.GANTT = [
    ("Préparation et implantation", 1, 1), ("Dépose de la piscine Intex", 1, 1), ("Terrassement, fondation, puisard", 2, 1.5),
    ("Radier et caisson du puisard", 3, 1), ("Voiles et chaînage", 4, 1.5), ("Noyau de la cascade, tranchées", 5, 1),
    ("Canalisations et essai de pression", 5, 1.5), ("Cure du béton", 5.5, 3.5), ("Enduit et membrane", 9, 1),
    ("Essai d'étanchéité et remblai", 10, 1), ("Mosaïque, margelles, cascade", 11, 2), ("Plage, caniveau, escalier d'accès", 12, 1.5),
    ("Électricité, cage, pompe", 11, 2), ("Jardins, clôtures", 13, 2), ("Mise en eau et essais", 14, 1),
]

GL = dict(build.GLOSS)
for k in ("Local technique", "Filtre à sable", "Bonde de fond", "Prise balai", "Nourrice (collecteur)", "Skimmer", "Buse de refoulement"):
    GL.pop(k, None)
GL.update({
    "Puisard": "حوض تجميع",
    "Cage de protection": "قفص حماية",
    "Pompe immergée": "مضخة غاطسة",
    "Cascade / lame d'eau": "شلال / شفرة مائية",
    "Regard de vannes": "غرفة الصمامات",
    "Vanne": "صمام",
    "Très basse tension de sécurité": "جهد منخفض جدا للسلامة",
    "Tuyau": "أنبوب",
})
build.GLOSS = list(GL.items())

build.VERIFY = build.VERIFY + [
    f"Fiche de la pompe 24 V réellement achetée : points {nf(VC.Q_C, 0)} m³/h à {PC['head']} mCE et {nf(VC.Q_GARDEN, 0)} m³/h à {PC['head_1']} mCE sur sa courbe, pose horizontale admise, Ø ≤ 100 mm et longueur ≤ {nf(PC['L'])} m, matériaux pour eau chlorée.",
    "Électricité : l'électricien valide le concept (boîtier AL hors volumes, TBTS 24 V et 12 V, DDR, liaison équipotentielle) avant l'achat de la pompe et du boîtier.",
    "Rejet au jardin : vérifier la capacité d'infiltration du verger par un essai à l'eau claire avant la première vidange.",
    "Sans filtre, l'eau se trouble plus vite : décider avant le chantier si l'on ajoute le filtre sur le tube 2 (option) ; le mur de cascade peut le recevoir.",
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
    new = [("BASSIN", "inchangé"), ("UNE POMPE", f"{VC.U_DC:.0f} V, au puisard"), ("UNE CAGE", "inox, au ras du fond"),
           ("TUBE 1", "vers le jardin"), ("TUBE 2", "vers la cascade"), ("UN BOÎTIER", f"AL, à {nf(DIST_AL)} m")]
    chip = lambda a, b, c="": f'<div class="chip{c}"><b>{esc(a)}</b><span>{esc(b)}</span></div>'
    return f'''<section class="blk" id="principe">
  <h2><span class="sn">03</span>Principe : une pompe, deux tubes</h2>
  <p class="lead">{fr("Le bassin de l'indice E ne change pas : dimensions, implantation, niveaux, profil du fond, structure et finitions. Tout le reste est remplacé par votre schéma : une pompe couchée au point le plus bas, sous une cage métallique ajourée, et deux tubes. Le tube 1 envoie l'eau dehors, vers le jardin ; le tube 2 l'envoie vers la cascade, d'où elle retombe dans le bassin.")}</p>
  <div class="flow"><p class="flow-l">Indice E</p><div class="chips">{"".join(chip(a, b) for a, b in orig)}</div>
  <p class="flow-a">{ic("arrow-down")}</p><p class="flow-l red">Variante C</p><div class="chips">{"".join(chip(a, b, " new") for a, b in new)}</div>
  <p class="flow-k">{ic("ban")} Ni local technique, ni filtre, ni skimmer</p></div>
  <div class="two">
    <div class="spec"><h3>{ic("shield-halved")}Ce qui reste en plus de la pompe et des tubes</h3><ul>
      <li>{fr(f"La cage inox au ras du fond : elle laisse entrer l'eau, protège la pompe et ne peut pas retenir une personne ({nf(CG['L'])} × {nf(CG['W'])} m).")}</li>
      <li>{fr(f"Un regard de {nf(RV['a'])} × {nf(RV['a'])} m au ras du sol, côté NO : le té et les deux vannes qui choisissent le tube 1 ou le tube 2.")}</li>
      <li>{fr(f"Le boîtier AL sur un poteau à {nf(DIST_AL)} m du bassin : protection, alimentation de sécurité {VC.U_DC:.0f} V de la pompe et 12 V des projecteurs.")}</li>
    </ul></div>
    <div class="spec"><h3>{ic("circle-check")}Ce qui ne change pas</h3><ul>
      <li>{fr("Bassin 10,00 × 5,00 m centré sur la façade, à 5,00 m de la villa ; margelles à −0,70, eau à −0,85.")}</li>
      <li>{fr(f"Profondeur 0,55 → 1,80 m, rupture de pente à 1,20 m, volume {hu(Q['water_vol']).replace('.', ',')} m³.")}</li>
      <li>{fr("Radier, voiles et chaînage de l'indice E, escalier d'entrée, projecteurs, échelle, plage, jardins, escalier d'accès.")}</li>
    </ul></div>
  </div>
</section>'''


def sec_pump():
    items = SC.pit_items()
    lis = "".join(f"<li>{esc(t_)}</li>" for _, _, t_ in items)
    pos = [("Cascade (usage normal)", "fermée", "ouverte", "tube 2 → cascade → bassin", f"{nf(VC.Q_C, 0)} m³/h"),
           ("Jardin, vidange", "ouverte, réglée", "fermée", "tube 1 → verger, puits perdu", f"{nf(VC.Q_GARDEN, 0)} m³/h"),
           ("Arrêt, entretien", "fermée", "fermée", "pompe arrêtée, boîtier AL coupé", "0")]
    return f'''<section class="blk" id="pompe">
  <h2><span class="sn">00</span>La pompe dans le puisard, sous la cage</h2>
  <p class="lead">{fr(f"La pompe est couchée au point le plus bas du bassin, dans un puisard de {nf(CG['L'])} × {nf(CG['W'])} × {nf(VC.PIT['depth'])} m fermé par une cage inox perforée au ras du fond. L'eau traverse la cage, longe le moteur dans sa chemise et entre par la crépine ; la pompe la renvoie par le tube T0 jusqu'au regard RV, puis vers le tube 1 ou le tube 2.")}</p>
  <p class="note">{ic("triangle-exclamation")}<span>{fr(f"Votre pompe 1 HP 220 V ne doit pas être posée dans l'eau du bassin. Dans l'eau (volume 0), seule la très basse tension de sécurité est admise : 12 V alternatif ou 30 V continu au plus, produite par une source de sécurité placée hors des volumes. Un défaut d'isolement d'un moteur 220 V dans le bassin peut électrocuter un baigneur, même avec un différentiel. La pompe du puisard a donc la même forme et la même longueur que la vôtre ({nf(PC['L'])} m, 4 pouces, tête laiton, crépine, câble plat bleu), avec un moteur {VC.U_DC:.0f} V CC alimenté par le boîtier AL à {nf(DIST_AL)} m du bassin. Votre pompe 220 V reste utile dans le puits du terrain. Conformité non vérifiée : un électricien qualifié doit valider ce concept.")}</span></p>
  <figure class="plan" id="fig-pit"><figcaption><span class="pl-n mono">VC-01</span><span class="pl-t">Puisard, cage et pompe, vue rapprochée<small>écorché sans échelle ; cage représentée soulevée</small></span>
  <button type="button" class="zoom" aria-pressed="false" aria-label="Agrandir la vue du puisard">{ic("expand")}<span>Agrandir</span></button></figcaption>
  <div class="plan-scroll">{SC.pit_figure()}</div></figure>
  <ol class="callouts">{lis}</ol>
  <h3>{ic("toolbox")}La pompe : même forme et même longueur que la vôtre</h3>
  <figure class="plan"><figcaption><span class="pl-n mono">VC-05</span><span class="pl-t">Pompe de forage 4" {VC.U_DC:.0f} V CC, couchée<small>élévation ; cotes et détails sur VC-05</small></span></figcaption>
  <div class="plan-scroll">{SC.pump_figure()}</div></figure>
  <h3>{ic("faucet-drip")}Les deux tubes</h3>
  <figure class="plan"><div class="plan-scroll">{SC.principle_figure()}</div></figure>
  {tbl(("Usage", "V1 (tube 1)", "V2 (tube 2)", "L'eau va vers", "Débit"), pos, num=(4,))}
  <p class="mute small">{fr(f"V1 reste fermée hors vidange : la sortie du puits perdu est plus basse que l'eau du bassin, le tube 1 se viderait seul par gravité. Le bassin se vide entièrement par le tube 1 en {nf(R['drain_h'], 1)} h, la pompe étant au point le plus bas.")}</p>
</section>'''


def loss_table(key, title, q):
    rows, tot = R[key]
    trs = "".join(f"<tr><td>{esc(n)}</td><td class='num'>{nf(v)}</td></tr>" for n, v in rows)
    return (f'<div class="loss"><h4>{esc(title)} <span class="mono">{nf(q, 0)}{NB}m³/h</span></h4><div class="tbl"><table><tbody>{trs}'
            f'<tr class="vol-tot"><th>HMT</th><td class="num">{nf(tot)}{NB}mCE</td></tr></tbody></table></div></div>')


def sec_calc():
    data = [
        ("Volume d'eau", f"{hu(Q['water_vol']).replace('.', ',')} m³"),
        ("Débit vers la cascade", f"{nf(VC.Q_C, 0)} m³/h : tout le volume passe par la cascade en {hm(Q['water_vol'] / VC.Q_C)}"),
        ("Cage du puisard", f"{nf(CG['L'])} × {nf(CG['W'])} m, {CG['open_ratio'] * 100:.0f} % de vide : {nf(R['cage_open'], 3)} m² de passage, {nf(R['v_cage'], 4)} m/s au travers (limite usuelle 0,5 m/s)"),
        ("Cage non obstruable par un corps", f"plus grande que 457 × 584 mm (gabarit d'une personne couchée) : {'oui' if R['unblockable'] else 'non'}"),
        ("Refroidissement du moteur", f"chemise Ø{PC['sleeve_D'] * 1000:.0f} : {nf(R['v_sleeve'])} m/s le long du moteur (minimum usuel 0,08 m/s)"),
        ("Vitesses dans les tubes", f"T0 et tube 2 Ø63 : {nf(R['v_t0'])} m/s ; flexible 1-1/4\" : {nf(R['v_hose'])} m/s ; tube 1 Ø50 : {nf(R['v_t1'])} m/s"),
        ("Lame d'eau 600 × 6 mm", f"{nf(R['slot_q_per_m'])} L/s par mètre (minimum usuel {nf(B.SHEET_MIN, 1)} L/s/m) : lame continue {'oui' if R['sheet_ok'] else 'non'}"),
        ("Pompe retenue", f"{nf(VC.Q_C, 0)} m³/h à {PC['head']} mCE et {nf(VC.Q_GARDEN, 0)} m³/h à {PC['head_1']} mCE, {VC.U_DC:.0f} V CC, Ø{PC['D'] * 1000:.0f} × {nf(PC['L'])} m"),
        ("Puissance", f"hydraulique {n0(R['p_hyd'])} W ; absorbée {n0(R['p1'])} W en cascade, {n0(R['p1_max'])} W au point nominal (rendement {nf(VC.ETA)}, hypothèse)"),
        ("Courant et câble", f"{nf(R['cable']['i_avg'], 1)} A en cascade, {nf(R['i_dc'], 1)} A nominal sous {VC.U_DC:.0f} V ; câble 2 × {R['cable']['s']:g} mm² de {nf(L['pump_cable'], 1)} m : chute {nf(R['cable']['drop_avg_pct'], 1)} % / {nf(R['cable']['drop_pct'], 1)} % (limite 5 %)"),
        ("Vidange complète par le tube 1", f"{nf(R['drain_h'], 1)} h à {nf(VC.Q_GARDEN, 0)} m³/h"),
    ]
    losses = loss_table("tdh_2", "Tube 2 - cascade", VC.Q_C) + loss_table("tdh_1", "Tube 1 - bassin plein", VC.Q_GARDEN) + loss_table("tdh_1_end", "Tube 1 - fin de vidange", VC.Q_GARDEN)
    return f'''<section class="blk" id="calc">
  <h2><span class="sn">05</span>Calculs hydrauliques et électriques</h2>
  <p class="lead">{fr("Pertes de charge calculées par Hazen-Williams (PVC, C = 150) et coefficients de singularités, sur les longueurs mesurées sur les plans. Le courant de la pompe et la section du câble sont calculés au point nominal.")}</p>
  {tbl(("Grandeur", "Valeur"), data)}
  <div class="losses">{losses}</div>
</section>'''


def sec_compare():
    rows = [
        ("Où est la pompe", "local technique extérieur", "fosse sèche sous trappe", "dans le puisard, sous la cage"),
        ("Tension de la pompe", "230 V", "230 V", f"{VC.U_DC:.0f} V CC (TBTS)"),
        ("Ouvrage technique", "local 2,40 × 2,00 m", "fosse étanche sous l'eau + trappe", f"puisard {nf(CG['L'])} × {nf(CG['W'])} m + regard {nf(RV['a'])} × {nf(RV['a'])} m"),
        ("Filtration", "sable Ø600 + vanne 6 voies", "cartouche 13,9 m²", "aucune (option possible)"),
        ("Skimmers", "2", "2", "aucun (option possible)"),
        ("Total général HT du devis (DH)", n0(CC["total_e"]), n0(CC["total_b"]), n0(CC["total_c"])),
        (f"Énergie ({CC['hours']} h de pompe par an, kWh)", n0(CC["e_e"]), n0(CC["e_b"]), n0(CC["e_c"])),
        ("Exploitation calculée (DH / an)", n0(CC["ops_e"]), n0(CC["ops_b"]), n0(CC["ops_c"])),
    ]
    return f'''<section class="blk" id="comparaison">
  <h2><span class="sn">06</span>Comparaison indice E / variante B / variante C</h2>
  <p class="lead">{fr("Mêmes prix unitaires et mêmes hypothèses pour les trois. Aucune économie n'est supposée : tout est calculé sur les trois modèles.")}</p>
  {tbl(("Critère", "Indice E", "Variante B", "Variante C"), rows)}
  <p class="note">{ic("scale-balanced")}<span>{fr(f"La variante C coûte {money(round(CC['total_e'] - CC['total_c']))} DH HT de moins que l'indice E, surtout parce qu'elle n'a ni filtre ni skimmer. Son exploitation ne compte que l'électricité d'une pompe {VC.U_DC:.0f} V : {money(round(CC['ops_c']))} DH par an. Ce qu'elle ne fait pas : nettoyer l'eau. Sans filtre, l'eau se trouble plus vite ; un remplissage complet par camion-citerne coûte {money(round(R['refill']))} DH. Le filtre à cartouche sur le tube 2 reste possible plus tard, dans le mur de cascade (option à {money(11000)} DH HT).")}</span></p>
  <p class="mute small">{fr(f"Hypothèses communes : {CC['hours']} h de pompe par an ; électricité {nf(B.OPS['tariff'])} DH/kWh ; eau à {B.OPS['water_price']} DH/m³ (camion-citerne, article 7.01) ; rendement {nf(VC.ETA)} pour la pompe 24 V. Remplacez ces valeurs par vos prix réels : l'écart change, la méthode reste.")}</p>
</section>'''


def sec_equipment():
    rows = [
        ("Local technique 2,40 × 2,00", "supprimé", "plus rien à loger : la pompe est dans le puisard", "-"),
        ("Filtre à sable + vanne 6 voies", "supprimé", "à votre demande : pas de filtre (option sur le tube 2)", "-"),
        ("Skimmers SK1-SK2", "supprimés", "à votre demande (option : 2 skimmers raccordés au puisard)", "épuisette chaque jour"),
        ("Bondes de fond, prise balai, buses R1-R4", "supprimées", "remplacées par le puisard et la cascade", "-"),
        ("Pompe 230 V", "remplacée", f"pompe de forage {VC.U_DC:.0f} V CC au puisard, même forme que la vôtre", "contrôle annuel, crépine rincée"),
        ("Projecteurs P1-P3, échelle", "conservés", "inchangés ; transformateur 12 V dans AL", "joint de lampe à chaque ouverture"),
        ("Puisard + cage inox", "ajoutés", "aspiration au point bas, sans risque de coincement", "brosser la cage chaque semaine"),
        ("Regard RV (té, V1, V2)", "ajouté", "choix du tube 1 ou du tube 2", "manœuvrer les vannes chaque mois"),
        ("Cascade + lame inox", "ajoutée", "retour de l'eau au bassin (tube 2)", "détartrer la lame 2 fois par an"),
        ("Tube 1 vers le verger", "ajouté", "vidange et arrosage", "contrôle du chlore avant chaque vidange"),
        ("Boîtier AL sur poteau", "ajouté", f"le seul boîtier : protection, {VC.U_DC:.0f} V et 12 V", "test du DDR chaque mois"),
    ]
    return f'''<section class="blk" id="equip">
  <h2><span class="sn">07</span>Équipements supprimés, conservés et ajoutés</h2>
  {tbl(("Équipement", "Statut", "Pourquoi", "Entretien"), rows)}
  <p class="mute small">{fr("La nomenclature complète (quantités, spécifications, emplacements, coûts, entretien sans filtre) est sur la planche VC-08.")}</p>
</section>'''


def sec_points():
    lay = [("Membrane ciment flexible 2 couches", "étanchéité du bassin", "faces mouillées, puisard, face de la cascade"),
           ("Enduit hydrofuge", "support régulier", "sous la membrane"),
           ("Béton B25 + hydrofuge", "structure, non considérée comme étanche", "radier, voiles, caisson du puisard"),
           ("Mosaïque + joint époxy", "finition, n'étanche pas", "sur la membrane"),
           ("Joints hydrogonflants, fourreaux à collerette", "continuité", "reprises de bétonnage et traversées")]
    rej = [("Chlore libre", "< 0,1 mg/L", "arrêter le chlore 5 à 7 jours, ou neutraliser"),
           ("pH", "6,5 à 8,5", "corriger avant le rejet"),
           ("Sel, algicide, floculant, cuivre", "aucun", "puits perdu ou évacuation autorisée"),
           ("Débit", f"≤ {nf(VC.Q_GARDEN, 0)} m³/h, V1 réglée", "arrêter dès qu'une flaque se forme"),
           ("Destination", "verger NO / NE seulement", "jamais vers le chemin ni les voisins")]
    el = "".join(f"<li><b>{esc(a)}.</b> {esc(b)}</li>" for a, b in build.ELEC)
    care = [("Chaque jour", "épuisette sur la surface ; cascade en marche à l'horloge, quelques heures par jour"),
            ("Chaque semaine", "brosser la cage et les parois ; chlore libre 1 à 3 mg/L, pH 7,2 à 7,6"),
            ("Chaque mois", "manœuvrer V1 et V2 ; tester le DDR du boîtier AL"),
            ("Eau trouble", "chlore choc ; si elle ne s'éclaircit pas, vidange par le tube 1 et remplissage"),
            ("Chaque année", "couper AL (I0 cadenassé), déposer la cage, sortir la pompe, rincer sa crépine")]
    return f'''<section class="blk" id="points">
  <h2><span class="sn">08</span>Étanchéité, électricité, vidange et entretien</h2>
  <h3>{ic("water")}Quelle couche étanche</h3>
  {tbl(("Couche", "Rôle", "Où"), lay)}
  <div class="two">
    <div class="spec"><h3>{ic("bolt")}Concept de sécurité électrique</h3><ul>{el}</ul>
      <p class="note">{ic("triangle-exclamation")}<span>{fr("Conformité non vérifiée. Ce concept reprend les principes de la NF C 15-100 section 702 et de la CEI 60364-7-702 ; un électricien qualifié doit le valider avec les fiches des matériels achetés, puis réceptionner l'installation.")}</span></p></div>
    <div class="spec"><h3>{ic("seedling")}Vidange vers le jardin (tube 1)</h3>
      {tbl(("Paramètre", "Seuil", "Sinon"), rej)}
      <ul>
        <li>{fr("V1 reste fermée hors vidange : la sortie du tube 1 est plus basse que l'eau, le bassin se viderait seul par gravité.")}</li>
        <li>{fr("Vidange totale seulement de mai à octobre : un bassin vide en saison des pluies peut se soulever (voir PL-05).")}</li>
      </ul></div>
  </div>
  <h3>{ic("droplet")}Sans filtre : l'entretien à prévoir</h3>
  {tbl(("Quand", "Quoi"), care)}
</section>'''


EXTRA_CSS = """
.plan-scroll .sheet.iso,.plan-scroll .sheet.conn{min-width:0}
.plan.big .plan-scroll .sheet.iso{min-width:1150px}
.callouts{margin:0;padding-left:2.2em;columns:2 260px;column-gap:28px;font-size:14px}
.callouts li{break-inside:avoid;padding:2px 0}
.flow{display:grid;gap:10px;border:1px solid var(--rule);background:var(--panel);padding:14px 16px}
.flow-l{font:600 11.5px/1 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)} .flow-l.red{color:var(--accent)}
.chips{display:grid;grid-template-columns:repeat(auto-fit,minmax(112px,1fr));gap:8px}
.chip{border:1px solid var(--ink);background:var(--sheet);padding:8px 10px;display:grid;gap:2px;min-width:0}
.chip b{font:700 12.5px/1.25 var(--f-disp)} .chip span{font-size:12.5px;color:var(--ink-2)}
.chip.new{border-color:var(--accent)} .chip.new b{color:var(--accent)}
.flow-a{font-size:20px;color:var(--accent);margin:0} .flow-k{font:800 17px/1.3 var(--f-disp);color:var(--accent);display:flex;gap:8px;align-items:center}
.losses{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.loss{display:grid;gap:6px;min-width:0} .loss h4{margin:0;font:700 14px/1.3 var(--f-disp);display:flex;justify-content:space-between;gap:8px}
.loss td{font-size:13px}
"""


def page_c(objs):
    html_ = build.page(objs)

    def rep(a, b, n=1):
        nonlocal html_
        assert html_.count(a) == n, (a[:80], html_.count(a))
        html_ = html_.replace(a, b)
    rep("<title>Piscine et jardins Gharsa Foquiya</title>", "<title>Piscine, pompe et deux tubes</title>")
    rep(f"Dossier d'exécution de la piscine et des jardins, Douar Ghanem, Tanger-Assilah - AbodyStudio Limited, v{VERSION}",
        f"Variante C de la piscine (pompe au puisard, deux tubes), Douar Ghanem, Tanger-Assilah - AbodyStudio Limited, v{VERSION}")
    rep("<h1>Piscine et jardins, terrain Gharsa Foquiya</h1>", "<h1>Piscine : une pompe, deux tubes, terrain Gharsa Foquiya</h1>")
    rep(f"Dossier d'exécution - indice {INDICE} - v{VERSION}</p>", f"Variante C - indice {INDICE} - v{VERSION}</p>")
    lead_old = fr("Bassin en béton armé de 10 × 5 m, implanté à 5,00 m devant la villa existante et centré sur sa façade de 12 m, avec l'aménagement des jardins autour. Plans établis selon l'usage marocain : cartouche, cotes en mètres, niveaux rapportés au ±0,00 du sol fini du rez-de-chaussée.")
    rep(lead_old, fr("Même bassin que l'indice E (v1.3.1) : 10 × 5 m, 5,00 m devant la villa, mêmes niveaux, même profil, même structure. Votre schéma remplace tout le reste : ni local technique, ni filtre, ni skimmer. Une pompe 24 V couchée au point le plus bas sous une cage, un tube vers le jardin et un tube vers la cascade."))
    rep(fr("Villa existante avec l'escalier extérieur côté allée et l'ancien coffret de filtration. Le nouveau local technique se place côté NO."),
        fr("Villa existante avec l'escalier extérieur côté allée et l'ancien coffret de filtration. Dans cette variante, aucun local technique : la pompe est au fond du bassin, sous une cage."))
    rep(fr("Six planches A3. En rouge : constructions neuves ; hachuré gris : villa existante ; tirets jaunes : piscine Intex à déposer. Touchez « Agrandir » pour lire une planche en pleine taille. Les mêmes planches sont dans le zip en fichiers SVG, imprimables en A3 à 100 % aux échelles indiquées."),
        fr("Onze planches A3 : VC-01 à VC-08 pour la variante C, puis PL-01, PL-02 et PL-05 mis à jour. En rouge : ouvrages neufs. Touchez « Agrandir » pour lire une planche en pleine taille. Les mêmes planches sont dans le zip en fichiers SVG, imprimables en A3 à 100 % aux échelles indiquées."))
    fit_at = html_.index('<section class="blk" id="plans">')
    html_ = html_[:fit_at] + sec_principle() + sec_pump() + html_[fit_at:]
    plans_end = html_.index('<section class="blk" id="spec">')
    html_ = html_[:plans_end] + sec_calc() + sec_compare() + sec_equipment() + sec_points() + html_[plans_end:]
    count = iter(range(1, 100))
    html_ = re.sub(r'(<section class="blk" id="[a-z0-9]+">\s*<h2><span class="sn">)\d+(</span>)', lambda m: f"{m.group(1)}{next(count):02d}{m.group(2)}", html_)
    rep('  <li><a href="#plans">Plans</a></li>', '  <li><a href="#principe">Principe : une pompe, deux tubes</a></li>\n  <li><a href="#pompe">La pompe dans le puisard</a></li>\n  <li><a href="#plans">Plans</a></li>')
    rep('  <li><a href="#spec">Descriptif technique</a></li>',
        '  <li><a href="#calc">Calculs</a></li>\n  <li><a href="#comparaison">Comparaison E / B / C</a></li>\n  <li><a href="#equip">Équipements</a></li>\n'
        '  <li><a href="#points">Étanchéité, électricité, entretien</a></li>\n  <li><a href="#spec">Descriptif technique</a></li>')
    rep(fr("Deux bondes de fond anti-vortex, margelles et plage antidérapantes, marquage des profondeurs et « Plongeon interdit » (1,80 m ne suffit pas pour plonger)."),
        fr(f"Cage inox de {nf(CG['L'])} × {nf(CG['W'])} m vissée au ras du fond sur le puisard : plus grande qu'un corps, elle ne peut pas retenir une personne. Margelles et plage antidérapantes, marquage des profondeurs et « Plongeon interdit » (1,80 m ne suffit pas pour plonger, la cascade n'est pas un plongeoir)."))
    rep(fr("Gardez les poules clôturées à au moins 8 m de l'eau, et les produits chimiques dans un coffre fermé à clé dans le local technique."),
        fr("Gardez les poules clôturées à au moins 8 m de l'eau. Produits chimiques dans un coffre fermé à clé dans la villa ou la remise. Le boîtier AL et le regard RV restent fermés à clé."))
    rep(fr("Contre-lavage quand le manomètre monte de 0,3 à 0,5 bar au-dessus de la pression du filtre propre. Sable à changer tous les 5 à 6 ans."),
        fr("Pas de filtre : épuisette chaque jour, brosse sur la cage chaque semaine. Si l'eau se trouble malgré le chlore, vidange par le tube 1 et remplissage, ou ajout du filtre sur le tube 2 (option)."))
    rep(fr("pH 7,2 à 7,6. Chlore libre 1 à 3 mg/L, ou sel 4 g/L avec électrolyseur. TAC 80 à 120 mg/L."),
        fr("pH 7,2 à 7,6. Chlore libre 1 à 3 mg/L. TAC 80 à 120 mg/L. Pas d'électrolyseur au sel : l'eau doit pouvoir aller au verger. La cascade fait monter le pH : contrôlez-le plus souvent quand elle tourne."))
    rep(fr("Ce dossier est un plan d'exécution de principe. Le béton armé est prédimensionné selon les règles BAEL 91 mod. 99 ; le RPS 2000 (version 2011) reste à appliquer. Un bureau d'études agréé (BET) doit vérifier et viser le radier, les voiles et le local technique avant le démarrage, et un électricien qualifié doit réceptionner l'installation."),
        fr("Ce dossier est un plan d'exécution de principe. Le béton armé est prédimensionné selon les règles BAEL 91 mod. 99 ; le RPS 2000 (version 2011) reste à appliquer. Un bureau d'études agréé (BET) doit vérifier et viser le radier, les voiles et le puisard avant le démarrage. Le concept électrique n'est pas vérifié pour la conformité : un électricien qualifié doit le valider puis réceptionner l'installation."))
    rep(fr("Durée de filtration en été : température de l'eau ÷ 2, en heures ; 2 à 4 h par jour en hiver (hivernage actif)."),
        fr("Cascade à l'horloge : quelques heures par jour en été pour brasser l'eau et répartir le chlore, 1 à 2 h par jour en hiver."))
    rep(fr("Chaque semaine : vider les paniers, brosser la ligne d'eau, passer le balai, analyser l'eau."),
        fr("Chaque semaine : brosser la cage du puisard, la ligne d'eau et les parois, analyser l'eau."))
    html_ = html_.replace("@media (prefers-reduced-motion:reduce)", EXTRA_CSS + "@media (prefers-reduced-motion:reduce)", 1)
    return html_


def main():
    objs = [f() for f in SC.SHEET_FUNCS]
    dist = os.path.join(ROOT, "dist", f"v{VERSION}")
    if os.path.isdir(dist):
        shutil.rmtree(dist)
    os.makedirs(os.path.join(dist, "img"))
    os.makedirs(os.path.join(dist, "plans-svg"))
    SH.SVG_CSS = build.SVG_CSS
    body = page_c(objs)
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
    for (num, fr_, en, sc), o in zip(SH.SHEETS, objs):
        svg = o.svg(o.title, standalone=True).replace("<style>", "<style>" + build.LIGHT_SVG_VARS).replace("<defs>", fonts + "<defs>", 1)
        slug = unicodedata.normalize("NFKD", fr_.split(" - ")[0].split(" : ")[0]).encode("ascii", "ignore").decode()
        name = f"{num}_{slug.replace(',', '').replace(' ', '-').replace(chr(39), '')}.svg"
        with open(os.path.join(dist, "plans-svg", name), "w") as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
    readme = f"""Gharsa Foquiya - Piscine - Variante C : une pompe au puisard, deux tubes
Version {VERSION} (indice {INDICE}) - {DATE}
Même bassin que l'indice E (v1.3.1). Ni local technique, ni filtre, ni skimmer : une pompe 24 V couchée au fond
sous une cage inox, le tube 1 vers le jardin, le tube 2 vers la cascade.
Conception : {AUTHOR['name']} - {AUTHOR['url']} - {AUTHOR['email']} - WhatsApp {AUTHOR['whatsapp']}
Exécution : {CONTRACTOR['name']} - {CONTRACTOR['form']} - RC {CONTRACTOR['rc']} {CONTRACTOR['tribunal']} - ICE {CONTRACTOR['ice']}
            {CONTRACTOR['address']} - Tél. {CONTRACTOR['phones']} - {CONTRACTOR['emails']}

index.html        Dossier : principe, la pompe dans le puisard, plans, calculs, comparaison E / B / C, équipements,
                  étanchéité, électricité, entretien, descriptif, phasage, devis, planning, lexique
plans-svg/        Planches VC-01 à VC-08, PL-01, PL-02, PL-05 (format A3, imprimer à 100 %)
img/              Photos du site + cover.png et image1.png, image2.png... (galerie) :
                  déposez-les dans img/, ils s'affichent automatiquement à l'ouverture de index.html

Ouvrir index.html dans un navigateur (connexion internet pour les polices).
Votre pompe 220 V ne doit pas aller dans l'eau du bassin : la pompe du puisard est en 24 V CC (TBTS).
Sans filtre, l'eau se trouble plus vite : options possibles (filtre sur le tube 2, robot sans fil).
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
                z.write(p, os.path.join(f"Piscine-Variante-C_v{VERSION}", os.path.relpath(p, dist)))
    print("built", dist, "zip", zpath, os.path.getsize(zpath))


if __name__ == "__main__":
    main()
