# Beauty Style Skills

![Beauty Style Skills cover](assets/cover.png)

把文字主题或授权照片转译为可沟通的个人造型视觉提案。仓库包含六个可独立调用的 Codex Skill；旧的 `hairstyle-upgrade-board` 目录作为兼容别名保留，不计作新的能力包：

- `facial-style-preview`：非医疗的六区域面部造型预览。
- `nail-design-board`：从主题或灵感图生成十指美甲清单、模拟上手图和横向 4:3 提案板。
- `hairstyle-style-preview`：从授权肖像生成身份保持的发型风格报告。
- `eyewear-style-preview`：比较镜框风格，不估算处方或毫米尺寸。
- `personal-outfit-studio`：灵感转译、个人改造和四季系列三种穿搭模式。
- `intimate-loungewear-board`：内衣与家居服产品提案两种模式。

每个目录都包含自己的 `SKILL.md`、调用界面、使用方法和 `assets/cover.png`；可以只安装其中一个。

## 安装

将需要的 Skill 目录复制到本机 Skill 目录：

```bash
cp -R skills/facial-style-preview ~/.codex/skills/
cp -R skills/nail-design-board ~/.codex/skills/
cp -R skills/hairstyle-style-preview ~/.codex/skills/
cp -R skills/eyewear-style-preview ~/.codex/skills/
cp -R skills/personal-outfit-studio ~/.codex/skills/
cp -R skills/intimate-loungewear-board ~/.codex/skills/
```

重启或刷新 Codex 后即可使用。也可以显式调用：

```text
使用 $nail-design-board 把“春日书页”做成十指美甲提案图。
使用 $hairstyle-style-preview 根据这张已授权照片生成自然、低维护的发型风格报告。
使用 $eyewear-style-preview 比较通勤用的金属框、透明框和板材框。
使用 $personal-outfit-studio，模式为 inspiration，做三套城市通勤造型。
使用 $intimate-loungewear-board，模式为 loungewear，做一张产品提案。
```

## 交付边界

这些 Skill 生成的是 AI 视觉提案，不是实拍、施工结果、医疗判断或效果保证。真人照片、手部照片、生成的人像和中间素材不应提交到公开仓库；本仓库封面为非真人、非身份参考的抽象视觉资产。

## 本地验证

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/nail-design-board
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/facial-style-preview
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/hairstyle-style-preview
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/eyewear-style-preview
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/personal-outfit-studio
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/intimate-loungewear-board
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
```

## 来源说明

Skill 逻辑根据用户桌面上的《AI美甲灵感方案》与《AI发型美学升级报告》提示词文档重新组织；原始 DOCX 不随仓库发布。
