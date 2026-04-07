---

## name: GoClaw Team Setup  
description: Deterministic operational contract for team setup, role research, role rendering, team model synthesis, and evidence-gated completion.  
version: v13git s  
language: en

# GoClaw Team Setup

## 1. Metadata and Purpose

Purpose: execute a strict, deterministic team-setup workflow that is research-first, template-conformant, role-deep, and evidence-gated.

Applies when user requests setup/regeneration of a GoClaw team pack with roles, governance, workflows, policies, runbooks, metrics, and verification artifacts.

Core invariants:

- `team_roles == raci_roles == acl_roles == workflow_roles` (set equality on normalized slugs; see §4 schema)
- Runtime package excludes template sources by default: `agent-settings/templates/` (see `verify/package_manifest.yaml` field `exclude_template_sources`)
- Per-role GoClaw context files live under `agent-settings/roles/<role-slug>/` (exactly four canonical files; see §4)
- Per-role `HEARTBEAT.md` lives under `roles/<role-slug>/` (not under `agent-settings/roles/`)
- No role content may drift outside declared `team_type`
- No completion by intent text; completion by artifact evidence only

## 2. Execution Model (State Machine)

Canonical sequence:
`INTAKE -> TEAM_RESEARCH -> ROLE_PLANNING -> ROLE_RESEARCH -> ROLE_RENDER -> TEAM_MODELING -> VERIFY -> PACKAGE -> DONE`

State transition rules:

- No state skipping.
- Each state requires explicit entry prerequisites and exit gates.
- Any failed gate maps to one deterministic blocked/failed state.
- Failure resolution is `first-match-wins` using the precedence table below.

Deterministic failure precedence (evaluate top to bottom, stop on first match):


| Precedence | Condition (first true wins)                                                                                               | State                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| 1          | Required input missing/empty at intake                                                                                    | `BLOCKED_INPUT_MISSING`           |
| 2          | Any required research artifact missing/incomplete                                                                         | `BLOCKED_INCOMPLETE_RESEARCH`     |
| 3          | Team settings directory contract violation (§4.1)                                                                         | `FAILED_TEAM_SETTINGS_STRUCTURE`  |
| 4          | `agent-settings/` directory contract violation (§4.2)                                                                     | `FAILED_AGENT_SETTINGS_STRUCTURE` |
| 5          | `agent-settings/roles/<slug>/` file set not exactly the four canonical files                                              | `FAILED_ROLE_FILE_SET`            |
| 6          | `research/template-fill-map.yaml` or `verify/package_manifest.yaml` `template_map` missing any required role-file mapping | `FAILED_TEMPLATE_MAPPING`         |
| 7          | Any required template heading/order mismatch (role template files)                                                        | `FAILED_TEMPLATE_CONFORMANCE`     |
| 8          | Any role-depth score below threshold or generic critical-section content detected                                         | `FAILED_ROLE_DEPTH`               |
| 9          | Cross-layer ownership/actor/responder inconsistency                                                                       | `FAILED_TEAM_MODEL_CONSISTENCY`   |
| 10         | Malformed or empty artifact layout (including literal brace directories) not covered above                                | `FAILED_ARTIFACT_LAYOUT`          |
| 11         | Verification evidence missing/stale/incoherent for current generation window                                              | `BLOCKED_NO_EVIDENCE`             |


Deterministic failure states:

- `BLOCKED_INPUT_MISSING`
- `BLOCKED_INCOMPLETE_RESEARCH`
- `FAILED_TEAM_SETTINGS_STRUCTURE`
- `FAILED_AGENT_SETTINGS_STRUCTURE`
- `FAILED_ROLE_FILE_SET`
- `FAILED_TEMPLATE_MAPPING`
- `FAILED_TEMPLATE_CONFORMANCE`
- `FAILED_ROLE_DEPTH`
- `FAILED_TEAM_MODEL_CONSISTENCY`
- `FAILED_ARTIFACT_LAYOUT`
- `BLOCKED_NO_EVIDENCE`

