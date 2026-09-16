import unittest
import copy
import random
import re
from pathlib import Path

from pyraminx_sim import Pyraminx

CCW = "R U R' U R U R'"
CW = "R U' R' U' R U' R'"
FLIP = "L R' L' R U' R U R'"
LEFT = "R U' R'"
RIGHT = "L' U L"


def reframe(puzzle):
    # Turn the whole puzzle about U, then rename side colors with their faces.
    # This preserves the canonical solved frame while changing the front view.
    mapping = dict(zip('ULBR', 'UBRL'))
    for name in ('edges', 'axials', 'tips'):
        group = getattr(puzzle, name)
        setattr(puzzle, name, {
            ''.join(sorted(mapping[v] for v in position)):
            {mapping[f]: mapping[c] for f, c in stickers.items()}
            for position, stickers in group.items()
        })


def align_axial(puzzle, vertex):
    for _ in range(3):
        if all(f == c for f, c in puzzle.axials[vertex].items()):
            return
        puzzle.apply(vertex)
    raise AssertionError('Axial alignment failed')


def finish_edges(puzzle):
    align_axial(puzzle, 'U')
    identity = set(puzzle.edges['LU'].values())
    if identity == {'B', 'L'}:
        puzzle.apply(CCW)
    elif identity == {'L', 'R'}:
        puzzle.apply(CW)
    solved = Pyraminx()
    assert all(set(puzzle.edges[p].values()) == set(s.values()) for p, s in solved.edges.items())
    if puzzle.edges != solved.edges:
        for _ in range(3):
            if puzzle.edges['BU'] == solved.edges['BU']:
                break
            reframe(puzzle)
        puzzle.apply(FLIP)
    assert puzzle.edges == solved.edges


def taught_solve(puzzle):
    for vertex in 'LRBU':
        align_axial(puzzle, vertex)
    for vertex in 'ULRB':
        for _ in range(3):
            if puzzle.tips[vertex] == puzzle.axials[vertex]:
                break
            puzzle.apply(vertex.lower())
    for _ in range(12):
        if puzzle.base_solved():
            break
        upper = [p for p, s in puzzle.edges.items() if 'U' in p and 'U' in s.values()]
        if not upper:
            for _ in range(3):
                if puzzle.edges['LR'] != Pyraminx().edges['LR']:
                    break
                reframe(puzzle)
            puzzle.apply(LEFT)
            continue
        for _ in range(3):
            if any('U' in p and set(s.values()) == {'U', 'B'} for p, s in puzzle.edges.items()):
                break
            reframe(puzzle)
        before = {p: dict(s) for p, s in puzzle.edges.items()
                  if 'U' not in p and s == Pyraminx().edges[p]}
        for _ in range(3):
            if puzzle.edges['LU'] == {'R': 'U', 'B': 'B'}:
                puzzle.apply(LEFT)
                break
            if puzzle.edges['RU'] == {'L': 'U', 'B': 'B'}:
                puzzle.apply(RIGHT)
                break
            puzzle.apply('U')
        else:
            raise AssertionError('No documented insertion case')
        assert puzzle.edges['LR'] == Pyraminx().edges['LR']
        assert all(puzzle.edges[p] == s for p, s in before.items())
    assert puzzle.base_solved()
    finish_edges(puzzle)
    assert puzzle.key() == Pyraminx().key()


