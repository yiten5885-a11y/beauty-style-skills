# Beauty Style Skills

![Beauty Style Skills cover](assets/cover.png)

把文字主题或授权照片转译为可沟通的美甲与发型视觉提案。仓库包含两个可独立调用的 Codex Skill：

- `nail-design-board`：从主题或灵感图生成十指美甲设计清单、模拟上手图和横向 4:3 提案板。
- `hairstyle-upgrade-board`：从授权肖像生成身份保持的 Before/After 发型升级报告、推荐方案、避雷提醒和执行指南。

## 安装

将需要的 Skill 目录复制到本机 Skill 目录：

```bash
cp -R skills/nail-design-board ~/.codex/skills/
cp -R skills/hairstyle-upgrade-board ~/.codex/skills/
```

重启或刷新 Codex 后即可使用。也可以显式调用：

```text
使用 $nail-design-board 把“春日书页”做成十指美甲提案图。
使用 $hairstyle-upgrade-board 根据这张已授权照片生成自然、低维护的发型升级报告。
```

## 交付边界

这些 Skill 生成的是 AI 视觉提案，不是实拍、施工结果、医疗判断或效果保证。真人照片、手部照片、生成的人像和中间素材不应提交到公开仓库；本仓库封面为非真人、非身份参考的抽象视觉资产。

## 本地验证

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/nail-design-board
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/hairstyle-upgrade-board
```

## 来源说明

Skill 逻辑根据用户桌面上的《AI美甲灵感方案》与《AI发型美学升级报告》提示词文档重新组织；原始 DOCX 不随仓库发布。