## 3. Mandatory Step Contracts (4 Steps)

Role slug naming contract:

- All role-derived names (file names, IDs, workflow actor labels, metric owner keys) use deterministic lowercase kebab-case slug normalization.
- Normalize by: trim -> lowercase -> replace spaces/underscores with `-` -> collapse repeated `-` -> remove non `[a-z0-9-]` -> trim `-`.
- `research/role-<role-name>.md` uses `<role-name>` as normalized slug.

Canonical state gate contracts:


| State           | Entry prerequisites                          | Exit gate                                                                                                         |
| --------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `INTAKE`        | `team_type`, objective, constraints provided | Inputs complete and non-empty; else `BLOCKED_INPUT_MISSING`                                                       |
| `TEAM_RESEARCH` | `INTAKE` passed                              | `research/team-architecture.md` exists and includes required subsections                                          |
| `ROLE_PLANNING` | `TEAM_RESEARCH` passed                       | `research/role-matrix.yaml` valid with required per-role fields                                                   |
| `ROLE_RESEARCH` | `ROLE_PLANNING` passed                       | `research/role-<slug>.md` exists for every planned role                                                           |
| `ROLE_RENDER`   | `ROLE_RESEARCH` passed                       | All outputs in §4.2–§4.3 exist per role; `research/template-fill-map.yaml` complete; template conformance prepass |
| `TEAM_MODELING` | `ROLE_RENDER` passed                         | `team-model/operating-model.md` + `team-model/raci-matrix.yaml` complete; cross-layer mappings coherent           |
| `VERIFY`        | `TEAM_MODELING` passed                       | Required verification artifacts (§7) generated with passing thresholds                                            |
| `PACKAGE`       | `VERIFY` passed                              | `verify/package_manifest.yaml` exists, valid, and matches canonical layout + bundle rules                         |
| `DONE`          | `PACKAGE` passed                             | Final output contract satisfied and deterministic status set to `DONE`                                            |


Step 1 - Team structure and best-practice research:

- Inputs: `team_type`, business objective, constraints, quality bar.
- Output: `research/team-architecture.md`.
- Must include: topology, operating cadence, KPI model, common failure modes, mitigations, references.
- Gate: if missing or generic -> `BLOCKED_INCOMPLETE_RESEARCH`.

Step 2 - Required role planning:

- Output: `research/role-matrix.yaml`.
- Per-role fields: `role_name`, `mission`, `core_responsibilities`, `decision_rights`, `handoffs_in`, `handoffs_out`, `success_metrics`.
- Gate: unresolved role ownership/accountability collisions -> `FAILED_TEAM_MODEL_CONSISTENCY`.

Step 3 - Per-role generation from agent-settings templates:

- Precondition: `research/role-<role-name>.md` exists for every role.
- Template source-of-truth: `agent-settings/templates/` (canonical). Rendered outputs MUST be written under `agent-settings/roles/<role-slug>/` and validated there.
- Outputs:
  - `agent-settings/roles/<role-slug>/AGENTS.md`
  - `agent-settings/roles/<role-slug>/IDENTITY.md`
  - `agent-settings/roles/<role-slug>/SOUL.md`
  - `agent-settings/roles/<role-slug>/USER_PREDEFINED.md`
  - `roles/<role-slug>/HEARTBEAT.md` (required; no paired file in `agent-settings/templates/` unless one is added explicitly later)
  - `research/template-fill-map.yaml` (maps each rendered file above that has a template to its `agent-settings/templates/...` path)
- `USER.md` and `BOOTSTRAP.md` are out of scope: the skill MUST NOT generate them as part of this pipeline unless templates are added under `agent-settings/templates/` and this skill is revised.
- Gate: wrong file set under `agent-settings/roles/<slug>/` -> `FAILED_ROLE_FILE_SET`; any template heading mismatch -> `FAILED_TEMPLATE_CONFORMANCE`; any shallow role content -> `FAILED_ROLE_DEPTH`; missing fill-map or template_map entries -> `FAILED_TEMPLATE_MAPPING`.

