# Pro-level case data for the three guides (3x3 CFOP, 2x2 Ortega + CLL,
# Pyraminx L4E / Oka). Every picture attribute is DERIVED here from the cubie
# simulator: state = inverse(algorithm) applied to a solved cube. The HTML
# generator (pro_blocks.py) reads only this module, and test_pro_cases.py
# proves every algorithm solves the case it is drawn with.
#
# Picture conventions (same as the hand-authored beginner diagrams):
#   c  = U face read back row -> front row, left -> right
#   b/f/l/r = side strips of the top layer along the same axes
#   colours: y w r o g b, x = grey (not relevant). Whole-cube rotations inside
#   an algorithm are handled by relabelling so the front centre is always green.
import re

from verify_algs import fresh, invert

LET = {'U': 'y', 'D': 'w', 'F': 'g', 'B': 'b', 'L': 'o', 'R': 'r'}
DIRS = {'U': (0, 1, 0), 'D': (0, -1, 0), 'F': (0, 0, 1), 'B': (0, 0, -1), 'L': (-1, 0, 0), 'R': (1, 0, 0)}


def normalize(alg):
    """Expand (...)2 groups, drop parentheses, U2' -> U2, collapse spaces."""
    alg = alg.replace('’', "'")
    alg = re.sub(r'\(([^()]*)\)2', lambda m: ' ' + ' '.join([m.group(1)] * 2) + ' ', alg)
    alg = alg.replace('(', ' ').replace(')', ' ')
    alg = re.sub(r"2'", '2', alg)
    return ' '.join(alg.split())


def state_for(alg):
    c = fresh()
    c.apply(invert(normalize(alg)))
    return c


def _frame(c):
    return {c.sticker(DIRS[f], DIRS[f]): f for f in 'UDFBLR'}


def st(c, pos, d):
    """Sticker colour letter, relabelled so the current centres read as home colours."""
    col = c.sticker(pos, d)
    if col is None:
        return 'x'
    return LET[_frame(c)[col]]


def mask(s):
    return ''.join('y' if ch == 'y' else 'x' for ch in s)


def u_face(c, n=3):
    rng = (-1, 0, 1) if n == 3 else (-1, 1)
    return ''.join(st(c, (x, 1, z), (0, 1, 0)) for z in rng for x in rng)


def strips(c, n=3, y=1):
    rng = (-1, 0, 1) if n == 3 else (-1, 1)
    b = ''.join(st(c, (x, y, -1), (0, 0, -1)) for x in rng)
    f = ''.join(st(c, (x, y, 1), (0, 0, 1)) for x in rng)
    l = ''.join(st(c, (-1, y, z), (-1, 0, 0)) for z in rng)
    r = ''.join(st(c, (1, y, z), (1, 0, 0)) for z in rng)
    return b, f, l, r


def _clone(c):
    d = fresh()
    d.cubies = [[p, dict(s)] for p, s in c.cubies]
    return d


def _auf_fix(c):
    """Turn U so that the most top-layer pieces are solved (nicest PLL picture)."""
    best = None
    ref = fresh()
    for k in range(4):
        d = _clone(c)
        if k:
            d.apply(' '.join(['U'] * k))
        n = sum(1 for cu in d.cubies if cu[0][1] == 1 and
                all(ref.sticker(cu[0], dd) == col for dd, col in cu[1].items()))
        if best is None or n > best[0]:
            best = (n, d)
    return best[1]


def _pll_arrows(c):
    ref = fresh()
    arrows = []
    for cu in c.cubies:
        if cu[0][1] != 1 or cu[0] == (0, 1, 0):
            continue
        cols = set(cu[1].values())
        home = [r[0] for r in ref.cubies if set(r[1].values()) == cols][0]
        if home != cu[0]:
            arrows.append({'f': ['u', cu[0][0] + 1, cu[0][2] + 1], 't': ['u', home[0] + 1, home[2] + 1], 'curve': 14})
    out, seen = [], set()
    for a in arrows:
        k = (tuple(a['f']), tuple(a['t']))
        rk = (tuple(a['t']), tuple(a['f']))
        if rk in seen:
            for o in out:
                if (tuple(o['f']), tuple(o['t'])) == rk:
                    o['dbl'] = 1
                    o['curve'] = 0
            continue
        seen.add(k)
        out.append(a)
    return out


