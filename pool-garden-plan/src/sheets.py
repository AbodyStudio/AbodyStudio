"""A3 drawing sheets (SVG, millimetres) in Moroccan plan style.

Author: AbodyStudio Limited - https://abodystudio.com/
"""
import math
from model import *  # noqa: F401,F403

W, H = 420, 297
BAND = 315          # cartouche band starts here (right side)


def f2(x):
    return f"{x:.2f}"


class S:
    """Tiny SVG builder; all coordinates in sheet millimetres."""

    def __init__(self, sid):
        self.id = sid
        self.o = []
        self.k = 1.0

    def add(self, s):
        self.o.append(s)

    def line(self, a, b, c="k w2"):
        self.add(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" class="{c}"/>')

    def pl(self, pts, c="k w2", close=False):
        tag = "polygon" if close else "polyline"
        p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        self.add(f'<{tag} points="{p}" class="{c}"/>')

    def rect(self, x, y, w, h, c="k w2"):
        self.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" class="{c}"/>')

    def circ(self, x, y, r, c="k w2"):
        self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" class="{c}"/>')

    def t(self, x, y, s, c="t", a="middle", rot=0, size=None):
        st = f' style="font-size:{size}px"' if size else ""
        tr = f' transform="rotate({rot:.2f} {x:.2f} {y:.2f})"' if rot else ""
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" class="{c}" text-anchor="{a}"{tr}{st}>{s}</text>')

    def dim(self, a, b, off, label=None, c="k w1", size=2.9):
        """Dimension line with 45 deg ticks; off = signed offset (mm) to the left of a->b."""
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return
        ux, uy = dx / L, dy / L
        nx, ny = uy, -ux
        if off < 0:
            pass
        pa = (a[0] + nx * off, a[1] + ny * off)
        pb = (b[0] + nx * off, b[1] + ny * off)
        sg = 1 if off >= 0 else -1
        ext = 1.2
        self.line((a[0] + nx * sg * 0.8, a[1] + ny * sg * 0.8), (pa[0] + nx * sg * ext, pa[1] + ny * sg * ext), c)
        self.line((b[0] + nx * sg * 0.8, b[1] + ny * sg * 0.8), (pb[0] + nx * sg * ext, pb[1] + ny * sg * ext), c)
        self.line((pa[0] - ux * 1.2, pa[1] - uy * 1.2), (pb[0] + ux * 1.2, pb[1] + uy * 1.2), c)
        for p in (pa, pb):
            self.line((p[0] - (ux + nx) * 0.9, p[1] - (uy + ny) * 0.9), (p[0] + (ux + nx) * 0.9, p[1] + (uy + ny) * 0.9), "k w3")
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90.01 or ang <= -90:
            ang += 180
        r = math.radians(ang)
        tx, ty = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        # text sits above the line (screen-up relative to text direction)
        tnx, tny = math.sin(r), -math.cos(r)
        tx += tnx * 0.9
        ty += tny * 0.9
        self.t(tx, ty, label if label is not None else f"{L / self.k:.2f}", "t dimt", "middle", ang, size)

    def level(self, x, y, s, side="r", section=False):
        """Level marker: triangle + value."""
        if section:
            self.pl([(x - 1.4, y - 2.2), (x + 1.4, y - 2.2), (x, y)], "k w1 fk", True)
            self.line((x - 3, y), (x + 3, y), "k w1")
            self.t(x + (2.2 if side == "r" else -2.2), y - 2.6, s, "t lvl", "start" if side == "r" else "end")
        else:
            self.circ(x, y, 1.3, "k w1 fs")
            self.line((x - 1.3, y), (x + 1.3, y), "k w1")
            self.line((x, y - 1.3), (x, y + 1.3), "k w1")
            self.t(x + (2.2 if side == "r" else -2.2), y + 1.1, s, "t lvl", "start" if side == "r" else "end")

    def label(self, p, q, s, a="start", c="t lab"):
        """Leader line from point p to text anchor q."""
        self.circ(p[0], p[1], 0.45, "k w1 fk")
        self.line(p, q, "k w1")
        dx = 1 if a == "start" else -1
        self.line(q, (q[0] + dx * 2, q[1]), "k w1")
        self.t(q[0] + dx * 2.6, q[1] + 1.1, s, c, a)

    def svg(self, title, standalone=False):
        clip = f'<defs><clipPath id="{self.id}-clip"><rect x="16" y="11" width="{BAND - 18}" height="{H - 22}"/></clipPath></defs>'
        body = "\n".join(self.o)
        extra = (DEFS + "<style>" + SVG_CSS + "</style>") if standalone else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" class="sheet" role="img" '
                f'aria-label="{title}">{extra}{clip}<rect x="0" y="0" width="{W}" height="{H}" class="sh-bg"/>{body}</svg>')


DEFS = """<defs>
<pattern id="hx" width="2.2" height="2.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="2.2" class="pat"/></pattern>
<pattern id="cc" width="3" height="3" patternUnits="userSpaceOnUse"><circle cx="0.8" cy="0.8" r="0.22" class="patf"/><circle cx="2.2" cy="2.1" r="0.16" class="patf"/><path d="M1.9 0.6 l0.5 0.4 -0.6 0.1z" class="patf"/></pattern>
<pattern id="ea" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.6" class="pat"/><line x1="2" y1="2" x2="2" y2="3.6" class="pat"/></pattern>
<pattern id="gr" width="3.2" height="3.2" patternUnits="userSpaceOnUse"><circle cx="0.9" cy="0.9" r="0.45" class="pat"/><circle cx="2.4" cy="2.3" r="0.35" class="pat"/></pattern>
<pattern id="st" width="5" height="4" patternUnits="userSpaceOnUse"><path d="M0.4 1.6 q1 -1.4 2.2 -0.2 q0.6 1 -0.6 1.6 q-1.4 0.4 -1.6 -1.4z" class="pat"/><path d="M3 3.2 q0.8 -1 1.7 0" class="pat"/></pattern>
<pattern id="gz" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M1 3 l0.3 -1 M1.6 3 l0 -1.2 M2.2 3 l-0.3 -1" class="patg"/></pattern>
<pattern id="tl" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M6 0 V6 H0" class="patt"/></pattern>
<marker id="ar" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L6 3 L0 6z" class="patk"/></marker>
</defs>"""
SVG_CSS = ""


# --------------------------------------------------------------------------
# Frame + cartouche (right-hand band, Moroccan practice)
# --------------------------------------------------------------------------

def frame(s, num, title, title_en, scale):
    s.rect(14, 9, W - 23, H - 18, "k w4")
    x0, x1 = BAND, W - 9
    s.line((x0, 9), (x0, H - 9), "k w4")
    cx = (x0 + x1) / 2
    y = 17
    s.t(cx, y, "ROYAUME DU MAROC", "t cb", size=4.2)
    s.t(cx, y + 6, "المملكة المغربية", "t ar", size=4.6)
    s.t(cx, y + 12, PROJECT["province"], "t cs")
    s.t(cx, y + 16.5, PROJECT["commune"], "t cs")
    s.line((x0, y + 20), (x1, y + 20), "k w2")
    s.t(x0 + 3, y + 26, "PROJET", "t cl", "start")
    s.t(cx, y + 32, "CONSTRUCTION D'UNE PISCINE", "t cb", size=3.6)
    s.t(cx, y + 37, "ET AMÉNAGEMENT DES ABORDS", "t cb", size=3.6)
    s.t(cx, y + 42, "Villa existante (RDC)", "t cs")
    s.line((x0, y + 46), (x1, y + 46), "k w2")
    s.t(x0 + 3, y + 52, "SITUATION", "t cl", "start")
    s.t(x0 + 3, y + 58, f"{PROJECT['lieu']} - Terrain dit « {PROJECT['terrain']} »", "t cs", "start")
    s.t(x0 + 3, y + 63, f"Superficie : {PROJECT['surface']} m² (plan topographique)", "t cs", "start")
    s.line((x0, y + 67), (x1, y + 67), "k w2")
    s.t(x0 + 3, y + 73, "MAÎTRE D'OUVRAGE", "t cl", "start")
    s.t(x0 + 3, y + 79, "Le propriétaire", "t cs", "start")
    s.line((x0, y + 83), (x1, y + 83), "k w2")
    s.t(x0 + 3, y + 89, "CONCEPTION", "t cl", "start")
    s.t(x0 + 3, y + 95.5, AUTHOR["name"], "t cb", "start", size=3.8)
    s.t(x0 + 3, y + 101, AUTHOR["web"] + " - " + AUTHOR["email"], "t cs", "start")
    s.t(x0 + 3, y + 105.5, "WhatsApp " + AUTHOR["whatsapp"], "t cs", "start")
    s.line((x0, y + 110), (x1, y + 110), "k w2")
    s.t(x0 + 3, y + 116, "VISA BET / ARCHITECTE", "t cl", "start")
    s.rect(x0 + 3, y + 119, x1 - x0 - 6, 26, "k w1 dash")
    s.t(cx, y + 134, "cachet et signature", "t cs mute")
    yb = H - 64
    s.line((x0, yb), (x1, yb), "k w3")
    s.t(x0 + 3, yb + 6, "PLAN", "t cl", "start")
    words = title.upper()
    if len(words) > 30:
        cut = words.rfind(" ", 0, 30)
        s.t(cx, yb + 13, words[:cut], "t ct")
        s.t(cx, yb + 19.5, words[cut + 1:], "t ct")
    else:
        s.t(cx, yb + 15, words, "t ct")
    s.t(cx, yb + 25, title_en, "t cs mute")
    yc = yb + 29
    s.line((x0, yc), (x1, yc), "k w2")
    cols = [("N°", num), ("ÉCHELLE", scale), ("INDICE", f"{INDICE} - v{VERSION}")]
    cw = (x1 - x0) / 3
    for i, (k, v) in enumerate(cols):
        xx = x0 + i * cw
        if i:
            s.line((xx, yc), (xx, yc + 14), "k w1")
        s.t(xx + cw / 2, yc + 5, k, "t cl")
        s.t(xx + cw / 2, yc + 11.5, v, "t cb", size=3.4 if i else 4.2)
    s.line((x0, yc + 14), (x1, yc + 14), "k w2")
    s.t(x0 + 3, yc + 19, f"Date : {DATE}", "t cs", "start")
    s.t(x1 - 3, yc + 19, "Phase : EXE", "t cs", "end")
    s.t(x0 + 3, yc + 23.6, "Cotes en mètres - niveaux / ±0.00 = sol fini RDC", "t cs mute", "start")


