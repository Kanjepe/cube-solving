# Cubie-based NxN cube simulator used to verify every algorithm claim in the
# guides before editing them. Coordinates: x -> R, y -> U, z -> F.
# Colors are named by home face: U D F B L R.
# Import-safe: the self-checks run only when executed directly.
import copy
import itertools

AXES = {'x': 0, 'y': 1, 'z': 2}

def rot_vec(v, axis, quarter):
    # quarter = number of +90-degree steps around axis (right-hand rule)
    x, y, z = v
    for _ in range(quarter % 4):
        if axis == 'x':   x, y, z = x, -z, y
        elif axis == 'y': x, y, z = z, y, -x
        else:             x, y, z = -y, x, z
    return (x, y, z)

class Cube:
    def __init__(self):
        self.cubies = []  # list of [pos, {dir: color}]
        faces = {(0, 1, 0): 'U', (0, -1, 0): 'D', (0, 0, 1): 'F',
                 (0, 0, -1): 'B', (1, 0, 0): 'R', (-1, 0, 0): 'L'}
        for pos in itertools.product((-1, 0, 1), repeat=3):
            if pos == (0, 0, 0):
                continue
            stickers = {}
            for d, col in faces.items():
                if (d[0] and d[0] == pos[0]) or (d[1] and d[1] == pos[1]) or (d[2] and d[2] == pos[2]):
                    stickers[d] = col
            if stickers:
                self.cubies.append([pos, stickers])

    def turn(self, axis, layer_sel, quarter):
        ax = AXES[axis]
        for c in self.cubies:
            if c[0][ax] in layer_sel:
                c[0] = rot_vec(c[0], axis, quarter)
                c[1] = {rot_vec(d, axis, quarter): col for d, col in c[1].items()}

    # face turns: clockwise viewed from outside the face
    MOVES = {
        'R': ('x', (1,), -1), 'L': ('x', (-1,), 1), 'M': ('x', (0,), 1),
        'U': ('y', (1,), -1), 'D': ('y', (-1,), 1), 'E': ('y', (0,), 1),
        'F': ('z', (1,), -1), 'B': ('z', (-1,), 1), 'S': ('z', (0,), -1),
        'r': ('x', (1, 0), -1), 'l': ('x', (-1, 0), 1), 'u': ('y', (1, 0), -1),
        'd': ('y', (-1, 0), 1), 'f': ('z', (1, 0), -1), 'b': ('z', (-1, 0), 1),
        'x': ('x', (-1, 0, 1), -1), 'y': ('y', (-1, 0, 1), -1), 'z': ('z', (-1, 0, 1), -1),
    }

    def apply(self, alg):
        for mv in alg.split():
            base = mv[0]
            rest = mv[1:]
            if base not in self.MOVES:
                raise KeyError('unknown move: %r' % mv)
            if rest not in ('', "'", '2', "2'"):
                raise ValueError('bad move suffix: %r' % mv)
            axis, layers, q = self.MOVES[base]
            n = q
            if '2' in rest:
                n = q * 2
            if "'" in rest:
                n = -n
            self.turn(axis, layers, n)

    def sticker(self, pos, direction):
        for c in self.cubies:
            if c[0] == pos:
                return c[1].get(direction)
        return None

    def face_solved(self, direction):
        cols = set()
        for c in self.cubies:
            if direction in c[1]:
                ax = [i for i in range(3) if direction[i]][0]
                if c[0][ax] == direction[ax]:
                    cols.add(c[1][direction])
        return len(cols) == 1

    def solved(self):
        return all(self.face_solved(d) for d in
                   [(0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0)])

    def layer_snapshot(self, y):
        out = []
        for c in self.cubies:
            if c[0][1] == y:
                for d, col in sorted(c[1].items()):
                    out.append((c[0], d, col))
        return sorted(out)

def fresh():
    return Cube()

def invert(alg):
    out = []
    for mv in reversed(alg.split()):
        if mv.endswith('2'):
            out.append(mv)
        elif mv.endswith("'"):
            out.append(mv[:-1])
        else:
            out.append(mv + "'")
    return ' '.join(out)

TPERM = "R U R' U' R' F R2 U' R' U' R U R' F'"
YPERM = "F R U' R' U' R U R' F' R U R' U' R' F R F'"
SUNE = "R U R' U R U2 R'"

