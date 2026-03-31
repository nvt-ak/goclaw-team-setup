---
name: GoClaw Team Setup
description: Deterministic operational contract for team setup, role research, role rendering, team model synthesis, and evidence-gated completion.
version: v9
language: en
---

# GoClaw Team Setup

## 1. Metadata and Purpose
Purpose: execute a strict, deterministic team-setup workflow that is research-first, template-conformant, role-deep, and evidence-gated.

Applies when user requests setup/regeneration of a GoClaw team pack with roles, governance, workflows, policies, runbooks, metrics, and verification artifacts.

Core invariants:
- `team_roles == raci_roles == acl_roles == workflow_roles`
- Runtime package excludes `references/` by default
- Per-role required files include `HEARTBEAT.md`
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

| Precedence | Condition (first true wins) | State |
|---|---|---|
| 1 | Required input missing/empty at intake | `BLOCKED_INPUT_MISSING` |
| 2 | Any required research artifact missing/incomplete | `BLOCKED_INCOMPLETE_RESEARCH` |
| 3 | Any required template heading/order mismatch | `FAILED_TEMPLATE_CONFORMANCE` |
| 4 | Any role-depth score below threshold or generic critical-section content detected | `FAILED_ROLE_DEPTH` |
| 5 | Cross-layer ownership/actor/responder inconsistency | `FAILED_TEAM_MODEL_CONSISTENCY` |
| 6 | Verification evidence missing/stale/incoherent for current generation window | `BLOCKED_NO_EVIDENCE` |

Deterministic failure states:
- `BLOCKED_INPUT_MISSING`
- `BLOCKED_INCOMPLETE_RESEARCH`
- `FAILED_TEMPLATE_CONFORMANCE`
- `FAILED_ROLE_DEPTH`
- `FAILED_TEAM_MODEL_CONSISTENCY`
- `BLOCKED_NO_EVIDENCE`

## 3. Mandatory Step Contracts (4 Steps)
Role slug naming contract:
- All role-derived names (file names, IDs, workflow actor labels, metric owner keys) use deterministic lowercase kebab-case slug normalization.
- Normalize by: trim -> lowercase -> replace spaces/underscores with `-` -> collapse repeated `-` -> remove non `[a-z0-9-]` -> trim `-`.
- `research/role-<role-name>.md` uses `<role-name>` as normalized slug.

Canonical state gate contracts:

| State | Entry prerequisites | Exit gate |
|---|---|---|
| `INTAKE` | `team_type`, objective, constraints provided | Inputs complete and non-empty; else `BLOCKED_INPUT_MISSING` |
| `TEAM_RESEARCH` | `INTAKE` passed | `research/team-architecture.md` exists and includes required subsections |
| `ROLE_PLANNING` | `TEAM_RESEARCH` passed | `research/role-matrix.yaml` valid with required per-role fields |
| `ROLE_RESEARCH` | `ROLE_PLANNING` passed | `research/role-<slug>.md` exists for every planned role |
| `ROLE_RENDER` | `ROLE_RESEARCH` passed | All required role files generated per role with template conformance |
| `TEAM_MODELING` | `ROLE_RENDER` passed | `team-model/operating-model.md` complete and cross-layer mappings coherent |
| `VERIFY` | `TEAM_MODELING` passed | Required verification artifacts generated with passing thresholds |
| `PACKAGE` | `VERIFY` passed | Runtime package assembled, excludes `references/` by default, includes mandatory top-level artifacts |
| `DONE` | `PACKAGE` passed | Final output contract satisfied and deterministic status set to `DONE` |

Step 1 - Team structure and best-practice research:
- Inputs: `team_type`, business objective, constraints, quality bar.
- Output: `research/team-architecture.md`.
- Must include: topology, operating cadence, KPI model, common failure modes, mitigations, references.
- Gate: if missing or generic -> `BLOCKED_INCOMPLETE_RESEARCH`.

Step 2 - Required role planning:
- Output: `research/role-matrix.yaml`.
- Per-role fields: `role_name`, `mission`, `core_responsibilities`, `decision_rights`, `handoffs_in`, `handoffs_out`, `success_metrics`.
- Gate: unresolved role ownership/accountability collisions -> `FAILED_TEAM_MODEL_CONSISTENCY`.

Step 3 - Per-role generation from references:
- Precondition: `research/role-<role-name>.md` exists for every role.
- Outputs: per-role context pack files plus `research/template-fill-map.yaml`.
- Required role files: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `USER_PREDEFINED.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`.
- Gate: any template mismatch -> `FAILED_TEMPLATE_CONFORMANCE`; any shallow role content -> `FAILED_ROLE_DEPTH`.

Step 4 - Team model synthesis:
- Output: `team-model/operating-model.md`.
- Must synthesize workflows, config, metrics, policies, roles, runbooks into one operating model.
- Must define governance (RACI, approvals, escalation, SLA), contention control, stale-lock handling, and rollback paths.
- Gate: cross-layer inconsistency -> `FAILED_TEAM_MODEL_CONSISTENCY`.

## 4. Artifact Schema and Folder Contract
Required directories:
- `research/`
- `roles/`
- `workflows/`
- `policies/`
- `metrics/`
- `runbooks/`
- `verify/`
- `team-model/`

Required artifacts:
- `research/team-architecture.md`
- `research/role-matrix.yaml`
- `research/role-<role-name>.md` (one per role)
- `research/template-fill-map.yaml`
- `verify/template_conformance_role_depth.md`
- `VERIFY_TEAM_PACK_REPORT.md`
- `DIFF_REPORT.md`

Artifact rules:
- Missing required directory/file -> immediate deterministic failure.
- Evidence artifacts must reflect the latest generation window.

