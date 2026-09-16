import re
import unittest
from pathlib import Path

from verify_algs import fresh, invert

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '3x3' / 'rubiks-3x3-guide.html'


class TestBeginnerMobileContent(unittest.TestCase):
    def test_unified_beginner_matches_the_standalone_source(self):
        def beginner(html):
            return html.split('<div class="guide3">', 1)[1].split('</div><!-- /mode-beginner -->', 1)[0]
        source = beginner(SOURCE.read_text(encoding='utf-8'))
        unified = beginner((ROOT / 'cube-solving.html').read_text(encoding='utf-8'))
        unified = re.sub(r'id="a3-([^"]+)"', r'id="\1"', unified)
        self.assertEqual(source, unified)

    def test_generated_page_uses_lf_line_endings(self):
        self.assertFalse(b'\r\n' in (ROOT / 'cube-solving.html').read_bytes(),
                         'Generated HTML must use LF line endings')

    def test_grip_diagrams_have_readable_latvian_labels(self):
        html = SOURCE.read_text(encoding='utf-8')
        figures = re.findall(r'<figure class="g3-grip-figure">(.*?)</figure>', html, re.S)
        self.assertEqual(len(figures), 3)
        for figure in figures:
            self.assertIn('Priekšpuse', figure)
            self.assertIn('Labā puse', figure)
            self.assertIn('Atzīmēts viens gabaliņš: augšā, priekšā pa labi.', figure)
            self.assertIn('Sānu centru krāsas ir tikai piemērs.', figure)
            self.assertNotIn('?', figure)

    def test_shared_tail_is_identical_to_the_archived_source(self):
        html = SOURCE.read_text(encoding='utf-8')
        # footer and shared renderer script: unchanged since before the Pro redesign
        before_pro = (ROOT / 'archive/2026-09-16-before-pro-rubiks-3x3-guide.html').read_text(encoding='utf-8')
        end = '</div><!-- /mode-pro -->'
        self.assertEqual(html[html.index(end):], before_pro[before_pro.index(end):])

    def test_all_learning_pages_and_local_help_exist(self):
        html = SOURCE.read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'data-g3-page="([^"]+)"', html),
                         ['intro', '1', '2', '3', '4', '5', '6', '7', 'scramble'])
        self.assertIn('data-g3-help', html)
        self.assertIn('data-g3-menu', html)

    def test_five_distinct_scrambles_mix_all_faces_and_are_reversible(self):
        html = SOURCE.read_text(encoding='utf-8')
        scrambles = re.findall(r'data-g3-scramble="([^"]+)"', html)
        self.assertEqual(len(set(scrambles)), 5)
        states = set()
        for alg in scrambles:
            moves = alg.split()
            self.assertEqual(len(moves), 25)
            self.assertEqual({move[0] for move in moves}, set('RLUDFB'))
            for first, second in zip(moves, moves[1:]):
                self.assertNotEqual(first[0], second[0])
            c = fresh()
            c.apply(alg)
            self.assertFalse(c.solved())
            self.assertTrue(all(not c.face_solved(d) for d in
                                 [(1, 0, 0), (-1, 0, 0), (0, 1, 0),
                                  (0, -1, 0), (0, 0, 1), (0, 0, -1)]))
            states.add(repr(c.cubies))
            c.apply(invert(alg))
            self.assertTrue(c.solved())
        self.assertEqual(len(states), 5)

    def test_final_step_warns_before_the_algorithm(self):
        html = SOURCE.read_text(encoding='utf-8')
        section = re.search(r'data-g3-page="7"([\s\S]*?)data-g3-page="scramble"', html)
        self.assertIsNotNone(section)
        text = section.group(1)
        self.assertLess(text.index('visus 4 gājienus'), text.index('data-alg='))
        self.assertNotIn('līdz apakšējās kārtas atkal', text)


if __name__ == '__main__':
    unittest.main()
