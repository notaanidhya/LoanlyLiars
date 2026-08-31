import React from 'react';
import MarginColumn from '../components/MarginColumn';
import TimelineEntry from '../components/TimelineEntry';
import LedgerTable from '../components/LedgerTable';
import StampBadge from '../components/StampBadge';
import hwghData from '../content/how_we_got_here.json';

export default function HowWeGotHere() {
  const { debugging_narratives, accepted_rejected_ai, code_ownership } = hwghData;

  const decisionColumns = [
    { header: 'Date', key: 'timestamp', width: '100px', render: (val) => <span className="mono-data">{val}</span> },
    { header: 'Component', key: 'component', width: '140px', render: (val) => <strong>{val}</strong> },
    { header: 'AI Proposal', key: 'ai_proposal' },
    {
      header: 'Technical Decision',
      key: 'decision',
      width: '120px',
      render: (val) => <StampBadge action={val === 'ACCEPTED' ? 'APPROVED' : 'REJECTED'} size="small" />
    },
    { header: 'Engineering Rationale', key: 'rationale' }
  ];

  const ownershipColumns = [
    { header: 'Module File', key: 'module', width: '220px', render: (val) => <strong className="mono-data" style={{ color: 'var(--brass)' }}>{val}</strong> },
    { header: 'Architectural Purpose', key: 'purpose' },
    { header: 'AI Share', key: 'ai_share', numeric: true, width: '90px', render: (val) => <span className="mono-data">{val}</span> },
    { header: 'Human Review & Verification Protocol', key: 'human_review' }
  ];

  return (
    <div className="page-grid">
      <MarginColumn
        sectionNumber="06"
        sectionTitle="How We Got Here"
        contextInfo="Development Timeline, Defect Diagnostics & AI Governance"
        subLinks={[
          { id: 'defect-timeline', label: '6 Key Incident Narratives' },
          { id: 'accepted-rejected', label: 'Accepted vs. Rejected Proposals' },
          { id: 'code-ownership', label: 'Code Ownership & Review' }
        ]}
      />

      <div className="content-column">
        <header className="page-header">
          <h1>Engineering Progression & Defect Audit Trail</h1>
          <p className="page-lead">
            An authentic, chronological retrospective of edge cases diagnosed, leakage vectors eliminated, and AI proposals accepted or rejected throughout development.
          </p>
        </header>

        {/* Section 1: Numbered Chronological Timeline */}
        <section id="defect-timeline" style={{ marginBottom: 'var(--space-10)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            1. Chronological Incident & Defect Resolution Timeline
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-6)' }}>
            Six real-world technical failures diagnosed through strict empirical validation and corrected in code.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {debugging_narratives.map((incident, idx) => (
              <TimelineEntry key={incident.id} index={idx} incident={incident} />
            ))}
          </div>
        </section>

        {/* Section 2: Accepted vs Rejected AI Proposals */}
        <section id="accepted-rejected" style={{ marginBottom: 'var(--space-10)' }}>
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            2. Accepted vs. Rejected AI Outputs (Task 8 Governance)
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-4)' }}>
            Key decisions where initial AI proposals violated domain constraints and were overridden by human engineering review.
          </p>
          <LedgerTable columns={decisionColumns} data={accepted_rejected_ai} keyField="timestamp" caption="Formal Log of AI Proposal Approvals and Rejections" />
        </section>

        {/* Section 3: Code Ownership Table */}
        <section id="code-ownership">
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>
            3. Code Ownership & Review Share by Module
          </h2>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-muted)', marginBottom: 'var(--space-4)' }}>
            Transparent breakdown of automated code generation and manual verification across all core repository modules.
          </p>
          <LedgerTable columns={ownershipColumns} data={code_ownership} keyField="module" caption="Repository Code Ownership and Human Verification Matrix" />
        </section>
      </div>
    </div>
  );
}
