"""Liquidity heatmap service for stop-loss clusters and trap levels."""

from __future__ import annotations

from typing import Any


class LiquidityHeatmapService:
    """Derive strike-level liquidity zones from option-chain concentrations."""

    def build(self, options_analysis: dict[str, Any], trap_signals: dict[str, Any]) -> dict[str, Any]:
        calls = options_analysis.get("chain", {}).get("calls", [])
        puts = options_analysis.get("chain", {}).get("puts", [])

        stop_clusters = self._stop_loss_clusters(calls, puts)
        high_liquidity = self._high_liquidity_zones(calls, puts)
        breakout_traps = self._breakout_trap_levels(calls, puts, trap_signals)

        return {
            "stop_loss_clusters": stop_clusters,
            "high_liquidity_zones": high_liquidity,
            "breakout_trap_levels": breakout_traps,
        }

    def _stop_loss_clusters(self, calls: list[dict[str, Any]], puts: list[dict[str, Any]]) -> list[dict[str, float]]:
        combined = []
        for row in calls:
            combined.append((float(row.get("strikePrice", 0.0)), float(row.get("changeinOpenInterest", 0.0))))
        for row in puts:
            combined.append((float(row.get("strikePrice", 0.0)), float(row.get("changeinOpenInterest", 0.0))))

        combined.sort(key=lambda item: abs(item[1]), reverse=True)
        return [
            {"strike": strike, "intensity": round(abs(change_oi), 2)}
            for strike, change_oi in combined[:5]
            if strike > 0
        ]

    def _high_liquidity_zones(self, calls: list[dict[str, Any]], puts: list[dict[str, Any]]) -> list[dict[str, float]]:
        score_map: dict[float, float] = {}
        for row in calls + puts:
            strike = float(row.get("strikePrice", 0.0))
            if strike <= 0:
                continue
            oi = float(row.get("openInterest", 0.0))
            volume = float(row.get("totalTradedVolume", 0.0))
            score_map[strike] = score_map.get(strike, 0.0) + oi + (volume * 0.3)

        ranked = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        return [{"strike": strike, "liquidity_score": round(score, 2)} for strike, score in ranked[:6]]

    def _breakout_trap_levels(
        self,
        calls: list[dict[str, Any]],
        puts: list[dict[str, Any]],
        trap_signals: dict[str, Any],
    ) -> list[dict[str, Any]]:
        levels: list[dict[str, Any]] = []
        if trap_signals.get("call_trap") and calls:
            call_wall = max(calls, key=lambda x: float(x.get("openInterest", 0.0)))
            levels.append({"type": "call_wall", "strike": float(call_wall.get("strikePrice", 0.0))})

        if trap_signals.get("put_trap") and puts:
            put_wall = max(puts, key=lambda x: float(x.get("openInterest", 0.0)))
            levels.append({"type": "put_wall", "strike": float(put_wall.get("strikePrice", 0.0))})

        if trap_signals.get("fake_breakout") and calls and puts:
            levels.append(
                {
                    "type": "fake_breakout_band",
                    "lower": float(min(puts, key=lambda x: float(x.get("openInterest", 0.0))).get("strikePrice", 0.0)),
                    "upper": float(max(calls, key=lambda x: float(x.get("openInterest", 0.0))).get("strikePrice", 0.0)),
                }
            )

        return levels
