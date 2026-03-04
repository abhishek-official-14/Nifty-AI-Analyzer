"""AI prediction service that combines ML forecasts with weighted market scoring."""

from __future__ import annotations

from dataclasses import asdict

import numpy as np
import pandas as pd

from app.models.ml_models import MLPredictionEngine
from app.services.data_fetcher import DataFetcher, NIFTY50_SYMBOLS
from app.services.fundamental_analysis import FundamentalAnalysisService
from app.services.market_breadth import MarketBreadthService
from app.services.option_chain_analysis import OptionChainAnalysisService
from app.services.sector_rotation import SectorRotationService
from app.services.technical_analysis import TechnicalAnalysisService


class AIPredictionService:
    """Generate AI trade signals using technical/options/fundamental + ML ensemble."""

    def __init__(
        self,
        fetcher: DataFetcher,
        technical_service: TechnicalAnalysisService,
        fundamental_service: FundamentalAnalysisService,
        breadth_service: MarketBreadthService,
        sector_service: SectorRotationService,
        option_chain_service: OptionChainAnalysisService,
    ) -> None:
        self.fetcher = fetcher
        self.technical_service = technical_service
        self.fundamental_service = fundamental_service
        self.breadth_service = breadth_service
        self.sector_service = sector_service
        self.option_chain_service = option_chain_service

    def generate_signals(self, symbols: list[str] | None = None, limit: int = 5) -> dict[str, object]:
        """Build directional AI signals for requested symbols."""
        chosen = symbols or [s.replace(".NS", "") for s in NIFTY50_SYMBOLS[:limit]]
        quotes = self.fetcher.fetch_nifty50_quotes()
        breadth = self.breadth_service.calculate_breadth(quotes)
        breadth_score = self._breadth_to_score(breadth)
        options_analysis = self.option_chain_service.get_analysis()
        options_score = float(options_analysis.get("options_score", 50.0))
        sector_scores = {
            row["sector"]: float(row["strength_score"]) for row in self.sector_service.get_sector_strength().get("sectors", [])
        }

        signals: list[dict[str, object]] = []
        for symbol in chosen:
            candles = self.fetcher.fetch_ohlc(symbol, period="1y", interval="1d")
            if candles.empty:
                continue

            indicators = self.technical_service.compute_indicators(candles)
            fundamentals = self.fundamental_service.get_fundamental_snapshot(symbol.upper())
            sector_strength = self._resolve_sector_strength(symbol, sector_scores)
            ml_block = self._ml_predict(symbol, candles, options_score, breadth_score, sector_strength)

            final_score = self._final_ai_score(
                technical=indicators["technical_score"],
                options=options_score,
                fundamental=float(fundamentals["fundamental_score"]),
                market_breadth=breadth_score,
                sector_strength=sector_strength,
                ml_prediction=ml_block["ml_score"],
            )
            signal = self._build_signal(symbol, candles, ml_block, final_score)
            signal["score_breakdown"] = {
                "technical": round(indicators["technical_score"], 2),
                "options": round(options_score, 2),
                "fundamental": round(float(fundamentals["fundamental_score"]), 2),
                "market_breadth": round(breadth_score, 2),
                "sector_strength": round(sector_strength, 2),
                "ml_prediction": round(float(ml_block["ml_score"]), 2),
                "final_ai_score": final_score,
            }
            signal["ml_models"] = ml_block["models"]
            signals.append(signal)

        return {
            "signals": signals,
            "market_context": {
                "options_score": options_score,
                "market_breadth": breadth,
            },
        }

    def _ml_predict(
        self,
        symbol: str,
        candles: pd.DataFrame,
        options_score: float,
        breadth_score: float,
        sector_strength: float,
    ) -> dict[str, object]:
        features, target = self._build_training_set(candles, options_score, breadth_score, sector_strength)
        if len(features) < 30 or target.nunique() < 2:
            features, target = self._mock_training_data(symbol, options_score, breadth_score, sector_strength)

        engine = MLPredictionEngine()
        engine.train(features, target)
        latest_features = features.tail(1)
        ensemble = engine.predict_ensemble(latest_features)

        up_probability = float(ensemble["ensemble_probability"])
        direction = "Bullish" if up_probability >= 0.5 else "Bearish"
        confidence = round(max(up_probability, 1 - up_probability) * 100, 2)
        ml_score = up_probability * 100

        return {
            "direction": direction,
            "probability": round(up_probability * 100, 2),
            "confidence": confidence,
            "ml_score": ml_score,
            "models": [asdict(model) for model in ensemble["model_outputs"]],
        }

    def _build_training_set(
        self,
        candles: pd.DataFrame,
        options_score: float,
        breadth_score: float,
        sector_strength: float,
    ) -> tuple[pd.DataFrame, pd.Series]:
        df = candles.copy()
        df["return_1d"] = df["Close"].pct_change()
        df["return_5d"] = df["Close"].pct_change(5)
        df["ma_20"] = df["Close"].rolling(20).mean()
        df["ma_50"] = df["Close"].rolling(50).mean()
        df["ma_ratio"] = df["ma_20"] / df["ma_50"]
        df["vol_ratio"] = df["Volume"] / df["Volume"].rolling(20).mean()

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        rs = gain.rolling(14).mean() / loss.rolling(14).mean().replace(0, np.nan)
        df["rsi"] = 100 - (100 / (1 + rs))

        ema_fast = df["Close"].ewm(span=12, adjust=False).mean()
        ema_slow = df["Close"].ewm(span=26, adjust=False).mean()
        df["macd"] = ema_fast - ema_slow

        df["options_score"] = options_score
        df["market_breadth_score"] = breadth_score
        df["sector_strength"] = sector_strength

        df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
        feature_cols = [
            "Close",
            "rsi",
            "macd",
            "ma_20",
            "ma_50",
            "vol_ratio",
            "options_score",
            "market_breadth_score",
            "sector_strength",
            "return_1d",
            "return_5d",
            "ma_ratio",
        ]

        model_df = df[feature_cols + ["target"]].dropna()
        return model_df[feature_cols], model_df["target"]

    def _mock_training_data(
        self,
        symbol: str,
        options_score: float,
        breadth_score: float,
        sector_strength: float,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Generate deterministic synthetic training rows when market data is short."""
        seed = sum(ord(ch) for ch in symbol)
        rng = np.random.default_rng(seed)
        size = 180

        close = rng.normal(1500, 200, size=size).clip(min=100)
        rsi = rng.uniform(20, 80, size=size)
        macd = rng.normal(0.2, 1.1, size=size)
        ma_20 = close * rng.uniform(0.98, 1.02, size=size)
        ma_50 = close * rng.uniform(0.96, 1.04, size=size)
        vol_ratio = rng.uniform(0.7, 1.8, size=size)
        ret_1d = rng.normal(0.0005, 0.015, size=size)
        ret_5d = rng.normal(0.002, 0.03, size=size)
        ma_ratio = ma_20 / ma_50

        feature_df = pd.DataFrame(
            {
                "Close": close,
                "rsi": rsi,
                "macd": macd,
                "ma_20": ma_20,
                "ma_50": ma_50,
                "vol_ratio": vol_ratio,
                "options_score": options_score,
                "market_breadth_score": breadth_score,
                "sector_strength": sector_strength,
                "return_1d": ret_1d,
                "return_5d": ret_5d,
                "ma_ratio": ma_ratio,
            }
        )

        signal_strength = (rsi - 50) * 0.04 + macd * 0.8 + (ma_ratio - 1.0) * 20 + ret_5d * 8
        logits = signal_strength + rng.normal(0, 0.8, size=size)
        target = pd.Series((logits > np.median(logits)).astype(int))
        return feature_df, target

    @staticmethod
    def _breadth_to_score(breadth: dict[str, float | int | str]) -> float:
        ad_ratio = float(breadth.get("advance_decline_ratio", 1.0))
        vol_breadth = float(breadth.get("volume_breadth", 1.0))
        score = 50 + ((ad_ratio - 1.0) * 20) + ((vol_breadth - 1.0) * 15)
        return round(min(max(score, 0.0), 100.0), 2)

    @staticmethod
    def _resolve_sector_strength(symbol: str, sector_scores: dict[str, float]) -> float:
        symbol = symbol.upper()
        if any(key in symbol for key in ["BANK", "FIN", "SBI", "HDFC", "ICICI", "AXIS", "KOTAK"]):
            return sector_scores.get("Banking", 50.0)
        if any(key in symbol for key in ["TECH", "INFY", "TCS", "WIPRO", "HCL"]):
            return sector_scores.get("IT", 50.0)
        if any(key in symbol for key in ["ONGC", "NTPC", "POWER", "RELIANCE", "BPCL"]):
            return sector_scores.get("Energy", 50.0)
        if any(key in symbol for key in ["AUTO", "MOTO", "MARUTI", "TATA"]):
            return sector_scores.get("Auto", 50.0)
        if any(key in symbol for key in ["ITC", "NESTLE", "HINDUNILVR", "BRITANNIA"]):
            return sector_scores.get("FMCG", 50.0)

        ranked = list(sector_scores.values())
        return round(float(np.mean(ranked)), 2) if ranked else 50.0

    @staticmethod
    def _final_ai_score(
        technical: float,
        options: float,
        fundamental: float,
        market_breadth: float,
        sector_strength: float,
        ml_prediction: float,
    ) -> float:
        """Mandatory weighted formula for final AI score."""
        weighted = (
            (technical * 0.25)
            + (options * 0.25)
            + (fundamental * 0.15)
            + (market_breadth * 0.10)
            + (sector_strength * 0.10)
            + (ml_prediction * 0.15)
        )
        return round(min(max(weighted, 0.0), 100.0), 2)

    @staticmethod
    def _build_signal(symbol: str, candles: pd.DataFrame, ml_block: dict[str, object], final_score: float) -> dict[str, object]:
        close = float(candles["Close"].iloc[-1])
        atr_proxy = float((candles["High"] - candles["Low"]).rolling(14).mean().iloc[-1])
        if np.isnan(atr_proxy) or atr_proxy <= 0:
            atr_proxy = close * 0.015

        bullish = ml_block["direction"] == "Bullish"
        entry = round(close, 2)
        stop_loss = round(close - (1.2 * atr_proxy), 2) if bullish else round(close + (1.2 * atr_proxy), 2)
        target = round(close + (2.2 * atr_proxy), 2) if bullish else round(close - (2.2 * atr_proxy), 2)

        return {
            "stock": symbol.upper(),
            "direction": ml_block["direction"],
            "probability_score": ml_block["probability"],
            "confidence_percent": ml_block["confidence"],
            "entry": entry,
            "stop_loss": stop_loss,
            "target": target,
            "final_ai_score": final_score,
        }
