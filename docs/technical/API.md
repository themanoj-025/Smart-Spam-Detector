# API — Smart-Spam-Detector: API Reference

|Field|Value|
|---|---|
|Version|v0.1|
|Last Updated|2026-08-06|
|Owner|Backend Engineer|
|Status|In Review|

Base URL (dev): `http://localhost:8000` · Versioning: `/v1` prefix.

## 1. Endpoint Summary

|Method|Path|Auth|Purpose|
|---|---|---|---|
|GET|/v1/health|N|Liveness + model version|
|POST|/v1/predict|Optional API key|Single-message classification|
|POST|/v1/predict-batch|Optional API key|Batch classification|
|GET|/v1/models|API key|List model versions|

## 2. Auth

- v1 default: open (no auth) with optional `X-API-Key` header enforcement via env flag `REQUIRE_API_KEY=true`.
- Rate limit: 60 req/min per IP (single), 10 req/min (batch).

## 3. Endpoint Details

### POST /v1/predict

**Request**

```json
{ "text": "WINNER! Claim your free prize now" }
```

**Response 200**

```json
{
  "text": "WINNER! Claim your free prize now",
  "label": "spam",
  "score": 0.991,
  "model_version": "1.2.0",
  "latency_ms": 12,
  "top_tokens": ["prize", "winner", "claim"]
}
```

**Status codes**

|Code|Meaning|
|---|---|
|200|Classified|
|400|E400_INVALID_INPUT — empty/oversized text|
|401|Missing/invalid API key (when enforced)|
|429|Rate limit exceeded|
|500|E500_INTERNAL — model unavailable|
|503|Model not loaded (E404_MODEL_NOT_FOUND variant)|

### POST /v1/predict-batch

**Request**

```json
{ "messages": ["msg one", "msg two"] }
```

**Response 200**

```json
{
  "results": [
    { "text": "msg one", "label": "ham", "score": 0.97, "top_tokens": [] },
    { "text": "msg two", "label": "spam", "score": 0.95, "top_tokens": ["free"] }
  ],
  "summary": { "total": 2, "spam": 1, "ham": 1 }
}
```

Max batch size: 100 messages; otherwise `400`.

### GET /v1/health

**Response 200**

```json
{ "status": "ok", "model_version": "1.2.0", "artifact_sha": "a3f9..." }
```

### GET /v1/models

**Response 200**

```json
{ "versions": [{ "id": "1.2.0", "status": "live", "promoted_at": "2026-09-20T10:00:00Z" }] }
```

## 4. Auth Flow (sequence)

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant K as Key store
    C->>A: POST /v1/predict + X-API-Key
    A->>K: validate key
    K-->>A: ok
    A-->>C: 200 prediction
    Note over C,A: Optional; disabled by default
```

## 5. Rate Limits & Versioning

- Policy: sliding window per IP; headers `X-RateLimit-Limit/Remaining/Reset`.
- Versioning: breaking changes → new major (`/v2`); additive → minor without prefix change.
- Deprecation: announce ≥ 3 months before removing an endpoint.

## 6. Related Documents

|Document|Relationship|
|---|---|
|[TechSpec.md](TechSpec.md)|Implementation behind these contracts|
|[Schema.md](Schema.md)|TBL-prediction record shape|
|[Testing.md](Testing.md)|Contract tests for each endpoint|
|[SecurityAndCompliance.md](SecurityAndCompliance.md)|Rate limiting and key policy|
