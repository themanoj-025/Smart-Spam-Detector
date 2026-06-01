"""Model comparison utilities for the Model Comparison Dashboard.

Loads all trained models from the latest training run, computes confusion
matrices, and provides Plotly figures for radar charts and heatmaps.
"""

import os
import re
import glob
from typing import Dict, List, Optional, Any
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from src.utils.utils import load_pickle
from src.utils.logger import get_logger
from src.config.config import Config

logger = get_logger(__name__)


class ModelComparison:
    """Loads and compares all trained models from the latest training run.

    Provides metrics, confusion matrices, and Plotly-ready data for
    the Streamlit Model Comparison Dashboard.
    """

    MODELS_ORDER = [
        "LogisticRegression",
        "DecisionTree",
        "SVM",
        "KNN",
        "RandomForest",
        "StackingClassifier",
    ]

    METRIC_LABELS = {
        "accuracy": "Accuracy",
        "precision": "Precision",
        "recall": "Recall",
        "f1_score": "F1-Score",
    }

    def __init__(self):
        self.config = Config()
        self.models: Dict[str, Any] = {}
        self.metrics: Dict[str, Dict[str, float]] = {}
        self.confusion_matrices: Dict[str, np.ndarray] = {}
        self.best_model_name: Optional[str] = None
        self.class_names: List[str] = ["Spam", "Ham"]
        self.run_dir: Optional[str] = None
        self._loaded = False
        self._error_message: Optional[str] = None

        # Test data (loaded lazily for computing confusion matrices)
        self.X_test: Optional[np.ndarray] = None
        self.y_test: Optional[np.ndarray] = None

    def _discover_latest_run(self) -> Optional[str]:
        """Find the most recent timestamped training run directory.

        Returns:
            Path to the latest run directory, or None if none found.
        """
        base_dir = Path(self.config.OUTPUT_BASE_DIR)
        if not base_dir.exists():
            return None

        run_dirs = sorted(
            [
                d for d in base_dir.iterdir()
                if d.is_dir()
                and re.match(
                    r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$",
                    d.name,
                )
            ],
            reverse=True,
        )

        return str(run_dirs[0]) if run_dirs else None

    def _load_metrics_from_csv(self, run_dir: str) -> bool:
        """Load model metrics from the saved CSV files in a training run.

        Args:
            run_dir: Path to the training run directory.

        Returns:
            True if metrics were loaded successfully.
        """
        obs_dir = os.path.join(run_dir, "observations")
        summary_path = os.path.join(obs_dir, "model_comparison_summary.csv")
        best_info_path = os.path.join(obs_dir, "best_model_info.csv")

        if not os.path.exists(summary_path):
            return False

        try:
            df = pd.read_csv(summary_path)
            for _, row in df.iterrows():
                name = row["Model"]
                self.metrics[name] = {
                    "accuracy": float(row["Accuracy"]),
                    "precision": float(row["Precision"]),
                    "recall": float(row["Recall"]),
                    "f1_score": float(row["F1_Score"]),
                }

            # Load best model name
            if os.path.exists(best_info_path):
                df_best = pd.read_csv(best_info_path)
                best_row = df_best[df_best["Attribute"] == "Best Model Name"]
                if not best_row.empty:
                    self.best_model_name = best_row.iloc[0]["Value"]

            logger.info(f"Loaded metrics for {len(self.metrics)} models from CSV")
            return True

        except Exception as e:
            logger.warning(f"Could not load metrics CSV: {e}")
            return False

    def _load_all_models(self, run_dir: str) -> bool:
        """Load all trained model pickle files from a training run.

        Args:
            run_dir: Path to the training run directory.

        Returns:
            True if at least one model was loaded.
        """
        models_dir = os.path.join(run_dir, "models")
        if not os.path.exists(models_dir):
            return False

        model_files = glob.glob(os.path.join(models_dir, "*_model.pkl"))
        if not model_files:
            return False

        for model_path in model_files:
            basename = os.path.basename(model_path)
            # Extract model name (e.g., "SVM_model.pkl" -> "SVM")
            name = basename.replace("_model.pkl", "")
            try:
                model = load_pickle(model_path)
                self.models[name] = model
                logger.info(f"  Loaded: {name}")
            except Exception as e:
                logger.warning(f"  Failed to load {name}: {e}")

        # Also load the vectorizer
        vec_path = os.path.join(models_dir, "vectorizer.pkl")
        if os.path.exists(vec_path):
            try:
                self.vectorizer = load_pickle(vec_path)
            except Exception:
                self.vectorizer = None
        else:
            self.vectorizer = None

        return len(self.models) > 0

    def _prepare_test_data(self) -> bool:
        """Load and transform the test data for computing confusion matrices.

        Loads the original dataset, applies the same train/test split and
        TF-IDF vectorization, and stores the test features and labels.

        Returns:
            True if test data was prepared successfully.
        """
        if self.X_test is not None and self.y_test is not None:
            return True

        try:
            # Load dataset
            df = pd.read_csv(self.config.training_data_path)
            label_mapping = {"spam": 0, "ham": 1}
            df["Category"] = df["Category"].map(label_mapping).astype(int)

            X = df["Message"]
            y = np.array(df["Category"], dtype=int)

            # Split (same seed as training pipeline)
            _, X_test, _, y_test = train_test_split(
                X, y,
                test_size=self.config.test_size,
                random_state=self.config.random_state,
                stratify=y,
            )

            # Vectorize (use loaded vectorizer if available, else fit fresh)
            if self.vectorizer is not None:
                X_test_vec = self.vectorizer.transform(X_test)
            else:
                vec = TfidfVectorizer(lowercase=True, stop_words="english")
                # We need the full training data to fit — this is approximate
                # In practice, the vectorizer should always be saved alongside models
                X_train, _, _, _ = train_test_split(
                    X, y,
                    test_size=self.config.test_size,
                    random_state=self.config.random_state,
                    stratify=y,
                )
                X_combined = pd.concat([X_train, X_test])
                vec.fit(X_combined)
                X_test_vec = vec.transform(X_test)
                self.vectorizer = vec

            self.X_test = X_test_vec
            self.y_test = y_test
            logger.info(f"Test data prepared: {X_test_vec.shape[0]} samples")
            return True

        except Exception as e:
            logger.warning(f"Could not prepare test data: {e}")
            return False

    def compute_confusion_matrices(self) -> None:
        """Compute confusion matrices for all loaded models.

        Requires that models and test data are already loaded.
        """
        if not self.models:
            return

        if self.X_test is None or self.y_test is None:
            if not self._prepare_test_data():
                return

        for name, model in self.models.items():
            try:
                y_pred = model.predict(self.X_test)
                cm = confusion_matrix(self.y_test, y_pred)
                self.confusion_matrices[name] = cm
                logger.info(f"  Confusion matrix computed for {name}")
            except Exception as e:
                logger.warning(f"  Could not compute CM for {name}: {e}")

    def load(self, run_dir: Optional[str] = None) -> bool:  # noqa: C901
        """Load all model data from a training run.

        Args:
            run_dir: Specific run directory. If None, discovers the latest.

        Returns:
            True if data was loaded successfully.
        """
        if self._loaded:
            return True

        if run_dir is None:
            run_dir = self._discover_latest_run()

        if run_dir is None:
            self._error_message = (
                "No training runs found. Please train models first:\n"
                "  python -m src.pipeline.training_pipeline"
            )
            return False

        self.run_dir = run_dir

        # Load metrics from CSV if available
        metrics_loaded = self._load_metrics_from_csv(run_dir)

        # Load model objects
        models_loaded = self._load_all_models(run_dir)

        if not metrics_loaded and not models_loaded:
            self._error_message = (
                f"No model data found in: {run_dir}"
            )
            return False

        # If models are loaded, compute confusion matrices
        if self.models:
            self.compute_confusion_matrices()

            # If we have models but no metrics, compute metrics from predictions
            if not metrics_loaded and self.X_test is not None:
                for name, model in self.models.items():
                    try:
                        y_pred = model.predict(self.X_test)
                        self.metrics[name] = {
                            "accuracy": accuracy_score(self.y_test, y_pred),
                            "precision": precision_score(
                                self.y_test, y_pred,
                                average="weighted", zero_division=0,
                            ),
                            "recall": recall_score(
                                self.y_test, y_pred,
                                average="weighted", zero_division=0,
                            ),
                            "f1_score": f1_score(
                                self.y_test, y_pred,
                                average="weighted", zero_division=0,
                            ),
                        }
                    except Exception:
                        pass

        # Determine best model
        if self.metrics and not self.best_model_name:
            self.best_model_name = max(self.metrics, key=lambda x: self.metrics[x]["f1_score"])

        self._loaded = True
        return True

    def get_comparison_df(self) -> pd.DataFrame:
        """Get a DataFrame of model metrics sorted by F1-score descending.

        Returns:
            DataFrame with columns: Model, Accuracy, Precision, Recall, F1-Score, Best.
        """
        rows = []
        for name, metrics in self.metrics.items():
            rows.append({
                "Model": name,
                "Accuracy": round(metrics.get("accuracy", 0), 4),
                "Precision": round(metrics.get("precision", 0), 4),
                "Recall": round(metrics.get("recall", 0), 4),
                "F1-Score": round(metrics.get("f1_score", 0), 4),
                "Best": "⭐" if name == self.best_model_name else "",
            })

        df = pd.DataFrame(rows)
        if not df.empty and "F1-Score" in df.columns:
            df = df.sort_values("F1-Score", ascending=False).reset_index(drop=True)
        return df

    def get_radar_chart(self) -> Any:
        """Generate a Plotly radar/spider chart comparing all models.

        Returns:
            A plotly.graph_objects.Figure object, or None if no data.
        """
        if not self.metrics:
            return None

        import plotly.graph_objects as go

        # Metrics to plot (omit f1_score — it's a composite; include the individual ones)
        radar_metrics = ["accuracy", "precision", "recall"]
        metric_labels = [self.METRIC_LABELS[m] for m in radar_metrics]

        fig = go.Figure()

        # Color palette for models
        colors = [
            "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
            "#FFA15A", "#19D3F3", "#FF6692", "#B6E880",
        ]

        for i, (name, metrics) in enumerate(
            sorted(self.metrics.items(), key=lambda x: x[1].get("f1_score", 0), reverse=True)
        ):
            values = [metrics.get(m, 0) * 100 for m in radar_metrics]
            # Close the loop by repeating the first value
            values_closed = values + [values[0]]
            labels_closed = metric_labels + [metric_labels[0]]

            color = colors[i % len(colors)]
            line_width = 3 if name == self.best_model_name else 1.5
            opacity = 1.0 if name == self.best_model_name else 0.7

            fig.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=labels_closed,
                name=f"{name} {'⭐' if name == self.best_model_name else ''}",
                line=dict(color=color, width=line_width),
                opacity=opacity,
                fill="toself",
                fillcolor=f"rgba{self._hex_to_rgba(color, 0.08)}",  # noqa
            ))

        # Compute dynamic range: round down min value to nearest 5%
        all_vals = [
            metrics.get(m, 0) * 100
            for metrics in self.metrics.values()
            for m in radar_metrics
        ]
        min_val = (min(all_vals) // 5) * 5 if all_vals else 85
        max_val = 100
        # Ensure at least a 5% spread
        if max_val - min_val < 10:
            min_val = max(0, min_val - 5)

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[min_val, max_val],
                    tickfont=dict(size=11),
                    gridcolor="#e0e0e0",
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, weight="bold"),
                    gridcolor="#e0e0e0",
                ),
                bgcolor="rgba(0,0,0,0)",
            ),
            title=dict(
                text="Model Performance Comparison (Radar Chart)",
                font=dict(size=16),
                x=0.5,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=11),
            ),
            margin=dict(l=80, r=80, t=60, b=60),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="var(--text-primary, #1a1a2e)"),
            template="plotly_white",
            hovermode="closest",
        )

        return fig

    def get_confusion_matrix_heatmap(self, model_name: str) -> Any:
        """Generate a Plotly confusion matrix heatmap for a specific model.

        Args:
            model_name: Name of the model to display.

        Returns:
            A plotly.graph_objects.Figure, or None if no data.
        """
        if model_name not in self.confusion_matrices:
            return None

        import plotly.graph_objects as go

        cm = self.confusion_matrices[model_name]
        is_best = model_name == self.best_model_name

        # Normalize to percentages for coloring
        cm_pct = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100

        annotations = []
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                annotations.append(dict(
                    text=f"{cm[i, j]}<br><sub>{cm_pct[i, j]:.1f}%</sub>",
                    x=j,
                    y=i,
                    font=dict(size=13, color="white" if cm_pct[i, j] > 40 else "#333"),
                    showarrow=False,
                ))

        fig = go.Figure(data=go.Heatmap(
            z=cm_pct,
            x=self.class_names,
            y=self.class_names,
            text=[[str(cm[i, j]) for j in range(cm.shape[1])] for i in range(cm.shape[0])],
            texttemplate="%{text}",
            hovertemplate="True: %{y}<br>Predicted: %{x}<br>Count: %{text}<br>Rate: %{z:.1f}%<extra></extra>",
            colorscale="Blues",
            showscale=True,
            colorbar=dict(
                title="%",
                tickformat=".0f",
                thickness=15,
                len=0.7,
            ),
        ))

        fig.update_layout(
            title=dict(
                text=f"{'⭐ ' if is_best else ''}{model_name} — Confusion Matrix",
                font=dict(size=14),
                x=0.5,
            ),
            xaxis=dict(title="Predicted Label", side="bottom", tickfont=dict(size=12)),
            yaxis=dict(title="True Label", tickfont=dict(size=12), autorange="reversed"),
            margin=dict(l=60, r=40, t=50, b=60),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="var(--text-primary, #1a1a2e)"),
            width=400,
            height=360,
        )

        return fig

    def get_all_confusion_matrices(self) -> Dict[str, Any]:
        """Get confusion matrix heatmaps for all models that have them.

        Returns:
            Dict of model_name -> plotly figure.
        """
        return {
            name: self.get_confusion_matrix_heatmap(name)
            for name in self.models
            if name in self.confusion_matrices
        }

    @staticmethod
    def _hex_to_rgba(hex_color: str, alpha: float = 0.2) -> tuple:
        """Convert hex color string to rgba tuple.

        Args:
            hex_color: Hex color string (e.g., "#636EFA").
            alpha: Alpha channel value (0-1).

        Returns:
            Tuple of (r, g, b, a) integers.
        """
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, alpha)

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def model_names(self) -> List[str]:
        """Get list of model names in canonical order."""
        names = list(self.models.keys())
        return [m for m in self.MODELS_ORDER if m in names]
