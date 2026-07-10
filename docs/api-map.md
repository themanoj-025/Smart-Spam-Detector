# API Map — Smart-Spam-Detector

## REST API (`api.py`)

### Endpoints
| Method | Route | Handler | Input | Output | Purpose |
|--------|-------|---------|-------|--------|---------|
| POST | `/predict` | predict() | `{ "text": str }` | `{ "prediction": str, "confidence": float }` | Classify email |
| POST | `/analyze` | analyze_text() | `{ "text": str }` | `{ "prediction": str, "urls": list, "threat_score": float }` | Analyze with URL scanning |
| GET | `/history` | get_history() | Query params | `{ "predictions": list, "total": int }` | Prediction history |
| GET | `/health` | health_check() | None | `{ "status": str, "model_loaded": bool }` | Health check |

## Internal Module APIs

### Classification Engine (`classify.py`)
| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `classify(text)` | Raw email text | `(label, confidence)` | Main classification function |
| `vectorize(text)` | Raw text | TF-IDF sparse matrix | Transform text to features |
| `train(data, labels)` | Training data | Trained model | Train classifier |
| `load_model()` | None | Loaded model | Load saved model from disk |

### URL Analyzer (`tests/test_url_analyzer.py`)
| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `extract_urls(text)` | Email text | List of URLs | Extract embedded URLs |
| `analyze_url(url)` | URL string | Risk score | Assess URL threat level |

## External Integrations
None — fully self-contained with pre-trained model.
