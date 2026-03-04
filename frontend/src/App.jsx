import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import AiSignalsPage from './pages/AiSignalsPage';
import DashboardPage from './pages/DashboardPage';
import FiiDiiPage from './pages/FiiDiiPage';
import MarketBreadthPage from './pages/MarketBreadthPage';
import NiftyHeatmapPage from './pages/NiftyHeatmapPage';
import NiftyOverviewPage from './pages/NiftyOverviewPage';
import OptionChainPage from './pages/OptionChainPage';
import SectorStrengthPage from './pages/SectorStrengthPage';
import SmartMoneyPage from './pages/SmartMoneyPage';
import StockAnalysisPage from './pages/StockAnalysisPage';

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/nifty-overview" element={<NiftyOverviewPage />} />
        <Route path="/nifty-heatmap" element={<NiftyHeatmapPage />} />
        <Route path="/stock-analysis" element={<StockAnalysisPage />} />
        <Route path="/options-chain" element={<OptionChainPage />} />
        <Route path="/sector-strength" element={<SectorStrengthPage />} />
        <Route path="/market-breadth" element={<MarketBreadthPage />} />
        <Route path="/fii-dii" element={<FiiDiiPage />} />
        <Route path="/smart-money" element={<SmartMoneyPage />} />
        <Route path="/ai-signals" element={<AiSignalsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  );
}
