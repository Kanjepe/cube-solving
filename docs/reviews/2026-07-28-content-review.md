# Content review — all sections, beginner-comprehension focus (2026-07-28)

Three parallel review passes (one per puzzle) over the source guides and `_build/` fragments.
Algorithm claims for 2x2 and 3x3 were verified by move simulation in the review agents;
re-verify independently before changing any algorithm.

Severity: HIGH = beginner gets stuck or misled, MED = confusing, LOW = polish.

---

## A. Factual errors (beginner cannot succeed)

### 2x2 (`2x2/rubiks-2x2-guide.html`)
- **HIGH (L461-466, cheat L591-594):** Both step 3A "adjacent corner swap" algorithms
  (`L' U R' D2 R U' R' D2 R2`, `R' U R' D2 R U' R' D2 R2`) do NOT preserve the solved
  bottom layer — they scramble steps 1-2. Root cause: classic alg `R' F R' B2 R F' R' B2 R2`
  transcribed with F→U, B→D (wrong rotation). Fix: replace with the guide's own verified
  T-perm `R U R' U' R' F R2 U' R' U' R U R' F'`, hold the correct pair on the LEFT, final U to align.
- **HIGH (L436-438, cheat L589):** Step 2 placement rule "unoriented corner front-LEFT with
  yellow facing left" is unsatisfiable/never-terminating (verified over all 26 orientation
  states: 0/26 solved). Correct rule: unoriented corner front-RIGHT, any facing, ≤4 Sunes.
- **HIGH (L401-405):** First white corner has no "own place" on a centerless 2x2 — tell the
  beginner the first corner goes anywhere and becomes the reference.
- **MED (L474-476):** 3A recognition diagram shows a solved-looking top; real adjacent-swap
  state has only the back uniform (`data-b="bb" data-f="or" data-l="rg" data-r="og"`).
- **MED (L415-417):** Step 1 diagram puts white on the F face at the destination; white must
  face DOWN after insertion.

### 3x3 (`3x3/rubiks-3x3-guide.html`)
- **HIGH (L813-817):** 2-look PLL corners: text says hold "lukturi" (headlights) at the BACK;
  T-perm actually preserves the LEFT pair and swaps the RIGHT pair → hold headlights LEFT.
  Diagram arrows must show right-column swap.
- **MED (L821-823):** Ua-perm diagram shows left edge fixed; `M2 U M U2 M' U M2` keeps the
  BACK edge fixed (cycles UL→UF→UR→UL). Fix arrows + caption.
- **HIGH (L748, L780):** OLL 19/32 use the `S` slice move, never explained anywhere.
  Add to pro notation tip or replace with S-free algs.
- **LOW (L818-820):** Verify Y-perm diagonal arrows by simulation before trusting.

### Pyraminx (`pyraminx/rubiks-pyraminx-guide.html`, `_build/py-beginner.html`)
- **HIGH (py-beginner L102-108):** Step 3 diagnostics miss the combined case: after a correct
  3-cycle, 2 flipped edges often remain → beginner thinks they failed. Add "turpini ar B gadījumu".
- **HIGH (guide L269-294):** Clockwise reference viewpoint never defined. Add: judge CW/CCW
  looking straight AT the vertex being turned, from outside.
- **HIGH (guide L419,431,433,440,466,483,516):** Typo "salikc" → "saliec" (7x; L516 is in the
  shared Tips section seen by everyone).
- **MED (guide L272-286):** Notation diagrams for U/L/R highlight only the tip — visually
  identical to the small-turn (u/l/r) cell, though U-vs-u confusion is called "mistake #1".
  Highlight the full layer: U → 0,1,2,3; L → 4,5 (+1,6); R → 8,7 (+3,6).
- **MED (guide L255,257,436):** Standalone pyraminx file still has swapped stūri/malas marks
  and old V mark — fixed only via assemble.py injection in the unified page. Divergence if
  someone opens the standalone file directly.
- **MED (guide L292,518 vs py-beginner L39):** "2 stāvokļi" is wrong (3 states: identity + 2
  turns); contradicts py-beginner which correctly says 3.
