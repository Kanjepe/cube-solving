# 3x3 beginner mobile guide

Status: implemented and verified on 2026-09-09.

## Agreed scope

- Improve only the 3x3 beginner experience, in both the standalone and unified HTML guides.
- Preserve the 2x2, Pyraminx and 3x3 Pro content and behavior. A concise Pro reference is a later phase.
- Show one learning step at a time, with persistent Previous / Steps / Next navigation and a saved current step.
- Keep move explanations and troubleshooting beside the action, without losing the reading position.
- Use a short, consistent sequence: goal, grip, case, action, result check. Critical warnings remain visible.
- Make the layout readable and usable on 320–430px phone screens, with large touch targets and no horizontal page scrolling.
- Add five distinct 25-move practice scrambles, with a move-by-move aid. They are practice sequences, not ranked difficulty levels or official random-state competition scrambles.
- Keep the existing solving method. Verify changed holding instructions and decision branches against the cube simulator.

## Content decisions

1. White cross: separate daisy construction from moving petals to the white face; explain misplaced/flipped petals and protect completed petals.
2. White corners: distinguish cube rotation from layer turns; show the target slot and check only after a complete algorithm.
3. Middle layer: separate right, left and trapped-edge cases, including precise grip for extraction.
4. Yellow cross: ignore corner stickers, identify dot/L/line/cross, reorient and reassess after every complete algorithm.
5. Yellow edges: inspect all four U alignments before selecting adjacent/opposite/all-correct cases; verify the decision rule.
6. Corner positions: distinguish piece position from orientation; explicitly skip when all corners are already in place.
7. Corner orientation: finish every four-move cycle, keep the same front face, turn only U between corners, and do not use temporary lower-layer appearance as a stop condition.

Remove the approved beginner assumptions about prior 2x2 knowledge and replace the advice to scramble again when confused with local diagnostic checks. Preserve a dated copy of the original 3x3 guide.

## Implementation and checks

1. Add failing tests for navigation state, move guidance, scramble validity, required content and isolation of unrelated puzzle/Pro content.
2. Implement the scoped beginner HTML/CSS/JS in the standalone 3x3 source; the existing assembler carries it into the unified page.
3. Replace the assembler's obsolete step-7 warning injection with the warning authored directly in the beginner source.
4. Run simulator checks for cases and scrambles, existing regressions, and the build.
5. Exercise navigation, help, persistence, scramble stepping and mobile layout in a browser test where available.
6. Record results and remaining limitations here. A real first-time learner still needs to try a complete solve.

No commit, push or deployment is authorized by this implementation approval.

## Verification results

- Python simulator and guide checks: 50 tests passed.
- Browser checks: 6 tests passed for standalone and unified pages.
- Tested 320, 360, 390 and 430px widths: no page overflow; bottom navigation remains visible.
- Tested local move help, step navigation, saved step and completion state, five scramble sequences, and isolation of 2x2, Pyraminx and 3x3 Pro.
- Archived the previous standalone 3x3 source at `archive/2026-09-09-rubiks-3x3-guide.html` before the rewrite.

## Completion audit on 2026-09-10

The existing implementation was checked against this plan and completed in both HTML variants. The seven learning steps, introduction, local troubleshooting, move-help dialog, persistent navigation/progress and five guided scrambles were already implemented; no duplicate implementation was needed.

- Preserved the pre-fix standalone page at `archive/2026-09-10-rubiks-3x3-guide.html`.
- Fixed damaged Latvian labels and captions in the three grip diagrams. A new regression test failed on the damaged source before the correction and now passes.
- Made assembly explicitly write LF line endings on Windows, following a failing output-format regression test.
- Verified that the generated beginner block matches its standalone source after ID prefixing.
- Verified that the 2x2 and Pyraminx panels match the committed version, and that the 3x3 Pro block matches the archived source.
- Python: 54 passing tests, including complete solves for all five practice scrambles and 30 additional scrambles, all 24 yellow-edge permutations, diagrams, assembly and content checks.
- Node state tests: 5 passing tests.
- Edge browser tests: 10 passing tests, including direct step links, navigation, help without scroll-position loss, persistence, all five practice sequences, invalid storage recovery and isolation of other modes.
- Both standalone and unified layouts tested at 320, 360, 390 and 430px, on all nine pages with troubleshooting expanded: no horizontal overflow, persistent navigation visible, navigation targets at least 44px high.
- Visually reviewed unified mobile screenshots of the introduction, final step and scramble page; corrected Latvian captions are legible.
- Rebuilt `cube-solving.html` and passed `git diff --check`.

Commands:

```powershell
python _build/assemble.py
python -m unittest discover -s _build -p "test_*.py"
node --test _build/test_guide3_state.cjs
# Point to an existing Playwright installation if it is not locally installed.
$env:CUBE_PLAYWRIGHT = 'C:\Users\Egils.Varna\AppData\Local\Temp\cube-guide3-browser-tests\node_modules\playwright'
node --test _build/test_guide3_browser.cjs
```

Browser verification used installed Microsoft Edge with mobile viewport emulation, not a physical phone. A first-time learner's complete physical solve remains a usability follow-up. No commit, push or deployment was performed.
