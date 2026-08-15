# File Move Ledger — Smart-Spam-Detector

Restructure date: **2026-08-11** (v6) · Method: `git mv` · Branch: `main`
(local commits, no push).

## Moved Files

| # | Old Path | New Path | Category | Reason | Risk | Verified? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `docs/migration_summary.md` | `docs/migration/migration_summary.md` | Meta → Docs | Consolidate migration records under `docs/migration/` (protocol Phase 6) | Low (0 refs) | ✅ |

## Files Rewritten

| Path | Reason |
| --- | --- |
| `docs/architecture.md` | 3-line stub → full architecture (src-layout, 3 interfaces). |
| `docs/folder_structure.md` | 10-line stub → accurate annotated tree. |

## Files Added

`docs/module_dependency.md`, `docs/startup_flow.md`, `docs/package_overview.md`,
`docs/migration/old_tree_to_new_tree.md`, `docs/migration/file_move_ledger.md` —
Phase 6 deliverables.

## Files Deliberately NOT MOVED (contract analysis)

| Path | Why it stays | Risk if moved |
| --- | --- | --- |
| `api.py` / `app.py` / `classify.py` | Docker `COPY api.py app.py classify.py` + `CMD uvicorn api:app` / `streamlit run app.py`; Makefile compileall; labeler glob | High |
| `src/` | CI import checks (`from src.* import ...`), Makefile compileall, all entry points import it | High — src-layout is canonical |
| `outputs/2026-06-01_18-54-30/` | Tracked canonical run (artifact contract in `src/config/config.py` + `.gitignore` negations) | High |
| `data/`, `tests/` | Already canonical | Medium |

## Untracked / Out of Scope (no action)

| Path | Note |
| --- | --- |
| `logs/` | Gitignored runtime logs — untracked. |
| `Notebook Experiments/Spam Email Detection.ipynb` | Untracked local folder (not in git). If it should be part of the repo, add it deliberately under `notebooks/` in a separate commit. |

## Flagged (follow-up backlog)

| Item | Flag |
| --- | --- |
| `Notebook Experiments/` naming/location | Non-canonical name with spaces; untracked today. If committed, rename to `notebooks/spam_email_detection.ipynb`. |
| `outputs/` multi-run retention | Policy is "keep latest run"; older tracked run dirs (if ever added) should be pruned deliberately. |

## Deletions

None in this restructure.
