# Implementation Plan: agent-settings contract enforcement

## Scope

Implement the approved design in `docs/superpowers/specs/2026-04-07-agent-settings-contract-design.md` by updating skill contract text, repository structure conventions, and verification artifacts to enforce:

- fixed team settings structure
- `references/` replacement with `agent-settings/`
- canonical per-role file set
- deterministic evidence-gated completion

## Outcomes

- `SKILL.md` reflects the new contract and failure states.
- Team packs generated under the new rules must validate against `verify/structure_conformance.md`, `verify/template_conformance.md`, and `verify/package_manifest.yaml`.
- Migration path from `references/` to `agent-settings/templates/` is explicit and testable.

## Phase 0 - Baseline and safety

1. Capture baseline contract points in current `SKILL.md`:
  - top-level folder contract
  - required artifacts
  - template source paths
  - failure states and completion rules
2. Record intentional behavior changes (breaking vs non-breaking).
3. Define compatibility window for legacy `references/` fallback.

Exit criteria:

- Change log section drafted in this plan and mirrored in implementation PR notes.

## Phase 1 - Contract rewrite in SKILL.md

1. Replace template source-of-truth references:
  - old: `references/goclaw-template-*.md`
  - new: `agent-settings/templates/*.md`
2. Add team settings canonical directories as strict invariants:
  - `config/`, `metrics/`, `policies/`, `runbooks/`, `rules/`, `workflows/`
3. Add agent settings canonical structure:
  - `agent-settings/templates/`
  - `agent-settings/roles/<role-slug>/` with exactly:
    - `AGENTS.md`
    - `IDENTITY.md`
    - `SOUL.md`
    - `USER_PREDEFINED.md`
4. Update Step 3 output contract and template-fill map examples to point to `agent-settings/templates`.
5. Add new deterministic failure states:
  - `FAILED_TEAM_SETTINGS_STRUCTURE`
  - `FAILED_AGENT_SETTINGS_STRUCTURE`
  - `FAILED_ROLE_FILE_SET`
  - `FAILED_TEMPLATE_MAPPING`
  - `FAILED_TEMPLATE_CONFORMANCE`
6. Update failure precedence to include new states in deterministic order.
7. Update `DONE` gating language to require all three verification artifacts.

Exit criteria:

- `SKILL.md` no longer uses `references/` as canonical template source.
- All new invariants are present and non-contradictory.

## Phase 2 - Verification artifact specification updates

1. Extend required artifacts list:
  - include `verify/structure_conformance.md`
  - include `verify/template_conformance.md`
  - keep `verify/package_manifest.yaml`
2. Define machine-checkable schema additions in package manifest:
  - `team_settings.directories_required`
  - `agent_settings.templates_dir`
  - `agent_settings.roles_dir`
  - `agent_settings.required_role_files`
  - `agent_settings.role_slugs_expected`
  - `agent_settings.role_slugs_actual`
  - `agent_settings.role_count_expected`
  - `agent_settings.role_count_actual`
  - `agent_settings.unknown_role_dirs`
  - `template_map` with per-file score metadata
3. Specify conformance checks for:
  - exact role folder/file allowlists
  - no unknown role directories
  - expected/actual role count equality
  - heading order and required section coverage
4. Align tuple freshness requirements across all verify artifacts.

Exit criteria:

- Verification section defines deterministic pass/fail with no implicit/manual interpretation.

## Phase 3 - Migration policy and backward compatibility

1. Add migration policy text:
  - new generation uses `agent-settings/templates/` only.
  - temporary read-only fallback from `references/` is allowed if templates are missing.
2. Require all rendered role outputs under `agent-settings/roles/` even during fallback.
3. Mark legacy packs as non-DONE unless regenerated under new contract.
4. Define sunset condition to remove fallback.

Exit criteria:

- Migration path is explicit and includes termination criteria for fallback.

## Phase 4 - Repository structure alignment (non-runtime content)

1. Add/adjust repository docs to reflect rename:
  - update `README.md`
  - update `references/README.md` (or move to `agent-settings/README.md` if directory migration is executed in this phase)
2. If directory migration is executed now:
  - create `agent-settings/templates/` and copy canonical templates
  - retain `references/` only as legacy alias during transition
3. Ensure no contradictory guidance remains in docs.

Exit criteria:

- Human-facing docs align with contract language in `SKILL.md`.

## Phase 5 - Test and verification protocol

1. Create a synthetic 3-role sample for contract validation:
  - role slugs: `a`, `b`, `c`
  - ensure each role folder has exact 4 canonical files
2. Run structure verification and capture artifact output.
3. Run template conformance verification and capture mismatch-free output.
4. Validate package manifest schema and set-equality checks.
5. Negative tests:
  - remove one required role file -> expect `FAILED_ROLE_FILE_SET`
  - add unknown role folder -> expect failure
  - break heading order -> expect `FAILED_TEMPLATE_CONFORMANCE`

Exit criteria:

- Positive path passes all gates.
- Negative paths fail with deterministic expected states.

## Phase 6 - Rollout and acceptance

1. Publish contract update with short migration notes.
2. Mark old references-based contract as deprecated.
3. Require new verify artifacts for all future generated packs.

Acceptance checklist:

- Team settings canonical directories enforced
- Agent settings structure enforced
- Role file set exactness enforced
- Template mapping + heading conformance enforced
- DONE blocked without mandatory verify artifacts
- Migration/backward compatibility policy documented

## Risks and mitigations

- Risk: Existing automation still writes to `references/`
  - Mitigation: transitional fallback + explicit warning + sunset date.
- Risk: Partial contract update causes internal contradictions in `SKILL.md`
  - Mitigation: single-pass consistency review of folder names, artifact names, and failure states.
- Risk: Overly strict checks block legitimate edge-cases
  - Mitigation: keep allowlist explicit and versioned; add contract version bump notes.

## Execution order recommendation

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5
6. Phase 6

This order minimizes inconsistencies by locking policy before docs and testing.