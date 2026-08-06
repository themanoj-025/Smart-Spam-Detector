# SecurityAndCompliance — Smart-Spam-Detector: Security & Compliance

|Field|Value|
|---|---|
|Version|v0.1|
|Last Updated|2026-08-06|
|Owner|Security Engineer|
|Status|In Review|

---

## 1. Threat Model (STRIDE)

|Threat|Asset|Mitigation|
|---|---|---|
|Spoofing|API identity|Optional API keys; signature on artifacts (sha256)|
|Tampering|Model artifacts|Hash verification at load; read-only artifact dir|
|Repudiation|Prediction records|Structured audit log with request ids|
|Info disclosure|Message text (PII)|TLS in prod; log truncation to 100 chars|
|DoS|API endpoints|Rate limiting (60/10 req/min); max batch 100|
|Elevation|Admin functions|No admin surface in v1; env-based config only|

## 2. Auth & Authz

- v1: service open by default (self-hosted trust boundary).
- Optional: `REQUIRE_API_KEY=true` enables `X-API-Key` check (constant-time compare).
- No user accounts, roles, or multi-tenancy in v1 (see PRD Non-Goals).

## 3. Data Classification

|Class|Examples|Handling|
|---|---|---|
|PII (possible)|Message text, prediction text|TLS in transit, log truncation, optional at-rest encryption|
|Public|Dataset metadata, metrics|No restriction|
|Secret|API keys, env secrets|Never committed; env vars / secret manager|

## 4. Encryption Standards

- In transit: TLS 1.2+ (prod reverse proxy).
- At rest: optional volume encryption; artifacts integrity via sha256 rather than encryption (model weights not sensitive).

## 5. Compliance Checklist

- [ ] GDPR: right to erasure supported via hard-delete utility for stored texts.
- [ ] Data minimization: no storage of predictions unless explicitly enabled.
- [ ] Logging: no raw full message bodies in logs.
- [ ] Dependency scanning: monthly `pip-audit` in CI.

## 6. Incident Response (Outline)

1. Detect: alert on 5xx spikes or /health failures.
2. Triage: check deploy history + recent artifact changes.
3. Mitigate: roll back model artifact or redeploy previous image.
4. Recover: restore from versioned artifacts; verify metrics gate.
5. Postmortem: log entry in ../project/Tracker.md changelog within 48h.

## 7. Related Documents

|Document|Relationship|
|---|---|
|[TechSpec.md](TechSpec.md)|NFR security targets|
|[Rules.md](../project/Rules.md)|Security baseline rules (Section 6)|
|[API.md](API.md)|Auth + rate limit specifics|
|[RiskRegister.md](../project/RiskRegister.md)|Security risks R-06..R-09|
