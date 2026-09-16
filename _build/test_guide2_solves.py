"""Corner-only proofs of the 2x2 beginner method and user sequences."""
import copy
import itertools
import random
import re
import unittest
from pathlib import Path

from verify_algs import fresh, invert, SUNE, TPERM

SOURCE = Path(__file__).resolve().parents[1] / '2x2/rubiks-2x2-guide.html'
INSERT = "R U R' U'"
TWIST = "R' D' R D"
DIAGONAL = "R U' R' U' F2 U' R U R' D R2"
MIX = "U R F2 U R F2 R U F' R"
U, D = (0, 1, 0), (0, -1, 0)
SIDES = [(0, 0, 1), (1, 0, 0), (0, 0, -1), (-1, 0, 0)]
TOP = [(x, 1, z) for x in (-1, 1) for z in (-1, 1)]
BOTTOM = [(x, -1, z) for x in (-1, 1) for z in (-1, 1)]


def cube():
    result = fresh()
    result.cubies = [cubie for cubie in result.cubies if len(cubie[1]) == 3]
    return result


def signature(c):
    return tuple(sorted((p, tuple(sorted(s.items()))) for p, s in c.cubies))


def correct(c, position):
    reference = cube()
    return all(c.sticker(position, d) == reference.sticker(position, d)
               for d in [(position[0], 0, 0), (0, position[1], 0), (0, 0, position[2])])


def turn_until(c, move, condition):
    for _ in range(4):
        if condition():
            return
        c.apply(move)
    raise AssertionError('Holding or alignment condition not reachable with ' + move)


def orient_top(c):
    # Keep the same front throughout; visit every corner using only U.
    for _ in range(4):
        for repeat in range(7):
            if c.sticker((1, 1, 1), U) == 'U':
                break
            assert repeat < 6, 'Corner did not orient after complete cycles'
            c.apply(TWIST)
        c.apply('U')
    assert all(c.sticker(p, U) == 'U' for p in TOP)
    assert all(correct(c, p) for p in BOTTOM), 'Bottom did not recover'


def pairs(c):
    return [d for d in SIDES if len({s[d] for p, s in c.cubies if p[1] == 1 and d in s}) == 1]


def permute_top(c):
    matches = pairs(c)
    assert len(matches) in (0, 1, 4)
    if len(matches) == 1:
        turn_until(c, 'y', lambda: (-1, 0, 0) in pairs(c))
        c.apply(TPERM)
    elif not matches:
        c.apply(DIAGONAL)
    turn_until(c, 'U', c.solved)
    return len(matches)


def top_states():
    # U supplies odd permutations; Sune supplies twists; T-perm connects the rest.
    pending = [cube()]
    seen = {}
    while pending:
        c = pending.pop()
        key = signature(c)
        if key in seen:
            continue
        seen[key] = c
        for algorithm in ['U', SUNE, TPERM]:
            other = copy.deepcopy(c)
            other.apply(algorithm)
            pending.append(other)
    return list(seen.values())


def solve_first_layer(c):
    # Place one white anchor by whole-cube rotation, then derive side colors from it.
    orientations = [('', c)]
    seen = set()
    while orientations:
        moves, candidate = orientations.pop()
        if correct(candidate, (-1, -1, 1)):
            c.cubies = candidate.cubies
            break
        key = signature(candidate)
        if key in seen:
            continue
        seen.add(key)
        for move in ['x', 'y']:
            other = copy.deepcopy(candidate)
            other.apply(move)
            orientations.append((moves + move, other))
    else:
        raise AssertionError('Cannot place the anchor')

    for _ in range(12):
        if all(correct(c, p) for p in BOTTOM):
            return
        candidates = [(p, s) for p, s in c.cubies if p[1] == 1 and 'D' in s.values()]
        if not candidates:
            bad = next(p for p in BOTTOM if not correct(c, p))
            # Rotate the cube and reference together; undo to retain test coordinates.
            turns = next(n for n in range(4) if rotated_position(bad, n) == (1, -1, 1))
            c.apply(' '.join(['y'] * turns))
            c.apply(INSERT)
            c.apply(' '.join(["y'"] * turns))
            continue
        colors = set(candidates[0][1].values())
        target = next(p for p, s in cube().cubies if p[1] == -1 and set(s.values()) == colors)
        turns = next(n for n in range(4) if rotated_position(target, n) == (1, -1, 1))
        c.apply(' '.join(['y'] * turns))
        turn_until(c, 'U', lambda: next(set(s.values()) for p, s in c.cubies if p == (1, 1, 1)) == colors)
        reference = cube()
        reference.apply(' '.join(['y'] * turns))
        expected = next(s for p, s in reference.cubies if p == (1, -1, 1))
        for _ in range(6):
            c.apply(INSERT)
            if next(s for p, s in c.cubies if p == (1, -1, 1)) == expected:
                break
        c.apply(' '.join(["y'"] * turns))
        assert correct(c, target)
    raise AssertionError('First layer failed to terminate')


