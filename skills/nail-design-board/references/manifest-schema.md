# 设计清单契约

清单是十指设计、生成素材和最终排版之间的内容真源。不要在清单中保存原始照片路径、姓名或可复原的手部身份描述。

## 顶层字段

```json
{
  "version": "1.0",
  "locale": "zh-CN",
  "title": "AI美甲灵感方案",
  "theme": "月下银桂",
  "source": {
    "kind": "text_theme",
    "label": "月下银桂",
    "summary": "从月光、银杏叶和夜雾中提取冷暖对比与轻盈层次。"
  },
  "palette": [
    {"role": "primary", "name": "夜雾蓝", "hex": "#34445A"},
    {"role": "primary", "name": "月光银", "hex": "#C8CDD4"},
    {"role": "primary", "name": "雾白", "hex": "#EEEAE2"},
    {"role": "secondary", "name": "桂叶金", "hex": "#B69A58"},
    {"role": "secondary", "name": "浅烟灰", "hex": "#A7A9AC"},
    {"role": "accent", "name": "墨蓝", "hex": "#172235"}
  ],
  "keywords": ["清冷", "克制", "轻盈", "夜色"],
  "motifs": ["银杏叶", "月弧", "细金线", "雾化渐变"],
  "finishes": ["微珠光", "细金线", "半透明晕染"],
  "nails": [
    {
      "id": "L1",
      "finger": "左手拇指",
      "design_name": "月弧主视觉",
      "base_color": "夜雾蓝",
      "motif": "月弧",
      "finish": "微珠光",
      "description": "深蓝底配偏心银色月弧，作为左手主视觉。"
    }
  ],
  "summary": "以雾蓝和月光银建立夜色基调，用桂叶金控制温度与节奏。",
  "recommended_shapes": ["短椭圆甲", "方圆甲"],
  "scenes": ["通勤", "晚宴", "秋冬"],
  "preview": {
    "mode": "generic_adult_hand",
    "simulation_label": "AI 模拟上手图"
  },
  "feasibility_note": "材料、价格、时长与施工可行性请由美甲师结合实物确认。",
  "final_note": "从月夜意象提取色彩和符号，转译为可讨论的十指系列。"
}
```

`nails` 示例只展示一枚，实际清单必须写满十枚。

## 不变量

- `source.kind` 只能是 `text_theme` 或 `inspiration_image`。
- `palette` 正好六项：三个 `primary`、两个 `secondary`、一个 `accent`；色值为六位十六进制。
- `keywords` 和 `motifs` 各四至六项；`finishes` 二至六项。
- `nails` 正好十项，ID 集合必须严格等于 `L1`–`L5` 与 `R1`–`R5`。
- ID 与中文指位固定映射：`L1/R1` 拇指、`L2/R2` 食指、`L3/R3` 中指、`L4/R4` 无名指、`L5/R5` 小指。
- 每枚包含设计名、基色、元素、工艺和一句短说明；至少有四个不同的设计名，防止十指机械复制。
- `recommended_shapes` 一至两项；`scenes` 一至五项。
- `preview.mode` 只能是 `user_hand` 或 `generic_adult_hand`；标签必须明确包含“模拟”。

长度上限由校验器执行，目的是保证 2400x1800 排版可读。需要更长的制作说明时，另交付美甲师文字简报，不要压进单张提案图。
