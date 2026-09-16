"""Execute the beginner instructions on physical cube states, including five scrambles."""
import copy
import itertools
import random
import re
import unittest
from pathlib import Path

from verify_algs import fresh, SUNE

SOURCE = Path(__file__).resolve().parents[1] / '3x3/rubiks-3x3-guide.html'
U, D, F = (0, 1, 0), (0, -1, 0), (0, 0, 1)
EDGE_POSITIONS = [(0, 1, 1), (1, 1, 0), (0, 1, -1), (-1, 1, 0)]
INSERT = "R U R' U'"
RIGHT = "U R U' R' U' F' U F"
LEFT = "U' L' U L U F U' F'"
CROSS = "F R U R' U' F'"
CORNERS = "U R U' L' U R' U' L"
TWIST = "R' D' R D"


def center(cube, direction):
    return cube.sticker(direction, direction)


def cubie_correct(cube, position):
    stickers = next(stickers for pos, stickers in cube.cubies if pos == position)
    return all(color == center(cube, direction) for direction, color in stickers.items())


def corner_in_place(cube, position):
    stickers = next(stickers for pos, stickers in cube.cubies if pos == position)
    return set(stickers.values()) == {center(cube, direction) for direction in stickers}


def rotate_until(cube, move, predicate):
    for _ in range(4):
        if predicate():
            return
        cube.apply(move)
    raise AssertionError('Cannot establish holding condition for ' + move)


def cross_edges_correct(cube):
    return [p for p in EDGE_POSITIONS if cubie_correct(cube, p)]


def align_best(cube):
    best, count = 0, -1
    for turn in range(4):
        value = len(cross_edges_correct(cube))
        if value > count:
            best, count = turn, value
        cube.apply('U')
    cube.apply(' '.join(['U'] * best))
    return cross_edges_correct(cube)


def solve_edges(cube):
    for _ in range(4):
        matches = align_best(cube)
        if len(matches) == 4:
            return
        assert len(matches) == 2, 'Best U alignment must have two or four matches'
        opposite = all(a + b == 0 for a, b in zip(
            (matches[0][0], matches[0][2]), (matches[1][0], matches[1][2])))
        if not opposite:
            rotate_until(cube, 'y', lambda: cubie_correct(cube, (0, 1, -1)) and cubie_correct(cube, (1, 1, 0)))
        cube.apply(SUNE)
    raise AssertionError('Yellow edge instructions did not terminate')


def solve_corners(cube):
    positions = [(x, 1, z) for x in (-1, 1) for z in (-1, 1)]
    for _ in range(4):
        correct = [p for p in positions if corner_in_place(cube, p)]
        if len(correct) == 4:
            break
        assert len(correct) in (0, 1)
        if correct:
            rotate_until(cube, 'y', lambda: corner_in_place(cube, (1, 1, 1)))
        cube.apply(CORNERS)
    assert all(corner_in_place(cube, p) for p in positions)
    # The front face stays fixed for every corner; check only after complete cycles.
    for _ in range(4):
        for repetition in range(7):
            if cube.sticker((1, 1, 1), U) == center(cube, U):
                break
            assert repetition < 6
            cube.apply(TWIST)
        cube.apply('U')
    rotate_until(cube, 'U', lambda: cube.solved())


