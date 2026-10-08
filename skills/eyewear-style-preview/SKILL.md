---
name: eyewear-style-preview
description: Create an identity-preserving, non-medical eyewear style preview from an authorized portrait, with frame-shape comparisons, deterministic Chinese layout, and store-ready style notes. Use for glasses try-on concepts or frame selection; do not use for prescriptions, exact measurements, or guaranteed fit.
---

# Eyewear Style Preview

Turn an authorized portrait and the user's stated use case into a visual frame comparison that can support a conversation with an optician. The image is a styling simulation, not a measurement or a finished pair of glasses.

## Inputs and limits

- Require a clear near-frontal portrait and explicit authorization to use it.
- Collect current glasses status, intended use, preferred shapes, bridge comfort concerns, and any user-supplied measurements. Treat measurements from a user or optician as facts; never infer millimetres, pupillary distance, prescription, bridge fit, or lens power from one photograph.
- Keep face, skin tone, hair, clothing, lighting, expression, and background stable. If the source already contains glasses, label it as `原图已戴镜`; do not invent an unglassed original.

## Standard output

Deliver one 2400x1800 PNG report plus a short structured brief. The report contains the untouched source, one primary frame, four recommended frame options, two or three options to try in person, three style-comparison directions, and frame-shape, colour, and material notes. Mark edited frames as `AI 模拟试戴`.

## Workflow

1. Record the brief, source role (`person_reference`), visible occlusion, and uncertainty. Separate visible observations, user preferences, and optician-supplied facts.
2. Choose comparison dimensions before generation: silhouette, brow-line, lens height, rim weight, bridge style, colour, and intended context. Use user preferences to override defaults.
3. Create a manifest with one entry per proposed frame. Keep labels short and move detailed explanations into the deterministic layout layer.
4. Generate clean, text-free frame edits using a tool that actually accepts the portrait reference. Change eyewear only. Reject identity drift, changed lighting, altered eyes or facial geometry, invented uncovered eyes, and malformed temples or lenses.
5. Compose Chinese text and arrows with a deterministic renderer. Do not ask the image model to typeset the final report.
6. Inspect the full-size and reduced report. Confirm frame labels match the visible frames, the original remains unchanged, the simulation label is visible, and no personal path or metadata is exposed.

## Failure behaviour

If the portrait is missing, unreadable, already occluded, unauthorized, or the image tool cannot preserve the reference, stop at a brief and explain the missing gate. Do not return a lookalike or call a prompt a completed try-on.

## Boundaries

- This is visual style exploration, not an optometry, prescription, pupillary-distance, or comfort assessment.
- Do not claim exact size, fit, UV protection, lens material, price, durability, or current availability without a supplied specification.
- Real comfort, nose-pad contact, temple pressure, and prescription suitability require an in-person fitting or verified product data.
- Keep portraits and generated personal images outside Git and public repositories.
