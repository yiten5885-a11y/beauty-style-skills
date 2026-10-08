---
name: personal-outfit-studio
description: Create structured, identity-consistent outfit proposals from a theme, reference image, or authorized portrait across inspiration, personal makeover, and four-season series modes. Use for outfit boards and styling reports; do not infer gender identity, body measurements, climate suitability, or personal seasonal colour diagnosis.
---

# Personal Outfit Studio

Design outfits as a reusable visual proposal rather than a pasted prompt. The user chooses the mode, expression, scene, and constraints; a photograph does not authorize identity or body changes.

## Modes

- `inspiration`: a theme or reference image, with an optional person reference. Deliver one 2400x1800 4:3 board with distinct Hero, Work, and Date looks.
- `personal-makeover`: an authorized portrait or full-body photo, target style, scenes, and constraints. Deliver one 2400x1800 4:3 Before/After report and three extension looks. Before stays untouched; proportions change through clothes and styling only.
- `four-season`: a person or neutral model reference, style brief, and any real climate requirements. Deliver four independent 1800x2400 3:4 images, one per season, with the requested five or six extension looks. Never collapse the four outputs into one collage.

## Workflow

1. Confirm the mode, image roles (`person_reference`, `inspiration_reference`, or neither), language, scenes, budget or practicality constraints, and whether the user wants masculine, feminine, mixed, or self-described styling. Do not infer this from appearance.
2. Create one shared data structure for each Look: scene, complete outfit, item list, colour, material, accessories, and uncertainty. Keep season as weather/collection context, not as a diagnosis of a personal colour season.
3. Generate text-free visual assets with the correct reference role. For a personal mode, preserve identity, body proportions, face, skin, and camera character. For inspiration mode, do not call a reference-model person the user.
4. Compose labels and long Chinese copy deterministically. Every look must differ in scene and construction, not only in colour.
5. Check exact page count and ratio, identity consistency, model/reference role, clothing-to-copy match, readable text, and absence of personal image files from the package.

## Boundaries and failure

- Do not infer gender identity, height, weight, body measurements, income, profession, or attractiveness.
- Do not promise trend status, slimming, warmth, comfort, fabric composition, price, or availability without evidence.
- If a personal photo is missing, switch to a clearly labelled generic model only for `inspiration`; do not fabricate a personal Before.
- If image generation is unavailable or reference use is unverified, return an explicitly incomplete brief instead of calling a text plan a finished visual report.
