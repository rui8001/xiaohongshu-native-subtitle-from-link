"""Publish safety regressions using generated images, never private media."""
import argparse
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image

SPEC = importlib.util.spec_from_file_location(
    "packager", Path(__file__).resolve().parents[1] / "scripts/package_publish_images.py")
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class PackagerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "render"
        self.source.mkdir()
        self.publish = self.root / "publish"
        self.archive = self.root / "publish.zip"
        Image.new("RGB", (12, 16), "blue").save(self.source / "01_first.jpg")

    def run_package(self):
        args = argparse.Namespace(source=self.source, publish=self.publish, archive=self.archive)
        with patch.object(packager, "parse_args", return_value=args):
            return packager.main()

    def assert_no_outputs(self):
        self.assertFalse(self.publish.exists())
        self.assertFalse(self.archive.exists())

    def test_success_only_numbered_jpegs_in_numeric_order(self):
        for name in ("99_last.jpg", "100_more.jpg", "contact_sheet.jpg"):
            Image.new("RGB", (12, 16), "red").save(self.source / name)
        self.assertEqual(self.run_package(), 0)
        with zipfile.ZipFile(self.archive) as archive:
            self.assertEqual(archive.namelist(), ["01_first.jpg", "99_last.jpg", "100_more.jpg"])
            self.assertIsNone(archive.testzip())
            for name in archive.namelist():
                self.assertEqual(archive.read(name), (self.source / name).read_bytes())

    def test_copy_failure_leaves_no_outputs_and_retry_succeeds(self):
        with patch.object(packager.shutil, "copy2", side_effect=OSError("synthetic copy failure")):
            with self.assertRaises(OSError):
                self.run_package()
        self.assert_no_outputs()
        self.assertEqual(self.run_package(), 0)

    def test_zip_failure_leaves_no_outputs(self):
        with patch.object(packager.zipfile.ZipFile, "write", side_effect=OSError("synthetic ZIP failure")):
            with self.assertRaises(OSError):
                self.run_package()
        self.assert_no_outputs()

    def test_existing_outputs_are_preserved(self):
        self.archive.write_bytes(b"keep")
        with self.assertRaises(SystemExit):
            self.run_package()
        self.assertEqual(self.archive.read_bytes(), b"keep")
        self.assertFalse(self.publish.exists())

    def test_symlink_source_is_rejected(self):
        (self.source / "02_link.jpg").symlink_to(self.source / "01_first.jpg")
        with self.assertRaises(SystemExit):
            self.run_package()
        self.assert_no_outputs()

    def test_corrupt_jpeg_is_rejected_before_publication(self):
        (self.source / "02_invalid.jpg").write_bytes(b"not an image")
        with self.assertRaises(SystemExit):
            self.run_package()
        self.assert_no_outputs()

    def test_dangling_output_symlink_is_preserved(self):
        target = self.root / "missing"
        self.publish.symlink_to(target, target_is_directory=True)
        with self.assertRaises(SystemExit):
            self.run_package()
        self.assertTrue(self.publish.is_symlink())
        self.assertFalse(target.exists())
        self.assertFalse(self.archive.exists())

    def test_zip_cannot_be_inside_publish_directory(self):
        self.archive = self.publish / "images.zip"
        with self.assertRaises(SystemExit):
            self.run_package()
        self.assert_no_outputs()

    def test_final_publication_failure_rolls_back_owned_files(self):
        original = packager.shutil.copyfileobj
        def fail_on_archive(source, target, *args):
            name = getattr(target, "name", None)
            if isinstance(name, str) and Path(name).resolve() == self.archive.resolve():
                target.write(b"partial")
                raise OSError("synthetic final ZIP copy failure")
            return original(source, target, *args)
        with patch.object(packager.shutil, "copyfileobj", side_effect=fail_on_archive):
            with self.assertRaises(OSError):
                self.run_package()
        self.assert_no_outputs()

    def test_archive_created_during_staging_is_not_overwritten(self):
        original = packager.shutil.copy2
        def concurrent_output(*args, **kwargs):
            result = original(*args, **kwargs)
            self.archive.write_bytes(b"other process")
            return result
        with patch.object(packager.shutil, "copy2", side_effect=concurrent_output):
            with self.assertRaises(FileExistsError):
                self.run_package()
        self.assertFalse(self.publish.exists())
        self.assertEqual(self.archive.read_bytes(), b"other process")


if __name__ == "__main__":
    unittest.main()
