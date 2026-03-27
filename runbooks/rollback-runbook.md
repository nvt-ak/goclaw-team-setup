# Rollback Runbook - GoClaw Team Setup

## Overview
Steps to safely rollback changes when deployment or operation fails.

## Rollback Triggers

### Automatic Triggers
- Health checks failing for > 5 minutes
- Error rate > 10%
- Response time > 5x baseline
- Critical alerts triggered

### Manual Triggers
- Team lead decision
- Customer complaints > threshold
- Performance degradation noticed
- Security vulnerability detected

## Rollback Levels

### Level 1: Configuration Rollback
- Revert config changes only
- Duration: < 5 minutes
- Risk: Low
- Approvals: None required

### Level 2: Feature Rollback
- Disable specific features
- Duration: < 15 minutes
- Risk: Medium
- Approvals: Lead approval

### Level 3: Version Rollback
- Rollback to previous version
- Duration: < 30 minutes
- Risk: High
- Approvals: Manager approval

### Level 4: Full Rollback
- Complete system rollback
- Duration: < 60 minutes
- Risk: Critical
- Approvals: CTO approval

## Rollback Procedure

### Pre-Rollback Checks
- Verify backup systems are healthy
- Confirm rollback plan is tested
- Ensure team is available for monitoring
- Notify stakeholders of planned rollback

### Rollback Steps
1. Pause incoming traffic - Route traffic to stable version
2. Execute rollback - Deploy previous configuration
3. Validate rollback - Run health checks
4. Resume operations - Gradually restore traffic

### Post-Rollback Actions
- Document root cause
- Update runbooks
- Schedule post-mortem
- Communicate to stakeholders