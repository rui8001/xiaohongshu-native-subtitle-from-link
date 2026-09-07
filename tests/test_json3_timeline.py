"""JSON3 boundary regressions using synthetic captions only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/json3_to_timeline.py"


def cue(**changes):
    value = {"tStartMs": 2400, "dDurationMs": 2200, "segs": [{"utf8": "Synthetic caption"}]}
    value.update(changes)
    return value


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "input.json3"
        self.output = self.root / "result" / "timeline.md"
        self.case_number = 0

    def run_payload(self, payload):
        self.source.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(self.source), str(self.output)],
                              capture_output=True, text=True)

    def assert_rejected(self, payload):
        self.case_number += 1
        self.output = self.root / f"result-{self.case_number}" / "timeline.md"
        result = self.run_payload(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn("Synthetic caption", result.stderr)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.output.parent.exists())

    def test_valid_captions_metadata_and_noise(self):
        result = self.run_payload({"events": [{"id": 1}, cue(segs=[]),
            cue(segs=[{"utf8": "[Music]"}]), cue(), cue(),
            cue(tStartMs=3600123, segs=[{"utf8": "Second\n"}, {"utf8": "caption"}])]})
        self.assertEqual(result.returncode, 0, result.stderr)
        content = self.output.read_text(encoding="utf-8")
        self.assertIn("`00:02.400–00:04.600` Synthetic caption", content)
        self.assertIn("`01:00:00.123–01:00:02.323` Second caption", content)
        self.assertEqual(content.count("\n- "), 2)

    def test_invalid_container_shapes(self):
        for payload in [None, [], {}, {"events": None}, {"events": {}},
                        {"events": [None]}, {"events": ["caption"]}]:
            with self.subTest(payload=payload):
                self.assert_rejected(payload)

    def test_invalid_segments(self):
        for segments in [None, {}, "caption", [None], ["caption"], [{"utf8": 1}], [{"utf8": None}]]:
            with self.subTest(segments=segments):
                self.assert_rejected({"events": [cue(segs=segments)]})

    def test_invalid_times_even_in_duplicate_caption(self):
        for field in ["tStartMs", "dDurationMs"]:
            for value in [-1, True, False, None, "2400", 1.5, float("nan"), float("inf")]:
                with self.subTest(field=field, value=value):
                    self.assert_rejected({"events": [cue(), cue(**{field: value})]})

    def test_missing_caption_times(self):
        for field in ["tStartMs", "dDurationMs"]:
            event = cue()
            del event[field]
            with self.subTest(field=field):
                self.assert_rejected({"events": [event]})

    def test_zero_times_supported(self):
        result = self.run_payload({"events": [cue(tStartMs=0, dDurationMs=0)]})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("`00:00.000–00:00.000`", self.output.read_text())

    def test_empty_timeline_rejected(self):
        for events in [[], [{"id": 1}], [cue(segs=[{"utf8": "[掌声]"}])]]:
            with self.subTest(events=events):
                self.assert_rejected({"events": events})

    def test_malformed_json_has_no_traceback(self):
        self.source.write_text('{"events":', encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.source), str(self.output)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.output.parent.exists())

    def test_existing_output_preserved(self):
        self.output.parent.mkdir()
        self.output.write_text("original")
        result = self.run_payload({"events": [cue()]})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_text(), "original")
