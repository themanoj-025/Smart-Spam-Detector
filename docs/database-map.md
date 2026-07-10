# Database Map — Smart-Spam-Detector

## Database Type
**No external database** — this application uses in-memory storage and optionally file-based history persistence.

## Data Storage
| Store | Type | Location | Purpose |
|-------|------|----------|---------|
| Prediction History | In-memory / JSON file | `history.json` (runtime) | Store past predictions |
| Model Artifacts | Pickle files | Bundled with app | Pre-trained TF-IDF + classifier |

## Entity: Prediction
| Field | Type | Description |
|-------|------|-------------|
| id | int | Prediction ID |
| text | string | Email text analyzed |
| prediction | string | "spam" or "ham" |
| confidence | float | Confidence score (0-1) |
| timestamp | datetime | When prediction was made |
| urls | list | Extracted URLs (if analyzed) |
| threat_score | float | URL threat score (if analyzed) |

## Relationships
Prediction (1) → URLs (many): One email may contain multiple URLs
