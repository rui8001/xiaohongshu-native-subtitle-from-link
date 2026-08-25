# Xiaohongshu Native Subtitle From Link

An independently installable Codex Skill that turns a public video with burned-in Chinese subtitles into separate 3:4 native-subtitle images and a JPG-only delivery ZIP.

The text always comes from real video frames. The workflow downloads and records the source, confirms visible subtitles, selects complete passages, previews the subtitle band, extracts stable frames, renders contact sheets, performs visual QC, and creates a clean publishing package.

## Install

```bash
git clone https://github.com/rui8001/xiaohongshu-native-subtitle-from-link.git \
  ~/.codex/skills/xiaohongshu-native-subtitle-from-link
python3 -m venv ~/.codex/skills/xiaohongshu-native-subtitle-from-link/.venv
~/.codex/skills/xiaohongshu-native-subtitle-from-link/.venv/bin/pip install \
  -r ~/.codex/skills/xiaohongshu-native-subtitle-from-link/requirements.txt
```

A supplied link defines the requested source but does not prove republication rights. The Skill prepares a draft package and never bypasses access controls or publishes automatically.

See [SKILL.md](./SKILL.md) for the operating contract and [README.md](./README.md) for the full Chinese guide.
