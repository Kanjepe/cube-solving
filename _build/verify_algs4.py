# Part 4: search a composite, teachable step-2 rule:
#   policy = f(number of yellow stickers on top) -> holding condition
import copy
import itertools

import verify_algs as sim
from verify_algs import fresh

SUNE = "R U R' U R U2 R'"
TOP = [(-1, 1, -1), (1, 1, -1), (-1, 1, 1), (1, 1, 1)]  # UBL UBR UFL UFR
FL, FR = (-1, 1, 1), (1, 1, 1)

def ycount(c):
    return sum(1 for p in TOP if c.sticker(p, (0, 1, 0)) == 'U')

# holding conditions, each returns True if current rotation satisfies it
CONDS = {
    'orientedFL':  lambda c: c.sticker(FL, (0, 1, 0)) == 'U',
    'orientedFR':  lambda c: c.sticker(FR, (0, 1, 0)) == 'U',
    'yFLfront':    lambda c: c.sticker(FL, (0, 0, 1)) == 'U',
    'yFLleft':     lambda c: c.sticker(FL, (-1, 0, 0)) == 'U',
    'yFRfront':    lambda c: c.sticker(FR, (0, 0, 1)) == 'U',
    'yFRright':    lambda c: c.sticker(FR, (1, 0, 0)) == 'U',
    'any':         lambda c: True,
}

def run_policy(state, pol, max_iter=8):
    c = copy.deepcopy(state)
    for _ in range(max_iter):
        if sim.top_oriented(c):
            return True
        cond = CONDS[pol[min(ycount(c), 2)]]
        placed = False
        for _ in range(4):
            if cond(c):
                placed = True
                break
            c.apply('y')
        if not placed:
            return False
        c.apply(SUNE)
    return sim.top_oriented(c)

states = sim.orientation_states()
unsolved = [s for s in states if not sim.top_oriented(s)]

opts0 = ['yFLfront', 'yFLleft', 'yFRfront', 'yFRright', 'any']
opts1 = ['orientedFL', 'orientedFR']
opts2 = ['yFLfront', 'yFLleft', 'yFRfront', 'yFRright', 'any']
best = []
for p0, p1, p2 in itertools.product(opts0, opts1, opts2):
    pol = {0: p0, 1: p1, 2: p2}
    ok = sum(1 for s in unsolved if run_policy(s, pol))
    if ok == len(unsolved):
        best.append((p0, p1, p2))
    elif ok > 96:
        print('near miss %s: %d/%d' % ((p0, p1, p2), ok, len(unsolved)))
print('policies solving ALL %d states:' % len(unsolved))
for b in best:
    # measure worst-case sune count
    def cnt(state):
        c = copy.deepcopy(state); n = 0
        while not sim.top_oriented(c) and n < 8:
            cond = CONDS[{0: b[0], 1: b[1], 2: b[2]}[min(ycount(c), 2)]]
            for _ in range(4):
                if cond(c):
                    break
                c.apply('y')
            c.apply(SUNE); n += 1
        return n
    mx = max(cnt(s) for s in unsolved)
    print('   0y:%-9s 1y:%-10s 2y:%-9s  (max Sunes: %d)' % (b[0], b[1], b[2], mx))