def north(s, x, y, ang, r=9):
    """North arrow; ang = rotation in degrees (0 = north up)."""
    s.add(f'<g transform="rotate({ang:.2f} {x:.2f} {y:.2f})">'
          f'<circle cx="{x}" cy="{y}" r="{r}" class="k w1"/>'
          f'<polygon points="{x},{y - r - 2} {x + 2.6},{y + 3} {x},{y + 1} {x - 2.6},{y + 3}" class="k w1 fk"/>'
          f'<text x="{x}" y="{y - r - 3.2}" class="t cb" text-anchor="middle">N</text></g>')


def band_north(s, ang, note=None):
    north(s, (BAND + W - 9) / 2, 192, ang, 10)
    s.t((BAND + W - 9) / 2, 212, "Nord (Lambert)", "t cs mute")
    if note:
        s.t((BAND + W - 9) / 2, 217, note, "t cs mute")


def tree(s, x, y, r, c="k w1 tree"):
    s.circ(x, y, r, c)
    s.circ(x, y, 0.35, "k w1 fk")


def table(s, x, y, cols, rows, widths, rh=4.6, head=True, size=None):
    tw = sum(widths)
    n = len(rows) + (1 if head else 0)
    s.rect(x, y, tw, rh * n, "k w2 fs")
    if head:
        s.rect(x, y, tw, rh, "k w2 fh")
    cx = x
    for w in widths[:-1]:
        cx += w
        s.line((cx, y), (cx, y + rh * n), "k w1")
    for i in range(1, n):
        s.line((x, y + rh * i), (x + tw, y + rh * i), "k w1")
    allr = ([cols] if head else []) + rows
    for ri, r in enumerate(allr):
        cx = x
        for ci, (cell, w) in enumerate(zip(r, widths)):
            cls = "t cb" if (head and ri == 0) else "t cs"
            if ci == 0 or (isinstance(cell, str) and not cell.replace('.', '').replace(' ', '').replace('-', '').isdigit() and len(cell) > 8):
                s.t(cx + 1.2, y + rh * ri + rh - 1.35, cell, cls, "start", size=size)
            else:
                s.t(cx + w - 1.2, y + rh * ri + rh - 1.35, cell, cls, "end", size=size)
            cx += w


# --------------------------------------------------------------------------
# Views
# --------------------------------------------------------------------------

class UV:
    """u to the right, v up."""

    def __init__(self, x0, y0, umin, vmax, sc):
        self.x0, self.y0, self.umin, self.vmax, self.k = x0, y0, umin, vmax, 1000 / sc

    def __call__(self, u, v):
        return (self.x0 + (u - self.umin) * self.k, self.y0 + (self.vmax - v) * self.k)


class XY:
    def __init__(self, x0, y0, xmin, ymax, sc):
        self.x0, self.y0, self.xmin, self.ymax, self.k = x0, y0, xmin, ymax, 1000 / sc

    def __call__(self, X, Y):
        return (self.x0 + (X - self.xmin) * self.k, self.y0 + (self.ymax - Y) * self.k)

    def uv(self, u, v):
        return self(*to_xy(u, v))


