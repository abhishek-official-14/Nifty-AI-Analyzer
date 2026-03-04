"""Fundamental analysis service for stock quality scoring."""

from __future__ import annotations

import numpy as np

from app.utils.scoring import score_from_thresholds, weighted_score


class FundamentalAnalysisService:
    """Scores company fundamentals using normalized threshold rules."""

    def get_fundamental_snapshot(self, symbol: str) -> dict[str, float | str]:
        """Return mock/live-like fundamental metrics with deterministic values per symbol."""
        seed = sum(ord(ch) for ch in symbol)
        rng = np.random.default_rng(seed)

        metrics = {
            "symbol": symbol,
            "pe": float(rng.uniform(12, 38)),
            "pb": float(rng.uniform(1.5, 9)),
            "roe": float(rng.uniform(8, 28)),
            "roce": float(rng.uniform(10, 30)),
            "debt_to_equity": float(rng.uniform(0.05, 1.8)),
            "eps_growth": float(rng.uniform(-5, 35)),
            "revenue_growth": float(rng.uniform(2, 28)),
            "promoter_holding": float(rng.uniform(35, 78)),
        }
        metrics["fundamental_score"] = self.compute_fundamental_score(metrics)
        return metrics

    def compute_fundamental_score(self, m: dict[str, float | str]) -> float:
        """Aggregate fundamentals into a 0-100 score."""
        pe_score = score_from_thresholds(float(m["pe"]), good=18, bad=45, inverse=True)
        pb_score = score_from_thresholds(float(m["pb"]), good=3, bad=10, inverse=True)
        roe_score = score_from_thresholds(float(m["roe"]), good=20, bad=8)
        roce_score = score_from_thresholds(float(m["roce"]), good=22, bad=10)
        de_score = score_from_thresholds(float(m["debt_to_equity"]), good=0.2, bad=2, inverse=True)
        eps_score = score_from_thresholds(float(m["eps_growth"]), good=20, bad=-10)
        rev_score = score_from_thresholds(float(m["revenue_growth"]), good=18, bad=0)
        promoter_score = score_from_thresholds(float(m["promoter_holding"]), good=65, bad=30)

        return weighted_score(
            [
                (pe_score, 0.12),
                (pb_score, 0.10),
                (roe_score, 0.16),
                (roce_score, 0.14),
                (de_score, 0.12),
                (eps_score, 0.14),
                (rev_score, 0.14),
                (promoter_score, 0.08),
            ]
        )
