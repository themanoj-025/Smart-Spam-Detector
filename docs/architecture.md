# Smart-Spam-Detector — Architecture

```mermaid
graph TB
    subgraph UI ["User Interfaces"]
        A[Streamlit App - app.py]
        B[FastAPI API - api.py]
    end

    subgraph Pipeline ["ML Pipeline"]
        C[src/components/data_ingestion.py]
        D[src/components/data_transformation.py]
        E[src/components/model_training.py]
        F[src/pipeline/training_pipeline.py]
        G[src/pipeline/prediction_pipeline.py]
    end

    subgraph Utils ["Utilities"]
        H[src/utils/email_utils.py]
        I[src/utils/url_analyzer.py]
        J[src/utils/history_manager.py]
        K[src/utils/report_generator.py]
        L[src/utils/model_comparison.py]
    end

    subgraph Config ["Configuration"]
        M[src/config/config.py]
    end

    subgraph Models ["Trained Models"]
        N[outputs/{timestamp}/models/*.pkl]
    end

    UI --> Pipeline
    UI --> Utils
    Pipeline --> M
    Pipeline --> N
    Utils --> M
    A --> G
    B --> G
```

## Key Patterns

- **Bearer token auth**: API protected by `SPAM_API_KEY` environment variable
- **Rate limiting**: slowapi per-key rate limiting to prevent API abuse
- **Model auto-discovery**: `Config.__post_init__()` scans `outputs/{}` for latest trained model
- **Multiple classifiers**: Logistic Regression, Decision Tree, SVM, KNN, Random Forest, XGBoost, Stacking
- **SHAP explanations**: Model explainability via SHAP word-level contributions
- **MBOX support**: Email processing from MBOX files with text extraction and classification