# ------------------------------------------------------------------ 3x3 OLL --
OLL_GROUPS = [('Dot', 'Punkts – neviena dzeltena mala'), ('Square', 'Kvadrāts'), ('Lightning', 'Zibens'),
              ('Fish', 'Zivs'), ('Knight', 'Bruņinieks'), ('OCLL', 'Krusts gatavs – tikai stūri (OCLL)'),
              ('Stūri gatavi', 'Stūri gatavi – tikai malas'), ('Awkward', 'Neērtie'), ('P', 'P forma'),
              ('T', 'T forma'), ('C', 'C forma'), ('W', 'W forma'), ('L', 'L forma'), ('Line', 'Līnija')]
OCLL_NAMES = {21: 'H', 22: 'Pi', 23: 'U (lukturi)', 24: 'T', 25: 'L', 26: 'Antisune', 27: 'Sune'}

_OLL = [(1, 'Dot', "R U2 R2 F R F' U2 R' F R F'"), (2, 'Dot', "F R U R' U' F' f R U R' U' f'"),
        (3, 'Dot', "f R U R' U' f' U' F R U R' U' F'"), (4, 'Dot', "f R U R' U' f' U F R U R' U' F'"),
        (17, 'Dot', "R U R' U R' F R F' U2 R' F R F'"), (18, 'Dot', "R U2 R2 F R F' U2 M' U R U' r'"),
        (19, 'Dot', "S' R U R' S U' R' F R F'"), (20, 'Dot', "r U R' U' M2 U R U' R' U' M'"),
        (5, 'Square', "l' U2 L U L' U l"), (6, 'Square', "r U2 R' U' R U' r'"),
        (7, 'Lightning', "r U R' U R U2 r'"), (8, 'Lightning', "l' U' L U' L' U2 l"),
        (11, 'Lightning', "r' R2 U R' U R U2 R' U M'"), (12, 'Lightning', "M' R' U' R U' R' U2 R U' M"),
        (39, 'Lightning', "L F' L' U' L U F U' L'"), (40, 'Lightning', "R' F R U R' U' F' U R"),
        (9, 'Fish', "R U R' U' R' F R2 U R' U' F'"), (10, 'Fish', "R U R' U R' F R F' R U2 R'"),
        (35, 'Fish', "R U2 R2 F R F' R U2 R'"), (37, 'Fish', "F R' F' R U R U' R'"),
        (13, 'Knight', "F U R U2 R' U' R U R' F'"), (14, 'Knight', "R' F R U R' F' R F U' F'"),
        (15, 'Knight', "l' U' l L' U' L U l' U l"), (16, 'Knight', "r U r' R U R' U' r U' r'"),
        (21, 'OCLL', "R U R' U R U' R' U R U2 R'"), (22, 'OCLL', "R U2 R2 U' R2 U' R2 U2 R"),
        (23, 'OCLL', "R2 D' R U2 R' D R U2 R"), (24, 'OCLL', "r U R' U' r' F R F'"),
        (25, 'OCLL', "F R' F' r U R U' r'"), (26, 'OCLL', "R U2 R' U' R U' R'"), (27, 'OCLL', "R U R' U R U2 R'"),
        (28, 'Stūri gatavi', "r U R' U' M U R U' R'"), (57, 'Stūri gatavi', "R U R' U' M' U R U' r'"),
        (29, 'Awkward', "R U R' U' R U' R' F' U' F R U R'"), (30, 'Awkward', "F U R U2 R' U' R U2 R' U' F'"),
        (41, 'Awkward', "R U R' U R U2 R' F R U R' U' F'"), (42, 'Awkward', "R' U' R U' R' U2 R F R U R' U' F'"),
        (31, 'P', "R' U' F U R U' R' F' R"), (32, 'P', "S R U R' U' R' F R f'"),
        (43, 'P', "R' U' F' U F R"), (44, 'P', "f R U R' U' f'"),
        (33, 'T', "R U R' U' R' F R F'"), (45, 'T', "F R U R' U' F'"),
        (34, 'C', "R U R2 U' R' F R U R U' F'"), (46, 'C', "R' U' R' F R F' U R"),
        (36, 'W', "L' U' L U' L' U L U L F' L' F"), (38, 'W', "R U R' U R U' R' U' R' F R F'"),
        (47, 'L', "F R' F' R U2 R U' R' U R U2 R'"), (48, 'L', "F R U R' U' R U R' U' F'"),
        (49, 'L', "r U' r2 U r2 U r2 U' r"), (50, 'L', "R' F R2 B' R2 F' R2 B R'"),
        (53, 'L', "l' U' L U' L' U L U' L' U2 l"), (54, 'L', "r U R' U R U' R' U R U2 r'"),
        (51, 'Line', "F U R U' R' U R U' R' F'"), (52, 'Line', "R U R' U R U' B U' B' R'"),
        (55, 'Line', "R' F R U R U' R2 F' R2 U' R' U R U R'"), (56, 'Line', "r U r' U R U' R' U R U' R' r U' r'")]

