import React from 'react';
import MarginColumn from '../components/MarginColumn';

export default function Problem() {
  const tasks = [
    { id: 't1', title: 'Task 1: Data Intelligence & Profiling', desc: 'Diagnosing distributional shifts, missingness (MCAR vs MAR), cross-column relationship breaks, and data-quality scores.' },
    { id: 't2', title: 'Task 2: Multi-Outcome Risk Prediction', desc: 'Predicting delinquency, default, and prepayment across 3M, 6M, and 12M horizons with strict time-aware validation.' },
    { id: 't3', title: 'Task 3: Time-to-Event Survival Modeling', desc: 'Estimating non-parametric Kaplan-Meier and semi-parametric Cox Proportional Hazards curves under right-censoring.' },
    { id: 't4', title: 'Task 4: Anomaly & Exception Detection', desc: 'Synthesizing unsupervised Isolation Forest scores with deterministic rule breaches and servicer reconciliation.' },
    { id: 't5', title: 'Task 5: Scenario & Stress Simulation', desc: 'Simulating portfolio performance under Base, Adverse-Credit (+150bps rate), and High-Prepayment (-150bps rate) shocks.' },
    { id: 't6', title: 'Task 6: Explainability & Error Analysis', desc: 'Attributing risk drivers via directional TreeSHAP log-odds, analyzing false positives and false negatives.' },
    { id: 't7', title: 'Task 7: Governed Reviewer Copilot', desc: 'Generating natural-language reviewer audit memos with deterministic hallucination guardrails (HAL-001..004).' },
    { id: 't8', title: 'Task 8: Agentic Development Governance', desc: 'Documenting human-in-the-loop decisions, rejected AI proposals, and reproducible competition artifacts.' },
  ];

  return (
    <div className="page-grid">
      <MarginColumn
        sectionNumber="01"
        sectionTitle="The Problem"
        contextInfo="Panel Loan Architecture, Data Realities & The 8 Core Tasks"
        subLinks={[
          { id: 'panel-structure', label: 'Panel Structure' },
          { id: 'data-realities', label: 'Data Realities' },
          { id: 'core-tasks', label: 'The 8 Challenge Tasks' }
        ]}
      />

      <div className="content-column">
        <header className="page-header">
          <h1>Panel Data Structure & Analytical Scope</h1>
          <p className="page-lead">
            Mortgage portfolios evolve across time as dynamic panel datasets where single loans generate monthly performance updates over multi-year horizons.
          </p>
        </header>

        {/* Section 1: The Loan x Month Panel Grid Visual Device */}
        <section id="panel-structure" style={{ marginBottom: 'var(--space-8)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-3)' }}>
            1. The Panel Data Structure (Loan &times; Month Matrix)
          </h2>
          <p style={{ marginBottom: 'var(--space-4)' }}>
            Unlike static cross-sectional tabular data where each row represents an independent borrower, residential mortgage performance data is a longitudinal panel. Each loan enters at origination and generates a monthly observation tracking balance amortization, interest rates, payment status, delinquency transitions, and servicer updates until termination.
          </p>

          {/* Visual Matrix Container */}
          <div className="ledger-card" style={{ padding: 'var(--space-4)' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              borderBottom: '1px solid var(--brass)',
              paddingBottom: 'var(--space-2)',
              marginBottom: 'var(--space-3)'
            }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--brass)', textTransform: 'uppercase' }}>
                Panel Observation Grid & Temporal Split Boundary
              </span>
              <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>
                712,107 Total Monthly Observations &bull; 20,000 Unique Loans
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr 1fr 1fr 1fr', gap: '8px', fontSize: 'var(--text-xs)', textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, textAlign: 'left', color: 'var(--ledger-ink)' }}>Loan ID</div>
              <div style={{ backgroundColor: 'var(--paper-subtle)', padding: '6px', borderRadius: '2px' }}>Month 1 (2019-01)</div>
              <div style={{ backgroundColor: 'var(--paper-subtle)', padding: '6px', borderRadius: '2px' }}>Month 18 (2020-06)</div>
              <div style={{ backgroundColor: 'var(--paper-subtle)', padding: '6px', borderRadius: '2px', borderRight: '2px solid var(--flagged-red)' }}>
                Month 30 (2021-06) <span style={{ display: 'block', fontSize: '0.65rem', color: 'var(--flagged-red)', fontWeight: 700 }}>[SPLIT BOUNDARY]</span>
              </div>
              <div style={{ backgroundColor: 'rgba(138, 109, 59, 0.08)', padding: '6px', borderRadius: '2px' }}>
                Month 48+ (2022+) <span style={{ display: 'block', fontSize: '0.65rem', color: 'var(--brass)', fontWeight: 700 }}>[TEST HOLDOUT]</span>
              </div>

              <div className="mono-data" style={{ textAlign: 'left', fontWeight: 600 }}>F19Q10000268</div>
              <div className="mono-data" style={{ color: 'var(--reconciled-green)' }}>CURRENT ($210k)</div>
              <div className="mono-data" style={{ color: 'var(--reconciled-green)' }}>CURRENT ($202k)</div>
              <div className="mono-data" style={{ color: 'var(--reconciled-green)', borderRight: '2px solid var(--flagged-red)' }}>CURRENT ($196k)</div>
              <div className="mono-data" style={{ color: 'var(--reconciled-green)' }}>PREPAID ($0)</div>

              <div className="mono-data" style={{ textAlign: 'left', fontWeight: 600 }}>F19Q10010151</div>
              <div className="mono-data" style={{ color: 'var(--reconciled-green)' }}>CURRENT ($245k)</div>
              <div className="mono-data" style={{ color: 'var(--brass)' }}>30DPD ($240k)</div>
              <div className="mono-data" style={{ color: 'var(--flagged-red)', borderRight: '2px solid var(--flagged-red)' }}>60DPD ($238k)</div>
              <div className="mono-data" style={{ color: 'var(--flagged-red)' }}>DEFAULT ($232k)</div>

              <div className="mono-data" style={{ textAlign: 'left', fontWeight: 600 }}>F19Q20248240</div>
              <div className="mono-data" style={{ color: 'var(--reconciled-green)' }}>CURRENT ($50k)</div>
              <div className="mono-data" style={{ color: 'var(--reconciled-green)' }}>CURRENT ($48k)</div>
              <div className="mono-data" style={{ color: 'var(--reconciled-green)', borderRight: '2px solid var(--flagged-red)' }}>CURRENT ($46k)</div>
              <div className="mono-data" style={{ color: 'var(--brass)' }}>DOC_GAP ($40k)</div>
            </div>

            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginTop: 'var(--space-3)' }}>
              &bull; Strict calendar-time split cut: 407,733 records (&le; 2021-06) form the Training and Calibration sets; 304,374 forward records (&gt; 2021-06) form the out-of-sample Test Holdout.
            </p>
          </div>
        </section>

        {/* Section 2: Messy Data Realities */}
        <section id="data-realities" style={{ marginBottom: 'var(--space-8)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-3)' }}>
            2. Realities of Messy Secondary Market Loan Tapes
          </h2>
          <p style={{ marginBottom: 'var(--space-3)' }}>
            In production credit workflows, secondary market tapes suffer from multi-originator inconsistencies:
          </p>
          <ul style={{ paddingLeft: 'var(--space-5)', marginBottom: 'var(--space-4)', lineHeight: 'var(--leading-loose)' }}>
            <li><strong>Cross-Source Servicer Conflicts</strong>: Primary loan tapes frequently diverge from secondary servicer portals in reported balance and payment status (VR-007).</li>
            <li><strong>Feed Latency & Staleness</strong>: Servicer updates can lag the reporting period by 30 to 90 days, creating stale state indicators (VR-008).</li>
            <li><strong>Terminal Accounting Invariants</strong>: Records marked as prepaid or liquidated occasionally maintain non-zero balances due to feed truncation bugs (VR-005).</li>
            <li><strong>Trailing Document Gaps</strong>: Post-closing missing notes or unverified appraisals create compliance exceptions without indicating direct borrower credit distress (VR-006).</li>
          </ul>
        </section>

        {/* Section 3: The 8 Core Tasks */}
        <section id="core-tasks">
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-4)' }}>
            3. The 8 Required Challenge Tasks
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
            {tasks.map((t, idx) => (
              <div key={idx} className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                <h3 style={{ fontSize: 'var(--text-base)', color: 'var(--ledger-ink)', marginBottom: 'var(--space-2)' }}>
                  {t.title}
                </h3>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', lineHeight: 'var(--leading-snug)' }}>
                  {t.desc}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
