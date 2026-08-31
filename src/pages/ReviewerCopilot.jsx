import React, { useState } from 'react';
import MarginColumn from '../components/MarginColumn';
import CaseCard from '../components/CaseCard';
import StampBadge from '../components/StampBadge';
import copilotData from '../content/reviewer_copilot.json';

export default function ReviewerCopilot() {
  const { curated_cases, hallucination_cases } = copilotData;

  const [selectedAction, setSelectedAction] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedHalCase, setSelectedHalCase] = useState(0);

  const actions = ['ALL', 'MANUAL_AUDIT', 'ESCALATE_DOC_REVIEW', 'OVERRIDE_SERVICER', 'REQUEST_CURE', 'AUTO_APPROVE'];

  const filteredCases = curated_cases.filter((c) => {
    const matchesAction = selectedAction === 'ALL' || c.action === selectedAction;
    const matchesQuery = !searchQuery || c.loan_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesAction && matchesQuery;
  });

  const activeHal = hallucination_cases[selectedHalCase] || hallucination_cases[0];

  return (
    <div className="page-grid">
      <MarginColumn
        sectionNumber="05"
        sectionTitle="Reviewer Copilot"
        contextInfo="24 Stratified Audit Cases, TreeSHAP & HAL-001..004 Guardrails"
        subLinks={[
          { id: 'case-browser', label: '24 Curated Cases' },
          { id: 'guardrail-showcase', label: 'Safety Guardrails (HAL-001..004)' }
        ]}
      />

      <div className="content-column">
        <header className="page-header">
          <h1>Grounded LLM Reviewer Copilot & Governance Layer</h1>
          <p className="page-lead">
            Translating high-dimensional calibrated ML forecasts, Isolation Forest anomaly scores, and TreeSHAP drivers into structured natural-language audit notes constrained by deterministic rule guardrails.
          </p>
        </header>

        {/* Section 1: 24-Case Interactive Browser */}
        <section id="case-browser" style={{ marginBottom: 'var(--space-10)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
            <div>
              <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: '2px' }}>
                1. Stratified Reviewer Case Directory
              </h2>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--ink-muted)' }}>
                Showing {filteredCases.length} of {curated_cases.length} verified audit records across 6 action classes.
              </p>
            </div>

            {/* Search Box */}
            <div>
              <input
                type="text"
                placeholder="Search Loan ID (e.g. F19Q10021012)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  padding: 'var(--space-2) var(--space-3)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  border: '1px solid var(--faint-rule)',
                  backgroundColor: 'var(--paper-card)',
                  color: 'var(--ledger-ink)',
                  borderRadius: 'var(--border-radius-sm)',
                  width: '260px'
                }}
              />
            </div>
          </div>

          {/* Action Filter Ledger Tabs */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: 'var(--space-4)' }}>
            {actions.map((act) => (
              <button
                key={act}
                type="button"
                onClick={() => setSelectedAction(act)}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  padding: '4px 10px',
                  border: '1px solid',
                  borderColor: selectedAction === act ? 'var(--brass)' : 'var(--faint-rule)',
                  backgroundColor: selectedAction === act ? 'var(--brass)' : 'var(--paper-card)',
                  color: selectedAction === act ? 'var(--ledger-paper)' : 'var(--ledger-ink)',
                  cursor: 'pointer',
                  borderRadius: '2px'
                }}
              >
                {act}
              </button>
            ))}
          </div>

          {/* List of Case Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {filteredCases.map((c, idx) => (
              <CaseCard key={`${c.loan_id}-${c.reporting_month}-${idx}`} caseData={c} defaultExpanded={idx === 0} />
            ))}
          </div>
        </section>

        {/* Section 2: Hallucination Guardrail Showcase (HAL-001 through HAL-004) */}
        <section id="guardrail-showcase" style={{ marginBottom: 'var(--space-10)' }}>
          <div style={{ borderBottom: '1px solid var(--brass)', paddingBottom: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--brass)', textTransform: 'uppercase' }}>
              Governance & AI Safety Catalog (Task 7 Rubric)
            </span>
            <h2 style={{ fontSize: 'var(--text-xl)', marginTop: '2px' }}>
              2. Hallucination & Rejection Guardrails (HAL-001 through HAL-004)
            </h2>
          </div>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-4)' }}>
            Systematic demonstration of deliberate edge cases where naive LLM recommendations were caught and overridden by deterministic invariant policies.
          </p>

          {/* 4 Case Selector Tabs */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: 'var(--space-4)' }}>
            {hallucination_cases.map((hal, i) => (
              <button
                key={hal.case_id}
                type="button"
                onClick={() => setSelectedHalCase(i)}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--text-xs)',
                  fontWeight: 600,
                  padding: '6px 12px',
                  border: '1px solid',
                  borderColor: selectedHalCase === i ? 'var(--flagged-red)' : 'var(--faint-rule)',
                  backgroundColor: selectedHalCase === i ? 'var(--flagged-red)' : 'var(--paper-card)',
                  color: selectedHalCase === i ? 'var(--ledger-paper)' : 'var(--ledger-ink)',
                  cursor: 'pointer',
                  borderRadius: '2px'
                }}
              >
                [{hal.case_id}] {hal.title.split('(')[0]}
              </button>
            ))}
          </div>

          {/* Active Guardrail Card */}
          <div className="ledger-card" style={{ borderLeft: '3px solid var(--flagged-red)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 'var(--space-3)' }}>
              <h3 style={{ fontSize: 'var(--text-md)', color: 'var(--ledger-ink)' }}>
                Case `{activeHal.case_id}`: {activeHal.title}
              </h3>
              <StampBadge action="REJECTED" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-4)', fontSize: 'var(--text-xs)', marginBottom: 'var(--space-4)' }}>
              <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px' }}>
                <span style={{ color: 'var(--flagged-red)', fontWeight: 700, display: 'block', marginBottom: '4px' }}>
                  [1] Naive / Ungrounded LLM Proposal:
                </span>
                <p style={{ fontStyle: 'italic', color: 'var(--ledger-ink)' }}>
                  &ldquo;{activeHal.naive_llm_output}&rdquo;
                </p>
              </div>

              <div style={{ padding: 'var(--space-3)', backgroundColor: 'var(--paper-subtle)', borderRadius: '2px' }}>
                <span style={{ color: 'var(--brass)', fontWeight: 700, display: 'block', marginBottom: '4px' }}>
                  [2] Technical Failure Diagnosis:
                </span>
                <p style={{ color: 'var(--ledger-ink)' }}>
                  {activeHal.failure_analysis}
                </p>
              </div>
            </div>

            <div style={{ padding: 'var(--space-3)', backgroundColor: 'rgba(62, 92, 78, 0.08)', borderLeft: '3px solid var(--reconciled-green)', fontSize: 'var(--text-xs)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                <strong style={{ color: 'var(--reconciled-green)' }}>[3] Enforced Deterministic Guardrail Override:</strong>
                <span className="mono-data" style={{ fontWeight: 700, color: 'var(--reconciled-green)' }}>
                  Action: {activeHal.corrected_action}
                </span>
              </div>
              <p style={{ color: 'var(--ledger-ink)', marginTop: '2px' }}>
                {activeHal.corrected_memo}
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
