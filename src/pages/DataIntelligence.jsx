import React from 'react';
import MarginColumn from '../components/MarginColumn';
import LedgerTable from '../components/LedgerTable';
import StampBadge from '../components/StampBadge';
import diData from '../content/data_intelligence.json';

export default function DataIntelligence() {
  const { headline_metrics, missingness_profiles, drift_summary, rule_breaches, dq_distribution } = diData;

  const ruleColumns = [
    { header: 'Rule ID', key: 'rule_id', width: '90px', render: (val) => <strong className="mono-data" style={{ color: 'var(--brass)' }}>{val}</strong> },
    { header: 'Name', key: 'name', width: '220px' },
    {
      header: 'Severity',
      key: 'severity',
      width: '110px',
      render: (val) => <StampBadge action={val === 'CRITICAL' ? 'FLAGGED' : val === 'HIGH' ? 'HIGH' : 'MEDIUM'} size="small" />
    },
    { header: 'Train Hits', key: 'train_hits', numeric: true, width: '100px', render: (val) => val.toLocaleString('en-US') },
    { header: 'Test Hits', key: 'test_hits', numeric: true, width: '100px', render: (val) => val.toLocaleString('en-US') },
    { header: 'Contractual / Invariant Logic', key: 'description' }
  ];

  const driftColumns = [
    { header: 'Feature', key: 'feature', render: (val) => <strong className="mono-data">{val}</strong> },
    { header: 'PSI Score', key: 'psi', numeric: true, render: (val) => val.toFixed(3) },
    { header: 'KS p-value', key: 'ks_pvalue', numeric: true, render: (val) => val.toFixed(3) },
    {
      header: 'Stability Status',
      key: 'status',
      render: (val) => (
        <span className="mono-data" style={{ color: val === 'STABLE' ? 'var(--reconciled-green)' : 'var(--brass)', fontWeight: 600 }}>
          {val}
        </span>
      )
    },
    { header: 'Analytical Finding', key: 'note' }
  ];

  return (
    <div className="page-grid">
      <MarginColumn
        sectionNumber="02"
        sectionTitle="Data Intelligence"
        contextInfo="Distributional Diagnostics, Drift & Data Quality"
        subLinks={[
          { id: 'headline-dq', label: 'Data Quality Summary' },
          { id: 'rule-evaluator', label: 'Deterministic Rules (VR-001..008)' },
          { id: 'temporal-drift', label: 'Train vs Test Drift' },
          { id: 'missingness-profiles', label: 'Missingness Strategy' }
        ]}
      />

      <div className="content-column">
        <header className="page-header">
          <h1>Data Intelligence & Profiling Layer</h1>
          <p className="page-lead">
            Comprehensive profiling across 712,107 panel records identifying missingness mechanisms, contractual rule violations, temporal feature drift, and record-level data quality scores.
          </p>
        </header>

        {/* Section 1: Headline DQ Metric & Distribution */}
        <section id="headline-dq" style={{ marginBottom: 'var(--space-8)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-6)' }}>
            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)', borderLeft: '3px solid var(--reconciled-green)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Batch Data Quality Score</span>
              <span className="mono-data" style={{ fontSize: 'var(--text-3xl)', fontWeight: 800, color: 'var(--reconciled-green)' }}>
                {headline_metrics.batch_dq_score}%
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-muted)' }}>Weighted portfolio health score</span>
            </div>

            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Total Panel Records</span>
              <span className="mono-data" style={{ fontSize: 'var(--text-2xl)', fontWeight: 700 }}>
                {headline_metrics.total_records.toLocaleString('en-US')}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-muted)' }}>407,733 Train &bull; 304,374 Test</span>
            </div>

            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Unique Loan Portfolios</span>
              <span className="mono-data" style={{ fontSize: 'var(--text-2xl)', fontWeight: 700 }}>
                {headline_metrics.unique_loans.toLocaleString('en-US')}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-muted)' }}>Freddie Mac 2019 benchmark</span>
            </div>

            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)', borderLeft: '3px solid var(--flagged-red)' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Defective Records Flagged</span>
              <span className="mono-data" style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: 'var(--flagged-red)' }}>
                {headline_metrics.total_rule_breaches.toLocaleString('en-US')}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-muted)' }}>31,813 unique records &bull; 51,207 total rule hits</span>
            </div>
          </div>

          {/* Record-Level DQ Score Distribution */}
          <div className="ledger-card">
            <h3 style={{ fontSize: 'var(--text-md)', marginBottom: 'var(--space-3)' }}>
              Record-Level Data Quality Score Distribution &mdash; Holdout Test Cohort (304,374 Records)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              {dq_distribution.map((bucket, idx) => (
                <div key={idx} style={{ fontSize: 'var(--text-xs)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                    <span style={{ fontWeight: 600 }}>{bucket.score_bucket}</span>
                    <span className="mono-data">{bucket.percentage}% ({bucket.count.toLocaleString('en-US')} rows)</span>
                  </div>
                  <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${bucket.percentage}%`,
                        height: '100%',
                        backgroundColor: idx === 0 ? 'var(--reconciled-green)' : idx === 1 ? 'var(--brass)' : 'var(--flagged-red)'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 2: Deterministic Rule Evaluator Table */}
        <section id="rule-evaluator" style={{ marginBottom: 'var(--space-8)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            Deterministic Business Rules (VR-001 through VR-008)
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-3)' }}>
            Eight contractual and accounting checks evaluated instantaneously across every panel row.
          </p>
          <LedgerTable columns={ruleColumns} data={rule_breaches} keyField="rule_id" caption="Validation Rule Breaches Across Training and Holdout Test Sets" />
          <div style={{ marginTop: 'var(--space-2)', fontSize: '0.75rem', color: 'var(--ink-muted)', fontStyle: 'italic', lineHeight: 1.5 }}>
            * Note on Rule Reconciliation: The 8 rows above sum to 51,207 individual breach instances (31,813 in Train, 19,394 in Test) across invariant checks due to multi-rule co-occurrence on individual defective records (e.g., VR-004 remaining term anomaly paired with VR-006 trailing document gap). A total of 31,813 unique individual records in the dataset trigger &ge; 1 breach.
          </div>
        </section>

        {/* Section 3: Temporal Train vs Test Drift */}
        <section id="temporal-drift" style={{ marginBottom: 'var(--space-8)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            Temporal Train vs. Test Drift Analysis
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-3)' }}>
            Population Stability Index (PSI) and Kolmogorov-Smirnov test statistics audited across the 2021-06 split threshold.
          </p>
          <LedgerTable columns={driftColumns} data={drift_summary} keyField="feature" caption="Chronological Drift Audits across Key Tabular Covariates" />
        </section>

        {/* Section 4: Missingness Profiles */}
        <section id="missingness-profiles">
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            Missing-Value Patterns & Sentinel Handling
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-3)' }}>
            Distinguishing Missing Completely At Random (MCAR) from Missing At Random (MAR) and structural reconciliation gaps.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 'var(--space-4)' }}>
            {missingness_profiles.map((m, idx) => (
              <div key={idx} className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 'var(--space-2)' }}>
                  <strong className="mono-data" style={{ color: 'var(--ledger-ink)' }}>{m.feature}</strong>
                  <span className="mono-data" style={{ color: 'var(--brass)', fontWeight: 700, fontSize: 'var(--text-xs)' }}>{m.missing_pct}%</span>
                </div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-2)' }}>
                  Mechanism: <strong className="mono-data" style={{ color: 'var(--ledger-ink)' }}>{m.type}</strong>
                </div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', borderTop: '1px dotted var(--faint-rule)', paddingTop: '4px' }}>
                  Handling: {m.strategy}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
