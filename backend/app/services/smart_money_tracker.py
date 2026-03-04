"""Smart money detection service using price, volume, and OI regime shifts."""

from __future__ import annotations

from typing import Any


class SmartMoneyTrackerService:
    """Classify position-building behavior in options data."""

    def detect(self, options_analysis: dict[str, Any]) -> dict[str, Any]:
        metrics = options_analysis.get("metrics", {})
        chain = options_analysis.get("chain", {})
        underlying = float(options_analysis.get("underlying_value", 0.0))
        pcr = float(metrics.get("pcr", 0.0))

        atm_snapshot = self._atm_snapshot(chain, underlying)
        price_change = float(atm_snapshot.get("net_price_change", 0.0))
        volume_spike = float(atm_snapshot.get("volume_spike_ratio", 1.0))
        oi_change = float(atm_snapshot.get("net_oi_change", 0.0))

        regime = self._classify_regime(price_change, volume_spike, oi_change)
        confidence = self._confidence(price_change, volume_spike, oi_change, pcr)

        return {
            "regime": regime,
            "confidence": confidence,
            "signals": {
                "price_change": round(price_change, 2),
                "volume_spike_ratio": round(volume_spike, 2),
                "oi_change": round(oi_change, 2),
                "pcr": round(pcr, 3),
            },
            "distribution": self._regime_distribution(price_change, volume_spike, oi_change),
        }

    def _atm_snapshot(self, chain: dict[str, Any], underlying: float) -> dict[str, float]:
        calls = chain.get("calls", [])
        puts = chain.get("puts", [])
        if not calls or not puts:
            return {"net_price_change": 0.0, "volume_spike_ratio": 1.0, "net_oi_change": 0.0}

        call_row = min(calls, key=lambda row: abs(float(row.get("strikePrice", 0.0)) - underlying))
        put_row = min(puts, key=lambda row: abs(float(row.get("strikePrice", 0.0)) - underlying))

        call_price = float(call_row.get("lastPrice", call_row.get("impliedVolatility", 0.0)))
        put_price = float(put_row.get("lastPrice", put_row.get("impliedVolatility", 0.0)))
        call_vol = float(call_row.get("totalTradedVolume", 0.0))
        put_vol = float(put_row.get("totalTradedVolume", 0.0))
        call_oi_chg = float(call_row.get("changeinOpenInterest", 0.0))
        put_oi_chg = float(put_row.get("changeinOpenInterest", 0.0))

        net_price_change = put_price - call_price
        avg_vol = (call_vol + put_vol) / 2 if (call_vol + put_vol) else 1.0
        baseline = max(avg_vol * 0.75, 1.0)
        spike_ratio = avg_vol / baseline

        return {
            "net_price_change": net_price_change,
            "volume_spike_ratio": spike_ratio,
            "net_oi_change": put_oi_chg + call_oi_chg,
        }

    def _classify_regime(self, price_change: float, volume_spike: float, oi_change: float) -> str:
        high_volume = volume_spike >= 1.15
        if price_change > 0 and oi_change > 0 and high_volume:
            return "Long Buildup"
        if price_change < 0 and oi_change > 0 and high_volume:
            return "Short Buildup"
        if price_change > 0 and oi_change < 0:
            return "Short Covering"
        if price_change < 0 and oi_change < 0:
            return "Long Unwinding"
        return "Neutral / Mixed"

    def _confidence(self, price_change: float, volume_spike: float, oi_change: float, pcr: float) -> float:
        strength = min(abs(price_change) * 2.2, 35)
        activity = min(max(volume_spike - 1, 0) * 50, 25)
        positioning = min(abs(oi_change) / 1500, 25)
        pcr_alignment = 15 if 0.85 <= pcr <= 1.25 else max(0.0, 15 - abs(1 - pcr) * 20)
        return round(min(strength + activity + positioning + pcr_alignment, 100.0), 2)

    def _regime_distribution(self, price_change: float, volume_spike: float, oi_change: float) -> dict[str, float]:
        raw = {
            "Long Buildup": max(0.0, price_change) + max(0.0, oi_change / 2000),
            "Short Buildup": max(0.0, -price_change) + max(0.0, oi_change / 2000),
            "Short Covering": max(0.0, price_change) + max(0.0, -oi_change / 2000),
            "Long Unwinding": max(0.0, -price_change) + max(0.0, -oi_change / 2000),
            "Neutral / Mixed": max(0.2, 1.1 - abs(price_change) - max(0.0, volume_spike - 1.0)),
        }
        total = sum(raw.values()) or 1.0
        return {k: round((v / total) * 100, 2) for k, v in raw.items()}
