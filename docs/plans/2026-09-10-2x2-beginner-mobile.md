# 2x2 beginner guide with the 3x3 mobile layout

Status: implemented and verified on 2026-09-10.

## Approved scope and final decision

Update the existing `2x2/rubiks-2x2-guide.html`, keeping it independently usable and importable by the current assembler. Match the current 3x3 beginner layout and interactions. Preserve 2x2 Pro, 3x3 and Pyraminx.

The user approved a three-step beginner method with `R' D' R D` as the primary opposite-face orientation algorithm. Sune is only a collapsed explanatory note for readers who already know its case and grip; there is no Sune recognition tree in the main beginner path.

## Implementation

1. Preserve the previous 2x2 source in `archive/2026-09-10-rubiks-2x2-guide.html` and the pre-change unified build in `archive/2026-09-10-before-2x2-cube-solving.html`.
2. Add tests before the new source runtime and page structure. Observe missing-runtime, missing-page and missing-scramble failures.
3. Create five pages: introduction, white layer, yellow face, side permutation and scramble practice. Use the same scoped CSS as the 3x3 reference, adapted only for the 2x2 namespace and existing standalone reference sections.
4. Explain the first white anchor, three-color slot identification without centers, insertion, trapped corners and full-layer checks. Retain the user's `R U R' U'`. Require all three corner colors to match before stopping an insertion cycle.
5. Teach opposite-face orientation one corner at a time with `R' D' R D`: complete every four moves, keep the same front for the entire step, move only U between corners and expect the bottom to recover after all twists. Keep Sune in a closed optional note and warn against mixing it into an unfinished twist process.
6. Distinguish four upper side pairs, one pair and no pair. Use the existing T-perm with the matching pair on the left, or the user's diagonal algorithm `R U' R' U' F2 U' R U R' D R2`. Finish by aligning U against the current bottom layer. Derive the two case diagrams from the inverse algorithms; a regression test exposed and corrected the previous diagonal diagram's sticker colors.
7. Preserve the user's two other sequences as reference text with their unresolved usage clearly stated, not as executable beginner instructions. Direct corner-only simulation shows they do not implement the prescribed final-step behavior in its required holding position. The existing tests prohibiting them as active algorithms still pass.
8. Preserve `R2 U2` in a collapsed FINISH note with a precise conditional example: it undoes `U2 R2` from a solved cube, but scrambles an already solved cube. It is not appended to the beginner method automatically.
9. Use the user's exact ten-move MIX as the first practice sequence, followed by four distinct 25-move practice sequences. Drive counters, completion, back/next and saved cursors from each sequence's actual length.
10. Add independent 2x2 page/completion/practice storage, Previous / Steps / Next controls and in-place move help. Keep all UI code and styles in the standalone HTML. Update the old shared beginner summary to agree with the new method.
11. Rebuild `cube-solving.html` using the existing assembler. Adjust the previous 3x3 isolation test to allow the intended 2x2 beginner change while continuing to protect 2x2 Pro and Pyraminx; add a snapshot comparison protecting the entire pre-existing 3x3/Pyraminx output.

## Verification

- Python discovery: 64 tests passed.
- Node state tests: 8 tests passed (3 for 2x2 and 5 for 3x3).
- Edge browser integration: 18 tests passed (8 for 2x2 and 10 for 3x3).
- Enumerated all 648 legal last-layer states with the first layer solved. Each completes the new orientation and permutation path. Covered all final-step branches: 0, 1 and 4 side pairs.
- Solved all five authored practice sequences and 50 additional seeded random scrambles with the taught method. Only corner cubies are used for 2x2 checks, so invisible 3x3 centers and edges do not affect the results.
- Compared authored case-diagram sticker colors with inverse algorithm states.
- Tested both standalone and unified guides at 320, 360, 390, 430 and 1440px on all five pages, including expanded troubleshooting: no horizontal overflow, persistent navigation stays visible and its buttons are at least 44px tall.
- Browser checks cover default-collapsed Sune, move help without lost scroll position, saved progress, direct step links, each move of all five scrambles, end boundaries, invalid storage, mode isolation and equality of 2x2/3x3 computed button and heading styles.
- Reviewed mobile and desktop screenshots. Physical-phone testing and a complete solve by a first-time learner remain usability follow-ups, not claims made by automated browser emulation.
- The generated 2x2 block matches the standalone source after ID prefixing. 2x2 Pro and its existing renderer are preserved; the 3x3 and Pyraminx output after the 2x2 panel matches the pre-change snapshot.
- `git diff --check` passes. No commit, push or deployment was performed.

## Commands

```powershell
python _build/assemble.py
python -m unittest discover -s _build -p "test_*.py"
node --test _build/test_guide2_state.cjs _build/test_guide3_state.cjs
$env:CUBE_PLAYWRIGHT = 'C:\Users\Egils.Varna\AppData\Local\Temp\cube-guide3-browser-tests\node_modules\playwright'
node --test _build/test_guide2_browser.cjs _build/test_guide3_browser.cjs
```

Playwright was reused from the previous external test environment. No application dependencies were added. Set `CUBE_SCREENSHOTS` to a temporary directory to capture the 2x2 page screenshots at each tested width.
