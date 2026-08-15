# Old Tree → New Tree — Smart-Spam-Detector

Restructure performed **2026-08-11** (v6, Principal Architect protocol). The repo
already used the canonical **src-layout** (`src/components|config|pipeline|utils`) with
three thin root entry points and a real test suite; this pass consolidates migration
records and replaces stub docs with the Phase 6 suite. **Zero code/import/entry-point
changes.**

## Before (2026-08-10)

```
Smart-Spam-Detector/
├── api.py · app.py · classify.py
├── src/ (config, components/, pipeline/, utils/)
├── tests/ (8 modules)
├── data/dataset/dataset.csv
├── outputs/2026-06-01_18-54-30/ (tracked canonical run)
├── logs/ (untracked) · Notebook Experiments/ (untracked)
├── docs/
│   ├── architecture.md           (STUB — 3 lines)
│   ├── folder_structure.md       (STUB — 10 lines)
│   ├── migration_summary.md      (root of docs/)
│   ├── community/ design/ product/ project/ reference/ technical/
├── .github/workflows/ · .vscode/
├── Dockerfile · docker-compose*.yml · Makefile
├── pyproject.toml · requirements*.txt · packages.txt · runtime.txt · uv.lock
├── .pre-commit-config.yaml · .python-version · .env.example
├── README.md · PROJECT_OVERVIEW.md · PROJECT_ANALYSIS.md · AGENTS.md
└── .gitignore · .dockerignore · .editorconfig · .gitattributes
```

## After (2026-08-11)

```
Smart-Spam-Detector/
├── api.py · app.py · classify.py                      (unchanged — entry contract)
├── src/ · tests/ · data/ · outputs/                   (unchanged)
├── logs/ · Notebook Experiments/                      (untracked, untouched)
├── docs/
│   ├── architecture.md            (REWRITTEN)
│   ├── folder_structure.md        (REWRITTEN)
│   ├── module_dependency.md       (NEW)
│   ├── startup_flow.md            (NEW)
│   ├── package_overview.md        (NEW)
│   ├── migration/
│   │   ├── migration_summary.md   (MOVED from docs/)
│   │   ├── old_tree_to_new_tree.md (NEW — this file)
│   │   └── file_move_ledger.md    (NEW)
│   ├── community/ design/ product/ project/ reference/ technical/   (unchanged)
├── .github/workflows/ · .vscode/                      (unchanged)
├── Dockerfile · docker-compose*.yml · Makefile         (unchanged)
├── pyproject.toml · requirements*.txt · packages.txt · runtime.txt · uv.lock (unchanged)
├── .pre-commit-config.yaml · .python-version · .env.example           (unchanged)
├── README.md · PROJECT_OVERVIEW.md · PROJECT_ANALYSIS.md · AGENTS.md   (unchanged)
└── .gitignore · .dockerignore · .editorconfig · .gitattributes         (unchanged)
```

## Summary

| Kind | Count |
| --- | --- |
| Files moved (`git mv`) | 1 |
| Docs rewritten (stubs → real) | 2 |
| Docs added | 5 |
| Code / imports / entry points / CI / Docker changed | 0 |
| Deleted | 0 |