def rect_uv(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


# angle of the u axis on a north-up sheet (screen degrees)
U_ANG = BEARING_U - 90          # 44.6 deg, clockwise on screen


# ==========================================================================
# PL-01  Plan de masse 1/250 (north up, on the survey)
# ==========================================================================

def pl01():
    s = S("p1")
    V = XY(26, 14, 444596.0, 535120.0, 250)
    P = lambda u, v: V.uv(u, v)
    s.add(f'<g clip-path="url(#{s.id}-clip)">')
    # public road (6.00 m) offset outward from B4..B10
    road = [b for b in BORNES_UV if b[0] in ("B4", "B5", "B6", "B7", "B8", "B9", "B10")]
    inner = [(u, v) for _, u, v in road]
    inner = [(inner[0][0] + 6, inner[0][1] - 1.0)] + inner + [(inner[-1][0] - 6, inner[-1][1] + 1.2)]
    outer = [(u, v - 6.0) for u, v in inner]
    s.pl([P(*p) for p in inner], "k w1 dash")
    s.pl([P(*p) for p in outer], "k w1 dash")
    mid = P(8, -3.2)
    s.t(mid[0], mid[1], "CHEMIN PUBLIC (6.00 m)", "t lab road", "middle", U_ANG - 180 + 180)
    # parcel
    pts = [V(x, y) for _, x, y in BORNES]
    s.pl(pts, "k w4 parcel", True)
    for (n, x, y), (a, b, L) in zip(BORNES, edge_lengths()):
        px, py = V(x, y)
        s.circ(px, py, 0.9, "k w1 fs")
        s.t(px + 1.6, py - 1.4, n, "t borne", "start")
        if L > 9:
            nx_ = [bb for bb in BORNES if bb[0] == b][0]
            qx, qy = V(nx_[1], nx_[2])
            ang = math.degrees(math.atan2(qy - py, qx - px))
            if ang > 90 or ang < -90:
                ang += 180
            s.t((px + qx) / 2, (py + qy) / 2 - 1.6, f"{L:.2f}", "t dimt borne", "middle", ang)
    # driveway (gravel), 3.00 m along SE fence
    v_end = 40.0
    dpoly = [(_bx, _by) for _bx, _by in [(u_se(1.2), 1.2), (u_se(v_end), v_end), (u_drive(v_end), v_end), (u_drive(1.0), 1.0)]]
    s.pl([P(*p) for p in dpoly], "k w1 fgr", True)
    # chickens, gardens, orchard
    ch = [(u_nw(CHICKEN_V[0]) + 0.3, CHICKEN_V[0]), (NW_GARDEN_EDGE, CHICKEN_V[0]), (NW_GARDEN_EDGE, CHICKEN_V[1]), (u_nw(CHICKEN_V[1]) + 0.3, CHICKEN_V[1])]
    s.pl([P(*p) for p in ch], "k w1 dash fch", True)
    for (u, v) in [(2, 34), (7, 33), (12, 32), (17, 31), (21, 34), (4, 40), (9, 39), (14, 38), (19, 40), (0, 46), (6, 45), (11, 44), (16, 45), (21, 46), (1, 28), (20, 28), (-1, 9), (2, 6), (3, 11)]:
        x, y = P(u, v)
        tree(s, x, y, 1.6)
    # house (existing)
    hp = rect_uv(HOUSE["u0"], HOUSE["v0"], HOUSE["u1"], HOUSE["v1"])
    s.pl([P(*p) for p in hp], "k w3 fhx", True)
    s.pl([P(*p) for p in rect_uv(STAIR["u0"], STAIR["v0"], STAIR["u1"], STAIR["v1"])], "k w2 fs", True)
    # deck + walkway, pool, tech room
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], DECK[0], HOUSE["u1"], DECK[1])], "k w1 fpv", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - WALK, POOL["v0"] - WALK, POOL["u1"] + WALK, POOL["v1"] + WALK)], "k w1 fpv", True)
    s.pl([P(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w3 fw", True)
    s.pl([P(*p) for p in rect_uv(TECH["u0"], TECH["v0"], TECH["u1"], TECH["v1"])], "red w3 fs", True)
    x, y = P(SOAKAWAY["u"], SOAKAWAY["v"])
    s.circ(x, y, SOAKAWAY["r"] * 4, "red w2 fs")
    s.add("</g>")
    # labels (rotated with the house)
    c = P((HOUSE["u0"] + HOUSE["u1"]) / 2, (HOUSE["v0"] + HOUSE["v1"]) / 2)
    s.t(c[0], c[1] - 1, "VILLA EXISTANTE", "t lab b", "middle", U_ANG)
    s.t(c[0] - 2.6, c[1] + 4.4, "RDC ±0.00", "t lab", "middle", U_ANG)
    c = P((POOL["u0"] + POOL["u1"]) / 2, (POOL["v0"] + POOL["v1"]) / 2)
    s.t(c[0], c[1] + 1, "PISCINE 10.00 × 5.00", "t lab b red-t", "middle", U_ANG)
    c = P((TECH["u0"] + TECH["u1"]) / 2 + 0.6, TECH["v0"] - 1.3)
    s.t(c[0], c[1], "Local technique", "t lab red-t", "middle", U_ANG)
    c = P(SOAKAWAY["u"] + 1.2, SOAKAWAY["v"] + 1.6)
    s.t(c[0], c[1], "Puits perdu", "t lab red-t", "start", U_ANG)
    c = P(u_drive(24) + 1.5, 24)
    s.t(c[0], c[1], "ALLÉE / PARKING 3.00", "t lab", "middle", U_ANG - 90 + 8.5)
    c = P((u_nw(22) + NW_GARDEN_EDGE) / 2, 22)
    s.t(c[0], c[1], "POULAILLER", "t lab", "middle", U_ANG - 90)
    c = P(NW_GARDEN_EDGE + 4.2, 17.0)
    s.t(c[0], c[1], "JARDIN", "t lab", "middle", U_ANG)
    c = P(13, 40.5)
    s.t(c[0], c[1], "VERGER EXISTANT (à conserver)", "t lab", "middle", U_ANG)
    c = P(19.5, 0.6)
    s.t(c[0] + 2, c[1] + 3, "Accès", "t lab b", "start")
    s.line(P(19.6, -2.2), P(19.6, 1.6), "k w2 arrow")
    # riverains
    for u, v, txt in [(14, 58, "Propriété riveraine"), (32, 30, "Propriété riveraine"), (-13, 34, "Propriété riveraine")]:
        x, y = P(u, v)
        s.t(x, y, txt, "t lab mute", "middle")
    # key distances
    s.dim(P(POOL["u0"] + 2.0, POOL["v1"]), P(POOL["u0"] + 2.0, 52.55), 0, f"{52.55 - POOL['v1']:.2f}")
    s.dim(P(u_nw(POOL["v1"] + 2), POOL["v1"] + 2), P(POOL["u0"], POOL["v1"] + 2), 0, f"{POOL['u0'] - u_nw(POOL['v1'] + 2):.2f}")
    s.dim(P(HOUSE["u0"] + 1.5, HOUSE["v0"] - BACK_GARDEN - 0.05), P(HOUSE["u0"] + 1.5, HOUSE["v0"]), 0, "≥3.00")
    # Lambert crosses
    for X in (444600, 444625, 444650):
        for Y in (535075, 535100):
            x, y = V(X, Y)
            if x < BAND - 4:
                s.line((x - 2.5, y), (x + 2.5, y), "k w1")
                s.line((x, y - 2.5), (x, y + 2.5), "k w1")
                s.t(x + 1, y - 1, f"{X}/{Y}", "t tiny", "start")
    north(s, 292, 30, 0)
    s.t(292, 46, "Lambert Nord Maroc", "t cs mute", "middle")
    # coordinates table (top-left free corner)
    rows = [(n, f"{x:.2f}", f"{y:.2f}") for n, x, y in BORNES]
    s.t(20, 18.5, "COORDONNÉES DES BORNES", "t cl", "start")
    table(s, 20, 20.5, ("Borne", "X", "Y"), rows, (11, 22, 22), rh=4.4)
    s.t(20, 79.5, f"Contenance : {PROJECT['surface']} m² - polygone recalculé : {PARCEL_AREA:.1f} m²", "t cs", "start")
    # surfaces table (bottom right of drawing area)
    hs = (HOUSE["u1"] - HOUSE["u0"]) * (HOUSE["v1"] - HOUSE["v0"])
    st = (STAIR["u1"] - STAIR["u0"]) * (STAIR["v1"] - STAIR["v0"])
    pav = Q["deck"] + (POOL_L + 2 * WALK) * (POOL_W + 2 * WALK) - POOL_L * POOL_W
    tech = (TECH["u1"] - TECH["u0"]) * (TECH["v1"] - TECH["v0"])
    drive = DRIVE_W * 39
    green = PARCEL_AREA - hs - st - POOL_L * POOL_W - pav - tech - drive
    rows = [
        ("Superficie du terrain", f"{PROJECT['surface']:.0f} m²"),
        ("Villa existante (emprise)", f"{hs:.0f} m²"),
        ("Escalier existant", f"{st:.1f} m²"),
        ("Plan d'eau piscine", f"{POOL_L * POOL_W:.0f} m²"),
        ("Plage + margelles", f"{pav:.1f} m²"),
        ("Local technique", f"{tech:.1f} m²"),
        ("Allée / parking gravier", f"{drive:.0f} m²"),
        ("Espaces verts, verger, poulailler", f"{green:.0f} m²"),
    ]
    s.t(196, 236.5, "TABLEAU DES SURFACES", "t cl", "start")
    table(s, 196, 238.5, ("Désignation", "Surface"), rows, (82, 32), rh=4.4, head=True)
    # legend
    lg = [("fhx", "Construction existante"), ("fw red", "Piscine projetée"), ("fpv", "Plage / margelles"),
          ("fgr", "Allée en gravier"), ("fch dash", "Parc à poules"), ("parcel", "Limite de propriété")]
    s.t(268, 60, "LÉGENDE", "t cl", "start")
    for i, (c_, txt) in enumerate(lg):
        yy = 63 + i * 7
        s.rect(268, yy, 8, 4.5, f"k w2 {c_}")
        s.t(279, yy + 3.6, txt, "t cs", "start")
    s.t(268, 112, "Position de la villa : d'après les cotes", "t cs mute", "start")
    s.t(268, 116.5, "du propriétaire - à confirmer par un", "t cs mute", "start")
    s.t(268, 121, "relevé topographique de l'existant.", "t cs mute", "start")
    frame(s, "PL-01", "Plan de masse", "Site plan on the survey", "1/250")
    s.title = "PL-01 Plan de masse"
    return s


# ==========================================================================
# PL-02  Plan d'aménagement des abords 1/100
# ==========================================================================

def pl02():
    s = S("p2")
    V = UV(19, 12, -5.4, 27.4, 100)
    P = V
    s.k = V.k
    s.add(f'<g clip-path="url(#{s.id}-clip)">')
    # boundaries
    s.pl([P(u_nw(-1), -1), P(u_nw(30), 30)], "k w4 parcel")
    s.pl([P(u_se(-1), -1), P(u_se(30), 30)], "k w4 parcel")
    road = sorted([(u, v) for n, u, v in BORNES_UV if n in ("B4", "B5", "B6", "B7", "B8", "B9")])
    s.pl([P(*p) for p in road], "k w4 parcel")
    # driveway
    dpoly = [(u_se(0.9), 0.9), (u_se(30), 30), (u_drive(30), 30), (u_drive(0.9), 0.9)]
    s.pl([P(*p) for p in dpoly], "k w1 fgr", True)
    # lawn areas
    s.pl([P(*p) for p in rect_uv(NW_GARDEN_EDGE, FRONT_GARDEN[0], HOUSE["u0"], 30)], "k w1 fgz", True)
    s.pl([P(*p) for p in [(HOUSE["u1"], FRONT_GARDEN[0]), (u_drive(FRONT_GARDEN[0]), FRONT_GARDEN[0]), (u_drive(30), 30), (HOUSE["u1"], 30)]], "k w1 fgz", True)
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], POOL["v1"] + WALK, HOUSE["u1"], 30)], "k w1 fgz", True)
    # back + side gardens of house
    s.pl([P(*p) for p in rect_uv(u_nw(3), 0.2, HOUSE["u0"], FRONT_GARDEN[0])], "k w1 fgz", True)
    # chickens
    ch = rect_uv(u_nw(CHICKEN_V[0]) + 0.3, CHICKEN_V[0], NW_GARDEN_EDGE, CHICKEN_V[1])
    s.pl([P(*p) for p in ch], "k w2 dash fch", True)
    s.pl([P(*p) for p in rect_uv(u_nw(26) + 0.5, 26.4, u_nw(26) + 2.5, 28.4)], "k w2 fs", True)
    # house
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], HOUSE["v0"], HOUSE["u1"], HOUSE["v1"])], "k w4 fhx", True)
    s.pl([P(*p) for p in rect_uv(STAIR["u0"], STAIR["v0"], STAIR["u1"], STAIR["v1"])], "k w2 fs", True)
    for i in range(1, 18):
        vv = STAIR["v1"] - i * STAIR_LEN / 18
        s.line(P(STAIR["u0"], vv), P(STAIR["u1"], vv), "k w1")
    s.line(P((STAIR["u0"] + STAIR["u1"]) / 2, STAIR["v1"] - 0.2), P((STAIR["u0"] + STAIR["u1"]) / 2, STAIR["v0"] + 0.4), "k w1 arrow")
    # awning (above, dashed)
    a = AWNING
    cx, cy = P(a["uc"], HOUSE["v1"])
    r = a["r"] * V.k
    s.add(f'<path d="M{cx - r:.2f} {cy:.2f} A {r:.2f} {a["depth"] * V.k:.2f} 0 0 1 {cx + r:.2f} {cy:.2f}" class="k w1 dash"/>')
    # front garden + steps
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], FRONT_GARDEN[0], HOUSE["u1"], FRONT_GARDEN[1])], "k w1 fgz", True)
    sd = STEPS_DOOR
    for i in range(sd["n"]):
        vv = FRONT_GARDEN[0] + 0.15 + i * sd["tread"]
        s.pl([P(*p) for p in rect_uv(sd["uc"] - sd["w"] / 2, vv, sd["uc"] + sd["w"] / 2, vv + sd["tread"])], "k w1 fs", True)
    for k in range(9):
        uu = HOUSE["u0"] + 0.8 + k * 1.3
        if abs(uu - sd["uc"]) > 1.3:
            x, y = P(uu, FRONT_GARDEN[0] + 0.7)
            s.circ(x, y, 3.2, "k w1 shrub")
    # channel drain
    s.rect(*P(HOUSE["u0"], FRONT_GARDEN[1] + 0.08), (HOUSE["u1"] - HOUSE["u0"]) * V.k, 0.16 * V.k, "k w2 fk")
    # deck
    s.pl([P(*p) for p in rect_uv(HOUSE["u0"], DECK[0], HOUSE["u1"], DECK[1])], "k w2 ftl", True)
    for i in range(4):
        u = POOL["u0"] + 0.9 + i * 2.35
        x, y = P(u, DECK[1] - 0.25)
        s.rect(x, y, 0.72 * V.k, 2.0 * V.k, "k w1 fs")
        s.line((x, y + 5), (x + 7.2, y + 5), "k w1")
    x, y = P(POOL["u0"] + 0.9 + 4 * 2.35 - 0.2, DECK[1] - 1.1)
    s.circ(x, y, 13, "k w1 dash")
    # walkway with 50x50 coping
    s.pl([P(*p) for p in rect_uv(POOL["u0"] - WALK, POOL["v0"] - WALK, POOL["u1"] + WALK, POOL["v1"] + WALK)], "k w2 fs", True)
    for i in range(int(POOL_L / 0.5) + 1):
        u = POOL["u0"] + i * 0.5
        s.line(P(u, POOL["v0"] - WALK), P(u, POOL["v0"]), "k w1")
        s.line(P(u, POOL["v1"]), P(u, POOL["v1"] + WALK), "k w1")
    for i in range(int(POOL_W / 0.5) + 1):
        v = POOL["v0"] + i * 0.5
        s.line(P(POOL["u0"] - WALK, v), P(POOL["u0"], v), "k w1")
        s.line(P(POOL["u1"], v), P(POOL["u1"] + WALK, v), "k w1")
    # pool
    s.pl([P(*p) for p in rect_uv(POOL["u0"], POOL["v0"], POOL["u1"], POOL["v1"])], "red w4 fw", True)
    for i in range(STEP["n_tread"]):
        uu = POOL["u1"] - STEP["tread"] * (i + 1)
        s.line(P(uu, POOL["v0"]), P(uu, POOL["v0"] + STEP["width"]), "k w1")
    s.line(P(POOL["u1"] - STEP["tread"] * 4, POOL["v0"] + STEP["width"]), P(POOL["u1"], POOL["v0"] + STEP["width"]), "k w1")
    # tech room
    s.pl([P(*p) for p in rect_uv(TECH["u0"], TECH["v0"], TECH["u1"], TECH["v1"])], "red w3 fcc", True)
    s.pl([P(*p) for p in rect_uv(TECH["u0"] + TECH_WALL, TECH["v0"] + TECH_WALL, TECH["u1"] - TECH_WALL, TECH["v1"] - TECH_WALL)], "k w1 fs", True)
    # shower
    sh = SHOWER
    s.pl([P(*p) for p in rect_uv(sh["u"] - sh["s"] / 2, sh["v"] - sh["s"] / 2, sh["u"] + sh["s"] / 2, sh["v"] + sh["s"] / 2)], "k w1 ftl", True)
    x, y = P(sh["u"], sh["v"])
    s.circ(x, y, 1.6, "k w1 fs")
    # hedge along the driveway
    for k in range(12):
        v = FRONT_GARDEN[0] + 0.8 + k * 1.0
        x, y = P(u_drive(v) - 0.45, v)
        s.circ(x, y, 3.6, "k w1 shrub")
    # bollards
    for (u, v) in [(u_drive(15) - 1.1, 15), (u_drive(19) - 1.1, 19), (u_drive(23) - 1.1, 23), (HOUSE["u0"] + 0.4, FRONT_GARDEN[1] - 0.4), (HOUSE["u1"] - 0.4, FRONT_GARDEN[1] - 0.4), (POOL["u0"] - 1.2, POOL["v1"] + 1.0), (POOL["u1"] + 1.2, POOL["v1"] + 1.0)]:
        x, y = P(u, v)
        s.circ(x, y, 1.2, "k w1 fk")
    # optional safety fence
    fo = FENCE_OFFSET + WALK
    fpts = [(HOUSE["u0"], HOUSE["v1"]), (HOUSE["u0"] - 0.0, POOL["v1"] + fo), (HOUSE["u1"] + 0.5, POOL["v1"] + fo), (HOUSE["u1"] + 0.5, HOUSE["v1"])]
    s.pl([P(*p) for p in fpts], "red w2 fence")
    # orchard trees
    for (u, v) in [(-2.5, 6.5), (0.5, 5.0), (2.5, 8.0), (0, 11.5), (7.6, 26.6), (11.6, 26.9), (15.6, 26.6)]:
        x, y = P(u, v)
        tree(s, x, y, 7)
    # Intex footprint (to remove, yellow)
    s.pl([P(*p) for p in rect_uv(POOL["u0"] + 1.2, DECK[1] - 1.6, POOL["u0"] + 1.2 + 7.32, DECK[1] - 1.6 + 3.66)], "demo w2", True)
    s.add("</g>")
    # labels
    def lab(u, v, txt, c="t lab", rot=0, a="middle"):
        x, y = P(u, v)
        s.t(x, y, txt, c, a, rot)
    hc = ((HOUSE["u0"] + HOUSE["u1"]) / 2, (HOUSE["v0"] + HOUSE["v1"]) / 2)
    lab(hc[0], hc[1] + 0.6, "VILLA EXISTANTE - RDC", "t lab b")
    lab(hc[0], hc[1] - 0.4, "(attentes R+1 existantes)", "t lab")
    lab(STAIR["u1"] + 0.25, (STAIR["v0"] + STAIR["v1"]) / 2, "Escalier existant", "t lab", -90)
    lab(a["uc"] + 2.6, HOUSE["v1"] + 0.12, "Auvent existant (au-dessus)", "t lab mute", 0, "start")
    lab(HOUSE["u0"] + 0.3, FRONT_GARDEN[0] + 1.6, "Jardinière plantée 2.00", "t lab", 0, "start")
    lab(HOUSE["u1"] - 0.2, FRONT_GARDEN[1] - 0.3, "Caniveau à grille", "t lab", 0, "end")
    lab(HOUSE["u0"] + 0.3, DECK[0] + 0.45, "PLAGE SOLARIUM 2.50 (transats)", "t lab b", 0, "start")
    lab((POOL["u0"] + POOL["u1"]) / 2, (POOL["v0"] + POOL["v1"]) / 2 + 0.4, "PISCINE 10.00 × 5.00", "t lab b red-t")
    lab((POOL["u0"] + POOL["u1"]) / 2, (POOL["v0"] + POOL["v1"]) / 2 - 0.6, "prof. 1.20 → 1.60 - V ≈ 67 m³", "t lab red-t")
    lab(POOL["u1"] - 0.75, POOL["v0"] + 1.0, "Escalier", "t lab", -90)
    lab((TECH["u0"] + TECH["u1"]) / 2, TECH["v1"] + 0.35, "Local technique", "t lab red-t")
    lab((TECH["u0"] + TECH["u1"]) / 2, TECH["v0"] - 0.75, "2.40 × 2.00", "t lab red-t")
    lab((NW_GARDEN_EDGE + POOL["u0"]) / 2 - 0.6, POOL["v1"] + 2.4, "JARDIN", "t lab b")
    lab((u_nw(22) + NW_GARDEN_EDGE) / 2 + 0.15, 22, "PARC À POULES", "t lab b", -90)
    lab(u_nw(26) + 1.5, 28.9, "Abri poules", "t lab")
    lab(u_drive(8) + 1.55, 8, "ALLÉE / PARKING (gravier)", "t lab b", -90 + 8.5)
    lab(u_drive(19) - 1.95, 17.4, "Jardin latéral", "t lab", 0)
    lab(SHOWER["u"] + 0.75, SHOWER["v"] - 0.15, "Douche", "t lab", 0, "start")
    lab((HOUSE["u0"] + HOUSE["u1"]) / 2, POOL["v1"] + 3.1, "Verger existant (agrumes, à conserver)", "t lab")
    lab(HOUSE["u1"] + 0.7, POOL["v1"] + 0.45, "Clôture sécurité", "t lab red-t", 0, "start")
    lab(HOUSE["u1"] + 0.7, POOL["v1"] + 0.05, "h 1.20 (option)", "t lab red-t", 0, "start")
    lab(HOUSE["u0"] + 2.0, 1.7, "JARDIN ARRIÈRE (existant)", "t lab", 0, "start")
    lab(POOL["u0"] + 1.35, DECK[1] + 1.82, "Piscine hors-sol existante (position approx.) : à déposer", "t tiny2 demo-t", 0, "start")
    # dimension chains (v, left of pool zone)
    ux = HOUSE["u0"] - 0.0
    chain_v = [HOUSE["v1"], FRONT_GARDEN[1], DECK[1], POOL["v0"], POOL["v1"], POOL["v1"] + WALK]
    for a_, b_ in zip(chain_v, chain_v[1:]):
        s.dim(P(ux, a_), P(ux, b_), 6.5, f"{b_ - a_:.2f}")
    s.dim(P(ux, HOUSE["v1"]), P(ux, POOL["v0"]), 13, f"{POOL['v0'] - HOUSE['v1']:.2f}")
    s.dim(P(HOUSE["u0"], HOUSE["v0"]), P(HOUSE["u0"], HOUSE["v1"]), 6.5, f"{HOUSE['v1'] - HOUSE['v0']:.2f}*")
    s.dim(P(HOUSE["u0"] + 1.0, _road_v_at(HOUSE["u0"] + 1.0)), P(HOUSE["u0"] + 1.0, HOUSE["v0"]), 0, f"{HOUSE['v0'] - _road_v_at(HOUSE['u0'] + 1.0):.2f}")
    # u chain above the pool
    vy = POOL["v1"] + WALK
    chain_u = [u_nw(vy + 1.6), NW_GARDEN_EDGE, POOL["u0"], POOL["u1"], u_drive(vy + 1.6), u_se(vy + 1.6)]
    labels = [None, "8.00", "10.00", None, "3.00"]
    for (a_, b_), lb in zip(zip(chain_u, chain_u[1:]), labels):
        s.dim(P(a_, vy + 1.6), P(b_, vy + 1.6), 0, lb)
    # house width and pool offsets (between house and pool)
    s.dim(P(HOUSE["u0"], HOUSE["v0"]), P(HOUSE["u1"], HOUSE["v0"]), -5, "12.00")
    s.dim(P(HOUSE["u0"], POOL["v0"] - WALK - 0.05), P(POOL["u0"], POOL["v0"] - WALK - 0.05), -3, "1.00")
    s.dim(P(POOL["u1"], POOL["v0"] - WALK - 0.05), P(HOUSE["u1"], POOL["v0"] - WALK - 0.05), -3, "1.00")
    s.dim(P(STAIR["u1"], STAIR["v0"] + 0.2), P(u_drive(STAIR["v0"] + 0.2), STAIR["v0"] + 0.2), 0, f"{u_drive(STAIR['v0'] + 0.2) - STAIR['u1']:.2f}")
    s.dim(P(HOUSE["u1"], HOUSE["v0"] + 0.4), P(u_drive(HOUSE["v0"] + 0.4), HOUSE["v0"] + 0.4), 0, f"{u_drive(HOUSE['v0'] + 0.4) - HOUSE['u1']:.2f}")
    # levels
    x, y = P(hc[0] + 3.2, hc[1] - 2.2)
    s.level(x, y, "±0.00")
    x, y = P(HOUSE["u0"] + 0.35, DECK[0] + 0.9)
    s.level(x, y, f"{LV['deck_low']:+.2f}")
    x, y = P(POOL["u0"] + 0.5, POOL["v1"] + 0.25)
    s.level(x, y, f"{LV['coping']:+.2f}")
    x, y = P(POOL["u1"] - 2.3, POOL["v1"] - 0.7)
    s.level(x, y, f"eau {LV['water']:+.2f}")
    band_north(s, -U_ANG, "axe façade : 134.6° (gisement)")
    # section marks
    for (u, v0_, v1_, nm) in [(POOL["u0"] + FITTINGS["drains"][0][0], DECK[0] - 3.4, POOL["v1"] + 0.9, "B")]:
        a1, b1 = P(u, v0_), P(u, v1_)
        s.line(a1, b1, "k w1 axis")
        for pp, dy in ((a1, 1), (b1, -1)):
            s.circ(pp[0], pp[1], 2.4, "k w2 fs")
            s.t(pp[0], pp[1] + 1.1, nm, "t cb")
    s.t(20, 283.5, "* profondeur de la villa supposée 10.00 m - à relever. Les cotes non indiquées se lisent à l'échelle.", "t cs mute", "start")
    frame(s, "PL-02", "Plan d'aménagement des abords", "Garden and pool layout", "1/100")
    s.title = "PL-02 Plan d'aménagement"
    return s


