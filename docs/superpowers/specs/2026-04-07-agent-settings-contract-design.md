---
title: Agent settings contract (references -> agent-settings)
date: 2026-04-07
status: approved (design)
repo: goclaw-team-setup
approach: Approach 2 (contract + verifier artifact gate)
---

## Summary

We will harden GoClaw team-pack generation by separating:

- **Team settings**: a fixed directory contract that must be identical for every generated team pack.
- **Agent settings**: a template-driven, per-role context pack that must match canonical filenames and template structure.

The system becomes evidence-gated: an agent may not claim `DONE` unless machine-checkable manifests and human-readable verification artifacts prove conformance.

## Goals

- Make structure and template conformance **deterministic** and **verifiable**.
- Eliminate drift in folder/file names by enforcing **canonical naming**.
- Keep content flexible per team composition while keeping structure fixed.
- Make failures explicit with deterministic failure states (no ambiguous "almost done").

## Non-goals

- Designing new role content templates beyond the current four role templates.
- Changing the core generation state machine order (no skipping states).
- Adding new runtime packager behavior beyond the existing "exclude templates by default" invariant unless explicitly specified by the packaging manifest.

## Canonical naming decisions

Canonical filenames and folder naming MUST use:

- `AGENTS.md`
- `IDENTITY.md`
- `SOUL.md`
- `USER_PREDEFINED.md`
- `agent-settings/` (new canonical name; replaces `references/` as source-of-truth for templates)

## Section 1 — Folder contract (canonical structure)

### 1.1 Team settings (fixed structure)

The following directories are **team settings** and MUST exist in every generated team-pack root with these exact names:

- `config/`
- `metrics/`
- `policies/`
- `runbooks/`
- `rules/`
- `workflows/`

Rules:

- The structure (presence and directory names) is **non-negotiable**.
- Content inside these directories is flexible and is generated based on the researched team type and role composition.

### 1.2 Agent settings (templates + role outputs)

`agent-settings/` is the canonical location for template sources and per-role rendered context packs.

Canonical structure:

- `agent-settings/templates/`
  - Holds canonical templates (migrated from the old `references/` directory).
- `agent-settings/roles/<role-slug>/`
  - One directory per role.
  - Each role directory MUST contain exactly these four files:
    - `AGENTS.md`
    - `IDENTITY.md`
    - `SOUL.md`
    - `USER_PREDEFINED.md`

Rules:

- Role directory name MUST be a deterministic, normalized kebab-case slug derived from `research/role-matrix.yaml`.
- No extra files are permitted in `agent-settings/roles/<role-slug>/` unless explicitly allowlisted by this contract (currently none).
- Agents must render role files using **template-first** rules: headings and ordering must match the template.

## Section 2 — Evidence-gated verification contract

### 2.1 Verification artifacts (mandatory)

The following verification artifacts MUST be produced for every generation run:

1. `verify/structure_conformance.md`
2. `verify/template_conformance.md`
3. `verify/package_manifest.yaml`

If any of the above is missing, generation MUST fail and may not claim `DONE`.

### 2.2 `verify/structure_conformance.md` requirements

This artifact must prove the filesystem contract:

- Team settings directories exist exactly as declared:
  - `config/`, `metrics/`, `policies/`, `runbooks/`, `rules/`, `workflows/`
- Template directory exists:
  - `agent-settings/templates/`
- Role directories match the role plan:
  - Every role in `research/role-matrix.yaml` has exactly one matching directory in `agent-settings/roles/`.
  - There are no unknown role directories beyond the role slug set.
- Each role directory contains **exactly**:
  - `AGENTS.md`, `IDENTITY.md`, `SOUL.md`, `USER_PREDEFINED.md`
  - No extra files.

### 2.3 `verify/template_conformance.md` requirements

This artifact must prove template adherence:

- For every role and for every canonical role file:
  - the file maps to a template in `agent-settings/templates/`
  - required headings exist
  - heading order matches template order
  - a score is computed (per file and global) plus a mismatch report

The verification must NOT be "self-reported". It must be reproducible from the template + rendered output.

### 2.4 `verify/package_manifest.yaml` requirements (machine-checkable)

This manifest is the primary machine-readable contract for packaging and conformance.

Minimum schema (proposed; exact field names must be frozen in SKILL + verifier):

- `generation_id` (string)
- `generated_at` (RFC3339 UTC)
- `commit_sha` (40-char git SHA)
- `layout_directories_required` (array of strings)
  - MUST include team settings directories and `agent-settings/` and other required pack directories.
