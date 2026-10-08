# Safety and privacy boundary

## Non-medical scope

This Skill supports reversible styling previews. It does not evaluate or recommend injections, fillers, neuromodulators, threads, lasers, peels, prescription products, surgery, implants, permanent makeup, or other invasive or regulated procedures. It does not determine candidacy, treatment areas, product, device, dosage, technique, timing, recovery, contraindications, cost, or expected outcome from a photograph.

A disclaimer cannot repair an unsafe workflow that already produced individualized treatment recommendations. When a user asks for medical or procedural advice:

1. Do not analyze the portrait for treatment suitability or rank interventions.
2. Offer to narrow the task to reversible grooming, cosmetics, color, light, or finish.
3. For medical questions, state that a photograph and a generative preview cannot replace an in-person assessment by an appropriately licensed professional.
4. If urgent symptoms or complications are described, do not continue the appearance workflow; direct the user to timely medical care or local emergency services as appropriate.

The U.S. FDA describes filler injection as a medical procedure and advises seeking a licensed, trained health-care provider. It also documents potentially serious complications. The NHS likewise states that cosmetic procedures carry risks and recommends consultation with a practitioner. These sources support the separation between a visual styling tool and clinical decision-making; they do not establish the licensing or regulatory rules of every jurisdiction.

Official references:

- FDA, Dermal Fillers (Soft Tissue Fillers): https://www.fda.gov/medical-devices/aesthetic-cosmetic-devices/dermal-fillers-soft-tissue-fillers
- NHS, Before you have a cosmetic procedure: https://www.nhs.uk/tests-and-treatments/cosmetic-procedures/advice/before-you-have-a-cosmetic-procedure/

## Appearance and sensitive inference

- Do not score beauty, symmetry, youthfulness, masculinity, femininity, race, ethnicity, or social desirability.
- Do not infer gender identity, age, nationality, disability, health, pregnancy, substance use, emotional state, personality, or socioeconomic status from the image.
- Do not call visible color or texture a disease. Use bounded language such as "the photo shows uneven illumination" or "detail is limited by resolution."
- Do not invent hidden facial structure from a single frontal view.
- When the user's chosen style has gendered or cultural language, attribute it to the user's preference and avoid treating it as the person's identity.

## Consent and third-party images

Proceed only when the user states or reasonably establishes that they own the image or are authorized to edit it. Do not create deceptive identity changes, impersonation assets, or a report presented as a professional medical opinion.

For a known minor, keep the task strictly non-medical and age-appropriate. Do not sexualize the presentation, recommend permanent procedures, or frame ordinary developmental features as defects.

## Data minimization

- Keep portraits out of the Skill folder, Git history, tests, examples, and shared repositories.
- Do not create face embeddings, biometric templates, or persistent appearance profiles.
- Do not place names, contact details, filenames, local paths, account identifiers, prompts, or model names in the manifest or QA receipt.
- Store working images with restrictive permissions when possible, strip EXIF and other nonessential metadata from delivery files, and delete temporary copies when the task and environment permit.
- A hash, validation pass, or successful render proves only that narrow gate; it does not prove consent, identity fidelity, medical validity, or user satisfaction.
