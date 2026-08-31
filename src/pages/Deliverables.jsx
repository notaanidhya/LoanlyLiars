import React, { useState } from 'react';
import MarginColumn from '../components/MarginColumn';
import LedgerTable from '../components/LedgerTable';
import StampBadge from '../components/StampBadge';
import delivData from '../content/deliverables.json';

export default function Deliverables() {
  const { submission_summary, preview_rows, github_url, model_card_markdown, dev_log_markdown } = delivData;
  const [activeDoc, setActiveDoc] = useState('MODEL_CARD'); // MODEL_CARD or DEV_LOG

  const subColumns = [
    { header: 'Loan ID', key: 'loan_id', render: (val) => <strong className="mono-data">`{val}`</strong> },
    { header: 'Month', key: 'month_index', numeric: true, render: (val) => <span className="mono-data">{val}</span> },
    { header: 'P(3M Delinq)', key: 'next_3m_delinquency_prob', numeric: true, render: (val) => <span className="mono-data">{(val * 100).toFixed(1)}%</span> },
    { header: 'P(12M Def)', key: 'next_12m_default_prob', numeric: true, render: (val) => <span className="mono-data">{(val * 100).toFixed(1)}%</span> },
    { header: 'P(12M Prep)', key: 'next_12m_prepayment_prob', numeric: true, render: (val) => <span className="mono-data">{(val * 100).toFixed(1)}%</span> },
    { header: 'Next State', key: 'next_state', render: (val) => <span className="mono-data">{val}</span> },
    { header: 'Anomaly Score', key: 'anomaly_score', numeric: true, render: (val) => <strong className="mono-data">{val.toFixed(4)}</strong> },
    { header: 'Action Stamp', key: 'action', render: (val) => <StampBadge action={val} size="small" /> },
    { header: 'Primary SHAP Driver', key: 'top_driver_1', render: (val) => <span className="mono-data" style={{ fontSize: '0.7rem' }}>{val}</span> }
  ];

  return (
    <div className="page-grid">
      <MarginColumn
        sectionNumber="07"
        sectionTitle="Deliverables"
        contextInfo="Competition Submission, Formal Model Card & Dev Logs"
        subLinks={[
          { id: 'submission-preview', label: 'submission.csv Preview' },
          { id: 'model-card', label: 'Model Card & Dev Logs' },
          { id: 'repository-links', label: 'Repository & Code' }
        ]}
      />

      <div className="content-column">
        <header className="page-header">
          <h1>Competition Deliverables & Governance Catalog</h1>
          <p className="page-lead">
            Official Intain Campus Challenge 2026 deliverables: verified 304,374-row competition submission file, formal Model Card, and development audit trails.
          </p>
        </header>

        {/* Section 1: submission.csv Preview & Download */}
        <section id="submission-preview" style={{ marginBottom: 'var(--space-10)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 'var(--space-2)' }}>
            <div>
              <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: '2px' }}>
                1. Final Competition Submission File (`submission.csv`)
              </h2>
              <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--reconciled-green)', fontWeight: 700 }}>
                &check; 304,374 Rows &bull; 15 Schema Columns &bull; 0 Nulls &bull; 100% Tolerance Matched
              </span>
            </div>

            <a
              href={`${github_url}/blob/main/submission.csv`}
              target="_blank"
              rel="noreferrer"
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-xs)',
                fontWeight: 700,
                padding: '6px 14px',
                backgroundColor: 'var(--brass)',
                color: 'var(--ledger-paper)',
                border: 'none',
                borderRadius: '2px',
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              View submission.csv (GitHub) &rarr;
            </a>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 'var(--space-3)', margin: 'var(--space-4) 0' }}>
            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-3)' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-dim)', display: 'block' }}>AUTO_APPROVE</span>
              <strong className="mono-data" style={{ color: 'var(--reconciled-green)' }}>{(submission_summary.action_counts?.AUTO_APPROVE || 284641).toLocaleString('en-US')}</strong> ({((submission_summary.action_counts?.AUTO_APPROVE || 284641) / 304374 * 100).toFixed(1)}%)
            </div>
            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-3)' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-dim)', display: 'block' }}>REQUEST_CURE</span>
              <strong className="mono-data" style={{ color: 'var(--brass)' }}>{(submission_summary.action_counts?.REQUEST_CURE || 9772).toLocaleString('en-US')}</strong> ({((submission_summary.action_counts?.REQUEST_CURE || 9772) / 304374 * 100).toFixed(1)}%)
            </div>
            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-3)' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-dim)', display: 'block' }}>OVERRIDE_SERVICER</span>
              <strong className="mono-data" style={{ color: 'var(--flagged-red)' }}>{(submission_summary.action_counts?.OVERRIDE_SERVICER || 3164).toLocaleString('en-US')}</strong> ({((submission_summary.action_counts?.OVERRIDE_SERVICER || 3164) / 304374 * 100).toFixed(1)}%)
            </div>
            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-3)' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-dim)', display: 'block' }}>MANUAL_AUDIT</span>
              <strong className="mono-data" style={{ color: 'var(--flagged-red)' }}>{(submission_summary.action_counts?.MANUAL_AUDIT || 2871).toLocaleString('en-US')}</strong> ({((submission_summary.action_counts?.MANUAL_AUDIT || 2871) / 304374 * 100).toFixed(1)}%)
            </div>
            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-3)' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-dim)', display: 'block' }}>ESCALATE_DOC_REVIEW</span>
              <strong className="mono-data" style={{ color: 'var(--flagged-red)' }}>{(submission_summary.action_counts?.ESCALATE_DOC_REVIEW || 2264).toLocaleString('en-US')}</strong> ({((submission_summary.action_counts?.ESCALATE_DOC_REVIEW || 2264) / 304374 * 100).toFixed(1)}%)
            </div>
            <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-3)' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-dim)', display: 'block' }}>ACCEPT_PRIMARY</span>
              <strong className="mono-data" style={{ color: 'var(--brass)' }}>{(submission_summary.action_counts?.ACCEPT_PRIMARY || 1662).toLocaleString('en-US')}</strong> ({((submission_summary.action_counts?.ACCEPT_PRIMARY || 1662) / 304374 * 100).toFixed(1)}%)
            </div>
          </div>

          <LedgerTable columns={subColumns} data={preview_rows} keyField="loan_id" caption="Live 10-Row Sample Preview from 304,374 Scored Holdout Records" />
        </section>

        {/* Section 2: Rendered Model Card & Dev Log Viewer */}
        <section id="model-card" style={{ marginBottom: 'var(--space-10)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: '1px solid var(--brass)', paddingBottom: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
            <h2 style={{ fontSize: 'var(--text-xl)' }}>
              2. Formal Model Governance & Development Logs
            </h2>
            <div style={{ display: 'flex', gap: '6px' }}>
              <button
                type="button"
                onClick={() => setActiveDoc('MODEL_CARD')}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  padding: '4px 10px',
                  border: '1px solid',
                  borderColor: activeDoc === 'MODEL_CARD' ? 'var(--brass)' : 'var(--faint-rule)',
                  backgroundColor: activeDoc === 'MODEL_CARD' ? 'var(--brass)' : 'var(--paper-card)',
                  color: activeDoc === 'MODEL_CARD' ? 'var(--ledger-paper)' : 'var(--ledger-ink)',
                  cursor: 'pointer',
                  borderRadius: '2px'
                }}
              >
                Model Card (Task 8)
              </button>
              <button
                type="button"
                onClick={() => setActiveDoc('DEV_LOG')}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  padding: '4px 10px',
                  border: '1px solid',
                  borderColor: activeDoc === 'DEV_LOG' ? 'var(--brass)' : 'var(--faint-rule)',
                  backgroundColor: activeDoc === 'DEV_LOG' ? 'var(--brass)' : 'var(--paper-card)',
                  color: activeDoc === 'DEV_LOG' ? 'var(--ledger-paper)' : 'var(--ledger-ink)',
                  cursor: 'pointer',
                  borderRadius: '2px'
                }}
              >
                AI Development Log
              </button>
            </div>
          </div>

          <div className="ledger-card" style={{ maxHeight: '520px', overflowY: 'auto', padding: 'var(--space-6)', backgroundColor: 'var(--paper-card)', border: '1px solid var(--faint-rule)' }}>
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', lineHeight: '1.5', color: 'var(--ledger-ink)' }}>
              {activeDoc === 'MODEL_CARD' ? model_card_markdown : dev_log_markdown}
            </pre>
          </div>
        </section>

        {/* Section 3: Repository & Verification Links */}
        <section id="repository-links">
          <div className="ledger-callout" style={{ borderLeftColor: 'var(--reconciled-green)', backgroundColor: 'var(--paper-card)' }}>
            <h2 style={{ fontSize: 'var(--text-md)', color: 'var(--ledger-ink)', marginBottom: 'var(--space-2)' }}>
              3. Repository & Live Execution Commands
            </h2>
            <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-3)' }}>
              Clone the verified competition repository and execute all 8 challenge tasks with sub-2s inference:
            </p>
            <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--ledger-ink)', color: 'var(--ledger-paper)', borderRadius: '2px', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', marginBottom: 'var(--space-3)' }}>
              <code>git clone https://github.com/notaanidhya/LoanlyLiars.git<br/>cd LoanlyLiars<br/>py -3.13 demo.py</code>
            </div>
            <a
              href={github_url}
              target="_blank"
              rel="noreferrer"
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-xs)',
                color: 'var(--brass)',
                fontWeight: 700,
                textDecoration: 'none'
              }}
            >
              &rarr; View GitHub Repository (notaanidhya/LoanlyLiars)
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}
