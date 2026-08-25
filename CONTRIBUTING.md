# Contributing

Issues and pull requests are welcome when they improve the reusable native-subtitle workflow without importing real production content.

Before submitting:

1. Preserve real burned-in subtitles; do not add subtitle redrawing, translation, or synthetic replacement.
2. Use synthetic test media and remove personal, account, source, and production data.
3. Keep downloader behavior within ordinary public access and never add access-control bypasses.
4. Keep outputs non-destructive: no overwriting of sources, accepted renders, or packages.
5. Run the official Skill validator, script syntax checks, synthetic rendering test, and secret scan.
6. Document user-visible changes in `CHANGELOG.md`.
