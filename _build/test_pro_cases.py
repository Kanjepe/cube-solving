"""Every Pro case picture is derived from the simulator and must stay consistent
with the algorithm it claims to solve. This test guards `pro_cases.py`, the
single source for all Pro diagram attributes."""
import unittest

from verify_algs import fresh, invert
import pro_cases as pc


def solved_below_top(c):
    ref = fresh()
    for pos, stickers in c.cubies:
        if pos[1] <= 0:
            for d, col in stickers.items():
                if ref.sticker(pos, d) != col:
                    return False
    return True


def top_oriented(c, n=3):
    rng = (-1, 0, 1) if n == 3 else (-1, 1)
    return all(c.sticker((x, 1, z), (0, 1, 0)) == 'U' for z in rng for x in rng)


class TestCounts(unittest.TestCase):
    def test_case_counts_match_the_methods(self):
        self.assertEqual(len(pc.OLL), 57)
        self.assertEqual(len(pc.PLL), 21)
        self.assertEqual(len(pc.F2L), 40)
        self.assertEqual(len(pc.CLL), 42)
        self.assertEqual(len(pc.OLL2), 7)
        self.assertEqual(len(pc.PBL), 5)
        self.assertEqual(len(pc.PYRA), 7)

    def test_group_sizes(self):
        self.assertEqual(sorted(k for k, _ in pc.OLL_GROUPS), sorted({d['g'] for d in pc.OLL}))
        self.assertEqual(sum(1 for d in pc.OLL if d['g'] == 'OCLL'), 7)
        self.assertEqual({g: sum(1 for d in pc.CLL if d['g'] == g) for g, _ in pc.CLL_GROUPS},
                         {'Sune': 6, 'Antisune': 6, 'U': 6, 'T': 6, 'L': 6, 'Pi': 6, 'H': 4, 'O': 2})
        self.assertEqual([len([d for d in pc.F2L if d['g'] == g]) for g in pc.F2L_GROUP_ORDER],
                         [4, 4, 6, 4, 4, 2, 6, 6, 4])
        self.assertEqual(sum(len(n) for _, n in pc.PLL_GROUPS), 21)

    def test_ids_are_unique_and_algorithms_normalized(self):
        cll_own = [d for d in pc.CLL if d['g'] != 'O']
        ids = [d['id'] for d in pc.OLL + pc.PLL + pc.F2L + cll_own + pc.OLL2 + pc.PBL + pc.PYRA + pc.OLL_EDGES]
        self.assertEqual(len(ids), len(set(ids)))
        # the two solved-orientation CLL cases ARE the PBL T and Y perms and share their ids
        pbl_ids = {d['id'] for d in pc.PBL}
        for d in pc.CLL:
            if d['g'] == 'O':
                self.assertIn(d['id'], pbl_ids)
        for d in pc.OLL + pc.PLL + pc.F2L + pc.CLL + pc.OLL2 + pc.PBL:
            self.assertNotIn('(', d['alg'])
            self.assertNotIn("2'", d['alg'])
            self.assertEqual(d['alg'], ' '.join(d['alg'].split()))


class TestInversesProduceGenuineCases(unittest.TestCase):
    def test_oll_inverse_keeps_f2l_and_leaves_top_unoriented(self):
        for d in pc.OLL + pc.OLL_EDGES:
            c = fresh()
            c.apply(invert(d['alg']))
            self.assertTrue(solved_below_top(c), d['id'])
            self.assertFalse(top_oriented(c), d['id'])
            c.apply(d['alg'])
            self.assertTrue(top_oriented(c), d['id'])

    def test_pll_inverse_keeps_f2l_and_top_oriented_but_not_solved(self):
        for d in pc.PLL:
            c = fresh()
            c.apply(invert(d['alg']))
            self.assertTrue(solved_below_top(c), d['id'])
            self.assertTrue(top_oriented(c), d['id'])
            self.assertFalse(c.solved(), d['id'])

    def test_f2l_inverse_moves_only_the_front_right_pair(self):
        for d in pc.F2L:
            c = fresh()
            c.apply(invert(d['alg']))
            ref = fresh()
            for pos, stickers in c.cubies:
                if pos[1] <= 0 and not (pos[0] == 1 and pos[2] == 1):
                    # frame independent: every sticker must match the centre of its face
                    for dd, col in stickers.items():
                        self.assertEqual(c.sticker(dd, dd), col, (d['id'], pos))
            c.apply(d['alg'])
            self.assertTrue(c.solved(), d['id'])

    def test_2x2_oll_and_cll_inverses_keep_the_bottom_layer(self):
        for d in pc.OLL2 + pc.CLL:
            c = fresh()
            c.apply(invert(d['alg']))
            for pos, stickers in c.cubies:
                if pos[1] == -1 and pos[0] and pos[2]:
                    for dd, col in stickers.items():
                        self.assertEqual(c.sticker(dd, dd), col, (d['id'], pos))

    def test_pbl_inverse_leaves_both_faces_oriented(self):
        for d in pc.PBL:
            c = fresh()
            c.apply(invert(d['alg']))
            self.assertTrue(top_oriented(c, 2), d['id'])
            self.assertTrue(all(c.sticker((x, -1, z), (0, -1, 0)) == 'D' for z in (-1, 1) for x in (-1, 1)), d['id'])
            self.assertFalse(c.solved(), d['id'])

    def test_cll_cases_fall_into_their_named_orientation_group(self):
        shapes = pc.cll_shape_masks()
        for d in pc.CLL:
            if d['g'] == 'O':
                continue
            c = fresh()
            c.apply(invert(d['alg']))
            self.assertIn(pc.top_pattern_2x2(c), shapes[d['g']], d['id'])


class TestPicturesMatchPublishedConventions(unittest.TestCase):
    def test_sune_pictures_equal_the_beginner_diagrams(self):
        sune = [d for d in pc.OLL if d['n'] == 27][0]
        self.assertEqual((sune['c'], sune['b'], sune['f'], sune['l'], sune['r']),
                         ('xyxyyyyyx', 'yxx', 'xxy', 'xxx', 'yxx'))
        sune2 = [d for d in pc.OLL2 if d['n'] == 'Sune'][0]
        self.assertEqual((sune2['c'], sune2['b'], sune2['f'], sune2['l'], sune2['r']),
                         ('xxyx', 'yx', 'xy', 'xx', 'yx'))

    def test_t_perm_has_headlights_on_the_left_and_a_double_arrow(self):
        t = [d for d in pc.PLL if d['n'] == 'T'][0]
        self.assertEqual(t['l'][0], t['l'][2])
        self.assertTrue(any(a.get('dbl') for a in t['arrows']))

    def test_f2l_pictures_colour_only_the_pair_and_centres(self):
        for d in pc.F2L:
            coloured = sum(1 for ch in d['u'] + d['f'] + d['r'] if ch != 'x')
            self.assertGreaterEqual(coloured, 3 + 2, d['id'])  # three centres + at least the two visible pair stickers
            self.assertEqual(d['f'][4], 'g', d['id'])
            self.assertEqual(d['r'][4], 'r', d['id'])
            self.assertEqual(d['u'][4], 'y', d['id'])

    def test_pbl_bottom_views_are_real_colours(self):
        for d in pc.PBL:
            b = d['bottom']
            self.assertEqual(b['c'], 'wwww', d['id'])
            for k in 'bflr':
                self.assertTrue(set(b[k]) <= set('rgbo'), (d['id'], k, b[k]))


if __name__ == '__main__':
    unittest.main()
