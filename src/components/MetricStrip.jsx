import React from 'react';

export default function MetricStrip({ modelInfo }) {
  const {
    target,
    is_multiclass,
    baseline_model,
    baseline_pr_auc,
    baseline_roc_auc,
    baseline_macro_f1,
    tuned_model,
    tuned_pr_auc,
    tuned_roc_auc,
    tuned_macro_f1,
    tuned_weighted_f1,
    classes,
    f1_score,
    optimal_threshold,
    brier_score,
    key_drivers
  } = modelInfo;

  if (is_multiclass) {
    const macroGain = (tuned_macro_f1 - baseline_macro_f1).toFixed(4);
    return (
      <div className="metric-strip">
        <div className="metric-strip-target">{target}</div>
        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-2)' }}>
          Tuned Algorithm: <strong style={{ color: 'var(--ledger-ink)' }}>{tuned_model}</strong>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)', margin: 'var(--space-3) 0' }}>
          <div>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Macro-F1 (Gain)</span>
            <span className="mono-data" style={{ fontSize: 'var(--text-md)', fontWeight: 700, color: 'var(--reconciled-green)' }}>
              {tuned_macro_f1.toFixed(4)}
              <small style={{ fontSize: '0.7em', color: 'var(--brass)', marginLeft: '4px' }}>
                ({macroGain >= 0 ? `+${macroGain}` : macroGain})
              </small>
            </span>
          </div>
          <div>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>Weighted-F1</span>
            <span className="mono-data" style={{ fontSize: 'var(--text-md)', fontWeight: 700, color: 'var(--ledger-ink)' }}>
              {tuned_weighted_f1.toFixed(4)}
            </span>
          </div>
        </div>

        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-2)' }}>
          Classes ({classes?.length || 5}): <strong className="mono-data" style={{ color: 'var(--ledger-ink)', fontSize: '0.75rem' }}>{classes?.join(', ')}</strong>
        </div>

        <div className="metric-strip-comparison">
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>Baseline ({baseline_model})</span>
          <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)' }}>
            Macro-F1: {baseline_macro_f1.toFixed(4)}
          </span>
        </div>

        {key_drivers && key_drivers.length > 0 && (
          <div style={{ marginTop: 'var(--space-3)', paddingTop: 'var(--space-2)', borderTop: '1px dotted var(--faint-rule)' }}>
            <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--brass)', letterSpacing: '0.05em', display: 'block', marginBottom: '2px' }}>
              Top Feature Attribution Drivers
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {key_drivers.map((d, i) => (
                <span key={i} className="mono-data" style={{ fontSize: '0.7rem', backgroundColor: 'var(--paper-subtle)', padding: '1px 5px', borderRadius: '2px', color: 'var(--ledger-ink)' }}>
                  {d}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  const prGain = (tuned_pr_auc - baseline_pr_auc).toFixed(4);

  return (
    <div className="metric-strip">
      <div className="metric-strip-target">{target}</div>
      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-2)' }}>
        Tuned Algorithm: <strong style={{ color: 'var(--ledger-ink)' }}>{tuned_model}</strong>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)', margin: 'var(--space-3) 0' }}>
        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>PR-AUC (Gain)</span>
          <span className="mono-data" style={{ fontSize: 'var(--text-md)', fontWeight: 700, color: 'var(--reconciled-green)' }}>
            {tuned_pr_auc.toFixed(4)}
            <small style={{ fontSize: '0.7em', color: 'var(--brass)', marginLeft: '4px' }}>(+{prGain})</small>
          </span>
        </div>
        <div>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)', display: 'block' }}>ROC-AUC</span>
          <span className="mono-data" style={{ fontSize: 'var(--text-md)', fontWeight: 700, color: 'var(--ledger-ink)' }}>
            {tuned_roc_auc.toFixed(4)}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-2)' }}>
        <span>Optimal F1: <strong className="mono-data" style={{ color: 'var(--ledger-ink)' }}>{f1_score.toFixed(4)}</strong> (@{optimal_threshold})</span>
        <span>Brier: <strong className="mono-data" style={{ color: 'var(--ledger-ink)' }}>{brier_score.toFixed(4)}</strong></span>
      </div>

      <div className="metric-strip-comparison">
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-dim)' }}>Baseline ({baseline_model})</span>
        <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)' }}>
          PR-AUC: {baseline_pr_auc.toFixed(4)}
        </span>
      </div>

      {key_drivers && key_drivers.length > 0 && (
        <div style={{ marginTop: 'var(--space-3)', paddingTop: 'var(--space-2)', borderTop: '1px dotted var(--faint-rule)' }}>
          <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: 'var(--brass)', letterSpacing: '0.05em', display: 'block', marginBottom: '2px' }}>
            Top TreeSHAP Attribution Drivers
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {key_drivers.map((d, i) => (
              <span key={i} className="mono-data" style={{ fontSize: '0.7rem', backgroundColor: 'var(--paper-subtle)', padding: '1px 5px', borderRadius: '2px', color: 'var(--ledger-ink)' }}>
                {d}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