def solve_beginner(cube):
    white = center(cube, D)
    for _ in range(100):
        candidates = [(p, s) for p, s in cube.cubies if len(s) == 2 and white in s.values()
                      and s.get(U) != white]
        if not candidates:
            break
        position, stickers = candidates[0]
        colors = set(stickers.values())
        def target():
            return next((p, s) for p, s in cube.cubies if set(s.values()) == colors)
        if stickers.get(D) == white:
            rotate_until(cube, 'y', lambda: target()[0] == (0, -1, 1))
            rotate_until(cube, 'U', lambda: cube.sticker((0, 1, 1), U) != white)
            cube.apply('F2')
        else:
            rotate_until(cube, 'y', lambda: target()[1].get(F) == white)
            position, stickers = target()
            if position[1] != 0:
                rotate_until(cube, 'U', lambda: cube.sticker((0, 1, 1), U) != white)
                cube.apply('F')
            else:
                right = position[0] == 1
                top = (1 if right else -1, 1, 0)
                rotate_until(cube, 'U', lambda: cube.sticker(top, U) != white)
                cube.apply('R' if right else "L'")
    else:
        raise AssertionError('Daisy instructions did not terminate')
    assert all(cube.sticker(p, U) == white for p in EDGE_POSITIONS)
    for _ in range(4):
        rotate_until(cube, 'U', lambda: cube.sticker((0, 1, 1), U) == white)
        colors = next(set(s.values()) for p, s in cube.cubies if p == (0, 1, 1))
        def matching_petal():
            for p in EDGE_POSITIONS:
                direction = (p[0], 0, p[2])
                if cube.sticker(p, U) == white and cube.sticker(p, direction) == center(cube, direction):
                    return True
            return False
        rotate_until(cube, 'U', matching_petal)
        rotate_until(cube, 'y', lambda: cube.sticker((0, 1, 1), U) == white and cube.sticker((0, 1, 1), F) == center(cube, F))
        cube.apply('F2')
    assert all(cubie_correct(cube, (x, -1, z)) for x, _, z in EDGE_POSITIONS)

    for _ in range(12):
        bottom = [(x, -1, z) for x in (-1, 1) for z in (-1, 1)]
        if all(cubie_correct(cube, p) for p in bottom):
            break
        candidates = [(p, s) for p, s in cube.cubies if len(s) == 3 and p[1] == 1 and white in s.values()]
        if not candidates:
            rotate_until(cube, 'y', lambda: not cubie_correct(cube, (1, -1, 1)))
            cube.apply(INSERT)
            continue
        colors = set(candidates[0][1].values())
        rotate_until(cube, 'y', lambda: colors == {white, center(cube, F), center(cube, (1, 0, 0))})
        rotate_until(cube, 'U', lambda: next(set(s.values()) for p, s in cube.cubies if p == (1, 1, 1)) == colors)
        for repeat in range(6):
            cube.apply(INSERT)
            if cubie_correct(cube, (1, -1, 1)):
                break
        assert cubie_correct(cube, (1, -1, 1))
    assert all(cubie_correct(cube, p) for p, s in cube.cubies if p[1] == -1)

    yellow = center(cube, U)
    for _ in range(12):
        middle = [(x, 0, z) for x in (-1, 1) for z in (-1, 1)]
        if all(cubie_correct(cube, p) for p in middle):
            break
        candidates = [(p, s) for p, s in cube.cubies if len(s) == 2 and p[1] == 1 and yellow not in s.values()]
        if not candidates:
            rotate_until(cube, 'y', lambda: not cubie_correct(cube, (1, 0, 1)))
            cube.apply(RIGHT)
            continue
        colors = set(candidates[0][1].values())
        rotate_until(cube, 'U', lambda: any(set(s.values()) == colors and s.get((p[0], 0, p[2])) == center(cube, (p[0], 0, p[2])) for p, s in cube.cubies if p[1] == 1 and len(s) == 2))
        rotate_until(cube, 'y', lambda: next(set(s.values()) for p, s in cube.cubies if p == (0, 1, 1)) == colors)
        right = cube.sticker((0, 1, 1), U) == center(cube, (1, 0, 0))
        cube.apply(RIGHT if right else LEFT)
    assert all(cubie_correct(cube, p) for p, s in cube.cubies if p[1] < 1)

    for _ in range(4):
        oriented = [p for p in EDGE_POSITIONS if cube.sticker(p, U) == yellow]
        if len(oriented) == 4:
            break
        assert len(oriented) in (0, 2)
        if len(oriented) == 2:
            opposite = oriented[0][0] == -oriented[1][0] and oriented[0][2] == -oriented[1][2]
            required = [(-1, 1, 0), (1, 1, 0) if opposite else (0, 1, -1)]
            rotate_until(cube, 'U', lambda: all(cube.sticker(p, U) == yellow for p in required))
        cube.apply(CROSS)
    assert all(cube.sticker(p, U) == yellow for p in EDGE_POSITIONS)
    solve_edges(cube)
    solve_corners(cube)
    assert cube.solved()


class TestCompleteBeginnerMethod(unittest.TestCase):
    def test_all_taught_algorithms_are_present(self):
        html = SOURCE.read_text(encoding='utf-8')
        for alg in (INSERT, RIGHT, LEFT, CROSS, SUNE, CORNERS, TWIST):
            self.assertIn('data-alg="' + alg + '"', html)

    def test_all_24_yellow_edge_permutations_follow_the_decision_tree(self):
        signature = lambda c: tuple(c.sticker(p, (p[0], 0, p[2])) for p in EDGE_POSITIONS)
        seen = {}
        pending = [fresh()]
        while pending:
            c = pending.pop()
            if signature(c) in seen:
                continue
            seen[signature(c)] = c
            for alg in ('U', SUNE):
                other = copy.deepcopy(c)
                other.apply(alg)
                pending.append(other)
        self.assertEqual(len(seen), 24)
        for c in seen.values():
            solve_edges(c)
            self.assertEqual(len(cross_edges_correct(c)), 4)
            self.assertTrue(all(cubie_correct(c, p) for p, s in c.cubies if p[1] < 1))

    def test_all_five_practice_scrambles_can_be_solved_by_the_instructions(self):
        html = SOURCE.read_text(encoding='utf-8')
        scrambles = re.findall(r'data-g3-scramble="([^"]+)"', html)
        self.assertEqual(len(scrambles), 5)
        for alg in scrambles:
            with self.subTest(scramble=alg):
                c = fresh()
                c.apply(alg)
                solve_beginner(c)

    def test_thirty_additional_scrambles_follow_the_complete_method(self):
        rng = random.Random(9)
        for index in range(30):
            with self.subTest(index=index):
                c = fresh()
                c.apply(' '.join(rng.choice('RLUDFB') + rng.choice(['', "'", '2']) for _ in range(25)))
                solve_beginner(c)


if __name__ == '__main__':
    unittest.main()
