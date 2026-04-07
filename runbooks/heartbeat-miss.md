# Runbook: Heartbeat Miss Recovery

## Overview

Steps to follow when agent heartbeat signals are missing or stale.

## Detection Criteria

- Miss 2 consecutive heartbeat windows
- No activity signal for more than 5 minutes
- Lock held without heartbeat confirmation

## Recovery Steps

### 1. Immediate Response (0-30s)

- Mark agent as potentially offline
- Check if it is a temporary network issue
- Verify system health metrics
- Log incident if severity above medium

### 2. Stale Lock Recovery (30s-2m)

- Detect abandoned resource locks
- Apply stale lock policy from policies/resource-contention.yaml
- Auto-release locks after timeout threshold
- Reassign critical tasks if auto_reassign enabled

### 3. Escalation (2-5m)

- Trigger escalation based on escalation-matrix.yaml
- Notify lead for severity 1-2
- Notify manager for severity 3-4
- Create incident ticket if auto_reassign fails

### 4. Recovery Actions

- Reassign tasks to available agents
- Preserve work-in-progress state
- Restart failed agents if possible
- Update task assignments and dependencies

## Verification

- Confirm agent back online OR tasks reassigned
- Validate lock recovery completed
- Verify task continuity maintained
- Update monitoring status

## Post-Recovery

- Document root cause
- Update runbooks if needed
- Communicate resolution to stakeholders
- Monitor for recurrence