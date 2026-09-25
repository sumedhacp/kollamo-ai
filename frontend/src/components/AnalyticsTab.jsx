// src/components/AnalyticsTab.jsx
import React, { useState } from 'react';

export default function AnalyticsTab({ data, summary }) {
  const [filter, setFilter] = useState('ALL');

  if (!data || data.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          No Evaluated Data Available
        </h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-subtle)', maxWidth: '420px', margin: '0 auto' }}>
          Navigate to the Social Ingestion tab to extract comments and trigger batch transformer analysis.
        </p>
      </div>
    );
  }

  // Normalize data fields from the backend
  const processed = data.map((item) => {
    const rawLabel = item.sentiment || item.label || 'Neutral';
    const label = rawLabel.charAt(0).toUpperCase() + rawLabel.slice(1).toLowerCase();

    return {
      id: item.id || item.comment_id,
      author: item.author || '@anonymous',
      text: item.text || item.comment || '',
      translation: item.translation || item.translated_text || item.text,
      label: label,
      confidence: item.confidence ?? 0,
      isSupported: item.isSupported ?? item.is_supported ?? (label !== 'Unsupported'),
      likes: item.likes ?? item.like_count ?? 0,
      date: item.date || item.published_at || 'Recent'
    };
  });

  const total = processed.length;
  const supportedCount = processed.filter((c) => c.isSupported).length;
  const posCount = processed.filter((c) => c.label === 'Positive').length;
  const negCount = processed.filter((c) => c.label === 'Negative').length;
  const neuCount = processed.filter((c) => c.label === 'Neutral').length;
  const mixCount = processed.filter((c) => c.label === 'Mixed').length;

  const posPct = total > 0 ? Math.round((posCount / total) * 100) : 0;
  const negPct = total > 0 ? Math.round((negCount / total) * 100) : 0;
  const neuPct = total > 0 ? Math.round((neuCount / total) * 100) : 0;
  const nss = posPct - negPct;

  const filteredComments = processed.filter((c) => {
    if (filter === 'ALL') return true;
    return c.label.toUpperCase() === filter;
  });

  // Handler: Download comments as CSV
  const handleExportCSV = () => {
    const headers = ["Author", "Original Comment", "Translation", "Sentiment", "Confidence (%)", "Likes", "Date"];
    const rows = processed.map((c) => [
      `"${c.author.replace(/"/g, '""')}"`,
      `"${c.text.replace(/"/g, '""')}"`,
      `"${c.translation.replace(/"/g, '""')}"`,
      c.label,
      c.confidence,
      c.likes,
      `"${c.date}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `kollamo_audience_data_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Handler: Download dataset & executive summary as JSON
  const handleExportJSON = () => {
    const exportObject = {
      meta: {
        total_analyzed: total,
        supported_count: supportedCount,
        net_sentiment_score: nss,
        sentiment_percentages: { positive: posPct, negative: negPct, neutral: neuPct }
      },
      summary: summary || null,
      comments: processed
    };

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObject, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", dataStr);
    link.setAttribute("download", `kollamo_audience_report_${Date.now()}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      
      {/* Title Header with Export Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>
            Audience Intelligence Dashboard
          </h2>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', margin: '0.2rem 0 0' }}>
            Multi-class Dravidian dialect calibration & executive narrative synthesis
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            className="btn btn-secondary" 
            onClick={handleExportCSV} 
            style={{ fontSize: '0.75rem', padding: '0.4rem 0.8rem' }}
          >
            Export CSV
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={handleExportJSON} 
            style={{ fontSize: '0.75rem', padding: '0.4rem 0.8rem' }}
          >
            Export JSON
          </button>
        </div>
      </div>

      {/* KPI Cards Header */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
        gap: '1rem'
      }}>
        <div className="card" style={{ marginBottom: 0 }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--text-subtle)', fontFamily: 'var(--font-mono)' }}>
            TOTAL EVALUATED
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', marginTop: '0.25rem' }}>
            {total}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
            Supported: {supportedCount}
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0 }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--pos-color)', fontFamily: 'var(--font-mono)' }}>
            POSITIVE RATIO
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', color: 'var(--pos-color)', marginTop: '0.25rem' }}>
            {posPct}%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
            {posCount} comments
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0 }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--neg-color)', fontFamily: 'var(--font-mono)' }}>
            NEGATIVE RATIO
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', color: 'var(--neg-color)', marginTop: '0.25rem' }}>
            {negPct}%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
            {negCount} comments
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0 }}>
          <div style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--neu-color)', fontFamily: 'var(--font-mono)' }}>
            NET SENTIMENT SCORE (NSS)
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', marginTop: '0.25rem' }}>
            {nss > 0 ? `+${nss}` : nss}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
            Scale: -100 to +100
          </div>
        </div>
      </div>

      {/* Executive Briefing Card (Rendered automatically when summary is ready) */}
      {summary && (
        <div className="card" style={{ backgroundColor: 'var(--bg-surface)', borderLeft: '4px solid var(--pos-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.6875rem', fontWeight: 800, letterSpacing: '0.05em', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>
              Executive Audience Briefing ({summary.domain_label || summary.domain || 'General'})
            </span>
            <span className="badge badge-slate" style={{ fontSize: '0.6875rem' }}>
              Vibe: {summary.audience_vibe || 'Neutral'}
            </span>
          </div>

          <h3 style={{ fontSize: '1.0625rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.35rem' }}>
            {summary.headline}
          </h3>

          <p style={{ fontSize: '0.875rem', lineHeight: '1.5', color: 'var(--text-main)', marginBottom: '0.85rem' }}>
            {summary.verdict}
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.85rem' }}>
            {/* Acclaim Drivers */}
            <div style={{ backgroundColor: 'var(--bg-subtle)', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--pos-color)', marginBottom: '0.35rem' }}>
                Primary Acclaim Drivers
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.8125rem', color: 'var(--text-main)' }}>
                {summary.key_strengths && summary.key_strengths.length > 0 ? (
                  summary.key_strengths.map((s, idx) => (
                    <li key={idx} style={{ marginBottom: '0.2rem' }}>{s}</li>
                  ))
                ) : (
                  <li>Consistent positive audience engagement.</li>
                )}
              </ul>
            </div>

            {/* Critique Drivers */}
            <div style={{ backgroundColor: 'var(--bg-subtle)', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--neg-color)', marginBottom: '0.35rem' }}>
                Key Criticisms & Observations
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.8125rem', color: 'var(--text-main)' }}>
                {summary.primary_criticisms && summary.primary_criticisms.length > 0 ? (
                  summary.primary_criticisms.map((c, idx) => (
                    <li key={idx} style={{ marginBottom: '0.2rem' }}>{c}</li>
                  ))
                ) : (
                  <li>No recurring negative consensus identified.</li>
                )}
              </ul>
            </div>
          </div>

          {summary.strategic_takeaway && (
            <div style={{ marginTop: '0.85rem', fontSize: '0.8125rem', color: 'var(--text-subtle)', fontStyle: 'italic', borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem' }}>
              <strong>Strategic Takeaway:</strong> {summary.strategic_takeaway}
            </div>
          )}
        </div>
      )}

      {/* Aggregate Distribution Bar */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Continuous Class Projections</div>
          <div className="card-subtitle">Aggregate polarity distribution calculated across the verified comment batch</div>
        </div>
        <div className="progress-track" style={{ height: '14px', marginBottom: '0.75rem' }}>
          <div className="progress-fill-pos" style={{ width: `${posPct}%` }} title={`Positive: ${posPct}%`} />
          <div className="progress-fill-neg" style={{ width: `${negPct}%` }} title={`Negative: ${negPct}%`} />
          <div className="progress-fill-neu" style={{ width: `${neuPct}%` }} title={`Neutral: ${neuPct}%`} />
        </div>
        <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--pos-color)' }} />
            Positive ({posPct}%)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--neg-color)' }} />
            Negative ({negPct}%)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--neu-color)' }} />
            Neutral ({neuPct}%)
          </span>
        </div>
      </div>

      {/* Filter Matrix Controls & Data Stream */}
      <div className="card">
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
          flexWrap: 'wrap',
          gap: '0.5rem'
        }}>
          <div>
            <div className="card-title">Curated Analysis Stream</div>
            <div className="card-subtitle">Showing {filteredComments.length} of {total} records</div>
          </div>

          <div style={{ display: 'flex', gap: '0.25rem', backgroundColor: 'var(--bg-subtle)', padding: '0.25rem', borderRadius: '6px' }}>
            {['ALL', 'POSITIVE', 'MIXED', 'NEUTRAL', 'NEGATIVE', 'UNSUPPORTED'].map((tab) => (
              <button
                key={tab}
                onClick={() => setFilter(tab)}
                style={{
                  border: 'none',
                  background: filter === tab ? '#ffffff' : 'transparent',
                  color: filter === tab ? 'var(--text-main)' : 'var(--text-muted)',
                  fontWeight: filter === tab ? '700' : '500',
                  fontSize: '0.6875rem',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontFamily: 'var(--font-mono)',
                  boxShadow: filter === tab ? '0 1px 2px rgba(0,0,0,0.05)' : 'none'
                }}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Comment Rows */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {filteredComments.map((c, i) => (
            <div key={c.id || i} style={{
              padding: '0.875rem 1rem',
              backgroundColor: 'var(--bg-subtle)',
              borderRadius: '8px',
              border: '1px solid var(--border-color)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
                <span style={{ fontWeight: '700', fontSize: '0.8125rem' }}>{c.author}</span>
                <span className={`badge ${
                  c.label === 'Positive' ? 'badge-pos' : 
                  c.label === 'Negative' ? 'badge-neg' : 
                  c.label === 'Mixed' ? 'badge-slate' : 
                  c.label === 'Unsupported' ? 'badge-neg' : 'badge-neu'
                }`}>
                  {c.label} {c.confidence > 0 && `(${c.confidence}%)`}
                </span>
              </div>
              <p style={{ fontSize: '0.875rem', marginBottom: '0.375rem', color: 'var(--text-main)' }}>
                "{c.text}"
              </p>
              <div style={{ fontSize: '0.75rem', fontStyle: 'italic', color: 'var(--text-muted)' }}>
                Translation: "{c.translation}"
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}