def rotated_position(position, turns):
    from verify_algs import rot_vec
    return rot_vec(position, 'y', -turns)


class TestGuide2Solves(unittest.TestCase):
    def test_authored_permutation_diagrams_match_their_algorithms(self):
        html = SOURCE.read_text(encoding='utf-8')
        step = html.split('data-g2-page="3"', 1)[1].split('data-g2-page="scramble"', 1)[0]
        figures = re.findall(r'<figure class="dg"([^>]*)>', step)
        self.assertEqual(len(figures), 2)
        colors = {'U': 'y', 'D': 'w', 'F': 'g', 'B': 'b', 'R': 'o', 'L': 'r'}
        positions = {
            'c': ([(-1, 1, -1), (1, 1, -1), (-1, 1, 1), (1, 1, 1)], U),
            'b': ([(-1, 1, -1), (1, 1, -1)], (0, 0, -1)),
            'f': ([(-1, 1, 1), (1, 1, 1)], (0, 0, 1)),
            'l': ([(-1, 1, -1), (-1, 1, 1)], (-1, 0, 0)),
            'r': ([(1, 1, -1), (1, 1, 1)], (1, 0, 0)),
        }
        for attrs, algorithm in zip(figures, [TPERM, DIAGONAL]):
            self.assertIn('data-alg="' + algorithm + '"', step)
            c = cube()
            c.apply(invert(algorithm))
            for name, (slots, direction) in positions.items():
                expected = ''.join(colors[c.sticker(p, direction)] for p in slots)
                self.assertEqual(re.search('data-' + name + '="([^"]+)"', attrs).group(1), expected)

    def test_main_orientation_algorithm_is_authored_before_optional_sune(self):
        html = SOURCE.read_text(encoding='utf-8')
        self.assertIn('data-g2-page="2"', html)
        step = html.split('data-g2-page="2"', 1)[1].split('data-g2-page="3"', 1)[0]
        self.assertIn('data-alg="' + TWIST + '"', step)
        self.assertLess(step.index('visus 4 gājienus'), step.index('data-alg='))
        optional = re.search(r'<details data-g2-sune>(.*?)</details>', step, re.S)
        self.assertIsNotNone(optional)
        self.assertIn('data-alg="' + SUNE + '"', optional.group(1))
        self.assertEqual(step.count('data-alg="' + SUNE + '"'), 1)

    def test_all_648_last_layer_states_finish_with_the_taught_method(self):
        states = top_states()
        self.assertEqual(len(states), 648)
        cases = set()
        for c in states:
            orient_top(c)
            cases.add(permute_top(c))
            self.assertTrue(c.solved())
        self.assertEqual(cases, {0, 1, 4})

    def test_all_scrambles_and_50_random_states_solve(self):
        html = SOURCE.read_text(encoding='utf-8')
        scrambles = re.findall(r'data-g2-scramble="([^"]+)"', html)
        self.assertEqual(len(set(scrambles)), 5)
        self.assertEqual(scrambles[0], MIX)
        rng = random.Random(22)
        scrambles += [' '.join(rng.choice('RUF') + rng.choice(['', "'", '2']) for _ in range(25)) for _ in range(50)]
        for alg in scrambles:
            with self.subTest(algorithm=alg):
                c = cube()
                c.apply(alg)
                self.assertFalse(c.solved())
                solve_first_layer(c)
                orient_top(c)
                permute_top(c)
                self.assertTrue(c.solved())

    def test_finish_is_conditional_and_mix_is_reversible(self):
        c = cube()
        c.apply('R2 U2')
        self.assertFalse(c.solved(), 'Finish must not be applied to an already solved cube')
        c = cube()
        c.apply('U2 R2')
        c.apply('R2 U2')
        self.assertTrue(c.solved())
        c.apply(MIX)
        self.assertFalse(c.solved())
        c.apply(invert(MIX))
        self.assertTrue(c.solved())


if __name__ == '__main__':
    unittest.main()
