#!/usr/bin/env python3
"""Validate the content invariants of a nail-design-board manifest."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any


NAIL_MAP = {
    "L1": "左手拇指",
    "L2": "左手食指",
    "L3": "左手中指",
    "L4": "左手无名指",
    "L5": "左手小指",
    "R1": "右手拇指",
    "R2": "右手食指",
    "R3": "右手中指",
    "R4": "右手无名指",
    "R5": "右手小指",
}
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _text(value: Any, path: str, errors: list[str], *, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: must be a non-empty string")
        return ""
    value = value.strip()
    if len(value) > maximum:
        errors.append(f"{path}: exceeds {maximum} characters")
    return value


def _string_list(
    value: Any, path: str, errors: list[str], *, minimum: int, maximum: int, item_max: int
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{path}: must be a list")
        return []
    if not minimum <= len(value) <= maximum:
        errors.append(f"{path}: must contain {minimum}-{maximum} items")
    items = []
    for index, item in enumerate(value):
        items.append(_text(item, f"{path}[{index}]", errors, maximum=item_max))
    if len(set(items)) != len(items):
        errors.append(f"{path}: duplicate items are not allowed")
    return items


def validate_manifest(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: must be a JSON object"]

    if data.get("version") != "1.0":
        errors.append("version: must equal '1.0'")
    _text(data.get("locale"), "locale", errors, maximum=16)
    _text(data.get("title"), "title", errors, maximum=30)
    _text(data.get("theme"), "theme", errors, maximum=40)

    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("source: must be an object")
    else:
        if source.get("kind") not in {"text_theme", "inspiration_image"}:
            errors.append("source.kind: must be text_theme or inspiration_image")
        _text(source.get("label"), "source.label", errors, maximum=40)
        _text(source.get("summary"), "source.summary", errors, maximum=72)

    palette = data.get("palette")
    if not isinstance(palette, list) or len(palette) != 6:
        errors.append("palette: must contain exactly 6 colors")
        palette = []
    roles: list[str] = []
    palette_names: list[str] = []
    for index, color in enumerate(palette):
        path = f"palette[{index}]"
        if not isinstance(color, dict):
            errors.append(f"{path}: must be an object")
            continue
        role = color.get("role")
        if role not in {"primary", "secondary", "accent"}:
            errors.append(f"{path}.role: invalid role")
        else:
            roles.append(role)
        palette_names.append(_text(color.get("name"), f"{path}.name", errors, maximum=12))
        value = color.get("hex")
        if not isinstance(value, str) or not HEX_RE.fullmatch(value):
            errors.append(f"{path}.hex: must be #RRGGBB")
    if roles.count("primary") != 3 or roles.count("secondary") != 2 or roles.count("accent") != 1:
        errors.append("palette: roles must be 3 primary, 2 secondary, and 1 accent")
    if len(set(palette_names)) != len(palette_names):
        errors.append("palette: color names must be unique")

    _string_list(data.get("keywords"), "keywords", errors, minimum=4, maximum=6, item_max=12)
    _string_list(data.get("motifs"), "motifs", errors, minimum=4, maximum=6, item_max=16)
    _string_list(data.get("finishes"), "finishes", errors, minimum=2, maximum=6, item_max=16)

    nails = data.get("nails")
    if not isinstance(nails, list) or len(nails) != 10:
        errors.append("nails: must contain exactly 10 items")
        nails = []
    ids: list[str] = []
    design_names: list[str] = []
    for index, nail in enumerate(nails):
        path = f"nails[{index}]"
        if not isinstance(nail, dict):
            errors.append(f"{path}: must be an object")
            continue
        nail_id = nail.get("id")
        if nail_id not in NAIL_MAP:
            errors.append(f"{path}.id: invalid nail id")
        else:
            ids.append(nail_id)
            if nail.get("finger") != NAIL_MAP[nail_id]:
                errors.append(f"{path}.finger: must equal {NAIL_MAP[nail_id]}")
        design_names.append(_text(nail.get("design_name"), f"{path}.design_name", errors, maximum=14))
        _text(nail.get("base_color"), f"{path}.base_color", errors, maximum=16)
        _text(nail.get("motif"), f"{path}.motif", errors, maximum=16)
        _text(nail.get("finish"), f"{path}.finish", errors, maximum=16)
        _text(nail.get("description"), f"{path}.description", errors, maximum=42)
    if set(ids) != set(NAIL_MAP) or len(ids) != len(set(ids)):
        errors.append("nails: ids must be the unique set L1-L5 and R1-R5")
    if nails and len(set(design_names)) < 4:
        errors.append("nails: use at least 4 distinct design names")

    _text(data.get("summary"), "summary", errors, maximum=140)
    _string_list(
        data.get("recommended_shapes"),
        "recommended_shapes",
        errors,
        minimum=1,
        maximum=2,
        item_max=16,
    )
    _string_list(data.get("scenes"), "scenes", errors, minimum=1, maximum=5, item_max=12)

    preview = data.get("preview")
    if not isinstance(preview, dict):
        errors.append("preview: must be an object")
    else:
        if preview.get("mode") not in {"user_hand", "generic_adult_hand"}:
            errors.append("preview.mode: must be user_hand or generic_adult_hand")
        label = _text(preview.get("simulation_label"), "preview.simulation_label", errors, maximum=24)
        if label and "模拟" not in label:
            errors.append("preview.simulation_label: must visibly identify the preview as simulated")

    _text(data.get("feasibility_note"), "feasibility_note", errors, maximum=90)
    _text(data.get("final_note"), "final_note", errors, maximum=80)
    return errors


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a JSON object")
    return data


def _valid_fixture() -> dict[str, Any]:
    nails = []
    for index, (nail_id, finger) in enumerate(NAIL_MAP.items()):
        nails.append(
            {
                "id": nail_id,
                "finger": finger,
                "design_name": f"设计{index % 5 + 1}",
                "base_color": "夜雾蓝",
                "motif": "月弧",
                "finish": "微珠光",
                "description": "系列呼应与留白形成清晰节奏。",
            }
        )
    return {
        "version": "1.0",
        "locale": "zh-CN",
        "title": "AI美甲灵感方案",
        "theme": "月下银桂",
        "source": {"kind": "text_theme", "label": "月下银桂", "summary": "月光与银杏的抽象转译。"},
        "palette": [
            {"role": "primary", "name": "夜雾蓝", "hex": "#34445A"},
            {"role": "primary", "name": "月光银", "hex": "#C8CDD4"},
            {"role": "primary", "name": "雾白", "hex": "#EEEAE2"},
            {"role": "secondary", "name": "桂叶金", "hex": "#B69A58"},
            {"role": "secondary", "name": "浅烟灰", "hex": "#A7A9AC"},
            {"role": "accent", "name": "墨蓝", "hex": "#172235"},
        ],
        "keywords": ["清冷", "克制", "轻盈", "夜色"],
        "motifs": ["银杏叶", "月弧", "细金线", "雾化渐变"],
        "finishes": ["微珠光", "细金线"],
        "nails": nails,
        "summary": "用冷色基调和细金线建立克制的夜色节奏。",
        "recommended_shapes": ["短椭圆甲", "方圆甲"],
        "scenes": ["通勤", "晚宴"],
        "preview": {"mode": "generic_adult_hand", "simulation_label": "AI 模拟上手图"},
        "feasibility_note": "材料、价格、时长与施工可行性请由美甲师确认。",
        "final_note": "从月夜意象提取色彩与符号，形成完整十指系列。",
    }


def self_test() -> int:
    valid = _valid_fixture()
    if validate_manifest(valid):
        print("SELF-TEST FAIL: valid fixture was rejected", file=sys.stderr)
        return 1
    invalid = copy.deepcopy(valid)
    invalid["nails"] = invalid["nails"][:-1]
    errors = validate_manifest(invalid)
    if not any("exactly 10" in error for error in errors):
        print("SELF-TEST FAIL: missing nail was not detected", file=sys.stderr)
        return 1
    invalid = copy.deepcopy(valid)
    invalid["preview"]["simulation_label"] = "上手效果"
    errors = validate_manifest(invalid)
    if not any("simulated" in error for error in errors):
        print("SELF-TEST FAIL: simulation label violation was not detected", file=sys.stderr)
        return 1
    print("SELF-TEST PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.manifest is None:
        parser.error("manifest is required unless --self-test is used")
    try:
        data = load_manifest(args.manifest)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    errors = validate_manifest(data)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PASS: manifest satisfies nail-design-board invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