- `team_settings`
  - `directories_required` (array): exactly the six team settings directories (same names as Section 1.1)
- `agent_settings`
  - `templates_dir` (string): `agent-settings/templates`
  - `roles_dir` (string): `agent-settings/roles`
  - `required_role_files` (array of strings): exactly the four canonical files
  - `role_slugs_expected` (array of strings): derived from `research/role-matrix.yaml`
  - `role_slugs_actual` (array of strings): derived from filesystem
  - `role_count_expected` (int)
  - `role_count_actual` (int)
  - `unknown_role_dirs` (array of strings)
- `template_map` (object)
  - Keys: `<role-slug>/<file>` (e.g. `platform-engineer/AGENTS.md`)
  - Values:
    - `template_path` (string): path under `agent-settings/templates/`
    - `required_headings` (array of strings)
    - `matched_headings` (array of strings)
    - `structure_match_score` (number in [0,1])

Gates:

- `role_slugs_expected` set MUST equal `role_slugs_actual` set (after normalization and sorting).
- `role_count_expected == role_count_actual`.
- `unknown_role_dirs` MUST be empty.
- `required_role_files` MUST match exactly the role folder contents for every role.
- Any mismatch forces a deterministic failure state.

### 2.5 Deterministic failure states (additions)

Add the following deterministic failure tokens:

- `FAILED_TEAM_SETTINGS_STRUCTURE`
- `FAILED_AGENT_SETTINGS_STRUCTURE`
- `FAILED_ROLE_FILE_SET`
- `FAILED_TEMPLATE_MAPPING`
- `FAILED_TEMPLATE_CONFORMANCE`

Mapping (first-match-wins precedence for VERIFY failures):

1. Missing required directories/files in team settings -> `FAILED_TEAM_SETTINGS_STRUCTURE`
2. Missing `agent-settings/templates` or `agent-settings/roles` -> `FAILED_AGENT_SETTINGS_STRUCTURE`
3. Role folder exists but required file set mismatch -> `FAILED_ROLE_FILE_SET`
4. Template mapping missing for any role-file -> `FAILED_TEMPLATE_MAPPING`
5. Template headings/order mismatch beyond threshold -> `FAILED_TEMPLATE_CONFORMANCE`

## Section 3 — State machine updates + migration strategy

### 3.1 State machine (no skipping)

Keep canonical sequence:

`INTAKE -> TEAM_RESEARCH -> ROLE_PLANNING -> ROLE_RESEARCH -> ROLE_RENDER -> TEAM_MODELING -> VERIFY -> PACKAGE -> DONE`

New hard requirements:

- `ROLE_RENDER` exit gate requires:
  - rendered outputs exist under `agent-settings/roles/<role-slug>/`
  - template map can be generated for every role-file
- `VERIFY` exit gate requires the three artifacts in Section 2.1.
- `DONE` is forbidden unless all `VERIFY` gates pass.

### 3.2 Migration: `references/` -> `agent-settings/`

Source-of-truth changes:

- Templates MUST live in `agent-settings/templates/`.
- The old `references/` directory becomes legacy and must not be used as the long-term source-of-truth.

Transition period (optional but recommended):

- Allow a temporary read-only fallback: if `agent-settings/templates/` is missing, the system MAY read from `references/` to populate templates.
- Even during fallback, outputs MUST be written to `agent-settings/roles/...` and verification MUST validate `agent-settings/`.

End state:

- Remove fallback.
- `references/` is either removed from runtime or remains as internal legacy only, but it is not referenced by contract or verifier.

### 3.3 Backward compatibility policy

- Packs generated under the old contract are "legacy".
- Only packs generated under this new contract may reach `DONE`.
- If a legacy pack is regenerated, it MUST be upgraded to the `agent-settings/` contract.

### 3.4 Guardrails (anti-drift)

- Role slug validator: only kebab-case allowed; invalid slugs fail `FAILED_AGENT_SETTINGS_STRUCTURE`.
- Role folder allowlist: only directories in `role_slugs_expected` may exist under `agent-settings/roles/`.
- Role file allowlist: exactly four canonical files; any extra file fails `FAILED_ROLE_FILE_SET`.
- Template conformance validator:
  - heading extraction from templates
  - exact ordered match rules
  - per-file score calculation and global threshold

## Open questions (none)

All naming, structure, and evidence gates were approved during brainstorming.

