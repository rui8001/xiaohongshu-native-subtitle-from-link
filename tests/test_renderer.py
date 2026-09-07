"""Synthetic rendering and failure-boundary regressions; no downloaded media."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import imageio_ffmpeg
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("renderer", ROOT / "scripts/native_subtitle_stitch.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(json.dumps({"images": [{"title": "synthetic", "times": [0, 1]}]}))
        self.args = argparse.Namespace(video=self.root / "source.mp4", manifest=self.manifest,
            out_dir=self.root / "render", aspect=(3, 4), width=1440, band_top=.68,
            band_bottom=.96, crop_left=0, crop_right=1, hero_fraction=.42, strip_height=160)

    def test_existing_output_is_untouched(self):
        self.args.out_dir.mkdir()
        sentinel = self.args.out_dir / "01_synthetic.jpg"
        sentinel.write_bytes(b"original")
        with self.assertRaises(SystemExit):
            renderer.command_render(self.args)
        self.assertEqual(sentinel.read_bytes(), b"original")

    def test_invalid_late_item_leaves_no_output(self):
        self.manifest.write_text(json.dumps({"images": [{"times": [0, 1]}, {"times": [2, 1]}]}))
        with patch.object(renderer, "grab_frame") as grab:
            with self.assertRaises(SystemExit):
                renderer.command_render(self.args)
            grab.assert_not_called()
        self.assertFalse(self.args.out_dir.exists())

    def test_nonfinite_negative_and_boolean_times_rejected(self):
        for value in [float("nan"), float("inf"), -1, True, "1"]:
            with self.subTest(value=value):
                self.manifest.write_text(json.dumps({"images": [{"times": [0, value]}]}))
                with self.assertRaises(SystemExit):
                    renderer.command_render(self.args)
                self.assertFalse(self.args.out_dir.exists())

    def test_decode_failure_does_not_publish_partial_batch(self):
        self.manifest.write_text(json.dumps({"images": [{"times": [0, 1]}, {"times": [2, 3]}]}))
        with patch.object(renderer, "grab_frame", side_effect=[Image.new("RGB", (640,360)),
                Image.new("RGB", (640,360)), RuntimeError("synthetic decode failure")]):
            with self.assertRaises(RuntimeError):
                renderer.command_render(self.args)
        self.assertFalse(self.args.out_dir.exists())
        self.assertEqual(list(self.root.glob(".subtitle-render-*")), [])

    def test_real_ffmpeg_render_and_jpg_only_package(self):
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-f", "lavfi", "-i",
            "testsrc2=duration=3:size=640x360:rate=5", "-c:v", "libx264", str(self.args.video)], check=True)
        renderer.command_render(self.args)
        with Image.open(self.args.out_dir / "01_synthetic.jpg") as image:
            self.assertEqual(image.size, (1440, 1920))
        publish = self.root / "publish"
        command = [sys.executable, str(ROOT / "scripts/package_publish_images.py"), str(self.args.out_dir), str(publish)]
        subprocess.run(command, check=True)
        with zipfile.ZipFile(self.root / "publish.zip") as archive:
            self.assertEqual(archive.namelist(), ["01_synthetic.jpg"])
            self.assertIsNone(archive.testzip())
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_aspect_rejects_nan_and_infinity(self):
        for value in ["nan:4", "3:inf", "0:4"]:
            with self.assertRaises(argparse.ArgumentTypeError):
                renderer.parse_aspect(value)


if __name__ == "__main__":
    unittest.main()