OLL = []
for _n, _g, _a in _OLL:
    _c = state_for(_a)
    _uf = u_face(_c)
    _b, _f, _l, _r = strips(_c)
    OLL.append({'id': 'oll-%d' % _n, 'n': _n, 'g': _g, 'alg': normalize(_a), 'c': mask(_uf),
                'b': mask(_b), 'f': mask(_f), 'l': mask(_l), 'r': mask(_r), 'ycount': _uf.count('y')})

# 2-look OLL edge cases: picture shows only the edges (corners grey).
_EDGES = [('oll-e-line', 'Līnija', "F R U R' U' F'", 'Ar U novieto līniju horizontāli (no kreisās uz labo). Izpildi vienreiz.'),
          ('oll-e-l', 'L forma', "F U R U' R' F'", 'Ar U novieto abas dzeltenās malas aizmugurē un pa kreisi. Izpildi vienreiz.'),
          ('oll-e-dot', 'Punkts', "F R U R' U' F' U2 F U R U' R' F'", 'Neviena dzeltena mala. Divi algoritmi pēc kārtas: pēc pirmā rodas L vai līnija, tad izvēlies to.')]
OLL_EDGES = []
for _id, _name, _a, _hint in _EDGES:
    _m = mask(u_face(state_for(_a)))
    OLL_EDGES.append({'id': _id, 'name': _name, 'alg': _a, 'hint': _hint,
                      'c': ''.join(_m[i] if i in (1, 3, 4, 5, 7) else 'x' for i in range(9))})

# ------------------------------------------------------------------ 3x3 PLL --
PLL_GROUPS = [('Tikai stūri', ['Aa', 'Ab', 'E']), ('Tikai malas', ['Ua', 'Ub', 'H', 'Z']),
              ('Blakus stūru maiņa', ['T', 'Ja', 'Jb', 'Ra', 'Rb', 'F']),
              ('Diagonālā stūru maiņa', ['V', 'Y', 'Na', 'Nb']), ('G permutācijas', ['Ga', 'Gb', 'Gc', 'Gd'])]
