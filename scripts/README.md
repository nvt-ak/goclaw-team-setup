# Team pack verification (stub)

Implements a mechanical check + report generation aligned with `SKILL.md` v12:

- `verify/structure_conformance.md`
- `verify/template_conformance.md`
- `verify/package_manifest.yaml`

## Setup

```bash
pip install -r scripts/requirements-verify.txt
```

## Usage

From the **team-pack root** (directory that should contain `config/`, `research/`, …):

```bash
python3 scripts/verify_team_pack.py --root .
```

Options:

- `--dry-run` — print findings; do not write files under `verify/`.
- `--strict-extra-top-level` — fail if any unexpected top-level entry exists (besides hidden dirs like `.git`).

Exit code `0` when all gates in this tool pass; non-zero otherwise.

**Note:** This repository root is a *skill bundle*, not a full generated pack; running the verifier here is expected to report many missing artifacts until you scaffold a pack.