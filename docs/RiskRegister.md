# RiskRegister — Smart-Spam-Detector: Known Risks & Mitigations

| Field | Value |
|---|---|
| Version | v0.1 |
| Last Updated | 2026-08-06 |
| Owner | Program Manager |
| Status | In Review |

| ID | Risk | Likelihood | Impact | Score | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| R-01 | Training data too small / skewed | Medium | High | 9 | Curate multi-source datasets; stratified split; augment | DS | Open |
| R-02 | Classifier overfits (high val, low test F1) | Medium | Medium | 6 | CV + early stopping + regularized models | DS | Open |
| R-03 | Data poisoning / mislabeled rows | Medium | High | 9 | Dedupe + label audit + validation gates | DS | Open |
| R-04 | Model drift as spam evolves | High | Medium | 8 | Scheduled retraining + drift monitor | DS | Open |
| R-05 | Slow inference under batch load | Low | Medium | 4 | Vectorized batch predict + load test | Eng | Open |
| R-06 | API abuse / scraping | Medium | Medium | 6 | Rate limiting + optional API keys | Sec | Open |
| R-07 | Artifact version skew (train vs serve) | Medium | High | 9 | Manifest with sha256; version log at startup | Eng | Open |
| R-08 | Dependency CVE | Medium | Medium | 6 | pip-audit monthly + dependabot | DevOps | Open |
| R-09 | PII leakage via logs | Medium | Medium | 6 | Log truncation + no storage by default | Sec | Open |

## Risk Matrix

```mermaid
quadrantChart
    title Risk Prioritization
    x-axis Low Likelihood --> High Likelihood
    y-axis Low Impact --> High Impact
    quadrant-1 Watch: R-05
    quadrant-2 Manage: R-02, R-08, R-06, R-09
    quadrant-3 Avoid: R-04
    quadrant-4 Critical: R-01, R-03, R-07
```

## Top 3 Focus Risks

1. **R-07 Artifact version skew** — enforced via sha256 manifests (see Schema.md TBL-artifact).
2. **R-03 Data quality** — validation gates block promotion when metrics drop below F1 0.97.
3. **R-04 Drift** — quarterly retraining cadence with documented FPR trend.

## Related Documents

| Document | Relationship |
|---|---|
| PRD.md | Summarizes top risks (Section 10) |
| SecurityAndCompliance.md | Security risks detail |
| TechSpec.md | Technical risk mitigations |
| Tracker.md | Risk status updates |
