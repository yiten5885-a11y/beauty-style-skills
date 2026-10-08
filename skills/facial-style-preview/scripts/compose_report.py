#!/usr/bin/env python3
"""Compose a deterministic 4:3 facial styling preview report."""

from __future__ import annotations

import argparse
import errno
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont, ImageOps

from report_manifest import (
    CONFIDENCE,
    MODES,
    REGION_NAMES,
    ManifestError,
    load_manifest,
)


DEFAULT_WIDTH = 2400
DEFAULT_HEIGHT = 1800
MAX_PIXELS = 50_000_000
BACKGROUND = "#F4F2ED"
PANEL = "#FFFDF9"
INK = "#16243B"
MUTED = "#5E6876"
LINE = "#D8D5CE"
ACCENT = "#758765"
ACCENT_PALE = "#E9EEE4"
WARM_PALE = "#F2E9DF"


class LayoutError(ValueError):
    """Raised when the report cannot be composed safely."""


def _font_candidates(bold: bool) -> Iterable[str]:
    if bold:
        yield "/System/Library/Fonts/STHeiti Medium.ttc"
        yield "/System/Library/Fonts/PingFang.ttc"
        yield "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
        yield "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        yield "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
        yield "DejaVuSans-Bold.ttf"
    else:
        yield "/System/Library/Fonts/STHeiti Light.ttc"
        yield "/System/Library/Fonts/STHeiti Medium.ttc"
        yield "/System/Library/Fonts/PingFang.ttc"
        yield "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        yield "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
        yield "DejaVuSans.ttf"


def _load_font(
    path: str | None, size: int, *, bold: bool
) -> ImageFont.FreeTypeFont:
    candidates: Sequence[str] = (path,) if path else tuple(_font_candidates(bold))
    errors: list[str] = []
    for candidate in candidates:
        if not candidate:
            continue
        try:
            return ImageFont.truetype(candidate, size=size)
        except (OSError, ValueError) as error:
            errors.append(f"{candidate}: {error}")
    detail = "; ".join(errors[-2:])
    raise LayoutError(
        "no usable font was found; pass --font and --font-bold"
        + (f" ({detail})" if detail else "")
    )


def _glyph_signature(
    font: ImageFont.FreeTypeFont, character: str
) -> tuple[tuple[int, int], bytes]:
    mask = font.getmask(character, mode="L")
    return mask.size, bytes(mask)


def _validate_font_coverage(
    font: ImageFont.FreeTypeFont, texts: Iterable[str]
) -> None:
    missing = {
        _glyph_signature(font, sentinel)
        for sentinel in ("\u0378", "\u0380", "\ufdd0", "\U0010ffff")
    }
    for text in texts:
        for character in text:
            if character.isspace():
                continue
            if _glyph_signature(font, character) in missing:
                raise LayoutError(f"font does not contain required glyph {character!r}")


def _rounded_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    fill: str = PANEL,
) -> None:
    draw.rounded_rectangle(box, radius=24, fill=fill, outline=LINE, width=2)


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    width: int,
) -> list[str]:
    lines: list[str] = []
    current = ""
    last_space = -1
    for character in text:
        candidate = current + character
        if draw.textlength(candidate, font=font) <= width:
            current = candidate
            if character.isspace():
                last_space = len(current) - 1
            continue
        if not current:
            raise LayoutError("a glyph is wider than the available text box")
        if last_space > 0:
            lines.append(current[:last_space].rstrip())
            current = current[last_space + 1 :] + character
        else:
            lines.append(current.rstrip())
            current = character.lstrip()
        last_space = max(current.rfind(" "), current.rfind("\t"))
    if current:
        lines.append(current.rstrip())
    return lines or [""]


def _fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    font_path: str | None,
    *,
    bold: bool = False,
    max_size: int,
    min_size: int,
    fill: str = INK,
    line_gap_ratio: float = 0.28,
) -> int:
    x1, y1, x2, y2 = box
    for size in range(max_size, min_size - 1, -1):
        font = _load_font(font_path, size, bold=bold)
        lines = _wrap_text(draw, text, font, x2 - x1)
        line_gap = max(3, round(size * line_gap_ratio))
        boxes = [draw.textbbox((0, 0), line or " ", font=font) for line in lines]
        heights = [box[3] - box[1] for box in boxes]
        total_height = sum(heights) + max(0, len(lines) - 1) * line_gap
        if total_height <= y2 - y1:
            y = y1
            for line, line_height in zip(lines, heights):
                draw.text((x1, y), line, font=font, fill=fill)
                y += line_height + line_gap
            return size
    raise LayoutError(f"text cannot fit at the readable minimum: {text[:24]!r}")


