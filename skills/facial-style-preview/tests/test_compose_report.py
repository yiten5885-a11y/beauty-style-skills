from __future__ import annotations

import hashlib
import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw, PngImagePlugin


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compose_report import LayoutError, compose_report  # noqa: E402
from report_manifest import REGION_IDS  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font_path() -> str | None:
    candidates = (
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
    )
    selected = next((path for path in candidates if path.is_file()), None)
    return str(selected) if selected else None


def manifest_payload() -> dict:
    return {
        "schema_version": "1.0",
        "style_goal": "自然清爽的日常妆面，由用户明确选择",
        "regions": [
            {
                "id": region_id,
                "mode": (
                    "simulated-visual-effect"
                    if region_id in {"nose", "contour"}
                    else "styling"
                ),
                "observation": "正面照片可见颜色与边界，细节受光线限制",
                "styling": "仅使用可逆妆容演示视觉层次并保持原有结构",
                "confidence": "medium",
            }
            for region_id in REGION_IDS
        ],
        "preserved": [
            "身份与面部几何",
            "年龄感与自然表情",
            "发型服装背景和光线",
        ],
        "uncertainties": [
            "单张正面照片不能确认侧面结构",
            "颜色受原图白平衡影响",
        ],
    }


class ComposeReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.before = self.root / "before.png"
        self.after = self.root / "after.png"
        for path, color in (
            (self.before, "#B7C6D9"),
            (self.after, "#C9D2B7"),
        ):
            image = Image.new("RGB", (600, 800), color)
            draw = ImageDraw.Draw(image)
            draw.ellipse((150, 90, 450, 470), outline="#24364B", width=10)
            draw.arc((220, 210, 290, 260), 180, 360, fill="#24364B", width=5)
            draw.arc((310, 210, 380, 260), 180, 360, fill="#24364B", width=5)
            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("PrivateNote", "must not survive")
            image.save(path, pnginfo=metadata)
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(
            json.dumps(manifest_payload(), ensure_ascii=False), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_composes_4_3_report_without_mutating_inputs(self) -> None:
        selected_font = font_path()
        if not selected_font:
            self.skipTest("no CJK font available")
        before_hash = sha256(self.before)
        after_hash = sha256(self.after)
        output = self.root / "report.png"
        receipt_path = self.root / "qa.json"
        receipt = compose_report(
            self.before,
            self.after,
            self.manifest,
            output,
            width=1200,
            height=900,
            font_path=selected_font,
            font_bold_path=selected_font,
            qa_report_path=receipt_path,
        )
        self.assertEqual(before_hash, sha256(self.before))
        self.assertEqual(after_hash, sha256(self.after))
        with Image.open(output) as image:
            self.assertEqual(image.size, (1200, 900))
            self.assertNotIn("PrivateNote", image.info)
            self.assertEqual(len(image.getexif()), 0)
        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["content"]["region_ids"], list(REGION_IDS))
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
        serialized = receipt_path.read_text(encoding="utf-8")
        self.assertNotIn(manifest_payload()["style_goal"], serialized)
        self.assertNotIn(str(self.before), serialized)

    def test_refuses_non_4_3_canvas_and_input_overwrite(self) -> None:
        selected_font = font_path()
        if not selected_font:
            self.skipTest("no CJK font available")
        with self.assertRaisesRegex(LayoutError, "4:3"):
            compose_report(
                self.before,
                self.after,
                self.manifest,
                self.root / "bad.png",
                width=1200,
                height=950,
                font_path=selected_font,
            )
        with self.assertRaisesRegex(LayoutError, "distinct"):
            compose_report(
                self.before,
                self.after,
                self.manifest,
                self.before,
                width=1200,
                height=900,
                font_path=selected_font,
            )

    def test_refuses_existing_output_without_overwrite(self) -> None:
        selected_font = font_path()
        if not selected_font:
            self.skipTest("no CJK font available")
        output = self.root / "report.png"
        output.write_bytes(b"user-owned")
        with self.assertRaises(FileExistsError):
            compose_report(
                self.before,
                self.after,
                self.manifest,
                output,
                width=1200,
                height=900,
                font_path=selected_font,
            )
        self.assertEqual(output.read_bytes(), b"user-owned")


if __name__ == "__main__":
    unittest.main()
