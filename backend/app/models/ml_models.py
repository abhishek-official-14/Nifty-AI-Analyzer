"""Machine learning model abstractions for directional stock prediction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover - fallback for limited runtime envs
    XGBClassifier = None


@dataclass
class ModelOutput:
    """Unified model inference output."""

    name: str
    probability_up: float


class BaseDirectionalModel:
    """Interface for pluggable directional ML classifiers."""

    name = "base"

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        raise NotImplementedError

    def predict_proba_up(self, X: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError


class SklearnDirectionalModel(BaseDirectionalModel):
    """Thin wrapper for sklearn-compatible binary classifiers."""

    def __init__(self, name: str, estimator: object, needs_scaling: bool = False) -> None:
        self.name = name
        self.model = Pipeline([("scaler", StandardScaler()), ("estimator", estimator)]) if needs_scaling else estimator

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        self.model.fit(X, y)

    def predict_proba_up(self, X: pd.DataFrame) -> np.ndarray:
        proba = self.model.predict_proba(X)
        return proba[:, 1]


class MLPredictionEngine:
    """Train and infer with multiple models, then aggregate probabilities."""

    def __init__(self, models: Iterable[BaseDirectionalModel] | None = None) -> None:
        self.models: list[BaseDirectionalModel] = list(models) if models is not None else self._default_models()

    def _default_models(self) -> list[BaseDirectionalModel]:
        """Create default model set: RF, XGBoost, Gradient Boosting."""
        models: list[BaseDirectionalModel] = [
            SklearnDirectionalModel(
                name="random_forest",
                estimator=RandomForestClassifier(
                    n_estimators=250,
                    max_depth=6,
                    min_samples_leaf=3,
                    random_state=42,
                ),
            ),
            SklearnDirectionalModel(
                name="gradient_boosting",
                estimator=GradientBoostingClassifier(
                    n_estimators=200,
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=42,
                ),
            ),
        ]

        if XGBClassifier is not None:
            models.append(
                SklearnDirectionalModel(
                    name="xgboost",
                    estimator=XGBClassifier(
                        n_estimators=200,
                        learning_rate=0.05,
                        max_depth=4,
                        subsample=0.9,
                        colsample_bytree=0.9,
                        objective="binary:logistic",
                        eval_metric="logloss",
                        random_state=42,
                    ),
                )
            )
        return models

    def train(self, features: pd.DataFrame, target: pd.Series) -> None:
        """Fit all configured models on the same feature matrix."""
        for model in self.models:
            model.fit(features, target)

    def predict_ensemble(self, feature_row: pd.DataFrame) -> dict[str, float | list[ModelOutput]]:
        """Predict bullish probability using all models and a mean ensemble."""
        outputs: list[ModelOutput] = []
        for model in self.models:
            prob = float(model.predict_proba_up(feature_row)[0])
            outputs.append(ModelOutput(name=model.name, probability_up=prob))

        mean_probability = float(np.mean([o.probability_up for o in outputs])) if outputs else 0.5
        return {
            "ensemble_probability": round(mean_probability, 4),
            "model_outputs": outputs,
        }
