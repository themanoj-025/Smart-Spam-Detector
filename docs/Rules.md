# Rules — Smart-Spam-Detector: Coding Standards & AI-Agent Operating Rules

| Field | Value |
|---|---|
| Version | v0.1 |
| Last Updated | 2026-08-06 |
| Owner | Staff Engineer |
| Status | Approved (pending review) |

---

## 1. Guiding Principles

1. **Reproducibility is sacred** — any training run must be repeatable with the same seed and pinned deps.
2. **Readability over cleverness** — plain code beats one-liners.
3. **No silent failures** — always log errors; never swallow exceptions.
4. **Small PRs only** — ≤ 400 lines unless justified.
5. **Explainability is a feature** — every prediction should be able to say *why*.
6. **Tests protect the model contract** — API and training contracts must be covered.

## 2. Code Style

- **Language:** Python 3.9+.
- **Formatter/linter:** ruff (line length 100).
- **Naming:** `snake_case` functions/vars, `UPPER_CASE` constants, descriptive module names.
- **Structure:**

```
Smart-Spam-Detector/
├── api.py               # FastAPI server
├── app.py               # Streamlit UI
├── classify.py          # Training/eval CLI
├── helpers.py           # Shared utils (if needed)
├── data/                # Datasets (gitignored where large)
├── models/              # Artifacts (gitignored)
└── tests/
```

## 3. Git Workflow

- **Branches:** `feature/<slug>`, `fix/<slug>`, `docs/<slug>`.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- **PRs:** small, ≥ 1 reviewer, CI must pass, merge via squash.
- **Never:** commit artifacts (`.pkl`, `.joblib`) or datasets to git unless explicitly versioned and small.

## 4. Testing Requirements

- Minimum coverage: 80% on `api.py` and `classify.py` core paths.
- MUST test: input validation, prediction contract, training determinism (same seed → same metrics).
- Optional: Streamlit UI smoke tests (manual or Playwright).
- See Testing.md for full strategy.

## 5. AI Agent Operating Rules

- Read Tracker.md and ImplementationPlan.md before starting any task.
- Never mark a task 🟢 Done without tests passing.
- Never invent requirements not in PRD.md/TechSpec.md — flag ambiguity instead of guessing.
- Always update Schema.md when the data model or artifact format changes.
- Never commit secrets; use environment variables per SecurityAndCompliance.md.
- Always pin the training seed (default 42) and document it in run metadata.
- Always cross-check Design.md before building UI components.
- When a rule conflicts with a request, state the conflict rather than silently picking one.

## 6. Security Baseline Rules

- Validate all API input (type, length ≤ 10k chars) before vectorization.
- No raw shell interpolation with user input.
- Secrets only via env vars (`.env` gitignored).
- Run dependency scan (pip-audit) in CI monthly.

## 7. Documentation Rules

- Any API change → same-PR update to API.md.
- Any schema/artifact change → same-PR update to Schema.md.
- Any new screen → update AppFlow.md inventory and navigation map.

## 8. Prohibited Patterns

| Pattern | Why |
|---|---|
| `except: pass` | Silent failures violate Principle 3 |
| Unseeded `random`/`np.random` in training | Breaks reproducibility |
| Committing `.env` or API keys | Leaks secrets |
| Hardcoded model paths in app code | Artifact version drift |
| Training inside the API request path | Latency + concurrency hazards |

## 9. Escalation Rules

**Ask a human:**
- Dataset license questions.
- Deleting/archiving historical artifacts.
- Changing the prediction contract (label set, response shape).

**Decide autonomously:**
- Internal refactors with test coverage.
- Adding metrics/logs.
- Bug fixes within defined contracts.

## 10. Related Documents

| Document | Relationship |
|---|---|
| Testing.md | Enforcement details for Section 4 |
| SecurityAndCompliance.md | Full security baseline |
| API.md | Contract changes trigger doc rules |
| PRD.md | Source of requirements |
