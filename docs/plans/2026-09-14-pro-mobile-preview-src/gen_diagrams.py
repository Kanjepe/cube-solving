# Derive OLL/PLL/2x2 case diagrams from the simulator: state = inverse(alg) on a solved cube.
import sys, json, io, os
ROOT = r'C:\Users\Egils.Varna\Projects\EV\13-cube-solving'
sys.path.insert(0, os.path.join(ROOT, '_build'))
from verify_algs import fresh, invert, bottom_corners_ok

LET = {'U': 'y', 'D': 'w', 'F': 'g', 'B': 'b', 'L': 'o', 'R': 'r'}


def st(c, pos, d):
    return LET[c.sticker(pos, d)]


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


def f2l_ok(c):
    ref = fresh()
    for cu in c.cubies:
        if cu[0][1] <= 0:
            for d, col in cu[1].items():
                if ref.sticker(cu[0], d) != col:
                    return False
    return True


def mask(s):
    return ''.join('y' if ch == 'y' else 'x' for ch in s)


def state_for(alg):
    c = fresh()
    c.apply(invert(alg))
    return c


def clone(c):
    d = fresh()
    d.cubies = [[p, dict(s)] for p, s in c.cubies]
    return d


def auf_fix(c):
    best = None
    for k in range(4):
        d = clone(c)
        if k:
            d.apply(' '.join(['U'] * k))
        ref = fresh()
        n = 0
        for cu in d.cubies:
            if cu[0][1] == 1 and all(ref.sticker(cu[0], dd) == col for dd, col in cu[1].items()):
                n += 1
        if best is None or n > best[0]:
            best = (n, k, d)
    return best[2], best[1]


def grid(pos):
    return [pos[0] + 1, pos[2] + 1]


def pll_arrows(c):
    ref = fresh()
    arrows = []
    for cu in c.cubies:
        if cu[0][1] != 1 or cu[0] == (0, 1, 0):
            continue
        cols = set(cu[1].values())
        home = [r[0] for r in ref.cubies if set(r[1].values()) == cols][0]
        if home != cu[0]:
            arrows.append({'f': ['u'] + grid(cu[0]), 't': ['u'] + grid(home), 'curve': 14})
    out = []
    seen = set()
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


OLL = [(1, 'Dot', "R U2 R2 F R F' U2 R' F R F'"), (2, 'Dot', "F R U R' U' F' f R U R' U' f'"), (3, 'Dot', "f R U R' U' f' U' F R U R' U' F'"), (4, 'Dot', "f R U R' U' f' U F R U R' U' F'"), (17, 'Dot', "R U R' U R' F R F' U2 R' F R F'"), (18, 'Dot', "R U2 R2 F R F' U2 M' U R U' r'"), (19, 'Dot', "S' R U R' S U' R' F R F'"), (20, 'Dot', "r U R' U' M2 U R U' R' U' M'"),
       (5, 'Square', "l' U2 L U L' U l"), (6, 'Square', "r U2 R' U' R U' r'"), (7, 'Lightning', "r U R' U R U2 r'"), (8, 'Lightning', "l' U' L U' L' U2 l"), (11, 'Lightning', "r' R2 U R' U R U2 R' U M'"), (12, 'Lightning', "M' R' U' R U' R' U2 R U' M"), (39, 'Lightning', "L F' L' U' L U F U' L'"), (40, 'Lightning', "R' F R U R' U' F' U R"),
       (9, 'Fish', "R U R' U' R' F R2 U R' U' F'"), (10, 'Fish', "R U R' U R' F R F' R U2 R'"), (35, 'Fish', "R U2 R2 F R F' R U2 R'"), (37, 'Fish', "F R' F' R U R U' R'"),
       (13, 'Knight', "F U R U2 R' U' R U R' F'"), (14, 'Knight', "R' F R U R' F' R F U' F'"), (15, 'Knight', "l' U' l L' U' L U l' U l"), (16, 'Knight', "r U r' R U R' U' r U' r'"),
       (21, 'OCLL', "R U R' U R U' R' U R U2 R'"), (22, 'OCLL', "R U2 R2 U' R2 U' R2 U2 R"), (23, 'OCLL', "R2 D' R U2 R' D R U2 R"), (24, 'OCLL', "r U R' U' r' F R F'"), (25, 'OCLL', "F R' F' r U R U' r'"), (26, 'OCLL', "R U2 R' U' R U' R'"), (27, 'OCLL', "R U R' U R U2 R'"),
       (28, 'Stūri gatavi', "r U R' U' M U R U' R'"), (57, 'Stūri gatavi', "R U R' U' M' U R U' r'"),
       (29, 'Awkward', "R U R' U' R U' R' F' U' F R U R'"), (30, 'Awkward', "F U R U2 R' U' R U2 R' U' F'"), (41, 'Awkward', "R U R' U R U2 R' F R U R' U' F'"), (42, 'Awkward', "R' U' R U' R' U2 R F R U R' U' F'"),
       (31, 'P', "R' U' F U R U' R' F' R"), (32, 'P', "S R U R' U' R' F R f'"), (43, 'P', "R' U' F' U F R"), (44, 'P', "f R U R' U' f'"),
       (33, 'T', "R U R' U' R' F R F'"), (45, 'T', "F R U R' U' F'"), (34, 'C', "R U R2 U' R' F R U R U' F'"), (46, 'C', "R' U' R' F R F' U R"),
       (36, 'W', "L' U' L U' L' U L U L F' L' F"), (38, 'W', "R U R' U R U' R' U' R' F R F'"),
       (47, 'L', "F R' F' R U2 R U' R' U R U2 R'"), (48, 'L', "F R U R' U' R U R' U' F'"), (49, 'L', "r U' r2 U r2 U r2 U' r"), (50, 'L', "R' F R2 B' R2 F' R2 B R'"), (53, 'L', "l' U' L U' L' U L U' L' U2 l"), (54, 'L', "r U R' U R U' R' U R U2 r'"),
       (51, 'Line', "F U R U' R' U R U' R' F'"), (52, 'Line', "R U R' U R U' B U' B' R'"), (55, 'Line', "R' F R U R U' R2 F' R2 U' R' U R U R'"), (56, 'Line', "r U r' U R U' R' U R U' R' r U' r'")]