def _draw_image_slot(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    image: Image.Image,
    box: tuple[int, int, int, int],
    label: str,
    font_path: str | None,
    *,
    accent: bool,
    scale: float,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(
        box,
        radius=max(12, round(26 * scale)),
        fill="#E7E5E0",
        outline=ACCENT if accent else LINE,
        width=max(2, round(3 * scale)),
    )
    label_height = round(62 * scale)
    image_box = (
        x1 + round(4 * scale),
        y1 + label_height,
        x2 - round(4 * scale),
        y2 - round(4 * scale),
    )
    target_w = image_box[2] - image_box[0]
    target_h = image_box[3] - image_box[1]
    contained = ImageOps.contain(
        image, (target_w, target_h), method=Image.Resampling.LANCZOS
    )
    layer = Image.new("RGB", (target_w, target_h), "#E7E5E0")
    layer.paste(
        contained,
        ((target_w - contained.width) // 2, (target_h - contained.height) // 2),
    )
    canvas.paste(layer, (image_box[0], image_box[1]))
    label_font = _load_font(
        font_path, max(13, round(26 * scale)), bold=True
    )
    draw.text(
        (x1 + round(22 * scale), y1 + round(16 * scale)),
        label,
        font=label_font,
        fill=ACCENT if accent else INK,
    )


def _open_image(path: Path) -> tuple[Image.Image, tuple[int, int]]:
    try:
        with Image.open(path) as opened:
            if opened.width * opened.height > MAX_PIXELS:
                raise LayoutError(
                    f"input image exceeds the {MAX_PIXELS:,}-pixel limit"
                )
            original_size = (opened.width, opened.height)
            image = ImageOps.exif_transpose(opened).convert("RGB")
            image.load()
            return image, original_size
    except (OSError, ValueError) as error:
        raise LayoutError(f"cannot read image: {error}") from error


def _atomic_save_png(
    image: Image.Image, destination: Path, overwrite: bool
) -> None:
    if destination.suffix.lower() != ".png":
        raise LayoutError("output must use the .png extension")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.stem}.", suffix=".png", dir=destination.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        image.save(temporary, format="PNG", optimize=True)
        if overwrite:
            os.replace(temporary, destination)
        else:
            try:
                os.link(temporary, destination)
                temporary.unlink()
            except FileExistsError:
                raise
            except OSError as error:
                unsupported = {
                    errno.EPERM,
                    errno.EXDEV,
                    getattr(errno, "ENOTSUP", errno.EPERM),
                    getattr(errno, "EOPNOTSUPP", errno.EPERM),
                }
                if error.errno not in unsupported:
                    raise
                descriptor = os.open(
                    destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
                try:
                    with temporary.open("rb") as source, os.fdopen(
                        descriptor, "wb"
                    ) as target:
                        shutil.copyfileobj(source, target)
                        target.flush()
                        os.fsync(target.fileno())
                except Exception:
                    destination.unlink(missing_ok=True)
                    raise
                temporary.unlink()
        os.chmod(destination, 0o600)
    finally:
        temporary.unlink(missing_ok=True)


def _write_private_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
        os.chmod(path, 0o600)
    finally:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


def compose_report(
    before_path: Path,
    after_path: Path,
    manifest_path: Path,
    output_path: Path,
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    font_path: str | None = None,
    font_bold_path: str | None = None,
    overwrite: bool = False,
    qa_report_path: Path | None = None,
) -> dict:
    if width < 1200 or height < 900 or width > 6000 or height > 4500:
        raise LayoutError(
            "canvas must be between 1200 x 900 and 6000 x 4500 pixels"
        )
    if width * 3 != height * 4:
        raise LayoutError("canvas must use an exact 4:3 landscape ratio")
    resolved_output = output_path.resolve()
    if resolved_output in {
        before_path.resolve(),
        after_path.resolve(),
        manifest_path.resolve(),
    }:
        raise LayoutError("output path must be distinct from every input path")
    if qa_report_path and qa_report_path.resolve() == resolved_output:
        raise LayoutError("QA report path must differ from the image output path")

    manifest = load_manifest(manifest_path)
    before, before_size = _open_image(before_path)
    after, after_size = _open_image(after_path)

    scale = width / DEFAULT_WIDTH
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    def regular(size: int) -> ImageFont.FreeTypeFont:
        return _load_font(font_path, max(12, round(size * scale)), bold=False)

    def bold(size: int) -> ImageFont.FreeTypeFont:
        return _load_font(
            font_bold_path or font_path,
            max(12, round(size * scale)),
            bold=True,
        )

    fixed_texts = [
        "面部造型预览",
        "FACIAL STYLING PREVIEW",
        "输入照片",
        "造型模拟 · 非医疗",
        "用户选择的方向",
        "明确保持不变",
        "照片无法确认",
        "可见",
        "造型",
        "置信度",
        "右图为非医疗视觉模拟，不是诊断、治疗方案或效果承诺；涉及医疗问题，请咨询具备相应资质的专业人员。",
        *REGION_NAMES.values(),
        *MODES.values(),
        *CONFIDENCE.values(),
    ]
    _validate_font_coverage(regular(28), fixed_texts)
    _validate_font_coverage(
        regular(24),
        [
            manifest["style_goal"],
            *manifest["preserved"],
            *manifest["uncertainties"],
            *(region["observation"] for region in manifest["regions"]),
            *(region["styling"] for region in manifest["regions"]),
        ],
    )

    margin = round(72 * scale)
    draw.text(
        (margin, round(42 * scale)),
        "面部造型预览",
        font=bold(54),
        fill=INK,
    )
    draw.text(
        (margin, round(112 * scale)),
        "FACIAL STYLING PREVIEW",
        font=regular(22),
        fill=MUTED,
    )
    draw.line(
        (margin, round(168 * scale), width - margin, round(168 * scale)),
        fill=LINE,
        width=max(2, round(2 * scale)),
    )

    image_y1 = round(205 * scale)
    image_y2 = round(1125 * scale)
    image_x1 = margin
    image_x2 = round(1160 * scale)
    gap = round(20 * scale)
    slot_width = (image_x2 - image_x1 - gap) // 2
    _draw_image_slot(
        canvas,
        draw,
        before,
        (image_x1, image_y1, image_x1 + slot_width, image_y2),
        "输入照片",
        font_bold_path or font_path,
        accent=False,
        scale=scale,
    )
    _draw_image_slot(
        canvas,
        draw,
        after,
        (image_x1 + slot_width + gap, image_y1, image_x2, image_y2),
        "造型模拟 · 非医疗",
        font_bold_path or font_path,
        accent=True,
        scale=scale,
    )

    grid_x1 = round(1210 * scale)
    grid_x2 = width - margin
    grid_gap = round(18 * scale)
    card_width = (grid_x2 - grid_x1 - grid_gap) // 2
    card_height = (image_y2 - image_y1 - 2 * grid_gap) // 3
    for index, region in enumerate(manifest["regions"]):
        column = index % 2
        row = index // 2
        x1 = grid_x1 + column * (card_width + grid_gap)
        y1 = image_y1 + row * (card_height + grid_gap)
        x2 = x1 + card_width
        y2 = y1 + card_height
        _rounded_panel(
            draw,
            (x1, y1, x2, y2),
            fill=ACCENT_PALE if region["mode"] == "unchanged" else PANEL,
        )
        pad = round(22 * scale)
        draw.text(
            (x1 + pad, y1 + round(18 * scale)),
            f"{index + 1:02d}  {REGION_NAMES[region['id']]}",
            font=bold(28),
            fill=INK,
        )
        mode_text = MODES[region["mode"]]
        mode_font = regular(19)
        mode_width = draw.textlength(mode_text, font=mode_font)
        draw.text(
            (x2 - pad - mode_width, y1 + round(23 * scale)),
            mode_text,
            font=mode_font,
            fill=ACCENT,
        )
        body_x1 = x1 + pad
        body_x2 = x2 - pad
        body_top = y1 + round(72 * scale)
        body_mid = y1 + round(164 * scale)
        _fit_text(
            draw,
            "可见：" + region["observation"],
            (body_x1, body_top, body_x2, body_mid - round(6 * scale)),
            font_path,
            max_size=max(12, round(23 * scale)),
            min_size=max(9, round(17 * scale)),
            fill=MUTED,
        )
        _fit_text(
            draw,
            "造型：" + region["styling"],
            (body_x1, body_mid, body_x2, y2 - round(42 * scale)),
            font_path,
            max_size=max(12, round(23 * scale)),
            min_size=max(9, round(17 * scale)),
            fill=INK,
        )
        draw.text(
            (body_x1, y2 - round(35 * scale)),
            "置信度：" + CONFIDENCE[region["confidence"]],
            font=regular(17),
            fill=MUTED,
        )

    bottom_y1 = round(1165 * scale)
    bottom_y2 = round(1570 * scale)
    bottom_gap = round(18 * scale)
    inner_width = width - 2 * margin
    widths = [round(660 * scale), round(760 * scale)]
    widths.append(inner_width - sum(widths) - 2 * bottom_gap)
    panel_titles = ["用户选择的方向", "明确保持不变", "照片无法确认"]
    panel_contents = [
        manifest["style_goal"],
        "  ·  ".join(manifest["preserved"]),
        "  ·  ".join(manifest["uncertainties"]),
    ]
    x = margin
    for panel_width, title, content in zip(
        widths, panel_titles, panel_contents
    ):
        x2 = x + panel_width
        _rounded_panel(draw, (x, bottom_y1, x2, bottom_y2))
        pad = round(26 * scale)
        draw.text(
            (x + pad, bottom_y1 + round(24 * scale)),
            title,
            font=bold(27),
            fill=INK,
        )
        _fit_text(
            draw,
            content,
            (
                x + pad,
                bottom_y1 + round(82 * scale),
                x2 - pad,
                bottom_y2 - round(26 * scale),
            ),
            font_path,
            max_size=max(12, round(27 * scale)),
            min_size=max(9, round(18 * scale)),
            fill=MUTED,
            line_gap_ratio=0.38,
        )
        x = x2 + bottom_gap

    notice_box = (
        margin,
        round(1600 * scale),
        width - margin,
        round(1735 * scale),
    )
    draw.rounded_rectangle(
        notice_box,
        radius=max(10, round(20 * scale)),
        fill=WARM_PALE,
        outline=LINE,
        width=max(2, round(2 * scale)),
    )
    notice = "右图为非医疗视觉模拟，不是诊断、治疗方案或效果承诺；涉及医疗问题，请咨询具备相应资质的专业人员。"
    _fit_text(
        draw,
        notice,
        (
            notice_box[0] + round(28 * scale),
            notice_box[1] + round(28 * scale),
            notice_box[2] - round(28 * scale),
            notice_box[3] - round(22 * scale),
        ),
        font_bold_path or font_path,
        bold=True,
        max_size=max(12, round(25 * scale)),
        min_size=max(9, round(19 * scale)),
        fill=INK,
    )

    _atomic_save_png(canvas, output_path, overwrite)
    mode_counts = Counter(region["mode"] for region in manifest["regions"])
    receipt = {
        "status": "pass",
        "schema_version": manifest["schema_version"],
        "output": {
            "width": width,
            "height": height,
            "format": "PNG",
            "bytes": output_path.stat().st_size,
            "mode": oct(output_path.stat().st_mode & 0o777),
            "metadata_stripped": True,
        },
        "inputs": {
            "before_dimensions": list(before_size),
            "after_dimensions": list(after_size),
        },
        "content": {
            "region_ids": [region["id"] for region in manifest["regions"]],
            "mode_counts": dict(sorted(mode_counts.items())),
            "preserved_count": len(manifest["preserved"]),
            "uncertainty_count": len(manifest["uncertainties"]),
            "contains_user_text": False,
        },
        "checks": {
            "exact_4_3_ratio": True,
            "six_regions_exactly_once": True,
            "text_fit": True,
            "medical_wording_gate": True,
        },
    }
    if qa_report_path:
        _write_private_json(qa_report_path, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--qa-report", type=Path)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--font")
    parser.add_argument("--font-bold")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        receipt = compose_report(
            args.before,
            args.after,
            args.manifest,
            args.output,
            width=args.width,
            height=args.height,
            font_path=args.font,
            font_bold_path=args.font_bold,
            overwrite=args.overwrite,
            qa_report_path=args.qa_report,
        )
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0
    except (
        LayoutError,
        ManifestError,
        FileExistsError,
        OSError,
    ) as error:
        print(f"ERROR: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
