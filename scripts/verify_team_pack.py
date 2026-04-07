#!/usr/bin/env python3
"""
Mechanical verifier for GoClaw team-pack layout (SKILL.md v13).

Writes:
  verify/structure_conformance.md
  verify/template_conformance.md
  verify/package_manifest.yaml

Requires: PyYAML (pip install -r scripts/requirements-verify.txt)
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    print("Missing PyYAML. Install: pip install -r scripts/requirements-verify.txt", file=sys.stderr)
    sys.exit(2)


# Canonical layout (no trailing slashes in manifest), ordered per SKILL §4.4
LAYOUT_DIRS = [
    "agent-settings",
    "config",
    "metrics",
    "policies",
    "research",
    "roles",
    "runbooks",
    "rules",
    "team-model",
    "verify",
    "workflows",
]

TEAM_SETTINGS_DIRS = ["config", "metrics", "policies", "runbooks", "rules", "workflows"]

ROLE_CONTEXT_FILES = ["AGENTS.md", "IDENTITY.md", "SOUL.md", "USER_PREDEFINED.md"]

FILE_TO_TEMPLATE = {
    "AGENTS.md": "goclaw-template-agents.md",
    "IDENTITY.md": "goclaw-template-identity.md",
    "SOUL.md": "goclaw-template-soul.md",
    "USER_PREDEFINED.md": "goclaw-template-user-predefined.md",
}

STRUCTURE_THRESHOLD = 0.90
DEPTH_THRESHOLD = 0.75

_slug_re = re.compile(r"[^a-z0-9-]+")


def normalize_slug(name: str) -> str:
    s = name.strip().lower().replace("_", " ")
    s = re.sub(r"\s+", "-", s)
    s = _slug_re.sub("", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def normalize_heading(text: str) -> str:
    t = " ".join(text.strip().split())
    return t


def extract_h2_h3(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out: list[str] = []
    for line in lines:
        if line.startswith("### "):
            out.append(normalize_heading(line[4:]))
        elif line.startswith("## "):
            out.append(normalize_heading(line[3:]))
    return out


def extract_h2_sections(content: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = ""
    for line in content.splitlines():
        if line.startswith("## "):
            current = normalize_heading(line[3:])
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def structure_match_ordered(required: list[str], got: list[str]) -> tuple[list[str], float]:
    """Count required headings matched in order (subsequence), normalized equality per heading."""
    matched: list[str] = []
    gi = 0
    for h in required:
        while gi < len(got) and got[gi] != h:
            gi += 1
        if gi < len(got) and got[gi] == h:
            matched.append(h)
            gi += 1
    if not required:
        return [], 1.0
    return matched, len(matched) / len(required)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def heartbeat_ok(content: str) -> bool:
    if word_count(content) < 8:
        return False
    # actionable checklist / signal heuristic
    return bool(re.search(r"(?m)^\s*[-*]\s+\S", content)) or bool(re.search(r"(?i)\b(checklist|signal|heartbeat)\b", content))


def _stub_depth_score(content: str) -> float:
    """v0 heuristic; replace with rubric later."""
    wc = word_count(content)
    return min(1.0, wc / 180.0)


def _stub_generic_flags(content: str) -> int:
    """v0: flag if body is extremely thin."""
    return 1 if word_count(content) < 40 else 0


def _agents_professional_findings(role_slug: str, content: str) -> list[str]:
    findings: list[str] = []
    sections = extract_h2_sections(content)
    required_sections = [
        "Mission",
        "Scope and Non-Goals",
        "Inputs and Signals",
        "Decision Rights",
        "Operating Procedure",
        "Escalation and Exception Handling",
        "Handoffs",
        "Success Metrics",
        "Quality Bar and Review Checklist",
        "Anti-Patterns",
    ]
    for sec in required_sections:
        if sec not in sections:
            findings.append(f"missing required AGENTS section: {sec}")

    for sec in ("Mission", "Decision Rights", "Handoffs", "Success Metrics"):
        if sec in sections and word_count(sections[sec]) < 18:
            findings.append(f"section too short for professional depth: {sec}")

    if "Operating Procedure" in sections:
        sop = sections["Operating Procedure"]
        step_count = len(re.findall(r"(?m)^\s*\d+\.\s+", sop))
        if step_count < 4:
            findings.append("Operating Procedure must contain at least 4 numbered steps")

    if "Handoffs" in sections:
        h = sections["Handoffs"]
        if "Inbound" not in h or "Outbound" not in h:
            findings.append("Handoffs must include both Inbound and Outbound")
        if role_slug in h and re.search(rf"(?i)from\s+{re.escape(role_slug)}", h):
            findings.append("Handoffs contains self-referential inbound mapping")

    if "Success Metrics" in sections:
        m = sections["Success Metrics"]
        metric_count = len(re.findall(r"(?m)^\s*-\s*Metric:", m))
        if metric_count < 3:
            findings.append("Success Metrics must define at least 3 metrics")

    return findings


def _identity_professional_findings(content: str) -> list[str]:
    findings: list[str] = []
    sections = extract_h2_sections(content)
    required = [
        "Role",
        "Team Type",
        "Core Responsibility",
        "Operational Boundary",
        "Escalation Contract",
        "Interface Signature",
    ]
    for sec in required:
        if sec not in sections:
            findings.append(f"missing required IDENTITY section: {sec}")
    for sec in ("Core Responsibility", "Operational Boundary", "Escalation Contract", "Interface Signature"):
        if sec in sections and word_count(sections[sec]) < 14:
            findings.append(f"section too short for professional depth: {sec}")
    return findings


def _soul_professional_findings(content: str) -> list[str]:
    findings: list[str] = []
    sections = extract_h2_sections(content)
    required = ["Tone", "Communication Rules", "Reasoning Style", "Domain Focus", "Boundaries"]
    for sec in required:
        if sec not in sections:
            findings.append(f"missing required SOUL section: {sec}")
    for sec in ("Communication Rules", "Reasoning Style", "Boundaries"):
        if sec in sections and word_count(sections[sec]) < 14:
            findings.append(f"section too short for professional depth: {sec}")
    return findings


def _user_predefined_professional_findings(content: str) -> list[str]:
    findings: list[str] = []
    sections = extract_h2_sections(content)
    required = [
        "Principles",
        "Language",
        "User Profiles",
        "Quality Bar",
        "Escalation Policy",
        "Non-Overridable Rules",
    ]
    for sec in required:
        if sec not in sections:
            findings.append(f"missing required USER_PREDEFINED section: {sec}")
    for sec in ("Principles", "Quality Bar", "Escalation Policy", "Non-Overridable Rules"):
        if sec in sections and word_count(sections[sec]) < 12:
            findings.append(f"section too short for professional depth: {sec}")
    return findings


def git_head(root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if len(out) == 40 and re.fullmatch(r"[0-9a-f]+", out):
            return out
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass
    return ""


def dir_has_file(root: Path, subdir: str) -> bool:
    p = root / subdir
    if not p.is_dir():
        return False
    for c in p.iterdir():
        if c.is_file():
            return True
    return False


def load_role_slugs(role_matrix_path: Path) -> tuple[list[str], dict[str, Any] | None, str]:
    if not role_matrix_path.is_file():
        return [], None, "missing research/role-matrix.yaml"
    data = yaml.safe_load(role_matrix_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return [], data, "role-matrix.yaml root must be a mapping"
    roles = data.get("roles")
    if not isinstance(roles, list):
        return [], data, "role-matrix.yaml missing roles array"
    slugs: list[str] = []
    for r in roles:
        if not isinstance(r, dict):
            continue
        rn = r.get("role_name")
        if isinstance(rn, str) and rn.strip():
            slugs.append(normalize_slug(rn))
    return sorted(set(slugs)), data, ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify GoClaw team-pack (v13) and write verify/* artifacts.")
    ap.add_argument("--root", type=Path, default=Path("."), help="team-pack root directory")
    ap.add_argument("--dry-run", action="store_true", help="do not write files")
    ap.add_argument(
        "--strict-extra-top-level",
        action="store_true",
        help="fail on unexpected top-level directories/files",
    )
    args = ap.parse_args()
    root = args.root.resolve()

    lines_struct: list[str] = []
    issues: list[str] = []
    fail = False

    def add(msg: str, *, critical: bool = True) -> None:
        nonlocal fail
        lines_struct.append(("- " if critical else "- (note) ") + msg)
        if critical:
            fail = True

    lines_struct.append("# structure_conformance")
    lines_struct.append("")
    lines_struct.append(f"- pack_root: `{root}`")
    lines_struct.append(f"- generated_at_utc: `{datetime.now(timezone.utc).isoformat()}`")
    lines_struct.append("")

    # Top-level layout
    if not root.is_dir():
        print("root is not a directory", file=sys.stderr)
        return 1

    top_dirs = {p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")}
    top_files = {p.name for p in root.iterdir() if p.is_file() and not p.name.startswith(".")}

    missing_layout = [d for d in LAYOUT_DIRS if d not in top_dirs]
    if missing_layout:
        add(f"missing required top-level directories: {missing_layout}")

    extra_dirs = sorted(top_dirs - set(LAYOUT_DIRS))
    if extra_dirs:
        msg = f"unexpected top-level directories: {extra_dirs}"
        if args.strict_extra_top_level:
            add(msg)
        else:
            lines_struct.append(f"- (note) {msg}")

    mandatory_root_files = {"VERIFY_TEAM_PACK_REPORT.md", "DIFF_REPORT.md"}
    missing_root = sorted(mandatory_root_files - top_files)
    if missing_root:
        add(f"missing mandatory root files: {missing_root}")

    allowed_root_files = mandatory_root_files | {"README.md"}
    extra_files = sorted(top_files - allowed_root_files)
    if extra_files:
        msg = f"unexpected top-level files: {extra_files}"
        if args.strict_extra_top_level:
            add(msg)
        else:
            lines_struct.append(f"- (note) {msg}")

    # Team settings: dirs exist + non-empty
    for d in TEAM_SETTINGS_DIRS:
        p = root / d
        if not p.is_dir():
            add(f"team settings directory missing: {d}/")
        elif not dir_has_file(root, d):
            add(f"team settings directory empty (need >=1 file): {d}/")

    # Specific minimums
    reqs = [
        (root / "config" / "team.yaml", "config/team.yaml"),
        (root / "policies" / "retry-policy.yaml", "policies/retry-policy.yaml"),
        (root / "policies" / "resource-contention.yaml", "policies/resource-contention.yaml"),
        (root / "workflows" / "README.md", "workflows/README.md"),
    ]
    for path, label in reqs:
        if not path.is_file():
            add(f"missing {label}")

    workflow_dir = root / "workflows"
    if workflow_dir.is_dir():
        yamls = [p for p in workflow_dir.iterdir() if p.is_file() and p.suffix.lower() in (".yaml", ".yml")]
        if not yamls:
            add("workflows/: need at least one *.yaml workflow spec")

    # Research + role plan
    rm_path = root / "research" / "role-matrix.yaml"
    slugs, rm_data, rm_err = load_role_slugs(rm_path)
    if rm_err:
        add(f"role matrix: {rm_err}")
    for label in (
        "research/team-architecture.md",
        "research/template-fill-map.yaml",
    ):
        if not (root / label).is_file():
            add(f"missing {label}")

    if slugs:
        for slug in slugs:
            rp = root / "research" / f"role-{slug}.md"
            if not rp.is_file():
                add(f"missing research artefact for role `{slug}`: {rp.relative_to(root)}")

    # Agent settings
    tpl_dir = root / "agent-settings" / "templates"
    if not tpl_dir.is_dir():
        add("missing agent-settings/templates/")
    else:
        for fn, tfn in FILE_TO_TEMPLATE.items():
            if not (tpl_dir / tfn).is_file():
                add(f"missing template {tpl_dir.relative_to(root)}/{tfn} (for {fn})")

    roles_root = root / "agent-settings" / "roles"
    unknown_role_dirs: list[str] = []
    actual_slugs: list[str] = []
    if roles_root.is_dir():
        for child in sorted(roles_root.iterdir()):
            if child.name.startswith("."):
                continue
            if child.is_file():
                # allow scm placeholder only at roles root (not inside slug dirs)
                if child.name == ".gitkeep":
                    continue
                add(f"unexpected file under agent-settings/roles: {child.name}")
                continue
            if child.is_dir():
                actual_slugs.append(child.name)
    actual_slugs = sorted(set(actual_slugs))

    if slugs:
        exp = set(slugs)
        act = set(actual_slugs)
        if exp != act:
            add(
                "agent-settings/roles slug mismatch: "
                f"expected={sorted(exp)} actual={sorted(act)}"
            )
        for slug in slugs:
            rdir = roles_root / slug
            if not rdir.is_dir():
                continue
            files = sorted([p.name for p in rdir.iterdir() if p.is_file()])
            if files != ROLE_CONTEXT_FILES:
                add(
                    f"role file set mismatch for `{slug}`: have {files}, need exactly {ROLE_CONTEXT_FILES}"
                )
            extras = [p.name for p in rdir.iterdir() if p.is_dir()]
            if extras:
                add(f"extra entries (dirs) under agent-settings/roles/{slug}: {extras}")

        unknown_role_dirs = sorted(act - exp)
        if unknown_role_dirs:
            add(f"unknown role directories under agent-settings/roles: {unknown_role_dirs}")

    # roles/<slug>/HEARTBEAT.md
    op_roles = root / "roles"
    if slugs and op_roles.is_dir():
        for slug in slugs:
            hb = op_roles / slug / "HEARTBEAT.md"
            if not hb.is_file():
                add(f"missing {hb.relative_to(root)}")
            else:
                if not heartbeat_ok(hb.read_text(encoding="utf-8", errors="replace")):
                    add(f"HEARTBEAT too thin or no checklist-like content: {hb.relative_to(root)}")

    # team-model
    for label in ("team-model/operating-model.md", "team-model/raci-matrix.yaml"):
        if not (root / label).is_file():
            add(f"missing {label}")

    lines_struct.append("")
    lines_struct.append("## Result")
    lines_struct.append("")
    lines_struct.append("- status: **FAIL**" if fail else "- status: **PASS**")

    # --- Template conformance ---
    tmpl_lines: list[str] = []
    tmpl_lines.append("# template_conformance")
    tmpl_lines.append("")
    tmpl_lines.append(f"- pack_root: `{root}`")
    tmpl_lines.append(f"- generated_at_utc: `{datetime.now(timezone.utc).isoformat()}`")
    tmpl_lines.append("")
    tmpl_lines.append("## Heading extraction (## and ### only)")
    tmpl_lines.append("")

    structure_scores: list[float] = []
    depth_scores: list[float] = []
    generic_flags_total = 0
    template_map: dict[str, Any] = {}

    if tpl_dir.is_dir() and slugs and not fail:
        for slug in slugs:
            tmpl_lines.append(f"### role `{slug}`")
            for fn in ROLE_CONTEXT_FILES:
                tname = FILE_TO_TEMPLATE[fn]
                tpath = tpl_dir / tname
                rpath = roles_root / slug / fn
                key = f"{slug}/{fn}"
                if not tpath.is_file() or not rpath.is_file():
                    tmpl_lines.append(f"- **{fn}**: SKIP (missing template or rendered file)")
                    continue
                req = extract_h2_h3(tpath)
                got = extract_h2_h3(rpath)
                tmpl_lines.append(f"- **{fn}**")
                tmpl_lines.append(f"  - template: `{tpath.relative_to(root)}`")
                tmpl_lines.append(f"  - required_headings ({len(req)}): {req}")
                tmpl_lines.append(f"  - rendered_headings ({len(got)}): {got}")
                matched, score = structure_match_ordered(req, got)
                structure_scores.append(score)
                tmpl_lines.append(f"  - structure_match_score: {score:.4f}")

                body = rpath.read_text(encoding="utf-8", errors="replace")
                ds = _stub_depth_score(body)
                depth_scores.append(ds)
                gf = _stub_generic_flags(body)
                generic_flags_total += gf
                tmpl_lines.append(f"  - role_depth_score_stub: {ds:.4f}")
                tmpl_lines.append(f"  - generic_content_flags_stub: {gf}")

                professional_findings: list[str] = []
                if fn == "AGENTS.md":
                    professional_findings = _agents_professional_findings(slug, body)
                elif fn == "IDENTITY.md":
                    professional_findings = _identity_professional_findings(body)
                elif fn == "SOUL.md":
                    professional_findings = _soul_professional_findings(body)
                elif fn == "USER_PREDEFINED.md":
                    professional_findings = _user_predefined_professional_findings(body)

                if professional_findings:
                    generic_flags_total += len(professional_findings)
                    tmpl_lines.append("  - professional_findings:")
                    for pf in professional_findings:
                        tmpl_lines.append(f"    - {pf}")
                else:
                    tmpl_lines.append("  - professional_findings: []")

                template_map[key] = {
                    "template_path": str(tpath.relative_to(root)).replace("\\", "/"),
                    "required_headings": req,
                    "matched_headings": matched,
                    "structure_match_score": round(score, 4),
                    "role_depth_score_stub": round(ds, 4),
                    "generic_content_flags_stub": gf,
                    "professional_findings": professional_findings,
                }
            tmpl_lines.append("")

    global_structure = sum(structure_scores) / len(structure_scores) if structure_scores else 0.0
    global_depth = sum(depth_scores) / len(depth_scores) if depth_scores else 0.0

    tmpl_lines.append("## Aggregates")
    tmpl_lines.append("")
    tmpl_lines.append(f"- global_structure_match_score: {global_structure:.4f} (threshold {STRUCTURE_THRESHOLD})")
    tmpl_lines.append(f"- global_role_depth_score_stub: {global_depth:.4f} (threshold {DEPTH_THRESHOLD})")
    tmpl_lines.append(f"- generic_content_flags_stub_total: {generic_flags_total}")
    tmpl_lines.append("")

    tmpl_fail = False
    if structure_scores and global_structure + 1e-9 < STRUCTURE_THRESHOLD:
        tmpl_fail = True
    if depth_scores and global_depth + 1e-9 < DEPTH_THRESHOLD:
        tmpl_fail = True
    if generic_flags_total > 0:
        tmpl_fail = True

    tmpl_lines.append("## Result")
    tmpl_lines.append("")
    tmpl_lines.append("- status: **FAIL**" if tmpl_fail else "- status: **PASS**")

    if fail:
        tmpl_fail = True

    # Generation tuple
    gen_id = ""
    gen_at = ""
    commit_sha = ""
    if isinstance(rm_data, dict):
        gid = rm_data.get("generation_id")
        ga = rm_data.get("generated_at")
        cs = rm_data.get("commit_sha")
        if isinstance(gid, str):
            gen_id = gid
        if isinstance(ga, str):
            gen_at = ga
        if isinstance(cs, str):
            commit_sha = cs.lower()
    if not commit_sha:
        commit_sha = git_head(root)

    manifest: dict[str, Any] = {
        "generation_id": gen_id or "unset",
        "generated_at": gen_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit_sha": commit_sha or ("0" * 40),
        "exclude_template_sources": True,
        "layout_directories": list(LAYOUT_DIRS),
        "layout_root_files_mandatory": ["VERIFY_TEAM_PACK_REPORT.md", "DIFF_REPORT.md"],
        "team_settings": {"directories_required": list(TEAM_SETTINGS_DIRS)},
        "agent_settings": {
            "templates_dir": "agent-settings/templates",
            "roles_dir": "agent-settings/roles",
            "required_role_files": list(ROLE_CONTEXT_FILES),
            "role_slugs_expected": list(slugs),
            "role_slugs_actual": list(actual_slugs),
            "role_count_expected": len(slugs),
            "role_count_actual": len(actual_slugs),
            "unknown_role_dirs": unknown_role_dirs,
        },
        "template_map": template_map,
        "verify_tool": {"name": "verify_team_pack.py", "note": "stub headings/depth; extend rubric in pipeline"},
    }

    text_struct = "\n".join(lines_struct) + "\n"
    text_tmpl = "\n".join(tmpl_lines) + "\n"
    text_yaml = yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True)

    if args.dry_run:
        print(text_struct)
        print("---")
        print(text_tmpl)
        print("---")
        print(text_yaml)
        return 1 if (fail or tmpl_fail) else 0

    verify_dir = root / "verify"
    verify_dir.mkdir(parents=True, exist_ok=True)
    (verify_dir / "structure_conformance.md").write_text(text_struct, encoding="utf-8")
    (verify_dir / "template_conformance.md").write_text(text_tmpl, encoding="utf-8")
    (verify_dir / "package_manifest.yaml").write_text(text_yaml, encoding="utf-8")

    return 1 if (fail or tmpl_fail) else 0


if __name__ == "__main__":
    raise SystemExit(main())
