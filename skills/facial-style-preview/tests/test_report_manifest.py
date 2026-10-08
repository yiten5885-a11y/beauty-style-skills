from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from report_manifest import (  # noqa: E402
    ManifestError,
    REGION_IDS,
    validate_manifest,
    validation_receipt,
)


def valid_manifest() -> dict:
    regions = []
    for region_id in REGION_IDS:
        regions.append(
            {
                "id": region_id,
                "mode": (
                    "styling"
                    if region_id not in {"nose", "contour"}
                    else "simulated-visual-effect"
                ),
                "observation": "照片中可见的颜色与边界，细节受光线限制",
                "styling": "使用可逆妆容演示视觉层次，同时保持原有结构",
                "confidence": "medium",
            }
        )
    return {
        "schema_version": "1.0",
        "style_goal": "自然清爽的日常妆面，由用户明确选择",
        "regions": regions,
        "preserved": ["身份与面部几何", "年龄感与自然表情"],
        "uncertainties": ["单张正面照片不能确认侧面信息"],
    }


class ReportManifestTests(unittest.TestCase):
    def test_valid_manifest_is_normalized_and_receipt_has_no_text(self) -> None:
        payload = valid_manifest()
        payload["regions"].reverse()
        clean = validate_manifest(payload)
        self.assertEqual(
            [region["id"] for region in clean["regions"]], list(REGION_IDS)
        )
        receipt = validation_receipt(clean)
        self.assertFalse(receipt["contains_user_text"])
        serialized = str(receipt)
        self.assertNotIn(payload["style_goal"], serialized)

    def test_rejects_missing_and_duplicate_region(self) -> None:
        payload = valid_manifest()
        payload["regions"][-1] = copy.deepcopy(payload["regions"][0])
        with self.assertRaisesRegex(ManifestError, "duplicate"):
            validate_manifest(payload)

    def test_rejects_treatment_recommendation(self) -> None:
        payload = valid_manifest()
        payload["regions"][2]["styling"] = "建议鼻部填充并评估注射剂量"
        with self.assertRaisesRegex(ManifestError, "disallowed"):
            validate_manifest(payload)

    def test_rejects_diagnosis_and_attractiveness_rating(self) -> None:
        for unsafe in (
            "诊断为皮肤炎症",
            "颜值评分为八分",
            "remove acne with treatment",
        ):
            payload = valid_manifest()
            payload["regions"][5]["observation"] = unsafe
            with self.subTest(unsafe=unsafe), self.assertRaises(ManifestError):
                validate_manifest(payload)

    def test_rejects_unknown_mode_and_multiline_text(self) -> None:
        payload = valid_manifest()
        payload["regions"][0]["mode"] = "surgery"
        with self.assertRaises(ManifestError):
            validate_manifest(payload)
        payload = valid_manifest()
        payload["style_goal"] = "自然\n清爽"
        with self.assertRaises(ManifestError):
            validate_manifest(payload)


if __name__ == "__main__":
    unittest.main()
