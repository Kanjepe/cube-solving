"""Sticker model for a Pyraminx held with U up, L/R in front and B behind.

Faces are named after the opposite vertex; face U is the green base.
Clockwise vertex cycles follow the outward view of a right-handed tetrahedron.
This model is verification tooling, not a runtime dependency of the guide.
"""

from itertools import combinations
import re


class Pyraminx:
    cycles = {'U': 'LBR', 'L': 'URB', 'R': 'UBL', 'B': 'ULR'}

    def __init__(self):
        self.edges = {
            ''.join(pair): {face: face for face in 'BLRU' if face not in pair}
            for pair in combinations('BLRU', 2)
        }
        self.axials = {v: {f: f for f in 'BLRU' if f != v} for v in 'BLRU'}
        self.tips = {v: dict(stickers) for v, stickers in self.axials.items()}

    def apply(self, sequence):
        moves = sequence.split()
        if any(not re.fullmatch(r"[ULRBulrb]'?", move) for move in moves):
            raise ValueError('Invalid Pyraminx move')
        for move in moves:
            vertex = move[0].upper()
            cycle = self.cycles[vertex]
            mapping = dict(zip(cycle, cycle[1:] + cycle[:1]))
            for _ in range(2 if move.endswith("'") else 1):
                self.tips[vertex] = {mapping[f]: c for f, c in self.tips[vertex].items()}
                if move[0].isupper():
                    self.axials[vertex] = {mapping[f]: c for f, c in self.axials[vertex].items()}
                    changed = {}
                    for position, stickers in self.edges.items():
                        if vertex in position:
                            destination = ''.join(sorted(mapping.get(v, v) for v in position))
                            changed[destination] = {mapping[f]: c for f, c in stickers.items()}
                    self.edges.update(changed)
        return self

    def base_solved(self):
        return all(f == c for pos, stickers in self.edges.items() if 'U' not in pos
                   for f, c in stickers.items())

    def key(self):
        return tuple(tuple((p, tuple(sorted(s.items()))) for p, s in sorted(group.items()))
                     for group in (self.edges, self.axials, self.tips))