PLL_2LOOK = ('T', 'Y', 'Ua', 'H')
_PLL = [('Aa', 'Stūru 3-cikls', "x R' U R' D2 R U' R' D2 R2 x'"), ('Ab', 'Stūru 3-cikls (pretēji)', "x R2 D2 R U R' D2 R U' R x'"),
        ('E', 'Abas diagonāles', "x' R U' R' D R U R' D' R U R' D R U' R' D' x"),
        ('Ua', 'Malu 3-cikls', "M2 U M U2 M' U M2"), ('Ub', 'Malu 3-cikls (pretēji)', "M2 U' M U2 M' U' M2"),
        ('H', 'Abas pretējās malas', "M2 U' M2 U2 M2 U' M2"), ('Z', 'Divi blakus malu pāri', "M' U' M2 U' M2 U' M' U2 M2"),
        ('T', 'Blakus stūri + malas', "R U R' U' R' F R2 U' R' U' R U R' F'"), ('Ja', 'Blakus stūri + malas', "x R2 F R F' R U2 r' U r U2 x'"),
        ('Jb', 'Blakus stūri + malas (spog.)', "R U R' F' R U R' U' R' F R2 U' R'"),
        ('Ra', 'R-tips', "R U' R' U' R U R D R' U' R D' R' U2 R'"), ('Rb', 'R-tips (spog.)', "R' U2 R U2 R' F R U R' U' R' F' R2"),
        ('F', 'Blakus stūri + pretējās malas', "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R"),
        ('V', 'Diagonāle + malas', "R' U R' U' R D' R' D R' U D' R2 U' R2 D R2"), ('Y', 'Diagonāle + malas', "F R U' R' U' R U R' F' R U R' U' R' F R F'"),
        ('Na', 'N-perm', "R U R' U R U R' F' R U R' U' R' F R2 U' R' U2 R U' R'"), ('Nb', 'N-perm (spog.)', "R' U R U' R' F' U' F R U R' F R' F' R U' R"),
        ('Ga', 'Stūru + malu 3-cikls', "R2 U R' U R' U' R U' R2 D U' R' U R D'"), ('Gb', 'Stūru + malu 3-cikls', "D R' U' R U D' R2 U R' U R U' R U' R2"),
        ('Gc', 'Stūru + malu 3-cikls', "R2 U' R U' R U R' U R2 D' U R U' R' D"), ('Gd', 'Stūru + malu 3-cikls', "R U R' U' D R2 U' R U' R' U R' U R2 D'")]
PLL = []
for _n, _d, _a in _PLL:
    _c = _auf_fix(state_for(_a))
    _b, _f, _l, _r = strips(_c)
    PLL.append({'id': 'pll-%s' % _n, 'n': _n, 'd': _d, 'alg': normalize(_a), 'b': _b, 'f': _f, 'l': _l, 'r': _r,
                'arrows': _pll_arrows(_c)})

