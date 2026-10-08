#!/usr/bin/env python3
"""Validate the content contract for a non-medical facial styling report."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
REGION_IDS = ("brow", "eyes", "nose", "contour", "lips", "skin")
REGION_NAMES = {
    "brow": "眉部",
    "eyes": "眼部",
    "nose": "鼻部视觉",
    "contour": "轮廓视觉",
    "lips": "唇口周",
    "skin": "肤质呈现",
}
MODES = {
    "unchanged": "保持原貌",
    "styling": "非医疗造型",
    "simulated-visual-effect": "视觉效果",
    "not-assessable": "无法判断",
}
CONFIDENCE = {
    "high": "高",
    "medium": "中",
    "low": "低",
    "unknown": "未知",
}

_DISALLOWED_PATTERNS = (
    r"注射|填充|玻尿酸|肉毒|瘦脸针|水光针|线雕|埋线|激光|光子|射频|超声刀|热玛吉|医美",
    r"手术|整形|削骨|磨骨|假体|隆鼻|开眼角|双眼皮手术|丰唇|处方|剂量|针数|疗程|恢复期|适应证|禁忌证",
    r"诊断|治疗|痤疮|炎症|感染|过敏|疾病|病变|激素|处方药",
    r"颜值|丑|缺陷|瑕疵|完美脸|高级脸|网红脸|打分|评分|变美|变帅",
    r"\b(?:botox|filler|inject(?:ion|able)?|surgery|implant|laser|prescription|dose|diagnos\w*|treat(?:ment)?|disease|infection|allerg\w*|acne|attractiveness|ugly|flaw|defect|score)\b",
)
DISALLOWED_RE = re.compile(
    "|".join(f"(?:{item})" for item in _DISALLOWED_PATTERNS), re.IGNORECASE
)
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class ManifestError(ValueError):
    """Raised when a report manifest violates the contract."""


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(f"{label} must be a JSON object")
    return value


def _require_list(value: Any, label: str, minimum: int, maximum: int) -> list[Any]:
    if not isinstance(value, list):
        raise ManifestError(f"{label} must be a JSON array")
    if not minimum <= len(value) <= maximum:
        raise ManifestError(f"{label} must contain {minimum} to {maximum} items")
    return value


def _clean_text(value: Any, label: str, minimum: int, maximum: int) -> str:
    if not isinstance(value, str):
        raise ManifestError(f"{label} must be a string")
    text = value.strip()
    if not minimum <= len(text) <= maximum:
        raise ManifestError(f"{label} must contain {minimum} to {maximum} characters")
    if "\n" in text or "\r" in text or "\t" in text or CONTROL_RE.search(text):
        raise ManifestError(f"{label} must be a single line without control characters")
    match = DISALLOWED_RE.search(text)
    if match:
        raise ManifestError(
            f"{label} contains disallowed medical, diagnostic, or rating language: "
            f"{match.group(0)!r}"
        )
    return text


def validate_manifest(payload: Any) -> dict[str, Any]:
    data = _require_object(payload, "manifest")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ManifestError(f"schema_version must be {SCHEMA_VERSION!r}")

    clean: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "style_goal": _clean_text(data.get("style_goal"), "style_goal", 1, 80),
    }

    regions = _require_list(data.get("regions"), "regions", 6, 6)
    clean_regions: list[dict[str, str]] = []
    seen: list[str] = []
    for index, raw_region in enumerate(regions):
        region = _require_object(raw_region, f"regions[{index}]")
        region_id = region.get("id")
        if region_id not in REGION_IDS:
            raise ManifestError(
                f"regions[{index}].id must be one of {', '.join(REGION_IDS)}"
            )
        seen.append(region_id)
        mode = region.get("mode")
        if mode not in MODES:
            raise ManifestError(f"regions[{index}].mode is not supported")
        confidence = region.get("confidence")
        if confidence not in CONFIDENCE:
            raise ManifestError(f"regions[{index}].confidence is not supported")
        clean_regions.append(
            {
                "id": region_id,
                "mode": mode,
                "observation": _clean_text(
                    region.get("observation"),
                    f"regions[{index}].observation",
                    1,
                    64,
                ),
                "styling": _clean_text(
                    region.get("styling"), f"regions[{index}].styling", 1, 72
                ),
                "confidence": confidence,
            }
        )

    counts = Counter(seen)
    duplicates = sorted(region for region, count in counts.items() if count > 1)
    missing = sorted(set(REGION_IDS) - set(seen))
    if duplicates or missing:
        details = []
        if duplicates:
            details.append("duplicate: " + ", ".join(duplicates))
        if missing:
            details.append("missing: " + ", ".join(missing))
        raise ManifestError(
            "regions must contain each required ID exactly once ("
            + "; ".join(details)
            + ")"
        )

    by_id = {region["id"]: region for region in clean_regions}
    clean["regions"] = [by_id[region_id] for region_id in REGION_IDS]

    preserved = _require_list(data.get("preserved"), "preserved", 2, 6)
    clean["preserved"] = [
        _clean_text(item, f"preserved[{index}]", 1, 42)
        for index, item in enumerate(preserved)
    ]
    uncertainties = _require_list(data.get("uncertainties"), "uncertainties", 1, 4)
    clean["uncertainties"] = [
        _clean_text(item, f"uncertainties[{index}]", 1, 56)
        for index, item in enumerate(uncertainties)
    ]
    return clean


def load_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        size = source.stat().st_size
    except OSError as error:
        raise ManifestError(f"cannot read manifest: {error}") from error
    if size > 256_000:
        raise ManifestError("manifest exceeds the 256 KB limit")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ManifestError(f"manifest is not valid UTF-8 JSON: {error}") from error
    return validate_manifest(payload)


def validation_receipt(data: dict[str, Any]) -> dict[str, Any]:
    mode_counts = Counter(region["mode"] for region in data["regions"])
    return {
        "status": "pass",
        "schema_version": data["schema_version"],
        "region_ids": list(REGION_IDS),
        "mode_counts": dict(sorted(mode_counts.items())),
        "preserved_count": len(data["preserved"]),
        "uncertainty_count": len(data["uncertainties"]),
        "contains_user_text": False,
    }
