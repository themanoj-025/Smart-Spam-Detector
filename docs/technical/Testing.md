# Testing — Smart-Spam-Detector: Test Strategy

|Field|Value|
|---|---|
|Version|v0.1|
|Last Updated|2026-08-06|
|Owner|QA Engineer|
|Status|In Review|

---

## 1. Test Pyramid

```mermaid
graph TD
    E2E[E2E: Streamlit smoke (few)] --> INT[Integration: API + artifacts]
    INT --> UNIT[Unit: preprocessing, validation, metrics]
```

- Unit: ~70% of tests · Integration: ~25% · E2E: ~5%.

## 2. Unit Test Strategy

|Area|Cases|
|---|---|
|Text preprocessing|Dedupe, length cap, empty/whitespace input|
|Metric computation|F1/precision/recall edge cases (zero denominators)|
|Validation|Oversized text → 400; bad labels rejected|

## 3. Integration Test Strategy

|Area|Cases|
|---|---|
|Training determinism|Same seed + data → identical metrics|
|Artifact round-trip|Train → export → load → predict consistency|
|API contract|`/predict` shape, status codes, batch limit|

## 4. Critical Test Cases per Feature

|Feature|Case|Expected|
|---|---|---|
|Single predict|Realistic spam message|label=spam, score>0.9|
|Single predict|Empty text|400 E400_INVALID_INPUT|
|Batch|101 messages|400|
|Explainability|3-token sample|top_tokens non-empty, ≤ 10 tokens|
|Health|Artifact present|status=ok + version|

## 5. Test Data Strategy

- Fixed fixture datasets (small, synthetic) committed under `tests/fixtures/`.
- Never use production user data in CI.
- Deterministic splitter seeded to 42.

## 6. CI Gates

|Gate|Command|Blocking|
|---|---|---|
|Lint|`make lint`|Yes|
|Unit+integration|`make test`|Yes|
|Coverage|≥ 80% core paths|Yes|
|Deps audit|`pip-audit`|Yes (fail on critical)|

## 7. Related Documents

|Document|Relationship|
|---|---|
|[Rules.md](../project/Rules.md)|Testing requirements (Section 4)|
|[API.md](API.md)|Contracts under test|
|[ImplementationPlan.md](../project/ImplementationPlan.md)|TASK gates|
|[Tracker.md](../project/Tracker.md)|Test task status|
