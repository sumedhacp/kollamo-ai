// src/components/SocialStudio.jsx
import React, { useState } from 'react';

export default function SocialStudio({ onAnalyze, setActiveTab }) {
  const [url, setUrl] = useState('https://www.youtube.com/watch?v=2hAfg4tjc-s');
  const [limitMode, setLimitMode] = useState('50');
  const [customCount, setCustomCount] = useState(10);
  const [sortOrder, setSortOrder] = useState('top');
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState('');
  const [fetchNotice, setFetchNotice] = useState('');
  const [detectedPlatform, setDetectedPlatform] = useState('YOUTUBE');

  // Initialized with realistic Code-Mixed Malayalam comments as starting baseline
  const [comments, setComments] = useState([
    { id: 'c_1', author: '@rahul_nair', text: 'Padam thooki! Climax scene romancham aayirunnu 🔥🔥', likes: 450, date: '1d ago' },
    { id: 'c_2', author: '@anjali_k', text: 'Valare bore aayi poyi, second half full lag waste of money', likes: 112, date: '1d ago' },
    { id: 'c_3', author: '@cinema_lover', text: 'First half pwoli, but second half valare bore', likes: 89, date: '2d ago' },
    { id: 'c_4', author: '@tovino_fan', text: 'Acting super, especially Tovino and lead actors. Must watch!', likes: 340, date: '3d ago' },
    { id: 'c_5', author: '@sreejith_v', text: 'BGM kollam, pakshe direction theere thripthikaram alla.', likes: 62, date: '4d ago' },
    { id: 'c_6', author: '@ott_updates', text: 'Ee movie OTT release date eppozhaanu?', likes: 15, date: '5d ago' },
    { id: 'c_7', author: '@rohan_sharma', text: 'यह फिल्म बहुत अच्छी है', likes: 8, date: '6d ago' }
  ]);
  const [selectedIds, setSelectedIds] = useState(new Set());

  // Auto-detect whether user pastes YouTube or Instagram link
  const handleUrlChange = (val) => {
    setUrl(val);
    const low = val.toLowerCase();
    if (low.includes('instagram.com') || low.includes('instagr.am')) {
      setDetectedPlatform('INSTAGRAM');
    } else if (low.includes('youtube.com') || low.includes('youtu.be')) {
      setDetectedPlatform('YOUTUBE');
    } else {
      setDetectedPlatform('AUTO-DETECT');
    }
  };

  // Live Extraction Trigger calling FastAPI backend /api/scrape-comments
    // Sort helper ensuring Top Liked, Newest, and Oldest sort accurately
  const sortFeed = (items, order) => {
    const parseTime = (str) => {
      if (!str) return 0;
      const s = str.toLowerCase().trim();
      if (/^\d{4}-\d{2}-\d{2}/.test(s)) {
        return new Date(s).getTime() || 0;
      }
      const numMatch = s.match(/(\d+)/);
      const val = numMatch ? parseFloat(numMatch[1]) : 1;
      const now = Date.now();
      if (s.includes('sec')) return now - val * 1000;
      if (s.includes('min')) return now - val * 60 * 1000;
      if (s.includes('hour') || s.includes('hr')) return now - val * 3600 * 1000;
      if (s.includes('day')) return now - val * 86400 * 1000;
      if (s.includes('week')) return now - val * 7 * 86400 * 1000;
      if (s.includes('month')) return now - val * 30 * 86400 * 1000;
      if (s.includes('year')) return now - val * 365 * 86400 * 1000;
      return now;
    };

    const copy = [...items];
    if (order === 'top' || order === 'Top Liked') {
      return copy.sort((a, b) => (b.likes || 0) - (a.likes || 0));
    } else if (order === 'newest') {
      return copy.sort((a, b) => parseTime(b.date) - parseTime(a.date));
    } else if (order === 'oldest') {
      return copy.sort((a, b) => parseTime(a.date) - parseTime(b.date));
    }
    return copy;
  };

  const handleFetchFeed = async () => {
    if (!url.trim()) {
      setFetchError("Please paste a valid YouTube or Instagram URL.");
      return;
    }

    setLoading(true);
    setFetchError('');
    setFetchNotice('');
    // Reset state immediately so previous search results do not persist
    setComments([]);
    setSelectedIds(new Set());

    try {
      const targetLimit = limitMode === 'all' 
        ? 0 
        : (limitMode === 'custom' ? Math.max(1, parseInt(customCount, 10) || 1) : parseInt(limitMode, 10));

      const response = await fetch('/api/scrape-comments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          url: url.trim(),
          max_comments: targetLimit,
          sort_order: sortOrder
        })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server responded with error status ${response.status}`);
      }

      const data = await response.json();
      const extractedList = data.comments || [];
      const totalCount = extractedList.length;

      if (totalCount === 0) {
        setFetchError("No comments could be retrieved. Ensure comments are enabled and accessible on this post/video.");
        setComments([]);
        setSelectedIds(new Set());
        return;
      }

      const mapped = extractedList.map((item, index) => ({
        id: item.comment_id ? `${item.comment_id}__${index}` : `comment_${index}`,
        author: item.author || '@anonymous',
        text: item.text || '',
        likes: Number(item.like_count) || 0,
        date: item.published_at || 'Recent'
      }));

      // Sort with precision
      const sortedComments = sortFeed(mapped, sortOrder);
      setComments(sortedComments);
      setSelectedIds(new Set());

      if (targetLimit > 0 && totalCount < targetLimit) {
        setFetchNotice(`Note: You requested ${targetLimit.toLocaleString()} comments, but this video only has ${totalCount.toLocaleString()} total comments available. Extracted all ${totalCount.toLocaleString()} comments.`);
      } else if (targetLimit === 0) {
        setFetchNotice(`Successfully extracted all ${totalCount.toLocaleString()} comments from this video.`);
      }
    } catch (err) {
      setFetchError(err.message || "Failed to extract comments feed.");
    } finally {
      setLoading(false);
    }
  };

  const isAllSelected = comments.length > 0 && selectedIds.size === comments.length;

  const toggleSelectAll = () => {
    if (isAllSelected) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(comments.map((c) => c.id)));
    }
  };

  const toggleOne = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleExecuteBatch = (mode) => {
    const itemsToProcess = mode === 'all' 
      ? comments 
      : comments.filter((c) => selectedIds.has(c.id));

    if (itemsToProcess.length === 0) {
      alert("Select at least one comment row to proceed.");
      return;
    }

    // App.jsx will call /api/analyze-batch, populate the data, and switch tabs when ready
    onAnalyze(itemsToProcess);
  };

  return (
    <div>
      {/* Controls Card */}
      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div className="card-title">Live Comment Ingestion Console</div>
            <div className="card-subtitle">Extracts social comment feeds stripped of DOM buttons, timecodes, and player tags</div>
          </div>
          <span style={{ 
            fontSize: '0.6875rem', 
            fontWeight: '700', 
            padding: '0.25rem 0.5rem', 
            borderRadius: '4px', 
            backgroundColor: '#e2e8f0', 
            color: '#334155' 
          }}>
            Source: {detectedPlatform}
          </span>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '2fr 1fr 1fr auto',
          gap: '0.75rem',
          alignItems: 'end'
        }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.6875rem', fontWeight: '700', marginBottom: '0.375rem', color: 'var(--text-subtle)' }}>
              PUBLIC URL (YOUTUBE / SHORTS / INSTAGRAM REEL / POST)
            </label>
            <input
              type="text"
              className="input-text"
              value={url}
              onChange={(e) => handleUrlChange(e.target.value)}
              placeholder="Paste YouTube watch/short link or Instagram reel/post..."
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.6875rem', fontWeight: '700', marginBottom: '0.375rem', color: 'var(--text-subtle)' }}>
              LIMIT
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <select className="select-box" value={limitMode} onChange={(e) => setLimitMode(e.target.value)}>
                <option value="50">First 50</option>
                <option value="100">First 100</option>
                <option value="200">First 200</option>
                <option value="all">All</option>
                <option value="custom">Custom</option>
              </select>
              {limitMode === 'custom' && (
                <input
                  type="number"
                  min="1"
                  max="3000"
                  value={customCount}
                  onChange={(e) => setCustomCount(Math.max(1, parseInt(e.target.value, 10) || 1))}
                  className="input-text"
                  style={{ width: '80px', padding: '0.4rem 0.5rem', textAlign: 'center' }}
                  title="Enter custom number of comments (e.g. 1, 2, 3...)"
                />
              )}
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.6875rem', fontWeight: '700', marginBottom: '0.375rem', color: 'var(--text-subtle)' }}>
              SORT
            </label>
            <select 
              className="select-box" 
              value={sortOrder} 
              onChange={(e) => setSortOrder(e.target.value)}
              disabled={detectedPlatform === 'INSTAGRAM'}
            >
              <option value="top">Top Liked</option>
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
            </select>
          </div>

          <button 
            className="btn btn-primary" 
            onClick={handleFetchFeed} 
            disabled={loading}
            style={{ minWidth: '110px' }}
          >
            {loading ? "Extracting..." : "Fetch Feed"}
          </button>
        </div>

        {fetchNotice && (
          <div style={{ marginTop: '0.85rem', padding: '0.65rem 0.9rem', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.25)', color: '#1d4ed8', fontSize: '0.8125rem', fontWeight: '500' }}>
            ℹ️ {fetchNotice}
          </div>
        )}
        {fetchError && (
          <div style={{ marginTop: '0.85rem', color: '#b91c1c', fontSize: '0.8125rem', fontWeight: '600' }}>
            {fetchError}
          </div>
        )}
      </div>

      {/* Curation Table */}
      <div className="card" style={{ marginTop: '1.25rem' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem'
        }}>
          <div>
            <span style={{ fontWeight: '700', fontSize: '0.9375rem' }}>
              Extracted Records ({comments.length})
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginLeft: '0.5rem' }}>
              Selected: {selectedIds.size}
            </span>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn btn-secondary" onClick={toggleSelectAll}>
              {isAllSelected ? 'Deselect All' : 'Select All'}
            </button>
            <button className="btn btn-primary" onClick={() => handleExecuteBatch('selected')}>
              Analyze Selected ({selectedIds.size})
            </button>
            <button className="btn btn-dark" onClick={() => handleExecuteBatch('all')}>
              Analyze All ({comments.length})
            </button>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '40px', textAlign: 'center' }}>
                  <input
                    type="checkbox"
                    checked={isAllSelected}
                    onChange={toggleSelectAll}
                  />
                </th>
                <th style={{ width: '150px' }}>Author</th>
                <th>Comment Payload</th>
                <th style={{ width: '100px', textAlign: 'right' }}>Likes</th>
                <th style={{ width: '100px', textAlign: 'right' }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {comments.map((item) => {
                const isSelected = selectedIds.has(item.id);
                return (
                  <tr
                    key={item.id}
                    onClick={() => toggleOne(item.id)}
                    style={{
                      cursor: 'pointer',
                      backgroundColor: isSelected ? '#f8fafc' : 'transparent'
                    }}
                  >
                    <td style={{ textAlign: 'center' }} onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleOne(item.id)}
                      />
                    </td>
                    <td style={{ fontWeight: '600' }}>{item.author}</td>
                    <td>{item.text}</td>
                    <td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)' }}>{item.likes}</td>
                    <td style={{ textAlign: 'right', color: 'var(--text-subtle)' }}>{item.date}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}