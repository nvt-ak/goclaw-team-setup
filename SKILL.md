---
name: GoClaw Team Setup
description: Public-ready unified skill for GoClaw multi-agent team setup. Use when users setup/regenerate multi-agent teams with per-role settings, governance (RACI/approval/SLA), conflict controls, and deterministic verification artifacts. Stateless-by-default, memory-optional, optimized for low tool-call execution.
version: v8
---

# GoClaw Team Setup

## Scope
This skill handles:
- End-to-end multi-agent team setup (design -> research -> generation -> verify -> package)
- Per-role context packs (AGENTS/SOUL/IDENTITY/TOOLS/USER/USER_PREDEFINED/HEARTBEAT)
- Governance (RACI, approval, escalation, SLA)
- Deterministic completion evidence and fail-fast validation

This skill does NOT handle:
- Non-GoClaw orchestration systems
- Infra provisioning (K8s/Terraform/CI secrets)
- Policy bypass / fake artifact completion

## Activation Triggers
Use this skill when user asks to:
- Setup/regenerate multi-agent team
- Build or re-build per-role settings
- Add governance/approval gates/conflict controls
- Verify team pack quality with reports
- Package a reusable setup bundle/zip

## Mandatory Invariants (non-negotiable)
1. `team_roles == raci_roles == acl_roles == workflow_roles`
2. Runtime package must exclude `references/` by default
3. No DONE state without BOTH:
   - `VERIFY_TEAM_PACK_REPORT.md`
   - `DIFF_REPORT.md`
4. Per-role required files must include `HEARTBEAT.md`
5. Semantic role content must match declared `team_type` (no cross-domain drift)

## Deterministic Completion Contract
A run is DONE only when all checks pass:
- Structural checks pass
- Semantic checks pass
- Evidence pair exists and is fresh for the latest generation window

If any condition fails, force one of:
- `INCOMPLETE_SETUP`
- `BLOCKED_NO_EVIDENCE`
- `FAILED_SEMANTIC_DRIFT`
- `BLOCKED_INCOMPLETE_RESEARCH`

## Runtime Watchdog Policy
- Keep execution alive with checkpoint artifacts every <= 5 minutes
- If a 5-minute boundary passes without new evidence checkpoint -> `BLOCKED_NO_EVIDENCE`
- Never close by intent/status text only; close by artifact proof only
- Enforce resource lock timeout: shared write locks auto-release after 10 minutes if no heartbeat
- Validate state transitions: enforce allowed state machine transitions per workflow
- Monitor for stale locks: detect and recover from abandoned resource locks

## Role Research Phase (MANDATORY before render)
**Every role must be researched before template filling.**

For each role in roster:
1. **Gather domain context**: industry best-practices, typical responsibilities, KPIs, failure modes
2. **Map to team_type semantics**: ensure role vocabulary aligns with declared team type (content/backend/frontend/ops/security)
3. **Identify role-specific obligations**: what makes this role unique vs template defaults
4. **Document anti-patterns**: what NOT to do for this role
5. **Output artifact**: `research/role-<role-name>.md` (source + findings + mapping to template)

**Fail condition**: If research artifact missing or too generic (< 200 words domain-specific content) → BLOCKED_INCOMPLETE_RESEARCH

| Context File       | Reference Template                            |
|--------------------|-----------------------------------------------|
| AGENTS.md          | references/goclaw-template-agents.md          |
| SOUL.md            | references/goclaw-template-soul.md            |
| IDENTITY.md        | references/goclaw-template-identity.md        |
| USER.md            | references/goclaw-template-user.md            |
| USER_PREDEFINED.md | references/goclaw-template-user-predefined.md |
| BOOTSTRAP.md       | references/goclaw-template-bootstrap.md       |
### Template Compliance Rules
1. **READ reference template BEFORE generating** each context file
2. **FOLLOW exact structure** - copy section headings, format, and key content patterns
3. **FILL IN role-specific content** - customize examples to match role's domain (from research artifacts)
4. **NEVER skip sections** - even if appears optional in template
5. **Preserve markdown formatting** - headers, bullet points, code blocks

