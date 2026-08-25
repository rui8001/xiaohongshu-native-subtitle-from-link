#!/usr/bin/env python3
"""Convert a yt-dlp JSON3 subtitle file into a compact Markdown timeline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NON_SPEECH = re.compile(
    r"^\s*[\[（(].*(music|applause|laughter|音乐|掌声|笑声).*[\]）)]\s*$",
    re.IGNORECASE,
)


def format_time(milliseconds: int) -> str:
    seconds, millis = divmod(max(0, milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"
    return f"{minutes:02d}:{seconds:02d}.{millis:03d}"


def event_text(event: dict) -> str:
    text = "".join(segment.get("utf8", "") for segment in event.get("segs", []))
    return " ".join(text.replace("\n", " ").split())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input .json3 file")
    parser.add_argument("output", type=Path, help="New output .md file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        raise SystemExit(f"Subtitle file does not exist: {args.input}")
    if args.output.exists():
        raise SystemExit(f"Output already exists: {args.output}")

    with args.input.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    lines = [f"# Subtitle timeline: {args.input.name}", ""]
    previous_text = ""
    cue_count = 0
    for event in payload.get("events", []):
        text = event_text(event)
        if not text or text == previous_text or NON_SPEECH.match(text):
            continue
        start = int(event.get("tStartMs", 0))
        end = start + int(event.get("dDurationMs", 0))
        lines.append(f"- `{format_time(start)}–{format_time(end)}` {text}")
        previous_text = text
        cue_count += 1

    if cue_count == 0:
        raise SystemExit("No usable subtitle events")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {cue_count} subtitle cues: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
