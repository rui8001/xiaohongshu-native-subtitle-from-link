# Release checklist

1. Confirm the release contains no downloaded video, real output image, cookie, account data, personal path, or restricted source.
2. Run the official Skill validator against the repository root.
3. Parse YAML and JSON, compile every Python script, and run `zsh -n scripts/fetch_source`.
4. Generate a synthetic video, run timeline conversion, band preview, rendering, contact-sheet creation, and JPG-only packaging.
5. Verify output dimensions and ZIP entries, then visually inspect the synthetic result and both SVG assets.
6. Review `git diff`, run the secret scan, and update `CHANGELOG.md`.
7. Commit with the public no-reply author, create an annotated `vX.Y.Z` tag, and publish release notes from the changelog.
8. Install dependencies in a clean environment and verify the workflow from a fresh clone.
