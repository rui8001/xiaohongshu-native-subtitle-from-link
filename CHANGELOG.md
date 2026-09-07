# Changelog

## [Unreleased]

- Validate JSON3 containers, caption segments and integer timestamps before writing a timeline; malformed captions fail clearly without publishing a partial timeline or echoing caption text.
- Add nine synthetic JSON3 regression tests covering invalid shapes, missing/negative/non-finite/boolean times, duplicates, metadata events and valid formatting.
- Stage and validate JPEGs and ZIP before publication; clean up owned outputs on ordinary write failures without overwriting existing files.
- Reject symlink/non-JPEG inputs and overlapping output paths; include images numbered 100 and above in numeric order.
- Add ten focused packager regressions, including retry after failure and a concurrently created ZIP.
- Refuse existing render/preview outputs and validate every manifest item before rendering.
- Publish only complete rendered batches; failed decodes no longer leave partial output.
- Reject non-finite, negative, boolean and nonnumeric timestamps.
- Add six renderer/package regressions and public repository quality CI using synthetic media only.

## [0.1.0] - 2026-08-25

### Added

- One independently installable link-to-native-subtitle Skill.
- Public-source acquisition, JSON3 timeline, native-frame renderer, contact-sheet QC, and JPG-only packager.
- Integrated the renderer that previously required a second Skill.
- Synthetic manifest and subtitle-timeline examples.
- Project homepage, artwork, contributor guide, security policy, and issue templates.