PLL = [('Aa', 'Stūru 3-cikls', "x R' U R' D2 R U' R' D2 R2 x'"), ('Ab', 'Stūru 3-cikls (pretēji)', "x R2 D2 R U R' D2 R U' R x'"), ('E', 'Abas diagonāles', "x' R U' R' D R U R' D' R U R' D R U' R' D' x"),
       ('Ua', 'Malu 3-cikls', "M2 U M U2 M' U M2"), ('Ub', 'Malu 3-cikls (pretēji)', "M2 U' M U2 M' U' M2"), ('H', 'Abas pretējās malas', "M2 U' M2 U2 M2 U' M2"), ('Z', 'Divi blakus malu pāri', "M' U' M2 U' M2 U' M' U2 M2"),
       ('T', 'Blakus stūri + malas', "R U R' U' R' F R2 U' R' U' R U R' F'"), ('Ja', 'Blakus stūri + malas', "x R2 F R F' R U2 r' U r U2 x'"), ('Jb', 'Blakus stūri + malas (spog.)', "R U R' F' R U R' U' R' F R2 U' R'"),
       ('Ra', 'R-tips', "R U' R' U' R U R D R' U' R D' R' U2 R'"), ('Rb', 'R-tips (spog.)', "R' U2 R U2 R' F R U R' U' R' F' R2"), ('F', 'Blakus stūri + pretējās malas', "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R"),
       ('V', 'Diagonāle + malas', "R' U R' U' R D' R' D R' U D' R2 U' R2 D R2"), ('Y', 'Diagonāle + malas', "F R U' R' U' R U R' F' R U R' U' R' F R F'"),
       ('Na', 'N-perm', "R U R' U R U R' F' R U R' U' R' F R2 U' R' U2 R U' R'"), ('Nb', 'N-perm (spog.)', "R' U R U' R' F' U' F R U R' F R' F' R U' R"),
       ('Ga', 'Stūru + malu 3-cikls', "R2 U R' U R' U' R U' R2 D U' R' U R D'"), ('Gb', 'Stūru + malu 3-cikls', "D R' U' R U D' R2 U R' U R U' R U' R2"), ('Gc', 'Stūru + malu 3-cikls', "R2 U' R U' R U R' U R2 D' U R U' R' D"), ('Gd', 'Stūru + malu 3-cikls', "R U R' U' D R2 U' R U' R' U R' U R2 D'")]
