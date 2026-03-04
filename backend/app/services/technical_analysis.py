"""Technical analysis service with indicator and scoring utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.utils.scoring import clamp, weighted_score

try:
    import talib
except Exception:  # pragma: no cover
    talib = None


class TechnicalAnalysisService:
    """Computes key technical indicators and a normalized technical score."""

    def compute_indicators(self, candles: pd.DataFrame) -> dict:
        """Compute indicators and derived trend levels for given OHLCV candles."""
        df = candles.copy()

        close = df["Close"].astype(float)
        high = df["High"].astype(float)
        low = df["Low"].astype(float)
        volume = df["Volume"].astype(float)

        if talib:
            rsi = talib.RSI(close, timeperiod=14)
            macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            ma20 = talib.SMA(close, timeperiod=20)
            ma50 = talib.SMA(close, timeperiod=50)
            ma200 = talib.SMA(close, timeperiod=200)
            bb_upper, bb_mid, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            adx = talib.ADX(high, low, close, timeperiod=14)
        else:
            rsi = self._rsi_fallback(close, 14)
            ema_fast = close.ewm(span=12, adjust=False).mean()
            ema_slow = close.ewm(span=26, adjust=False).mean()
            macd = ema_fast - ema_slow
            macd_signal = macd.ewm(span=9, adjust=False).mean()
            macd_hist = macd - macd_signal
            ma20 = close.rolling(20).mean()
            ma50 = close.rolling(50).mean()
            ma200 = close.rolling(200).mean()
            rolling_std = close.rolling(20).std()
            bb_mid = ma20
            bb_upper = bb_mid + (2 * rolling_std)
            bb_lower = bb_mid - (2 * rolling_std)
            adx = self._adx_fallback(high, low, close, 14)

        typical_price = (high + low + close) / 3.0
        vwap = (typical_price * volume).cumsum() / volume.cumsum()

        window = 20
        support = low.rolling(window).min().iloc[-1]
        resistance = high.rolling(window).max().iloc[-1]

        latest = {
            "rsi": float(rsi.iloc[-1]),
            "macd": float(macd.iloc[-1]),
            "macd_signal": float(macd_signal.iloc[-1]),
            "macd_hist": float(macd_hist.iloc[-1]),
            "ma20": float(ma20.iloc[-1]),
            "ma50": float(ma50.iloc[-1]),
            "ma200": float(ma200.iloc[-1]) if not np.isnan(ma200.iloc[-1]) else float(ma50.iloc[-1]),
            "vwap": float(vwap.iloc[-1]),
            "bb_upper": float(bb_upper.iloc[-1]),
            "bb_mid": float(bb_mid.iloc[-1]),
            "bb_lower": float(bb_lower.iloc[-1]),
            "support": float(support),
            "resistance": float(resistance),
            "trend_strength": float(adx.iloc[-1]),
            "close": float(close.iloc[-1]),
        }

        latest["technical_score"] = self.compute_technical_score(latest)
        return latest

    def compute_technical_score(self, indicator: dict[str, float]) -> float:
        """Generate 0-100 technical score from indicator values."""
        rsi_score = 100 - abs(indicator["rsi"] - 55) * 2
        macd_score = 80 if indicator["macd"] > indicator["macd_signal"] else 40
        trend_score = clamp(indicator["trend_strength"] * 3)

        close = indicator["close"]
        ma_alignment = sum(
            [
                1 if close > indicator["ma20"] else 0,
                1 if close > indicator["ma50"] else 0,
                1 if close > indicator["ma200"] else 0,
            ]
        )
        ma_score = (ma_alignment / 3) * 100

        band_score = 100 if indicator["bb_lower"] <= close <= indicator["bb_upper"] else 55
        vwap_score = 90 if close >= indicator["vwap"] else 50

        return weighted_score(
            [
                (clamp(rsi_score), 0.20),
                (macd_score, 0.20),
                (trend_score, 0.20),
                (ma_score, 0.20),
                (band_score, 0.10),
                (vwap_score, 0.10),
            ]
        )

    @staticmethod
    def _rsi_fallback(series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _adx_fallback(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
        plus_dm = high.diff().clip(lower=0)
        minus_dm = (-low.diff()).clip(lower=0)
        tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)) * 100
        return dx.rolling(period).mean().fillna(20)
