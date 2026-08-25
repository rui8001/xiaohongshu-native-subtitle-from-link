---
name: xiaohongshu-native-subtitle-from-link
description: Download a user-provided public video link, identify complete growth, learning, motivation, or reflection passages, and produce separate Xiaohongshu-ready native-subtitle images plus a JPG-only ZIP. Use when the user supplies a link or asks for this established link-to-images workflow; do not use when the video lacks burned-in Chinese subtitles.
---

# Xiaohongshu Native Subtitle From Link

Resolve `<SKILL_DIR>` as this Skill's directory. Read [references/workflow.md](references/workflow.md) before processing a link.

The user's link places that source in the task scope but does not prove publication rights. Record the source and prepare a draft package only; do not log in or publish.

Use `<WORK_ROOT>` as the user's specified project or the current workspace. If it already contains `素材/` and `输出/`, preserve that layout. Otherwise use `materials/` and `outputs/`.

## Entries

- Download: `<SKILL_DIR>/scripts/fetch_source`
- JSON3 timeline: `<SKILL_DIR>/scripts/json3_to_timeline.py`
- Band preview and rendering: `<SKILL_DIR>/scripts/native_subtitle_stitch.py`
- JPG-only package: `<SKILL_DIR>/scripts/package_publish_images.py`

Create each task in a new dated output directory. Never overwrite source files, manifests, renders, accepted images, or delivery packages.

Select complete passages about growth, learning, motivation, creativity, action, choices, habits, work methods, or general life experience. Exclude politics, gender disputes, climate/environment, health, illness, medicine, and treatment. If an excluded subject cannot be separated without changing the meaning, reject the passage.

For every candidate, preserve its premise, contrast, cause, and conclusion. One complete candidate becomes one independent JPG; the result count is not fixed. The final words must come from visible video frames. Never translate, rewrite, redraw, blur over, or cover the native subtitles.

Preview the real subtitle band before rendering. Prefer the stable middle of each caption, choose distinct frames in increasing time order, and avoid empty captions, repeated text, transitions, black borders, awkward face crops, watermarks, QR codes, name straps, logos, and unrelated brands. Remove marks only by choosing another frame or changing the crop.

Inspect every numbered JPG and the contact sheet. A result is complete only when each numbered file independently expresses one coherent passage, preserves the original subtitles, matches the requested dimensions, and passes subtitle, subject, border, mark, and spacing checks.

Report candidate themes as progress, then continue with all qualified candidates unless the user asked to choose first. Stop only when the public link cannot be accessed normally, the video has no burned-in Chinese subtitles, the source is unreadable, or the entire video has no qualified complete passage. Never bypass access controls or fabricate native subtitles.