class TestPyraminxMechanics(unittest.TestCase):
    def test_turns_have_order_three_and_inverses(self):
        for move in 'ULRBulrb':
            self.assertEqual(Pyraminx().apply(' '.join([move] * 3)).key(), Pyraminx().key())
            self.assertEqual(Pyraminx().apply(move + ' ' + move + "'").key(), Pyraminx().key())

    def test_clockwise_upper_turn(self):
        puzzle = Pyraminx().apply('U')
        # Viewed from above: front-left -> rear -> front-right -> front-left.
        self.assertEqual(set(puzzle.edges['BU'].values()), {'B', 'R'})
        self.assertEqual(set(puzzle.edges['RU'].values()), {'L', 'R'})
        self.assertEqual(set(puzzle.edges['LU'].values()), {'B', 'L'})
        self.assertTrue(puzzle.base_solved())

    def test_tip_turn_changes_only_one_tip(self):
        solved = Pyraminx()
        puzzle = Pyraminx().apply('r')
        self.assertEqual(puzzle.edges, solved.edges)
        self.assertEqual(puzzle.axials, solved.axials)
        self.assertNotEqual(puzzle.tips['R'], solved.tips['R'])
        for vertex in 'ULB':
            self.assertEqual(puzzle.tips[vertex], solved.tips[vertex])

    def test_rejects_cube_notation(self):
        for move in ['U2', 'D', 'F', 'UU', "R''"]:
            with self.assertRaises(ValueError):
                Pyraminx().apply(move)

    def test_verified_insertions_and_extraction_preserve_other_base_edges(self):
        for algorithm, source, green_face in [(LEFT, 'LU', 'R'), (RIGHT, 'RU', 'L')]:
            inverse = ' '.join(m[:-1] if m.endswith("'") else m + "'" for m in algorithm.split()[::-1])
            puzzle = Pyraminx().apply(inverse)
            self.assertEqual(puzzle.edges[source], {green_face: 'U', 'B': 'B'})
            puzzle.apply(algorithm)
            self.assertEqual(puzzle.key(), Pyraminx().key())
            puzzle.apply(algorithm)
            for pos in ['BL', 'BR']:
                self.assertEqual(puzzle.edges[pos], Pyraminx().edges[pos])
            for vertex in 'LRB':
                self.assertEqual(puzzle.axials[vertex], Pyraminx().axials[vertex])

    def test_cycles_and_flip_have_the_documented_mapping(self):
        solved = Pyraminx()
        for alg, destination in [(CCW, 'RU'), (CW, 'BU')]:
            puzzle = Pyraminx().apply(alg)
            self.assertTrue(puzzle.base_solved())
            self.assertEqual(puzzle.axials, solved.axials)
            self.assertEqual(set(puzzle.edges[destination].values()), {'B', 'R'})
            self.assertEqual(puzzle.apply(alg + ' ' + alg).key(), solved.key())
        puzzle = Pyraminx().apply(FLIP)
        self.assertEqual(puzzle.edges['BU'], solved.edges['BU'])
        self.assertTrue(puzzle.base_solved())
        self.assertEqual(puzzle.edges['LU'], {'B': 'R', 'R': 'B'})
        self.assertEqual(puzzle.edges['RU'], {'B': 'L', 'L': 'B'})
        self.assertEqual(puzzle.apply(FLIP).key(), solved.key())

    def test_all_twelve_legal_last_edge_states(self):
        seen = {}
        pending = [Pyraminx()]
        while pending:
            puzzle = pending.pop()
            if puzzle.key() in seen:
                continue
            seen[puzzle.key()] = puzzle
            for algorithm in [CCW, CW, FLIP]:
                pending.append(copy.deepcopy(puzzle).apply(algorithm))
        # 3 even permutations times 4 even flip patterns.
        self.assertEqual(len(seen), 12)
        for puzzle in seen.values():
            finish_edges(puzzle)
            self.assertEqual(puzzle.key(), Pyraminx().key())

    def test_seeded_scrambles_follow_the_taught_route(self):
        rng = random.Random(20260910)
        for _ in range(200):
            scramble = ' '.join(rng.choice('ULRBulrb') + rng.choice(['', "'"]) for _ in range(30))
            taught_solve(Pyraminx().apply(scramble))

    def test_five_authored_practice_sequences(self):
        html = (Path(__file__).resolve().parents[1] / 'pyraminx/rubiks-pyraminx-guide.html').read_text(encoding='utf-8')
        sequences = re.findall(r'data-gpy-scramble="([^"]+)"', html)
        self.assertEqual(len(set(sequences)), 5)
        for sequence in sequences:
            taught_solve(Pyraminx().apply(sequence))


if __name__ == '__main__':
    unittest.main()
