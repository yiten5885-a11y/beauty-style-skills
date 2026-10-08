---
name: intimate-loungewear-board
description: Create privacy-conscious innerwear or loungewear design proposals from a theme, palette, product type, and material intent, with consistent flat-lay, mannequin or fictional adult model, detail, and scene directions. Do not use for sexualized real-person editing, age ambiguity, product-performance claims, or production certification.
---

# Intimate Loungewear Board

Turn a product idea into a brand-style proposal. Select exactly one mode: `innerwear` or `loungewear`. Prefer a flat-lay, mannequin, or fictional clearly adult model. A real-person reference requires explicit authorization and an explicit adult confirmation before any try-on style visual is considered.

## Standard output

Deliver one 2400x1800 4:3 board containing a model/mannequin or flat-lay view, a matching product breakdown, detail notes, a colour/material board, and three context directions. Keep the product construction, palette, and silhouette consistent across all views.

## Workflow

1. Capture the brief: mode, product type, theme, palette, material intent, coverage, comfort language supplied by the user, target scene, and whether the visual is flat-lay, mannequin, or fictional adult model.
2. Treat `inspiration_reference` and `product_reference` as design sources, not as people to copy. Extract abstract colour, construction, texture, and mood; do not reproduce logos, watermarks, or a creator's complete composition.
3. Build a product manifest before generation. Separate design intention from verified specification. “蕾丝感”“缎面观感” are visual directions unless the user supplies real material data.
4. Generate clean visual assets without dense text, then use deterministic composition for Chinese labels. Reject mismatch between model view, flat-lay, and detail view.
5. Mark every generated presentation as `AI 视觉提案` or `设计模拟`; review the full image and thumbnail for accidental nudity, ambiguous age, malformed anatomy, inconsistent products, and unreadable text.

## Boundaries and failure

- Do not create sexualized edits of a real person, and do not proceed with a real-person model when age or authorization is unclear.
- Do not claim support, breathability, softness, safety, size fit, durability, fibre content, cost, or manufacturability without product specifications or physical review.
- Do not turn a lingerie brief into a loungewear brief by copying scene restrictions; choose the requested mode explicitly.
- If the image tool is unavailable, return a text design brief with an incomplete visual status, not a fake finished board.
