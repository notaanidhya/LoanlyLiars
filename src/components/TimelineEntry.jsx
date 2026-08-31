import React from 'react';

export default function TimelineEntry({ index, incident }) {
  const { title, assumed, broke_it, found_it, fixed_it } = incident;

  return (
    <div style={{ marginBottom: 'var(--space-8)', display: 'grid', gridTemplateColumns: '48px 1fr', gap: 'var(--space-4)' }}>
      {/* Number Marker */}
      <div style={{
        fontFamily: 'var(--font-serif)',
        fontSize: 'var(--text-xl)',
        fontWeight: 800,
        color: 'var(--brass)',
        textAlign: 'right',
        lineHeight: 1
      }}>
        {String(index + 1).padStart(2, '0')}.
      </div>

      {/* Narrative Card */}
      <div className="ledger-card" style={{ margin: 0, padding: 'var(--space-5)' }}>
        <h3 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-3)', color: 'var(--ledger-ink)' }}>
          {title}
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-4)', fontSize: 'var(--text-sm)' }}>
          <div>
            <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--ink-dim)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '2px' }}>
              1. What We Assumed
            </span>
            <p style={{ color: 'var(--ledger-ink)', lineHeight: 'var(--leading-snug)' }}>{assumed}</p>
          </div>

          <div>
            <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--flagged-red)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '2px' }}>
              2. What Broke
            </span>
            <p style={{ color: 'var(--ledger-ink)', lineHeight: 'var(--leading-snug)' }}>{broke_it}</p>
          </div>

          <div>
            <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--brass)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '2px' }}>
              3. How We Found It
            </span>
            <p style={{ color: 'var(--ledger-ink)', lineHeight: 'var(--leading-snug)' }}>{found_it}</p>
          </div>

          <div>
            <span style={{ fontSize: 'var(--text-xs)', textTransform: 'uppercase', color: 'var(--reconciled-green)', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: '2px' }}>
              4. The Fix Implemented
            </span>
            <p style={{ color: 'var(--ledger-ink)', lineHeight: 'var(--leading-snug)', fontWeight: 600 }}>{fixed_it}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
