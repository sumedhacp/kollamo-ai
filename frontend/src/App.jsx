// src/App.jsx
import React, { useState } from 'react';
import Navbar from './components/Navbar';
import OverviewTab from './components/OverviewTab';
import SandboxTab from './components/SandboxTab';
import SocialStudioTab from './components/SocialStudioTab';
import AnalyticsTab from './components/AnalyticsTab';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Real analyzed comments returned by the backend
  const [analyzedBatch, setAnalyzedBatch] = useState([]);
  
  // Real executive summary & global sentiment metrics
  const [batchMetrics, setBatchMetrics] = useState(null);
  
  // Loading & error state during batch processing
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState('');

  // Primary Batch Pipeline: Sends scraped comments to backend /api/analyze-batch
  const handleRunBatchInference = async (selectedComments) => {
    if (!selectedComments || selectedComments.length === 0) {
      alert("No comments selected for analysis.");
      return;
    }

    setIsAnalyzing(true);
    setAnalyzeError('');

    try {
      // 1. Structure payload exactly matching BatchAnalyzeRequest schema
      const payload = {
        comments: selectedComments.map((c, idx) => ({
          comment_id: String(c.id || `c_${idx}`),
          text: String(c.text || c.comment_payload || ''),
          author: String(c.author || '@anonymous'),
          like_count: Number(c.likes || c.like_count || 0),
          published_at: String(c.date || c.published_at || 'Recent')
        }))
      };

      // 2. Call FastAPI Batch Inference Endpoint
      const response = await fetch('http://127.0.0.1:8000/api/analyze-batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errDetail = await response.json().catch(() => ({}));
        throw new Error(errDetail.detail || `Server returned HTTP ${response.status}`);
      }

      const data = await response.json();

      // 3. Format backend AnalyzedCommentItem records into state
      const processedItems = data.comments.map((item) => ({
        id: item.comment_id,
        author: item.author,
        text: item.comment,
        cleaned_text: item.cleaned_comment,
        translation: item.translated_text || item.comment, // Dynamic individual translation
        sentiment: String(item.label).toUpperCase(),        // POSITIVE, NEGATIVE, NEUTRAL, MIXED
        confidence: Math.round(item.confidence),
        probabilities: item.probabilities,
        likes: item.like_count,
        date: item.published_at,
        is_supported: item.is_supported,
        language_type: item.language_type,
        tokens: item.token_breakdown
      }));

      setAnalyzedBatch(processedItems);

      // 4. Update macro distribution & telemetry
      setBatchMetrics({
        total: data.total_analyzed,
        supported: data.supported_count,
        unsupported: data.unsupported_count,
        distribution: data.sentiment_distribution,
        percentages: data.sentiment_percentages,
        nss: data.net_sentiment_score
      });

      // 5. Navigate to Analytics Tab
      setActiveTab('analytics');

    } catch (err) {
      console.error("Batch Analysis Execution Failed:", err);
      setAnalyzeError(err.message || "Failed to process batch analysis.");
      alert(`Batch Inference Error: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="app-container">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'overview' && (
          <OverviewTab setActiveTab={setActiveTab} />
        )}

        {activeTab === 'sandbox' && (
          <SandboxTab />
        )}

        {activeTab === 'studio' && (
          <SocialStudioTab 
            onAnalyze={handleRunBatchInference} 
            setActiveTab={setActiveTab} 
            isAnalyzing={isAnalyzing}
          />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsTab 
            data={analyzedBatch} 
            metrics={batchMetrics} 
            setActiveTab={setActiveTab} 
          />
        )}
      </main>

      <footer style={{
        borderTop: '1px solid var(--border-color)',
        backgroundColor: 'var(--bg-surface)',
        padding: '1.5rem 1.5rem',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: 'var(--text-subtle)'
      }}>
        <div style={{ fontWeight: '600', color: 'var(--text-main)' }}>
          Kollamo.ai v1.0 • Multilingual Social Intelligence Platform
        </div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.6875rem', marginTop: '0.35rem', color: 'var(--text-subtle)' }}>
          Calibrated Transformer Inference Engine for Code-Mixed Dravidian Dialects
        </div>
      </footer>
    </div>
  );
}