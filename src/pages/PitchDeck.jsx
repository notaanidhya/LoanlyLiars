import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, Printer } from 'lucide-react';
import MarginColumn from '../components/MarginColumn';

export default function PitchDeck() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const totalSlides = 10;

  const nextSlide = () => {
    if (currentSlide < totalSlides - 1) setCurrentSlide(currentSlide + 1);
  };

  const prevSlide = () => {
    if (currentSlide > 0) setCurrentSlide(currentSlide - 1);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="page-grid">
      <MarginColumn
        sectionNumber="08"
        sectionTitle="Pitch Deck"
        contextInfo="Executive Memorandum and Presentation Slides"
        subLinks={[
          { id: 'slide-viewer', label: 'Executive Deck Viewer' }
        ]}
      />

      <div className="content-column">
        <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>Executive Pitch Deck & Memorandum</h1>
            <p className="page-lead">
              Institutional presentation dossier covering end-to-end architecture, multi-outcome predictive modeling, survival analysis, anomaly arbitration, and governance guardrails.
            </p>
          </div>

          <button
            type="button"
            onClick={handlePrint}
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-xs)',
              fontWeight: 700,
              padding: '8px 16px',
              backgroundColor: 'var(--brass)',
              color: 'var(--ledger-paper)',
              border: 'none',
              borderRadius: '2px',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Printer size={14} /> Print / Export PDF
          </button>
        </header>

        <section id="slide-viewer" style={{ marginBottom: 'var(--space-8)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--paper-subtle)', padding: '8px 16px', border: '1px solid var(--brass)', borderRadius: '2px 2px 0 0' }}>
            <span className="mono-data" style={{ fontSize: 'var(--text-sm)', fontWeight: 700 }}>
              Slide {currentSlide + 1} of {totalSlides}
            </span>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                onClick={prevSlide}
                disabled={currentSlide === 0}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  padding: '4px 12px',
                  backgroundColor: currentSlide === 0 ? 'var(--paper-card)' : 'var(--ledger-ink)',
                  color: currentSlide === 0 ? 'var(--ink-dim)' : 'var(--ledger-paper)',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: currentSlide === 0 ? 'not-allowed' : 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <ArrowLeft size={12} /> Prev
              </button>
              <button
                type="button"
                onClick={nextSlide}
                disabled={currentSlide === totalSlides - 1}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  padding: '4px 12px',
                  backgroundColor: currentSlide === totalSlides - 1 ? 'var(--paper-card)' : 'var(--ledger-ink)',
                  color: currentSlide === totalSlides - 1 ? 'var(--ink-dim)' : 'var(--ledger-paper)',
                  border: 'none',
                  borderRadius: '2px',
                  cursor: currentSlide === totalSlides - 1 ? 'not-allowed' : 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                Next <ArrowRight size={12} />
              </button>
            </div>
          </div>

          <div className="ledger-card" style={{ margin: 0, minHeight: '440px', borderTop: 'none', borderRadius: '0 0 2px 2px', padding: 'var(--space-6)' }}>
            {currentSlide === 0 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                  Intain Campus FinTech Challenge 2026 • AI Track • Executive Memorandum
                </span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-3xl)', margin: 'var(--space-2) 0 var(--space-4)' }}>
                  Loan Performance Intelligence Engine
                </h2>
                <p style={{ fontSize: 'var(--text-md)', color: 'var(--ink-muted)', marginBottom: 'var(--space-6)', fontStyle: 'italic' }}>
                  An Enterprise ML-First System for Mortgage Risk Forecasting, Hybrid Anomaly Arbitration, Macro Stress Simulation, and Governed Copilot Review.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--space-4)' }}>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>PORTFOLIO SCALE</span>
                    <strong className="mono-data" style={{ fontSize: 'var(--text-2xl)', display: 'block', color: 'var(--ledger-ink)', marginTop: '4px' }}>712,107</strong>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>Monthly panel records</span>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>TEST INTEGRITY</span>
                    <strong className="mono-data" style={{ fontSize: 'var(--text-2xl)', display: 'block', color: 'var(--ledger-ink)', marginTop: '4px' }}>304,374</strong>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--reconciled-green)', fontWeight: 700 }}>100% verified • 0 nulls</span>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>12M DEFAULT ROC-AUC</span>
                    <strong className="mono-data" style={{ fontSize: 'var(--text-2xl)', display: 'block', color: 'var(--reconciled-green)', marginTop: '4px' }}>0.8595</strong>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>+108.4% PR-AUC lift</span>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>COX PH C-STAT</span>
                    <strong className="mono-data" style={{ fontSize: 'var(--text-2xl)', display: 'block', color: 'var(--brass)', marginTop: '4px' }}>0.6866</strong>
                    <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>Survival timing accuracy</span>
                  </div>
                </div>
              </div>
            )}

            {currentSlide === 1 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 01 / PROBLEM CONTEXT</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  The Challenge: Moving Beyond Shallow AI Wrappers
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>1. Disparate and Messy Feeds</h3>
                    <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)' }}>
                      Mortgage tapes arrive with conflicting balances, missing borrower data, and non-standard date sequences across 53 jurisdictions.
                    </p>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>2. Competing Dual-Hazards</h3>
                    <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)' }}>
                      Credit risk is not a single binary label. High-FICO borrowers refinance voluntarily under rate drops while low-FICO borrowers default under leverage shocks.
                    </p>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>3. High-Stakes Governance</h3>
                    <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)' }}>
                      Ungrounded LLMs hallucinate exact FICO points and overrule accounting rules. Systems must enforce deterministic override layers.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {currentSlide === 2 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 02 / ARCHITECTURE</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  End-to-End Enterprise Quantitative Architecture
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-3)', marginTop: 'var(--space-4)' }}>
                  {[
                    { title: '1. Ingestion and Profiling', desc: '712k panel records; MCAR/MNAR audit' },
                    { title: '2. Zero-Leakage FE', desc: '44 features with boundary lag persistence' },
                    { title: '3. Predictive Models', desc: 'Calibrated XGBoost for Default and Prepayment' },
                    { title: '4. Hazard Engine', desc: 'Cox PH (C-stat 0.6866) and competing curves' },
                    { title: '5. Anomaly Engine', desc: 'Differential Evolution weight optimization' },
                    { title: '6. TreeSHAP Attribution', desc: 'Decoupled credit decay vs refinance drivers' },
                    { title: '7. Stress Engine', desc: '36M capital loss-at-risk simulation' },
                    { title: '8. Governed Copilot', desc: 'Grounded memos with deterministic overrides' }
                  ].map((s, idx) => (
                    <div key={idx} className="ledger-card" style={{ margin: 0, padding: 'var(--space-3)' }}>
                      <strong className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)', display: 'block' }}>{s.title}</strong>
                      <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginTop: '4px', display: 'block' }}>{s.desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {currentSlide === 3 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 03 / DATA INTELLIGENCE</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  Strict Zero-Leakage Validation and Panel Profiling
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)', marginTop: 'var(--space-4)' }}>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Leakage Elimination Protocol</h3>
                    <ul style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', paddingLeft: '18px', lineHeight: 1.6 }}>
                      <li><strong>Chronological 3-Way Split:</strong> Train 70% (through 2021-06), Calibration 15%, Validation 15%.</li>
                      <li><strong>Boundary Lag Persistence:</strong> FeatureEngineer.history_tail_df eliminates lag collapse.</li>
                      <li><strong>Transition Universe Masking:</strong> Prevents post-default memorization.</li>
                    </ul>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Dataset Profile Findings</h3>
                    <ul style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', paddingLeft: '18px', lineHeight: 1.6 }}>
                      <li><strong>Mean Data Quality Score:</strong> 99.3 / 100 (only 0.06% below 80).</li>
                      <li><strong>Structural Censoring:</strong> 35.45% nulls in 12M default handled via dynamic right-censoring.</li>
                      <li><strong>Contractual Rule Breaches:</strong> VR-001 (0.79%) and VR-003 (4.58%) detected.</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {currentSlide === 4 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 04 / PREDICTIVE ML</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  Multi-Horizon Supervised Learning Benchmarks
                </h2>
                <table className="ledger-table" style={{ width: '100%', marginTop: 'var(--space-3)' }}>
                  <thead>
                    <tr>
                      <th>Target Horizon</th>
                      <th>Baseline Model</th>
                      <th>Base PR-AUC</th>
                      <th>XGBoost PR-AUC</th>
                      <th>PR-AUC Lift</th>
                      <th>XGBoost ROC-AUC</th>
                      <th>Brier Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>next_12m_default_flag</strong></td>
                      <td>Scaled Logistic Reg</td>
                      <td className="mono-data">0.1622</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>0.3380</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>+108.4%</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>0.8595</td>
                      <td className="mono-data">0.0273</td>
                    </tr>
                    <tr>
                      <td><strong>next_3m_delinquency_flag</strong></td>
                      <td>Scaled Logistic Reg</td>
                      <td className="mono-data">0.3134</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>0.6368</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>+103.2%</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>0.8916</td>
                      <td className="mono-data">0.0253</td>
                    </tr>
                    <tr>
                      <td><strong>next_6m_delinquency_flag</strong></td>
                      <td>Scaled Logistic Reg</td>
                      <td className="mono-data">0.3019</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>0.5812</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>+92.5%</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>0.8827</td>
                      <td className="mono-data">0.0442</td>
                    </tr>
                    <tr>
                      <td><strong>next_12m_prepayment_flag</strong></td>
                      <td>Scaled Logistic Reg</td>
                      <td className="mono-data">0.3791</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>0.5048</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>+33.2%</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>0.6542</td>
                      <td className="mono-data">0.1943</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {currentSlide === 5 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 05 / SURVIVAL ANALYSIS</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  Time-to-Event Survival and Roll-Rate Dynamics
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)', marginTop: 'var(--space-4)' }}>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Cox PH Model (C-stat: 0.6866)</h3>
                    <ul style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', paddingLeft: '18px', lineHeight: 1.6 }}>
                      <li><strong>Interest Rate Spread Shock:</strong> 1.204x Hazard Ratio (p &lt; 0.0001)</li>
                      <li><strong>Loan Age at Origination:</strong> 1.095x Hazard Ratio (p = 0.0246)</li>
                      <li><strong>DTI Shock Index:</strong> 1.075x Hazard Ratio (p &lt; 0.0001)</li>
                      <li><strong>LTV Leverage Index:</strong> 1.049x Hazard Ratio (p = 0.0001)</li>
                    </ul>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Empirical Markov Roll Dynamics</h3>
                    <ul style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', paddingLeft: '18px', lineHeight: 1.6 }}>
                      <li><strong>30DPD Cure Rate:</strong> 37.4% cure back to CURRENT status.</li>
                      <li><strong>Terminal Accumulation:</strong> 90+ DPD bucket shows 86.9% persistence.</li>
                      <li><strong>Cumulative Prepayment:</strong> Scales from 1.12% at 3M to 55.48% at 24M.</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {currentSlide === 6 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 06 / ANOMALY ARBITRATION</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  4-Layer Anomaly Engine and Action Precedence
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)', marginTop: 'var(--space-4)' }}>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Calibrated Optimal Weights (DE)</h3>
                    <p className="mono-data" style={{ fontSize: 'var(--text-xs)', backgroundColor: 'var(--paper-subtle)', padding: '6px', borderRadius: '2px', marginBottom: '12px' }}>
                      S_anomaly = 0.463*S_rule + 0.364*S_ML + 0.135*S_servicer + 0.038*S_DQ
                    </p>
                    <ul style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', paddingLeft: '18px', lineHeight: 1.6 }}>
                      <li><strong>Validation Rules (46.3%):</strong> VR-001..VR-008 checks.</li>
                      <li><strong>Unsupervised ML (36.4%):</strong> Isolation Forest (200 trees).</li>
                      <li><strong>Servicer Reconciliation (13.5%):</strong> VR-007 balance drift.</li>
                      <li><strong>Data Quality (3.8%):</strong> Format integrity and nulls.</li>
                    </ul>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Prescriptive Action Distribution</h3>
                    <ul style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', listStyle: 'none', lineHeight: 1.8 }}>
                      <li><strong style={{ color: 'var(--reconciled-green)' }}>AUTO_APPROVE:</strong> 284,641 (93.52%) | Mean Conf: 0.90</li>
                      <li><strong style={{ color: 'var(--brass)' }}>REQUEST_CURE:</strong> 9,772 (3.21%) | Mean Conf: 0.86</li>
                      <li><strong style={{ color: 'var(--flagged-red)' }}>OVERRIDE_SERVICER:</strong> 3,164 (1.04%) | Mean Conf: 0.81</li>
                      <li><strong style={{ color: 'var(--flagged-red)' }}>MANUAL_AUDIT:</strong> 2,871 (0.94%) | Mean Conf: 0.90</li>
                      <li><strong style={{ color: 'var(--flagged-red)' }}>ESCALATE_DOC_REVIEW:</strong> 2,264 (0.74%) | Mean Conf: 0.93</li>
                      <li><strong style={{ color: 'var(--reconciled-green)' }}>ACCEPT_PRIMARY:</strong> 1,662 (0.55%) | Mean Conf: 0.95</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {currentSlide === 7 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 07 / EXPLAINABILITY</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  Dual-Risk TreeSHAP Explainability and Diagnostics
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)', marginTop: 'var(--space-4)' }}>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Credit Risk Drivers</h3>
                    <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)' }}>
                      Default and delinquency risk are primarily pushed by dpd_3m_mean, dti_x_ltv, status_severity, and delinquency_velocity.
                    </p>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Voluntary Duration Refinance Drivers</h3>
                    <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)' }}>
                      Prepayment yield risk is concentrated in high-FICO, low-LTV prime borrowers driven by prepayment_incentive (rate spread to market average).
                    </p>
                  </div>
                </div>
              </div>
            )}

            {currentSlide === 8 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 08 / SCENARIO STRESS</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  Macroeconomic Stress and Capital Loss-at-Risk
                </h2>
                <table className="ledger-table" style={{ width: '100%', marginTop: 'var(--space-3)' }}>
                  <thead>
                    <tr>
                      <th>Macro Trajectory</th>
                      <th>12M Default %</th>
                      <th>12M Prepay %</th>
                      <th>Performing Balance</th>
                      <th>Loss at Risk (35% Sev)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>Base Case</strong> (1.0x hazard)</td>
                      <td className="mono-data">2.57%</td>
                      <td className="mono-data">35.11%</td>
                      <td className="mono-data">$32.09 Billion</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>$463.1 Million</td>
                    </tr>
                    <tr>
                      <td><strong>Adverse Credit</strong> (+150 bps, -10% HPA)</td>
                      <td className="mono-data" style={{ color: 'var(--flagged-red)', fontWeight: 700 }}>2.71%</td>
                      <td className="mono-data">31.43%</td>
                      <td className="mono-data">$33.91 Billion</td>
                      <td className="mono-data" style={{ color: 'var(--flagged-red)', fontWeight: 700 }}>$488.4 Million</td>
                    </tr>
                    <tr>
                      <td><strong>High Prepayment</strong> (-150 bps, +6% HPA)</td>
                      <td className="mono-data">1.63%</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>77.38%</td>
                      <td className="mono-data">$10.81 Billion</td>
                      <td className="mono-data" style={{ color: 'var(--reconciled-green)', fontWeight: 700 }}>$293.7 Million</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {currentSlide === 9 && (
              <div>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)' }}>SECTION 09 / AI GOVERNANCE AND DELIVERABLES</span>
                <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-2xl)', margin: 'var(--space-2) 0' }}>
                  Governed Reviewer Copilot and Complete Submission Catalog
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)', marginTop: 'var(--space-4)' }}>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Audited Hallucination Catalog</h3>
                    <ul style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', paddingLeft: '18px', lineHeight: 1.6 }}>
                      <li><strong>HAL-001 (Accounting Invariant):</strong> Rejects PASS on prepaid loans with active balances &rarr; enforces MANUAL_AUDIT.</li>
                      <li><strong>HAL-002 (Point Fabrication):</strong> Filters hallucinated point FICO &rarr; grounds to discrete bands.</li>
                      <li><strong>HAL-003 (Overconfidence):</strong> Blocks 100% default claims &rarr; bounds by 37.4% cure rate.</li>
                      <li><strong>HAL-004 (Threshold Drift):</strong> Catches $70k balance conflicts &rarr; enforces OVERRIDE_SERVICER.</li>
                    </ul>
                  </div>
                  <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                    <h3 style={{ fontSize: 'var(--text-md)', marginBottom: '8px' }}>Competition Delivery Catalog</h3>
                    <ul style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', listStyle: 'none', lineHeight: 1.8 }}>
                      <li>✓ <strong>Live Web App:</strong> <a href="https://loanly-liars.vercel.app/" target="_blank" rel="noreferrer">loanly-liars.vercel.app</a></li>
                      <li>✓ <strong>Final Submission:</strong> submission.csv (304,374 rows, 0 nulls)</li>
                      <li>✓ <strong>Formal Model Card:</strong> reports/model_card.md</li>
                      <li>✓ <strong>CLI Terminal Demo:</strong> python demo.py (sub-5s inference)</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
