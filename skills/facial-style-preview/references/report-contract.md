# Report contract

## Output

Default deliverable: one 2400 x 1800 PNG in a 4:3 landscape canvas.

The report contains:

- `输入照片` on the left and `造型模拟` beside it;
- six numbered region cards on the right;
- the user's stated style goal, a keep-unchanged list, and uncertainty items below;
- a fixed notice that the right image is a non-medical visual simulation rather than a diagnosis, treatment plan, or outcome promise.

The image model produces only the edited portrait layer. `scripts/compose_report.py` owns all final text and report layout.

## Manifest schema

Use UTF-8 JSON. Keep user names, filenames, paths, contact details, and identity descriptions out of the manifest.

```json
{
  "schema_version": "1.0",
  "style_goal": "自然清爽的日常妆面，由用户明确选择",
  "regions": [
    {
      "id": "brow",
      "mode": "styling",
      "observation": "眉形在正面光线下可见，眉尾边界较柔和",
      "styling": "梳理眉流并用接近原眉色的产品轻补眉尾",
      "confidence": "medium"
    },
    {
      "id": "eyes",
      "mode": "styling",
      "observation": "正面照片可见眼周与睫毛线，细节受分辨率限制",
      "styling": "使用低对比度内眼线与自然睫毛强调，不改变眼形",
      "confidence": "medium"
    },
    {
      "id": "nose",
      "mode": "simulated-visual-effect",
      "observation": "鼻部正面受单一光线影响，侧面结构无法确认",
      "styling": "仅用低饱和阴影和高光演示光影层次，不改变结构",
      "confidence": "low"
    },
    {
      "id": "contour",
      "mode": "simulated-visual-effect",
      "observation": "正面轮廓可见，侧面与动态表情信息缺失",
      "styling": "仅用腮红与柔和阴影演示视觉层次，不收窄脸型",
      "confidence": "low"
    },
    {
      "id": "lips",
      "mode": "styling",
      "observation": "自然表情下唇色与边界可见",
      "styling": "使用低饱和润色产品并保持原有唇形和体积",
      "confidence": "medium"
    },
    {
      "id": "skin",
      "mode": "styling",
      "observation": "照片可见表面颜色和纹理，但不支持皮肤判断",
      "styling": "使用轻薄底妆与局部遮瑕模拟均匀妆效，保留纹理",
      "confidence": "low"
    }
  ],
  "preserved": [
    "身份与面部几何",
    "年龄感与表情",
    "发型服装背景和光线",
    "可辨识痣斑与皮肤纹理"
  ],
  "uncertainties": [
    "单张正面照片不能确认侧面结构",
    "妆面颜色会受显示器与原图白平衡影响"
  ]
}
```

## Required fields and limits

| Field | Rule |
|---|---|
| `schema_version` | exactly `1.0` |
| `style_goal` | 1-80 characters; describe the user's selected direction, not an objective judgment |
| `regions` | exactly six objects, one for each required ID |
| `regions[].id` | `brow`, `eyes`, `nose`, `contour`, `lips`, or `skin` |
| `regions[].mode` | `unchanged`, `styling`, `simulated-visual-effect`, or `not-assessable` |
| `regions[].observation` | 1-64 characters; visible information plus limits, without diagnosis |
| `regions[].styling` | 1-72 characters; reversible styling or the reason no change is shown |
| `regions[].confidence` | `high`, `medium`, `low`, or `unknown` |
| `preserved` | 2-6 items, each 1-42 characters |
| `uncertainties` | 1-4 items, each 1-56 characters |

The validator rejects control characters, treatment or procedure language, diagnosis or health claims, attractiveness scoring, duplicate regions, missing regions, and unknown modes or confidence values. This is a narrow wording gate, not a complete medical-safety classifier; the agent must still review meaning.

## Region semantics

1. `brow` / 眉部: eyebrow grooming, brow color, brow styling. Do not infer personality from brow shape.
2. `eyes` / 眼部: eye makeup and lash styling. Do not create a new eyelid fold, enlarge the eyes, or diagnose fatigue or disease.
3. `nose` / 鼻部视觉: cosmetic highlight and shadow only. Do not change bridge, tip, nostril, or facial geometry.
4. `contour` / 轮廓视觉: blush, highlight, and shadow only. Do not narrow the face, create a V-line, or reshape jaw or chin.
5. `lips` / 唇口周: color, finish, and liner that retain the existing shape and volume.
6. `skin` / 肤质呈现: reversible cosmetic finish and color correction while preserving texture and identifying marks; never diagnose a condition.

## Visual acceptance

- `输入照片` must contain the actual supplied image rather than a regenerated substitute.
- `造型模拟` must remain recognizable as the same person without structural facial changes.
- The image pair must use equivalent crop, scale, angle, expression, lighting, and background.
- Every user-facing claim must be supported by the image or explicitly marked uncertain.
- Text remains legible when the 2400 x 1800 report is displayed around 1200 x 900.
