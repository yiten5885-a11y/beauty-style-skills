---
name: facial-style-preview
description: Create identity-preserving, non-medical facial styling previews and deterministic 4:3 comparison reports from a user-authorized portrait. Use for eyebrow grooming, makeup, optical contouring, lip styling, skin-finish simulations, or a six-region facial styling comparison; do not use for attractiveness scoring, skin or health diagnosis, cosmetic-procedure recommendations, or predictions of treatment outcomes.
---

# Facial Style Preview

Turn a portrait and the user's stated style goal into a clearly labeled visual simulation. Preserve the person's identity and the factual status of the input: the source image is an input photo, the edited image is a simulation, and neither is evidence of a medical result.

## Core contract

- Deliver one 2400 x 1800 PNG report unless the user requests another 4:3 size.
- Cover exactly six regions: `brow`, `eyes`, `nose`, `contour`, `lips`, and `skin`.
- Use only non-invasive styling or optical effects: grooming, cosmetics, color, highlight, shadow, finish, and other reversible presentation choices.
- Keep the input photo unchanged. Never create a false "before" image or make it less flattering to exaggerate a difference.
- Label the edited portrait `造型模拟` or an equally clear simulation label.
- Do not infer age, gender identity, ethnicity, health, personality, or other sensitive traits from the portrait. Follow the user's stated style language without turning it into a judgment about who they are.
- Do not rate attractiveness, identify "defects," or present one face as objectively better. Describe what is visible, the user's goal, and the styling change.

## Required inputs

Obtain or confirm:

1. A clear portrait the user owns or is authorized to use. A near-frontal image is required for a balanced six-region comparison.
2. The user's chosen style goal, such as natural, editorial, polished, soft, defined, minimal, or a supplied reference.
3. Any explicit keep-unchanged requirements. Identity, apparent age, facial geometry, expression, hair, clothing, background, framing, and lighting remain unchanged by default.
4. Whether temporary makeup coverage or color cosmetics are wanted. Preserve moles, scars, freckles, and other identifying marks by default.

Do not infer consent from a file's presence. If authorization is unclear or the image appears to be of a third party, ask for confirmation before editing.

If the portrait is missing, unreadable, heavily filtered, strongly angled, occluded, or too small for the requested comparison, request a better image. A text plan may be supplied when requested, but must not be described as a completed visual report.

## Workflow

### 1. Lock scope before editing

Translate the request into a short brief containing the style goal, requested changes, keep-unchanged list, and uncertainty caused by the image. Separate user-supplied facts from visible observations.

If the request includes injections, surgery, laser or device treatment, diagnosis, candidacy, dosage, treatment ranking, recovery, contraindications, or outcome prediction, do not convert it into a visual treatment plan. Read [references/safety-and-privacy.md](references/safety-and-privacy.md) and either narrow the task to non-medical styling or direct the user to an appropriately licensed professional.

### 2. Plan all six regions

Create a UTF-8 JSON manifest that follows [references/report-contract.md](references/report-contract.md). Each region must use one mode:

- `unchanged`: deliberately keep the area as shown.
- `styling`: apply a reversible grooming or cosmetic choice.
- `simulated-visual-effect`: use color, highlight, shadow, or finish without changing anatomy.
- `not-assessable`: the image does not support a reliable observation.

For `nose` and `contour`, use only optical makeup or presentation effects. Do not warp facial geometry, create a new eyelid fold, resize eyes, narrow the nose, sharpen the jaw, change lip volume, or simulate a surgical or injectable result.

Validate the manifest before image editing:

```bash
python3 scripts/validate_manifest.py manifest.json --json-out manifest-qa.json
```

The validation receipt intentionally excludes the user's text.

### 3. Produce the edited portrait

Use an image-editing tool that can actually reference the input portrait. Read [references/image-editing.md](references/image-editing.md) before composing the edit request.

Generate only the clean edited portrait layer at this stage. Do not ask the image model to typeset the final report. Preserve framing, camera angle, expression, face geometry, hair, clothes, background, and lighting unless the user explicitly requests an in-scope change.

When the tool cannot reliably preserve identity or localize the requested changes, stop after the failed attempt and report the limitation. Do not hide identity drift inside the final layout.

### 4. Compare before composing

Inspect the input and edited portraits side by side at full useful resolution. Reject and regenerate when any of these appear:

- identity, apparent age, ethnicity, face geometry, expression, hairstyle, clothing, background, framing, or lighting drift;
- unintended edits outside the requested regions;
- erased identifying marks, plastic skin, invented texture, or distorted eyes, teeth, ears, or hairline;
- a change described in the manifest that is not visible, or a visible change absent from the manifest.

Do not call pixel-level identity preservation guaranteed. Record any remaining uncertainty in the manifest.

### 5. Compose deterministic text and layout

Use the packaged composer so Chinese labels remain readable and exact:

```bash
python3 scripts/compose_report.py \
  --before input.png \
  --after edited.png \
  --manifest manifest.json \
  --output facial-style-preview.png \
  --qa-report report-qa.json
```

If automatic font discovery fails or lacks required glyphs, pass `--font` and `--font-bold` with a CJK-capable TrueType/OpenType font. Do not replace Chinese with image-model text.

The composer refuses non-4:3 canvases, incomplete six-region manifests, disallowed medical or diagnostic wording, output overwrite without `--overwrite`, and unreadable text overflow. It writes a content-free QA receipt and strips inherited image metadata from the report.

### 6. Inspect the final PNG

Open the report at full resolution and at a reduced preview size. Confirm:

- the two portraits are recognizable as the same person and the left image is the untouched input;
- the simulation label is visible;
- all six region cards are present exactly once and match the visible edit;
- text is readable, not clipped, and not contradicted by the image;
- the report includes the user's goal, keep-unchanged items, uncertainty, and the fixed non-medical notice;
- no private filename, path, EXIF data, prompt, model identifier, or generated personal profile appears.

If any gate fails, redo only the failed layer when possible. A structurally valid Skill or PNG is not proof that the identity-preserving edit succeeded.

## Privacy and delivery

- Keep portraits and generated face images out of the Skill package and source-control repositories.
- Do not persist biometric templates, face embeddings, inferred profiles, names, or identity fields in manifests or QA logs.
- Use private working files, strip nonessential metadata, and remove temporary portrait copies after the user receives the requested deliverables when the environment and task allow it.
- Report these states separately: package validated, Skill installed/discovered, image edit completed, final report visually checked, and any external publication. Never infer one state from another.

## Supporting resources

- [references/report-contract.md](references/report-contract.md): read when creating or reviewing a manifest or report.
- [references/image-editing.md](references/image-editing.md): read before generating or editing a portrait.
- [references/safety-and-privacy.md](references/safety-and-privacy.md): read for medical requests, sensitive inferences, consent, or privacy handling.