# ---------- 2x2 helpers (corners only; same sim, ignore edges/centers) ----------
def bottom_corners_ok(c):
    ref = fresh()
    for pos in itertools.product((-1, 1), (-1,), (-1, 1)):
        for d in [(0, -1, 0), (pos[0], 0, 0), (0, 0, pos[2])]:
            if c.sticker(pos, d) != ref.sticker(pos, d):
                return False
    return True

def top_corner_positions():
    return [(x, 1, z) for x in (-1, 1) for z in (-1, 1)]

def top_oriented(c):
    return all(c.sticker(p, (0, 1, 0)) == 'U' for p in top_corner_positions())

def orientation_states():
    # all distinct top-layer states reachable via {Sune, U} with bottom intact
    seen = {}
    frontier = [fresh()]
    sig = lambda c: tuple(c.sticker(p, d) for p in top_corner_positions()
                          for d in [(0, 1, 0), (p[0], 0, 0), (0, 0, p[2])])
    seen[sig(frontier[0])] = frontier[0]
    while frontier:
        cur = frontier.pop()
        for alg in [SUNE, "U"]:
            nxt = copy.deepcopy(cur)
            nxt.apply(alg)
            if not bottom_corners_ok(nxt):
                continue
            s = sig(nxt)
            if s not in seen:
                seen[s] = nxt
                frontier.append(nxt)
    return list(seen.values())

def check(name, cond, detail=''):
    print('%-58s %s %s' % (name, 'OK' if cond else '** FAIL **', detail))

def main():
    c = fresh(); c.apply('R R R R'); check('sanity: R4 = identity', c.solved())
    c = fresh(); c.apply(' '.join(["R U R' U'"] * 6)); check('sanity: (sexy)x6 = identity', c.solved())
    c = fresh(); c.apply(TPERM); c.apply(TPERM); check('sanity: T-perm twice = identity', c.solved())
    c2 = fresh()
    for _ in range(3):
        c2.apply("M2 U M U2 M' U M2")
    check('sanity: Ua-perm order 3', c2.solved())

    c = fresh(); c.apply(TPERM)
    ufl = c.sticker((-1, 1, 1), (0, 0, 1)); ubl = c.sticker((-1, 1, -1), (0, 0, -1))
    left_pair_intact = (ufl == 'F' and ubl == 'B' and
                        c.sticker((-1, 1, 1), (-1, 0, 0)) == 'L' and
                        c.sticker((-1, 1, -1), (-1, 0, 0)) == 'L')
    bottom_ok = fresh().layer_snapshot(-1) == c.layer_snapshot(-1)
    check('3x3 T-perm: left corner pair intact (headlights LEFT)', left_pair_intact)
    check('3x3 T-perm: bottom layer untouched', bottom_ok)
    uf = c.sticker((0, 1, 1), (0, 0, 1)); ul = c.sticker((-1, 1, 0), (-1, 0, 0))
    ur = c.sticker((1, 1, 0), (1, 0, 0)); ub = c.sticker((0, 1, -1), (0, 0, -1))
    check('3x3 T-perm: edges UL<->UR swapped, UF/UB fixed',
          uf == 'F' and ub == 'B' and ul == 'R' and ur == 'L')

    c = fresh(); c.apply("M2 U M U2 M' U M2")
    check('3x3 Ua-perm: back edge fixed', c.sticker((0, 1, -1), (0, 0, -1)) == 'B')

    c = fresh(); c.apply(YPERM)
    diag = (c.sticker((1, 1, 1), (0, 0, 1)) != 'F' and c.sticker((-1, 1, -1), (0, 0, -1)) != 'B'
            and c.sticker((-1, 1, 1), (0, 0, 1)) == 'F' and c.sticker((1, 1, -1), (0, 0, -1)) == 'B')
    check('3x3 Y-perm: UFR<->UBL diagonal swapped, other fixed', diag)
    check('3x3 Y-perm: bottom layer untouched', fresh().layer_snapshot(-1) == c.layer_snapshot(-1))

    for alg in ["L' U R' D2 R U' R' D2 R2", "R' U R' D2 R U' R' D2 R2"]:
        c = fresh(); c.apply(alg)
        check('2x2 old 3A alg "%s": breaks bottom (expected)' % alg,
              not bottom_corners_ok(c))
    c = fresh(); c.apply(TPERM)
    check('2x2 T-perm: bottom corners preserved', bottom_corners_ok(c))

    states = orientation_states()
    print('   distinct top states reachable via Sune/U with bottom intact: %d' % len(states))

if __name__ == '__main__':
    main()
