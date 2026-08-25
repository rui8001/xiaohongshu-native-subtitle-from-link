#!/usr/bin/env python3
"""Copy numbered JPG outputs into a new publish directory and JPG-only ZIP."""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Render directory")
    parser.add_argument("publish", type=Path, help="New publish directory")
    parser.add_argument("archive", type=Path, nargs="?", help="New ZIP path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    publish = args.publish.resolve()
    archive = (args.archive or publish.with_suffix(".zip")).resolve()

    if not source.is_dir():
        raise SystemExit(f"Render directory does not exist: {source}")
    if publish.exists() or archive.exists():
        raise SystemExit("Publish directory or ZIP already exists; refusing to overwrite")

    images = sorted(source.glob("[0-9][0-9]_*.jpg"))
    if not images:
        raise SystemExit(f"No numbered JPG files found: {source}")

    publish.parent.mkdir(parents=True, exist_ok=True)
    publish.mkdir()
    copied = []
    for image in images:
        destination = publish / image.name
        shutil.copy2(image, destination)
        copied.append(destination)

    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as handle:
        for image in copied:
            handle.write(image, arcname=image.name)

    with zipfile.ZipFile(archive) as handle:
        names = handle.namelist()
    if names != [image.name for image in copied]:
        raise SystemExit("ZIP entries do not match published images")

    print(f"Published {len(copied)} JPG files: {publish}")
    print(f"Created JPG-only ZIP: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
