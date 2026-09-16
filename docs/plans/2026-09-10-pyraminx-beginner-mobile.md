# Pyraminx beginner guide with the existing 3x3 layout

Status: implemented 2026-09-11 (Pyraminx beginner block, simulator and tests; see the commit "Add mobile-first beginner guides for 2x2, 3x3, Pyraminx with simulator tests").

## Objective and scope

Make every beginner decision explicit: what to inspect, how to hold the puzzle, which move sequence applies, what must remain solved, and what to do next. Match the current 3x3 beginner layout and interactions, not its cube-specific solving method. Preserve 2x2, 3x3, and the Pyraminx Pro content.

The deliverable will remain `pyraminx/rubiks-pyraminx-guide.html`, usable independently without external runtime dependencies. Generate `cube-solving.html` through `_build/assemble.py`; do not edit the generated output manually. This document is a handoff plan, not evidence of completed algorithm verification.

## Findings from the current files

- The standalone Pyraminx beginner block is not the block shown in the unified guide. `_build/assemble.py` substitutes `_build/py-beginner.html` after extracting the original source.
- The substituted text uses a color-majority rule to identify face colors. That is not a dependable reference on a scrambled puzzle and will not be retained as an instruction.
- First-layer insertion describes a side turn and trial-and-error reversal without a complete setup/insertion/restoration sequence. Its effect on previously solved pieces must be verified before reuse.
- Last-edge recognition does not consistently separate the identity of an edge from its orientation.
- The cycle diagram uses the bottom edge of a front-face triangle as a stand-in for the rear upper edge. Replace this representation with an explicitly labeled top view.
- Recovery text offers alternatives without identifying the current state. Each recovery must end at a specific inspection checkpoint.

## Shared presentation contract

Reuse the 3x3 typography, content width, spacing, card styles, button dimensions, collapsed troubleshooting, move-help dialog, and fixed Previous / Steps / Next navigation. Adapt selectors to `.guidepy`, `gpy-*`, and `data-gpy-*` to avoid interference with the existing guides.

Five pages:

1. Introduction and piece recognition.
2. Axial pieces and tips.
3. Green first layer.
4. Remaining three edges.
5. Guided scramble practice.

Every solving page must contain, in order:

1. Goal.
2. Holding position with a labeled diagram.
3. Exactly which pieces to inspect and which to ignore.
4. Case conditions and the matching action.
5. Observable success criteria.
6. Recovery for a mismatching result.
7. The next checkpoint or page.

Keep the main route short; put exceptional cases in clearly titled expandable panels. Essential holding instructions must remain visible. Never require a beginner to infer an algorithm from a formula name.

## Page content specifications

### Introduction

Explain G (tips), S (axial pieces below tips), and M (two-color edges) with actual piece positions, not color alone. Show front, rear, left, right, and upper vertex. Contrast turning the entire puzzle with turning one vertex. Explain uppercase large turns versus lowercase tip turns, the apostrophe, and the viewpoint from which a turn is clockwise. Pyraminx turns must not inherit the cube runtime's 90-degree explanation.

Describe one continuous solution: establish the reference faces, solve the green layer, solve the remaining edges. Do not restart the method for each color.

### Step 1: establish reference faces

Use piece identity rather than a majority of visible stickers. The intended reference is the axial piece without green at the upper vertex, leaving the green face underneath. Explain how to inspect all three stickers of that piece without confusing it with a tip or edge.

Align the other three axial pieces so their green stickers face the same bottom face. Show the resulting reference stickers and explain how side colors follow from them. Align tips with their adjacent axial pieces. If the upper axial piece is aligned here, explicitly explain that later U setup turns can move it again and that it will be realigned before final-edge recognition.

Acceptance: the learner can identify the bottom face and reference side colors without using unsolved edges. Validate this holding convention against the simulator before finalizing diagrams.

### Step 2: insert three green edges

Explain a destination using both colors: a green-red edge belongs between the green bottom and red side, with both stickers matching their reference faces. A green bottom alone is not sufficient evidence of a solved first layer.

For each target edge, cover:

- Already correct: leave it in place and select another.
- In the upper group: bring the target destination to the front by rotating the whole puzzle while preserving green underneath; use U setup turns to obtain one of the two illustrated insertion cases.
- In a bottom slot but incorrect or flipped: use a verified extraction sequence, then return to the upper-edge inspection.

Each left/right insertion card must state the exact source position, direction of the green sticker, destination, full move sequence, and final check. Determine the sequences from the verified move model; do not copy the current single-turn instruction or paste an algorithm written for an upside-down holding convention.

Show before and after stickers. Verify that completed insertion sequences restore reference axial pieces and preserve previously solved bottom edges. Explicitly distinguish temporary movement during a sequence from the final restored state.

Acceptance: all three bottom edges match both adjacent faces. Explain when the whole puzzle may be rotated around its vertical axis and when its front must remain fixed for an entire algorithm.

### Step 3: solve the upper three edges

First realign the upper axial piece to the established side references. Only then judge edge positions. Name the three positions consistently: front-left, front-right, and rear. Use a true top-view diagram with the viewer/front marked.

Teach two separate questions:

1. Do these two colors belong between these two faces, regardless of which sticker faces which side?
2. If the edge belongs here, do its individual stickers face the correct colors?

Decision route:

- All edges match: finish.
- Edge identities are in the wrong slots: select the verified cycle direction using a named edge and its destination; execute the full sequence, then inspect identities again.
- Edge identities are correct but two edges are flipped: hold the two affected edges at the explicitly verified positions, execute the flip sequence, and check all faces.
- The observed state does not match a legal case under the step prerequisites: recheck upper axial alignment, both colors of every edge, and the completed bottom layer. Do not guess another algorithm.

Verify both existing cycle algorithms and the flip algorithm, including their required grip, edge mapping, orientation changes, and preservation of the bottom layer. Keep their familiar sequences only where verified. Do not promise a fixed algorithm count before this audit.

For a wrong cycle direction, specify the actual resulting state and exact recovery after simulation. Avoid the current unqualified instruction to either repeat the same sequence or use the other one. A cycle followed by a flip case is a normal branch if verified, not automatically an execution error.

### Practice

Provide five deterministic, verified practice sequences with actual-length move counters, previous/next move controls, and independent saved progress. Include tip notation in the help where used. State the starting grip and that a practice scramble starts from a solved puzzle. Do not describe these as official random-state competition scrambles.

## Implementation sequence and tests

### 1. Preserve references

Existing archive copies are already available:

- `archive/2026-09-10-rubiks-pyraminx-guide.html`
- `archive/2026-09-10-before-pyraminx-cube-solving.html`
- `archive/2026-09-10-py-beginner.html`
- `archive/2026-09-10-before-pyraminx-assemble.py`

Do not overwrite these snapshots or delete the legacy fragment. No commit, push, or deployment is included.

### 2. Verify the mechanics before authoring algorithms

Add `_build/test_pyraminx_sim.py` before `_build/pyraminx_sim.py`. Observe the expected missing-module failure, then implement the smallest geometry-derived model needed by the tests. Do not reuse the 3x3 model as if Pyraminx had the same mechanics.

Tests: move followed by inverse; three identical turns restore state; uppercase versus lowercase movement; piece and sticker inventory; independently checked clockwise direction; insertion and extraction cases; preservation of solved pieces; cycles and flips. Enumerate all legal last-three-edge states with the first layer and axial pieces aligned. Solve every authored practice scramble and seeded additional scrambles using the taught route, not a general solver that bypasses the instructions.

Record any algorithm correction and its concrete counterexample before updating the beginner text. If the same problem affects Pro, report it separately rather than silently expanding the edit scope.

### 3. Add content and state regression tests

Create `_build/test_guidepy_content.py` and `_build/test_guidepy_state.cjs` before implementing their required HTML/runtime behavior. Check the five pages, explicit holding/checkpoint content, notation help, valid saved-state bounds, variable scramble lengths, and isolated storage. Observe expected failures, then implement the source changes.

Preserve the Pyraminx Pro block. Reuse and namespace the 3x3 presentation and the existing five-page 2x2 interaction pattern. Do not import cube-specific move descriptions, piece counts, or solving terminology into Pyraminx.

### 4. Make the standalone file authoritative

Add a failing test that compares the standalone beginner block with the unified block after the assembler's ID prefixing. Update `_build/assemble.py` so Pyraminx no longer substitutes `_build/py-beginner.html`. Retain that file as inactive historical content, with its status documented in README.

Generate `cube-solving.html`. Narrow prior tests that deliberately protected the entire old Pyraminx panel so they protect its Pro block instead. Add comparisons protecting the entire current 2x2 and 3x3 panels against the pre-Pyraminx archive.

### 5. Browser and visual acceptance

Add `_build/test_guidepy_browser.cjs`. Test standalone and unified modes at 320, 360, 390, 430, and 1440 pixels: all five pages, expanded cases, no horizontal overflow, visible bottom navigation, and touch targets at least 44 pixels high. Check move help and restored focus, retained scroll position, page links, saved progress, malformed storage, practice boundaries, and isolation when switching puzzle or Pro mode.

Compare shared computed styles with 3x3. Inspect screenshots of both insertion cases and final-edge diagrams; passing DOM checks alone does not establish diagram correctness. Keep a complete physical-puzzle beginner walkthrough as an explicitly separate usability check if it cannot be performed here.

### 6. Final verification and handoff

```powershell
python _build/assemble.py
python -m unittest discover -s _build -p "test_*.py"
node --test _build/test_guide2_state.cjs _build/test_guide3_state.cjs _build/test_guidepy_state.cjs
$env:CUBE_PLAYWRIGHT = 'C:\Users\Egils.Varna\AppData\Local\Temp\cube-guide3-browser-tests\node_modules\playwright'
node --test _build/test_guide2_browser.cjs _build/test_guide3_browser.cjs _build/test_guidepy_browser.cjs
git diff --check
```

The new test paths above are planned files, not currently completed tests. Report actual results, any remaining physical usability checks, changed files, and confirmed preservation of the other guides. Update this plan's status only after verification.

## Technical references and limitations

- [Jaap Scherphuis: Pyraminx mechanics and solution](https://www.jaapsch.net/puzzles/pyraminx.htm): independent reference for piece types, legal-state constraints, reference-color selection, and staged edge solving. Its written solution uses a downward vertex and a top solved face; its formulas require a verified holding conversion before use here.
- [WCA notation regulations](https://www.worldcubeassociation.org/regulations/#12e): normative reference to check when implementing Pyraminx move help.

The current algorithm strings are audit inputs, not certified outputs. Final insertion formulas, cycle direction labels, flip grip, and sticker diagrams remain verification gates for implementation.