# ------------------------------------------------------------------ 3x3 F2L --
F2L_INTRO = {
    'Pamata ievietošana': 'Pāris jau savienots vai vienā gājienā savienojams. Šos četrus vajag zināt kā reizrēķinu.',
    'Malas pārvietošana': 'Stūris un mala augšā, bet mala nepareizā pusē. Vispirms pārvieto malu, tad ievieto.',
    'Mala jāpārvieto, stūris jāapgriež': 'Stūra baltais skatās uz augšu vai nepareizā virzienā. Algoritms pagriež stūri un savieno pāri.',
    'Pāri atdala, ejot pāri': 'Stūris un mala stāv kopā, bet nepareizi savienoti. Tos vispirms atdala.',
    'Pāris savienots sānā': 'Pāris savienots, bet stūra baltais skatās uz sānu. Pāri paceļ un ielaiž no otras puses.',
    'Īpašie gadījumi': 'Baltais skatās uz augšu un mala ir tieši zem vai blakus. Divi neparasti, bet biežāk sastopami gadījumi.',
    'Stūris slotā, mala augšā': 'Stūris jau sēž slotā (pareizi vai apgriezts), mala vēl augšā. Algoritms izceļ un ieliek kopā.',
    'Mala slotā, stūris augšā': 'Mala jau slotā, stūris augšā. Tas pats princips no otras puses.',
    'Abi slotā, bet nepareizi': "Abi gabaliņi slotā, bet apgriezti vai samainīti. Retākie gadījumi; sākumā vari vienkārši izcelt ar R U R' un sākt no jauna.",
}
_F2L_RAW = """1|Pamata ievietošana|U (R U' R')
2|Pamata ievietošana|y' U' (R' U R)
3|Pamata ievietošana|F' U' F
4|Pamata ievietošana|(R U R')
5|Malas pārvietošana|(U' R U R') U2 (R U' R')
6|Malas pārvietošana|d (R' U' R) U2' (R' U R)
7|Malas pārvietošana|U' (R U2' R') U2 (R U' R')
8|Malas pārvietošana|d (R' U2 R) U2' (R' U R)
9|Mala jāpārvieto, stūris jāapgriež|U' R U' R' d R' U' R
10|Mala jāpārvieto, stūris jāapgriež|U' (R U R' U)(R U R')
11|Mala jāpārvieto, stūris jāapgriež|U' (R U2' R') d (R' U' R)
12|Mala jāpārvieto, stūris jāapgriež|R U' R' U R U' R' U2 R U' R'
13|Mala jāpārvieto, stūris jāapgriež|d (R' U R U') (R' U' R)
14|Mala jāpārvieto, stūris jāapgriež|U' (R U' R' U) (R U R')
15|Pāri atdala, ejot pāri|R' D' R U' R' D R U (R U' R')
16|Pāri atdala, ejot pāri|(R U' R' U) d (R' U' R)
17|Pāri atdala, ejot pāri|(R U2 R') U' (R U R')
18|Pāri atdala, ejot pāri|y' (R' U2 R) U (R' U' R)
19|Pāris savienots sānā|U (R U2 R') U (R U' R')
20|Pāris savienots sānā|y' U' (R' U2 R) U' (R' U R)
21|Pāris savienots sānā|(R U' R') U2 (R U R')
22|Pāris savienots sānā|y' (R' U R) U2 (R' U' R)
23|Īpašie gadījumi|U2 R2 U2 (R' U' R U') R2
24|Īpašie gadījumi|(R U R') d (R' U R U') (R' U R)
25|Stūris slotā, mala augšā|U' (R' F R F') (R U R')
26|Stūris slotā, mala augšā|y' R U R U R U' R' U' R'
27|Stūris slotā, mala augšā|(R U' R' U)(R U' R')
28|Stūris slotā, mala augšā|(R U R' U') F R' F' R
29|Stūris slotā, mala augšā|y' (R' U' R U)(R' U' R)
30|Stūris slotā, mala augšā|(R U R' U')(R U R')
31|Mala slotā, stūris augšā|(R U' R') d (R' U R)
32|Mala slotā, stūris augšā|(R U R' U')2 (R U R')
33|Mala slotā, stūris augšā|U' (R U' R') U2' (R U' R')
34|Mala slotā, stūris augšā|U (F' U F) U2 (F' U F)
35|Mala slotā, stūris augšā|U' R U R' U (F' U' F)
36|Mala slotā, stūris augšā|U F' U' F U' (R U R')
38|Abi slotā, bet nepareizi|(R' F R F') (R U' R' U) (R U' R' U2) (R U' R')
39|Abi slotā, bet nepareizi|(R U' R') U' (R U R') U2 (R U' R')
40|Abi slotā, bet nepareizi|(R U' R' U)(R U2' R') U (R U' R')
41|Abi slotā, bet nepareizi|(r U' r') U2 (r U r') (R U R')"""


def _f2l_picture(c):
    fc, rc, dc = (c.sticker(DIRS[f], DIRS[f]) for f in 'FRD')
    pair = [cu for cu in c.cubies if set(cu[1].values()) in ({fc, rc, dc}, {fc, rc})]
    assert len(pair) == 2
    pair_pos = set(tuple(cu[0]) for cu in pair)
    rng = (-1, 0, 1)
    faces = {'U': [((x, 1, z), (0, 1, 0)) for z in rng for x in rng],
             'F': [((x, y, 1), (0, 0, 1)) for y in reversed(rng) for x in rng],
             'R': [((1, y, z), (1, 0, 0)) for y in reversed(rng) for z in reversed(rng)]}
    out = {}
    for face, cells in faces.items():
        out[face] = ''.join(st(c, pos, d) if (pos in pair_pos or pos in ((0, 1, 0), (0, 0, 1), (1, 0, 0))) else 'x'
                            for pos, d in cells)
    return out


