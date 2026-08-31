import React, { useState, useEffect } from 'react';
import StampBadge from './StampBadge';
import heroRecord from '../content/hero_record.json';

export default function HeroRecordAnimation() {
  const [stage, setStage] = useState(0); // 0: Raw Data, 1: Scoring, 2: Reconciled Stamp

  useEffect(() => {
    const timer1 = setTimeout(() => setStage(1), 700);
    const timer2 = setTimeout(() => setStage(2), 1400);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, []);

  return (
    <div style={{
      margin: 'var(--space-8) 0',
      padding: 'var(--space-6)',
      backgroundColor: 'var(--paper-card)',
      border: '2px solid var(--ledger-ink)',
      borderRadius: 'var(--border-radius-sm)',
      position: 'relative'
    }}>
      {/* Top Ledger Header Strip */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        borderBottom: '1px solid var(--brass)',
        paddingBottom: 'var(--space-2)',
        marginBottom: 'var(--space-4)'
      }}>
        <div>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--brass)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Live Ledger Ingestion Record
          </span>
          <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: 'var(--text-xl)', marginTop: '2px' }}>
            Loan Tape Entry: <span className="mono-data">`{heroRecord.loan_id}`</span>
          </h2>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>
            Reporting Period: {heroRecord.reporting_month}
          </span>
        </div>
      </div>

      {/* Ledger Data Columns */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
        gap: 'var(--space-4)',
        fontSize: 'var(--text-sm)'
      }}>
        {/* Raw Field Column 1 */}
        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Current Balance</span>
          <span className="mono-data" style={{ fontWeight: 700, fontSize: 'var(--text-md)' }}>
            ${heroRecord.current_balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--ink-muted)', display: 'block' }}>
            (${heroRecord.original_balance.toLocaleString('en-US')} Orig)
          </span>
        </div>

        {/* Raw Field Column 2 */}
        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Borrower FICO / LTV</span>
          <span style={{ fontWeight: 600 }}>{heroRecord.credit_score_band.split(' ')[0]}</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--ink-muted)', display: 'block' }}>
            LTV: {heroRecord.ltv_band}
          </span>
        </div>

        {/* Raw Field Column 3 */}
        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Servicer Entity</span>
          <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, display: 'block' }}>
            {heroRecord.servicer_name.split(' ')[0]}
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--ink-muted)' }}>
            Status: {heroRecord.current_status} ({heroRecord.days_past_due} DPD)
          </span>
        </div>

        {/* Multi-Outcome Prediction (Evaluated in Stage 1+) */}
        <div style={{
          transition: 'opacity 0.4s ease',
          opacity: stage >= 1 ? 1 : 0.2
        }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)', display: 'block', fontWeight: 600 }}>
            12M Default / Prepay
          </span>
          <span className="mono-data" style={{ fontWeight: 700 }}>
            {(heroRecord.p_default_12m * 100).toFixed(2)}% <span style={{ color: 'var(--ink-dim)', fontWeight: 400 }}>/</span> {(heroRecord.p_prepay_12m * 100).toFixed(1)}%
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--ink-muted)', display: 'block' }}>
            3M Delinq: {(heroRecord.p_delinquency_3m * 100).toFixed(1)}%
          </span>
        </div>

        {/* Anomaly Arbitration & Action Stamp (Evaluated in Stage 2) */}
        <div style={{
          transition: 'opacity 0.4s ease, transform 0.4s ease',
          opacity: stage >= 2 ? 1 : 0.2,
          transform: stage >= 2 ? 'scale(1)' : 'scale(0.95)'
        }}>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>
            Anomaly Score: <strong className="mono-data" style={{ color: 'var(--ledger-ink)' }}>{heroRecord.anomaly_score.toFixed(4)}</strong>
          </span>
          <div style={{ marginTop: '4px' }}>
            <StampBadge action={heroRecord.action} />
          </div>
        </div>
      </div>

      {/* Attribution Footnote */}
      <div style={{
        marginTop: 'var(--space-4)',
        paddingTop: 'var(--space-3)',
        borderTop: '1px dashed var(--faint-rule)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        fontSize: 'var(--text-xs)',
        color: 'var(--ink-muted)'
      }}>
        <span>
          Root TreeSHAP Drivers: <strong className="mono-data" style={{ color: 'var(--ledger-ink)' }}>{heroRecord.top_drivers.join(', ')}</strong>
        </span>
        <span style={{ color: 'var(--reconciled-green)', fontWeight: 600 }}>
          &check; All 8 Deterministic Invariant Rules Verified (VR-001..VR-008)
        </span>
      </div>
    </div>
  );
}
