#!/usr/bin/env python3
"""CLI validator for facial-style-preview manifests."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from report_manifest import ManifestError, load_manifest, validation_receipt


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    try:
        data = load_manifest(args.manifest)
        receipt = validation_receipt(data)
        if args.json_out:
            _write_private_json(args.json_out, receipt)
        if not args.quiet:
            print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0
    except (ManifestError, OSError) as error:
        print(f"ERROR: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