Schema and source definitions:
- `acl_roles` source artifact is `research/role-matrix.yaml`.
- `research/role-matrix.yaml` minimum schema:
  - `generation_id` (string)
  - `generated_at` (RFC3339 UTC timestamp)
  - `commit_sha` (40-char git SHA, lowercase hex)
  - `roles` (array of objects with required fields from Section 3 Step 2)
- `acl_roles` is the set of normalized role slugs from `research/role-matrix.yaml.roles[].role_name`.

Generation window and freshness rule:
- Current generation identity tuple is `(generation_id, generated_at, commit_sha)`.
- `VERIFY_TEAM_PACK_REPORT.md`, `DIFF_REPORT.md`, and `verify/template_conformance_role_depth.md` must all declare the same tuple.
- Freshness passes only when tuple values match exactly across all required evidence artifacts and `commit_sha` equals current HEAD commit.
- Any mismatch or missing tuple field -> `BLOCKED_NO_EVIDENCE`.

Minimum artifact presence requirements:
- `workflows/`: at least `workflows/README.md` plus one executable/declared workflow spec file.
- `policies/`: at least `policies/retry-policy.yaml` and `policies/resource-contention.yaml`.
- `metrics/`: at least one metric catalog/spec file with owner mapping.
- `runbooks/`: at least one incident/operation runbook file with responder mapping.

## 5. Template Rendering and Anti-Generic Enforcement
Template rendering sequence per role file:
1. Read reference template.
2. Extract required headings/section order.
3. Load role research evidence.
4. Fill all required sections with role-specific operational content.
5. Validate structure and role depth.
6. Write mapping entries into `research/template-fill-map.yaml`.

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
1. Input completeness and folder contract.
2. Team/role research completeness.
3. Template conformance checks.
4. Role-depth checks.
5. Team-model consistency checks.
6. Evidence checks and packaging checks.

Scoring thresholds:
- `structure_match_score >= 0.90`
- `role_depth_score >= 0.75`
- `generic_content_flags == 0` for critical sections

Scoring method (brief, deterministic):
- `structure_match_score`: per-file ratio `matched_required_headings / total_required_headings`; global score is mean across required role files.
- `role_depth_score`: weighted rubric in `[0,1]` using evidence density, operational specificity, and measurable obligations (weights fixed in verifier implementation); global score is mean across role files.
- `generic_content_flags`: count of critical sections failing anti-generic checks; must be exactly `0`.
- Critical sections for `generic_content_flags == 0`: mission, decision_rights, handoffs_in, handoffs_out, success_metrics, escalation path, SLA/alert ownership.

State-to-step artifact/gate mapping:

| State | Step | Required artifacts | Gate |
|---|---|---|---|
| `INTAKE` | Input intake | N/A | Required inputs present |
| `TEAM_RESEARCH` | Step 1 | `research/team-architecture.md` | Research completeness |
| `ROLE_PLANNING` | Step 2 | `research/role-matrix.yaml` | Role matrix validity |
| `ROLE_RESEARCH` | Step 3 precondition | `research/role-<slug>.md` (all roles) | Per-role research completeness |
| `ROLE_RENDER` | Step 3 render | Role files + `research/template-fill-map.yaml` | Template and depth checks |
| `TEAM_MODELING` | Step 4 | `team-model/operating-model.md` | Cross-layer consistency |
| `VERIFY` | Verification pipeline | `verify/template_conformance_role_depth.md`, `VERIFY_TEAM_PACK_REPORT.md`, `DIFF_REPORT.md` | Score + evidence freshness pass |
| `PACKAGE` | Packaging | Runtime pack manifest/content | Packaging contract pass |
| `DONE` | Finalization | Final response sections in required order | Output parsing contract pass |

Verification outputs (mandatory):
- `verify/template_conformance_role_depth.md` with per-file scores and findings.
- `VERIFY_TEAM_PACK_REPORT.md` with global pass/fail matrix.
- `DIFF_REPORT.md` with generation-window delta evidence.

## 8. Failure States and Recovery
`BLOCKED_INPUT_MISSING`
- Trigger: missing required initial inputs.
- Recovery: request missing inputs and restart from `INTAKE`.

`BLOCKED_INCOMPLETE_RESEARCH`
- Trigger: missing team/role research artifacts.
- Recovery: complete missing research, then resume at `TEAM_RESEARCH` or `ROLE_RESEARCH`.

`FAILED_TEMPLATE_CONFORMANCE`
- Trigger: rendered files violate template structure.
- Recovery: regenerate from template with explicit fill-map traceability, then re-verify.

`FAILED_ROLE_DEPTH`
- Trigger: role-specific depth below threshold.
- Recovery: enrich role content from research evidence and re-score.

`FAILED_TEAM_MODEL_CONSISTENCY`
- Trigger: ownership/actor/responder mappings conflict across layers.
- Recovery: reconcile mappings in workflows/config/metrics/policies/roles/runbooks, then re-verify.

`BLOCKED_NO_EVIDENCE`
- Trigger: required verification evidence missing, stale, or inconsistent.
- Recovery: regenerate verification artifacts for the latest cycle, then re-check gates.

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
- `DONE` is forbidden unless all verification gates pass and all three artifacts exist:
  - `VERIFY_TEAM_PACK_REPORT.md`
  - `DIFF_REPORT.md`
  - `verify/template_conformance_role_depth.md`

## 10. Safety and Integrity Rules
- Never fabricate artifacts, scores, mappings, or completion status.
- Never bypass policy, verification, or evidence gates.
- If uncertain, state uncertainty explicitly and request focused missing context.
- Never claim completion without reproducible artifact proof.