Step 4 - Team model synthesis:

- Output: `team-model/operating-model.md` plus `team-model/raci-matrix.yaml`.
- Must synthesize workflows, config, metrics, policies, roles, runbooks, rules into one operating model.
- Must define governance (RACI, approvals, escalation, SLA), contention control, stale-lock handling, and rollback paths.
- `team-model/raci-matrix.yaml` MUST list the same role slug set as `research/role-matrix.yaml` (`role_slugs` array).
- Gate: cross-layer inconsistency -> `FAILED_TEAM_MODEL_CONSISTENCY`.

## 4. Artifact Schema and Folder Contract

Scope: all paths below are relative to the **generated team-pack root** (the output directory of a setup run). Rules about “top-level directories” apply only to that root, not to the skill repository or the host workspace unless the team-pack root is the repo root.

### 4.1 Team settings (fixed structure)

These six directories MUST exist at team-pack root with these exact names (content is flexible):

1. `config/`
2. `metrics/`
3. `policies/`
4. `runbooks/`
5. `rules/`
6. `workflows/`

### 4.2 Agent settings (templates + rendered role context)

`agent-settings/` MUST exist at team-pack root and MUST contain:

- `agent-settings/templates/` — canonical template sources.
- `agent-settings/roles/<role-slug>/` — exactly one directory per planned role slug, containing **exactly** these four files and no others:
  - `AGENTS.md`
  - `IDENTITY.md`
  - `SOUL.md`
  - `USER_PREDEFINED.md`

### 4.3 Operational role artifacts (heartbeat)

`roles/` MUST contain at least `roles/<role-slug>/HEARTBEAT.md` for every role (additional files under `roles/<role-slug>/` allowed unless restricted by a future contract version).

### 4.4 Canonical top-level layout (ordered list for manifests)

Required top-level directories — create these exact names only; no brace expansion; no alternate spellings; **exactly eleven**:

1. `agent-settings/`
2. `config/`
3. `metrics/`
4. `policies/`
5. `research/`
6. `roles/`
7. `runbooks/`
8. `rules/`
9. `team-model/`
10. `verify/`
11. `workflows/`

Required root files (same directory as the folders above):

- `VERIFY_TEAM_PACK_REPORT.md`
- `DIFF_REPORT.md`

Optional root files: `README.md` for human operators only; they do not satisfy any gate.

No other top-level directories are part of the contract (excluding tooling such as `.git`). Additional nested paths under the eleven folders are allowed when required by filenames below.

Required artifacts:

- `config/team.yaml`
- `research/team-architecture.md`
- `research/role-matrix.yaml`
- `research/role-<role-name>.md` (one per role)
- `research/template-fill-map.yaml`
- `agent-settings/templates/` (at minimum: the four templates needed to render the four canonical role files per role)
- `agent-settings/roles/<role-slug>/AGENTS.md`, `IDENTITY.md`, `SOUL.md`, `USER_PREDEFINED.md` (per role)
- `roles/<role-slug>/HEARTBEAT.md` (per role)
- `team-model/operating-model.md`
- `team-model/raci-matrix.yaml`
- `verify/structure_conformance.md`
- `verify/template_conformance.md`
- `verify/package_manifest.yaml`
- `VERIFY_TEAM_PACK_REPORT.md`
- `DIFF_REPORT.md`

Artifact rules:

- Missing required directory/file -> immediate deterministic failure per precedence table.
- Evidence artifacts must reflect the latest generation window.
- Directory scaffolding must create real directories only; literal brace-name directories are invalid outputs.
- Forbidden malformed directory names include any top-level directory matching patterns like `\{.*\}` or containing comma-delimited brace tokens (example: `{config,research,...}`).
- Shell portability rule: do not rely on quoted brace expansion for scaffolding; use explicit path lists or unquoted brace expansion only when shell semantics are guaranteed.

Schema and source definitions:

