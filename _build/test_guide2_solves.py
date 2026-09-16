"""Corner-only proofs of the three-step 2x2 beginner method, optional white-layer
recovery, authored diagrams and complete solves from practice scrambles."""
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
# Step 3: with the layer that has exactly one same-colour side pair held at the
# BACK and that pair at the bottom, this cycles the other three back corners.
APERM = "R' U R' D2 R U' R' D2 R2"
ADJACENT = "L' U R' D2 R U' R' D2 R2"
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


def pairs(c, y=1):
    return [d for d in SIDES if len({s[d] for p, s in c.cubies if p[1] == y and d in s}) == 1]


def layer_solved(c, y):
    return len(pairs(c, y)) == 4


def arrange(c):
    """General permutation coverage for both algorithms, beyond the beginner flow.
    The actual beginner final step is modelled separately in permute_top()."""
    handled = []
    for y, to_back, back_again in ((-1, "x'", 'x'), (1, 'x', "x'")):
        if len(pairs(c, y)) == 1:
            c.apply(to_back)                      # yellow/white in front, this layer at the back
            turn_until(c, 'B', lambda: pairs_back_bottom(c))
            c.apply(APERM)
            c.apply(back_again)
            assert layer_solved(c, y), 'A perm did not finish the layer'
            handled.append('pair')
    for y, flip in ((1, ''), (-1, 'x2')):
        if not pairs(c, y):
            if flip:
                c.apply(flip)
            c.apply(DIAGONAL)
            if flip:
                c.apply(flip)
            assert layer_solved(c, y), 'diagonal algorithm did not finish the layer'
            handled.append('diagonal')
    assert layer_solved(c, 1) and layer_solved(c, -1)
    turn_until(c, 'U', c.solved)
    return handled


def pairs_back_bottom(c):
    # the back layer's only pair sits on the bottom face
    back = [(x, y, -1) for x in (-1, 1) for y in (-1, 1)]
    def same(face, positions):
        return len({c.sticker(p, face) for p in positions}) == 1
    on = [f for f, ps in ((D, [(-1, -1, -1), (1, -1, -1)]), (U, [(-1, 1, -1), (1, 1, -1)]),
                          ((-1, 0, 0), [(-1, -1, -1), (-1, 1, -1)]), ((1, 0, 0), [(1, -1, -1), (1, 1, -1)])) if same(f, ps)]
    return on == [D]


