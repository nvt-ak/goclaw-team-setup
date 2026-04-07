# goclaw-team-setup

Candidate bundle để anh test nhanh.

## Included

- SKILL.md (patched, v12+)
- `agent-settings/templates/` — canonical role context templates
- config/, metrics/, policies/, runbooks/, workflows/, roles/
- `scripts/` — `verify_team_pack.py` (needs `pip install -r scripts/requirements-verify.txt`)

## Notes

- Runtime package mặc định exclude nguồn template (`agent-settings/templates/`) theo `verify/package_manifest.yaml` → `excludes_references: true`.
- Bundle này dùng để review logic skill và tái đóng gói thử nghiệm.
