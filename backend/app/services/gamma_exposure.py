"""Gamma exposure estimation service for dealer hedging pressure."""

from __future__ import annotations

from typing import Any


class GammaExposureService:
    """Estimate aggregate gamma map from OI and implied volatility."""

    def compute(self, options_analysis: dict[str, Any]) -> dict[str, Any]:
        calls = options_analysis.get("chain", {}).get("calls", [])
        puts = options_analysis.get("chain", {}).get("puts", [])

        gamma_map: dict[float, float] = {}
        for row in calls:
            strike = float(row.get("strikePrice", 0.0))
            gamma_map[strike] = gamma_map.get(strike, 0.0) + self._proxy_gamma(row, option_type="call")
        for row in puts:
            strike = float(row.get("strikePrice", 0.0))
            gamma_map[strike] = gamma_map.get(strike, 0.0) + self._proxy_gamma(row, option_type="put")

        if not gamma_map:
            return {
                "net_gamma": 0.0,
                "dealer_hedging_levels": [],
                "volatility_expansion_zones": [],
            }

        ranked = sorted(gamma_map.items(), key=lambda x: abs(x[1]), reverse=True)
        dealer_levels = [{"strike": strike, "gamma": round(gamma, 2)} for strike, gamma in ranked[:5]]

        expansion = [
            {"strike": strike, "gamma": round(gamma, 2)}
            for strike, gamma in ranked
            if abs(gamma) >= (abs(ranked[0][1]) * 0.65)
        ]

        return {
            "net_gamma": round(sum(gamma_map.values()), 2),
            "dealer_hedging_levels": dealer_levels,
            "volatility_expansion_zones": expansion,
        }

    def _proxy_gamma(self, row: dict[str, Any], option_type: str) -> float:
        oi = float(row.get("openInterest", 0.0))
        iv = max(float(row.get("impliedVolatility", 0.0)), 1.0)
        strike = max(float(row.get("strikePrice", 0.0)), 1.0)
        sign = 1 if option_type == "call" else -1
        return sign * oi * (1 / iv) * (100 / strike)
