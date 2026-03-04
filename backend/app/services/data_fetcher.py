"""Data fetching utilities for market and stock data sources."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

import numpy as np
import pandas as pd
import requests
import yfinance as yf

logger = logging.getLogger(__name__)

NIFTY50_SYMBOLS: list[str] = [
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "APOLLOHOSP.NS",
    "ASIANPAINT.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS",
    "BAJAJFINSV.NS",
    "BEL.NS",
    "BHARTIARTL.NS",
    "BPCL.NS",
    "BRITANNIA.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "ETERNAL.NS",
    "GRASIM.NS",
    "HCLTECH.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "ITC.NS",
    "INDUSINDBK.NS",
    "INFY.NS",
    "JSWSTEEL.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "M&M.NS",
    "MARUTI.NS",
    "NESTLEIND.NS",
    "NTPC.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "RELIANCE.NS",
    "SBILIFE.NS",
    "SHRIRAMFIN.NS",
    "SBIN.NS",
    "SUNPHARMA.NS",
    "TCS.NS",
    "TATACONSUM.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "TECHM.NS",
    "TITAN.NS",
    "TRENT.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS",
]

SECTOR_MAPPING: dict[str, list[str]] = {
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "TECHM.NS", "WIPRO.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "NTPC.NS", "POWERGRID.NS"],
    "Auto": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS"],
}


@dataclass
class FetchConfig:
    """Configuration for historical price data fetches."""

    period: str = "6mo"
    interval: str = "1d"


class DataFetcher:
    """Fetches market data using Yahoo Finance with deterministic fallbacks."""

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def _normalize_symbol(self, symbol: str) -> str:
        symbol = symbol.upper()
        if not symbol.endswith(".NS") and symbol != "^NSEI":
            return f"{symbol}.NS"
        return symbol

    def fetch_ohlc(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Fetch OHLCV candles for a symbol and return a clean DataFrame."""
        norm_symbol = self._normalize_symbol(symbol)
        data = yf.download(norm_symbol, period=period, interval=interval, progress=False)

        if data.empty:
            logger.warning("Yahoo download failed for %s. Falling back to synthetic data.", norm_symbol)
            return self._generate_synthetic_ohlc()

        data = data.rename(columns=str.title)
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_cols:
            if col not in data.columns:
                data[col] = np.nan

        cleaned = data[required_cols].dropna().copy()
        cleaned.index = pd.to_datetime(cleaned.index)
        return cleaned

    def fetch_nifty_index(self, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """Fetch NIFTY index candles."""
        return self.fetch_ohlc("^NSEI", period=period, interval=interval)

    def fetch_nifty50_quotes(self, symbols: Iterable[str] | None = None) -> pd.DataFrame:
        """Fetch latest quote information for the NIFTY 50 list."""
        symbols = list(symbols) if symbols is not None else NIFTY50_SYMBOLS
        normalized = [self._normalize_symbol(s) for s in symbols]

        tickers = yf.Tickers(" ".join(normalized))
        rows: list[dict[str, float | str]] = []

        for symbol in normalized:
            try:
                info = tickers.tickers[symbol].fast_info
                rows.append(
                    {
                        "symbol": symbol,
                        "last_price": float(info.get("lastPrice") or np.nan),
                        "previous_close": float(info.get("previousClose") or np.nan),
                        "volume": float(info.get("lastVolume") or np.nan),
                    }
                )
            except Exception as exc:  # pragma: no cover - defensive for unstable provider data
                logger.exception("Quote fetch failed for %s: %s", symbol, exc)

        df = pd.DataFrame(rows)
        if df.empty:
            logger.warning("No quotes returned. Using synthetic quote fallback.")
            return self._synthetic_quotes(normalized)

        df["change_pct"] = ((df["last_price"] - df["previous_close"]) / df["previous_close"]) * 100
        return df

    def fetch_nse_fii_dii_activity(self) -> dict[str, float | str]:
        """Fetch FII/DII cash activity from NSE website, with fallback defaults."""
        url = "https://www.nseindia.com/api/fiidiiTradeReact"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/",
        }
        try:
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=self.timeout)
            response = session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, list) and payload:
                latest = payload[0]
                return {
                    "date": latest.get("date", "N/A"),
                    "fii_net": float(latest.get("fiiNet", 0.0)),
                    "dii_net": float(latest.get("diiNet", 0.0)),
                }
        except Exception as exc:  # pragma: no cover - external API safety
            logger.warning("NSE FII/DII fetch failed, using fallback data: %s", exc)

        return {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "fii_net": -250.0,
            "dii_net": 310.0,
        }

    def _generate_synthetic_ohlc(self, periods: int = 120) -> pd.DataFrame:
        """Generate deterministic synthetic OHLCV when providers fail."""
        dates = pd.date_range(datetime.utcnow() - timedelta(days=periods), periods=periods, freq="B")
        base = np.linspace(18000, 22500, periods) + np.sin(np.linspace(0, 15, periods)) * 200
        close = pd.Series(base, index=dates)
        open_ = close.shift(1).fillna(close.iloc[0])
        high = pd.concat([open_, close], axis=1).max(axis=1) + 20
        low = pd.concat([open_, close], axis=1).min(axis=1) - 20
        volume = np.random.default_rng(7).integers(1_000_000, 3_000_000, size=periods)

        return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume})

    def _synthetic_quotes(self, symbols: list[str]) -> pd.DataFrame:
        """Create synthetic quotes when external source is unavailable."""
        rng = np.random.default_rng(42)
        last_price = rng.normal(loc=1000, scale=200, size=len(symbols)).clip(min=100)
        previous_close = last_price * rng.uniform(0.98, 1.02, size=len(symbols))
        volume = rng.integers(100_000, 2_000_000, size=len(symbols))

        df = pd.DataFrame(
            {
                "symbol": symbols,
                "last_price": last_price,
                "previous_close": previous_close,
                "volume": volume,
            }
        )
        df["change_pct"] = ((df["last_price"] - df["previous_close"]) / df["previous_close"]) * 100
        return df
