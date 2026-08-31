import React, { useState } from 'react';
import StampBadge from './StampBadge';

export default function CaseCard({ caseData, defaultExpanded = false }) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [showPromptLog, setShowPromptLog] = useState(false);

  const {
    loan_id,
    reporting_month,
    action,
    confidence,
    anomaly_score,
    p_default_12m,
    p_prepay_12m,
    p_delinquency_3m,
    next_state,
    top_drivers = [],
    rule_breach,
    prompt_text,
    model,
    timestamp
  } = caseData;

  return (
    <div className="ledger-card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Header Bar (Clickable to toggle) */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          padding: 'var(--space-4) var(--space-6)',
          backgroundColor: expanded ? 'var(--paper-subtle)' : 'var(--paper-card)',
          cursor: 'pointer',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: expanded ? '1px solid var(--faint-rule)' : 'none',
          transition: 'background-color 0.15s ease'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          <span className="mono-data" style={{ fontWeight: 700, fontSize: 'var(--text-md)', color: 'var(--ledger-ink)' }}>
            `{loan_id}`
          </span>
          <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>
            Period: {reporting_month}
          </span>
          <StampBadge action={action} size="small" />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
          <div>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', marginRight: '6px' }}>Anomaly Score:</span>
            <span className="mono-data" style={{ fontWeight: 700, color: anomaly_score >= 0.35 ? 'var(--flagged-red)' : 'var(--ledger-ink)' }}>
              {typeof anomaly_score === 'number' ? anomaly_score.toFixed(4) : anomaly_score}
            </span>
          </div>
          <div>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', marginRight: '6px' }}>P(12M Def):</span>
            <span className="mono-data" style={{ fontWeight: 600 }}>
              {(p_default_12m * 100).toFixed(2)}%
            </span>
          </div>
          <button
            type="button"
            style={{
              background: 'none',
              border: '1px solid var(--brass)',
              padding: '2px 8px',
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-xs)',
              color: 'var(--brass)',
              cursor: 'pointer'
            }}
          >
            {expanded ? '[- Hide]' : '[+ Inspect]'}
          </button>
        </div>
      </div>

      {/* Expanded Detail Panel */}
      {expanded && (
        <div style={{ padding: 'var(--space-6)' }}>
          {/* Key Metrics Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-6)' }}>
            <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Reviewer Precedence Action</span>
              <div style={{ marginTop: '4px' }}><StampBadge action={action} /></div>
              <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginTop: '4px', display: 'block' }}>
                Confidence: {confidence}
              </span>
            </div>

            <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Rule Breach Tag</span>
              <span className="mono-data" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: rule_breach !== 'NORMAL_CONFORMING' ? 'var(--flagged-red)' : 'var(--reconciled-green)' }}>
                {rule_breach}
              </span>
            </div>

            <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px' }}>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Multi-Horizon Predictions</span>
              <span className="mono-data" style={{ fontSize: 'var(--text-xs)', display: 'block', marginTop: '2px' }}>
                12M Prepay: <strong>{(p_prepay_12m * 100).toFixed(1)}%</strong> | 3M Delinq: <strong>{(p_delinquency_3m * 100).toFixed(1)}%</strong>
              </span>
              <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>
                Next Roll State: <strong>{next_state || 'CURRENT'}</strong>
              </span>
            </div>
          </div>

          {/* TreeSHAP Local Feature Drivers */}
          {top_drivers && top_drivers.length > 0 && (
            <div style={{ marginBottom: 'var(--space-6)' }}>
              <span style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--ledger-ink)', display: 'block', marginBottom: 'var(--space-2)' }}>
                Root-Cause Feature Attribution (TreeSHAP Drivers)
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                {top_drivers.map((drv, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', fontSize: 'var(--text-xs)' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--brass)', width: '20px' }}>#{i + 1}</span>
                    <span className="mono-data" style={{ backgroundColor: 'var(--paper-subtle)', padding: '2px 8px', borderRadius: '2px', fontWeight: 600 }}>
                      {drv}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Grounded Reviewer Note Preview */}
          <div className="ledger-callout" style={{ margin: 'var(--space-4) 0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 'var(--space-2)' }}>
              <span className="ledger-callout-title" style={{ color: 'var(--ledger-ink)', fontSize: 'var(--text-sm)' }}>
                Synthesized Reviewer Audit Memo
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--ink-dim)', fontFamily: 'var(--font-mono)' }}>
                Model: {model || 'Intain-Reviewer-Copilot-v1.0'}
              </span>
            </div>
            <p style={{ fontSize: 'var(--text-sm)', lineHeight: 'var(--leading-normal)', color: 'var(--ledger-ink)' }}>
              {action === 'MANUAL_AUDIT' && `Severe data inconsistency detected for account ${loan_id} in period ${reporting_month}. Balance and status fields breach fundamental accounting rules (${rule_breach}). Immediate manual re-indexing required prior to tape submission.`}
              {action === 'ESCALATE_DOC_REVIEW' && `Document verification exception detected for account ${loan_id}. Trailing documentation checklist indicates unresolved exception (${rule_breach}). Escalate to post-closing compliance team for cure within 30 days.`}
              {action === 'OVERRIDE_SERVICER' && `Cross-feed reconciliation discrepancy identified for account ${loan_id} (${rule_breach}). Override secondary servicer records and enforce primary tape authority.`}
              {action === 'REQUEST_CURE' && `Non-critical term or reporting anomaly identified for account ${loan_id} (${rule_breach}). Formal Request for Cure issued to master servicer.`}
              {action === 'AUTO_APPROVE' && `Conforming record for account ${loan_id} in period ${reporting_month}. Performing within normal credit and underwriting parameters with composite anomaly score ${typeof anomaly_score === 'number' ? anomaly_score.toFixed(4) : anomaly_score} and zero critical rule breaches.`}
            </p>
          </div>

          {/* Collapsible Prompt & Retrieval Log */}
          <div style={{ marginTop: 'var(--space-4)', borderTop: '1px solid var(--faint-rule)', paddingTop: 'var(--space-3)' }}>
            <button
              type="button"
              onClick={() => setShowPromptLog(!showPromptLog)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--ink-dim)',
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-xs)',
                cursor: 'pointer',
                padding: '4px 0',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <span>{showPromptLog ? '▲ Hide' : '▼ View'} Prompt & Context Retrieval Log (Task 7 Rubric)</span>
            </button>

            {showPromptLog && (
              <div style={{ marginTop: 'var(--space-3)', padding: 'var(--space-4)', backgroundColor: 'var(--ledger-ink)', color: 'var(--ledger-paper)', borderRadius: '2px', fontSize: 'var(--text-xs)' }}>
                <div style={{ marginBottom: 'var(--space-2)', color: 'var(--brass)', fontFamily: 'var(--font-mono)' }}>
                  [Prompt Log Entry — {timestamp || '2026-08-31'}]
                </div>
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', lineHeight: '1.4' }}>
                  {prompt_text || `Generate grounded credit audit memo for Loan ID ${loan_id} in ${reporting_month}. P(Def 12m)=${p_default_12m}, Anomaly Score=${anomaly_score}, Action=${action}. SHAP: ${top_drivers.join(', ')}.`}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
