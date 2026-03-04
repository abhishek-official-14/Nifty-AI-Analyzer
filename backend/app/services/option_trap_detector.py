"""Option trap pattern detection for deceptive market structures."""

from __future__ import annotations

from typing import Any


class OptionTrapDetectorService:
    """Detect call/put traps, fake breakouts, and gamma squeeze signatures."""

    def detect(self, options_analysis: dict[str, Any], smart_money: dict[str, Any]) -> dict[str, Any]:
        metrics = options_analysis.get("metrics", {})
        chain = options_analysis.get("chain", {})
        regime = smart_money.get("regime", "Neutral / Mixed")

        calls = chain.get("calls", [])
        puts = chain.get("puts", [])

        call_trap = self._is_call_trap(metrics, regime)
        put_trap = self._is_put_trap(metrics, regime)
        fake_breakout = self._is_fake_breakout(calls, puts, metrics)
        gamma_squeeze = self._is_gamma_squeeze(calls, puts)

        return {
            "call_trap": call_trap,
            "put_trap": put_trap,
            "fake_breakout": fake_breakout,
            "gamma_squeeze": gamma_squeeze,
            "risk_level": self._risk_level(call_trap, put_trap, fake_breakout, gamma_squeeze),
        }

    def _is_call_trap(self, metrics: dict[str, Any], regime: str) -> bool:
        return float(metrics.get("call_change_oi", 0.0)) > 0 and float(metrics.get("pcr", 1.0)) > 1.1 and regime == "Long Buildup"

    def _is_put_trap(self, metrics: dict[str, Any], regime: str) -> bool:
        return float(metrics.get("put_change_oi", 0.0)) > 0 and float(metrics.get("pcr", 1.0)) < 0.85 and regime == "Short Buildup"

    def _is_fake_breakout(self, calls: list[dict[str, Any]], puts: list[dict[str, Any]], metrics: dict[str, Any]) -> bool:
        if not calls or not puts:
            return False
        max_call_oi = max(float(row.get("openInterest", 0.0)) for row in calls)
        max_put_oi = max(float(row.get("openInterest", 0.0)) for row in puts)
        oi_imbalance = abs(max_call_oi - max_put_oi) / max(max_call_oi + max_put_oi, 1.0)
        low_volume = min(float(metrics.get("call_volume", 0.0)), float(metrics.get("put_volume", 0.0))) < 100000
        return oi_imbalance > 0.25 and low_volume

    def _is_gamma_squeeze(self, calls: list[dict[str, Any]], puts: list[dict[str, Any]]) -> bool:
        if not calls or not puts:
            return False
        call_peak = max(calls, key=lambda x: float(x.get("openInterest", 0.0)))
        put_peak = max(puts, key=lambda x: float(x.get("openInterest", 0.0)))
        strike_diff = abs(float(call_peak.get("strikePrice", 0.0)) - float(put_peak.get("strikePrice", 0.0)))
        vol_spike = float(call_peak.get("totalTradedVolume", 0.0)) + float(put_peak.get("totalTradedVolume", 0.0))
        return strike_diff <= 200 and vol_spike > 50000

    def _risk_level(self, call_trap: bool, put_trap: bool, fake_breakout: bool, gamma_squeeze: bool) -> str:
        count = sum([call_trap, put_trap, fake_breakout, gamma_squeeze])
        if count >= 3:
            return "high"
        if count == 2:
            return "medium"
        if count == 1:
            return "elevated"
        return "low"