def _road_v_at(u):
    from model import _road_v
    return _road_v(u)


# ==========================================================================
# PL-03  Plan du bassin 1/50
# ==========================================================================

def pool_xy(x, y):
    """pool-local (x from NW wall, y from SW wall) -> u, v"""
    return (POOL["u0"] + x, POOL["v0"] + y)


def pl03():
    s = S("p3")
    V = UV(36, 24, 5.45, 24.55, 50)
    P = lambda x, y: V(*pool_xy(x, y))
    k = V.k
    s.k = k
    # walkway coping
    s.pl([P(-WALK, -WALK), P(POOL_L + WALK, -WALK), P(POOL_L + WALK, POOL_W + WALK), P(-WALK, POOL_W + WALK)], "k w2 fs", True)
    for i in range(int(POOL_L / 0.5) + 1):
        s.line(P(i * 0.5, -WALK), P(i * 0.5, 0), "k w1")
        s.line(P(i * 0.5, POOL_W), P(i * 0.5, POOL_W + WALK), "k w1")
    for i in range(int(POOL_W / 0.5) + 1):
        s.line(P(-WALK, i * 0.5), P(0, i * 0.5), "k w1")
        s.line(P(POOL_L, i * 0.5), P(POOL_L + WALK, i * 0.5), "k w1")
    # structural wall (hidden under coping): dashed outer line
    s.pl([P(-0.23, -0.23), P(POOL_L + 0.23, -0.23), P(POOL_L + 0.23, POOL_W + 0.23), P(-0.23, POOL_W + 0.23)], "k w1 dash", True)
    # water
    s.pl([P(0, 0), P(POOL_L, 0), P(POOL_L, POOL_W), P(0, POOL_W)], "red w4 fw", True)
    # depth zones
    for x in (DEEP_FLAT, SLOPE_END):
        s.line(P(x, 0), P(x, POOL_W), "k w1 dash")
    # steps
    x0 = STEP["x0"]
    for i in range(STEP["n_tread"] + 1):
        xx = POOL_L - i * STEP["tread"]
        s.line(P(xx, 0), P(xx, STEP["width"]), "k w2")
    s.line(P(x0, STEP["width"]), P(POOL_L, STEP["width"]), "k w2")
    for i in range(STEP["n_tread"]):
        xx = POOL_L - (i + 0.5) * STEP["tread"]
        x_, y_ = P(xx, STEP["width"] / 2)
        s.t(x_, y_ + 1, f"{LV['coping'] - STEP['rise'] * (i + 1):+.2f}", "t lvl", "middle", -90)
    # slope arrow
    a1, b1 = P(SLOPE_END - 0.3, 3.6), P(DEEP_FLAT + 0.3, 3.6)
    s.line(a1, b1, "k w2 arrow")
    s.t((a1[0] + b1[0]) / 2, a1[1] - 1.8, f"pente {SLOPE_PCT:.1f} %", "t lab")
    for x, txt in [(0.75 - 0.3, f"fond {FLOOR_DEEP:+.2f}"), ((DEEP_FLAT + SLOPE_END) / 2, ""), (SLOPE_END + 0.5, f"fond {FLOOR_SHALLOW:+.2f}")]:
        if txt:
            x_, y_ = P(x, 4.4)
            s.level(x_, y_, txt)
    # fittings
    sym = []
    for i, (x, y) in enumerate(FITTINGS["skimmers"]):
        a_ = P(x - 0.42, y - 0.3)
        s.rect(a_[0], a_[1] - 0.6 * k, 0.42 * k, 0.6 * k, "k w2 fs")
        s.line(P(x, y - 0.25), P(x, y + 0.25), "k w3")
        sym.append((P(x - 0.2, y), f"SK{i + 1}"))
    for i, (x, y) in enumerate(FITTINGS["drains"]):
        c_ = P(x, y)
        s.circ(c_[0], c_[1], 0.15 * k, "k w2 fs")
        s.line((c_[0] - 2, c_[1]), (c_[0] + 2, c_[1]), "k w1")
        sym.append((c_, f"BF{i + 1}"))
    s.line(P(*FITTINGS["drains"][0]), P(*FITTINGS["drains"][1]), "k w1 dash")
    for i, (x, y) in enumerate(FITTINGS["returns"]):
        c_ = P(x, y)
        s.pl([(c_[0] - 1.6, c_[1] - 1.6), (c_[0] + 1.6, c_[1] - 1.6), (c_[0], c_[1] + 1.4)] if y >= POOL_W else
             [(c_[0] + 1.6, c_[1] - 1.6), (c_[0] + 1.6, c_[1] + 1.6), (c_[0] - 1.4, c_[1])], "k w1 fk", True)
        sym.append((c_, f"R{i + 1}"))
    for (x, y) in FITTINGS["vacuum"]:
        c_ = P(x, y)
        s.rect(c_[0] - 1.2, c_[1] - 1.2, 1.2, 2.4, "k w1 fk")
        sym.append((c_, "PB"))
    for i, (x, y) in enumerate(FITTINGS["lights"]):
        c_ = P(x, y)
        s.add(f'<path d="M{c_[0] - 2.4:.2f} {c_[1]:.2f} A 2.4 2.4 0 0 0 {c_[0] + 2.4:.2f} {c_[1]:.2f}" class="k w2 flt"/>')
        sym.append((c_, f"P{i + 1}"))
    for (x, y) in FITTINGS["ladder"]:
        a_, b_ = P(x - 0.25, y), P(x + 0.25, y)
        s.rect(a_[0], a_[1] - 0.45 * k, 0.5 * k, 0.45 * k, "k w1 fs")
        for j in range(3):
            s.line((a_[0], a_[1] - (j + 0.5) * 0.15 * k), (b_[0], b_[1] - (j + 0.5) * 0.15 * k), "k w1")
        sym.append((P(x, y + 0.3), "ECH"))
    for c_, nm in sym:
        s.t(c_[0] + 3.2, c_[1] - 2.4, nm, "t lab b")
    # dimensions - overall
    s.dim(P(0, POOL_W + WALK), P(POOL_L, POOL_W + WALK), 10, "10.00")
    s.dim(P(-WALK, POOL_W + WALK), P(POOL_L + WALK, POOL_W + WALK), 17, "11.00")
    s.dim(P(POOL_L + WALK, 0), P(POOL_L + WALK, POOL_W), -9, "5.00")
    s.dim(P(POOL_L + WALK, -WALK), P(POOL_L + WALK, POOL_W + WALK), -17, "6.00")
    # depth zones
    yb = -WALK
    chain = [0, DEEP_FLAT, SLOPE_END, STEP["x0"], POOL_L]
    for a_, b_ in zip(chain, chain[1:]):
        s.dim(P(a_, yb), P(b_, yb), -14, f"{b_ - a_:.2f}")
    # fittings positions along NE wall (returns) and SW wall (lights, ladder)
    ne = sorted([0] + [x for x, y in FITTINGS["returns"] if y >= POOL_W] + [POOL_L])
    for a_, b_ in zip(ne, ne[1:]):
        s.dim(P(a_, POOL_W), P(b_, POOL_W), 4.5, f"{b_ - a_:.2f}", size=2.6)
    sw = sorted([0] + [x for x, y in FITTINGS["lights"]] + [x for x, y in FITTINGS["ladder"]] + [STEP["x0"], POOL_L])
    for a_, b_ in zip(sw, sw[1:]):
        s.dim(P(a_, 0), P(b_, 0), -14, f"{b_ - a_:.2f}", size=2.6)
    nw = sorted([0] + [y for x, y in FITTINGS["skimmers"]] + [y for x, y in FITTINGS["vacuum"]] + [POOL_W])
    for a_, b_ in zip(nw, nw[1:]):
        s.dim(P(0, a_), P(0, b_), 15, f"{b_ - a_:.2f}", size=2.6)
    s.dim(P(POOL_L, 0), P(POOL_L, STEP["width"]), -4.2, "2.00", size=2.6)
    s.dim(P(POOL_L, STEP["width"]), P(POOL_L, FITTINGS["returns"][0][1]), -4.2, "1.50", size=2.6)
    s.dim(P(FITTINGS["drains"][0][0], FITTINGS["drains"][0][1]), P(FITTINGS["drains"][1][0], FITTINGS["drains"][1][1]), -4, "1.00", size=2.6)
    # section lines
    ya = 1.0
    for (pa, pb, nm) in [(P(-1.4, ya), P(POOL_L + 1.4, ya), "A"), (P(FITTINGS["drains"][0][0], -1.6), P(FITTINGS["drains"][0][0], POOL_W + 1.6), "B")]:
        s.line(pa, pb, "k w1 axis")
        for pp in (pa, pb):
            s.circ(pp[0], pp[1], 2.4, "k w2 fs")
            s.t(pp[0], pp[1] + 1.1, nm, "t cb")
    # labels
    x_, y_ = P(POOL_L / 2 - 0.4, 2.0)
    s.t(x_, y_, "BASSIN 10.00 × 5.00 - plan d'eau 50 m²", "t lab b red-t")
    s.t(x_, y_ + 5, f"Volume ≈ {Q['water_vol']:.0f} m³ - mosaïque pâte de verre 25 × 25", "t lab red-t")
    x_, y_ = P(-WALK - 0.1, POOL_W + WALK + 0.15)
    s.t(x_, y_, "Margelles 50 × 50 pierre reconstituée", "t lab", "start")
    x_, y_ = P(POOL_L + 0.5, -WALK - 1.45)
    s.t(x_, y_, "Côté villa : plage solarium 2.50, jardinière 2.00, façade", "t lab mute", "end")
    x_, y_ = P(-WALK, -WALK - 1.45)
    s.t(x_, y_, "Local technique à 3.55 m du bassin (côté NO)", "t lab mute", "start")
    band_north(s, -U_ANG)
    # legend
    lg = [("SK1-SK2", "Skimmers grande meurtrière (vers local technique)"),
          ("BF1-BF2", "Bondes de fond anti-vortex reliées, écart 1.00 m"),
          ("R1-R4", "Buses de refoulement, axe à -0.35 sous le plan d'eau"),
          ("PB", "Prise balai, -0.30 sous le plan d'eau"),
          ("P1-P3", "Projecteurs LED 12 V 30 W, axe à -0.60 sous le plan d'eau"),
          ("ECH", "Échelle inox 316L 3 marches"),
          ("", f"Plan d'eau {LV['water']:+.2f} - margelles {LV['coping']:+.2f} - eau 1.20 → 1.60 m")]
    s.t(32, 222, "ÉQUIPEMENTS DU BASSIN", "t cl", "start")
    table(s, 32, 224, ("Repère", "Désignation"), lg, (24, 118), rh=5.0)
    notes = ["Pièces à sceller posées avant coulage des voiles,",
             "colliers d'étanchéité prévus pour la membrane.",
             "Buses orientées vers les skimmers (rotation horaire).",
             "Marquage des profondeurs 1.20 / 1.60 et « Plongeon",
             "interdit » sur margelles.",
             "Bondes de fond : clapet de décompression dans le puisard."]
    s.t(184, 222, "NOTES", "t cl", "start")
    for i, n in enumerate(notes):
        s.t(184, 229 + i * 5, n, "t cs", "start")
    frame(s, "PL-03", "Plan du bassin - implantation des équipements", "Pool plan and fittings", "1/50")
    s.title = "PL-03 Plan du bassin"
    return s


