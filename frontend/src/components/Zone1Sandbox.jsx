import React, { useState } from 'react';
import axios from 'axios';
import { Send, Loader2, Sparkles, Gauge, Zap } from 'lucide-react';

const BADGE_STYLES = {
  Positive: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  Negative: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  Neutral: 'bg-slate-500/10 text-slate-300 border-slate-500/30'
};

export default function Zone1Sandbox() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setLoading(true);
    setError('');
    try {
      const res = await axios.post('/api/analyze-text', { text: inputText });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Inference engine connection failed.');
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    "Padam kidu aayirunnu, visuals and BGM pwoli!",
    "Valare bore aayi poyi, second half full lag aanu.",
    "Ee movie release date eppozhaanu OTT release?"
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Zone 1: Single-Text Sandbox</h2>
            <p className="text-xs text-slate-400">Ad-hoc testing and model confidence scoring</p>
          </div>
        </div>
      </div>

      <form onSubmit={handlePredict} className="space-y-4">
        <div>
          <textarea
            rows={3}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type Romanized Malayalam (Manglish) text (e.g., Padam super aayirunnu, pakshe climax bore...)"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none transition"
          />
        </div>

        {/* Quick Sample Fillers */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-500">Quick Test:</span>
          {samplePrompts.map((prompt, idx) => (
            <button
              type="button"
              key={idx}
              onClick={() => setInputText(prompt)}
              className="text-xs bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 px-3 py-1 rounded-md transition"
            >
              {prompt.slice(0, 32)}...
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between pt-2">
          {error && <span className="text-xs text-rose-400">{error}</span>}
          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            className="ml-auto bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition flex items-center gap-2 shadow-lg shadow-emerald-900/30"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            <span>{loading ? 'Evaluating...' : 'Predict Sentiment'}</span>
          </button>
        </div>
      </form>

      {result && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${BADGE_STYLES[result.label] || 'bg-slate-800 text-slate-300'}`}>
                {result.label}
              </span>
              <span className="text-sm font-mono text-slate-200">
                Confidence: <strong className="text-white">{result.confidence}%</strong>
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Latency: {result.latency_ms} ms</span>
            </div>
          </div>

          {/* Probability Distribution Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Class Distribution (Softmax)</span>
              <span>Pos: {(result.probabilities.Positive * 100).toFixed(1)}% | Neg: {(result.probabilities.Negative * 100).toFixed(1)}% | Neu: {(result.probabilities.Neutral * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden flex">
              <div
                style={{ width: `${(result.probabilities.Positive || 0) * 100}%` }}
                className="bg-emerald-500 h-full transition-all duration-500"
                title="Positive"
              />
              <div
                style={{ width: `${(result.probabilities.Negative || 0) * 100}%` }}
                className="bg-rose-500 h-full transition-all duration-500"
                title="Negative"
              />
              <div
                style={{ width: `${(result.probabilities.Neutral || 0) * 100}%` }}
                className="bg-slate-500 h-full transition-all duration-500"
                title="Neutral"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}