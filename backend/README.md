# Nifty AI Analyzer Pro - Backend Core

Production-ready FastAPI backend foundation for an AI-powered trading analytics platform.

## Tech Stack

- Python
- FastAPI
- Pandas
- NumPy
- TA-Lib
- scikit-learn
- XGBoost (pipeline placeholders only, no training)

## Project Structure

```text
/backend
 ├── app
 │   ├── main.py
 │   ├── api
 │   │   └── routes.py
 │   ├── services
 │   │   ├── data_fetcher.py
 │   │   ├── technical_analysis.py
 │   │   ├── fundamental_analysis.py
 │   │   ├── market_breadth.py
 │   │   ├── sector_rotation.py
 │   │   ├── fii_dii_tracker.py
 │   │   └── intraday_volume.py
 │   └── utils
 │       └── scoring.py
 ├── requirements.txt
 └── README.md
```

## Features Implemented

### Data Fetching

- NIFTY 50 symbol list and quote fetching.
- Index data (`^NSEI`) for OHLC/volume candles.
- Generic OHLC historical candle fetch for any NSE symbol.
- NSE fallback support for FII/DII activity.
- Synthetic deterministic fallback data in case of provider failure.

### Technical Analysis

Implements:
- RSI
- MACD
- MA20 / MA50 / MA200
- VWAP
- Bollinger Bands
- Support & Resistance
- Trend Strength (ADX or fallback)

Outputs:
- `technical_score` in range 0–100.

### Fundamental Analysis

Computes a normalized 0–100 `fundamental_score` from:
- PE, PB, ROE, ROCE
- Debt/Equity
- EPS Growth
- Revenue Growth
- Promoter Holding

### Market Breadth

Provides:
- Advance/Decline ratio
- Volume breadth
- Market strength label

### Additional Market Modules

- Sector strength ranking (`/api/sector-strength`)
- FII/DII flow tracking (`/api/fii-dii`)
- Intraday volume context for overview

## API Endpoints

- `GET /api/nifty-overview`
- `GET /api/stock-analysis/{symbol}`
- `GET /api/market-breadth`
- `GET /api/sector-strength`
- `GET /api/fii-dii`

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Notes

- XGBoost and scikit-learn are included for upcoming model-serving and training extensions.
- No ML training logic is added yet by design.
- External market data provider dependencies can be unstable; fallback paths are implemented.
