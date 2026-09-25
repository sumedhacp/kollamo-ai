// src/components/SandboxTab.jsx
import React, { useState } from 'react';

export default function SandboxTab() {
  const [inputText, setInputText] = useState('vere nthaalla');
  const [result, setResult] = useState(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [apiError, setApiError] = useState('');

  const samplePresets = [
    "Padam thooki! Climax scene romancham aayirunnu 🔥🔥",
    "First half pwoli, but second half valare bore",
    "Verum churandiyath padam, total lag waste of money",
    "ennik ishtam ayila",
    "vere nthaalla",
    "ennik arum ellia",
    "Ee cinema OTT release date eppozhaanu?",
    "यह फिल्म बहुत अच्छी है"
  ];

  const handlePredict = async (overrideText) => {
    const textToTest = (overrideText !== undefined ? overrideText : inputText).trim();
    if (!textToTest) return;

    setIsEvaluating(true);
    setApiError('');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/analyze-single', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ text: textToTest }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned status ${response.status}`);
      }

      const data = await response.json();

      setResult({
        isSupported: data.is_supported,
        languageType: data.language_type || "MANGLISH (LATIN)",
        errorMessage: data.error_message,
        text: data.raw_text || textToTest,
        cleanedText: data.cleaned_text || textToTest,
        label: data.label,
        confidence: data.confidence,
        probabilities: {
          pos: Math.round((data.probabilities?.Positive || 0) * 100),
          neg: Math.round((data.probabilities?.Negative || 0) * 100),
          neu: Math.round((data.probabilities?.Neutral || 0) * 100),
        },
        translation: data.translated_text || "No translation required (Direct semantic match).",
        isMixed: Boolean(data.is_mixed_sentiment),
        spans: data.conflicting_spans || [],
        tokens: data.token_breakdown || [],
        latency: data.latency_ms || 45
      });

    } catch (err) {
      console.error("API Call Failed:", err);
      setApiError(`Could not reach backend at http://127.0.0.1:8000 (${err.message}). Ensure uvicorn is running.`);
      setResult(null);
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div style={{ maxWidth: '880px', margin: '0 auto' }}>
      {/* Input Deck */}
      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div className="card-title">Single-Comment Neural Sandbox</div>
            <div className="card-subtitle">Input any arbitrary code-mixed comment to evaluate live MuRIL inference & translation</div>
          </div>
          <span style={{ fontSize: '0.6875rem', fontFamily: 'var(--font-mono)', color: 'var(--text-subtle)' }}>
            Chars: {inputText.length}
          </span>
        </div>

        <textarea
          className="textarea-box"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type any Malayalam or Manglish text (e.g., vere nthaalla, ennik ishtam ayila, etc.)..."
          style={{ minHeight: '95px' }}
        />

        {/* Action Bar */}
        <div style={{ marginTop: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--text-subtle)', marginRight: '0.2rem' }}>
              PRESETS:
            </span>
            {samplePresets.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInputText(preset);
                  handlePredict(preset);
                }}
                style={{
                  border: '1px solid var(--border-color)',
                  background: 'var(--bg-subtle)',
                  borderRadius: '5px',
                  padding: '0.25rem 0.5rem',
                  fontSize: '0.6875rem',
                  cursor: 'pointer',
                  color: 'var(--text-muted)'
                }}
              >
                {preset.length > 22 ? preset.substring(0, 22) + '…' : preset}
              </button>
            ))}
          </div>

          <button
            className="btn btn-primary"
            onClick={() => handlePredict()}
            disabled={isEvaluating}
            style={{ padding: '0.55rem 1.25rem', fontSize: '0.8125rem' }}
          >
            {isEvaluating ? 'Evaluating Live…' : 'Run Predict →'}
          </button>
        </div>
      </div>

      {/* Connection Error Message if backend unreachable */}
      {apiError && (
        <div className="card" style={{ backgroundColor: 'var(--neg-bg)', borderColor: 'var(--neg-border)', color: '#991b1b' }}>
          <div style={{ fontWeight: '700', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Backend Connection Error</div>
          <div style={{ fontSize: '0.8125rem' }}>{apiError}</div>
        </div>
      )}

      {/* Result Deck */}
      {result && (
        <div style={{ marginTop: '1.25rem' }}>
          {!result.isSupported ? (
            <div className="card" style={{ backgroundColor: 'var(--neg-bg)', borderColor: 'var(--neg-border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <span className="badge badge-neg">GUARDRAIL BLOCKED</span>
                <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--neg-color)' }}>
                  {result.languageType}
                </span>
              </div>
              <p style={{ fontSize: '0.875rem', color: '#991b1b', lineHeight: 1.5 }}>
                {result.errorMessage}
              </p>
            </div>
          ) : (
            <div className="card">
              {/* Header Status */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span className={`badge ${
                    result.label === 'Positive' ? 'badge-pos' : 
                    result.label === 'Negative' ? 'badge-neg' : 
                    result.label === 'Mixed' ? 'badge-slate' : 'badge-neu'
                  }`}>
                    {result.label}
                  </span>
                  <span style={{ fontSize: '1.75rem', fontWeight: '800', fontFamily: 'var(--font-mono)', color: 'var(--text-main)' }}>
                    {result.confidence}%
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span className="badge badge-slate">{result.languageType}</span>
                  <span style={{ fontSize: '0.6875rem', fontFamily: 'var(--font-mono)', color: 'var(--text-subtle)' }}>
                    {result.latency} ms
                  </span>
                </div>
              </div>

              {/* Polarity Distribution */}
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono)',
                  marginBottom: '0.4rem',
                  fontWeight: '600'
                }}>
                  <span style={{ color: 'var(--pos-color)' }}>Positive: {result.probabilities.pos}%</span>
                  <span style={{ color: 'var(--neg-color)' }}>Negative: {result.probabilities.neg}%</span>
                  <span style={{ color: 'var(--neu-color)' }}>Neutral: {result.probabilities.neu}%</span>
                </div>
                <div className="progress-track" style={{ height: '10px' }}>
                  <div className="progress-fill-pos" style={{ width: `${result.probabilities.pos}%` }} />
                  <div className="progress-fill-neg" style={{ width: `${result.probabilities.neg}%` }} />
                  <div className="progress-fill-neu" style={{ width: `${result.probabilities.neu}%` }} />
                </div>
              </div>

              {/* Dual-Span Conflict View */}
              {result.isMixed && result.spans.length > 0 && (
                <div style={{
                  backgroundColor: 'var(--bg-subtle)',
                  padding: '1rem',
                  borderRadius: '8px',
                  marginBottom: '1.25rem',
                  border: '1px solid var(--border-color)'
                }}>
                  <div style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--text-subtle)', marginBottom: '0.5rem', fontFamily: 'var(--font-mono)' }}>
                    DUAL-SPAN CLAUSE EXTRACTION
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                    {result.spans.map((s, idx) => (
                      <div key={idx} style={{ background: '#fff', padding: '0.65rem 0.85rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                        <div style={{ fontSize: '0.8125rem', fontWeight: '600', color: 'var(--text-main)' }}>"{s.span_text || s.text}"</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.35rem', fontSize: '0.6875rem' }}>
                          <span className={s.label === 'Positive' ? 'badge badge-pos' : 'badge badge-neg'}>{s.label}</span>
                          <span style={{ fontFamily: 'var(--font-mono)', fontWeight: '700' }}>{s.score}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Semantic English Translation */}
              <div style={{
                backgroundColor: 'var(--bg-subtle)',
                padding: '1rem 1.25rem',
                borderRadius: '8px',
                border: '1px solid var(--border-color)'
              }}>
                <div style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--text-subtle)', marginBottom: '0.3rem', fontFamily: 'var(--font-mono)' }}>
                  SEMANTIC ENGLISH TRANSLATION
                </div>
                <div style={{ fontSize: '0.95rem', fontStyle: 'italic', color: 'var(--text-main)', fontWeight: '500' }}>
                  "{result.translation}"
                </div>
              </div>

              {/* Linguistic Token Badges */}
              {result.tokens && result.tokens.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <div style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--text-subtle)', marginBottom: '0.35rem', fontFamily: 'var(--font-mono)' }}>
                    TOKEN LINGUISTIC CLASSIFICATION
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {result.tokens.map((tok, i) => (
                      <span key={i} style={{
                        fontSize: '0.6875rem',
                        padding: '0.2rem 0.45rem',
                        backgroundColor: '#fff',
                        borderRadius: '4px',
                        border: '1px solid var(--border-color)',
                        fontFamily: 'var(--font-mono)'
                      }}>
                        {tok.token} <strong style={{ color: 'var(--primary)', fontSize: '0.625rem' }}>{tok.type}</strong>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}