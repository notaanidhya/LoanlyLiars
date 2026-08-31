import React from 'react';

export default function MarginColumn({ sectionNumber, sectionTitle, contextInfo, subLinks = [] }) {
  return (
    <aside className="margin-column" aria-label="Page Context and Navigation">
      {sectionNumber && <div className="margin-section-number">{sectionNumber}</div>}
      {sectionTitle && <div className="margin-section-title">{sectionTitle}</div>}
      {contextInfo && <div className="margin-running-context">{contextInfo}</div>}
      
      {subLinks && subLinks.length > 0 && (
        <ul className="margin-nav-links">
          {subLinks.map((link, idx) => (
            <li key={idx}>
              <a href={`#${link.id}`}>{idx + 1}. {link.label}</a>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
