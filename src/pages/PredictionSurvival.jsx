import React from 'react';
import MarginColumn from '../components/MarginColumn';
import MetricStrip from '../components/MetricStrip';
import predData from '../content/prediction_survival.json';

export default function PredictionSurvival() {
  const { models, calibration_curve, survival_curves, fp_fn_gallery, exception_required_narrative } = predData;

  return (
    <div className="page-grid">
      <MarginColumn
        sectionNumber="03"
        sectionTitle="Prediction & Survival"
        contextInfo="Supervised Modeling, Calibration, Survival & Leakage Audit"
        subLinks={[
          { id: 'supervised-models', label: 'Supervised Models' },
          { id: 'calibration-curve', label: 'Calibration Curve' },
          { id: 'survival-curves', label: 'Survival Analysis (Cox PH)' },
          { id: 'fp-fn-gallery', label: 'Error Diagnostics (FP/FN)' },
          { id: 'leakage-audit', label: 'exception_required Audit' }
        ]}
      />

      <div className="content-column">
        <header className="page-header">
          <h1>Loan Performance Prediction & Survival Modeling</h1>
          <p className="page-lead">
            Multi-horizon non-LLM supervised machine learning, isotonic calibration, and competing-risk survival analysis evaluated on out-of-sample chronological holdouts.
          </p>
        </header>

        {/* Section 1: Supervised Model Small Multiples */}
        <section id="supervised-models" style={{ marginBottom: 'var(--space-8)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            Supervised Performance Benchmarks
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-4)' }}>
            Comparing Scaled Logistic Regression / Decision Tree Baselines vs. Tuned XGBoost with Isotonic Probability Calibration.
          </p>

          <div className="metrics-small-multiples">
            {models.map((m, idx) => (
              <MetricStrip key={idx} modelInfo={m} />
            ))}
          </div>
        </section>

        {/* Section 2: Calibration Reliability Diagram & Survival Curves */}
        <section id="calibration-curve" style={{ marginBottom: 'var(--space-8)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-6)' }}>
            {/* Calibration Reliability Diagram */}
            <div className="ledger-card" style={{ margin: 0 }}>
              <div style={{ borderBottom: '1px solid var(--brass)', paddingBottom: 'var(--space-2)', marginBottom: 'var(--space-3)' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--brass)', textTransform: 'uppercase' }}>
                  Reliability Calibration Diagram
                </span>
                <h3 style={{ fontSize: 'var(--text-md)', marginTop: '2px' }}>
                  12-Month Default Model Calibration
                </h3>
              </div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-4)' }}>
                Comparing binned predicted probabilities vs. empirical default frequencies against the ideal 45&deg; line.
              </p>

              {/* Pure SVG Calibration Chart */}
              <div style={{ width: '100%', height: '220px', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px', padding: '10px' }}>
                <svg viewBox="0 0 300 200" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                  {/* Grid Lines */}
                  <line x1="40" y1="20" x2="280" y2="20" stroke="var(--faint-rule)" strokeDasharray="3 3" />
                  <line x1="40" y1="95" x2="280" y2="95" stroke="var(--faint-rule)" strokeDasharray="3 3" />
                  <line x1="40" y1="170" x2="280" y2="170" stroke="var(--ledger-ink)" strokeWidth="1.5" />
                  <line x1="40" y1="20" x2="40" y2="170" stroke="var(--ledger-ink)" strokeWidth="1.5" />

                  {/* 45 Degree Diagonal (Perfect Calibration) */}
                  <line x1="40" y1="170" x2="280" y2="20" stroke="var(--ink-dim)" strokeDasharray="4 4" strokeWidth="1.5" />

                  {/* Empirical Calibration Curve Line */}
                  <polyline
                    fill="none"
                    stroke="var(--reconciled-green)"
                    strokeWidth="2.5"
                    points={calibration_curve.map((pt) => {
                      const x = 40 + (pt.bin_midpoint * 240);
                      const y = 170 - (pt.empirical_fraction * 150);
                      return `${x},${y}`;
                    }).join(' ')}
                  />

                  {/* Points */}
                  {calibration_curve.map((pt, i) => {
                    const x = 40 + (pt.bin_midpoint * 240);
                    const y = 170 - (pt.empirical_fraction * 150);
                    return <circle key={i} cx={x} cy={y} r="3.5" fill="var(--reconciled-green)" stroke="var(--ledger-paper)" strokeWidth="1" />;
                  })}

                  {/* Axis Labels */}
                  <text x="160" y="192" fontSize="9" textAnchor="middle" fill="var(--ink-dim)" fontFamily="var(--font-mono)">Mean Predicted Probability</text>
                  <text x="15" y="95" fontSize="9" textAnchor="middle" transform="rotate(-90 15 95)" fill="var(--ink-dim)" fontFamily="var(--font-mono)">Empirical Default %</text>
                </svg>
              </div>
              <div style={{ marginTop: 'var(--space-2)', fontSize: 'var(--text-xs)', color: 'var(--reconciled-green)', fontWeight: 600, textAlign: 'center' }}>
                &check; Brier Score: 0.0273 &bull; Max Calibration Error &le; 1.2%
              </div>
            </div>

            {/* Survival Curves (Cox PH / Kaplan-Meier) */}
            <div id="survival-curves" className="ledger-card" style={{ margin: 0 }}>
              <div style={{ borderBottom: '1px solid var(--brass)', paddingBottom: 'var(--space-2)', marginBottom: 'var(--space-3)' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--brass)', textTransform: 'uppercase' }}>
                  Time-to-Event Survival Engine
                </span>
                <h3 style={{ fontSize: 'var(--text-md)', marginTop: '2px' }}>
                  Cox Proportional Hazards Trajectories
                </h3>
              </div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-4)' }}>
                Cumulative survival probability <span className="mono-data" style={{ color: 'var(--ledger-ink)', fontWeight: 600 }}>S(t)</span> over 36 months stratified across credit score tiers (C-statistic: 0.6866).
              </p>

              {/* Pure SVG Survival Curves Chart */}
              <div style={{ width: '100%', height: '220px', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px', padding: '10px' }}>
                <svg viewBox="0 0 300 200" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                  {/* Grid Lines */}
                  <line x1="40" y1="20" x2="280" y2="20" stroke="var(--faint-rule)" strokeDasharray="3 3" />
                  <line x1="40" y1="95" x2="280" y2="95" stroke="var(--faint-rule)" strokeDasharray="3 3" />
                  <line x1="40" y1="170" x2="280" y2="170" stroke="var(--ledger-ink)" strokeWidth="1.5" />
                  <line x1="40" y1="20" x2="40" y2="170" stroke="var(--ledger-ink)" strokeWidth="1.5" />

                  {/* Prime Tier Line */}
                  <polyline
                    fill="none"
                    stroke="var(--reconciled-green)"
                    strokeWidth="2"
                    points={survival_curves.map((pt) => `${40 + (pt.month / 36 * 240)},${170 - ((pt.prime - 0.7) / 0.3 * 150)}`).join(' ')}
                  />
                  {/* Good Tier Line */}
                  <polyline
                    fill="none"
                    stroke="var(--brass)"
                    strokeWidth="2"
                    points={survival_curves.map((pt) => `${40 + (pt.month / 36 * 240)},${170 - ((pt.good - 0.7) / 0.3 * 150)}`).join(' ')}
                  />
                  {/* Subprime Tier Line */}
                  <polyline
                    fill="none"
                    stroke="var(--flagged-red)"
                    strokeWidth="2"
                    points={survival_curves.map((pt) => `${40 + (pt.month / 36 * 240)},${170 - ((pt.subprime - 0.7) / 0.3 * 150)}`).join(' ')}
                  />

                  {/* Legend inside chart */}
                  <circle cx="210" cy="35" r="3" fill="var(--reconciled-green)" />
                  <text x="218" y="38" fontSize="8" fill="var(--ledger-ink)" fontFamily="var(--font-mono)">Prime (740+)</text>
                  <circle cx="210" cy="48" r="3" fill="var(--brass)" />
                  <text x="218" y="51" fontSize="8" fill="var(--ledger-ink)" fontFamily="var(--font-mono)">Good (680-740)</text>
                  <circle cx="210" cy="61" r="3" fill="var(--flagged-red)" />
                  <text x="218" y="64" fontSize="8" fill="var(--ledger-ink)" fontFamily="var(--font-mono)">Subprime (&le;620)</text>

                  {/* Axis Labels */}
                  <text x="160" y="192" fontSize="9" textAnchor="middle" fill="var(--ink-dim)" fontFamily="var(--font-mono)">Elapsed Loan Age (Months)</text>
                  <text x="15" y="95" fontSize="9" textAnchor="middle" transform="rotate(-90 15 95)" fill="var(--ink-dim)" fontFamily="var(--font-mono)">Survival S(t)</text>
                </svg>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: Concrete FP / FN Mini-Gallery */}
        <section id="fp-fn-gallery" style={{ marginBottom: 'var(--space-8)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            Error Diagnostics Mini-Gallery (Held-Out Validation Cohort)
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-4)' }}>
            Auditing concrete boundary failure modes on the untouched 15% temporal validation slice.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)' }}>
            {fp_fn_gallery.map((ex, idx) => (
              <div key={idx} className="ledger-card" style={{ margin: 0, padding: 'var(--space-4)' }}>
                <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)', display: 'block', marginBottom: '2px' }}>
                  {ex.case_type}
                </span>
                <h3 style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-2)' }}>
                  Loan `{ex.loan_id}`
                </h3>
                <div style={{ fontSize: 'var(--text-xs)', marginBottom: 'var(--space-2)' }}>
                  Predicted: <strong className="mono-data">{ex.pred_prob}</strong> &bull; Actual: <strong className="mono-data" style={{ color: 'var(--flagged-red)' }}>{ex.actual_outcome}</strong>
                </div>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)', marginBottom: 'var(--space-3)', lineHeight: 'var(--leading-snug)' }}>
                  {ex.root_cause}
                </p>
                <div style={{ borderTop: '1px dotted var(--faint-rule)', paddingTop: 'var(--space-2)', fontSize: '0.7rem', color: 'var(--ink-dim)' }}>
                  SHAP Divergence: <span className="mono-data" style={{ color: 'var(--ledger-ink)' }}>{ex.primary_shap_driver}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Section 4: exception_required & exception_type Target Leakage Investigation */}
        <section id="leakage-audit">
          <div className="ledger-callout" style={{ borderLeftColor: 'var(--brass)', backgroundColor: 'var(--paper-card)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 'var(--space-2)' }}>
              <h2 style={{ fontSize: 'var(--text-lg)', color: 'var(--ledger-ink)' }}>
                Target Transparency Audit: `exception_required` (0.9997 AUC) & `exception_type` (1.0000 Macro-F1)
              </h2>
              <span className="mono-data" style={{ fontSize: 'var(--text-xs)', color: 'var(--brass)', fontWeight: 700 }}>
                [METHODOLOGY DISCLOSURE]
              </span>
            </div>

            <p style={{ fontSize: 'var(--text-sm)', marginBottom: 'var(--space-3)', lineHeight: 'var(--leading-normal)' }}>
              During the modeling pass, `exception_required` achieved <strong>ROC-AUC 0.9997</strong> / <strong>PR-AUC 0.9964</strong>, and the baseline Decision Tree for `exception_type` achieved a literal <strong>1.0000 Macro-F1</strong>. A near-1.0 metric standing next to realistically hard 0.86 default and 0.65 prepayment models is the classic signature of deterministic rule reconstruction rather than behavioral credit risk.
            </p>

            <h3 style={{ fontSize: 'var(--text-sm)', marginBottom: 'var(--space-2)', color: 'var(--ledger-ink)' }}>
              TreeSHAP Feature Attribution & Partitioning Mechanism:
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
              {exception_required_narrative.findings.map((f, idx) => (
                <div key={idx} style={{ padding: 'var(--space-3)', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px', fontSize: 'var(--text-xs)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                    <strong className="mono-data">{f.feature.split(' ')[0]}</strong>
                    <span className="mono-data" style={{ color: 'var(--brass)', fontWeight: 700 }}>{f.importance}</span>
                  </div>
                  <span style={{ color: 'var(--ink-muted)' }}>{f.mechanism}</span>
                </div>
              ))}
            </div>

            <div style={{ padding: 'var(--space-3)', borderTop: '1px dashed var(--brass)', fontSize: 'var(--text-xs)', color: 'var(--ledger-ink)', lineHeight: 'var(--leading-normal)' }}>
              <strong>Rigorous Disclosure</strong>: Both `exception_required` and `exception_type` are deterministic snapshot targets defined directly by document status, balance surges, and term anomalies. Tree models easily partition these exact input boundaries. We retain both in the multi-task stack as high-speed operational rule reconstructors while reporting forward credit risk on genuine non-deterministic horizons (12M Default ROC-AUC: 0.8595, 12M Prepayment ROC-AUC: 0.6542).
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