- `team_roles` / `acl_roles`: derived from `research/role-matrix.yaml`. Same set: normalized slugs from `roles[].role_name`.
- `raci_roles`: derived from `team-model/raci-matrix.yaml`. Field `role_slugs` (array of strings) MUST list every accountable role with normalized slug spelling; set MUST equal `team_roles` after sorting for equality.
- `workflow_roles`: derived only from YAML files matching `workflows/*.yaml` (non-recursive). Union of normalized slugs from:
  - every entry of top-level `actors:` when present (list),
  - every scalar `owner`, `approval_owner`, `escalation_owner` under `stages:` entries when present.
  Set MUST equal `team_roles` after normalization (same members as `team_roles`).
- `research/role-matrix.yaml` minimum schema:
  - `generation_id` (string)
  - `generated_at` (RFC3339 UTC timestamp)
  - `commit_sha` (40-char git SHA, lowercase hex)
  - `roles` (array of objects with required fields from Section 3 Step 2)
- `team-model/raci-matrix.yaml` minimum schema:
  - `generation_id`, `generated_at`, `commit_sha` (same tuple as generation window)
  - `role_slugs` (array of strings, normalized slugs; sorted uniqueness check passes vs `team_roles`)
- `verify/package_manifest.yaml` minimum schema:
  - `generation_id`, `generated_at`, `commit_sha` (same tuple as generation window)
  - `exclude_template_sources` (boolean, MUST be `true` for shipped runtime bundles): when true, runtime bundle MUST exclude template sources (`agent-settings/templates/`)
  - `layout_directories` (array of exactly **eleven** strings): MUST equal the canonical directory names in §4.4 order (use directory names without trailing slash: `agent-settings`, `config`, …, `workflows`)
  - `layout_root_files_mandatory` (array of exactly two strings): `VERIFY_TEAM_PACK_REPORT.md`, `DIFF_REPORT.md` (order as listed)
  - Optional `layout_root_files_optional`: MAY list `README.md` only when present; MUST NOT list `agent-settings/templates/` as a required runtime path
  - `team_settings` (object):
    - `directories_required` (array of exactly six strings): `config`, `metrics`, `policies`, `runbooks`, `rules`, `workflows` (order as listed)
  - `agent_settings` (object):
    - `templates_dir` (string): `agent-settings/templates`
    - `roles_dir` (string): `agent-settings/roles`
    - `required_role_files` (array of four strings): `AGENTS.md`, `IDENTITY.md`, `SOUL.md`, `USER_PREDEFINED.md` (order as listed)
    - `role_slugs_expected` (array of strings): from `research/role-matrix.yaml`
    - `role_slugs_actual` (array of strings): from filesystem under `agent-settings/roles/`
    - `role_count_expected` (int), `role_count_actual` (int)
    - `unknown_role_dirs` (array of strings): MUST be empty at `DONE`
  - `template_map` (object): keys `<role-slug>/<filename>` mapping to at least `template_path`, `required_headings`, `matched_headings`, `structure_match_score` per design spec
- `config/team.yaml` minimum schema:
  - `team_type` (string, MUST match declared intake `team_type`)
  - `role_slugs` (array of strings): set of normalized slugs MUST equal `team_roles`

Generation window and freshness rule:

- Current generation identity tuple is `(generation_id, generated_at, commit_sha)`.
- These artifacts MUST all declare the same tuple: `research/role-matrix.yaml`, `VERIFY_TEAM_PACK_REPORT.md`, `DIFF_REPORT.md`, `verify/structure_conformance.md`, `verify/template_conformance.md`, `team-model/raci-matrix.yaml`, `verify/package_manifest.yaml`.
- Freshness passes only when tuple values match exactly across all tuple-bearing artifacts above and `commit_sha` equals current HEAD commit of the environment that produced the pack.
- Any mismatch or missing tuple field -> `BLOCKED_NO_EVIDENCE`.

Minimum artifact presence requirements:

