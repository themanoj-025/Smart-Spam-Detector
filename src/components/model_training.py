"""Model training module for training and evaluating multiple classifiers.

Supports Logistic Regression, Decision Tree, SVM, KNN, Random Forest,
and a Stacking ensemble classifier with comprehensive metrics logging.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any

import pandas as pd

from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
)

# Optional: XGBoost (graceful fallback if not installed)
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from src.utils.logger import get_logger
from src.utils.state import TrainingState
from src.config.config import Config, ModelConfig
from src.utils.utils import ensure_dir, save_pickle

logger = get_logger(__name__)


class ModelTraining:
    """Handles model training, hyperparameter tuning, and artifact serialization.

    Trains multiple classifiers using GridSearchCV, evaluates them on test data,
    selects the best model based on F1-score, and saves all artifacts.
    """

    def __init__(self):
        self.config = Config()
        self.param_grids = ModelConfig().models
        self.cv_config = ModelConfig()

    def _get_model_instances(self) -> Dict[str, object]:
        """Get dictionary of model name to untrained estimator instances.

        Returns:
            Dictionary mapping model names to sklearn estimators.
        """
        models = {
            'LogisticRegression': LogisticRegression(
                random_state=self.config.random_state, class_weight='balanced'
            ),
            'DecisionTree': DecisionTreeClassifier(
                random_state=self.config.random_state, class_weight='balanced'
            ),
            'SVM': SVC(
                random_state=self.config.random_state, probability=True, class_weight='balanced'
            ),
            'KNN': KNeighborsClassifier(),
            'RandomForest': RandomForestClassifier(
                random_state=self.config.random_state, class_weight='balanced'
            ),
        }
        if HAS_XGBOOST:
            models['XGBoost'] = XGBClassifier(
                random_state=self.config.random_state,
                eval_metric='logloss',
            )
        return models

    def _evaluate_model(self, model, X_test, y_test, y_pred) -> Dict[str, Any]:
        """Compute comprehensive evaluation metrics for a model.

        Args:
            model: Trained sklearn model.
            X_test: Test features.
            y_test: True test labels.
            y_pred: Predicted labels.

        Returns:
            Dictionary of metric names to values.
        """
        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
        }

    def save_pickle_files(self, state: TrainingState) -> str:
        """Save trained model, vectorizer, and metadata to disk.

        Args:
            state: Training state with trained models and metrics.

        Returns:
            Path to the output directory.
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = os.path.join(self.config.OUTPUT_BASE_DIR, timestamp)
            models_dir = os.path.join(output_dir, "models")
            observations_dir = os.path.join(output_dir, "observations")

            ensure_dir(models_dir)
            ensure_dir(observations_dir)

            # Save TF-IDF vectorizer
            save_pickle(state.tfidf_vectorizer, os.path.join(models_dir, "vectorizer.pkl"))

            # Save best model
            best_model_path = os.path.join(models_dir, f"{state.best_model_name}_model.pkl")
            save_pickle(state.best_model, best_model_path)

            # Save all trained models
            for model_name, model in state.trained_models.items():
                model_path = os.path.join(models_dir, f"{model_name}_model.pkl")
                save_pickle(model, model_path)

            # Save metadata
            metadata = {
                'timestamp': timestamp,
                'best_model_name': state.best_model_name,
                'best_model_params': str(state.best_params),
                'best_model_f1_score': float(
                    state.model_metrics[state.best_model_name]['f1_score']
                ),
                'best_model_accuracy': float(
                    state.model_metrics[state.best_model_name]['accuracy']
                ),
                'all_models_trained': list(state.trained_models.keys()),
                'tfidf_features': state.X_train_tfidf.shape[1],
                'vocabulary_size': len(state.tfidf_vectorizer.vocabulary_),
                'train_samples': len(state.y_train),
                'test_samples': len(state.y_test),
            }

            metadata_path = os.path.join(observations_dir, "model_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"All artifacts saved to: {output_dir}/")
            return output_dir

        except Exception as e:
            logger.error(f"Failed to save artifacts: {str(e)}")
            raise

    def save_metrics_to_csv(self, state: TrainingState, output_dir: str) -> None:
        """Save comprehensive metrics and comparison data as CSV files.

        Args:
            state: Training state with model metrics.
            output_dir: Base output directory.
        """
        observations_dir = os.path.join(output_dir, "observations")
        ensure_dir(observations_dir)

        # 1. Model Comparison Summary
        metrics_data = []
        for model_name, metrics in state.model_metrics.items():
            metrics_data.append({
                'Model': model_name,
                'Accuracy': round(metrics['accuracy'], 4),
                'Precision': round(metrics['precision'], 4),
                'Recall': round(metrics['recall'], 4),
                'F1_Score': round(metrics['f1_score'], 4),
                'CV_Score': round(metrics.get('best_cv_score', 0), 4),
                'Is_Best_Model': '✓' if model_name == state.best_model_name else ''
            })

        df_summary = pd.DataFrame(metrics_data)
        df_summary = df_summary.sort_values('F1_Score', ascending=False)
        df_summary.to_csv(
            os.path.join(observations_dir, "model_comparison_summary.csv"),
            index=False
        )
        logger.info("Saved: model_comparison_summary.csv")

        # 2. Best Parameters for Each Model
        params_data = []
        for model_name, metrics in state.model_metrics.items():
            best_params = metrics.get('best_params', {})
            params_data.append({
                'Model': model_name,
                'Best_Parameters': json.dumps(best_params),
                'CV_Score': round(metrics.get('best_cv_score', 0), 4)
            })

        df_params = pd.DataFrame(params_data)
        df_params.to_csv(
            os.path.join(observations_dir, "best_parameters.csv"),
            index=False
        )
        logger.info("Saved: best_parameters.csv")

        # 3. Cross-Validation Results Summary
        if state.cv_results:
            cv_summary = []
            for model_name, cv_data in state.cv_results.items():
                cv_summary.append({
                    'Model': model_name,
                    'Best_CV_Score': round(cv_data.get('best_score', 0), 4),
                    'Best_Parameters': json.dumps(cv_data.get('best_params', {}))
                })

            df_cv = pd.DataFrame(cv_summary)
            df_cv.to_csv(
                os.path.join(observations_dir, "cross_validation_summary.csv"),
                index=False
            )
            logger.info("Saved: cross_validation_summary.csv")

        # 4. Best Model Information
        best_model_info = {
            'Attribute': [
                'Best Model Name',
                'Accuracy',
                'Precision',
                'Recall',
                'F1-Score',
                'CV Score',
                'Best Parameters'
            ],
            'Value': [
                state.best_model_name,
                round(state.model_metrics[state.best_model_name]['accuracy'], 4),
                round(state.model_metrics[state.best_model_name]['precision'], 4),
                round(state.model_metrics[state.best_model_name]['recall'], 4),
                round(state.model_metrics[state.best_model_name]['f1_score'], 4),
                round(
                    state.model_metrics[state.best_model_name]
                    .get('best_cv_score', 0), 4
                ),
                json.dumps(state.best_params, indent=2),
            ]
        }

        df_best = pd.DataFrame(best_model_info)
        df_best.to_csv(
            os.path.join(observations_dir, "best_model_info.csv"),
            index=False
        )
        logger.info("Saved: best_model_info.csv")

    def train_models(self, state: TrainingState) -> TrainingState:
        """Train all models with hyperparameter tuning and select the best one.

        Args:
            state: Training state with transformed data.

        Returns:
            Updated training state with trained models and metrics.
        """
        logger.info("=" * 70)
        logger.info("MODEL TRAINING STARTED")
        logger.info("=" * 70)

        try:
            X_train = state.X_train_tfidf
            X_test = state.X_test_tfidf
            y_train = state.y_train
            y_test = state.y_test

            trained_models: Dict[str, object] = {}
            model_metrics: Dict[str, Dict[str, float]] = {}
            cv_results: Dict[str, Dict[str, Any]] = {}

            models = self._get_model_instances()

            for model_name, model in models.items():
                start_time = time.time()
                logger.info(f"\n{'─' * 50}")
                logger.info(f"Training: {model_name}")

                param_grid = self.param_grids.get(model_name, {})

                search = GridSearchCV(
                    model,
                    param_grid=param_grid,
                    cv=self.cv_config.cv_folds,
                    scoring=self.cv_config.scoring,
                    n_jobs=self.cv_config.n_jobs,
                    verbose=0,
                )

                search.fit(X_train, y_train)
                best_model = search.best_estimator_
                y_pred = best_model.predict(X_test)

                # Compute metrics
                metrics = self._evaluate_model(best_model, X_test, y_test, y_pred)
                metrics['best_params'] = search.best_params_
                metrics['best_cv_score'] = search.best_score_

                elapsed = time.time() - start_time

                trained_models[model_name] = best_model
                model_metrics[model_name] = metrics
                cv_results[model_name] = {
                    'cv_scores': search.cv_results_,
                    'best_params': search.best_params_,
                    'best_score': search.best_score_
                }

                logger.info(
                    f"Time: {elapsed:.2f}s | "
                    f"CV: {search.best_score_:.4f} | "
                    f"Acc: {metrics['accuracy']:.4f} | "
                    f"F1: {metrics['f1_score']:.4f}"
                )

            # Build stacking ensemble
            logger.info(f"\n{'─' * 50}")
            logger.info("Training: StackingClassifier (ensemble)")
            stack_start = time.time()

            # Use unfitted estimator classes for the stacking ensemble;
            # StackingClassifier handles fitting internally via cross-validation
            estimators = [
                ('lr', LogisticRegression(random_state=self.config.random_state)),
                ('dt', DecisionTreeClassifier(random_state=self.config.random_state)),
                ('rf', RandomForestClassifier(random_state=self.config.random_state)),
            ]
            stack = StackingClassifier(
                estimators=estimators,
                final_estimator=SVC(kernel='linear', probability=True),
                cv=5
            )
            stack.fit(X_train, y_train)
            y_pred_stack = stack.predict(X_test)

            stack_metrics = self._evaluate_model(stack, X_test, y_test, y_pred_stack)
            stack_metrics['best_params'] = {'estimators': 'LR+DT+RF', 'final_estimator': 'SVC(linear)'}
            stack_metrics['best_cv_score'] = 0  # No CV for stacking

            trained_models['StackingClassifier'] = stack
            model_metrics['StackingClassifier'] = stack_metrics

            logger.info(
                f"Time: {time.time() - stack_start:.2f}s | "
                f"Acc: {stack_metrics['accuracy']:.4f} | "
                f"F1: {stack_metrics['f1_score']:.4f}"
            )

            # Find best model based on F1-score
            best_model_name = max(model_metrics, key=lambda x: model_metrics[x]['f1_score'])
            best_model = trained_models[best_model_name]
            best_params = model_metrics[best_model_name]['best_params']

            logger.info(f"\n{'=' * 50}")
            logger.info(f"BEST MODEL: {best_model_name}")
            logger.info(f"F1-Score: {model_metrics[best_model_name]['f1_score']:.4f}")
            logger.info(f"Accuracy: {model_metrics[best_model_name]['accuracy']:.4f}")
            logger.info(f"Parameters: {best_params}")
            logger.info(f"{'=' * 50}")

            # Update state
            state.trained_models = trained_models
            state.model_metrics = model_metrics
            state.best_model_name = best_model_name
            state.best_model = best_model
            state.best_params = best_params
            state.cv_results = cv_results

            # Save all artifacts
            output_dir = self.save_pickle_files(state)
            self.save_metrics_to_csv(state, output_dir)

            logger.info(f"\n{'=' * 70}")
            logger.info("MODEL TRAINING COMPLETED SUCCESSFULLY")
            logger.info(f"Output directory: {output_dir}/")
            logger.info("=" * 70)

            return state

        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            raise
