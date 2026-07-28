# Unit tests for the cube simulator (verify_algs.py).
# Philosophy: try to FALSIFY the simulator against independently known cube
# facts (move orders, famous identities, checkerboard pattern) — not against
# values the simulator itself produced earlier.
import copy
import random
import unittest

from verify_algs import (Cube, fresh, invert, orientation_states,
                         top_corner_positions, top_oriented,
                         bottom_corners_ok, TPERM, YPERM, SUNE)

FACE_MOVES = ['R', 'L', 'U', 'D', 'F', 'B']
ALL_MOVES = list(Cube.MOVES.keys())

def sig(c):
    return tuple(sorted((tuple(p), tuple(sorted(s.items())))
                        for p, s in ((cb[0], cb[1]) for cb in c.cubies)))

def order_of(alg, limit=300):
    c = fresh()
    for i in range(1, limit + 1):
        c.apply(alg)
        if c.solved():
            return i
    return None

OPP = {'U': 'D', 'D': 'U', 'F': 'B', 'B': 'F', 'L': 'R', 'R': 'L'}
CENTERS = {'U': ((0, 1, 0), (0, 1, 0)), 'D': ((0, -1, 0), (0, -1, 0)),
           'F': ((0, 0, 1), (0, 0, 1)), 'B': ((0, 0, -1), (0, 0, -1)),
           'R': ((1, 0, 0), (1, 0, 0)), 'L': ((-1, 0, 0), (-1, 0, 0))}


class TestSimulatorFundamentals(unittest.TestCase):
    def test_solved_initially(self):
        self.assertTrue(fresh().solved())

    def test_every_move_has_state_order_4(self):
        # NOTE: solved() is orientation-blind (a whole-cube rotation still
        # "looks solved"), so single-move order must compare full state
        start = sig(fresh())
        for mv in ALL_MOVES:
            c = fresh()
            order = None
            for i in range(1, 9):
                c.apply(mv)
                if sig(c) == start:
                    order = i
                    break
            self.assertEqual(order, 4, 'move %s should have state order 4' % mv)

    def test_move_then_inverse_is_identity(self):
        for mv in ALL_MOVES:
            c = fresh()
            c.apply('%s %s\'' % (mv, mv))
            self.assertTrue(c.solved(), '%s %s\' not identity' % (mv, mv))

    def test_double_move_equals_two_quarters(self):
        for mv in ALL_MOVES:
            a, b = fresh(), fresh()
            a.apply(mv + '2')
            b.apply('%s %s' % (mv, mv))
            self.assertEqual(sig(a), sig(b), '%s2 != %s %s' % (mv, mv, mv))

    def test_sticker_count_conserved_after_scramble(self):
        random.seed(42)
        c = fresh()
        c.apply(' '.join(random.choice(ALL_MOVES) + random.choice(['', "'", '2'])
                         for _ in range(100)))
        counts = {}
        for pos, stickers in ((cb[0], cb[1]) for cb in c.cubies):
            for d, col in stickers.items():
                counts[col] = counts.get(col, 0) + 1
        self.assertEqual(sorted(counts.values()), [9] * 6)
        self.assertEqual(sum(counts.values()), 54)

    def test_centers_fixed_under_face_moves(self):
        random.seed(7)
        c = fresh()
        c.apply(' '.join(random.choice(FACE_MOVES) + random.choice(['', "'", '2'])
                         for _ in range(80)))
        for col, (pos, d) in CENTERS.items():
            self.assertEqual(c.sticker(pos, d), col,
                             'center %s moved under face turns' % col)

    def test_strict_parser_rejects_junk(self):
        with self.assertRaises(KeyError):
            fresh().apply('Q')
        with self.assertRaises(ValueError):
            fresh().apply('Rw')        # wide notation not supported -> must not silently be R
        with self.assertRaises(ValueError):
            fresh().apply("R''")

    # ---- famous independent facts ----
    def test_sexy_move_has_order_6(self):
        self.assertEqual(order_of("R U R' U'", 12), 6)

    def test_RU_has_order_105(self):
        self.assertEqual(order_of('R U', 210), 105)

    def test_tperm_and_yperm_are_involutions(self):
        self.assertEqual(order_of(TPERM, 4), 2)
        self.assertEqual(order_of(YPERM, 4), 2)

    def test_guide_hperm_is_involution_and_uperms_order_3(self):
        self.assertEqual(order_of("M2 U' M2 U2 M2 U' M2", 4), 2)     # H-perm
        self.assertEqual(order_of("M2 U M U2 M' U M2", 6), 3)        # Ua
        self.assertEqual(order_of("M2 U' M U2 M' U' M2", 6), 3)      # Ub

    def test_guide_antisune_is_inverse_of_sune(self):
        c = fresh()
        c.apply(SUNE)
        c.apply("R U2 R' U' R U' R'")   # the guides' Antisune
        self.assertTrue(c.solved())

    def test_checkerboard_pattern(self):
        c = fresh()
        c.apply('M2 E2 S2')
        for col, (pos, d) in CENTERS.items():
            self.assertEqual(c.sticker(pos, d), col)
        # corners keep face color, edges show the OPPOSITE face color
        for cb_pos, stickers in ((cb[0], cb[1]) for cb in c.cubies):
            zeros = sum(1 for v in cb_pos if v == 0)
            for d, col in stickers.items():
                face = {(0, 1, 0): 'U', (0, -1, 0): 'D', (0, 0, 1): 'F',
                        (0, 0, -1): 'B', (1, 0, 0): 'R', (-1, 0, 0): 'L'}[d]
                if zeros == 0:      # corner
                    self.assertEqual(col, face)
                elif zeros == 1:    # edge
                    self.assertEqual(col, OPP[face])

    def test_x_rotation_brings_front_to_top(self):
        c = fresh()
        c.apply('x')
        self.assertEqual(c.sticker((0, 1, 0), (0, 1, 0)), 'F')
        self.assertEqual(c.sticker((0, 0, 1), (0, 0, 1)), 'D')

    def test_y_rotation_brings_right_to_front(self):
        c = fresh()
        c.apply('y')
        self.assertEqual(c.sticker((0, 0, 1), (0, 0, 1)), 'R')
        self.assertEqual(c.sticker((-1, 0, 0), (-1, 0, 0)), 'F')

    def test_wide_r_equals_R_plus_Mprime(self):
        c = fresh()
        c.apply("r M R'")
        self.assertTrue(c.solved())

    def test_y_equals_U_Eprime_Dprime(self):
        c = fresh()
        c.apply("U E' D' y'")
        self.assertTrue(c.solved())

    def test_invert_roundtrip_on_random_algs(self):
        random.seed(3)
        for _ in range(10):
            alg = ' '.join(random.choice(ALL_MOVES) + random.choice(['', "'", '2'])
                           for _ in range(15))
            c = fresh()
            c.apply(alg)
            c.apply(invert(alg))
            self.assertTrue(c.solved(), 'invert failed for: %s' % alg)