- `config/`: REQUIRED file is exactly `config/team.yaml` (no substitute path).
- `rules/`: at least one rules/spec file (consumed by operating model or governance; non-empty).
- `workflows/`: at least `workflows/README.md` plus one executable/declared workflow spec file.
- `policies/`: at least `policies/retry-policy.yaml` and `policies/resource-contention.yaml`.
- `metrics/`: at least one metric catalog/spec file with owner mapping.
- `runbooks/`: at least one incident/operation runbook file with responder mapping.
- `agent-settings/templates/`: at least the four canonical markdown templates for role context rendering.
- `agent-settings/roles/<role-slug>/`: exactly the four canonical files per role (§4.2).
- `roles/<role-slug>/`: at least `HEARTBEAT.md` per role.
- Root artifact set must contain at least one file under each required directory (`agent-settings/`, `config/`, `research/`, `roles/`, `workflows/`, `policies/`, `metrics/`, `runbooks/`, `rules/`, `verify/`, `team-model/`), otherwise fail as incomplete generation.

Runtime packaging note: shipped bundles exclude template sources (`agent-settings/templates/`) by default per `exclude_template_sources: true`; the canonical on-disk layout applies before packaging.

## 5. Template Rendering and Anti-Generic Enforcement

Template-first rule (non-negotiable): no prose may be written into a role file until steps 1–3 below are complete for that file. Free-form outlines that replace template headings are invalid.

Template rendering sequence per role file (for files backed by `agent-settings/templates/`):

1. Read template from `agent-settings/templates/`.
2. Extract required headings/section order.
3. Load role research evidence.
4. Fill all required sections with role-specific operational content.
5. Validate structure and role depth.
6. Write mapping entries into `research/template-fill-map.yaml`.

Template map contract:

- `research/template-fill-map.yaml` MUST key each rendered template-backed output to its template path (e.g. `agent-settings/templates/goclaw-template-agents.md`).
- Each mapped entry MUST list `template_section` titles copied exactly from the template (same spelling and hierarchy), never ad-hoc section names invented for the role.
- If the template uses a combined H1 title line, treat `##` and `###` subtitles as the ordered list used for conformance (H1 may differ cosmetically; subtitles must appear in order).

Template conformance rules:

- Preserve section hierarchy and required headings.
- Do not rename/remove required sections.
- Do not skip sections marked required by template structure.

Anti-generic rules:

- Reject content that can be reused unchanged across multiple roles.
- Reject template paraphrase without role terminology, scenarios, or measurable obligations.
- Reject sections lacking concrete handoff/escalation/measurement details.

## 6. Team Model Synthesis Rules

The synthesized model must align all system layers:

- workflows
- config
- metrics
- policies
- roles
- runbooks
- rules

Consistency contract:

- Enforceable cardinality constraints:
  - `roles` is the canonical set from normalized role slugs.
  - `workflow actors`, `policy owners`, `metric owners`, and `runbook responders` must each be subsets of `roles`.
  - Every role in `roles` must appear in at least one ownership or responder mapping across workflows/policies/metrics/runbooks.
  - No mapping set may include unknown roles outside `roles`.
  - Cardinality coherence rule: each mapping set cardinality must be `>= 1` and `<= |roles|`.

Synthesis requirements:

- Every critical workflow stage has an approval owner and escalation owner.
- Every SLA-linked stage maps to alerting and responder runbooks.
- Conflict controls in `policies/resource-contention.yaml` match workflow execution behavior.
- Retry behavior in `policies/retry-policy.yaml` matches workflow recovery paths.

## 7. Verification Gates and Scoring

Verification order:

1. Input completeness and folder contract (§4).
2. Team settings six-directory contract (§4.1).
3. Agent settings contract (§4.2) and per-role file allowlist.
4. Team/role research completeness.
5. Template mapping completeness (`template_map`, fill-map).
6. Template conformance checks (headings/order).
7. Role-depth checks (documented in `verify/template_conformance.md`).
8. Team-model consistency checks.
9. Filesystem sanity checks (no malformed literal-brace directories; no empty artifact tree).
10. Evidence checks and packaging checks.

