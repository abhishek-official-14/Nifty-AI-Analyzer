export const mockData = {
  '/api/nifty-overview': {
    nifty: { value: 22435.2, change: 126.35, changePercent: 0.57 },
    trend: Array.from({ length: 20 }).map((_, i) => ({
      time: `2026-03-${String(i + 1).padStart(2, '0')}`,
      value: 21900 + i * 20 + Math.round((Math.random() - 0.3) * 80),
    })),
    topGainers: [
      { symbol: 'HDFCBANK', change: 2.8 },
      { symbol: 'TCS', change: 2.1 },
      { symbol: 'RELIANCE', change: 1.9 },
    ],
    topLosers: [
      { symbol: 'SBIN', change: -1.3 },
      { symbol: 'NTPC', change: -1.1 },
      { symbol: 'UPL', change: -0.9 },
    ],
    pcr: 1.12,
    maxPain: 22300,
    aiSentiment: 'Bullish',
  },
  '/api/nifty-heatmap': [
    { symbol: 'RELIANCE', technical: 82, options: 75, fundamental: 90, confidence: 88, bias: 'Bullish' },
    { symbol: 'HDFCBANK', technical: 46, options: 53, fundamental: 77, confidence: 61, bias: 'Neutral' },
    { symbol: 'INFY', technical: 28, options: 35, fundamental: 70, confidence: 44, bias: 'Bearish' },
    { symbol: 'TCS', technical: 67, options: 62, fundamental: 81, confidence: 72, bias: 'Bullish' },
  ],
  '/api/options-chain': { pcr: 1.12, maxPain: 22300, callOI: 2.4, putOI: 2.7 },
  '/api/sector-strength': [
    { sector: 'Banking', score: 86 },
    { sector: 'IT', score: 74 },
    { sector: 'Auto', score: 66 },
    { sector: 'FMCG', score: 58 },
    { sector: 'Metal', score: 39 },
  ],
  '/api/market-breadth': { advances: 34, declines: 16, unchanged: 0, ratio: 2.1 },
  '/api/fii-dii': {
    history: [
      { date: '2026-02-27', fii: -1200, dii: 980 },
      { date: '2026-02-28', fii: 430, dii: 220 },
      { date: '2026-03-01', fii: 780, dii: -110 },
      { date: '2026-03-02', fii: 940, dii: 330 },
      { date: '2026-03-03', fii: -150, dii: 460 },
    ],
  },
  '/api/smart-money': [
    { instrument: 'NIFTY 22500 CE', action: 'Accumulation', volume: 120000, conviction: 82 },
    { instrument: 'BANKNIFTY 48000 PE', action: 'Unwinding', volume: 95000, conviction: 64 },
    { instrument: 'FINNIFTY FUT', action: 'Long Build-up', volume: 67000, conviction: 75 },
  ],
  '/api/liquidity-heatmap': [
    { zone: '22400', liquidity: 'High', intensity: 90 },
    { zone: '22300', liquidity: 'Medium', intensity: 61 },
    { zone: '22200', liquidity: 'Low', intensity: 40 },
  ],
  '/api/ai-signals': [
    { symbol: 'NIFTY', signal: 'BUY', confidence: 84, horizon: 'Intraday' },
    { symbol: 'BANKNIFTY', signal: 'HOLD', confidence: 63, horizon: 'Swing' },
    { symbol: 'RELIANCE', signal: 'SELL', confidence: 71, horizon: 'Positional' },
  ],
};

export const mockStockAnalysis = (symbol) => ({
  symbol,
  ltp: 1240.75,
  trend: 'Bullish',
  technicals: [
    { metric: 'RSI', value: 62 },
    { metric: 'MACD', value: 1.3 },
    { metric: 'ADX', value: 28 },
  ],
  recommendation: 'Buy on Dips',
  confidence: 78,
});
