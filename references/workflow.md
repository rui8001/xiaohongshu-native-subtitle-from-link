# Link-to-native-subtitle workflow

## 1. Acquire and record

Run `scripts/fetch_source VIDEO_URL WORK_ROOT`. It downloads one public video, info JSON, and available subtitle tracks without overwriting existing files.

Create a new task directory under the selected output root. Record original URL, video ID, title, source account, program, speakers, download date, local filename, and source resolution. If ordinary public access fails, request a local upload; never bypass login, payment, or access controls.

## 2. Confirm visible subtitles

Inspect representative frames from the beginning, middle, and end. External subtitle tracks are only a navigation aid; the visible burned-in subtitle is the source of truth.

Convert JSON3 when available:

```bash
python3 "<SKILL_DIR>/scripts/json3_to_timeline.py" INPUT.json3 OUTPUT.md
```

## 3. Select complete passages

For each candidate, record title, start/end, one-sentence meaning, inclusion reason, and excluded-topic check. Preserve premise, contrast, cause, and conclusion. Do not join unrelated moments.

## 4. Preview the native subtitle band

```bash
python3 "<SKILL_DIR>/scripts/native_subtitle_stitch.py" band VIDEO -t TIME \
  --band-top 0.68 --band-bottom 0.96 \
  --crop-left 0.00 --crop-right 1.00 --out band-preview.jpg
```

The red rectangle is only a preview guide. Adjust the band and horizontal crop until it contains the complete visible subtitle and excludes avoidable marks.

## 5. Create a manifest and render

Create one manifest item per complete passage. Use stable, distinct captions in increasing time order:

```json
{
  "images": [
    {
      "title": "A short complete idea",
      "times": [12.4, 15.1, 18.0, 21.3, 24.8, 28.2]
    }
  ]
}
```

Render each revision into a new directory:

```bash
python3 "<SKILL_DIR>/scripts/native_subtitle_stitch.py" render VIDEO \
  --manifest manifest.json --out-dir OUTPUT \
  --aspect 3:4 --width 1440 \
  --band-top 0.68 --band-bottom 0.96 \
  --crop-left 0.00 --crop-right 1.00 --strip-height 160
```

Inspect every numbered JPG and the contact sheet for semantic completeness, subtitle integrity, duplicate text, transition residue, marks, face crops, borders, spacing, and 1440×1920 dimensions. Re-render a failed item after changing only its timestamps, subtitle region, crop, or strip height.

## 6. Package

Keep contact sheets, crop previews, and the final manifest as QC material. Package only numbered JPGs:

```bash
python3 "<SKILL_DIR>/scripts/package_publish_images.py" \
  RENDER_DIR PUBLISH_DIR PUBLISH.zip
```

Also deliver source record, candidate notes, title/body draft, and checklist. Default to a draft and never publish automatically.
