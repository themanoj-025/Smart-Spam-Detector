# Routes — Smart-Spam-Detector

## Streamlit App Routes
| Route | File | Purpose |
|-------|------|---------|
| `/` | `app.py` | Main Streamlit UI — classify emails |

## FastAPI API Routes (`api.py`)
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/predict` | Classify email text as spam/ham |
| POST | `/analyze` | Analyze email with URL scanning |
| GET | `/history` | Get prediction history |
| GET | `/health` | Health check endpoint |

## Route Details

### `POST /predict`
- **Input**: `{ "text": "email content here" }`
- **Output**: `{ "prediction": "spam"|"ham", "confidence": 0.95 }`
- **Auth**: None required
- **Rate Limit**: None

### `POST /analyze`
- **Input**: `{ "text": "email content here" }`
- **Output**: `{ "prediction": "spam"|"ham", "urls": [...], "threat_score": 0.3 }`
- **Auth**: None required

### `GET /history`
- **Input**: Query params (limit, offset)
- **Output**: `{ "predictions": [...], "total": 100 }`
- **Auth**: None required

### `GET /health`
- **Output**: `{ "status": "ok", "model_loaded": true }`
- **Auth**: None required
