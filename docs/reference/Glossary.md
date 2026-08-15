# Glossary — Smart-Spam-Detector: Shared Vocabulary

| Field | Value |
| --- | --- |
| Version | v0.1 |
| Last Updated | 2026-08-06 |
| Owner | Tech Writer |
| Status | In Review |

| Term | Definition |
| --- | --- |
| Spam | Unsolicited/fraudulent message the model flags as spam |
| Ham | Legitimate message the model accepts |
| Verdict | Model output pair (label, score) |
| Score / confidence | Probability in [0,1] the label is correct |
| Top tokens | Highest-weighted terms in the prediction |
| Artifact | Serialized vectorizer/model/metrics file (`.pkl`/`.joblib`) |
| Training run | One seeded execution of the training pipeline |
| Holdout | Test split never seen during training |
| FPR (false positive rate) | Fraction of ham flagged as spam |
| F1 | Harmonic mean of precision and recall |
| Smishing | SMS-based phishing |
| Vectorizer | TF-IDF transform mapping text → sparse features |
| Model version | Semver tag of a promoted artifact set |
| Metric gate | Automated threshold check (e.g., F1 ≥ 0.97) that must pass to promote |

## Related Documents

| Document | Relationship |
| --- | --- |
| [PRD.md](../product/PRD.md) | Feature vocabulary |
| [TechSpec.md](../technical/TechSpec.md) | Technical terms |
| [AppFlow.md](../design/AppFlow.md) | Screen-level terms |
| [Schema.md](../technical/Schema.md) | Data terms (TBL-*) |
| [ImplementationPlan.md](../project/ImplementationPlan.md) | Task vocabulary |
| [Tracker.md](../project/Tracker.md) | Status terms |
| [Rules.md](../project/Rules.md) | Convention terms |
| [API.md](../technical/API.md) | API vocabulary |
| [SecurityAndCompliance.md](../technical/SecurityAndCompliance.md) | Security terms |
| [Testing.md](../technical/Testing.md) | Test vocabulary |
| [Deployment.md](../technical/Deployment.md) | Ops terms |
| [RiskRegister.md](../project/RiskRegister.md) | Risk vocabulary |