F2L = []
F2L_GROUP_ORDER = []
for _line in _F2L_RAW.split('\n'):
    _n, _g, _a = _line.split('|')
    if _g not in F2L_GROUP_ORDER:
        F2L_GROUP_ORDER.append(_g)
    _pic = _f2l_picture(state_for(_a))
    F2L.append({'id': 'f2l-%s' % _n, 'n': int(_n), 'g': _g, 'alg': normalize(_a), 'u': _pic['U'], 'f': _pic['F'], 'r': _pic['R']})

# ------------------------------------------------------------- 2x2 Ortega --
_OLL2 = [('Sune', "R U R' U R U2 R'"), ('Antisune', "R U2 R' U' R U' R'"), ('Pi', "F R U R' U' R U R' U' F'"),
         ('H', "R2 U2 R U2 R2"), ('U', "F R U R' U' F'"), ('T', "R U R' U' R' F R F'"), ('L', "F R U' R' U' R U R' F'")]
OLL2 = []
for _n, _a in _OLL2:
    _c = state_for(_a)
    _b, _f, _l, _r = strips(_c, 2)
    OLL2.append({'id': 'o2-%s' % _n.lower(), 'n': _n, 'alg': _a, 'c': mask(u_face(_c, 2)),
                 'b': mask(_b), 'f': mask(_f), 'l': mask(_l), 'r': mask(_r)})

PBL_TEXT = {
    'adj-top': ('Blakus maiņa augšā, apakša gatava', 'Sakārtotais slānis apakšā. Augšā lukturi pa kreisi.'),
    'diag-top': ('Diagonāle augšā, apakša gatava', 'Sakārtotais slānis apakšā. Augšā neviens sāns nav vienā krāsā; leņķis vienalga.'),
    'adj-adj': ('Blakus + blakus', 'Abu slāņu vienādās krāsas pāri aizmugurē.'),
    'diag-diag': ('Diagonāle + diagonāle', 'Jebkurš leņķis. Trīs griezieni.'),
    'adj-diag': ('Blakus augšā + diagonāle apakšā', 'Slānis ar pāri augšā, tā pāris priekšā.'),
}
_PBL = [('adj-top', "R U R' U' R' F R2 U' R' U' R U R' F'"), ('diag-top', "F R U' R' U' R U R' F' R U R' U' R' F R F'"),
        ('adj-adj', "R2 U' R2 U2 F2 U' R2"), ('diag-diag', "R2 F2 R2"), ('adj-diag', "R U' R F2 R' U R'")]
PBL = []
for _k, _a in _PBL:
    _c = state_for(_a)
    _b, _f, _l, _r = strips(_c, 2)
    _d = _clone(_c)
    _d.apply('z2')  # turn the cube upside down keeping the same front
    _raw = lambda pos, dd: LET[_d.sticker(pos, dd)]
    _rng = (-1, 1)
    _bottom = {'c': ''.join(_raw((x, 1, z), (0, 1, 0)) for z in _rng for x in _rng),
               'b': ''.join(_raw((x, 1, -1), (0, 0, -1)) for x in _rng), 'f': ''.join(_raw((x, 1, 1), (0, 0, 1)) for x in _rng),
               'l': ''.join(_raw((-1, 1, z), (-1, 0, 0)) for z in _rng), 'r': ''.join(_raw((1, 1, z), (1, 0, 0)) for z in _rng)}
    PBL.append({'id': 'pbl-%s' % _k, 'n': _k, 'd': PBL_TEXT[_k][0], 'hold': PBL_TEXT[_k][1], 'alg': _a,
                'b': _b, 'f': _f, 'l': _l, 'r': _r, 'bottom': _bottom})

