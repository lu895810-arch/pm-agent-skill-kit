## Vendor Dependencies

This directory contains vendored runtime dependencies embedded into this skill.

### 1. `pyJianYingDraft/`
- **Upstream Repository**: [https://github.com/GuanYixuan/pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft)
- **Original Author**: GuanYixuan (管奕轩)
- **License**: [Apache License 2.0](pyJianYingDraft/LICENSE) (Copyright 2024 GuanYixuan)
- **Local Modifications & Patches** (compliant with Apache-2.0 Section 4(b)):
  - **Modern Draft Specification (5.9+)**: Adapted material identifiers and draft format to support JianYing Pro 5.9+ / 6.x+ `draft_info.json`.
  - **Asset Self-Containment**: Enhanced `local_materials.py` to generate stable `local_material_id` based on asset stem names, preventing media-missing errors on imported clips.
  - **Cross-Platform & Headless Fallbacks**: Added `ffprobe` probing fallback when `pymediainfo` is not present, and normalized media geometry.
  - **macOS Staging Support**: Integrated with draft-internal staging to resolve App Sandbox permission restrictions.

Guidelines:
- Keep upstream structure intact to simplify future sync.
- Prefer `git mv` for relocations to preserve history.
- Local patches are maintained specifically for AI Agent automation and cross-platform reliability.
