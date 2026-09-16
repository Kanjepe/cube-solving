# Cube Solving Guides

Interactive, single-page HTML guides (in Latvian) for solving three twisty puzzles:

- **2×2 Rubik's Cube** — Ortega beginner method + CLL for advanced solvers
- **3×3 Rubik's Cube** — classic 7-step layer-by-layer method + full CFOP (F2L, OLL, PLL)
- **Pyraminx** — layer-by-layer beginner method + L4E/Oka for advanced solvers

Everything is plain HTML/CSS/JS — no frameworks, no build dependencies beyond Python for assembly. Open any guide directly in a browser.

## The unified guide

[`cube-solving.html`](cube-solving.html) combines all three puzzles into one page with:

- a **puzzle selector** (2×2 / 3×3 / Pyraminx) in a sticky top bar
- a **difficulty selector** with three levels:
  - **Kids** — simplified steps, age-appropriate language, See/Do/Help structure
  - **Beginner** — detailed step-by-step instructions with diagnostic decision trees
  - **Pro** — advanced speedcubing methods (CFOP, CLL, L4E)
- inline cube diagrams rendered with JavaScript
- selection persisted between visits

## Project structure

```
├── cube-solving.html            # unified guide (GENERATED — do not edit by hand)
├── 2x2/rubiks-2x2-guide.html    # standalone 2×2 guide (source)
├── 3x3/rubiks-3x3-guide.html    # standalone 3×3 guide (source)
├── pyraminx/rubiks-pyraminx-guide.html  # standalone Pyraminx guide (source)
└── _build/
    ├── assemble.py              # build script — assembles cube-solving.html
    ├── shell-top.html           # unified page shell (head, styles, top bar)
    ├── shell-end.html           # unified page shell (scripts, footer)
    ├── kids-a2.html             # kids-level content for 2×2
    ├── kids-a3.html             # kids-level content for 3×3
    ├── kids-py.html             # kids-level content for Pyraminx
    └── py-beginner.html         # rewritten detailed Pyraminx beginner content
```

## Building

`cube-solving.html` is generated — never edit it directly. To rebuild after changing any source guide or fragment:

```
python _build/assemble.py
```

The script extracts the `<main>` content and step navigation from each standalone guide, prefixes element IDs to avoid collisions (`a2-`, `a3-`, `py-`), wraps them in the shell fragments, and writes the result to `cube-solving.html` (two levels: Iesācējs / Pro).

The three standalone guides in `2x2/`, `3x3/`, and `pyraminx/` remain fully usable on their own.

## Testing

```
python -m unittest discover -s _build -p "test_*.py"
```

- `_build/test_cubesim.py` — cube-simulator correctness against independently known facts (move orders, famous identities) plus regression tests for every algorithm claim the guides teach.
- `_build/test_guides.py` — build pipeline and HTML content: every `data-alg` string must parse, OLL/OCLL recognition diagrams are recomputed from the algorithms and compared against the HTML.
- `_build/verify_algs*.py` — one-off derivation scripts kept for reference (how the diagrams, holdings, and the step-2 rule were computed).

Known gap: the in-page JavaScript (SVG rendering, level switching, localStorage) has no automated tests — diagram data is validated at the attribute level only.

## 3x3 beginner mobile guide (September 2026)

The current build has two levels, Beginner and Pro; the Kids entries above describe the historical layout and their files are now archived. The 3x3 beginner guide presents one learning step at a time with saved progress, local move explanations, troubleshooting and five guided 25-move practice scrambles. It works in both the standalone guide and the generated unified page.

The JavaScript testing gap noted above is now covered for the new 3x3 beginner flow:

```powershell
node --test _build/test_guide3_state.cjs
node --test _build/test_guide3_browser.cjs
```

Browser tests require Playwright and Microsoft Edge. If Playwright is installed outside the repository, set `CUBE_PLAYWRIGHT` to its module directory. Optional `CUBE_SCREENSHOTS` specifies a screenshot output directory. The Python discovery command also runs `_build/test_guide3_mobile.py` and `_build/test_guide3_solves.py`.

See [the implementation and verification record](docs/plans/2026-09-09-3x3-beginner-mobile.md) for scope, commands and remaining physical-user testing.

## 2x2 beginner mobile guide

The 2x2 standalone source now uses the same step-by-step layout: white layer, yellow face and side permutation. The yellow face uses complete `R' D' R D` cycles; Sune remains an optional collapsed note. Practice starts with the user's ten-move MIX and includes four longer sequences, with counters based on the selected sequence's actual length.

```powershell
node --test _build/test_guide2_state.cjs _build/test_guide3_state.cjs
node --test _build/test_guide2_browser.cjs _build/test_guide3_browser.cjs
```

The browser prerequisites are the same as above. Python discovery includes the 2x2 content, case-diagram, all-648-last-layer-state and complete-solve checks. See [the 2x2 implementation record](docs/plans/2026-09-10-2x2-beginner-mobile.md).