# ---------------------------------------------------------------- 2x2 CLL --
CLL_GROUPS = [('Sune', 'Sune – 1 dzeltena augšā'), ('Antisune', 'Antisune – 1 dzeltena augšā'), ('U', 'U – 2 dzeltenas blakus'),
              ('T', 'T – 2 dzeltenas blakus'), ('L', 'L – 2 dzeltenas pa diagonāli'), ('Pi', 'Pi – 0 dzeltenu augšā'),
              ('H', 'H – 0 dzeltenu augšā'), ('O', 'Augša jau dzeltena')]
_CLL_RAW = """AS|1|y R U2 R' U' R U' R'
AS|2|R U2 R' F R' F' R U' R U' R'
AS|3|y2 F' L F L' U2 L' U2 L
AS|4|y2 R' F R F' R U R'
AS|5|y2 R U2 R' U2 R' F R F'
AS|6|y' R U2 R' U' R U' R' F R' F' R U R U' R' U'
H|1|F R2 U' R2 U' R2 U R2 F'
H|2|R U R' U R U R' F R' F' R
H|3|y F R U R' U' R U R' U' R U R' U' F'
H|4|y R2 U2 R' U2 R2
L|1|y R U2 R' F' R U2 R' U R' F2 R
L|2|y2 R U2 R2 F2 R U R' F2 R F'
L|3|y2 R' U R' U2 R U' R' U R U' R2
L|4|y R U2 R2 F R F' R U2 R'
L|5|y F R' F' R U R U' R'
L|6|y2 F' R U R' U' R' F R
Pi|1|y F R' F' R U2 R U' R' U R U2 R'
Pi|2|R U2 R' U' R U R' U2 R' F R F'
Pi|3|y F R2 U' R2 U R2 U R2 F'
Pi|4|y2 R' F R F' R U' R' U' R U' R'
Pi|5|y' R' U' R' F R F' R U' R' U2 R
Pi|6|F R U R' U' R U R' U' F'
Sune|1|L' U2 L U2 L F' L' F
Sune|2|R U R' U' R' F R F' R U R' U R U2 R'
Sune|3|R U' R' F R' F' R
Sune|4|F R' F' R U2 R U2 R'
Sune|5|y2 R U R' U R' F R F' R U2 R'
Sune|6|R U R' U R U2 R'
T|1|y' R U R' U' R' F R F'
T|2|y L' U' L U L F' L' F
T|3|F U' R U2 R' U' F2 R U R'
T|4|R' U R U2 R2 F' R U' R' F2 R2
T|5|y2 F R U R' U' R U' R' U' R U R' F'
T|6|R' U R U2 R2 F R F' R
U|1|y' F R U R' U' F'
U|2|R' U' R2 U R' U2 R U2 R' U R'
U|3|y2 F R U R' U2 F' R U' R' F
U|4|y' F R' F' R U' R U' R' U2 R U' R'
U|5|R U' R2 F R F' R U R' U' R U R'
U|6|R' U R' F R F' R U2 R' U R"""
_CLL_GROUP_NAME = {'AS': 'Antisune', 'H': 'H', 'L': 'L', 'Pi': 'Pi', 'Sune': 'Sune', 'T': 'T', 'U': 'U'}


def top_pattern_2x2(c):
    """Yellow positions of the whole top layer (U face + four strips), rotation sensitive."""
    m = ''.join('y' if c.sticker((x, 1, z), (0, 1, 0)) == 'U' else 'x' for z in (-1, 1) for x in (-1, 1))
    b, f, l, r = strips(c, 2)
    return m + '|' + mask(b + f + l + r)


def cll_shape_masks():
    """All four U-rotations of each Ortega OLL shape, keyed by group name."""
    out = {}
    for d in OLL2:
        ms = set()
        for k in range(4):
            c = state_for(d['alg'])
            if k:
                c.apply(' '.join(['U'] * k))
            ms.add(top_pattern_2x2(c))
        out[d['n']] = ms
    return out


