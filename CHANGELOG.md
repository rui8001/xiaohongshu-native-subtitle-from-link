# Changelog

## [Unreleased]

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
