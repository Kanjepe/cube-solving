# Part 2: derive OLL case diagrams, the correct step-2 rule, and PBL holdings.
import copy
import itertools

import verify_algs as sim
from verify_algs import Cube, fresh, invert

# guide color mapping for yellow-top diagrams: U->y else grey x
def y_or_x(col):
    return 'y' if col == 'U' else 'x'

TOPPOS = {'UBL': (-1, 1, -1), 'UBR': (1, 1, -1), 'UFL': (-1, 1, 1), 'UFR': (1, 1, 1)}

def oll_diagram(alg):
    c = fresh()
    c.apply(invert(alg))
    # data-c row-major from back-left: UBL UBR UFL UFR
    dc = ''.join(y_or_x(c.sticker(TOPPOS[k], (0, 1, 0))) for k in ('UBL', 'UBR', 'UFL', 'UFR'))
    db = ''.join(y_or_x(c.sticker(TOPPOS[k], (0, 0, -1))) for k in ('UBL', 'UBR'))
    df = ''.join(y_or_x(c.sticker(TOPPOS[k], (0, 0, 1))) for k in ('UFL', 'UFR'))
    dl = ''.join(y_or_x(c.sticker(TOPPOS[k], (-1, 0, 0))) for k in ('UBL', 'UFL'))
    dr = ''.join(y_or_x(c.sticker(TOPPOS[k], (1, 0, 0))) for k in ('UBR', 'UFR'))
    return dc, db, df, dl, dr

OLL2 = [('Sune', "R U R' U R U2 R'"), ('Antisune', "R U2 R' U' R U' R'"),
        ('Pi', "F R U R' U' R U R' U' F'"), ('H', "R2 U2 R U2 R2"),
        ('U', "F R U R' U' F'"), ('T', "R U R' U' R' F R F'"),
        ('L', "F R U' R' U' R U R' F'")]
print('== 2x2 OLL case diagrams (state the alg SOLVES, yellow=y, grey=x) ==')
print('   data-c order: UBL UBR UFL UFR ; b: UBL,UBR ; f: UFL,UFR ; l: UBL,UFL ; r: UBR,UFR')
for name, alg in OLL2:
    dc, db, df, dl, dr = oll_diagram(alg)
    print('   %-9s data-c="%s" data-b="%s" data-f="%s" data-l="%s" data-r="%s"'
          % (name, dc, db, df, dl, dr))

# ---- 3x3 OCLL: same algs? derive for the corner-only view (edges assumed oriented)
print('== 3x3 OCLL corner diagrams (same algs, corners; edges shown oriented) ==')
def ocll_diagram(alg):
    c = fresh()
    c.apply(invert(alg))
    names = {'UBL': (-1, 1, -1), 'UB': (0, 1, -1), 'UBR': (1, 1, -1),
             'UL': (-1, 1, 0), 'U': (0, 1, 0), 'UR': (1, 1, 0),
             'UFL': (-1, 1, 1), 'UF': (0, 1, 1), 'UFR': (1, 1, 1)}
    dc = ''.join(y_or_x(c.sticker(names[k], (0, 1, 0)))
                 for k in ('UBL', 'UB', 'UBR', 'UL', 'U', 'UR', 'UFL', 'UF', 'UFR'))
    db = ''.join(y_or_x(c.sticker(names[k], (0, 0, -1))) for k in ('UBL', 'UB', 'UBR'))
    df = ''.join(y_or_x(c.sticker(names[k], (0, 0, 1))) for k in ('UFL', 'UF', 'UFR'))
    dl = ''.join(y_or_x(c.sticker(names[k], (-1, 0, 0))) for k in ('UBL', 'UL', 'UFL'))
    dr = ''.join(y_or_x(c.sticker(names[k], (1, 0, 0))) for k in ('UBR', 'UR', 'UFR'))
    return dc, db, df, dl, dr
for name, alg in OLL2:
    dc, db, df, dl, dr = ocll_diagram(alg)
    print('   %-9s data-c="%s" data-b="%s" data-f="%s" data-l="%s" data-r="%s"'
          % (name, dc, db, df, dl, dr))

# ---- step 2 rule search ----
print('== 2x2 step-2 (Sune repetition) rule search ==')
SUNE = "R U R' U R U2 R'"
states = sim.orientation_states()
unsolved = [s for s in states if not sim.top_oriented(s)]

FACING = {'front': (0, 0, 1), 'right': (1, 0, 0), 'left': (-1, 0, 0)}

def try_rule2(state, pos, facing, max_iter=8):
    c = copy.deepcopy(state)
    for _ in range(max_iter):
        if sim.top_oriented(c):
            return True
        placed = False
        for _ in range(4):
            if facing == 'any':
                ok = c.sticker(pos, (0, 1, 0)) != 'U'
            else:
                d = FACING[facing]
                # rotate direction with position: for FL pos the side dirs differ; use abs dirs
                ok = c.sticker(pos, d) == 'U'
            if ok:
                placed = True
                break
            c.apply('y')
        if not placed:
            return False  # rule unsatisfiable in this state
        c.apply(SUNE)
    return sim.top_oriented(c)

for pos_name, pos in (('FR', (1, 1, 1)), ('FL', (-1, 1, 1))):
    for facing in ('front', 'right', 'left', 'any'):
        ok = sum(1 for s in unsolved if try_rule2(s, pos, facing))
        print('   pos=%s yellow-faces=%-6s solves %3d/%d' % (pos_name, facing, ok, len(unsolved)))

# ---- PBL holdings: full top+bottom side patterns ----
print('== PBL raw effects (which pairs stay intact, where) ==')
def pair_report(alg):
    c = fresh()
    c.apply(alg)
    # for each side direction, collect the 2 stickers of that face in layer y
    sides = {'F': (0, 0, 1), 'B': (0, 0, -1), 'L': (-1, 0, 0), 'R': (1, 0, 0)}
    out = {}
    for y in (1, -1):
        rep = []
        for nm, d in sides.items():
            st = []
            for x, z in itertools.product((-1, 1), (-1, 1)):
                pos = (x, y, z)
                # cubie on this face?
                if (d[0] and x == d[0]) or (d[2] and z == d[2]):
                    st.append(c.sticker(pos, d))
            same = st[0] == st[1]
            correct = same and st[0] == nm
            rep.append('%s:%s%s%s' % (nm, st[0], st[1], '=' if same else ' '))
        out[y] = ' '.join(rep)
    return out

for alg in ["R2 U' R2 U2 F2 U' R2", "R U' R F2 R' U R'", "R2 F2 R2"]:
    r = pair_report(alg)
    print('   %-24s TOP  %s' % (alg, r[1]))
    print('   %-24s BOT  %s' % ('', r[-1]))
