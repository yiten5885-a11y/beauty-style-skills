# Identity-preserving image editing

## Build the edit request from the manifest

Use the input portrait as the sole person reference. Translate only region entries whose mode is `styling` or `simulated-visual-effect` into edit instructions. Entries marked `unchanged` or `not-assessable` become preservation constraints, not invented changes.

State the edit in this order:

1. Identify the task as an edit of the supplied portrait, not creation of a new person.
2. List the exact reversible changes requested by the manifest.
3. Lock identity, face geometry, apparent age, expression, camera angle, crop, lighting, background, hair, clothing, and identifying marks.
4. Prohibit geometry warping, surgical or injectable simulation, plastic skin, and added report text.
5. Request one clean portrait layer with the same aspect ratio and resolution as the input when supported.

Example structure:

```text
Edit the supplied portrait of the same person. Apply only these reversible styling changes:
- [brow styling from manifest]
- [eye styling from manifest]
- [nose optical makeup from manifest]
- [contour optical makeup from manifest]
- [lip styling from manifest]
- [skin finish from manifest]

Preserve the person's identity, facial geometry, apparent age, expression, pose,
camera angle, crop, lighting, background, hair, clothing, natural skin texture,
and identifying marks. Do not enlarge eyes, create an eyelid fold, reshape the
nose, jaw, chin, or lips, smooth the face into plastic skin, or simulate a
medical/cosmetic procedure. Produce one clean edited portrait with no labels,
arrows, panels, borders, or text.
```

Do not include every original-source style label by default. Terms such as "Korean," "clean beauty," masculine, feminine, or androgynous are optional user-selected directions, not diagnoses or universal ideals.

## Regeneration limits

Identity-preserving edits can drift. Use a bounded retry rather than silently accepting the best-looking result:

- First attempt: exact requested local styling changes.
- Second attempt, if needed: simplify or reduce the changes that caused drift.
- Third attempt only when a clear prompt correction is available.

Stop after three failed attempts or earlier when the tool cannot reference the portrait, cannot localize changes, or repeatedly changes identity or geometry. Report image-edit completion separately from report-layout completion.

## Comparison review

Compare input and edit at matched scale. Inspect:

- eye spacing and shape;
- nose width, bridge, tip, and nostrils;
- jaw, chin, cheek, and forehead geometry;
- lip outline and volume;
- ears, hairline, scars, moles, and freckles;
- apparent age, ethnicity, expression, and head pose;
- clothing, background, shadows, and white balance.

Lighting or color drift can falsely imply a styling improvement. Reject it unless the user explicitly requested a lighting demonstration and the report labels that change.
