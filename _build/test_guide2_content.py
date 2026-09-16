"""Integration boundaries for the standalone 2x2 redesign."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '2x2/rubiks-2x2-guide.html'


class TestGuide2Content(unittest.TestCase):
    def test_three_steps_with_progress_and_local_help(self):
        html = SOURCE.read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'data-g2-page="([^"]+)"', html), ['intro', '1', '2', '3', 'scramble'])
        self.assertEqual(re.findall(r'<input[^>]*data-g2-done="([^"]+)"', html), ['1', '2', '3'])
        for step, title in (('1', 'Baltais slānis'), ('2', 'Dzeltenā puse'), ('3', 'Stūri vietās')):
            self.assertRegex(html, r'data-g2-page="%s"[^>]*>\s*<h2 tabindex="-1">%s</h2>' % (step, title))
        self.assertIn("'Pirms sākuma', 'Baltais slānis', 'Dzeltenā puse', 'Stūri vietās', 'Sajaukšana'", html)
        self.assertIn('data-g2-help', html)
        self.assertIn('data-g2-menu', html)

    def test_existing_renderer_script_is_preserved(self):
        # The Pro block is generated (see test_guidepro_content) and the beginner
        # block is authored; the shared renderer script must stay as archived.
        source = SOURCE.read_text(encoding='utf-8')
        old = (ROOT / 'archive/2026-09-16-before-pro-rubiks-2x2-guide.html').read_text(encoding='utf-8')
        self.assertEqual(source.split('<script>')[-1], old.split('<script>')[-1])

    def test_unified_beginner_matches_standalone(self):
        def block(html):
            self.assertIn('<div class="guide2">', html)
            return html.split('<div class="guide2">')[1].split('</div><!-- /mode-beginner -->')[0]
        source = block(SOURCE.read_text(encoding='utf-8'))
        unified = block((ROOT / 'cube-solving.html').read_text(encoding='utf-8'))
        unified = re.sub(r'id="a2-([^"]+)"', r'id="\1"', unified)
        self.assertEqual(source, unified)

    def test_unified_page_has_exactly_three_beginner_blocks(self):
        current = (ROOT / 'cube-solving.html').read_text(encoding='utf-8')
        self.assertEqual(current.count('<div class="mode mode-beginner">'), 3)
        self.assertEqual(current.count('</div><!-- /mode-beginner -->'), 3)

    def test_two_by_two_uses_same_scoped_styles_as_three_by_three(self):
        source = SOURCE.read_text(encoding='utf-8')
        reference = (ROOT / '3x3/rubiks-3x3-guide.html').read_text(encoding='utf-8')
        base = re.search(r'<style data-guide3-styles>(.*?)</style>', reference, re.S).group(1)
        actual = re.search(r'<style data-guide2-styles>(.*?)</style>', source, re.S)
        self.assertIsNotNone(actual)
        normalized = actual.group(1).split('/* Standalone')[0]
        self.assertEqual(normalized.strip(), base.replace('guide3', 'guide2').replace('g3-', 'g2-').replace('a3-', 'a2-').strip())


if __name__ == '__main__':
    unittest.main()
