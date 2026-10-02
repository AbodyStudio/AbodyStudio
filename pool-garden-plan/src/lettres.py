"""Montants en toutes lettres (orthographe traditionnelle), pour « Arrêté le présent devis à la somme de ».

Author: AbodyStudio Limited - https://abodystudio.com/
"""
UNITS = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
         "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
TENS = {2: "vingt", 3: "trente", 4: "quarante", 5: "cinquante", 6: "soixante"}


def _below_100(n, final):
    if n < 20:
        return UNITS[n]
    t, u = divmod(n, 10)
    if t in TENS:
        if u == 0:
            return TENS[t]
        return TENS[t] + (" et un" if u == 1 else "-" + UNITS[u])
    if t == 7:
        return "soixante" + (" et onze" if u == 1 else "-" + UNITS[10 + u])
    base = "quatre-vingt"
    if t == 8:
        return base + ("s" if final else "") if u == 0 else base + "-" + UNITS[u]
    return base + "-" + UNITS[10 + u]


def _below_1000(n, final):
    c, r = divmod(n, 100)
    out = []
    if c:
        if c == 1:
            out.append("cent")
        else:
            out.append(UNITS[c] + " cent" + ("s" if r == 0 and final else ""))
    if r:
        out.append(_below_100(r, final))
    return " ".join(out)


def en_lettres(n):
    n = int(round(n))
    if n == 0:
        return "zéro"
    out = []
    m, rest = divmod(n, 1_000_000)
    k, r = divmod(rest, 1000)
    if m:
        out.append(_below_1000(m, True) + (" millions" if m > 1 else " million"))
    if k:
        out.append("mille" if k == 1 else _below_1000(k, False) + " mille")
    if r:
        out.append(_below_1000(r, True))
    return " ".join(out)


if __name__ == "__main__":
    for x in (1, 21, 71, 80, 81, 91, 100, 180, 200, 280, 1000, 2000, 80000, 200000, 201000, 352200, 351219,
              1_000_000, 2_480_000, 99, 70, 77):
        print(x, en_lettres(x))
