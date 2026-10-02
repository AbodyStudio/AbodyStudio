"""Construit le dossier piscine et jardins : page HTML, planches SVG, archive zip.

Author: AbodyStudio Limited - https://abodystudio.com/
Usage : python3 build.py   (incrémenter VERSION dans src/model.py à chaque mise à jour)
"""
import html
import re
import unicodedata
import json
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

import sheets  # noqa: E402
from lettres import en_lettres  # noqa: E402
from model import (hu, CONTRACTOR, AUTHOR, DATE, INDICE, LV, POOL_L, POOL_W, PROJECT, Q, SHEETS, VERSION,  # noqa: E402
                   FLOOR_DEEP, FLOOR_SHALLOW, PARCEL_AREA, HOUSE, POOL, TECH, DECK, FRONT_GARDEN,
                   SLOPE_PCT, SLOPE_GENTLE, SLOPE_STEEP, WATER_SHALLOW, WATER_BREAK, WATER_DEEP, PUMP_FLOW, FILTER_D,
                   CHLORINATOR, dqe, u_drive, u_nw, STAIR, NW_GARDEN_EDGE, edge_lengths)

FA_DIR = os.environ.get("FA_DIR", "/tmp/fa/package/svgs")
ICONS = {
    "solid": ["images", "image", "xmark", "chevron-left", "chevron-right", "person-swimming", "ruler-combined", "map-location-dot", "camera", "compass-drafting", "layer-group",
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
.pipe-s{stroke:var(--p-s);fill:none}.pipe-r{stroke:var(--p-r);fill:none;stroke-dasharray:2.4 .8}
.pipe-e{stroke:var(--p-e);fill:none;stroke-dasharray:1.2 .8}.pipe-d{stroke:var(--green);fill:none;stroke-dasharray:.4 .8;stroke-linecap:round}
.elec{stroke:var(--p-el);fill:none;stroke-dasharray:3 .8 .6 .8}.water-l{stroke:var(--p-s);fill:none;stroke-dasharray:.8 .6}
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
                  "--tree-f:#e3efd9;--green:#4f7f35;--hatch:#7d8b95;--head:#e8eef2;--demo:#d9a400;--demo-ink:#8a6a00;"
                  "--p-s:#1683a8;--p-r:#1b8a5a;--p-e:#8a5a2b;--p-el:#7b3fb0}")


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


NB = " "     # espace insécable
NNB = " "    # espace fine insécable


def fr(t):
    """Typographie française : espaces insécables avant : ; ! ? et dans les guillemets."""
    t = str(t)
    for a, b in ((" :", NB + ":"), (" ;", NNB + ";"), (" !", NNB + "!"), (" ?", NNB + "?"),
                 ("« ", "«" + NB), (" »", NB + "»"), (" %", NB + "%"), (" m²", NB + "m²"), (" m³", NB + "m³")):
        t = t.replace(a, b)
    return t


def nf(x, d=2):
    """Nombre au format français (virgule décimale)."""
    return f"{x:.{d}f}".replace(".", ",")


def decfr(t):
    """Virgule décimale française dans un libellé (1.25 → 1,25)."""
    return re.sub(r"(\d)\.(\d)", r"\1,\2", t)


def hm(hours):
    """Durée en heures et minutes : 4.2 -> « 4 h 12 min »."""
    h = int(hours)
    m = int(round((hours - h) * 60))
    if m == 60:
        h, m = h + 1, 0
    return f"{h}{NB}h{NB}{m:02d}{NB}min"


def money(x):
    return f"{x:,.0f}".replace(",", NB)


def esc(t):
    return fr(html.escape(str(t), quote=False))


# ---------------------------------------------------------------------------
# Contenu (français)
# ---------------------------------------------------------------------------

def facts():
    q = Q
    rows = [
        ("Bassin (plan d'eau)", f"{nf(POOL_L)} × {nf(POOL_W)} m - 50 m²"),
        ("Profondeur d'eau", f"{nf(WATER_SHALLOW)} m (zone enfants) → {nf(WATER_DEEP)} m"),
        ("Volume d'eau", f"{nf(q['water_vol'], 1)} m³ (calcul par tranches)"),
        ("Filtration", f"{PUMP_FLOW} m³/h - recyclage en {hm(q['water_vol'] / PUMP_FLOW)}"),
        ("Structure", f"Béton armé B25, {nf(q['c_total'], 1)} m³ - acier {money(round(q['steel']))} kg"),
        ("Terrain", f"{money(PROJECT['surface'])} m² - Lambert Nord Maroc"),
    ]
    return "".join(f"<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>" for a, b in rows)


def fit_rows():
    sb = u_drive(STAIR["v0"]) - STAIR["u1"]
    sf = u_drive(HOUSE["v1"]) - STAIR["u1"]
    ch = NW_GARDEN_EDGE - u_nw(POOL["v0"])
    rows = [
        ("Façade → bassin", "2 m de jardin + 2,5 m de transats + 0,5 m de margelle", f"{nf(POOL['v0'] - HOUSE['v1'])} m", "Respecté"),
        ("Bassin / façade", "bassin de 10 m face à la façade de 12 m", "retrait de 1,00 m de chaque côté", "Respecté"),
        ("Largeur du bassin", "5 m", "5,00 m", "Respecté"),
        ("Arrière de la villa", "jardin de 3 m", "≥ 3,00 m jusqu'à la limite côté chemin", "Respecté"),
        ("Côté allée", "jardin de 1 à 1,5 m + route de 3 m", f"bande de {nf(sb)} à {nf(sf)} m + allée de 3,00 m", "La bande s'élargit vers l'avant : la clôture SE n'est pas parallèle à la villa"),
        ("Autre côté du bassin", "jardin de 8 m + poules", f"jardin de 8,00 m + parc à poules de {nf(ch)} m", "Le parc à poules prend la largeur restante"),
        ("Escalier vers la piscine", "escalier sur le côté gauche de la villa", "palier ±0,00 + 5 marches, largeur 1,40 m", "Ajouté en v1.1.0, au pied de l'escalier du toit-terrasse"),
        ("Au-delà du bassin", "-", f"{nf(52.55 - POOL['v1'])} m jusqu'à la limite NE", "Verger existant conservé"),
    ]
    return "".join(f"<tr><th>{esc(a)}</th><td>{esc(b)}</td><td class='num'>{esc(c)}</td><td>{esc(d)}</td></tr>" for a, b, c, d in rows)


SPECS = [
    ("trowel-bricks", "Lot 1 - Terrassements", [
        "Décaper 20 cm de terre végétale et la stocker pour les massifs et la pelouse.",
        f"Fouille de {Q['exc_base']:.0f} m² en fond, profondeur moyenne {nf(Q['exc_depth_avg'])} m ({nf(Q['exc_depth_max'])} m au grand fond), talus à 1/2. L'argile rouge ne doit jamais rester verticale au-delà de 1,30 m.",
        "Garder la fouille sèche : un puisard dans l'angle du grand fond et une pompe d'épuisement sur le chantier d'octobre à avril.",
        "Compacter le fond de forme, puis poser le hérisson de pierres de 20 cm et le béton de propreté de 8 cm.",
        "Remblayer seulement après l'essai d'étanchéité, bassin plein : bande de 40 cm de gravier 15/25 contre les voiles, puis matériaux sélectionnés du site compactés par couches de 20 cm.",
    ]),
    ("helmet-safety", "Lot 2 - Béton armé", [
        "Béton B25 dosé à 350 kg/m³ de CPJ 45, E/C ≤ 0,50, avec hydrofuge de masse. Vibration à l'aiguille. Aucun ajout d'eau sur le chantier.",
        "Couler le radier (20 cm, 2 nappes HA10 e=15) en une seule fois, avec les aciers en L des voiles et les deux bondes de fond déjà en place.",
        "Coller le joint hydrogonflant sur le radier avant les voiles. Voiles de 20 cm : HA12 e=15 verticaux et HA10 e=20 horizontaux sur les deux faces, chaînage 20 × 25.",
        "Placer toutes les pièces à sceller (skimmers, buses, prise balai, niches des projecteurs) dans le coffrage avant le coulage. Aucun carottage après coup.",
        "Cure humide de 7 jours minimum (toile de jute arrosée deux fois par jour au soleil ou au vent). Attendre 21 à 28 jours avant les enduits.",
    ]),
    ("water", "Lot 3 - Étanchéité et revêtements", [
        "Gobetis, puis enduit hydrofuge en deux couches (15 à 20 mm), gorges de 5 × 5 cm à tous les angles rentrants.",
        "Deux couches de ciment flexible bi-composant, avec bandes d'armature aux angles et colliers d'étanchéité sur chaque pièce à sceller.",
        "Essai d'étanchéité : remplir le bassin 7 jours et relever le niveau chaque matin. Un seau d'eau posé sur les marches permet de distinguer l'évaporation d'une fuite.",
        "Mosaïque pâte de verre 25 × 25 mm, colle C2TE S1 et joint époxy. Frise plus foncée à la ligne d'eau, ligne de carrelage contrastée à la rupture de pente (1,20 m) et marquage des profondeurs 0,55 / 1,20 / 1,80.",
        "Margelles 50 × 50 en pierre reconstituée, nez arrondi, débord de 3 cm, posées au mortier. Joint souple entre margelles et plage.",
    ]),
    ("seedling", "Lot 6 - Jardins autour du bassin", [
        "Escalier d'accès à la piscine sur le côté gauche de la villa (côté allée) : palier à ±0,00 relié au pied de l'escalier du toit-terrasse, puis 5 marches de 15 × 30 cm, largeur 1,40 m, jusqu'à la plage à −0,75, avec main courante. Il arrive face aux marches du bassin.",
        "Jardinière de 2,00 m sur le reste de la façade : lavande, romarin, agapanthe et gaura en goutte-à-goutte.",
        "Caniveau à grille au pied de la jardinière : l'eau de pluie venant de la villa ne doit jamais couler vers le bassin. Raccorder les descentes d'eaux pluviales du toit au puits perdu, jamais sur la plage.",
        "Plage solarium de 2,50 m en grès cérame antidérapant R11 60 × 60 sur forme en béton armé de 10 cm, pente de 1,5 % vers le caniveau.",
        "Jardin latéral SE avec douche extérieure près de l'escalier du bassin, haie de cyprès et bornes lumineuses le long de l'allée, comme sur l'image de synthèse.",
        "Côté NO : pelouse de 8,00 m avec le local technique, puis le parc à poules grillagé (h 1,50 m) le long de la limite.",
    ]),
]

HYD = [
    ("Pompe", f"{PUMP_FLOW} m³/h à 10 mCE, vitesse variable, 230 V (bassin de {nf(Q['water_vol'], 1)} m³ recyclé en {hm(Q['water_vol'] / PUMP_FLOW)})"),
    ("Filtre à sable", f"Ø {FILTER_D * 1000:.0f} mm, vanne 6 voies - vitesse de filtration {Q['filter_rate']:.0f} m/h (≤ 50)"),
    ("Aspiration", "2 skimmers + 2 bondes de fond (1 ligne) + prise balai : 4 lignes Ø50 indépendantes jusqu'à la nourrice, chacune avec sa vanne"),
    ("Refoulement", "Boucle Ø63, piquages Ø50 vers 4 buses orientées vers les skimmers"),
    ("Canalisations", "PVC pression PN16 collé. Essai de pression 24 h avant remblai, aucune chute de pression admise"),
    ("Local technique", f"2,40 × 2,00 m hors œuvre, semi-enterré. Pompe sous le plan d'eau ({nf(LV['water'])}) : aspiration en charge. Siphon de sol et ventilation"),
    ("Contre-lavage", "Vers le puits perdu (Ø 1,20 × 2,50 m) dans le verger. Avec un électrolyseur au sel, ne jamais envoyer cette eau vers les agrumes"),
    ("Traitement", f"Chlore au démarrage ; électrolyseur au sel {CHLORINATOR} m³ + régulation du pH en option"),
]
ELEC = [
    ("Alimentation", "Depuis le TGBT de la villa : câble U1000 R2V 3G6 mm² sous gaine TPC rouge Ø63 à 60 cm de profondeur, grillage avertisseur au-dessus"),
    ("Coffret piscine", "Interrupteur général, DDR 30 mA type A, disjoncteurs pompe (16 A), éclairage (10 A), électrolyseur et prise, contacteur, horloge, parafoudre"),
    ("Éclairage", "3 projecteurs LED 12 V 30 W, alimentés par un transformateur de sécurité 300 VA placé dans le local technique"),
    ("Volumes de sécurité", "Local et transformateur à 3,55 m de l'eau, hors volumes 0, 1 et 2 (NF C 15-100 / CEI 60364-7-702)"),
    ("Liaison équipotentielle", "Ferraillage du bassin, échelle et pièces métalliques reliés entre eux et au piquet de terre"),
]

SEQ = [
    ("Préparation", "Le topographe relève les angles de la villa et les niveaux, puis implante le bassin à partir de la façade. Se renseigner auprès de la Commune Sahel Chamali sur l'autorisation nécessaire. Laisser le chlore de la piscine Intex se dissiper 3 à 4 jours, puis la vider dans le verger."),
    ("Terrassement", "Décapage, fouille talutée, puisard. Contrôle du fond de forme : les poches molles sont purgées et remplacées par de la pierre."),
    ("Fondation", "Hérisson, béton de propreté, lit de pose du drain périphérique."),
    ("Radier", "Ferraillage, bondes de fond, aciers en L des voiles. <b>Point d'arrêt :</b> réception du ferraillage avant coulage. Coulage, vibration, cure."),
    ("Voiles", "Joint hydrogonflant, ferraillage, pièces à sceller, coffrage, coulage des voiles et du chaînage. Gros œuvre du local technique en parallèle."),
    ("Canalisations", "Pose de toutes les lignes jusqu'au local technique. <b>Point d'arrêt :</b> essai de pression 24 h avant de recouvrir."),
    ("Cure", "21 à 28 jours. Pendant ce temps : gaine électrique, puits perdu, escalier d'accès à la piscine côté gauche."),
    ("Étanchéité", "Enduit, gorges, membrane flexible. <b>Point d'arrêt :</b> essai d'étanchéité de 7 jours, puis remblai bassin plein."),
    ("Finitions", "Vider l'eau d'essai dans le verger. Mosaïque et joint époxy, margelles, plage, caniveau."),
    ("Équipements", "Pompe, filtre, coffret, projecteurs, échelle. L'électricien contrôle le déclenchement du DDR et la liaison équipotentielle."),
    ("Jardins", "Jardinière, pelouse, haie, éclairage, clôture du poulailler, clôture ou couverture de sécurité."),
    ("Mise en eau", "Remplissage par camion-citerne, mise en route de la filtration, équilibrage de l'eau, remise des clés au propriétaire."),
]

GANTT = [
    ("Préparation et implantation", 1, 1), ("Dépose de la piscine Intex", 1, 1), ("Terrassement et fondation", 2, 1.5),
    ("Radier", 3, 1), ("Voiles et chaînage", 4, 1.5), ("Local technique", 4, 2), ("Canalisations et essai de pression", 5, 1.5),
    ("Cure du béton", 5, 3.5), ("Enduit et membrane", 9, 1), ("Essai d'étanchéité et remblai", 10, 1),
    ("Mosaïque et margelles", 11, 2), ("Plage, caniveau, escalier d'accès", 12, 1.5), ("Électricité et équipements", 11, 2.5),
    ("Jardins, pelouse, clôtures", 13, 2), ("Mise en eau et mise en service", 14, 1),
]

GLOSS = [
    ("Piscine / bassin", "مسبح / حوض السباحة"),
    ("Radier", "بلاطة القاعدة"),
    ("Voile", "جدار خرساني مسلح"),
    ("Chaînage", "حزام خرساني"),
    ("Béton armé", "خرسانة مسلحة"),
    ("Béton de propreté", "خرسانة النظافة"),
    ("Hérisson", "طبقة الحجر المرصوص"),
    ("Fer HA / acier", "حديد التسليح"),
    ("Enrobage", "الغطاء الخرساني"),
    ("Joint hydrogonflant", "شريط منع التسرب"),
    ("Enduit hydrofuge", "تلبيس مقاوم للماء"),
    ("Étanchéité", "العزل المائي"),
    ("Mosaïque pâte de verre", "فسيفساء زجاجية"),
    ("Margelle", "حافة المسبح"),
    ("Plage", "الممشى حول المسبح"),
    ("Skimmer", "كاشطة سطحية (سكيمر)"),
    ("Bonde de fond", "مصرف القاع"),
    ("Buse de refoulement", "فوهة الإرجاع"),
    ("Prise balai", "مأخذ المكنسة"),
    ("Projecteur", "كشاف إنارة تحت الماء"),
    ("Local technique", "الغرفة التقنية"),
    ("Filtre à sable", "فلتر رملي"),
    ("Nourrice (collecteur)", "مجمّع الأنابيب"),
    ("Disjoncteur différentiel 30 mA", "قاطع تفاضلي 30 ميلي أمبير"),
    ("Liaison équipotentielle", "ربط تساوي الجهد"),
    ("Drain périphérique", "مصرف محيطي"),
    ("Puits perdu", "بئر التصريف"),
    ("Caniveau", "قناة تصريف"),
    ("Remblai", "الردم"),
    ("Terrain naturel (TN)", "سطح الأرض الطبيعي"),
    ("Poulailler", "خمّ الدجاج"),
]

VERIFY = [
    "Profondeur de la villa (supposée 10,00 m), position exacte de l'escalier du toit-terrasse et de la porte d'entrée : l'escalier d'accès à la piscine se cale sur le pied de l'escalier du toit.",
    "Niveaux : sol fini de la villa ±0,00, terrain naturel au droit du bassin (supposé −0,80) et pente vers le verger. Un relevé topographique fixe tout cela en une seule visite.",
    "Sol : creuser un sondage de 2,50 m à l'emplacement du grand fond, après une journée de pluie. Si l'eau entre dans le sondage, le drain et le clapet deviennent indispensables et le BET peut épaissir le radier.",
    "Emplacement du TGBT de la villa et puissance disponible pour la pompe et une éventuelle pompe à chaleur.",
    f"Eau de remplissage ({nf(Q['water_vol'], 1)} m³, deux fois) : camions-citernes ou puits.",
    "Autorisation : se renseigner auprès de la Commune Sahel Chamali et de l'Agence urbaine de Tanger avant le terrassement.",
]


def vol_rows():
    q = Q
    out = []
    for t in reversed(q["slices"]):
        depth = nf(t["d1"]) + " m" if abs(t["d1"] - t["d2"]) < 1e-6 else f"{nf(t['d2'])} → {nf(t['d1'])} m"
        out.append(f"<tr><th>{esc(t['name'])}</th><td class='num'>{nf(t['L'])} m</td><td class='num'>{depth}</td>"
                   f"<td class='num'>{nf(t['dm'], 3)} m</td><td class='num'>{nf(t['L'])} × {nf(t['dm'], 3)} × {nf(POOL_W)}</td>"
                   f"<td class='num'>{hu(t['v']).replace('.', ',')} m³</td></tr>")
    out.append(f"<tr><th>Volume brut</th><td class='num'>{nf(POOL_L)} m</td><td class='num'>{nf(WATER_SHALLOW)} → {nf(WATER_DEEP)} m</td>"
               f"<td class='num'>{nf(q['gross_vol'] / (POOL_L * POOL_W), 3)} m</td><td></td><td class='num'>{hu(q['gross_vol']).replace('.', ',')} m³</td></tr>")
    out.append(f"<tr><th>Déduction : escalier d'entrée</th><td></td><td></td><td></td><td class='num'>2 marches × 2,00 m</td>"
               f"<td class='num'>−{hu(q['steps_vol']).replace('.', ',')} m³</td></tr>")
    out.append(f"<tr class='vol-tot'><th>Volume d'eau</th><td></td><td></td><td></td><td></td><td class='num'>{hu(q['water_vol']).replace('.', ',')} m³</td></tr>")
    return "".join(out)


def dqe_html():
    lots, opt = dqe()
    out = []
    for code, lot_fr, _en, items in lots + [opt]:
        cls = " opt" if code == "O" else ""
        out.append(f'<tbody class="lot{cls}" data-lot="{code}"><tr class="lot-h"><th colspan="6">'
                   f'<span class="lot-n">{"Options" if code == "O" else "Lot " + code}</span> {esc(lot_fr)}</th></tr>')
        for n, dfr, _den, unit, qty, pu in items:
            out.append(
                f'<tr data-q="{qty}"><td class="mono">{n}</td><td>{esc(decfr(dfr))}</td>'
                f'<td class="c">{unit}</td><td class="num">{esc(nf(qty, 1) if qty % 1 else money(qty))}</td>'
                f'<td class="num"><input id="pu-{n}" class="pu" type="number" min="0" step="10" value="{pu}" aria-label="Prix unitaire {n}"></td>'
                f'<td class="num amt">{money(qty * pu)}</td></tr>')
        out.append(f'<tr class="sub"><td colspan="5">{"Total des options (non compris)" if code == "O" else "Sous-total lot " + code}</td><td class="num sub-v">0</td></tr></tbody>')
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


GALLERY_SLOTS = 6     # placeholders shown until images are found


def cover_html():
    return f'''<figure class="cover" id="cover">
  <img id="cover-img" alt="Piscine et jardins, terrain Gharsa Foquiya" hidden>
  <div class="cover-ph" id="cover-ph">{ic("image")}<span class="mono">img/cover.png</span>
    <small>{fr("Image de couverture : déposez cover.png dans le dossier img (paysage, 2400 × 1000 px conseillé).")}</small></div>
</figure>'''


def gallery_html():
    slots = "".join(
        f'<figure class="g-tile g-ph">{ic("image")}<span class="mono">img/image{i}.png</span></figure>'
        for i in range(1, GALLERY_SLOTS + 1))
    return f'''<div class="gal" id="gal">
  <div class="gal-head"><h3>{ic("images")}Proposition et autres vues</h3>
  <p class="gal-note">{fr("Deuxième proposition et autres points de vue des images de synthèse. Touchez une image pour l'agrandir.")}</p></div>
  <div class="gal-grid" id="gal-grid">{slots}</div>
  <p class="gal-hint mono" id="gal-hint">{fr("Déposez image1.png, image2.png, image3.png… dans le dossier img : elles s'affichent ici automatiquement, dans l'ordre.")}</p>
</div>
<div class="lb" id="lb" hidden role="dialog" aria-modal="true" aria-label="Vue en plein écran">
  <img id="lb-img" alt="">
  <p id="lb-cap"></p>
  <button type="button" class="lb-b lb-prev" id="lb-prev" aria-label="Vue précédente">{ic("chevron-left")}</button>
  <button type="button" class="lb-b lb-next" id="lb-next" aria-label="Vue suivante">{ic("chevron-right")}</button>
  <button type="button" class="lb-b lb-x" id="lb-x" aria-label="Fermer">{ic("xmark")}</button>
</div>'''


def sheet_figs(sheet_objs):
    out = []
    for (num, title, sub, sc), obj in zip(SHEETS, sheet_objs):
        out.append(f'''<figure class="plan" id="{num.lower()}">
<figcaption><span class="pl-n mono">{num}</span><span class="pl-t">{esc(title)}<small>{esc(sub)} - éch. {sc}</small></span>
<button type="button" class="zoom" aria-pressed="false" aria-label="Agrandir {num}">{ic("expand")}<span>Agrandir</span></button></figcaption>
<div class="plan-scroll">{obj.svg(obj.title)}</div></figure>''')
    return "".join(out)


def page(sheet_objs):
    lots, opt = dqe()
    total = sum(i[4] * i[5] for _, _, _, items in lots for i in items)
    photos = [
        ("site-aerial-from-roof.webp", "Aujourd'hui, vue du toit-terrasse", "Piscine Intex sur une plateforme nivelée. Verger et poulailler côté NO, allée en gravier le long de la clôture noire côté SE, verger ouvert au-delà."),
        ("site-from-driveway.webp", "Aujourd'hui, vue de l'allée", "Villa existante avec l'escalier extérieur côté allée et l'ancien coffret de filtration. Le nouveau local technique se place côté NO."),
        ("site-terrace-and-pool.webp", "Façade de la villa", "Plateforme surélevée et mur en moellons, attentes de poteaux pour un futur étage. La jardinière et l'escalier vers la plage remplacent cette zone."),
        ("concept-render.webp", "Ambiance visée (image de synthèse)", "Margelles et plage beiges, transats face au bassin, allée éclairée bordée de cyprès. Le plan suit vos cotes, pas les proportions de l'image."),
    ]
    ph = "".join(f'<figure class="ph"><img src="img/{f}" alt="{esc(t)}" loading="lazy" width="1400" height="1050"><figcaption><b>{esc(t)}</b>{esc(d)}</figcaption></figure>' for f, t, d in photos)
    specs = "".join(f'<section class="spec"><h3>{ic(i)}{esc(t)}</h3><ul>' + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul></section>" for i, t, items in SPECS)
    hyd = "".join(f"<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>" for a, b in HYD)
    ele = "".join(f"<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>" for a, b in ELEC)
    seq = "".join(f"<li><div><b>{esc(a)}.</b> {fr(b)}</div></li>" for a, b in SEQ)
    gl = "".join(f'<tr><td>{esc(a)}</td><td class="ar" lang="ar" dir="rtl">{c}</td></tr>' for a, c in GLOSS)
    ver = "".join(f"<li>{esc(v)}</li>" for v in VERIFY)
    nav_sheets = "".join(f'<li class="sub"><a href="#{n.lower()}"><span class="mono">{n}</span> {esc(t)}</a></li>' for n, t, sub, sc in SHEETS)
    return f"""<title>Piscine et jardins Gharsa Foquiya</title>
<meta name="description" content="Dossier d'exécution de la piscine et des jardins, Douar Ghanem, Tanger-Assilah - AbodyStudio Limited, v{VERSION}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Archivo+Narrow:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Cairo:wght@400;600&display=swap">
<style>
/* Mise en page : un dossier relié sur fond blanc - sommaire à gauche, une colonne de lecture, planches en pleine largeur. Thème clair unique, voulu. */
:root{{
  color-scheme:light;
  --paper:#ffffff; --sheet:#ffffff; --panel:#f7f9fa; --ink:#14212b; --ink-2:#56656f; --rule:#dde4e8; --head:#f2f5f7;
  --new:#c8372d; --parcel:#c8372d; --water:#1683a8; --water-f:#cdebf5; --light-f:#fff2b8; --paved-f:#eceff1;
  --chick-f:#f6efe2; --tree-f:#e3efd9; --green:#4f7f35; --hatch:#7d8b95; --demo:#d9a400; --demo-ink:#8a6a00;
  --p-s:#1683a8; --p-r:#1b8a5a; --p-e:#8a5a2b; --p-el:#7b3fb0;
  --accent:#c8372d; --chip:#ffffff;
  --f-disp:"Archivo","Arial",sans-serif; --f-body:"IBM Plex Sans",system-ui,sans-serif; --f-mono:"IBM Plex Mono",ui-monospace,monospace; --f-ar:"Cairo",sans-serif;
}}
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
.lead{{max-width:70ch;color:var(--ink-2);font-size:16.5px}}
.eyebrow{{font:600 12px/1 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent);display:flex;gap:.6em;align-items:center}}
header.top{{display:grid;gap:18px;padding-bottom:22px;border-bottom:2px solid var(--ink)}}
.meta{{display:flex;flex-wrap:wrap;gap:6px 18px;font:500 12.5px/1.4 var(--f-mono);color:var(--ink-2)}}
.meta b{{color:var(--ink);font-weight:500}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0;margin:0;border:1px solid var(--rule);background:var(--panel)}}
.facts div{{padding:12px 14px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);min-width:0}}
.facts dt{{font:600 11px/1.2 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}}
.facts dd{{margin:4px 0 0;font:600 15px/1.35 var(--f-disp)}}
.grid{{display:grid;grid-template-columns:230px minmax(0,1fr);gap:40px;margin-top:34px}}
nav.idx{{position:sticky;top:calc(env(safe-area-inset-top,0px) + 16px);align-self:start;font-size:13.5px}}
nav.idx ol{{list-style:none;margin:0;padding:0;display:grid;gap:2px}}
nav.idx a{{display:block;padding:5px 8px;text-decoration:none;border-left:2px solid transparent;color:var(--ink-2)}}
nav.idx a:hover,nav.idx a:focus-visible{{color:var(--ink);border-left-color:var(--accent);outline:none}}
nav.idx .sub{{padding-left:12px;font-size:12.5px}}
main{{display:grid;gap:56px;min-width:0}}
section.blk{{display:grid;gap:18px;min-width:0;scroll-margin-top:16px}}
.photos{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}
.ph{{margin:0;background:var(--sheet);border:1px solid var(--rule);display:grid;align-content:start;min-width:0}}
.ph img{{width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;display:block}}
.ph figcaption{{padding:10px 12px;font-size:13.5px;color:var(--ink-2);display:grid;gap:2px}}
.ph figcaption b{{color:var(--ink);font-family:var(--f-disp)}}
[hidden]{{display:none!important}}
.cover{{margin:0;width:100%;background:var(--panel);border-bottom:1px solid var(--rule)}}
.cover img{{display:block;width:100%;height:auto;aspect-ratio:12/5;object-fit:cover}}
.cover-ph{{aspect-ratio:12/5;display:grid;place-content:center;justify-items:center;gap:8px;text-align:center;padding:16px;
  color:var(--ink-2);border:2px dashed var(--rule);margin:12px;background:repeating-linear-gradient(135deg,transparent 0 14px,#eef2f4 14px 15px)}}
.cover-ph .ic{{width:34px;height:34px;color:#b8c3ca}}
.cover-ph .mono{{font-size:15px;color:var(--ink)}} .cover-ph small{{font-size:13px;max-width:52ch}}
@media (max-width:560px){{.cover img,.cover-ph{{aspect-ratio:4/3}}}}
.gal{{display:grid;gap:12px;margin-top:10px;min-width:0}}
.gal-head{{display:grid;gap:4px}} .gal-head h3 .ic{{color:var(--accent)}}
.gal-note{{font-size:14px;color:var(--ink-2);max-width:72ch}}
.gal-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}}
.g-tile{{margin:0;border:1px solid var(--rule);background:var(--sheet);min-width:0;display:grid}}
.g-tile button{{display:block;padding:0;border:0;background:none;cursor:zoom-in;width:100%}}
.g-tile img{{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover}}
.g-tile figcaption{{padding:8px 11px;font-size:13px;color:var(--ink-2)}}
.g-tile figcaption b{{color:var(--ink);font-family:var(--f-disp)}}
.g-ph{{aspect-ratio:3/2;place-content:center;justify-items:center;gap:6px;border:2px dashed var(--rule);background:var(--panel);color:var(--ink-2);font-size:13px}}
.g-ph .ic{{width:26px;height:26px;color:#b8c3ca}}
.gal-hint{{font-size:12px;color:var(--ink-2)}}
.g-tile button:focus-visible,.lb-b:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.lb{{position:fixed;inset:0;z-index:50;background:rgba(10,14,18,.94);display:grid;place-items:center;padding:calc(env(safe-area-inset-top,0px) + 56px) 16px calc(env(safe-area-inset-bottom,0px) + 56px)}}
.lb img{{max-width:100%;max-height:100%;object-fit:contain}}
.lb p{{position:absolute;left:16px;right:16px;bottom:calc(env(safe-area-inset-bottom,0px) + 16px);margin:0;text-align:center;color:#e8edf0;font-size:14px}}
.lb-b{{position:absolute;display:grid;place-items:center;width:44px;height:44px;border:1px solid rgba(255,255,255,.35);background:rgba(255,255,255,.08);color:#fff;cursor:pointer;font-size:18px}}
.lb-prev{{left:12px;top:50%;transform:translateY(-50%)}} .lb-next{{right:12px;top:50%;transform:translateY(-50%)}}
.lb-x{{right:12px;top:calc(env(safe-area-inset-top,0px) + 12px)}}
.tbl{{overflow-x:auto;border:1px solid var(--rule);background:var(--sheet)}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}}
thead th{{font:600 11.5px/1.3 var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);background:var(--head)}}
tbody th{{font-weight:600}}
td.num,th.num{{text-align:right;white-space:nowrap}} td.c,th.c{{text-align:center}}
.note{{border-left:3px solid var(--accent);padding:10px 14px;background:#fdf3f2;font-size:14px;display:flex;gap:10px;align-items:flex-start}}
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
.zoom,.reset{{display:inline-flex;gap:6px;align-items:center;border:1px solid var(--rule);background:var(--chip);padding:6px 10px;cursor:pointer;font-size:13px;white-space:nowrap}}
.zoom:hover,.zoom:focus-visible,.reset:hover,.reset:focus-visible{{border-color:var(--ink);outline:none}}
.specs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}}
.spec{{background:var(--panel);border:1px solid var(--rule);padding:16px 18px;display:grid;gap:10px;align-content:start;min-width:0}}
.spec h3 .ic{{color:var(--accent)}}
.spec ul{{margin:0;padding-left:1.1em;display:grid;gap:6px;font-size:14px}}
.two{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}}
.two > div{{min-width:0;display:grid;gap:8px;align-content:start}}
ol.seq{{margin:0;padding:0;list-style:none;counter-reset:s;display:grid;gap:0;border-top:1px solid var(--rule)}}
ol.seq li{{counter-increment:s;display:grid;grid-template-columns:44px minmax(0,1fr);gap:10px;padding:12px 0;border-bottom:1px solid var(--rule);font-size:14.5px}}
ol.seq li > div{{max-width:78ch}}
ol.seq li::before{{content:counter(s,decimal-leading-zero);font:500 13px/1.6 var(--f-mono);color:var(--accent)}}
.dqe td{{font-size:13.5px}}
.dqe .lot-h th{{background:var(--head);font:700 14px/1.3 var(--f-disp)}}
.lot-n{{font:600 11.5px var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-right:6px}}
.dqe .sub td{{font-weight:600;text-align:right;background:var(--sheet)}}
.dqe .opt td,.dqe .opt th{{color:var(--ink-2)}}
.pu{{width:92px;text-align:right;font:500 13px var(--f-mono);padding:4px 6px;border:1px solid var(--rule);background:var(--panel);color:var(--ink)}}
.pu:focus-visible{{outline:2px solid var(--accent);outline-offset:1px}}
.dq-head{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}
.dq-co{{border:1px solid var(--rule);background:var(--panel);padding:14px 16px;font-size:13.5px;line-height:1.5;min-width:0}}
.dq-l{{font:600 11px/1.4 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:4px}}
.dq-n{{font:800 17px/1.3 var(--f-disp);margin-bottom:4px}}
.dqe .grand td{{font:700 14px/1.3 var(--f-disp);text-align:right;background:var(--head);border-bottom:1px solid var(--rule)}}
.dqe .grand td.num{{font-family:var(--f-mono)}}
.dqe .grand .g-ttc td{{color:#fff;background:var(--ink);font-size:15.5px}}
.arrete{{font-size:15px;border:1px solid var(--rule);background:var(--panel);padding:12px 16px}}
.arrete b{{font-weight:600}}
.sign{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}
.sign > div{{border:1px dashed var(--rule);padding:14px 16px;min-height:120px;font-size:13.5px}}
.mute{{color:var(--ink-2)}}
.vol{{display:grid;gap:8px;min-width:0}} .vol h3 .ic{{color:var(--accent)}}
.vol .vol-tot th,.vol .vol-tot td{{font-weight:700;background:var(--head)}}
.small{{font-size:13px;max-width:90ch}}
.totals{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));border:1px solid var(--rule);background:var(--panel);margin:0}}
.totals div{{padding:12px 14px;border-right:1px solid var(--rule)}}
.totals dt{{font:600 11px var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}}
.totals dd{{margin:2px 0 0;font:800 22px/1.2 var(--f-disp);font-variant-numeric:tabular-nums}}
.totals .ttc dd{{color:var(--accent)}}
.row{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}}
.gantt{{background:var(--sheet);border:1px solid var(--rule);padding:12px;overflow-x:auto}}
.gantt-in{{min-width:700px;display:grid;gap:3px}}
.g-head,.g-row{{display:grid;grid-template-columns:240px 1fr;gap:10px;align-items:center}}
.g-weeks{{display:grid;grid-template-columns:repeat(15,1fr);font:500 11px var(--f-mono);color:var(--ink-2);text-align:center}}
.g-name{{font-size:13px}}
.g-track{{position:relative;height:16px;background:repeating-linear-gradient(90deg,transparent 0 calc(100%/15 - 1px),var(--rule) calc(100%/15 - 1px) calc(100%/15))}}
.g-track i{{position:absolute;top:3px;bottom:3px;background:var(--water)}}
.gl{{max-width:640px}}
.ar{{font-family:var(--f-ar);font-size:15.5px;text-align:right}}
ul.ver{{margin:0;padding-left:1.1em;display:grid;gap:8px;max-width:80ch}}
footer{{margin-top:56px;padding-top:18px;border-top:2px solid var(--ink);display:flex;flex-wrap:wrap;gap:8px 22px;font-size:13.5px;color:var(--ink-2)}}
footer span{{display:inline-flex;gap:7px;align-items:center}} footer b{{color:var(--ink)}}
@media (max-width:900px){{.grid{{grid-template-columns:minmax(0,1fr)}} nav.idx{{position:static}} nav.idx ol{{grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}}}}
@media (max-width:560px){{.photos{{grid-template-columns:1fr}}}}
@media (prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
{SVG_CSS}
</style>
{icon_sprite()}
{cover_html()}
<div class="wrap">
<header class="top">
  <p class="eyebrow">{ic("compass-drafting")} Dossier d'exécution - indice {INDICE} - v{VERSION}</p>
  <h1>Piscine et jardins, terrain Gharsa Foquiya</h1>
  <p class="lead">{fr("Bassin en béton armé de 10 × 5 m, implanté à 5,00 m devant la villa existante et centré sur sa façade de 12 m, avec l'aménagement des jardins autour. Plans établis selon l'usage marocain : cartouche, cotes en mètres, niveaux rapportés au ±0,00 du sol fini du rez-de-chaussée.")}</p>
  <p class="meta"><span>{PROJECT['lieu']}, {PROJECT['commune']}, {PROJECT['province']}</span><span>Date <b>{DATE}</b></span><span>Conception <b>{AUTHOR['name']}</b></span><span>Exécution <b>{CONTRACTOR['name']}</b></span></p>
  <dl class="facts">{facts()}</dl>
</header>
<div class="grid">
<nav class="idx" aria-label="Sommaire"><ol>
  <li><a href="#site">Site et existant</a></li>
  <li class="sub"><a href="#gal">Proposition et autres vues</a></li>
  <li><a href="#fit">Vos cotes sur le plan topographique</a></li>
  <li><a href="#plans">Plans</a></li>
  {nav_sheets}
  <li><a href="#spec">Descriptif technique</a></li>
  <li><a href="#hyd">Volume, filtration et électricité</a></li>
  <li><a href="#seq">Phasage des travaux</a></li>
  <li><a href="#dqe">Devis estimatif</a></li>
  <li><a href="#planning">Planning</a></li>
  <li><a href="#safety">Sécurité et entretien</a></li>
  <li><a href="#gloss">Lexique français - arabe</a></li>
  <li><a href="#verify">À vérifier avant de commencer</a></li>
</ol></nav>
<main>
<section class="blk" id="site">
  <h2><span class="sn">01</span>Site et existant</h2>
  <p class="lead">{fr(f"Le terrain fait {money(PROJECT['surface'])} m² (plan topographique de Sahraoui Topo ; {money(round(PARCEL_AREA))} m² recalculés à partir des 11 bornes). Il mesure environ 29 m côté NE et 40 à 49 m de profondeur depuis le chemin public de 6 m au SO. La villa est proche du chemin ; le bassin se place sur sa face NE, côté verger et vue dégagée.")}</p>
  <div class="photos">{ph}</div>
  {gallery_html()}
</section>
<section class="blk" id="fit">
  <h2><span class="sn">02</span>Vos cotes sur le plan topographique</h2>
  <div class="tbl"><table><thead><tr><th>Zone</th><th>Vos cotes</th><th class="num">Dans le plan</th><th>Remarque</th></tr></thead><tbody>{fit_rows()}</tbody></table></div>
  <p class="note">{ic("triangle-exclamation")}<span>{fr("Le plan topographique donne 28,97 m de largeur côté NE. Vos cotes latérales totalisent environ 22 m autour du bassin : la largeur restante revient au parc à poules, côté NO. La position de la villa sur le terrain est reprise de votre croquis et de vos cotes ; un topographe doit relever ses angles avant l'implantation. Le bassin s'implante à partir de la façade (5,00 m devant, retrait de 1,00 m à chaque angle) : il reste donc bien placé même si la villa est légèrement décalée sur le terrain.")}</span></p>
</section>
<section class="blk" id="plans">
  <h2><span class="sn">03</span>Plans</h2>
  <p class="lead">{fr("Six planches A3. En rouge : constructions neuves ; hachuré gris : villa existante ; tirets jaunes : piscine Intex à déposer. Touchez « Agrandir » pour lire une planche en pleine taille. Les mêmes planches sont dans le zip en fichiers SVG, imprimables en A3 à 100 % aux échelles indiquées.")}</p>
  {sheet_figs(sheet_objs)}
</section>
<section class="blk" id="spec">
  <h2><span class="sn">04</span>Descriptif technique</h2>
  <div class="specs">{specs}</div>
</section>
<section class="blk" id="hyd">
  <h2><span class="sn">05</span>Volume d'eau, filtration et électricité</h2>
  <div class="vol"><h3>{ic("water")}Volume d'eau - calcul par tranches</h3>
  <div class="tbl"><table><thead><tr><th>Tranche</th><th class="num">Longueur</th><th class="num">Profondeur d'eau</th><th class="num">Profondeur moyenne</th><th class="num">Calcul (× largeur 5,00 m)</th><th class="num">Volume</th></tr></thead><tbody>{vol_rows()}</tbody></table></div>
  <p class="mute small">{fr("Profondeurs mesurées sous le plan d'eau (−0,85), au sol fini. Méthode : section longitudinale découpée en trapèzes, multipliée par la largeur du bassin, moins le volume de l'escalier d'entrée. Ce volume sert au dimensionnement de la filtration, au remplissage et au dosage des produits.")}</p></div>
  <div class="two">
    <div><h3>{ic("faucet-drip")}Hydraulique (lot 4)</h3><div class="tbl"><table><tbody>{hyd}</tbody></table></div></div>
    <div><h3>{ic("bolt")}Électricité (lot 5)</h3><div class="tbl"><table><tbody>{ele}</tbody></table></div></div>
  </div>
</section>
<section class="blk" id="seq">
  <h2><span class="sn">06</span>Phasage des travaux</h2>
  <ol class="seq">{seq}</ol>
</section>
<section class="blk" id="dqe">
  <h2><span class="sn">07</span>Devis quantitatif et estimatif</h2>
  <p class="lead">{fr("Devis établi pour l'exécution des travaux par ABOUDI BTP Group. Les quantités sont tirées des plans ; les prix unitaires sont indicatifs (région de Tanger, 2026, en dirhams hors taxes) et restent modifiables dans les cases : les totaux, la TVA et le montant en lettres se mettent à jour. Vos modifications restent dans ce navigateur.")}</p>
  <dl class="totals"><div><dt>Total HT</dt><dd id="t-ht">{money(total)}</dd></div><div><dt>TVA 20{NB}%</dt><dd id="t-tva">{money(total * .2)}</dd></div><div class="ttc"><dt>Total TTC (DH)</dt><dd id="t-ttc">{money(total * 1.2)}</dd></div></dl>
  <div class="row"><span class="meta">Les options figurent à la fin et ne sont pas comptées dans les totaux.</span><button type="button" class="reset" id="reset">{ic("rotate-left")}Rétablir les prix</button></div>
  <div class="dq-head">
    <div class="dq-co"><p class="dq-l">Entreprise</p><p class="dq-n">{CONTRACTOR['name']}</p>
      <p>{esc(CONTRACTOR['form'])}</p><p>{esc(CONTRACTOR['address'])}</p>
      <p>RC {CONTRACTOR['rc']} ({CONTRACTOR['tribunal']}) - ICE {CONTRACTOR['ice']}</p>
      <p>{esc(CONTRACTOR['activity'])}</p><p>Tél. {CONTRACTOR['phones']}</p><p>{CONTRACTOR['emails']}</p></div>
    <div class="dq-co"><p class="dq-l">Maître d'ouvrage</p><p class="dq-n">Le propriétaire</p>
      <p>{esc(PROJECT['title_fr'])}</p><p>{PROJECT['lieu']}, terrain dit {esc("« " + PROJECT['terrain'] + " »")}</p><p>{PROJECT['commune']}, {PROJECT['province']}</p>
      <p>Réf. dossier : GF-PISC-v{VERSION} - {DATE}</p><p>Conception : {AUTHOR['name']}</p></div>
  </div>
  <div class="tbl"><table class="dqe"><thead><tr><th>N°</th><th>Désignation des ouvrages</th><th class="c">U</th><th class="num">Qté</th><th class="num">P.U. HT</th><th class="num">Montant HT</th></tr></thead>{dqe_html()}
  <tbody class="grand"><tr><td colspan="5">TOTAL GÉNÉRAL HT</td><td class="num" id="g-ht">{money(total)}</td></tr>
  <tr><td colspan="5">TVA 20{NB}%</td><td class="num" id="g-tva">{money(total * .2)}</td></tr>
  <tr class="g-ttc"><td colspan="5">TOTAL GÉNÉRAL TTC (DH)</td><td class="num" id="g-ttc">{money(total * 1.2)}</td></tr></tbody></table></div>
  <p class="arrete">Arrêté le présent devis à la somme de : <b id="g-words">{en_lettres(round(total * 1.2)).capitalize()} dirhams</b> toutes taxes comprises.</p>
  <div class="sign"><div><p class="dq-l">L'entreprise</p><p>{CONTRACTOR['name']} - le gérant, {CONTRACTOR['manager']}</p><p class="mute">cachet et signature</p></div>
    <div><p class="dq-l">Le maître d'ouvrage</p><p>Bon pour accord</p><p class="mute">date et signature</p></div></div>
</section>
<section class="blk" id="planning">
  <h2><span class="sn">08</span>Planning prévisionnel</h2>
  <p class="lead">{fr("Environ 15 semaines. En démarrant en octobre, l'essentiel du gros œuvre tombe pendant la saison des pluies : gardez la pompe d'épuisement et des bâches sur le chantier. Le bassin sera tout de même prêt au printemps 2027, avant les fortes chaleurs.")}</p>
  <div class="gantt"><div class="gantt-in">{gantt_html()}</div></div>
</section>
<section class="blk" id="safety">
  <h2><span class="sn">09</span>Sécurité et entretien</h2>
  <div class="two">
    <div class="spec"><h3>{ic("shield-halved")}Sécurité</h3><ul>
      <li>{fr("Des enfants vivent sur place : posez la clôture de 1,20 m avec portillon à fermeture automatique (indiquée sur le PL-02) ou une couverture à barres, et une alarme sur les portes de la villa qui donnent sur le bassin.")}</li>
      <li>{fr("Zone enfants à 0,55 m sur 2,50 m, puis pente douce (14 %) jusqu'à 1,20 m. Au-delà, la fosse descend à 1,80 m : ligne de carrelage contrastée et ligne de flotteurs amovible à la rupture de pente.")}</li>
      <li>{fr("Deux bondes de fond anti-vortex, margelles et plage antidérapantes, marquage des profondeurs et « Plongeon interdit » (1,80 m ne suffit pas pour plonger).")}</li>
      <li>{fr("Ne videz jamais le bassin entre novembre et avril : avec une nappe haute, la coque vide peut se soulever (voir PL-05).")}</li>
      <li>{fr("Gardez les poules clôturées à au moins 8 m de l'eau, et les produits chimiques dans un coffre fermé à clé dans le local technique.")}</li>
    </ul></div>
    <div class="spec"><h3>{ic("water")}Eau et entretien</h3><ul>
      <li>{fr("pH 7,2 à 7,6. Chlore libre 1 à 3 mg/L, ou sel 4 g/L avec électrolyseur. TAC 80 à 120 mg/L.")}</li>
      <li>{fr("Durée de filtration en été : température de l'eau ÷ 2, en heures ; 2 à 4 h par jour en hiver (hivernage actif).")}</li>
      <li>{fr("Contre-lavage quand le manomètre monte de 0,3 à 0,5 bar au-dessus de la pression du filtre propre. Sable à changer tous les 5 à 6 ans.")}</li>
      <li>{fr("Chaque semaine : vider les paniers, brosser la ligne d'eau, passer le balai, analyser l'eau.")}</li>
    </ul></div>
  </div>
</section>
<section class="blk" id="gloss">
  <h2><span class="sn">10</span>Lexique de chantier français - arabe</h2>
  <div class="tbl gl"><table><thead><tr><th>Français</th><th class="ar" lang="ar" dir="rtl">العربية</th></tr></thead><tbody>{gl}</tbody></table></div>
</section>
<section class="blk" id="verify">
  <h2><span class="sn">11</span>À vérifier avant de commencer</h2>
  <ul class="ver">{ver}</ul>
  <p class="note">{ic("helmet-safety")}<span>{fr("Ce dossier est un plan d'exécution de principe. Le béton armé est prédimensionné selon les règles BAEL 91 mod. 99 ; le RPS 2000 (version 2011) reste à appliquer. Un bureau d'études agréé (BET) doit vérifier et viser le radier, les voiles et le local technique avant le démarrage, et un électricien qualifié doit réceptionner l'installation.")}</span></p>
</section>
</main>
</div>
<footer><span>Conception <b>{AUTHOR['name']}</b></span><span>{ic("globe")}<a href="{AUTHOR['url']}">{AUTHOR['web']}</a></span><span>{ic("envelope")}{AUTHOR['email']}</span><span>{ic("whatsapp")}WhatsApp {AUTHOR['whatsapp']}</span><span>Exécution <b>{CONTRACTOR['name']}</b> - RC {CONTRACTOR['rc']} {CONTRACTOR['tribunal']} - ICE {CONTRACTOR['ice']}</span><span class="mono">v{VERSION} - indice {INDICE} - {DATE}</span></footer>
</div>
<script>
(function(){{
  var fmt=function(n){{return Math.round(n).toLocaleString('fr-FR').replace(/[\\u202f\\u00a0\\s]/g,'\\u00a0');}};
  var KEY='gf-pool-dqe-v{VERSION}';
  var U=['zéro','un','deux','trois','quatre','cinq','six','sept','huit','neuf','dix','onze','douze','treize','quatorze','quinze','seize','dix-sept','dix-huit','dix-neuf'];
  var T={{2:'vingt',3:'trente',4:'quarante',5:'cinquante',6:'soixante'}};
  function b100(n,f){{
    if(n<20) return U[n];
    var t=Math.floor(n/10), u=n%10;
    if(T[t]) return u===0?T[t]:T[t]+(u===1?' et un':'-'+U[u]);
    if(t===7) return 'soixante'+(u===1?' et onze':'-'+U[10+u]);
    if(t===8) return u===0?'quatre-vingt'+(f?'s':''):'quatre-vingt-'+U[u];
    return 'quatre-vingt-'+U[10+u];
  }}
  function b1000(n,f){{
    var c=Math.floor(n/100), r=n%100, o=[];
    if(c) o.push(c===1?'cent':U[c]+' cent'+(r===0&&f?'s':''));
    if(r) o.push(b100(r,f));
    return o.join(' ');
  }}
  function lettres(n){{
    if(n===0) return 'zéro';
    var m=Math.floor(n/1e6), rest=n%1e6, k=Math.floor(rest/1000), r=rest%1000, o=[];
    if(m) o.push(b1000(m,true)+(m>1?' millions':' million'));
    if(k) o.push(k===1?'mille':b1000(k,false)+' mille');
    if(r) o.push(b1000(r,true));
    return o.join(' ');
  }}
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
    document.getElementById('g-ht').textContent=fmt(ht);
    document.getElementById('g-tva').textContent=fmt(ht*.2);
    document.getElementById('g-ttc').textContent=fmt(ht*1.2);
    var w=lettres(Math.round(ht*1.2));
    document.getElementById('g-words').textContent=w.charAt(0).toUpperCase()+w.slice(1)+' dirhams';
  }}
  function save(){{var o={{}}; inputs.forEach(function(i){{if(i.value!==i.dataset.def) o[i.id]=i.value;}}); try{{localStorage.setItem(KEY,JSON.stringify(o));}}catch(e){{}}}}
  inputs.forEach(function(i){{i.addEventListener('input',function(){{calc();save();}});}});
  document.getElementById('reset').addEventListener('click',function(){{inputs.forEach(function(i){{i.value=i.dataset.def;}}); try{{localStorage.removeItem(KEY);}}catch(e){{}} calc();}});
  calc();
  // ---- cover + gallery: images dropped into img/ show up automatically
  var EXT=['png','jpg','jpeg','webp'];
  function probe(base,cb){{
    var k=0;
    (function next(){{
      if(k>=EXT.length) return cb(null);
      var url='img/'+base+'.'+EXT[k++], im=new Image();
      im.onload=function(){{cb(url);}}; im.onerror=next; im.src=url;
    }})();
  }}
  probe('cover',function(url){{
    if(!url) return;
    var ci=document.getElementById('cover-img');
    ci.src=url; ci.hidden=false; document.getElementById('cover-ph').hidden=true;
  }});
  var found=[], miss=0;
  (function scan(i){{
    if(i>60||miss>=2) return render();
    probe('image'+i,function(url){{
      if(url){{found.push(url); miss=0;}} else miss++;
      scan(i+1);
    }});
  }})(1);
  var lb=document.getElementById('lb'), lbi=document.getElementById('lb-img'), lbc=document.getElementById('lb-cap'), cur=0, lastFocus=null;
  function render(){{
    if(!found.length) return;
    var grid=document.getElementById('gal-grid'); grid.innerHTML='';
    found.forEach(function(url,i){{
      var f=document.createElement('figure'); f.className='g-tile';
      var b=document.createElement('button'); b.type='button'; b.setAttribute('aria-label','Agrandir la vue '+(i+1));
      var im=document.createElement('img'); im.src=url; im.alt='Vue '+(i+1); im.loading='lazy';
      b.appendChild(im); f.appendChild(b);
      var c=document.createElement('figcaption'); c.innerHTML='<b>Vue '+(i+1)+'</b>'; f.appendChild(c);
      b.addEventListener('click',function(){{openLb(i);}});
      grid.appendChild(f);
    }});
    document.getElementById('gal-hint').textContent='Pour ajouter une vue, déposez image'+(found.length+1)+'.png dans le dossier img.';
  }}
  function showLb(){{lbi.src=found[cur]; lbi.alt='Vue '+(cur+1); lbc.textContent='Vue '+(cur+1)+'  ('+(cur+1)+' / '+found.length+')';}}
  function openLb(i){{cur=i; lastFocus=document.activeElement; lb.hidden=false; showLb(); document.getElementById('lb-x').focus();}}
  function closeLb(){{lb.hidden=true; if(lastFocus) lastFocus.focus();}}
  function step(d){{cur=(cur+d+found.length)%found.length; showLb();}}
  document.getElementById('lb-x').addEventListener('click',closeLb);
  document.getElementById('lb-prev').addEventListener('click',function(){{step(-1);}});
  document.getElementById('lb-next').addEventListener('click',function(){{step(1);}});
  lb.addEventListener('click',function(e){{if(e.target===lb) closeLb();}});
  document.addEventListener('keydown',function(e){{
    if(lb.hidden) return;
    if(e.key==='Escape') closeLb(); else if(e.key==='ArrowLeft') step(-1); else if(e.key==='ArrowRight') step(1);
  }});
  document.querySelectorAll('.zoom').forEach(function(b){{
    b.addEventListener('click',function(){{
      var f=b.closest('.plan'), on=f.classList.toggle('big');
      b.setAttribute('aria-pressed',on); b.querySelector('span').textContent=on?'Ajuster':'Agrandir';
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
        fh.write('<!doctype html>\n<html lang="fr"><head><meta charset="utf-8">'
                 '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                 f'<meta name="author" content="{AUTHOR["name"]}"></head><body>\n' + body + "\n</body></html>\n")
    for f in os.listdir(os.path.join(ROOT, "assets", "photos")):
        shutil.copy(os.path.join(ROOT, "assets", "photos", f), os.path.join(dist, "img", f))
    gdir = os.path.join(ROOT, "assets", "gallery")
    for f in sorted(os.listdir(gdir)) if os.path.isdir(gdir) else []:
        if f.lower().rsplit(".", 1)[-1] in ("png", "jpg", "jpeg", "webp"):
            shutil.copy(os.path.join(gdir, f), os.path.join(dist, "img", f))
    for (num, fr, en, sc), o in zip(SHEETS, objs):
        svg = o.svg(o.title, standalone=True).replace("<style>", "<style>" + LIGHT_SVG_VARS)
        fonts = ('<style>@import url("https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@400;600;700'
                 '&amp;family=Cairo:wght@600&amp;display=swap");</style>')
        svg = svg.replace("<defs>", fonts + "<defs>", 1)
        slug = unicodedata.normalize("NFKD", fr.split(" - ")[0]).encode("ascii", "ignore").decode()
        name = f"{num}_{slug.replace(' ', '-').replace(chr(39), '')}.svg"
        with open(os.path.join(dist, "plans-svg", name), "w") as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
    readme = f"""Gharsa Foquiya - Piscine et jardins - dossier d'exécution
Version {VERSION} (indice {INDICE}) - {DATE}
Conception : {AUTHOR['name']} - {AUTHOR['url']} - {AUTHOR['email']} - WhatsApp {AUTHOR['whatsapp']}
Exécution : {CONTRACTOR['name']} - {CONTRACTOR['form']} - RC {CONTRACTOR['rc']} {CONTRACTOR['tribunal']} - ICE {CONTRACTOR['ice']}
            {CONTRACTOR['address']} - Tél. {CONTRACTOR['phones']} - {CONTRACTOR['emails']}

index.html        Dossier complet : site, plans, descriptif, phasage, devis, planning, lexique
plans-svg/        Planches PL-01 à PL-{len(SHEETS):02d} (format A3, imprimer à 100 %)
img/              Photos du site et image de synthèse
                  + cover.png (couverture) et image1.png, image2.png, image3.png... (galerie) :
                  déposez-les dans img/, ils s'affichent automatiquement à l'ouverture de index.html

Ouvrir index.html dans un navigateur (connexion internet pour les polices).
"""
    with open(os.path.join(dist, "LISEZMOI.txt"), "w") as fh:
        fh.write(readme)
    rel = os.path.join(os.path.dirname(ROOT), "releases")
    os.makedirs(rel, exist_ok=True)
    zpath = os.path.join(rel, f"AbodyStudio_Gharsa-Foquiya_Piscine-Jardins_v{VERSION}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fn in os.walk(dist):
            for f in sorted(fn):
                if f == "index.body.html":
                    continue
                p = os.path.join(dp, f)
                z.write(p, os.path.join(f"Piscine-Jardins_v{VERSION}", os.path.relpath(p, dist)))
    print("built", dist, "zip", zpath, os.path.getsize(zpath))


if __name__ == "__main__":
    main()
