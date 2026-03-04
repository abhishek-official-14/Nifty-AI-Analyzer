"""API routes for Nifty AI Analyzer Pro backend services."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.data_fetcher import DataFetcher
from app.services.fii_dii_tracker import FiiDiiTrackerService
from app.services.fundamental_analysis import FundamentalAnalysisService
from app.services.intraday_volume import IntradayVolumeService
from app.services.market_breadth import MarketBreadthService
from app.services.sector_rotation import SectorRotationService
from app.services.technical_analysis import TechnicalAnalysisService

router = APIRouter(prefix="/api", tags=["analysis"])

fetcher = DataFetcher()
tech_service = TechnicalAnalysisService()
fund_service = FundamentalAnalysisService()
breadth_service = MarketBreadthService()
sector_service = SectorRotationService(fetcher)
fii_dii_service = FiiDiiTrackerService(fetcher)
intraday_service = IntradayVolumeService()


@router.get("/nifty-overview")
def nifty_overview() -> dict:
    """Get a consolidated NIFTY market overview with technical and breadth metrics."""
    index_df = fetcher.fetch_nifty_index(period="6mo", interval="1d")
    if index_df.empty:
        raise HTTPException(status_code=503, detail="Unable to fetch NIFTY index data")

    quotes = fetcher.fetch_nifty50_quotes()
    technical = tech_service.compute_indicators(index_df)
    breadth = breadth_service.calculate_breadth(quotes)
    volume = intraday_service.summarize(index_df)

    return {
        "index": {
            "symbol": "NIFTY",
            "close": technical["close"],
            "support": technical["support"],
            "resistance": technical["resistance"],
        },
        "technical": technical,
        "market_breadth": breadth,
        "volume": volume,
    }


@router.get("/stock-analysis/{symbol}")
def stock_analysis(symbol: str) -> dict:
    """Analyze a stock with technical and fundamental scoring components."""
    candles = fetcher.fetch_ohlc(symbol, period="1y", interval="1d")
    if candles.empty:
        raise HTTPException(status_code=404, detail=f"No data available for {symbol}")

    technical = tech_service.compute_indicators(candles)
    fundamentals = fund_service.get_fundamental_snapshot(symbol.upper())

    composite = round((technical["technical_score"] * 0.55) + (fundamentals["fundamental_score"] * 0.45), 2)

    return {
        "symbol": symbol.upper(),
        "technical": technical,
        "fundamental": fundamentals,
        "composite_score": composite,
        "xgboost_pipeline": {
            "status": "not_trained",
            "note": "Model training intentionally excluded in this backend foundation.",
        },
    }


@router.get("/market-breadth")
def market_breadth() -> dict:
    """Get current market breadth snapshot across NIFTY 50 constituents."""
    quotes = fetcher.fetch_nifty50_quotes()
    return breadth_service.calculate_breadth(quotes)


@router.get("/sector-strength")
def sector_strength() -> dict:
    """Get ranked sector strength dashboard data."""
    return sector_service.get_sector_strength()


@router.get("/fii-dii")
def fii_dii() -> dict:
    """Get latest FII/DII activity and flow sentiment."""
    return fii_dii_service.get_flow()