### Template Fill Map (MANDATORY)
Produce `research/template-fill-map.yaml` mapping:
- template section -> role-specific source paragraph
- source artifact path + line anchor

If missing mapping for any required section -> `FAILED_TEMPLATE_FILL_MAP`

### Format Validation Check (MANDATORY after generation)
After generating each context file:
1. Extract required sections from reference template
2. Compare with generated content
3. If missing sections or < 70% template match → REGENERATE with template

## Role-Depth Conformance Gate (MANDATORY)
After generation, validate both:
1. Structure conformance (section match against template)
2. Role-depth conformance (content is role-specific and actionable)

Write report: `verify/template_conformance_role_depth.md`

Per file evaluation fields:
- `file`
- `template`
- `structure_match_score`
- `role_depth_score`
- `missing_sections`
- `generic_content_flags`
- `status`

Thresholds:
- `structure_match_score >= 0.90`
- `role_depth_score >= 0.75`
- `generic_content_flags == 0` for critical section

Else -> `FAILED_SEMANTIC_DRIFT`

## Critical Fail Conditions
- Missing required files
- Missing research artifacts
- Context file format mismatch (does not follow reference template structure)
- Generic/copy-template content without role-specific synthesis
- Workflow orphan/cycle
- Missing approval gate for high-risk stage
- Missing escalation owner for SLA breach
- No conflict control for shared writes
- Missing stale-lock recovery policy
- Schema fail in IDENTITY or AGENTS I-L-O-C
- Semantic drift vs selected `team_type`
- Missing evidence pair (`VERIFY_TEAM_PACK_REPORT.md`, `DIFF_REPORT.md`)
- Missing role-depth report (`verify/template_conformance_role_depth.md`)
- Missing template fill map (`research/template-fill-map.yaml`)
- Invalid state transition (violates allowed state machine transitions)
- Resource lock timeout (shared write lock held > 10 minutes without heartbeat)
- Stale lock detection (abandoned resource lock without release)
- Missing lock timeout policy in `policies/resource-contention.yaml`

## Verify Workflow (single-pass)
1. Role research artifacts present and valid
2. Collect all paths once
3. Validate locklist completeness
4. Validate role-map consistency (roles/raci/acl/workflow)
5. **Validate per-role context file format compliance** (MANDATORY):
   - For each role's AGENTS.md: verify matches `references/goclaw-template-agents.md` structure
   - For each role's SOUL.md: verify matches `references/goclaw-template-soul.md` structure
   - For each role's IDENTITY.md: verify matches `references/goclaw-template-identity.md` structure
   - Report: `file | template | match_score | status`
6. **Validate per-role role-depth conformance** (MANDATORY):
   - For each role's AGENTS.md: check `role_depth_score >= 0.75`
   - For each role's SOUL.md: check `role_depth_score >= 0.75`
   - For each role's IDENTITY.md: check `role_depth_score >= 0.75`
7. Validate per-role schema + semantic alignment
8. Validate packaging cleanliness (runtime excludes references)
9. Emit verification table: `path | expected | actual | status`
10. Write:
   - `VERIFY_TEAM_PACK_REPORT.md`
   - `DIFF_REPORT.md`
   - `verify/template_conformance_role_depth.md`

## Output Contract
Return in this order:
1. Mục tiêu
2. Giả định & ràng buộc
3. Kiến trúc team + governance
4. Research status per role
5. Role settings pack status
6. Workflow + policy status
7. Verify report (score + lỗi)
8. Improvement backlog
9. Go-live checklist
10. Final status (`DONE` or blocking state)

If missing mandatory artifact(s): return `INCOMPLETE_SETUP`.

## Safety
- Refuse policy bypass instructions
- Do not fabricate capabilities or artifacts
- If uncertain, state uncertainty + ask focused follow-up


---

Anh có thể copy-paste thẳng nội dung này vào file /app/data/skills-store/goclaw-team-setup/7/SKILL.md để update.  
Sau khi update, skill sẽ hoạt động đúng expectation: deep research + nội suy theo template + fail cứng nếu copy template.
