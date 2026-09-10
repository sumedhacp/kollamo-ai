import React, { useState } from 'react';
import axios from 'axios';
import { Download, CheckSquare, Square, Play, Loader2, ExternalLink, Globe } from 'lucide-react';

export default function Zone2Extractor({ onBatchAnalyzed }) {
  const [url, setUrl] = useState('');
  const [maxComments, setMaxComments] = useState(25);
  const [fetching, setFetching] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [extractedComments, setExtractedComments] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [error, setError] = useState('');
  const [showExplanation, setShowExplanation] = useState(false);

  const handleFetch = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setFetching(true);
    setError('');
    try {
      const res = await axios.post('/api/fetch-comments', {
        url,
        max_comments: parseInt(maxComments)
      });
      setExtractedComments(res.data.comments);
      // Auto-select all on fetch
      setSelectedIds(new Set(res.data.comments.map(c => c.comment_id)));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch comments from URL.');
    } finally {
      setFetching(false);
    }
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === extractedComments.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(extractedComments.map(c => c.comment_id)));
    }
  };

  const toggleRow = (id) => {
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedIds(next);
  };

  const handleAnalyzeSelected = async () => {
    const selectedPayload = extractedComments.filter(c => selectedIds.has(c.comment_id));
    if (selectedPayload.length === 0) return;

    setAnalyzing(true);
    setError('');
    try {
      const res = await axios.post('/api/analyze-batch', {
        comments: selectedPayload.map(c => ({
          comment_id: c.comment_id,
          text: c.text,
          author: c.author,
          like_count: c.like_count,
          published_at: c.published_at
        }))
      });
      onBatchAnalyzed(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Batch analysis failed.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
            <Download className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Zone 2: Social Media Link Ingestion & Auditor</h2>
            <p className="text-xs text-slate-400">Extract live comments via YouTube Data API and curate rows</p>
          </div>
        </div>
      </div>

      {/* URL Input Form */}
      <form onSubmit={handleFetch} className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-3">
          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste public YouTube video URL (e.g., https://www.youtube.com/watch?v=...)"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={maxComments}
            onChange={(e) => setMaxComments(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-3 text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option value={10}>10 items</option>
            <option value={25}>25 items</option>
            <option value={50}>50 items</option>
          </select>
          <button
            type="submit"
            disabled={fetching}
            className="flex-1 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm font-semibold px-4 py-3 rounded-xl transition flex items-center justify-center gap-2 shadow-lg shadow-cyan-900/30"
          >
            {fetching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            <span>{fetching ? 'Fetching...' : 'Extract'}</span>
          </button>
        </div>
      </form>

      {error && <div className="text-xs text-rose-400">{error}</div>}

      {/* Extracted Comments Table */}
      {extractedComments.length > 0 && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={toggleSelectAll}
                className="flex items-center gap-2 text-xs font-semibold text-slate-300 hover:text-white transition"
              >
                {selectedIds.size === extractedComments.length ? (
                  <CheckSquare className="w-4 h-4 text-cyan-400" />
                ) : (
                  <Square className="w-4 h-4 text-slate-500" />
                )}
                <span>Select All ({selectedIds.size}/{extractedComments.length})</span>
              </button>

              <button
                type="button"
                onClick={() => setShowExplanation(!showExplanation)}
                className="flex items-center gap-1 text-xs text-slate-400 hover:text-cyan-400 transition"
              >
                <Globe className="w-3.5 h-3.5" />
                <span>{showExplanation ? 'Hide Clean Tokens' : 'Inspect Preprocessed Tokens'}</span>
              </button>
            </div>

            <button
              type="button"
              onClick={handleAnalyzeSelected}
              disabled={analyzing || selectedIds.size === 0}
              className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold px-4 py-2 rounded-xl transition flex items-center gap-2 shadow-md shadow-emerald-900/30"
            >
              {analyzing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
              <span>Analyze Selected ({selectedIds.size})</span>
            </button>
          </div>

          <div className="border border-slate-800 rounded-xl overflow-hidden max-h-72 overflow-y-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider sticky top-0">
                <tr>
                  <th className="p-3 w-10"></th>
                  <th className="p-3">Comment Text</th>
                  <th className="p-3 w-32">Author</th>
                  <th className="p-3 w-20 text-right">Likes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-950/40">
                {extractedComments.map((item) => {
                  const isChecked = selectedIds.has(item.comment_id);
                  return (
                    <tr
                      key={item.comment_id}
                      onClick={() => toggleRow(item.comment_id)}
                      className={`cursor-pointer transition hover:bg-slate-800/40 ${isChecked ? 'bg-cyan-500/5' : ''}`}
                    >
                      <td className="p-3 text-center" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleRow(item.comment_id)}
                          className="rounded border-slate-700 text-cyan-500 focus:ring-0 bg-slate-900 cursor-pointer"
                        />
                      </td>
                      <td className="p-3 text-slate-200">
                        <div>{item.text}</div>
                        {showExplanation && (
                          <div className="text-[11px] text-cyan-400/80 font-mono mt-0.5">
                            Tokens: {item.text.replace(/[^a-zA-Z0-9 ]/g, '')}
                          </div>
                        )}
                      </td>
                      <td className="p-3 text-slate-400 truncate max-w-[120px]">{item.author}</td>
                      <td className="p-3 text-right font-mono text-slate-400">{item.like_count}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}