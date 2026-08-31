import React from 'react';
import MarginColumn from '../components/MarginColumn';
import LedgerTable from '../components/LedgerTable';
import StampBadge from '../components/StampBadge';
import scenData from '../content/scenario_stress.json';

export default function ScenarioStress() {
  const { scenarios, segment_stress_heatmap } = scenData;

  const segmentColumns = [
    { header: 'Borrower / Collateral Segment', key: 'segment', render: (val) => <strong>{val}</strong> },
    { header: 'Base 36M Loss Rate', key: 'base_loss', numeric: true, render: (val) => <span className="mono-data">{val}</span> },
    { header: 'Adverse 36M Loss Rate', key: 'adverse_loss', numeric: true, render: (val) => <strong className="mono-data" style={{ color: 'var(--flagged-red)' }}>{val}</strong> },
    { header: 'CPR Multiplier (Base -> High Prepayment)', key: 'prepay_speed', numeric: true, render: (val) => <span className="mono-data">{val}</span> },
    {
      header: 'Vulnerability Rating',
      key: 'vulnerability',
      render: (val) => <StampBadge action={val === 'HIGH' ? 'FLAGGED' : val === 'MEDIUM' ? 'WARNING' : 'AUTO_APPROVE'} size="small" />
    }
  ];

  return (
    <div className="page-grid">
      <MarginColumn
        sectionNumber="04"
        sectionTitle="Scenario & Stress"
        contextInfo="Macro Shocks, Cash Flow Impacts & Segment Heatmaps"
        subLinks={[
          { id: 'macro-scenarios', label: 'Macro Scenarios' },
          { id: 'compounding-math', label: 'Compounding Mechanics' },
          { id: 'segment-heatmap', label: 'Segment Vulnerability' }
        ]}
      />

      <div className="content-column">
        <header className="page-header">
          <h1>Macroeconomic Scenario & Stress Simulation Engine</h1>
          <p className="page-lead">
            Simulating portfolio cash flows, default escalations, and refinance waves under Federal Reserve rate shocks, unemployment surges, and home price appreciation (HPA) volatility.
          </p>
        </header>

        {/* Section 1: The 3 Macro Scenarios */}
        <section id="macro-scenarios" style={{ marginBottom: 'var(--space-8)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            1. Core Macroeconomic Stress Cases
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-4)' }}>
            Calibrated shock parameters applied to interest rate spreads and Markov roll-rate transition matrices.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-6)' }}>
            {scenarios.map((scen) => (
              <div
                key={scen.id}
                className="ledger-card"
                style={{
                  margin: 0,
                  borderLeft: `3px solid ${scen.id === 'adverse_credit' ? 'var(--flagged-red)' : scen.id === 'high_prepayment' ? 'var(--brass)' : 'var(--reconciled-green)'}`
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 'var(--space-2)' }}>
                  <h3 style={{ fontSize: 'var(--text-md)', color: 'var(--ledger-ink)' }}>{scen.name}</h3>
                  <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)', fontWeight: 700 }}>
                    {scen.rate_shock}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)', fontSize: 'var(--text-xs)', margin: 'var(--space-3) 0', padding: 'var(--space-3)', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px' }}>
                  <div>
                    <span style={{ color: 'var(--ink-dim)', display: 'block' }}>HPA Shock:</span>
                    <strong className="mono-data">{scen.hpa_shock}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--ink-dim)', display: 'block' }}>Unemployment:</span>
                    <strong className="mono-data">{scen.unemployment_shock}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--ink-dim)', display: 'block' }}>Default Hazard:</span>
                    <strong className="mono-data" style={{ color: scen.id === 'adverse_credit' ? 'var(--flagged-red)' : 'var(--ledger-ink)' }}>{scen.default_multiplier}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--ink-dim)', display: 'block' }}>Prepay Hazard:</span>
                    <strong className="mono-data" style={{ color: scen.id === 'high_prepayment' ? 'var(--brass)' : 'var(--ledger-ink)' }}>{scen.prepay_multiplier}</strong>
                  </div>
                </div>

                <div style={{ fontSize: 'var(--text-xs)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)', borderTop: '1px dashed var(--faint-rule)', paddingTop: 'var(--space-2)', marginBottom: 'var(--space-3)' }}>
                  <div>
                    <span style={{ color: 'var(--ink-dim)', display: 'block' }}>12M Default / Prepay:</span>
                    <span className="mono-data"><strong>{scen.default_12m}</strong> / <strong>{scen.prepay_12m}</strong></span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--ink-dim)', display: 'block' }}>36M Cum. Def / Prepay:</span>
                    <span className="mono-data"><strong>{scen.cumulative_default_36m}</strong> / <strong>{scen.cumulative_prepay_36m}</strong></span>
                  </div>
                </div>

                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', lineHeight: 'var(--leading-snug)' }}>
                  {scen.driver_summary}
                </p>
              </div>
            ))}
          </div>

          <div id="compounding-math" className="ledger-card" style={{ marginTop: 'var(--space-4)', backgroundColor: 'var(--paper-subtle)', borderLeft: '3px solid var(--brass)' }}>
            <h4 style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--brass)', letterSpacing: '0.05em', marginBottom: '4px' }}>
              Competing Hazard Compounding Formulation
            </h4>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', lineHeight: 1.6, margin: 0 }}>
              In multi-horizon survival forecasting, cumulative prepayment probability over $T=36$ months follows $P(\text{Prepay} \le 36M) = 1 - \prod_{t=1}^{36}(1 - \text{SMM}_t)$. The $2.75\times$ prepayment hazard in the High Prepayment scenario compounds monthly single-month mortality ($\text{SMM}$), causing prepayment to surge non-linearly to <strong>77.38% at 12M</strong> and asymptote to <strong>94.09% at 36M</strong> as the active performing balance pool is rapidly exhausted.
            </p>
          </div>
        </section>

        {/* Section 2: Segment Vulnerability Heatmap */}
        <section id="segment-heatmap">
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            2. Segment Stress Sensitivity & Vulnerability Table
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-3)' }}>
            Granular stress sensitivity showing loss-rate escalations across high-leverage and subprime borrower cohorts.
          </p>
          <LedgerTable columns={segmentColumns} data={segment_stress_heatmap} keyField="segment" caption="36-Month Cumulative Loss Rates and CPR Velocities Across Key Collateral Tiers" />
        </section>
      </div>
    </div>
  );
}
