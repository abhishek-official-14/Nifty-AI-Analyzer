"""Sector rotation and relative strength service."""

from __future__ import annotations

import pandas as pd

from app.services.data_fetcher import DataFetcher, SECTOR_MAPPING


class SectorRotationService:
    """Evaluates sector strength using basket performance."""

    def __init__(self, data_fetcher: DataFetcher) -> None:
        self.data_fetcher = data_fetcher

    def get_sector_strength(self) -> dict[str, list[dict[str, float | str]]]:
        """Compute score/rank for each tracked sector based on returns and volume."""
        sector_rows: list[dict[str, float | str]] = []

        for sector, symbols in SECTOR_MAPPING.items():
            quotes = self.data_fetcher.fetch_nifty50_quotes(symbols)
            avg_return = float(quotes["change_pct"].mean())
            avg_volume = float(quotes["volume"].mean())
            score = max(0.0, min(100.0, 50 + (avg_return * 8)))
            sector_rows.append(
                {
                    "sector": sector,
                    "average_change_pct": round(avg_return, 3),
                    "average_volume": round(avg_volume, 2),
                    "strength_score": round(score, 2),
                }
            )

        ranking = pd.DataFrame(sector_rows).sort_values("strength_score", ascending=False)
        ranking["rank"] = range(1, len(ranking) + 1)
        return {"sectors": ranking.to_dict(orient="records")}
