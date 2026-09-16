# Verify and derive diagrams for CLL (42), F2L (41) and PBL bottom views.
# Frame convention: sticker positions are read in the fixed simulator frame, which is
# the learner's frame right before executing the algorithm (whole-cube rotations inside
# the algorithm are therefore reflected in the case picture, as on speedcubedb).
import sys, json, io, os, re
ROOT = r'C:\Users\Egils.Varna\Projects\EV\13-cube-solving'
sys.path.insert(0, os.path.join(ROOT, '_build'))
from verify_algs import fresh, invert
HERE = os.path.dirname(os.path.abspath(__file__))

LET = {'U': 'y', 'D': 'w', 'F': 'g', 'B': 'b', 'L': 'o', 'R': 'r'}
DIRS = {'U': (0, 1, 0), 'D': (0, -1, 0), 'F': (0, 0, 1), 'B': (0, 0, -1), 'L': (-1, 0, 0), 'R': (1, 0, 0)}


def normalize(alg):
    """Expand (...)2 groups, drop parentheses, U2' -> U2."""
    alg = alg.replace('’', "'")
    def rep(m):
        return ' ' + ' '.join([m.group(1)] * 2) + ' '
    alg = re.sub(r'\(([^()]*)\)2', rep, alg)
    alg = alg.replace('(', ' ').replace(')', ' ')
    alg = re.sub(r"2'", '2', alg)
    return ' '.join(alg.split())


def center(c, face):
    d = DIRS[face]
    return c.sticker(d, d)


def st(c, pos, d):
    col = c.sticker(pos, d)
    if col is None:
        return 'x'
    # relabel by current centre colours: whatever colour sits at the front centre is drawn green, etc.
    frame = {c.sticker(DIRS[f], DIRS[f]): f for f in 'UDFBLR'}
    return LET[frame[col]]


def face_grid(c, face, n=3):
    """9 stickers of a face as seen from outside: rows top->bottom, cols left->right."""
    rng = (-1, 0, 1) if n == 3 else (-1, 1)
    out = ''
    if face == 'U':
        for z in rng:
            for x in rng:
                out += st(c, (x, 1, z), (0, 1, 0))
    elif face == 'F':
        for y in reversed(rng):
            for x in rng:
                out += st(c, (x, y, 1), (0, 0, 1))
    elif face == 'R':
        for y in reversed(rng):
            for z in reversed(rng):
                out += st(c, (1, y, z), (1, 0, 0))
    return out


def strips(c, n=3, y=1):
    rng = (-1, 0, 1) if n == 3 else (-1, 1)
    b = ''.join(st(c, (x, y, -1), (0, 0, -1)) for x in rng)
    f = ''.join(st(c, (x, y, 1), (0, 0, 1)) for x in rng)
    l = ''.join(st(c, (-1, y, z), (-1, 0, 0)) for z in rng)
    r = ''.join(st(c, (1, y, z), (1, 0, 0)) for z in rng)
    return b, f, l, r


def cubie_ok(c, cu):
    """Every sticker of this cubie matches the center of the face it sits on."""
    for d, col in cu[1].items():
        if c.sticker(d, d) != col:
            return False
    return True


def state_for(alg):
    c = fresh()
    c.apply(invert(normalize(alg)))
    return c


# ---------------------------------------------------------------- CLL -------
CLL_RAW = """AS|1|y R U2 R' U' R U' R'
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
GROUP_NAME = {'AS': 'Antisune', 'H': 'H', 'L': 'L', 'Pi': 'Pi', 'Sune': 'Sune', 'T': 'T', 'U': 'U'}
OLL2_ALG = {'Sune': "R U R' U R U2 R'", 'Antisune': "R U2 R' U' R U' R'", 'Pi': "F R U R' U' R U R' U' F'", 'H': "R2 U2 R U2 R2", 'U': "F R U R' U' F'", 'T': "R U R' U' R' F R F'", 'L': "F R U' R' U' R U R' F'"}


def pattern(c):
    """Yellow positions of the whole top layer: U face + 4 side strips (rotation-sensitive)."""
    m = ''.join('y' if c.sticker((x, 1, z), (0, 1, 0)) == 'U' else 'x' for z in (-1, 1) for x in (-1, 1))
    b, f, l, r = strips(c, 2)
    return m + '|' + ''.join('y' if ch == 'y' else 'x' for ch in b + f + l + r)


shape_masks = {}
for name, a in OLL2_ALG.items():
    ms = set()
    for k in range(4):
        c = fresh(); c.apply(invert(a))
        if k:
            c.apply(' '.join(['U'] * k))
        ms.add(pattern(c))
    shape_masks[name] = ms


def mask2(c):
    return pattern(c)


problems = []
cll = []
for line in CLL_RAW.split('\n'):
    g, n, a = line.split('|')
    c = state_for(a)
    bottom_ok = all(cubie_ok(c, cu) for cu in c.cubies if cu[0][1] == -1 and cu[0][0] and cu[0][2])
    if not bottom_ok:
        problems.append(('CLL', g, n, 'bottom layer broken'))
    m = mask2(c)
    shape = [s for s, ms in shape_masks.items() if m in ms]
    if not shape or shape[0] != GROUP_NAME[g]:
        problems.append(('CLL', g, n, 'shape mismatch: %s vs %s' % (shape, GROUP_NAME[g])))
    b, f, l, r = strips(c, 2)
    cll.append({'g': GROUP_NAME[g], 'n': int(n), 'alg': a, 'c': face_grid(c, 'U', 2), 'b': b, 'f': f, 'l': l, 'r': r})
assert len(cll) == 40
# The two solved-orientation cases complete the 42: adjacent swap (T perm) and diagonal swap (Y perm).
for n, a in ((1, "R U R' U' R' F R2 U' R' U' R U R' F'"), (2, "F R U' R' U' R U R' F' R U R' U' R' F R F'")):
    c = state_for(a)
    b, f, l, r = strips(c, 2)
    cll.append({'g': 'O', 'n': n, 'alg': a, 'c': face_grid(c, 'U', 2), 'b': b, 'f': f, 'l': l, 'r': r})
assert len(cll) == 42

# ---------------------------------------------------------------- F2L -------
F2L_RAW = """1|Pamata ievietošana|U (R U' R')
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

