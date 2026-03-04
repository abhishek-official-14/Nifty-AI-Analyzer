import axios from 'axios';
import { mockData, mockStockAnalysis } from '../mocks/mockData';

const api = axios.create({
  baseURL: '/',
  timeout: 5000,
});

const withFallback = async (path, fallbackFactory) => {
  try {
    const response = await api.get(path);
    return response.data;
  } catch {
    return fallbackFactory();
  }
};

export const fetchNiftyOverview = () => withFallback('/api/nifty-overview', () => mockData['/api/nifty-overview']);
export const fetchHeatmap = () => withFallback('/api/nifty-heatmap', () => mockData['/api/nifty-heatmap']);
export const fetchStockAnalysis = (symbol) =>
  withFallback(`/api/stock-analysis/${symbol}`, () => mockStockAnalysis(symbol));
export const fetchOptionsChain = () => withFallback('/api/options-chain', () => mockData['/api/options-chain']);
export const fetchSectorStrength = () => withFallback('/api/sector-strength', () => mockData['/api/sector-strength']);
export const fetchMarketBreadth = () => withFallback('/api/market-breadth', () => mockData['/api/market-breadth']);
export const fetchFiiDii = () => withFallback('/api/fii-dii', () => mockData['/api/fii-dii']);
export const fetchSmartMoney = () => withFallback('/api/smart-money', () => mockData['/api/smart-money']);
export const fetchLiquidityHeatmap = () =>
  withFallback('/api/liquidity-heatmap', () => mockData['/api/liquidity-heatmap']);
export const fetchAiSignals = () => withFallback('/api/ai-signals', () => mockData['/api/ai-signals']);
