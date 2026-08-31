import React from 'react';
import { Link } from 'react-router-dom';
import HeroRecordAnimation from '../components/HeroRecordAnimation';

export default function Home() {
  const sections = [
    { path: '/problem', title: 'Page 1 — The Problem', desc: 'Panel mortgage data structure, noise patterns, and the 8 required analytical tasks.' },
    { path: '/data-intelligence', title: 'Page 2 — Data Intelligence', desc: 'Missingness profiles, temporal feature drift, rule breaches, and data quality scoring.' },
    { path: '/prediction-survival', title: 'Page 3 — Prediction & Survival', desc: 'Calibrated multi-outcome risk models, Cox PH survival curves, and the exception_required leakage audit.' },
    { path: '/scenario-stress', title: 'Page 4 — Scenario & Stress', desc: 'Base, Adverse-Credit, and High-Prepayment macro shock projections across risk segments.' },
    { path: '/reviewer-copilot', title: 'Page 5 — The Reviewer Copilot', desc: '24 curated audit cases, TreeSHAP attribution, grounded memos, and HAL-001..004 safety guardrails.' },
    { path: '/how-we-got-here', title: 'Page 6 — How We Got Here', desc: 'Chronological timeline of real defects diagnosed and resolved during agentic development.' },
    { path: '/deliverables', title: 'Page 7 — Deliverables', desc: '304,374-row competition submission file, formal Model Card, and development audit logs.' },
  ];

  return (
    <div style={{ maxWidth: 'var(--site-max-width)', margin: '0 auto' }}>
      {/* Institutional Hero Banner */}
      <div style={{ padding: 'var(--space-8) 0 var(--space-4)', borderBottom: '2px solid var(--ledger-ink)' }}>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 'var(--text-xs)',
          color: 'var(--brass)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          display: 'block',
          marginBottom: 'var(--space-2)'
        }}>
          Intain Campus FinTech Challenge 2026 &bull; AI Track
        </span>
        <h1 style={{
          fontSize: 'clamp(2rem, 4vw, 3.2rem)',
          lineHeight: 'var(--leading-tight)',
          color: 'var(--ledger-ink)',
          marginBottom: 'var(--space-4)'
        }}>
          Loan Performance Intelligence Engine
        </h1>
        <p style={{
          fontSize: 'var(--text-lg)',
          color: 'var(--ink-muted)',
          maxWidth: '820px',
          lineHeight: 'var(--leading-normal)'
        }}>
          An enterprise-grade machine learning system for loan-data profiling, calibrated multi-outcome performance prediction, 4-layer hybrid anomaly detection, macroeconomic stress simulation, TreeSHAP explainability, and grounded LLM reviewer copilots.
        </p>
      </div>

      {/* The Single Motion Moment: Animated Reconciled Loan Record */}
      <HeroRecordAnimation />

      {/* Core Ledger Wayfinding Directory */}
      <div style={{ marginTop: 'var(--space-10)', marginBottom: 'var(--space-12)' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          borderBottom: '1px solid var(--ledger-ink)',
          paddingBottom: 'var(--space-2)',
          marginBottom: 'var(--space-6)'
        }}>
          <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-xl)' }}>
            System Architecture & Analytical Sections
          </h2>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>
            7 Verified Evaluation Modules
          </span>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 'var(--space-6)'
        }}>
          {sections.map((sec, idx) => (
            <Link
              key={idx}
              to={sec.path}
              className="ledger-card"
              style={{
                textDecoration: 'none',
                color: 'inherit',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'border-color 0.15s ease, background-color 0.15s ease',
                margin: 0
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--brass)';
                e.currentTarget.style.backgroundColor = 'var(--paper-subtle)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--faint-rule)';
                e.currentTarget.style.backgroundColor = 'var(--paper-card)';
              }}
            >
              <div>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--brass)', display: 'block', marginBottom: '4px' }}>
                  Section {String(idx + 1).padStart(2, '0')}
                </span>
                <h3 style={{ fontSize: 'var(--text-md)', marginBottom: 'var(--space-2)', color: 'var(--ledger-ink)' }}>
                  {sec.title.split('—')[1]?.trim() || sec.title}
                </h3>
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', lineHeight: 'var(--leading-snug)' }}>
                  {sec.desc}
                </p>
              </div>

              <div style={{ marginTop: 'var(--space-4)', paddingTop: 'var(--space-2)', borderTop: '1px dashed var(--faint-rule)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>
                  Open Module
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>
                  &rarr;
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
