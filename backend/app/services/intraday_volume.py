"""Intraday volume analytics service."""

from __future__ import annotations

import pandas as pd


class IntradayVolumeService:
    """Provides intraday volume trend and anomaly metrics."""

    def summarize(self, candles: pd.DataFrame) -> dict[str, float | str]:
        """Summarize current volume versus rolling baseline."""
        volume = candles["Volume"].astype(float)
        latest_volume = float(volume.iloc[-1])
        avg20 = float(volume.tail(20).mean())
        ratio = latest_volume / avg20 if avg20 else 1.0

        label = "Normal"
        if ratio >= 1.5:
            label = "High Participation"
        elif ratio <= 0.7:
            label = "Low Participation"

        return {
            "latest_volume": round(latest_volume, 2),
            "average_20d_volume": round(avg20, 2),
            "volume_ratio": round(ratio, 3),
            "volume_label": label,
        }
