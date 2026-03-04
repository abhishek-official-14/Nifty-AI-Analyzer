"""Market breadth calculations for overall market participation."""

from __future__ import annotations

import pandas as pd


class MarketBreadthService:
    """Computes market breadth indicators from stock quote snapshots."""

    def calculate_breadth(self, quotes: pd.DataFrame) -> dict[str, float | int | str]:
        """Calculate advance/decline ratio, volume breadth, and market strength label."""
        advances = int((quotes["change_pct"] > 0).sum())
        declines = int((quotes["change_pct"] < 0).sum())
        unchanged = int((quotes["change_pct"] == 0).sum())

        adv_volume = float(quotes.loc[quotes["change_pct"] > 0, "volume"].sum())
        dec_volume = float(quotes.loc[quotes["change_pct"] < 0, "volume"].sum())

        ad_ratio = advances / max(declines, 1)
        vol_breadth = adv_volume / max(dec_volume, 1)

        strength = "Neutral"
        if ad_ratio >= 1.6 and vol_breadth >= 1.2:
            strength = "Strong Bullish"
        elif ad_ratio >= 1.1:
            strength = "Mild Bullish"
        elif ad_ratio <= 0.7 and vol_breadth <= 0.85:
            strength = "Strong Bearish"
        elif ad_ratio <= 0.95:
            strength = "Mild Bearish"

        return {
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged,
            "advance_decline_ratio": round(ad_ratio, 3),
            "volume_breadth": round(vol_breadth, 3),
            "market_strength": strength,
        }