# ==========================================================================
# PL-04  Coupes
# ==========================================================================

def pool_section(s, Z, X, xs, floor_at, cut_steps, show_drain=None, left_end=None):
    """Generic pool cross-section helper. X maps metres along the cut, Z maps level."""


def pl04():
    s = S("p4")
    # ---- A-A longitudinal (u axis), 1/50, cut 1.00 m from the SW wall, looking NE
    k = 20
    X = lambda x: 30 + (x + 1.2) * k            # x = pool-local from NW wall
    Z = lambda z: 22 + (0.35 - z) * k
    fin = FINISH
    xin0, xin1 = 0, POOL_L
    # earth around
    exc_l, exc_r = -WALL - fin - 0.5, POOL_L + WALL + fin + 0.5
    zb_deep = FLOOR_DEEP - fin - SLAB - BLIND - HERISSON
    zb_sh = FLOOR_SHALLOW - fin - SLAB - BLIND - HERISSON
    s.rect(X(-1.2), Z(LV["tn"]), (POOL_L + 2.4) * k, (LV["tn"] - (zb_deep - 0.35)) * k, "k w1 fea")
    # backfill gravel
    for xa, xb in ((exc_l, -WALL - fin), (POOL_L + WALL + fin, exc_r)):
        s.rect(X(xa), Z(LV["tn"]), (xb - xa) * k, (LV["tn"] - (zb_deep if xa < 0 else zb_sh)) * k, "k w1 fgr")
    # layers under slab, following the floor profile
    prof = [(x, floor_depth(x)) for x in (0, DEEP_FLAT, SLOPE_END, POOL_L)]
    xl, xr = -WALL - fin, POOL_L + WALL + fin
    def band(off_top, off_bot, cls):
        top = [(xl, prof[0][1] - off_top)] + [(x, z - off_top) for x, z in prof] + [(xr, prof[-1][1] - off_top)]
        bot = [(xr + (0.1 if off_bot > SLAB + fin + 0.01 else 0), prof[-1][1] - off_bot)] + [(x, z - off_bot) for x, z in reversed(prof)] + [(xl - (0.1 if off_bot > SLAB + fin + 0.01 else 0), prof[0][1] - off_bot)]
        s.pl([(X(a), Z(b)) for a, b in top + bot], cls, True)
    band(fin + SLAB + BLIND, fin + SLAB + BLIND + HERISSON, "k w1 fst")
    band(fin + SLAB, fin + SLAB + BLIND, "k w1 fs")
    band(fin, fin + SLAB, "k w3 fcc")
    # walls
    for xa in (-WALL - fin, POOL_L + fin):
        zbot = prof[0][1] - fin if xa < 0 else prof[-1][1] - fin
        s.rect(X(xa), Z(LV["beam_top"]), WALL * k, (LV["beam_top"] - zbot) * k, "k w3 fcc")
    # coping + deck
    for xa in (-WALL - fin - 0.27, POOL_L - 0.03):
        s.rect(X(xa), Z(LV["coping"]), 0.53 * k, 0.07 * k, "k w2 fs")
    s.rect(X(-WALL - fin - 1.2 + 0.0), Z(LV["deck_edge"]), (1.2 - 0.47) * k, 0.12 * k, "k w1 fs")
    s.rect(X(POOL_L + 0.5), Z(LV["deck_edge"]), 0.7 * k, 0.12 * k, "k w1 fs")
    # water
    wpts = [(0, LV["water"])] + [(x, z) for x, z in prof] + [(POOL_L, LV["water"])]
    steps_poly = [(POOL_L, LV["water"])]
    s.pl([(X(a), Z(b)) for a, b in wpts], "k w1 fw", True)
    # steps (cut at y = 1.00)
    sp = [(POOL_L, LV["coping"] - STEP["rise"])]
    for i in range(STEP["n_tread"]):
        xa = POOL_L - STEP["tread"] * (i + 1)
        z1 = LV["coping"] - STEP["rise"] * (i + 1)
        sp += [(xa, z1), (xa, z1 - STEP["rise"])]
    sp += [(POOL_L, FLOOR_SHALLOW)]
    s.pl([(X(a), Z(b)) for a, b in sp], "k w3 fcc", True)
    # skimmer in NW wall
    s.rect(X(-WALL - fin - 0.02), Z(LV["water"] + 0.08), (WALL + fin + 0.04) * k, 0.16 * k, "k w2 fs")
    s.t(X(-0.25), Z(LV["water"] + 0.12), "SK", "t lab b", "end")
    # drains (beyond)
    for (x, y) in FITTINGS["drains"][:1]:
        s.rect(X(x - 0.15), Z(FLOOR_DEEP - 0.0), 0.3 * k, 0.18 * k, "k w1 dash fs")
        s.t(X(x + 0.25), Z(FLOOR_DEEP - 0.12), "BF", "t lab b", "start")
    # pipe to tech room
    s.line((X(-WALL - fin), Z(FLOOR_DEEP - 0.12)), (X(-1.2), Z(FLOOR_DEEP - 0.12)), "k w2 pipe")
    s.t(X(-1.15), Z(FLOOR_DEEP - 0.12) - 1.4, "vers local tech.", "t tiny2", "start")
    # TN line
    s.line((X(-1.2), Z(LV["tn"])), (X(POOL_L + 1.2), Z(LV["tn"])), "k w2")
    # levels
    for z, txt, xx in [(LV["coping"], f"{LV['coping']:+.2f} margelle", POOL_L + 0.75), (LV["water"], f"{LV['water']:+.2f} eau", POOL_L - 1.6),
                       (FLOOR_SHALLOW, f"{FLOOR_SHALLOW:+.2f}", POOL_L - 1.9), (FLOOR_DEEP, f"{FLOOR_DEEP:+.2f}", 0.5),
                       (zb_deep, f"{zb_deep:+.2f} fond de fouille", 1.0)]:
        s.level(X(xx), Z(z), txt, section=True)
    # depth dims
    s.dim((X(0.3), Z(LV["water"])), (X(0.3), Z(FLOOR_DEEP)), 0, "1.60")
    s.dim((X(POOL_L - 2.2), Z(LV["water"])), (X(POOL_L - 2.2), Z(FLOOR_SHALLOW)), 0, "1.20")
    chain = [0, DEEP_FLAT, SLOPE_END, POOL_L]
    zz = Z(zb_deep - 0.35) + 5
    for a_, b_ in zip(chain, chain[1:]):
        s.dim((X(a_), zz), (X(b_), zz), 0, f"{b_ - a_:.2f}")
    s.t(X(POOL_L / 2), 16, "COUPE A-A  (longitudinale)  1/50", "t ct", "middle")
    # ---- B-B transversal (v axis), 1/100, through drains + house, looking NW
    k2 = 10
    v0 = 1.6
    Xb = lambda v: 30 + (v - v0) * k2
    Zb = lambda z: 148 + (4.3 - z) * k2
    vmax = POOL["v1"] + 4.0
    # ground
    s.rect(Xb(v0), Zb(LV["tn"] + 0.5), (vmax - v0) * k2, (LV["tn"] + 0.5 - (zb_deep - 0.4)) * k2, "k w1 fea")
    # house
    hv0, hv1 = HOUSE["v0"], HOUSE["v1"]
    s.rect(Xb(hv0), Zb(0), (hv1 - hv0) * k2, 0.20 * k2, "k w2 fcc")
    s.rect(Xb(hv0), Zb(LV["roof"]), (hv1 - hv0) * k2, 0.20 * k2, "k w2 fcc")
    for vv in (hv0, hv1 - 0.20):
        s.rect(Xb(vv), Zb(LV["roof"]), 0.20 * k2, (LV["roof"] + 0.6) * k2, "k w2 fhx")
    s.rect(Xb(hv0), Zb(LV["parapet"]), 0.15 * k2, (LV["parapet"] - LV["roof"]) * k2, "k w1 fs")
    s.rect(Xb(hv1 - 0.15), Zb(LV["parapet"]), 0.15 * k2, (LV["parapet"] - LV["roof"]) * k2, "k w1 fs")
    for vv in (hv0 + 0.1, hv1 - 0.1):
        s.line((Xb(vv), Zb(LV["parapet"])), (Xb(vv), Zb(LV["parapet"] + 0.5)), "red w2")
    s.rect(Xb(hv0), Zb(0.0), (hv1 - hv0) * k2, 0.6 * k2, "k w1 fhx")
    s.t(Xb((hv0 + hv1) / 2), Zb(1.6), "VILLA EXISTANTE", "t lab b")
    s.t(Xb((hv0 + hv1) / 2), Zb(1.6) + 4.5, "(non modifiée)", "t lab")
    s.t(Xb(hv1 - 0.3), Zb(LV["parapet"] + 0.7), "attentes R+1", "t lab red-t", "end")
    # ground profile in front of house
    gpts = [(v0, LV["tn"] + 0.45), (hv0, LV["tn"] + 0.45)]
    s.line((Xb(v0), Zb(LV["tn"] + 0.45)), (Xb(hv0), Zb(LV["tn"] + 0.45)), "k w2")
    fg0, fg1 = FRONT_GARDEN
    s.pl([(Xb(hv1), Zb(-0.30)), (Xb(fg1 - 0.2), Zb(LV["channel"])), (Xb(fg1), Zb(LV["channel"]))], "k w2")
    s.pl([(Xb(hv1), Zb(-0.30)), (Xb(fg1 - 0.2), Zb(LV["channel"])), (Xb(fg1 - 0.2), Zb(LV["tn"] - 0.3)), (Xb(hv1), Zb(LV["tn"] - 0.3))], "k w1 fgz", True)
    s.rect(Xb(fg1 - 0.2), Zb(LV["channel"]), 0.2 * k2, 0.25 * k2, "k w2 fk")
    # deck
    s.pl([(Xb(fg1), Zb(LV["deck_low"])), (Xb(POOL["v0"] - WALK), Zb(LV["deck_edge"])), (Xb(POOL["v0"] - WALK), Zb(LV["deck_edge"] - 0.12)), (Xb(fg1), Zb(LV["deck_low"] - 0.12))], "k w1 fs", True)
    # pool at B-B (x = drains, deep)
    zf = FLOOR_DEEP
    pv0, pv1 = POOL["v0"], POOL["v1"]
    s.rect(Xb(pv0 - WALL - fin - 0.5), Zb(LV["tn"]), (POOL_W + 2 * (WALL + fin + 0.5)) * k2, (LV["tn"] - (zf - fin - SLAB)) * k2, "k w1 fgr")
    s.rect(Xb(pv0 - WALL - fin - 0.5), Zb(zf - fin - SLAB), (POOL_W + 2 * (WALL + fin + 0.5)) * k2, (BLIND + HERISSON) * k2, "k w1 fst")
    s.rect(Xb(pv0 - WALL - fin), Zb(zf - fin), (POOL_W + 2 * (WALL + fin)) * k2, SLAB * k2, "k w2 fcc")
    for vv in (pv0 - WALL - fin, pv1 + fin):
        s.rect(Xb(vv), Zb(LV["beam_top"]), WALL * k2, (LV["beam_top"] - (zf - fin)) * k2, "k w2 fcc")
    s.rect(Xb(pv0), Zb(LV["water"]), POOL_W * k2, (LV["water"] - zf) * k2, "k w1 fw")
    for vv in (pv0 - WALK, pv1 - 0.03):
        s.rect(Xb(vv), Zb(LV["coping"]), 0.53 * k2, 0.07 * k2, "k w1 fs")
    for (x, y) in FITTINGS["drains"]:
        s.rect(Xb(pv0 + y - 0.15), Zb(zf), 0.3 * k2, 0.15 * k2, "k w1 fs")
    s.add(f'<path d="M{Xb(pv0 + 0.02):.2f} {Zb(LV["water"] - 0.6):.2f} a 1.4 1.4 0 0 1 0 2.8" class="k w1 flt"/>')
    s.line((Xb(pv1 + 0.5), Zb(LV["tn"])), (Xb(vmax), Zb(LV["tn"] - 0.15)), "k w2")
    tree(s, Xb(pv1 + 3.0), Zb(LV["tn"] + 1.9), 9)
    s.line((Xb(pv1 + 3.0), Zb(LV["tn"] - 0.08)), (Xb(pv1 + 3.0), Zb(LV["tn"] + 1.0)), "k w2")
    # perimeter drains
    for vv in (pv0 - WALL - fin - 0.3, pv1 + WALL + fin + 0.3):
        s.circ(Xb(vv), Zb(zf - fin - SLAB + 0.05), 0.6, "k w1 fs")
    # dims chain
    zz = Zb(zb_deep - 0.4) + 8
    ch = [hv1, fg1, DECK[1], pv0, pv1, pv1 + WALK]
    for a_, b_ in zip(ch, ch[1:]):
        s.dim((Xb(a_), zz), (Xb(b_), zz), 0, f"{b_ - a_:.2f}")
    s.dim((Xb(hv0), zz), (Xb(hv1), zz), 0, f"{hv1 - hv0:.2f}*")
    for z, txt, vv in [(0.0, "±0.00 RDC", hv1 + 0.4), (LV["roof"], f"{LV['roof']:+.2f}", hv1 + 0.4), (LV["deck_low"], f"{LV['deck_low']:+.2f}", fg1 + 0.6),
                       (LV["coping"], f"{LV['coping']:+.2f}", pv0 - WALK + 0.05), (LV["water"], f"{LV['water']:+.2f}", pv0 + 1.4), (zf, f"{zf:+.2f}", pv0 + 3.2),
                       (LV["tn"], f"{LV['tn']:+.2f} TN", pv1 + 1.3)]:
        s.level(Xb(vv), Zb(z), txt, section=True)
    s.t(Xb(fg0 + 1.0), Zb(LV["tn"] - 0.75), "Jardinière", "t lab", "middle")
    s.t(Xb(fg1 + 1.25), Zb(LV["deck_low"]) - 6, "Plage 1.5 %", "t lab", "middle")
    s.t(Xb(fg1 + 1.2), Zb(LV["channel"]) + 6.0, "Caniveau", "t lab", "middle")
    s.t(Xb((pv0 + pv1) / 2), Zb(LV["water"] - 0.8), "PISCINE", "t lab b red-t")
    s.t(Xb(pv1 + 3.0), Zb(LV["tn"] + 3.4), "Verger", "t lab", "middle")
    s.t(Xb((v0 + vmax) / 2), 136, "COUPE B-B  (transversale villa - jardin - piscine)  1/100", "t ct", "middle")
    s.t(20, 285, "* profondeur de la villa supposée - à relever. Niveaux du terrain naturel à confirmer par relevé.", "t cs mute", "start")
    frame(s, "PL-04", "Coupes A-A et B-B", "Sections A-A and B-B", "1/50 - 1/100")
    s.title = "PL-04 Coupes"
    return s