- **MED (guide L478,503):** `L2'` in Oka table contradicts the page's own "Nav «2»!" rule
  (on Pyraminx L2 = L'; normalize to L).
- **MED (py-beginner L127-129):** 3-cycle diagram arrows pass through position 6 (the solved
  bottom edge); third cycling edge is actually on the back face. Add schematic disclaimer to
  caption or arrows 1↔3 only.

## B. Beginner flow (Pyraminx-class "no overall plan" gaps)

- **2x2 MED (L400 vs L436-438):** "nekad neapgriez kubu" vs steps that say "pagriez kubu tā,
  lai…" — never distinguishes allowed rotation (around vertical axis, white stays down)
  from forbidden flipping. Same in 3x3 (L387-388 vs L545+): add "starp algoritmiem kubu
  drīkst pagriezt ap vertikālo asi; aizliegums attiecas uz brīdi, kamēr izpildi algoritmu".
- **3x3 MED (L278-279):** Overall-plan sentence lives only in the hero (outside <main>,
  lost in unified page). Add plan paragraph to uzbuve card: 7 steps, once, white stays down.
- **3x3 MED (L514-529):** Step 5: after the alg, always turn U to align maximally, then
  re-evaluate. Cases 3/5 use inconsistent mental models.
- **2x2 MED (L468-483):** Step 3 never mentions the final U to align top with bottom.
- **Pyraminx MED (py-beginner L110-116):** Case A never says how to hold the pyramid (any
  face front, green down, direction is all that matters).
- **Pyraminx MED (py-beginner L111):** CW/CCW diagnosis needs one worked example.
- **Pyraminx MED (py-beginner L38):** "lielais grieziens — stūris + smailīte" omits that
  3 edges move too (contradicts notation warn).
- **Pyraminx MED:** Bridge sentence notation↔method grip: green face down = one vertex up,
  same grip; U top, L/R bottom.

## C. Pro accessibility (beginner → Pro bridge)

Common to all three: no "kad esi gatavs Pro" entry card with prerequisites, what changes
vs beginner method, and learning order. Add one intro card per pro section.

- **2x2 HIGH (L534-544, L612-616):** PBL tables have zero holding info — add "Kā turēt"
  column (verified positions: adj+adj → both correct pairs at BACK; T-perm → unsolved layer
  UP, headlights LEFT; Y-perm → unsolved layer UP, any angle; adj+diag → adjacent layer UP
  with its correct pair FRONT; diag+diag `R2 F2 R2` → any angle).
- **2x2 HIGH (L513-529):** OLL: 7 cases text-only; Sune vs Antisune and Pi vs H not
  distinguishable. Add 7 mini top-view diagrams with side stickers.
- **2x2 MED:** «Lukturi» never defined; "PLL" (L563) appears once, undefined — probably PBL.
- **3x3 HIGH (L723-734):** OCLL (2-look OLL corners) table has no diagrams and no holding
  instructions while edges (L715-722) got diagrams. Not executable.
- **3x3 MED (structural):** #uzbuve and #nota sit INSIDE .mode-beginner → invisible in Pro
  mode, though pro tip says "Notācija ir tā pati". Move outside the mode wrapper.
- **3x3 MED (L648-666):** Add "kad pāriet": beginner method ~2 min without notes; start with
  F2L + keep beginner last layer; explain that CFOP swaps the order (orient all, then permute).
- **3x3 MED (L658-661):** M direction (like L), x (like R), y (like U) not defined; needed
  by 2-look PLL.
- **Pyraminx MED (L451-452, 476-477, 501-502):** "Gadījums" column names the alg itself
  (circular); add state descriptions or diagrams.
- **Pyraminx MED (L412-424):** Add prerequisites + "«V» turi apakšā tāpat kā zaļo seju";
  intuitive L4E needs only ~2 new algorithms.
- **LOW (all):** Unexplained jargon at first use: inspekcija, look-ahead, sub-40s, slots,
  L4E expansion, top-first.

## D. Language / polish

- 2x2: "tavējā/tava versija" personalization (L277,390,583,641) → neutral wording;
  "ja kāda sāns" → "ja kāds sāns" (L458); stray `</p>` in tip (L563-564);
  "cuberis" → "risinātājs (speedcuber)" (L545).
- 3x3: "turi rādām" (L499), "nesakritīgiem" (L418), "Kā liek speedcuberi" (L645),
  "(uz sevis skatoties)" (L363).
- Pyraminx: "skaitās nepareizi" (py-beginner L68); "pašā beigās" → "pašās beigās" (L516).

---

## Suggested batches

1. **Critical fixes (A):** broken 2x2 algorithms + step-2 rule + first-corner note;
   3x3 T-perm/Ua-perm holding+arrows; Pyraminx combined case + CW viewpoint + salikc typos.
   Re-verify every algorithm change by simulation before editing.
2. **Beginner flow (B):** rotation-allowed clarification (2x2+3x3), 3x3 plan paragraph,
   final-U notes, Pyraminx case-A holding + CW example + big-turn wording.
3. **Pro bridge (C):** per-puzzle "kad pāriet uz Pro" intro cards, PBL/OCLL holding info,
   «lukturi» definition, uzbuve/nota visibility in Pro mode, jargon glosses.
   OLL/OCLL case diagrams are the largest sub-task.
4. **Polish (D):** language fixes.
