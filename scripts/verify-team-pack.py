#!/usr/bin/env python3
"""
Verify Team Pack - GoClaw Team Setup
Phase A Critical Fix #4: Checkpoint verify mỗi 5 phút để ngăn treo không evidence

Usage:
    python3 scripts/verify-team-pack.py [--checkpoint] [--full]

Flags:
    --checkpoint  Run partial verification and write checkpoint artifact
    --full        Run full verification (default)
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).parent.parent
CHECKPOINT_INTERVAL_SECONDS = 300  # 5 minutes
CHECKPOINT_DIR = ROOT_DIR / ".verify_checkpoints"

# Required files locklist
REQUIRED_FILES = [
    "config/team.yaml",
    "roles/role-settings-pack.yaml",
    "workflows/main.yaml",
    "policies/conflict-policy.yaml",
    "policies/resource-contention.yaml",
    "policies/escalation-matrix.yaml",
    "runbooks/incident-runbook.md",
    "runbooks/rollback-runbook.md",
]

PER_ROLE_REQUIRED_FILES = [
    "AGENTS.md",
    "SOUL.md",
    "IDENTITY.md",
    "TOOLS.md",
    "USER.md",
    "USER_PREDEFINED.md",
    "HEARTBEAT.md",
]

EVIDENCE_FILES = [
    "VERIFY_TEAM_PACK_REPORT.md",
    "DIFF_REPORT.md",
]


def ensure_checkpoint_dir():
    """Ensure checkpoint directory exists"""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


def write_checkpoint_checkpoint(result: dict):
    """Write checkpoint artifact with timestamp"""
    ensure_checkpoint_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_file = CHECKPOINT_DIR / f"checkpoint_{timestamp}.json"

    checkpoint_data = {
        "timestamp": timestamp,
        "iso_time": datetime.now().isoformat(),
        "status": result.get("status", "unknown"),
        "checks_passed": result.get("checks_passed", 0),
        "checks_failed": result.get("checks_failed", 0),
        "errors": result.get("errors", []),
    }

    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

    print(f"[CHECKPOINT] Written to {checkpoint_file}")
    return checkpoint_file


def run_partial_verification() -> dict:
    """Run partial verification - quick checks only"""
    result = {
        "status": "in_progress",
        "checks_passed": 0,
        "checks_failed": 0,
        "errors": [],
        "timestamp": datetime.now().isoformat(),
    }

    # Check 1: Required files exist
    for file_path in REQUIRED_FILES:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            result["checks_passed"] += 1
        else:
            result["checks_failed"] += 1
            result["errors"].append(f"Missing required file: {file_path}")

    # Check 2: Role directories exist
    roles_dir = ROOT_DIR / "roles"
    if roles_dir.exists():
        role_dirs = [d for d in roles_dir.iterdir() if d.is_dir()]
        for role_dir in role_dirs:
            for per_role_file in PER_ROLE_REQUIRED_FILES:
                role_file = role_dir / per_role_file
                if role_file.exists():
                    result["checks_passed"] += 1
                else:
                    result["checks_failed"] += 1
                    result["errors"].append(f"Missing role file: {role_dir.name}/{per_role_file}")
    else:
        result["errors"].append("Roles directory not found")

    # Set status
    if result["checks_failed"] == 0:
        result["status"] = "pass"
    elif result["checks_passed"] > 0:
        result["status"] = "partial"
    else:
        result["status"] = "fail"

    return result


def run_full_verification() -> dict:
    """Run full verification - all checks"""
    result = run_partial_verification()

    # Additional full checks
    # Check 3: Evidence files
    for evidence_file in EVIDENCE_FILES:
        full_path = ROOT_DIR / evidence_file
        if full_path.exists():
            # Check freshness (within last hour)
            mtime = datetime.fromtimestamp(full_path.stat().st_mtime)
            age_seconds = (datetime.now() - mtime).total_seconds()
            if age_seconds < 3600:
                result["checks_passed"] += 1
            else:
                result["checks_failed"] += 1
                result["errors"].append(f"Stale evidence file: {evidence_file}")
        else:
            result["checks_failed"] += 1
            result["errors"].append(f"Missing evidence file: {evidence_file}")

    # Check 4: Workflow state machine validity
    workflow_file = ROOT_DIR / "workflows/main.yaml"
    if workflow_file.exists():
        with open(workflow_file, "r", encoding="utf-8") as f:
            content = f.read()
            if "state_machine:" in content and "transition_guards:" in content:
                result["checks_passed"] += 1
            else:
                result["checks_failed"] += 1
                result["errors"].append("Workflow missing state_machine or transition_guards")
    else:
        result["checks_failed"] += 1
        result["errors"].append("Workflow file not found")

    # Check 5: Policy files validity
    policy_files = [
        "policies/escalation-matrix.yaml",
        "policies/resource-contention.yaml",
    ]
    for policy_file in policy_files:
        full_path = ROOT_DIR / policy_file
        if full_path.exists():
            result["checks_passed"] += 1
        else:
            result["checks_failed"] += 1
            result["errors"].append(f"Missing policy file: {policy_file}")

    # Final status
    if result["checks_failed"] == 0:
        result["status"] = "DONE"
    else:
        result["status"] = "INCOMPLETE"

    return result


def generate_verify_report(result: dict) -> str:
    """Generate VERIFY_TEAM_PACK_REPORT.md content"""
    report = f"""# Verify Team Pack Report

