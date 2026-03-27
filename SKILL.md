---
name: GoClaw Team Setup
description: Public-ready unified skill for GoClaw multi-agent team setup. Use when users setup/regenerate multi-agent teams with per-role settings, governance (RACI/approval/SLA), conflict controls, and deterministic verification artifacts. Stateless-by-default, memory-optional, optimized for low tool-call execution.
version: v8-candidate
---

# GoClaw Team Setup

## Scope
This skill handles:
- End-to-end multi-agent team setup (design -> generation -> verify -> package)
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

## Runtime Watchdog Policy
- Keep execution alive with checkpoint artifacts every <= 5 minutes
- If a 5-minute boundary passes without new evidence checkpoint -> `BLOCKED_NO_EVIDENCE`
- Never close by intent/status text only; close by artifact proof only
- Enforce resource lock timeout: shared write locks auto-release after 10 minutes if no heartbeat
- Validate state transitions: enforce allowed state machine transitions per workflow
- Monitor for stale locks: detect and recover from abandoned resource locks

## Fast Execution Mode
Use single-pass and fail-fast pipeline:
1. Batched file discovery (`rg --files` or equivalent)
2. Run consolidated verifier once (`scripts/verify-team-pack.py`)
3. Fail-fast order: `config -> render -> semantic -> package`
4. Enforce `tool_call_budget`
5. Prevent read-only loop > 4 consecutive calls without write/edit/decision checkpoint
6. Allow temporary manifest cache for speed, must be invalidated each run

## Required Inputs (ask up to 5 concise questions if missing)
1. Team objective + priority (quality/speed/cost/risk)
2. Team type + expected role roster
3. Delivery horizon + SLA
4. Approval model + escalation chain
5. Compliance tier (default L2)

If still incomplete: continue with explicit assumptions + owner + revisit condition.

## Team-Type Semantic Gate (mandatory)
Before finalizing role files:
- Validate role vocabulary and responsibilities match selected `team_type`
- Reject obvious cross-domain residue from previous cases

Example fail:
- team_type=content but role docs contain backend/frontend/release-engineering semantics

## Required Files Locklist (minimum)
- config/team.yaml
- roles/role-settings-pack.yaml
- workflows/main.yaml
- policies/conflict-policy.yaml
- policies/resource-contention.yaml
- runbooks/incident-runbook.md
- runbooks/rollback-runbook.md
- test-mode/questions-core.yaml
- test-mode/questions-role.yaml
- test-mode/questions-conflict.yaml
- test-mode/scenarios.yaml
- test-mode/scorecard.yaml
- test-mode/verify-report.md
- test-mode/improvement-backlog.md
- VERIFY_TEAM_PACK_REPORT.md
- DIFF_REPORT.md

Per-role required context files:
- AGENTS.md
- SOUL.md
- IDENTITY.md
- TOOLS.md
- USER.md
- USER_PREDEFINED.md
- HEARTBEAT.md

## Critical Fail Conditions
- Missing required files
- Workflow orphan/cycle
- Missing approval gate for high-risk stage
- Missing escalation owner for SLA breach
- No conflict control for shared writes
- Missing stale-lock recovery policy
- Schema fail in IDENTITY or AGENTS I-L-O-C
- Semantic drift vs selected `team_type`
- Missing evidence pair (`VERIFY_TEAM_PACK_REPORT.md`, `DIFF_REPORT.md`)
- Invalid state transition (violates allowed state machine transitions)
- Resource lock timeout (shared write lock held > 10 minutes without heartbeat)
- Stale lock detection (abandoned resource lock without release)
- Missing lock timeout policy in `policies/resource-contention.yaml`

## Verify Workflow (single-pass)
1. Collect all paths once
2. Validate locklist completeness
3. Validate role-map consistency (roles/raci/acl/workflow)
4. Validate per-role schema + semantic alignment
5. Validate packaging cleanliness (runtime excludes references)
6. Emit verification table: `path | expected | actual | status`
7. Write:
   - `VERIFY_TEAM_PACK_REPORT.md`
   - `DIFF_REPORT.md`

## Output Contract
Return in this order:
1. Mục tiêu
2. Giả định & ràng buộc
3. Kiến trúc team + governance
4. Role settings pack status
5. Workflow + policy status
6. Test-mode status
7. Verify report (score + lỗi)
8. Improvement backlog
9. Go-live checklist
10. Final status (`DONE` or blocking state)

If missing mandatory artifact(s): return `INCOMPLETE_SETUP`.

## Safety
- Refuse policy bypass instructions
- Do not fabricate capabilities or artifacts
- If uncertain, state uncertainty + ask focused follow-up