f2l = []
for line in F2L_RAW.split('\n'):
    n, g, a = line.split('|')
    na = normalize(a)
    c = state_for(a)
    # everything except U layer and the FR slot must be solved (frame independent)
    others_ok = all(cubie_ok(c, cu) for cu in c.cubies if cu[0][1] <= 0 and not (cu[0][0] == 1 and cu[0][2] == 1))
    if not others_ok:
        problems.append(('F2L', n, 'other slots/cross broken'))
    fc, rc, dc = center(c, 'F'), center(c, 'R'), center(c, 'D')
    pair = [cu for cu in c.cubies if set(cu[1].values()) in ({fc, rc, dc}, {fc, rc})]
    assert len(pair) == 2
    pair_pos = set(tuple(cu[0]) for cu in pair)
    # picture: U, F, R faces; only the pair stickers keep colors
    def grid_masked(face):
        g = ''
        rng = (-1, 0, 1)
        cells = []
        if face == 'U':
            cells = [((x, 1, z), (0, 1, 0)) for z in rng for x in rng]
        elif face == 'F':
            cells = [((x, y, 1), (0, 0, 1)) for y in reversed(rng) for x in rng]
        else:
            cells = [((1, y, z), (1, 0, 0)) for y in reversed(rng) for z in reversed(rng)]
        for pos, d in cells:
            if pos in pair_pos or pos in ((0, 1, 0), (0, 0, 1), (1, 0, 0)):
                g += st(c, pos, d)
            else:
                g += 'x'
        return g
    f2l.append({'n': int(n), 'g': g, 'alg': na, 'u': grid_masked('U'), 'f': grid_masked('F'), 'r': grid_masked('R')})
assert len(f2l) == 40

# --------------------------------------------------------- PBL bottom view ----
PBL = [('adj-top', "R U R' U' R' F R2 U' R' U' R U R' F'"), ('diag-top', "F R U' R' U' R U R' F' R U R' U' R' F R F'"), ('adj-adj', "R2 U' R2 U2 F2 U' R2"), ('diag-diag', "R2 F2 R2"), ('adj-diag', "R U' R F2 R' U R'")]
pbl_bottom = {}
for key, a in PBL:
    c = state_for(a)
    c.apply('z2')  # turn the cube upside down keeping the same front
    raw = lambda pos, d: LET[c.sticker(pos, d)]
    rng = (-1, 1)
    pbl_bottom[key] = {'c': ''.join(raw((x, 1, z), (0, 1, 0)) for z in rng for x in rng),
                       'b': ''.join(raw((x, 1, -1), (0, 0, -1)) for x in rng), 'f': ''.join(raw((x, 1, 1), (0, 0, 1)) for x in rng),
                       'l': ''.join(raw((-1, 1, z), (-1, 0, 0)) for z in rng), 'r': ''.join(raw((1, 1, z), (1, 0, 0)) for z in rng)}

json.dump({'cll': cll, 'f2l': f2l, 'pbl_bottom': pbl_bottom, 'problems': problems}, io.open(os.path.join(HERE, 'more.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('problems:', problems)
print('CLL groups:', {g: sum(1 for x in cll if x['g'] == g) for g in list(GROUP_NAME.values()) + ['O']})
print('F2L sample', f2l[0], f2l[1])
print('PBL bottom', pbl_bottom)
