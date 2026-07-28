# Integration tests for the guide HTML files and the build pipeline.
# Critical angle: the HTML must stay consistent with the MATH — every
# algorithm string must parse, and the recognition diagrams we generated
# must equal what the algorithms actually solve.
import io
import os
import re
import subprocess
import sys
import unittest

from verify_algs import Cube, fresh, invert

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G2 = os.path.join(ROOT, '2x2', 'rubiks-2x2-guide.html')
G3 = os.path.join(ROOT, '3x3', 'rubiks-3x3-guide.html')
GP = os.path.join(ROOT, 'pyraminx', 'rubiks-pyraminx-guide.html')
UNIFIED = os.path.join(ROOT, 'cube-solving.html')

def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()

def algs_in(html):
    return re.findall(r'data-alg="([^"]+)"', html)

def y_or_x(col):
    return 'y' if col == 'U' else 'x'

POS3 = {'UBL': (-1, 1, -1), 'UB': (0, 1, -1), 'UBR': (1, 1, -1),
        'UL': (-1, 1, 0), 'C': (0, 1, 0), 'UR': (1, 1, 0),
        'UFL': (-1, 1, 1), 'UF': (0, 1, 1), 'UFR': (1, 1, 1)}

def case_diagram_3x3(alg):
    c = fresh()
    c.apply(invert(alg))
    order = ('UBL', 'UB', 'UBR', 'UL', 'C', 'UR', 'UFL', 'UF', 'UFR')
    dc = ''.join(y_or_x(c.sticker(POS3[k], (0, 1, 0))) for k in order)
    db = ''.join(y_or_x(c.sticker(POS3[k], (0, 0, -1))) for k in ('UBL', 'UB', 'UBR'))
    df = ''.join(y_or_x(c.sticker(POS3[k], (0, 0, 1))) for k in ('UFL', 'UF', 'UFR'))
    dl = ''.join(y_or_x(c.sticker(POS3[k], (-1, 0, 0))) for k in ('UBL', 'UL', 'UFL'))
    dr = ''.join(y_or_x(c.sticker(POS3[k], (1, 0, 0))) for k in ('UBR', 'UR', 'UFR'))
    return dc, db, df, dl, dr

def case_diagram_2x2(alg):
    c = fresh()
    c.apply(invert(alg))
    P = {'UBL': (-1, 1, -1), 'UBR': (1, 1, -1), 'UFL': (-1, 1, 1), 'UFR': (1, 1, 1)}
    dc = ''.join(y_or_x(c.sticker(P[k], (0, 1, 0))) for k in ('UBL', 'UBR', 'UFL', 'UFR'))
    db = ''.join(y_or_x(c.sticker(P[k], (0, 0, -1))) for k in ('UBL', 'UBR'))
    df = ''.join(y_or_x(c.sticker(P[k], (0, 0, 1))) for k in ('UFL', 'UFR'))
    dl = ''.join(y_or_x(c.sticker(P[k], (-1, 0, 0))) for k in ('UBL', 'UFL'))
    dr = ''.join(y_or_x(c.sticker(P[k], (1, 0, 0))) for k in ('UBR', 'UFR'))
    return dc, db, df, dl, dr

# attribute-order independent: grab the whole tag, then pull attrs one by one
FIG_RE = re.compile(r'<figure class="dg"([^>]*)>\s*<figcaption>([^<]+)</figcaption>', re.S)

def fig_attr(attrs, name):
    m = re.search(r'%s="([^"]+)"' % re.escape(name), attrs)
    return m.group(1) if m else None


class TestBuildPipeline(unittest.TestCase):
    def test_assemble_runs_clean_and_output_exists(self):
        r = subprocess.run([sys.executable, os.path.join('_build', 'assemble.py')],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.exists(UNIFIED))

    def test_tag_balance_everywhere(self):
        for path in (G2, G3, GP, UNIFIED):
            s = read(path)
            for tag in ('div', 'section', 'table', 'figure', 'ul', 'ol'):
                self.assertEqual(len(re.findall(r'<%s\b' % tag, s)),
                                 len(re.findall(r'</%s>' % tag, s)),
                                 '%s unbalanced in %s' % (tag, os.path.basename(path)))

    def test_unified_has_all_three_panels_and_two_levels_only(self):
        s = read(UNIFIED)
        for pid in ('panel-a2', 'panel-a3', 'panel-py'):
            self.assertIn('id="%s"' % pid, s)
        self.assertNotIn('data-level="kids"', s.replace(
            "if (state.level === 'kids')", ''))  # only the JS fallback may mention kids
        self.assertNotIn('Bērniem', s)

    def test_shared_3x3_sections_visible_in_pro_mode(self):
        s = read(UNIFIED)
        panel = s[s.index('id="panel-a3"'):s.index('id="panel-py"')]
        self.assertLess(panel.index('id="a3-uzbuve"'),
                        panel.index('<div class="mode mode-beginner">'))
        self.assertLess(panel.index('id="a3-nota"'),
                        panel.index('<div class="mode mode-beginner">'))


