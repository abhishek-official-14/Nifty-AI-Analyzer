"""Option chain intelligence service for NSE NIFTY index options."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests


@dataclass
class OptionChainConfig:
    """Runtime settings for option chain retrieval."""

    symbol: str = "NIFTY"
    timeout: int = 8


class OptionChainAnalysisService:
    """Fetch and analyze NSE option chain with deterministic fallback."""

    API_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

    def __init__(self, config: OptionChainConfig | None = None) -> None:
        self.config = config or OptionChainConfig()

    def get_analysis(self) -> dict[str, Any]:
        """Return complete option chain intelligence and scoring output."""
        payload, source = self._fetch_option_chain()
        records = payload.get("records", {})
        data = records.get("data", [])

        ce_rows: list[dict[str, Any]] = []
        pe_rows: list[dict[str, Any]] = []
        for item in data:
            strike = item.get("strikePrice")
            if not strike:
                continue
            if isinstance(item.get("CE"), dict):
                ce = dict(item["CE"])
                ce["strikePrice"] = strike
                ce_rows.append(ce)
            if isinstance(item.get("PE"), dict):
                pe = dict(item["PE"])
                pe["strikePrice"] = strike
                pe_rows.append(pe)

        total_call_oi = sum(float(row.get("openInterest", 0.0)) for row in ce_rows)
        total_put_oi = sum(float(row.get("openInterest", 0.0)) for row in pe_rows)
        total_call_coi = sum(float(row.get("changeinOpenInterest", 0.0)) for row in ce_rows)
        total_put_coi = sum(float(row.get("changeinOpenInterest", 0.0)) for row in pe_rows)
        total_call_volume = sum(float(row.get("totalTradedVolume", 0.0)) for row in ce_rows)
        total_put_volume = sum(float(row.get("totalTradedVolume", 0.0)) for row in pe_rows)

        pcr = round(total_put_oi / total_call_oi, 3) if total_call_oi else 0.0
        max_pain = self._calculate_max_pain(data)
        iv = self._average_iv(ce_rows, pe_rows)

        options_score = self._options_score(
            pcr=pcr,
            call_oi=total_call_oi,
            put_oi=total_put_oi,
            call_coi=total_call_coi,
            put_coi=total_put_coi,
            call_volume=total_call_volume,
            put_volume=total_put_volume,
            iv=iv,
        )

        return {
            "symbol": self.config.symbol,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "underlying_value": float(records.get("underlyingValue") or 0.0),
            "metrics": {
                "call_oi": round(total_call_oi, 2),
                "put_oi": round(total_put_oi, 2),
                "call_change_oi": round(total_call_coi, 2),
                "put_change_oi": round(total_put_coi, 2),
                "call_volume": round(total_call_volume, 2),
                "put_volume": round(total_put_volume, 2),
                "average_iv": iv,
                "pcr": pcr,
                "max_pain": max_pain,
            },
            "options_score": options_score,
            "chain": {
                "calls": ce_rows,
                "puts": pe_rows,
            },
        }

    def _fetch_option_chain(self) -> tuple[dict[str, Any], str]:
        """Fetch from NSE with browser-like headers, fallback to static payload."""
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/",
        }
        url = self.API_URL.format(symbol=self.config.symbol)

        try:
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=self.config.timeout)
            response = session.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json(), "nse"
        except Exception:
            return self._mock_payload(), "mock"

    def _average_iv(self, ce_rows: list[dict[str, Any]], pe_rows: list[dict[str, Any]]) -> float:
        iv_values = [float(row.get("impliedVolatility", 0.0)) for row in ce_rows + pe_rows if row.get("impliedVolatility")]
        if not iv_values:
            return 0.0
        return round(sum(iv_values) / len(iv_values), 2)

    def _calculate_max_pain(self, chain_rows: list[dict[str, Any]]) -> float:
        """Approximate max pain strike by minimum payout across strikes."""
        strikes = sorted({float(row.get("strikePrice", 0.0)) for row in chain_rows if row.get("strikePrice")})
        if not strikes:
            return 0.0

        payout_map: dict[float, float] = {}
        for spot in strikes:
            payout = 0.0
            for row in chain_rows:
                strike = float(row.get("strikePrice", 0.0))
                call_oi = float(row.get("CE", {}).get("openInterest", 0.0))
                put_oi = float(row.get("PE", {}).get("openInterest", 0.0))
                payout += max(0.0, spot - strike) * call_oi
                payout += max(0.0, strike - spot) * put_oi
            payout_map[spot] = payout

        return min(payout_map, key=payout_map.get)

    def _options_score(
        self,
        pcr: float,
        call_oi: float,
        put_oi: float,
        call_coi: float,
        put_coi: float,
        call_volume: float,
        put_volume: float,
        iv: float,
    ) -> float:
        """Generate a 0-100 confidence score from core option-chain factors."""
        oi_balance = 50 + min(max((put_oi - call_oi) / max(call_oi + put_oi, 1.0) * 100, -25), 25)
        coi_balance = 50 + min(max((put_coi - call_coi) / max(abs(call_coi) + abs(put_coi), 1.0) * 100, -20), 20)
        vol_balance = 50 + min(max((put_volume - call_volume) / max(call_volume + put_volume, 1.0) * 100, -15), 15)
        pcr_score = 100 - min(abs(1.0 - pcr) * 100, 60)
        iv_score = 100 - min(max(iv - 18, 0) * 2, 40)

        weighted = (oi_balance * 0.25) + (coi_balance * 0.2) + (vol_balance * 0.15) + (pcr_score * 0.25) + (iv_score * 0.15)
        return round(min(max(weighted, 0.0), 100.0), 2)

    def _mock_payload(self) -> dict[str, Any]:
        """Mock NSE-compatible option-chain response for resilient backend usage."""
        strikes = [24400, 24500, 24600, 24700, 24800, 24900, 25000]
        underlying = 24735.0

        rows: list[dict[str, Any]] = []
        for idx, strike in enumerate(strikes):
            distance = abs(strike - underlying)
            base_oi = max(65000 - (distance * 30), 15000)
            rows.append(
                {
                    "strikePrice": strike,
                    "CE": {
                        "openInterest": int(base_oi + (idx * 1200)),
                        "changeinOpenInterest": int((-2200 + idx * 450)),
                        "totalTradedVolume": int(15000 + (idx * 1800)),
                        "impliedVolatility": round(13.5 + (idx * 0.55), 2),
                    },
                    "PE": {
                        "openInterest": int(base_oi + ((len(strikes) - idx) * 1500)),
                        "changeinOpenInterest": int((1900 - idx * 280)),
                        "totalTradedVolume": int(14500 + ((len(strikes) - idx) * 1600)),
                        "impliedVolatility": round(14.0 + ((len(strikes) - idx) * 0.45), 2),
                    },
                }
            )

        return {
            "records": {
                "underlyingValue": underlying,
                "timestamp": datetime.utcnow().isoformat(),
                "data": rows,
            }
        }
