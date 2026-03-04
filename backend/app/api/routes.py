"""API routes for Nifty AI Analyzer Pro backend services."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.ai_prediction import AIPredictionService
from app.services.data_fetcher import DataFetcher
from app.services.fii_dii_tracker import FiiDiiTrackerService
from app.services.fundamental_analysis import FundamentalAnalysisService
from app.services.gamma_exposure import GammaExposureService
from app.services.intraday_volume import IntradayVolumeService
from app.services.liquidity_heatmap import LiquidityHeatmapService
from app.services.market_breadth import MarketBreadthService
from app.services.option_chain_analysis import OptionChainAnalysisService
from app.services.option_trap_detector import OptionTrapDetectorService
from app.services.sector_rotation import SectorRotationService
from app.services.smart_money_tracker import SmartMoneyTrackerService
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.volume_profile import VolumeProfileService

router = APIRouter(prefix="/api", tags=["analysis"])

fetcher = DataFetcher()
tech_service = TechnicalAnalysisService()
fund_service = FundamentalAnalysisService()
breadth_service = MarketBreadthService()
sector_service = SectorRotationService(fetcher)
fii_dii_service = FiiDiiTrackerService(fetcher)
intraday_service = IntradayVolumeService()
option_chain_service = OptionChainAnalysisService()
smart_money_service = SmartMoneyTrackerService()
trap_detector_service = OptionTrapDetectorService()
liquidity_service = LiquidityHeatmapService()
volume_profile_service = VolumeProfileService()
gamma_service = GammaExposureService()
ai_prediction_service = AIPredictionService(
    fetcher=fetcher,
    technical_service=tech_service,
    fundamental_service=fund_service,
    breadth_service=breadth_service,
    sector_service=sector_service,
    option_chain_service=option_chain_service,
)


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


@router.get("/ai-signals")
def ai_signals(symbols: str | None = None, limit: int = 5) -> dict:
    """Get AI-powered directional trading signals with composite scoring."""
    parsed_symbols = [s.strip().upper() for s in symbols.split(",") if s.strip()] if symbols else None
    return ai_prediction_service.generate_signals(symbols=parsed_symbols, limit=limit)


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


@router.get("/options-chain")
def options_chain() -> dict:
    """Get NSE option chain intelligence with scoring and structure analytics."""
    analysis = option_chain_service.get_analysis()
    smart_money = smart_money_service.detect(analysis)
    trap_signals = trap_detector_service.detect(analysis, smart_money)
    volume_profile = volume_profile_service.compute(analysis)
    gamma_exposure = gamma_service.compute(analysis)

    return {
        "option_chain_analysis": analysis,
        "smart_money": smart_money,
        "option_traps": trap_signals,
        "volume_profile": volume_profile,
        "gamma_exposure": gamma_exposure,
    }


@router.get("/smart-money")
def smart_money() -> dict:
    """Get smart money regime classification and trap overlays."""
    analysis = option_chain_service.get_analysis()
    smart_money_data = smart_money_service.detect(analysis)
    trap_signals = trap_detector_service.detect(analysis, smart_money_data)
    gamma_exposure = gamma_service.compute(analysis)

    return {
        "smart_money": smart_money_data,
        "option_traps": trap_signals,
        "gamma_exposure": gamma_exposure,
    }


@router.get("/liquidity-heatmap")
def liquidity_heatmap() -> dict:
    """Get strike-wise liquidity heatmap and breakout trap zones."""
    analysis = option_chain_service.get_analysis()
    smart_money_data = smart_money_service.detect(analysis)
    trap_signals = trap_detector_service.detect(analysis, smart_money_data)
    heatmap = liquidity_service.build(analysis, trap_signals)

    return {
        "liquidity_heatmap": heatmap,
        "smart_money": smart_money_data,
        "option_traps": trap_signals,
    }