OLL2 = [('Sune', "R U R' U R U2 R'"), ('Antisune', "R U2 R' U' R U' R'"), ('Pi', "F R U R' U' R U R' U' F'"), ('H', "R2 U2 R U2 R2"), ('U', "F R U R' U' F'"), ('T', "R U R' U' R' F R F'"), ('L', "F R U' R' U' R U R' F'")]
PBL = [('adj-top', 'Blakus maiņa augšā, apakša gatava', "R U R' U' R' F R2 U' R' U' R U R' F'"), ('diag-top', 'Diagonāle augšā, apakša gatava', "F R U' R' U' R U R' F' R U R' U' R' F R F'"), ('adj-adj', 'Blakus + blakus', "R2 U' R2 U2 F2 U' R2"), ('diag-diag', 'Diagonāle + diagonāle', "R2 F2 R2"), ('adj-diag', 'Blakus augšā + diagonāle apakšā', "R U' R F2 R' U R'")]

out = {'oll': [], 'pll': [], 'oll2': [], 'pbl': [], 'problems': []}
for num, grp, alg in OLL:
    c = state_for(alg)
    if not f2l_ok(c):
        out['problems'].append(('OLL', num, 'F2L broken by inverse'))
    uf = u_face(c)
    b, f, l, r = strips(c)
    if uf.count('y') == 9:
        out['problems'].append(('OLL', num, 'inverse leaves U oriented'))
    out['oll'].append({'n': num, 'g': grp, 'alg': alg, 'c': mask(uf), 'b': mask(b), 'f': mask(f), 'l': mask(l), 'r': mask(r), 'ycount': uf.count('y')})
for name, desc, alg in PLL:
    c = state_for(alg)
    if not f2l_ok(c):
        out['problems'].append(('PLL', name, 'F2L broken'))
    if u_face(c) != 'yyyyyyyyy':
        out['problems'].append(('PLL', name, 'U not oriented'))
    c2, k = auf_fix(c)
    b, f, l, r = strips(c2)
    out['pll'].append({'n': name, 'd': desc, 'alg': alg, 'b': b, 'f': f, 'l': l, 'r': r, 'arrows': pll_arrows(c2), 'auf': k})
for name, alg in OLL2:
    c = state_for(alg)
    uf = u_face(c, 2)
    b, f, l, r = strips(c, 2)
    if not bottom_corners_ok(c):
        out['problems'].append(('OLL2', name, 'bottom corners broken'))
    out['oll2'].append({'n': name, 'alg': alg, 'c': mask(uf), 'b': mask(b), 'f': mask(f), 'l': mask(l), 'r': mask(r)})
for key, desc, alg in PBL:
    c = state_for(alg)
    uf = u_face(c, 2)
    if uf != 'yyyy':
        out['problems'].append(('PBL', key, 'U not oriented: ' + uf))
    dface = ''.join(st(c, (x, -1, z), (0, -1, 0)) for z in (-1, 1) for x in (-1, 1))
    if dface != 'wwww':
        out['problems'].append(('PBL', key, 'D not oriented: ' + dface))
    b, f, l, r = strips(c, 2)
    db, df, dl, dr = strips(c, 2, y=-1)
    out['pbl'].append({'n': key, 'd': desc, 'alg': alg, 'b': b, 'f': f, 'l': l, 'r': r, 'db': db, 'df': df, 'dl': dl, 'dr': dr})

here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, io.open(os.path.join(here, 'diagrams.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('problems:', out['problems'])
s = [d for d in out['oll'] if d['n'] == 27][0]
print('OLL27 sune', s, '\n existing: c=xyxyyyyyx b=yxx f=xxy l=xxx r=yxx')
t = [d for d in out['pll'] if d['n'] == 'T'][0]
print('T perm', t)
print('2x2 Sune', out['oll2'][0], '\n existing: c=xxyx b=yx f=xy l=xx r=yx')
for p in out['pbl']:
    print('PBL', p['n'], 'U strips b/f/l/r', p['b'], p['f'], p['l'], p['r'], '| D strips', p['db'], p['df'], p['dl'], p['dr'])
print('OLL ycounts by group:', [(d['n'], d['ycount']) for d in out['oll'] if d['g'] == 'OCLL'])
