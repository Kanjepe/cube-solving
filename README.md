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

The script extracts the `<main>` content and step navigation from each standalone guide, prefixes element IDs to avoid collisions (`a2-`, `a3-`, `py-`), injects the kids-level fragments and shell, and writes the result to `cube-solving.html`.

The three standalone guides in `2x2/`, `3x3/`, and `pyraminx/` remain fully usable on their own.
