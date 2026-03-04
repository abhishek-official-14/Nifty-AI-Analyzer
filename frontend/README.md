# Nifty AI Analyzer Pro Frontend

## Stack
- React + Vite
- TailwindCSS
- Axios
- Chart.js
- TradingView Lightweight Charts

## Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints Consumed
- `/api/nifty-overview`
- `/api/nifty-heatmap`
- `/api/stock-analysis/{symbol}`
- `/api/options-chain`
- `/api/sector-strength`
- `/api/market-breadth`
- `/api/fii-dii`
- `/api/smart-money`
- `/api/liquidity-heatmap`
- `/api/ai-signals`

If backend is unavailable, UI gracefully falls back to local mock data in `src/mocks/mockData.js`.
