# Part 3: step-2 oriented-corner rule + adj+adj PBL case pattern.
import copy

import verify_algs as sim
from verify_algs import fresh, invert

SUNE = "R U R' U R U2 R'"
states = sim.orientation_states()
unsolved = [s for s in states if not sim.top_oriented(s)]
print('unsolved reachable states: %d' % len(unsolved))

def oriented(c, pos):
    return c.sticker(pos, (0, 1, 0)) == 'U'

def rule_oriented_FL(state, max_iter=10):
    # "if some corner already shows yellow on top, hold it front-left;
    #  if none does, just do Sune from any position; repeat"
    c = copy.deepcopy(state)
    for _ in range(max_iter):
        if sim.top_oriented(c):
            return True
        any_oriented = any(oriented(c, p) for p in
                           [(1, 1, 1), (-1, 1, 1), (1, 1, -1), (-1, 1, -1)])
        if any_oriented:
            for _ in range(4):
                if oriented(c, (-1, 1, 1)):
                    break
                c.apply('y')
        c.apply(SUNE)
    return sim.top_oriented(c)

ok = sum(1 for s in unsolved if rule_oriented_FL(s))
print('rule "oriented corner FRONT-LEFT, else any": %d/%d' % (ok, len(unsolved)))

# worst-case Sune count for that rule
def count_sunes(state):
    c = copy.deepcopy(state)
    n = 0
    while not sim.top_oriented(c) and n < 10:
        if any(oriented(c, p) for p in [(1, 1, 1), (-1, 1, 1), (1, 1, -1), (-1, 1, -1)]):
            for _ in range(4):
                if oriented(c, (-1, 1, 1)):
                    break
                c.apply('y')
        c.apply(SUNE)
        n += 1
    return n if sim.top_oriented(c) else -1

counts = [count_sunes(s) for s in unsolved]
print('max Sune count: %s (fail=-1 count: %d)' % (max(counts), counts.count(-1)))

# also try variant: oriented corner FRONT-RIGHT
def rule_oriented_FR(state, max_iter=10):
    c = copy.deepcopy(state)
    for _ in range(max_iter):
        if sim.top_oriented(c):
            return True
        if any(oriented(c, p) for p in [(1, 1, 1), (-1, 1, 1), (1, 1, -1), (-1, 1, -1)]):
            for _ in range(4):
                if oriented(c, (1, 1, 1)):
                    break
                c.apply('y')
        c.apply(SUNE)
    return sim.top_oriented(c)
ok = sum(1 for s in unsolved if rule_oriented_FR(s))
print('rule "oriented corner FRONT-RIGHT, else any": %d/%d' % (ok, len(unsolved)))

# ---- adj+adj PBL: pattern of the case the alg SOLVES (inverse applied) ----
import itertools
def pair_report(c):
    sides = {'F': (0, 0, 1), 'B': (0, 0, -1), 'L': (-1, 0, 0), 'R': (1, 0, 0)}
    out = {}
    for y in (1, -1):
        rep = []
        for nm, d in sides.items():
            st = []
            for x, z in itertools.product((-1, 1), (-1, 1)):
                if (d[0] and x == d[0]) or (d[2] and z == d[2]):
                    st.append(c.sticker((x, y, z), d))
            rep.append('%s:%s%s%s' % (nm, st[0], st[1], '=' if st[0] == st[1] else ' '))
        out[y] = ' '.join(rep)
    return out

for alg in ["R2 U' R2 U2 F2 U' R2"]:
    c = fresh()
    c.apply(invert(alg))
    r = pair_report(c)
    print('case solved by %s:' % alg)
    print('   TOP %s' % r[1])
    print('   BOT %s' % r[-1])