**Generated:** {result['timestamp']}
**Status:** {result['status']}

## Summary

| Metric | Value |
|--------|-------|
| Checks Passed | {result['checks_passed']} |
| Checks Failed | {result['checks_failed']} |
| Total Errors | {len(result['errors'])} |

## Errors

"""
    if result['errors']:
        for i, error in enumerate(result['errors'], 1):
            report += f"{i}. {error}\n"
    else:
        report += "No errors found.\n"

    report += """
## Checklist

- [ ] Required files present
- [ ] Role files complete
- [ ] Evidence files fresh
- [ ] Workflow state machine valid
- [ ] Policy files valid

"""
    return report


def generate_diff_report() -> str:
    """Generate DIFF_REPORT.md content"""
    import subprocess

    report = """# Diff Report

**Generated:** """ + datetime.now().isoformat() + """

## Git Status

"""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
            timeout=10
        )
        if result.stdout:
            report += "```\n" + result.stdout + "\n```\n"
        else:
            report += "No uncommitted changes.\n"
    except Exception as e:
        report += f"Error running git status: {e}\n"

    report += """
## Recent Commits

"""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
            timeout=10
        )
        if result.stdout:
            report += "```\n" + result.stdout + "\n```\n"
        else:
            report += "No recent commits.\n"
    except Exception as e:
        report += f"Error running git log: {e}\n"

    return report


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Verify Team Pack")
    parser.add_argument(
        "--checkpoint",
        action="store_true",
        help="Run partial verification and write checkpoint"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full verification (default)"
    )

    args = parser.parse_args()

    if args.checkpoint:
        # Checkpoint mode - run partial and write checkpoint
        result = run_partial_verification()
        write_checkpoint_checkpoint(result)
        print(f"[CHECKPOINT] Status: {result['status']}")
        print(f"[CHECKPOINT] Passed: {result['checks_passed']}, Failed: {result['checks_failed']}")
    else:
        # Full mode - run full verification and generate reports
        result = run_full_verification()

        # Write reports
        verify_report = generate_verify_report(result)
        diff_report = generate_diff_report()

        verify_path = ROOT_DIR / "VERIFY_TEAM_PACK_REPORT.md"
        diff_path = ROOT_DIR / "DIFF_REPORT.md"

        with open(verify_path, "w", encoding="utf-8") as f:
            f.write(verify_report)

        with open(diff_path, "w", encoding="utf-8") as f:
            f.write(diff_report)

        print(f"[VERIFY] Status: {result['status']}")
        print(f"[VERIFY] Passed: {result['checks_passed']}, Failed: {result['checks_failed']}")
        print(f"[VERIFY] Report: {verify_path}")
        print(f"[VERIFY] Diff: {diff_path}")

        # Exit with error if verification failed
        if result['status'] != 'DONE':
            sys.exit(1)


if __name__ == "__main__":
    main()
