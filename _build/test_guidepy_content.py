"""Pyraminx source ownership and presentation regression checks."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestGuidePyContent(unittest.TestCase):
    def test_pages_and_explicit_checkpoints(self):
        html = (ROOT / 'pyraminx/rubiks-pyraminx-guide.html').read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'data-gpy-page="([^"]+)"', html), ['intro', '1', '2', '3', 'scramble'])
        for number in '123':
            page = re.search(r'data-gpy-page="' + number + r'"(.*?)</section>', html, re.S).group(1)
            for marker in ['gpy-grip', 'gpy-check', 'data-gpy-done', 'gpy-goal']:
                self.assertIn(marker, page)
        for marker in ['data-gpy-case="left"', 'data-gpy-case="right"', 'data-gpy-case="flip"', 'data-gpy-topview']:
            self.assertIn(marker, html)

    def test_canonical_source_and_pro_preservation(self):
        html = (ROOT / 'pyraminx/rubiks-pyraminx-guide.html').read_text(encoding='utf-8')
        unified = (ROOT / 'cube-solving.html').read_text(encoding='utf-8')
        marker = '<div class="guidepy">'
        self.assertIn(marker, html)
        source = html.split(marker)[1].split('</div><!-- /mode-beginner -->')[0]
        built = unified.split(marker)[1].split('</div><!-- /mode-beginner -->')[0]
        built = re.sub(r'id="py-([^"]+)"', r'id="\1"', built)
        self.assertEqual(source, built)
        old = (ROOT / 'archive/2026-09-10-rubiks-pyraminx-guide.html').read_text(encoding='utf-8')
        marker = '<div class="mode mode-pro">'
        end = '</div><!-- /mode-pro -->'
        self.assertEqual(html.split(marker)[1].split(end)[0], old.split(marker)[1].split(end)[0])
        self.assertEqual(html.split('<script>')[-1], old.split('<script>')[-1])

    def test_other_puzzles_are_unchanged(self):
        old = (ROOT / 'archive/2026-09-10-before-pyraminx-cube-solving.html').read_text(encoding='utf-8')
        new = (ROOT / 'cube-solving.html').read_text(encoding='utf-8')
        start = '<div class="cubepanel" id="panel-a2"'
        end = '<div class="cubepanel" id="panel-py"'
        self.assertEqual(new.split(start)[1].split(end)[0], old.split(start)[1].split(end)[0])

    def test_shared_layout_matches_three_by_three(self):
        reference = (ROOT / '3x3/rubiks-3x3-guide.html').read_text(encoding='utf-8')
        html = (ROOT / 'pyraminx/rubiks-pyraminx-guide.html').read_text(encoding='utf-8')
        base = re.search(r'<style data-guide3-styles>(.*?)</style>', reference, re.S).group(1)
        actual = re.search(r'<style data-guidepy-styles>(.*?)</style>', html, re.S)
        self.assertIsNotNone(actual)
        self.assertEqual(actual.group(1).split('/* Standalone')[0].strip(),
                         base.replace('guide3', 'guidepy').replace('g3-', 'gpy-').replace('a3-', 'py-').strip())


if __name__ == '__main__':
    unittest.main()