class TestGuideCriticalClaims(unittest.TestCase):
    """Regression tests pinning the algorithm facts the guides now teach."""

    def test_old_2x2_3A_algs_really_break_the_bottom(self):
        # documents WHY they were replaced; if someone 'restores' them, this explains it
        for alg in ["L' U R' D2 R U' R' D2 R2", "R' U R' D2 R U' R' D2 R2"]:
            c = fresh()
            c.apply(alg)
            self.assertFalse(bottom_corners_ok(c), alg)

    def test_tperm_preserves_bottom_and_swaps_right_corners(self):
        c = fresh()
        c.apply(TPERM)
        self.assertTrue(bottom_corners_ok(c))
        # left pair (headlights) intact
        self.assertEqual(c.sticker((-1, 1, 1), (-1, 0, 0)), 'L')
        self.assertEqual(c.sticker((-1, 1, -1), (-1, 0, 0)), 'L')
        # right corners exchanged (their stickers no longer match home faces)
        self.assertNotEqual(c.sticker((1, 1, 1), (0, 0, 1)), 'F')
        self.assertNotEqual(c.sticker((1, 1, -1), (0, 0, -1)), 'B')

    def test_step2_rule_solves_all_reachable_states_in_3_sunes(self):
        # guide rule: exactly one yellow corner up -> hold it front-left;
        # zero or two -> turn cube until FL corner's yellow sticker faces LEFT
        def ycount(c):
            return sum(1 for p in top_corner_positions()
                       if c.sticker(p, (0, 1, 0)) == 'U')

        def run(state):
            c = copy.deepcopy(state)
            for n in range(4):
                if top_oriented(c):
                    return n
                want_oriented = (ycount(c) == 1)
                for _ in range(4):
                    if want_oriented and c.sticker((-1, 1, 1), (0, 1, 0)) == 'U':
                        break
                    if not want_oriented and c.sticker((-1, 1, 1), (-1, 0, 0)) == 'U':
                        break
                    c.apply('y')
                else:
                    return None   # holding condition unsatisfiable -> rule broken
                c.apply(SUNE)
            return 99 if not top_oriented(c) else 4

        states = [s for s in orientation_states() if not top_oriented(s)]
        self.assertGreater(len(states), 0)
        results = [run(s) for s in states]
        self.assertNotIn(None, results, 'holding rule unsatisfiable in some state')
        self.assertLessEqual(max(results), 3, 'rule needs more than 3 Sunes')

    def test_pbl_adj_adj_case_has_both_correct_pairs_at_back(self):
        c = fresh()
        c.apply(invert("R2 U' R2 U2 F2 U' R2"))
        for y in (1, -1):
            # back side of both layers uniform and correct
            self.assertEqual(c.sticker((-1, y, -1), (0, 0, -1)), 'B')
            self.assertEqual(c.sticker((1, y, -1), (0, 0, -1)), 'B')
            # front side broken
            self.assertNotEqual(c.sticker((-1, y, 1), (0, 0, 1)),
                                c.sticker((1, y, 1), (0, 0, 1)))

    def test_pbl_adj_diag_case_top_pair_front(self):
        c = fresh()
        c.apply(invert("R U' R F2 R' U R'"))
        # top layer: correct pair at FRONT
        self.assertEqual(c.sticker((-1, 1, 1), (0, 0, 1)), 'F')
        self.assertEqual(c.sticker((1, 1, 1), (0, 0, 1)), 'F')
        # bottom layer: no uniform side anywhere (diagonal)
        for d, ax in (((0, 0, 1), 2), ((0, 0, -1), 2), ((1, 0, 0), 0), ((-1, 0, 0), 0)):
            stickers = [c.sticker(p, d) for p in
                        [(x, -1, z) for x in (-1, 1) for z in (-1, 1)]
                        if p[ax] == d[ax]]
            self.assertNotEqual(stickers[0], stickers[1], 'bottom has a uniform side')

    def test_beginner_3B_solves_an_independent_diagonal_state(self):
        # Y-perm is an independently verified PURE diagonal corner swap
        # (see test_tperm_and_yperm_are_involutions + main() checks), and at
        # this point of a real solve all top corners are oriented — exactly
        # the 3B case. (First attempt used TPERM·U·TPERM·U', but two
        # transpositions sharing a corner make a 3-cycle, not a diagonal.)
        base = fresh()
        base.apply(YPERM)
        # (2x2 view: ignore edges/centers — check corners only)
        DG = "R U' R' U' F2 U' R U R' D R2"

        def corners_solved(c):
            for pos in [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]:
                for d in [(0, pos[1], 0), (pos[0], 0, 0), (0, 0, pos[2])]:
                    ref = {(0, 1, 0): 'U', (0, -1, 0): 'D', (0, 0, 1): 'F',
                           (0, 0, -1): 'B', (1, 0, 0): 'R', (-1, 0, 0): 'L'}[d]
                    if c.sticker(pos, d) != ref:
                        return False
            return True

        solved_somehow = False
        for auf in range(4):
            c = copy.deepcopy(base)
            c.apply(' '.join(['U'] * auf) if auf else 'U U U U')
            c.apply(DG)
            for uk in range(4):
                for dk in range(4):
                    t = copy.deepcopy(c)
                    if uk:
                        t.apply(' '.join(['U'] * uk))
                    if dk:
                        t.apply(' '.join(['D'] * dk))
                    if corners_solved(t):
                        solved_somehow = True
        self.assertTrue(solved_somehow,
                        '3B alg + U/D alignment cannot solve a diagonal state')

    def test_ua_perm_cycle_and_fixed_back_edge(self):
        c = fresh()
        c.apply("M2 U M U2 M' U M2")
        self.assertEqual(c.sticker((0, 1, -1), (0, 0, -1)), 'B')  # back edge fixed
        self.assertEqual(c.sticker((0, 1, 1), (0, 0, 1)), 'L')    # UL -> UF
        self.assertEqual(c.sticker((1, 1, 0), (1, 0, 0)), 'F')    # UF -> UR
        self.assertEqual(c.sticker((-1, 1, 0), (-1, 0, 0)), 'R')  # UR -> UL

    def test_beginner_step6_fixes_front_right_corner(self):
        c = fresh()
        c.apply("U R U' L' U R' U' L")
        for d, col in (((0, 1, 0), 'U'), ((0, 0, 1), 'F'), ((1, 0, 0), 'R')):
            self.assertEqual(c.sticker((1, 1, 1), d), col)

    def test_beginner_step5_fixes_front_edge(self):
        c = fresh()
        c.apply(SUNE)
        self.assertEqual(c.sticker((0, 1, 1), (0, 0, 1)), 'F')


if __name__ == '__main__':
    unittest.main()
