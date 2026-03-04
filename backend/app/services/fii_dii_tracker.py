"""FII / DII tracking service."""

from __future__ import annotations

from app.services.data_fetcher import DataFetcher


class FiiDiiTrackerService:
    """Tracks institutional flow and classifies market flow sentiment."""

    def __init__(self, data_fetcher: DataFetcher) -> None:
        self.data_fetcher = data_fetcher

    def get_flow(self) -> dict[str, float | str]:
        """Fetch latest FII/DII net flow and infer sentiment."""
        payload = self.data_fetcher.fetch_nse_fii_dii_activity()
        fii_net = float(payload["fii_net"])
        dii_net = float(payload["dii_net"])
        combined = fii_net + dii_net

        sentiment = "Neutral"
        if combined > 250:
            sentiment = "Bullish"
        elif combined < -250:
            sentiment = "Bearish"

        return {
            **payload,
            "combined_net": round(combined, 2),
            "sentiment": sentiment,
        }
