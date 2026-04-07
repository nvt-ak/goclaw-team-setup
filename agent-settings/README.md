# Agent settings

Canonical location for **template sources** and **per-role rendered** GoClaw context files in a generated team pack.

- `templates/` — source-of-truth markdown templates (skill v12+). Same files may remain mirrored under `references/` during transition; prefer `templates/` for new work.
- `roles/<role-slug>/` — generated outputs only: `AGENTS.md`, `IDENTITY.md`, `SOUL.md`, `USER_PREDEFINED.md` (exactly these four files per role).

See `SKILL.md` §4.2 for the full contract.
