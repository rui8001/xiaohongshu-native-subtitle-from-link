#!/usr/bin/env python3
"""Copy numbered JPG outputs into a new publish directory and JPG-only ZIP."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Render directory")
    parser.add_argument("publish", type=Path, help="New publish directory")
    parser.add_argument("archive", type=Path, nargs="?", help="New ZIP path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    # Resolve parents, but never follow a destination symlink.
    publish = args.publish.parent.resolve() / args.publish.name
    archive_arg = args.archive or publish.with_suffix(".zip")
    archive = archive_arg.parent.resolve() / archive_arg.name

    if not source.is_dir():
        raise SystemExit(f"Render directory does not exist: {source}")
    if any(path.exists() or path.is_symlink() for path in (publish, archive)):
        raise SystemExit("Publish directory or ZIP already exists; refusing to overwrite")
    if archive == publish or publish in archive.parents or archive in publish.parents:
        raise SystemExit("Publish directory and ZIP paths must not overlap")

    images = sorted(
        (path for path in source.iterdir() if re.fullmatch(r"[0-9]{2,}_.+\.jpg", path.name)),
        key=lambda path: (int(path.name.split("_", 1)[0]), path.name),
    )
    if not images:
        raise SystemExit(f"No numbered JPG files found: {source}")

    for image in images:
        if image.is_symlink() or not image.is_file():
            raise SystemExit(f"Numbered images must be regular files: {image.name}")

    publish.parent.mkdir(parents=True, exist_ok=True)
    # Stage and verify before creating either final output. Normal publication
    # failures roll back only files created here; existing outputs stay intact.
    with tempfile.TemporaryDirectory(prefix=".subtitle-package-", dir=publish.parent) as temporary:
        staging = Path(temporary)
        copied = []
        for image in images:
            destination = staging / image.name
            shutil.copy2(image, destination, follow_symlinks=False)
            if destination.is_symlink():
                raise SystemExit(f"Source changed to a symlink: {image.name}")
            try:
                with Image.open(destination) as picture:
                    if picture.format != "JPEG":
                        raise ValueError("not JPEG")
                    picture.verify()
                with Image.open(destination) as picture:
                    picture.load()
            except (OSError, ValueError, UnidentifiedImageError) as exc:
                raise SystemExit(f"Invalid JPEG: {image.name}") from exc
            copied.append(destination)

        staged_zip = staging / "images.zip"
        with zipfile.ZipFile(staged_zip, "x", compression=zipfile.ZIP_DEFLATED) as handle:
            for image in copied:
                handle.write(image, arcname=image.name)
        with zipfile.ZipFile(staged_zip) as handle:
            if handle.namelist() != [image.name for image in copied] or handle.testzip():
                raise SystemExit("ZIP verification failed")

        archive.parent.mkdir(parents=True, exist_ok=True)
        owned_files = []
        owns_publish = owns_archive = False
        try:
            publish.mkdir()  # exclusive: refuse a destination created during staging
            owns_publish = True
            for image in copied:
                destination = publish / image.name
                with destination.open("xb") as target:
                    owned_files.append(destination)
                    with image.open("rb") as origin:
                        shutil.copyfileobj(origin, target)
            with archive.open("xb") as target:
                owns_archive = True
                with staged_zip.open("rb") as origin:
                    shutil.copyfileobj(origin, target)
        except BaseException:
            if owns_archive:
                archive.unlink(missing_ok=True)
            for path in owned_files:
                path.unlink(missing_ok=True)
            if owns_publish:
                publish.rmdir()  # never recursively remove unowned files
            raise

    print(f"Published {len(copied)} JPG files: {publish}")
    print(f"Created JPG-only ZIP: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
