#!/usr/bin/env python3
"""Render a deterministic 2400x1800 nail proposal board from a valid manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: install it in the active Python environment") from exc

from validate_nail_manifest import load_manifest, validate_manifest


WIDTH = 2400
HEIGHT = 1800
BG = "#F4F0E8"
PANEL = "#FCFAF6"
INK = "#23211E"
MUTED = "#6E675F"
LINE = "#D8D0C4"
ACCENT = "#8A6B4B"

FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


class LayoutError(RuntimeError):
    pass


def font_path() -> str:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    raise LayoutError("No CJK-capable font found; install Noto Sans CJK")


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = font_path()
    index = 1 if bold and path.endswith(".ttc") else 0
    try:
        return ImageFont.truetype(path, size=size, index=index)
    except OSError:
        return ImageFont.truetype(path, size=size)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str) -> None:
    draw.rounded_rectangle(box, radius=18, fill=PANEL, outline=LINE, width=2)
    x1, y1, _, _ = box
    draw.text((x1 + 24, y1 + 20), title, font=font(28, bold=True), fill=INK)


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        current = ""
        for char in paragraph:
            candidate = current + char
            if current and draw.textlength(candidate, font=selected_font) > width:
                lines.append(current.rstrip())
                current = char.lstrip()
            else:
                current = candidate
        lines.append(current.rstrip())
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    selected_font: ImageFont.FreeTypeFont,
    *,
    fill: str = INK,
    width: int,
    max_lines: int,
    line_gap: int = 8,
) -> int:
    lines = wrap_lines(draw, text, selected_font, width)
    if len(lines) > max_lines:
        raise LayoutError(f"text overflow: {text!r} needs {len(lines)} lines, limit is {max_lines}")
    x, y = xy
    bbox = selected_font.getbbox("国Ag")
    line_height = bbox[3] - bbox[1] + line_gap
    for line in lines:
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += line_height
    return y


def fitted(path: Path, size: tuple[int, int]) -> Image.Image:
    try:
        with Image.open(path) as source:
            converted = ImageOps.exif_transpose(source).convert("RGB")
            return ImageOps.fit(converted, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    except (OSError, ValueError) as exc:
        raise LayoutError(f"cannot decode image {path}: {exc}") from exc


def theme_tile(manifest: dict, size: tuple[int, int]) -> Image.Image:
    """Create a deterministic abstract mood tile for text-only themes."""
    width, height = size
    colors = [item["hex"] for item in manifest["palette"]]
    start = tuple(int(colors[0][i : i + 2], 16) for i in (1, 3, 5))
    end = tuple(int(colors[-1][i : i + 2], 16) for i in (1, 3, 5))
    tile = Image.new("RGB", size)
    tile_draw = ImageDraw.Draw(tile)
    for x in range(width):
        ratio = x / max(width - 1, 1)
        mixed = tuple(round(start[channel] * (1 - ratio) + end[channel] * ratio) for channel in range(3))
        tile_draw.line((x, 0, x, height), fill=mixed)
    tile_draw.ellipse((40, 34, 184, 178), outline=colors[1], width=9)
    tile_draw.ellipse((72, 18, 208, 160), fill=start)
    tile_draw.arc((width - 210, 24, width - 42, 192), start=210, end=520, fill=colors[3], width=8)
    for offset in (0, 48, 96):
        tile_draw.ellipse((width - 150 + offset // 3, 124 + offset // 4, width - 126 + offset // 3, 148 + offset // 4), fill=colors[3])
    return tile


def bullets(items: Iterable[str]) -> str:
    return "  ·  ".join(items)


def draw_source_panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    manifest: dict,
    inspiration: Path | None,
    box: tuple[int, int, int, int],
) -> None:
    panel(draw, box, "01  灵感来源 / INSPIRATION")
    x1, y1, x2, _ = box
    content_y = y1 + 68
    if inspiration:
        image = fitted(inspiration, (x2 - x1 - 48, 270))
        canvas.paste(image, (x1 + 24, content_y))
        content_y += 292
    else:
        canvas.paste(theme_tile(manifest, (x2 - x1 - 48, 230)), (x1 + 24, content_y))
        content_y += 252
    draw.text((x1 + 24, content_y), manifest["source"]["label"], font=font(30, bold=True), fill=ACCENT)
    draw_wrapped(
        draw,
        (x1 + 24, content_y + 52),
        manifest["source"]["summary"],
        font(22),
        fill=MUTED,
        width=x2 - x1 - 48,
        max_lines=4,
    )


def draw_palette(draw: ImageDraw.ImageDraw, manifest: dict, box: tuple[int, int, int, int]) -> None:
    panel(draw, box, "02  色彩系统 / PALETTE")
    x1, y1, _, _ = box
    for index, color in enumerate(manifest["palette"]):
        col = index % 3
        row = index // 3
        x = x1 + 28 + col * 154
        y = y1 + 84 + row * 116
        draw.ellipse((x, y, x + 54, y + 54), fill=color["hex"], outline=LINE, width=2)
        draw.text((x + 68, y - 2), color["name"], font=font(20, bold=True), fill=INK)
        draw.text((x + 68, y + 28), color["hex"].upper(), font=font(16), fill=MUTED)


def draw_keywords(draw: ImageDraw.ImageDraw, manifest: dict, box: tuple[int, int, int, int]) -> None:
    panel(draw, box, "03  视觉转译 / VISUAL LANGUAGE")
    x1, y1, x2, _ = box
    draw.text((x1 + 24, y1 + 78), "风格关键词", font=font(23, bold=True), fill=ACCENT)
    draw_wrapped(draw, (x1 + 24, y1 + 122), bullets(manifest["keywords"]), font(21), width=x2 - x1 - 48, max_lines=4)
    draw.text((x1 + 24, y1 + 250), "图案与符号", font=font(23, bold=True), fill=ACCENT)
    draw_wrapped(draw, (x1 + 24, y1 + 294), bullets(manifest["motifs"]), font(21), width=x2 - x1 - 48, max_lines=5)
    draw.text((x1 + 24, y1 + 445), "主题收束", font=font(23, bold=True), fill=ACCENT)
    draw_wrapped(draw, (x1 + 24, y1 + 489), manifest["final_note"], font(20), fill=MUTED, width=x2 - x1 - 48, max_lines=4)


def draw_nail_plan(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    image_path: Path,
    box: tuple[int, int, int, int],
) -> None:
    panel(draw, box, "04  十指设计平铺 / 10-NAIL PLAN")
    x1, y1, x2, _ = box
    image = fitted(image_path, (x2 - x1 - 48, 510))
    canvas.paste(image, (x1 + 24, y1 + 72))
    draw.rounded_rectangle((x1 + 24, y1 + 598, x2 - 24, y1 + 658), radius=12, fill="#EEE7DC")
    draw.text((x1 + 46, y1 + 612), "左手  L1  L2  L3  L4  L5", font=font(22, bold=True), fill=INK)
    draw.text((x1 + 610, y1 + 612), "右手  R1  R2  R3  R4  R5", font=font(22, bold=True), fill=INK)


def draw_nail_list(draw: ImageDraw.ImageDraw, manifest: dict, box: tuple[int, int, int, int]) -> None:
    panel(draw, box, "05  十指说明 / DESIGN NOTES")
    x1, y1, x2, _ = box
    mid = (x1 + x2) // 2
    draw.line((mid, y1 + 72, mid, box[3] - 24), fill=LINE, width=2)
    by_id = {item["id"]: item for item in manifest["nails"]}
    for side_index, prefix in enumerate(("L", "R")):
        col_x = x1 + 24 if side_index == 0 else mid + 24
        col_width = mid - x1 - 54
        for number in range(1, 6):
            item = by_id[f"{prefix}{number}"]
            row_y = y1 + 82 + (number - 1) * 116
            draw.text((col_x, row_y), item["id"], font=font(25, bold=True), fill=ACCENT)
            draw.text((col_x + 58, row_y), item["design_name"], font=font(23, bold=True), fill=INK)
            meta = f"{item['base_color']} · {item['motif']} · {item['finish']}"
            draw_wrapped(draw, (col_x + 58, row_y + 39), meta, font(18), fill=MUTED, width=col_width - 58, max_lines=2, line_gap=5)
            draw_wrapped(
                draw,
                (col_x + 58, row_y + 68),
                item["description"],
                font(16),
                fill=MUTED,
                width=col_width - 58,
                max_lines=2,
                line_gap=3,
            )
            if number < 5:
                draw.line((col_x, row_y + 102, col_x + col_width, row_y + 102), fill="#E8E1D6", width=1)


def draw_preview(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    manifest: dict,
    image_path: Path,
    box: tuple[int, int, int, int],
) -> None:
    panel(draw, box, "06  上手预览 / ON-HAND PREVIEW")
    x1, y1, x2, _ = box
    image = fitted(image_path, (x2 - x1 - 48, 480))
    canvas.paste(image, (x1 + 24, y1 + 72))
    label = manifest["preview"]["simulation_label"]
    label_font = font(22, bold=True)
    label_width = int(draw.textlength(label, font=label_font)) + 34
    draw.rounded_rectangle((x2 - label_width - 36, y1 + 88, x2 - 24, y1 + 134), radius=14, fill="#FFF5DE")
    draw.text((x2 - label_width - 19, y1 + 96), label, font=label_font, fill="#7A5526")
    mode = "使用用户手部参考" if manifest["preview"]["mode"] == "user_hand" else "通用成年手模"
    draw.text((x1 + 24, y1 + 574), mode, font=font(20), fill=MUTED)


def draw_summary(draw: ImageDraw.ImageDraw, manifest: dict, box: tuple[int, int, int, int]) -> None:
    panel(draw, box, "07  风格总结 / CONCEPT")
    x1, y1, x2, _ = box
    draw.text((x1 + 24, y1 + 78), manifest["theme"], font=font(34, bold=True), fill=ACCENT)
    draw_wrapped(draw, (x1 + 24, y1 + 132), manifest["summary"], font(21), width=x2 - x1 - 48, max_lines=6)


def draw_practical(draw: ImageDraw.ImageDraw, manifest: dict, box: tuple[int, int, int, int]) -> None:
    panel(draw, box, "08  落地建议 / PRACTICAL NOTES")
    x1, y1, x2, _ = box
    rows = [
        ("推荐甲型", bullets(manifest["recommended_shapes"])),
        ("关键工艺", bullets(manifest["finishes"])),
        ("适用场景", bullets(manifest["scenes"])),
    ]
    y = y1 + 78
    for label, value in rows:
        draw.text((x1 + 24, y), label, font=font(21, bold=True), fill=ACCENT)
        y = draw_wrapped(draw, (x1 + 146, y), value, font(20), width=x2 - x1 - 170, max_lines=2, line_gap=5) + 20
    draw.line((x1 + 24, y, x2 - 24, y), fill=LINE, width=1)
    draw_wrapped(draw, (x1 + 24, y + 22), manifest["feasibility_note"], font(18), fill=MUTED, width=x2 - x1 - 48, max_lines=4)


def render(manifest: dict, nail_plan: Path, on_hand: Path, inspiration: Path | None, output: Path) -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 44), manifest["title"], font=font(62, bold=True), fill=INK)
    draw.text((60, 124), "AI NAIL INSPIRATION BOARD", font=font(24), fill=MUTED)
    draw.text((1720, 66), manifest["theme"], font=font(36, bold=True), fill=ACCENT)
    draw.text((1720, 116), f"Inspired by {manifest['source']['label']}", font=font(20), fill=MUTED)
    draw.line((60, 176, 2340, 176), fill=LINE, width=2)

    draw_source_panel(canvas, draw, manifest, inspiration, (60, 204, 560, 706))
    draw_palette(draw, manifest, (60, 730, 560, 1064))
    draw_keywords(draw, manifest, (60, 1088, 560, 1688))
    draw_nail_plan(canvas, draw, nail_plan, (592, 204, 1722, 888))
    draw_nail_list(draw, manifest, (592, 912, 1722, 1688))
    draw_preview(canvas, draw, manifest, on_hand, (1754, 204, 2340, 854))
    draw_summary(draw, manifest, (1754, 878, 2340, 1244))
    draw_practical(draw, manifest, (1754, 1268, 2340, 1688))

    footer = "本图为设计与沟通参考。上手效果为 AI 模拟；材料、时长、价格及施工可行性以美甲师核实为准。"
    draw.text((60, 1728), footer, font=font(20), fill=MUTED)
    draw.text((2230, 1728), "4:3", font=font(20, bold=True), fill=ACCENT)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="PNG", optimize=True)
    with Image.open(output) as saved:
        if saved.size != (WIDTH, HEIGHT) or saved.format != "PNG":
            raise LayoutError("saved output failed dimension or format verification")
        disallowed = {key for key in saved.info if key.lower() not in {"dpi"}}
        if disallowed:
            raise LayoutError(f"saved output contains unexpected metadata: {sorted(disallowed)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--nail-plan", required=True, type=Path)
    parser.add_argument("--on-hand", required=True, type=Path)
    parser.add_argument("--inspiration", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        manifest = load_manifest(args.manifest)
        errors = validate_manifest(manifest)
        if errors:
            raise LayoutError("manifest validation failed:\n- " + "\n- ".join(errors))
        render(manifest, args.nail_plan, args.on_hand, args.inspiration, args.output)
    except (LayoutError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: rendered {args.output} ({WIDTH}x{HEIGHT})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