# ==========================================================================
# PL-05  Détail BA 1/20 + nomenclature
# ==========================================================================

def pl05():
    s = S("p5")
    k = 50  # 1/20
    X = lambda d: 40 + (d + 0.75) * k          # d: horizontal from inner face of rough wall (+ outward)
    Z = lambda z: 22 + (-0.55 - z) * k
    fin = FINISH
    zf = FLOOR_DEEP - fin            # rough floor
    zs = zf - SLAB
    zb = zs - BLIND
    zh = zb - HERISSON
    # earth
    s.rect(X(-0.75), Z(LV["tn"] + 0.05), (0.75 + 1.75) * k, (LV["tn"] + 0.05 - (zh - 0.15)) * k, "k w1 fea")
    s.rect(X(-0.75), Z(zh + 0.0), 2.5 * k, 0.15 * k, "k w1 fea")
    # gravel band + selected fill
    s.rect(X(WALL), Z(LV["tn"] - 0.10), 0.40 * k, (LV["tn"] - 0.10 - zb) * k, "k w1 fgr")
    s.rect(X(WALL + 0.40), Z(LV["tn"] - 0.10), 0.60 * k, (LV["tn"] - 0.10 - zb) * k, "k w1 fea2")
    # hérisson + blinding
    s.rect(X(-0.75), Z(zb), (0.75 + WALL + 1.0) * k, HERISSON * k, "k w1 fst")
    s.rect(X(-0.75), Z(zs), (0.75 + WALL + 0.1) * k, BLIND * k, "k w1 fs")
    # slab
    s.rect(X(-0.75), Z(zf), (0.75 + WALL) * k, SLAB * k, "k w3 fcc")
    # wall
    s.rect(X(0), Z(LV["beam_top"]), WALL * k, (LV["beam_top"] - zf) * k, "k w3 fcc")
    # finishes inside
    s.rect(X(-fin), Z(LV["beam_top"] - 0.02), fin * k, (LV["beam_top"] - 0.02 - zf) * k, "k w1 flt")
    s.rect(X(-0.75), Z(zf + fin), (0.75 - fin) * k, fin * k, "k w1 flt")
    s.pl([(X(-fin), Z(zf + fin + 0.05)), (X(-fin - 0.05), Z(zf + fin)), (X(-fin), Z(zf + fin))], "k w1 fs", True)
    # coping + bed + deck
    s.rect(X(-fin - 0.03), Z(LV["coping"]), 0.50 * k, 0.05 * k, "k w2 fs")
    s.rect(X(-fin + 0.0), Z(LV["coping"] - 0.05), (0.47) * k, 0.02 * k, "k w1 fk")
    s.rect(X(0.47 - fin), Z(LV["deck_edge"]), 0.75 * k, 0.12 * k, "k w1 fs")
    s.rect(X(0.47 - fin), Z(LV["deck_edge"] - 0.12), 0.75 * k, 0.10 * k, "k w1 fcc")
    # water
    s.rect(X(-0.75), Z(LV["water"]), (0.75 - fin) * k, (LV["water"] - (zf + fin)) * k, "k w1 fw op")
    # rebar: vertical L-bars both faces
    for d in (COVER + 0.006, WALL - COVER - 0.006):
        s.pl([(X(d), Z(LV["beam_top"] - 0.04)), (X(d), Z(zs + COVER)), (X(d - 0.45 if d < 0.1 else d - 0.45), Z(zs + COVER) if d < 0.1 else Z(zf - COVER))], "red w3 bar")
    s.pl([(X(WALL - COVER - 0.006), Z(LV["beam_top"] - 0.04)), (X(COVER + 0.006 + 0.1), Z(LV["beam_top"] - 0.04))], "red w2 bar")
    # horizontal bars (dots)
    z = zf + 0.12
    while z < LV["beam_top"] - 0.30:
        for d in (COVER + 0.018, WALL - COVER - 0.018):
            s.circ(X(d), Z(z), 0.55, "red w1 fred")
        z += 0.20
    # ring beam: 4 bars + stirrup
    rb_top, rb_bot = LV["beam_top"] - 0.05, LV["beam_top"] - 0.20
    s.rect(X(0.045), Z(rb_top + 0.01), (WALL - 0.09) * k, (rb_top - rb_bot + 0.02) * k, "red w1 bar")
    for d in (0.06, WALL - 0.06):
        for zz in (rb_top - 0.005, rb_bot + 0.005):
            s.circ(X(d), Z(zz), 0.65, "red w1 fred")
    # slab bars
    for zz in (zs + COVER, zf - COVER):
        s.line((X(-0.75), Z(zz)), (X(WALL - COVER), Z(zz)), "red w2 bar")
        d = -0.70
        while d < WALL - 0.05:
            s.circ(X(d), Z(zz + (0.012 if zz < zf - 0.1 else -0.012)), 0.5, "red w1 fred")
            d += 0.15
    # waterstop
    s.rect(X(0.08), Z(zf + 0.03), 0.04 * k, 0.03 * k, "k w1 fk")
    # perimeter drain
    s.circ(X(WALL + 0.20), Z(zb + 0.08), 0.05 * k, "k w2 fs")
    s.add(f'<path d="M{X(WALL + 0.02):.2f} {Z(zb + 0.25):.2f} L{X(WALL + 0.38):.2f} {Z(zb + 0.25):.2f} L{X(WALL + 0.38):.2f} {Z(zb - 0.0):.2f} L{X(WALL + 0.02):.2f} {Z(zb - 0.0):.2f}" class="k w1 dash"/>')
    # TN
    s.line((X(WALL + 1.0), Z(LV["tn"])), (X(1.75), Z(LV["tn"])), "k w2")
    # labels
    lx = X(1.85)
    L = [
        ((X(0.20), Z(LV["coping"] + 0.0)), "Margelle 50×50 pierre reconstituée, débord 3 cm"),
        ((X(0.05), Z(LV["coping"] - 0.06)), "Mortier de pose 2 cm"),
        ((X(0.8), Z(LV["deck_edge"] - 0.05)), "Plage : grès R11 sur forme BA 10 cm, pente 1.5 %"),
        ((X(0.10), Z(rb_top - 0.07)), "Chaînage 20×25 : 4 HA12 + cadres HA6 e=15"),
        ((X(WALL - 0.05), Z(-1.45)), "Voile BA 20 cm B25 + hydrofuge de masse"),
        ((X(COVER + 0.006), Z(-1.7)), "Verticales HA12 e=15 en L, 2 faces"),
        ((X(WALL - COVER - 0.018), Z(-1.95)), "Horizontales HA10 e=20, 2 faces"),
        ((X(WALL + 0.2), Z(-1.2)), "Gravier drainant 15/25 ép. 40 cm"),
        ((X(WALL + 0.7), Z(-1.0)), "Remblai sélectionné compacté (couches 20 cm)"),
        ((X(WALL + 0.20), Z(zb + 0.08)), "Drain Ø100 perforé + géotextile → puits perdu"),
        ((X(0.10), Z(zf + 0.045)), "Joint hydrogonflant de reprise"),
        ((X(-0.4), Z(zf - 0.1)), "Radier BA 20 cm : 2 nappes HA10 e=15"),
        ((X(-0.4), Z(zs - 0.04)), "Béton de propreté 8 cm (150 kg/m³)"),
        ((X(-0.4), Z(zb - 0.1)), "Hérisson pierres 40/80 ép. 20 cm"),
    ]
    L.sort(key=lambda it: it[0][1])
    for i, (p, txt) in enumerate(L):
        s.label(p, (lx, 30 + i * 9.6), txt)
    Lin = [((X(-fin / 2), Z(-1.3)), "Enduit hydrofuge 2 couches + membrane ciment flexible 2 couches + mosaïque 25×25 (colle C2TE S1, joint époxy)"),
           ((X(-fin - 0.03), Z(zf + fin + 0.02)), "Gorge 5×5 cm aux angles rentrants")]
    s.label(Lin[0][0], (X(-0.62), Z(-1.05)), "Revêtement :", "end")
    s.t(X(-0.62) - 4.6, Z(-1.05) + 5.2, "enduit hydrofuge", "t cs", "end")
    s.t(X(-0.62) - 4.6, Z(-1.05) + 9.4, "+ membrane flexible", "t cs", "end")
    s.t(X(-0.62) - 4.6, Z(-1.05) + 13.6, "+ mosaïque 25×25", "t cs", "end")
    s.label(Lin[1][0], (X(-0.62), Z(zf + 0.35)), "Gorge 5×5", "end")
    for z, txt in [(LV["coping"], f"{LV['coping']:+.2f}"), (LV["water"], f"{LV['water']:+.2f}"), (FLOOR_DEEP, f"{FLOOR_DEEP:+.2f}"), (zh, f"{zh:+.2f}")]:
        s.level(X(-0.55), Z(z), txt, "r", True)
    s.dim((X(0), Z(zh) + 9), (X(WALL), Z(zh) + 9), 0, "0.20")
    s.dim((X(WALL), Z(zh) + 9), (X(WALL + 0.4), Z(zh) + 9), 0, "0.40")
    s.dim((X(-0.75) - 4, Z(zf)), (X(-0.75) - 4, Z(zs)), 0, "0.20")
    s.t(X(0.5), 16, "DÉTAIL D1 - PAROI ET RADIER (grand fond)  1/20", "t ct")
    # bar schedule
    rows = [(str(r["pos"]), f"HA{r['d']}", str(r["n"]), f"{r['L']:.2f}", f"{r['kg']:.0f}") for r in Q["rebar"]]
    rows.append(("", "", "", "TOTAL", f"{Q['steel']:.0f} kg"))
    s.t(215, 168, "NOMENCLATURE DES ACIERS (FeE500)", "t cl", "start")
    table(s, 215, 170, ("Pos", "Ø", "Nb", "L (m)", "Poids kg"), rows, (12, 16, 16, 20, 24), rh=4.6)
    desc = [f"{r['pos']}  {r['desc']}" for r in Q["rebar"]]
    s.t(20, 192, "REPÈRES", "t cl", "start")
    for i, d in enumerate(desc):
        s.t(20 + (i // 7) * 92, 197 + (i % 7) * 4.3, d, "t tiny2", "start")
    notes = [
        "NOTES BÉTON ARMÉ",
        f"B25 dosé 350 kg/m³ CPJ 45, E/C ≤ 0.50, hydrofuge, vibré ({Q['c_total']:.1f} m³).",
        "Enrobage 4 cm face eau, 5 cm face terre. Recouvrements 50 Ø.",
        "Radier coulé en une fois, joint hydrogonflant avant voiles.",
        "Cure humide 7 jours minimum. Enduits après 21 à 28 jours.",
        f"Voile en console, pleine eau sans remblai : Mser ≈ {Q['m_ser']:.1f} kN.m/m,",
        f"σs HA12 e=15 ≈ {Q['sigma_s']:.0f} MPa : fissuration très préjudiciable OK.",
        f"Poids coque ≈ {Q['shell_weight']:.0f} kN : bassin vide soulevé si nappe",
        f"> {Q['float_head']:.2f} m au-dessus du radier → drain, clapet, ne pas vider l'hiver.",
        "Principe BAEL 91 mod. 99 / RPS 2000 (2011) - à valider par un BET agréé.",
    ]
    for i, n in enumerate(notes):
        s.t(20, 254 + i * 3.6, n, "t cb" if i == 0 else "t tiny2", "start")
    frame(s, "PL-05", "Détails béton armé et nomenclature des aciers", "RC details and bar schedule", "1/20")
    s.title = "PL-05 Détails BA"
    return s


SHEET_FUNCS = [pl01, pl02, pl03, pl04, pl05]