Scoring thresholds:

- `structure_match_score >= 0.90`
- `role_depth_score >= 0.75`
- `generic_content_flags == 0` for critical sections

Scoring method (brief, deterministic):

- `structure_match_score`: per-file ratio `matched_required_headings / total_required_headings`; **required headings are extracted from the paired `agent-settings/templates/goclaw-template-*.md` file** (ordered `##` / `###` list). Matching is exact string equality on normalized heading text after trim; global score is the mean across the four canonical role files per role (all roles). **Self-reported PASS lines in verification markdown are not evidence** — scores MUST be reproducible from a diff of extracted headings.
- `HEARTBEAT.md`: exclude from the structure mean; MUST be non-empty and contain at least one actionable checklist or signal list; otherwise `FAILED_TEMPLATE_CONFORMANCE`.
- `role_depth_score`: weighted rubric in `[0,1]` using evidence density, operational specificity, and measurable obligations (weights fixed in verifier implementation); global score is documented in `verify/template_conformance.md`.
- `generic_content_flags`: count of critical sections failing anti-generic checks; must be exactly `0`.
- Critical sections for `generic_content_flags == 0`: mission, decision_rights, handoffs_in, handoffs_out, success_metrics, escalation path, SLA/alert ownership.

State-to-step artifact/gate mapping:


| State           | Step                  | Required artifacts                                                                                                  | Gate                                             |
| --------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `INTAKE`        | Input intake          | N/A                                                                                                                 | Required inputs present                          |
| `TEAM_RESEARCH` | Step 1                | `research/team-architecture.md`                                                                                     | Research completeness                            |
| `ROLE_PLANNING` | Step 2                | `research/role-matrix.yaml`                                                                                         | Role matrix validity                             |
| `ROLE_RESEARCH` | Step 3 precondition   | `research/role-<slug>.md` (all roles)                                                                               | Per-role research completeness                   |
| `ROLE_RENDER`   | Step 3 render         | `agent-settings/roles/...`, `roles/.../HEARTBEAT.md`, `research/template-fill-map.yaml`                             | Structure, mapping, template, depth prepass      |
| `TEAM_MODELING` | Step 4                | `team-model/operating-model.md`, `team-model/raci-matrix.yaml`                                                      | Cross-layer consistency + RACI set               |
| `VERIFY`        | Verification pipeline | `verify/structure_conformance.md`, `verify/template_conformance.md`, `VERIFY_TEAM_PACK_REPORT.md`, `DIFF_REPORT.md` | Scores + evidence freshness pass                 |
| `PACKAGE`       | Packaging             | `verify/package_manifest.yaml`                                                                                      | Packaging manifest schema + layout contract pass |
| `DONE`          | Finalization          | Final response sections in required order                                                                           | Output parsing contract pass                     |


Verification outputs (mandatory):

- `verify/structure_conformance.md` — filesystem contract proof for §4.1–§4.3 (team settings, `agent-settings/`, per-role dirs/files, unknown dirs).
- `verify/template_conformance.md` — per-role-file template conformance, `structure_match_score`, `role_depth_score`, `generic_content_flags`, findings (reproducible; no self-reported PASS without extracted heading evidence).
- `VERIFY_TEAM_PACK_REPORT.md` with global pass/fail matrix.
- `DIFF_REPORT.md` with generation-window delta evidence.

Packaging output (mandatory after `PACKAGE`):

- `verify/package_manifest.yaml` as specified in §4.

## 8. Failure States and Recovery

`BLOCKED_INPUT_MISSING`

- Trigger: missing required initial inputs.
- Recovery: request missing inputs and restart from `INTAKE`.

`BLOCKED_INCOMPLETE_RESEARCH`

- Trigger: missing team/role research artifacts.
- Recovery: complete missing research artifacts, then **always** resume from `TEAM_RESEARCH` (re-run the pipeline forward in order; do not jump to mid-states).

`FAILED_TEAM_SETTINGS_STRUCTURE`

