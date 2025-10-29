import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import TradeAnalyzer from './components/TradeAnalyzer';
import LeagueConnect from './components/LeagueConnect';
import RosterPage from './pages/RosterPage';
import { LeagueProvider } from './context/LeagueContext';

function App() {
  return (
    <LeagueProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
          <Header />
          <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="max-w-7xl mx-auto">
              <Routes>
                <Route path="/" element={<LeagueConnect />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/trade" element={<TradeAnalyzer />} />
                <Route path="/roster" element={<RosterPage />} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </LeagueProvider>
  );
}

export default App;