class TestKnownBadContentStaysGone(unittest.TestCase):
    def test_broken_2x2_algorithms_absent(self):
        algs = algs_in(read(G2))
        self.assertNotIn("L' U R' D2 R U' R' D2 R2", algs)
        self.assertNotIn("R' U R' D2 R U' R' D2 R2", algs)

    def test_typos_and_bad_notation_absent(self):
        for path in (G2, G3, GP, UNIFIED):
            s = read(path).lower()
            self.assertNotIn('salikc', s, os.path.basename(path))
        self.assertNotIn("L2'", read(GP))

    def test_no_lukturi_at_back_instruction_for_tperm(self):
        s = read(G3)
        self.assertIn('turi tos <strong>pa kreisi</strong>', s)


class TestAlgorithmStringsParse(unittest.TestCase):
    def test_2x2_algs_parse_and_use_only_outer_face_moves(self):
        for alg in algs_in(read(G2)):
            c = fresh()
            c.apply(alg)   # raises on typo
            for mv in alg.split():
                self.assertIn(mv[0], 'RLUDFB',
                              '2x2 alg uses non-face move: %s in %r' % (mv, alg))

    def test_3x3_algs_parse(self):
        for alg in algs_in(read(G3)):
            c = fresh()
            c.apply(alg)   # raises on typo

    def test_pyraminx_algs_use_wca_notation_without_2(self):
        for alg in algs_in(read(GP)):
            for mv in alg.split():
                self.assertRegex(mv, r"^[ULRBulrb]'?$",
                                 'bad pyraminx move %r in %r' % (mv, alg))


class TestDiagramsMatchAlgorithms(unittest.TestCase):
    """The OLL/OCLL recognition diagrams must equal the case each listed
    algorithm actually solves (recomputed from scratch by the simulator)."""

    OLL_2X2 = {'Sune': "R U R' U R U2 R'", 'Antisune': "R U2 R' U' R U' R'",
               'Pi': "F R U R' U' R U R' U' F'", 'H': "R2 U2 R U2 R2",
               'U': "F R U R' U' F'", 'T': "R U R' U' R' F R F'",
               'L': "F R U' R' U' R U R' F'"}
    OCLL_3X3 = {'Sune': "R U R' U R U2 R'", 'Antisune': "R U2 R' U' R U' R'",
                'H': "R U R' U R U' R' U R U2 R'",
                'Pi': "R U2 R2 U' R2 U' R2 U2 R",
                'U': "R2 D' R U2 R' D R U2 R", 'T': "r U R' U' r' F R F'",
                'L': "F R' F' r U R U' r'"}

    def collect(self, path, expected_names):
        found = {}
        for attrs, caption in FIG_RE.findall(read(path)):
            if fig_attr(attrs, 'data-kind') != 'top' or not fig_attr(attrs, 'data-small'):
                continue
            vals = tuple(fig_attr(attrs, a) for a in
                         ('data-c', 'data-b', 'data-f', 'data-l', 'data-r'))
            if any(v is None or set(v) - set('xy') for v in vals):
                continue
            name = caption.split()[0].strip()
            if name in expected_names:
                found[name] = vals
        return found

    def test_2x2_oll_case_diagrams(self):
        found = self.collect(G2, self.OLL_2X2)
        self.assertEqual(sorted(found), sorted(self.OLL_2X2), 'missing OLL figures')
        for name, alg in self.OLL_2X2.items():
            self.assertEqual(found[name], case_diagram_2x2(alg),
                             '2x2 OLL diagram wrong for %s' % name)

    def test_3x3_ocll_case_diagrams(self):
        found = self.collect(G3, self.OCLL_3X3)
        self.assertEqual(sorted(found), sorted(self.OCLL_3X3), 'missing OCLL figures')
        for name, alg in self.OCLL_3X3.items():
            self.assertEqual(found[name], case_diagram_3x3(alg),
                             '3x3 OCLL diagram wrong for %s' % name)

    def test_ocll_algs_in_tables_match_tested_ones(self):
        # the diagrams are only right if the TABLE algs are the ones we tested
        s2, s3 = read(G2), read(G3)
        for alg in self.OLL_2X2.values():
            self.assertIn('data-alg="%s"' % alg, s2)
        for alg in self.OCLL_3X3.values():
            self.assertIn('data-alg="%s"' % alg, s3)


class TestPyraDiagramAttributes(unittest.TestCase):
    def test_pyra_marks_and_labels_are_valid(self):
        for path in (GP, UNIFIED, os.path.join(ROOT, '_build', 'py-beginner.html')):
            s = read(path)
            for m in re.finditer(r'data-kind="pyra"[^>]*', s):
                frag = m.group(0)
                mark = re.search(r'data-mark="([^"]+)"', frag)
                if mark:
                    idx = [int(x) for x in mark.group(1).split(',')]
                    self.assertTrue(all(0 <= i <= 8 for i in idx), frag)
                lab = re.search(r'data-plabels="([^"]+)"', frag)
                if lab:
                    self.assertEqual(len(lab.group(1)), 9, frag)
                    self.assertRegex(lab.group(1), r'^[GSM.]{9}$', frag)

    def test_piece_type_marks_are_geometrically_correct(self):
        # tips are the 3 outer corners, axials the inverted triangles next to
        # them, edges the side midpoints — fixed by the TRI grid geometry
        s = read(GP)
        self.assertIn('data-mark="0,4,8" data-plabels="G...G...G"', s)
        self.assertIn('data-mark="2,5,7" data-plabels="..S..S.S."', s)
        self.assertIn('data-mark="1,3,6" data-plabels=".M.M..M.."', s)


if __name__ == '__main__':
    unittest.main()