def permute_top(c):
    # Follow the visible final-step cards, not the broader recovery method.
    html = SOURCE.read_text(encoding='utf-8')
    step = html.split('data-g2-page="3"', 1)[1].split('data-g2-page="scramble"', 1)[0]
    cards = re.findall(r'<div class="g2-example">(.*?)</div>', step, re.S)
    algorithms = [re.search(r'data-alg="([^"]+)"', card).group(1) for card in cards]
    assert len(algorithms) == 2
    assert layer_solved(c, -1), 'The white layer must already be complete'
    matches = len(pairs(c))
    if matches == 1:
        turn_until(c, 'U', lambda: (0, 0, -1) in pairs(c))
        c.apply(algorithms[0])
        assert 'Pēc pēdējā gājiena' in cards[0] and 'dzeltenais atkal būtu augšā' in cards[0]
        c.apply("x'")
    elif matches == 0:
        c.apply(algorithms[1])
    turn_until(c, 'U', c.solved)
    return int(matches != 4)


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
    def test_optional_white_recovery_diagram_matches_the_a_perm_case(self):
        # Recovery picture: yellow in front, white at the back, seen from BELOW.
        # Back row of the bottom face = the finished pair; everything not part of the
        # rule is grey.
        html = SOURCE.read_text(encoding='utf-8')
        step = re.search(r'<details data-g2-white-recovery>(.*?)</details>', html, re.S).group(1)
        self.assertIn('data-alg="' + APERM + '"', step)
        self.assertNotIn('data-alg="' + TPERM + '"', step)
        figures = re.findall(r'<figure class="dg"([^>]*)>', step)
        self.assertEqual(len(figures), 1)
        c = cube()
        c.apply("x'")
        c.apply(invert(APERM))
        colors = {'U': 'y', 'D': 'w', 'F': 'g', 'B': 'b', 'R': 'o', 'L': 'r'}
        back_row = [colors[c.sticker(p, D)] for p in [(-1, -1, -1), (1, -1, -1)]]
        self.assertEqual(back_row[0], back_row[1], 'the pair must sit on the bottom face at the back')
        self.assertEqual({colors[c.sticker(p, (0, 0, -1))] for p in [(-1, -1, -1), (1, -1, -1)]}, {'w'})
        self.assertEqual({colors[c.sticker(p, (0, 0, 1))] for p in [(-1, -1, 1), (1, -1, 1)]}, {'y'})
        attrs = figures[0]
        self.assertEqual(re.search(r'data-c="([^"]+)"', attrs).group(1), back_row[0] * 2 + 'xx')
        self.assertEqual(re.search(r'data-b="([^"]+)"', attrs).group(1), 'ww')
        self.assertEqual(re.search(r'data-f="([^"]+)"', attrs).group(1), 'yy')
        self.assertEqual(re.search(r'data-mark="([^"]+)"', attrs).group(1), '0,1')

    def test_final_step_diagrams_match_both_algorithms(self):
        html = SOURCE.read_text(encoding='utf-8')
        step = html.split('data-g2-page="3"', 1)[1].split('<details data-g2-white-recovery>', 1)[0]
        self.assertIn('data-alg="' + DIAGONAL + '"', step)
        self.assertIn('data-alg="' + ADJACENT + '"', step)
        self.assertIn('Dzeltenais augšā, baltais lejā', step)
        self.assertRegex(step, r'gatavo malu\s*<strong>aizmugurē</strong>')
        figures = re.findall(r'<figure class="dg"([^>]*)>', step)
        self.assertEqual(len(figures), 2)
        self.assertIn('data-c="yyyy"', figures[0])
        colors = {'U': 'y', 'D': 'w', 'F': 'g', 'B': 'b', 'R': 'o', 'L': 'r'}
        positions = {
            'c': ([(-1, 1, -1), (1, 1, -1), (-1, 1, 1), (1, 1, 1)], U),
            'b': ([(-1, 1, -1), (1, 1, -1)], (0, 0, -1)),
            'f': ([(-1, 1, 1), (1, 1, 1)], (0, 0, 1)),
            'l': ([(-1, 1, -1), (-1, 1, 1)], (-1, 0, 0)),
            'r': ([(1, 1, -1), (1, 1, 1)], (1, 0, 0)),
        }
        for attrs, algorithm in zip(figures, [ADJACENT + " x'", DIAGONAL]):
            c = cube()
            c.apply(invert(algorithm))
            for name, (slots, direction) in positions.items():
                expected = ''.join(colors[c.sticker(p, direction)] for p in slots)
                self.assertEqual(re.search('data-' + name + '="([^"]+)"', attrs).group(1), expected)

    def test_a_perm_finishes_every_one_pair_layer_and_keeps_both_faces(self):
        # every permutation of the back layer reachable with B turns and the A perm
        seen = {}
        todo = [cube()]
        while todo:
            c = todo.pop()
            key = signature(c)
            if key in seen:
                continue
            seen[key] = c
            for move in ['B', APERM, invert(APERM)]:
                other = copy.deepcopy(c)
                other.apply(move)
                todo.append(other)
        self.assertEqual(len(seen), 24)
        one_pair = 0
        for c in seen.values():
            back_pairs = [f for f, ps in ((U, [(-1, 1, -1), (1, 1, -1)]), (D, [(-1, -1, -1), (1, -1, -1)]),
                                          ((-1, 0, 0), [(-1, -1, -1), (-1, 1, -1)]), ((1, 0, 0), [(1, -1, -1), (1, 1, -1)]))
                          if len({c.sticker(p, f) for p in ps}) == 1]
            if len(back_pairs) != 1:
                continue
            one_pair += 1
            turn_until(c, 'B', lambda: pairs_back_bottom(c))
            c.apply(APERM)
            self.assertTrue(all(len({s[(0, 0, 1)] for p, s in c.cubies if p[2] == 1}) == 1 for _ in [0]), 'front face broken')
            self.assertTrue(len({s[(0, 0, -1)] for p, s in c.cubies if p[2] == -1}) == 1, 'back face broken')
            turn_until(c, 'B', c.solved)
        self.assertEqual(one_pair, 16)

    def test_adjacent_algorithm_finishes_the_top_pair_at_the_back(self):
        # The guide's final adjacent case: yellow is up, white is down, and the
        # one finished side pair is at the back. Its natural hand position ends
        # with the cube rotated by x', which is a whole-cube rotation only.
        c = cube()
        c.apply(invert(ADJACENT + " x'"))
        self.assertEqual(pairs(c, 1), [(0, 0, -1)])
        self.assertTrue(layer_solved(c, -1))
        c.apply(ADJACENT + " x'")
        self.assertTrue(c.solved())

    def test_general_permutation_algorithms_cover_both_layers(self):
        # both faces oriented, both layers permuted arbitrarily (24 x 24 states)
        seen = {}
        todo = [cube()]
        while todo:
            c = todo.pop()
            key = signature(c)
            if key in seen:
                continue
            seen[key] = c
            for move in ['U', 'D', "x' " + APERM + " x", "x " + APERM + " x'"]:
                other = copy.deepcopy(c)
                other.apply(move)
                todo.append(other)
        self.assertEqual(len(seen), 576)
        cases = set()
        for c in seen.values():
            cases.add(tuple(arrange(c)))
            self.assertTrue(c.solved())
        self.assertIn(('pair', 'pair'), cases)
        self.assertIn(('diagonal', 'diagonal'), cases)
        self.assertIn(('pair', 'diagonal'), cases)

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
        self.assertEqual(cases, {0, 1})  # nothing to do, or one handled case (pair or diagonal)

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
