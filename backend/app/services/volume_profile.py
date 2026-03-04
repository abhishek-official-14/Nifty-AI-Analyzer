"""Volume profile computation over option strikes."""

from __future__ import annotations

from typing import Any


class VolumeProfileService:
    """Compute POC, VAH, and VAL using strike-wise traded volume."""

    def compute(self, options_analysis: dict[str, Any], value_area: float = 0.7) -> dict[str, float]:
        calls = options_analysis.get("chain", {}).get("calls", [])
        puts = options_analysis.get("chain", {}).get("puts", [])

        volume_by_strike: dict[float, float] = {}
        for row in calls + puts:
            strike = float(row.get("strikePrice", 0.0))
            vol = float(row.get("totalTradedVolume", 0.0))
            if strike <= 0:
                continue
            volume_by_strike[strike] = volume_by_strike.get(strike, 0.0) + vol

        if not volume_by_strike:
            return {"poc": 0.0, "vah": 0.0, "val": 0.0}

        poc = max(volume_by_strike, key=volume_by_strike.get)
        total_volume = sum(volume_by_strike.values())
        target = total_volume * value_area

        sorted_strikes = sorted(volume_by_strike.items(), key=lambda x: x[1], reverse=True)
        selected = []
        cumulative = 0.0
        for strike, vol in sorted_strikes:
            selected.append(strike)
            cumulative += vol
            if cumulative >= target:
                break

        return {
            "poc": float(poc),
            "vah": float(max(selected)),
            "val": float(min(selected)),
        }