- Trigger: any of `config/`, `metrics/`, `policies/`, `runbooks/`, `rules/`, `workflows/` missing or empty per §4.1 minimums.
- Recovery: scaffold team settings directories and minimum files, regenerate required artifacts, rerun verification pipeline from `TEAM_RESEARCH` forward.

`FAILED_AGENT_SETTINGS_STRUCTURE`

- Trigger: `agent-settings/` missing, or `agent-settings/templates/` / `agent-settings/roles/` contract violated.
- Recovery: create canonical `agent-settings/` tree; ensure canonical templates exist in `agent-settings/templates/`; re-render roles; rerun verification pipeline from `TEAM_RESEARCH` forward.

`FAILED_ROLE_FILE_SET`

- Trigger: any `agent-settings/roles/<slug>/` does not contain exactly `AGENTS.md`, `IDENTITY.md`, `SOUL.md`, `USER_PREDEFINED.md`, or contains extra files.
- Recovery: fix per-role file set; re-verify.

`FAILED_TEMPLATE_MAPPING`

- Trigger: `research/template-fill-map.yaml` or `verify/package_manifest.yaml` `template_map` missing any `<role-slug>/<file>` entry for a template-backed render.
- Recovery: complete mappings with explicit template paths; re-verify.

`FAILED_TEMPLATE_CONFORMANCE`

- Trigger: rendered files violate template structure.
- Recovery: regenerate from template with explicit fill-map traceability, then re-verify.

`FAILED_ROLE_DEPTH`

- Trigger: role-specific depth below threshold.
- Recovery: enrich role content from research evidence and re-score.

`FAILED_TEAM_MODEL_CONSISTENCY`

- Trigger: ownership/actor/responder mappings conflict across layers.
- Recovery: reconcile mappings in workflows/config/metrics/policies/roles/runbooks/rules, then re-verify.

`BLOCKED_NO_EVIDENCE`

- Trigger: required verification evidence missing, stale, or inconsistent.
- Recovery: regenerate verification artifacts for the latest cycle, then re-check gates.

`FAILED_ARTIFACT_LAYOUT`

- Trigger: malformed directory layout (including literal brace-directory creation) or required artifact tree is empty/incomplete in a way not covered by more specific failure states.
- Recovery: rebuild directory scaffold with valid paths, regenerate required artifacts, rerun verification pipeline from `TEAM_RESEARCH`.

## 9. Final Output Contract

Return final response in this exact order with exact headings:

1. `Objective`
2. `Assumptions and constraints`
3. `Team architecture and governance`
4. `Team research status`
5. `Role planning status`
6. `Role render status`
7. `Team model synthesis status`
8. `Verification summary (scores and failures)`
9. `Improvement backlog`
10. `Go-live checklist`
11. `Final status`

Parsing rules:

- Heading text must match exactly (case-sensitive) and appear once each.
- Additional sections are not allowed between required sections; appendices are allowed only after `Final status` and must be prefixed `Appendix:`.
- If a required section has no applicable content, write `N/A` (do not omit the section).
- `Final status` value must be exactly `DONE` or one deterministic failure state token.

Completion rule:

- `DONE` is forbidden unless all verification gates pass and **all** mandatory artifacts in §4 exist, including in particular:
  - `config/team.yaml`
  - `verify/structure_conformance.md`
  - `verify/template_conformance.md`
  - `VERIFY_TEAM_PACK_REPORT.md`
  - `DIFF_REPORT.md`
  - `team-model/raci-matrix.yaml`
  - `verify/package_manifest.yaml`
  - All per-role files under §4.2 and §4.3
- Tuple coherence (§4) MUST pass across every tuple-bearing artifact before `DONE`.

## 10. Safety and Integrity Rules

- Never fabricate artifacts, scores, mappings, or completion status.
- Never bypass policy, verification, or evidence gates.
- If uncertain, state uncertainty explicitly and request focused missing context.
- Never claim completion without reproducible artifact proof.

