import React from 'react';

export default function StampBadge({ action, size = 'normal' }) {
  const cleanAction = String(action || 'AUTO_APPROVE').toUpperCase();
  
  let stampClass = 'approved';
  if (['MANUAL_AUDIT', 'FLAGGED', 'REJECTED', 'CRITICAL', 'BREACH'].includes(cleanAction)) {
    stampClass = 'audit';
  } else if (['ESCALATE_DOC_REVIEW', 'OVERRIDE_SERVICER', 'REQUEST_CURE', 'ACCEPT_PRIMARY', 'WARNING', 'MEDIUM', 'HIGH'].includes(cleanAction)) {
    stampClass = 'neutral';
  }

  const isSmall = size === 'small';

  return (
    <span
      className={`stamp-badge ${stampClass}`}
      style={{
        fontSize: isSmall ? '0.7rem' : '0.8rem',
        padding: isSmall ? '2px 6px' : '4px 10px',
        letterSpacing: '0.06em'
      }}
    >
      [{cleanAction}]
    </span>
  );
}