CLL = []
for _line in _CLL_RAW.split('\n'):
    _g, _n, _a = _line.split('|')
    _c = state_for(_a)
    _b, _f, _l, _r = strips(_c, 2)
    CLL.append({'id': 'cll-%s-%s' % (_CLL_GROUP_NAME[_g].lower(), _n), 'g': _CLL_GROUP_NAME[_g], 'n': int(_n),
                'alg': _a, 'c': u_face(_c, 2), 'b': _b, 'f': _f, 'l': _l, 'r': _r})
# The two solved-orientation cases complete the 42; they are the PBL T and Y perms
# and share their learned state with the PBL cards (same id).
for _n, _k, _a in ((1, 'adj-top', "R U R' U' R' F R2 U' R' U' R U R' F'"), (2, 'diag-top', "F R U' R' U' R U R' F' R U R' U' R' F R F'")):
    _c = state_for(_a)
    _b, _f, _l, _r = strips(_c, 2)
    CLL.append({'id': 'pbl-%s' % _k, 'g': 'O', 'n': _n, 'alg': _a, 'c': u_face(_c, 2), 'b': _b, 'f': _f, 'l': _l, 'r': _r})

# ---------------------------------------------------------------- Pyraminx --
# Text-only cards: the Pyraminx picture convention for upper edges is not settled,
# so these have no derived diagram (see the Pro plan). Verified in test_pyraminx_sim.py.
PYRA = [{'id': 'l4e-cw', 'sets': 'l4e', 'name': 'Trīs malas pa apli: PK → PL', 'alg': "R U R' U R U R'",
         'hint': 'Priekšā kreisā mala pieder priekšā pa labi. Tas pats iesācēju cikls.'},
        {'id': 'l4e-ccw', 'sets': 'l4e', 'name': 'Trīs malas pa apli: PK → AM', 'alg': "R U' R' U' R U' R'",
         'hint': 'Priekšā kreisā mala pieder aizmugurē.'},
        {'id': 'flip', 'sets': 'l4e ell', 'name': 'Divas malas apgrieztas savās vietās', 'alg': "L R' L' R U' R U R'",
         'hint': 'Pareizā mala aizmugurē, abas apgrieztās priekšā.'},
        {'id': 'sledge', 'sets': 'l4e ell', 'name': 'Sledgehammer – ievietot no labās puses', 'alg': "R' L R L'",
         'hint': 'Trūkstošā apakšējā mala ir augšā priekšā pa labi, zaļais skatās uz sānu.'},
        {'id': 'hedge', 'sets': 'l4e ell', 'name': 'Hedgeslammer – ievietot no kreisās puses', 'alg': "L R' L' R",
         'hint': 'Spoguļgadījums: mala augšā priekšā pa kreisi.'},
        {'id': 'uperm', 'sets': 'ell', 'name': 'Trīs augšas malas pa apli (U perm)', 'alg': "R' L R L U L U'",
         'hint': 'Oka nobeigums: trīs augšējās malas jāpārbīda pa apli.'},
        {'id': 'uperm-m', 'sets': 'ell', 'name': 'Trīs augšas malas pretējā virzienā', 'alg': "L R' L' R' U' R' U",
         'hint': 'Spoguļa U perm.'}]
PYRA_BY_ID = {d['id']: d for d in PYRA}


if __name__ == '__main__':
    print('OLL', len(OLL), 'PLL', len(PLL), 'F2L', len(F2L), 'CLL', len(CLL), 'OLL2', len(OLL2), 'PBL', len(PBL), 'PYRA', len(PYRA))
    s = [d for d in OLL if d['n'] == 27][0]
    print('Sune', s['c'], s['b'], s['f'], s['l'], s['r'])
    t = [d for d in PLL if d['n'] == 'T'][0]
    print('T perm', t['b'], t['f'], t['l'], t['r'], t['arrows'])
