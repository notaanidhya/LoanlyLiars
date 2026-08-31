import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Link } from 'react-router-dom';

// Components
import ScrollToTop from './components/ScrollToTop';

// Pages
import Home from './pages/Home';
import Problem from './pages/Problem';
import DataIntelligence from './pages/DataIntelligence';
import PredictionSurvival from './pages/PredictionSurvival';
import ScenarioStress from './pages/ScenarioStress';
import ReviewerCopilot from './pages/ReviewerCopilot';
import HowWeGotHere from './pages/HowWeGotHere';
import Deliverables from './pages/Deliverables';
import PitchDeck from './pages/PitchDeck';

export default function App() {
  const navTabs = [
    { path: '/', label: 'Overview' },
    { path: '/problem', label: '1. The Problem' },
    { path: '/data-intelligence', label: '2. Data Intelligence' },
    { path: '/prediction-survival', label: '3. Prediction & Survival' },
    { path: '/scenario-stress', label: '4. Scenario & Stress' },
    { path: '/reviewer-copilot', label: '5. Reviewer Copilot' },
    { path: '/how-we-got-here', label: '6. How We Got Here' },
    { path: '/deliverables', label: '7. Deliverables' },
    { path: '/pitch', label: '8. Pitch Deck' },
  ];

  return (
    <Router>
      <ScrollToTop />
      <div className="app-wrapper">
        {/* Sticky Site Header with Ledger Wayfinding Tabs */}
        <header className="site-header">
          <div className="header-top">
            <div>
              <Link to="/" className="site-title">
                Loan Performance Intelligence Engine
              </Link>
            </div>
            <div className="site-subtitle">
              Intain Campus FinTech Challenge 2026 &bull; AI Track
            </div>
          </div>

          {/* Horizontal Ledger Navigation Strip */}
          <nav className="wayfinding-nav" aria-label="Main Navigation">
            {navTabs.map((tab) => (
              <NavLink
                key={tab.path}
                to={tab.path}
                className={({ isActive }) => `ledger-tab ${isActive ? 'active' : ''}`}
                end={tab.path === '/'}
              >
                {tab.label}
              </NavLink>
            ))}
          </nav>
        </header>

        {/* Main Content Body */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/problem" element={<Problem />} />
            <Route path="/data-intelligence" element={<DataIntelligence />} />
            <Route path="/prediction-survival" element={<PredictionSurvival />} />
            <Route path="/scenario-stress" element={<ScenarioStress />} />
            <Route path="/reviewer-copilot" element={<ReviewerCopilot />} />
            <Route path="/how-we-got-here" element={<HowWeGotHere />} />
            <Route path="/deliverables" element={<Deliverables />} />
            <Route path="/pitch" element={<PitchDeck />} />
          </Routes>
        </main>

        {/* Institutional Site Footer */}
        <footer className="site-footer">
          <div className="footer-content">
            <div>
              <span className="footer-brand">Loan Performance Intelligence Engine</span>
              <p style={{ marginTop: '2px', color: 'var(--ink-dim)' }}>
                Multi-Outcome Predictive Modeling, Anomaly Arbitrator & Governed LLM Copilot
              </p>
            </div>
            <div style={{ textAlign: 'right', fontFamily: 'var(--font-mono)' }}>
              <span>Freddie Mac Panel Benchmark &bull; 712,107 Records</span>
              <p style={{ marginTop: '2px' }}>MIT License &bull; Team LoanlyLiars</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}
