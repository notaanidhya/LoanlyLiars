import React from 'react';

export default function LedgerTable({ columns, data, keyField = 'id', caption }) {
  if (!data || data.length === 0) {
    return <p className="mono-data" style={{ color: 'var(--ink-dim)' }}>No ledger records available.</p>;
  }

  return (
    <div className="ledger-table-container">
      <table className="ledger-table">
        {caption && <caption style={{ textAlign: 'left', padding: 'var(--space-2) var(--space-4)', fontStyle: 'italic', fontSize: 'var(--text-xs)', color: 'var(--ink-muted)' }}>{caption}</caption>}
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th
                key={idx}
                className={col.numeric ? 'numeric' : ''}
                style={{ width: col.width || 'auto' }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr key={row[keyField] || rowIdx}>
              {columns.map((col, colIdx) => {
                const val = col.accessor ? (typeof col.accessor === 'function' ? col.accessor(row) : row[col.accessor]) : row[col.key];
                return (
                  <td key={colIdx} className={col.numeric ? 'numeric' : ''}>
                    {col.render ? col.render(val, row) : val}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
