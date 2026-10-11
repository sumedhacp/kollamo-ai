// src/components/OverviewTab.jsx
import React from 'react';

export default function OverviewTab({ setActiveTab }) {
  const kpiStats = [
    { label: "MODEL ACCURACY", value: "92.4%", sub: "Macro F1 across benchmark" },
    { label: "INFERENCE SPEED", value: "< 95 ms", sub: "PyTorch sequence classification" },
    { label: "VOCABULARY ROBUSTNESS", value: "24,000+", sub: "Slang & colloquial Manglish roots" },
    { label: "LANGUAGE GUARDRAIL", value: "100%", sub: "Zero leak for unsupported scripts" }
  ];

  const pillarCards = [
    {
      badge: "PROBLEM & CAPABILITY",
      badgeColor: "#2563eb",
      badgeBg: "#eff6ff",
      title: "Decoding Informal Romanized Manglish",
      description: "Over 80% of South Asian social media users express opinions in native languages using Latin phonetics ('Manglish'). Kollamo.ai resolves arbitrary character elongations ('pwoliii', 'kidilammm'), regional slang, and code-mixing that break traditional NLP platforms."
    },
    {
      badge: "NEURAL CORE",
      badgeColor: "#059669",
      badgeBg: "#ecfdf5",
      title: "Calibrated MuRIL Transformer Architecture",
      description: "Powered by Google's Multilingual Representations for Indian Languages (MuRIL), fine-tuned with calibrated inverse priors. Dynamically scores multi-class probability splits and flags dual-span mixed polarity clauses (e.g., contrasting a strong first half with a weak second half)."
    },
    {
      badge: "ACTIONABLE TELEMETRY",
      badgeColor: "#7c3aed",
      badgeBg: "#f5f3ff",
      title: "Live Social Stream Audience Analytics",
      description: "Streamlined comment extraction for YouTube and Instagram. Eliminates DOM noise, UI buttons, and timestamps to yield high-fidelity sentiment splits, Net Sentiment Scores (NSS), and automated English semantic glossing for non-native brand analysts."
    }
  ];

  const pipelineStages = [
    {
      num: "01",
      title: "Social Ingestion",
      desc: "Live stream extraction from YouTube Data API v3 and Instagram Reels with DOM UI stripping."
    },
    {
      num: "02",
      title: "Language Guardrail",
      desc: "Fast Unicode script boundary checks to filter out non-target Indic languages (e.g., Hindi, Tamil)."
    },
    {
      num: "03",
      title: "Phonetic Normalization",
      desc: "Collapses arbitrary character repeats ('supeeer') and normalizes regional digraphs (pw/th/zh)."
    },
    {
      num: "04",
      title: "Transformer Inference",
      desc: "Subword-level MuRIL classification with continuous probability distribution & mixed-clause split."
    },
    {
      num: "05",
      title: "Executive Synthesis",
      desc: "Computes Net Sentiment Score (NSS), key discussion themes, and accurate English paraphrasing."
    }
  ];

  return (
    <div style={{ maxWidth: '1240px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Hero Showcase Card */}
      <div className="card" style={{
        background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
        border: '1px solid var(--border-color)',
        padding: '3rem 2.5rem',
        borderRadius: '16px',
        boxShadow: '0 4px 20px -4px rgba(15, 23, 42, 0.05)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ maxWidth: '820px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            backgroundColor: '#eff6ff',
            color: '#1d4ed8',
            fontSize: '0.75rem',
            fontWeight: '700',
            fontFamily: 'var(--font-mono)',
            padding: '0.3rem 0.75rem',
            borderRadius: '9999px',
            marginBottom: '1rem',
            border: '1px solid #bfdbfe'
          }}>
            <span>NEXT-GEN INDIC LANGUAGE AI</span>
            <span>•</span>
            <span>v1.0 PRODUCTION READY</span>
          </div>

          <h1 style={{
            fontSize: '2.5rem',
            fontWeight: '800',
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
            color: 'var(--text-main)',
            marginBottom: '1rem'
          }}>
            Intelligent Sentiment Analytics for <span style={{ color: 'var(--primary)' }}>Code-Mixed Manglish</span>
          </h1>

          <p style={{
            color: 'var(--text-muted)',
            fontSize: '1.0625rem',
            lineHeight: 1.6,
            marginBottom: '2rem'
          }}>
            Kollamo.ai is a specialized natural language intelligence platform engineered to interpret Romanized Malayalam-English social discourse. We transform unstandardized social comments from YouTube and Instagram into real-time audience metrics, Net Sentiment Scores, and clear English translations.
          </p>

          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={() => setActiveTab('sandbox')} style={{ padding: '0.65rem 1.35rem', fontSize: '0.875rem' }}>
              Launch Interactive Sandbox →
            </button>
            <button className="btn btn-secondary" onClick={() => setActiveTab('studio')} style={{ padding: '0.65rem 1.35rem', fontSize: '0.875rem' }}>
              Connect Social Feeds
            </button>
            <button className="btn btn-secondary" onClick={() => setActiveTab('analytics')} style={{ padding: '0.65rem 1.35rem', fontSize: '0.875rem' }}>
              View Analytics Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* KPI Highlights Bar */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1rem'
      }}>
        {kpiStats.map((k, i) => (
          <div key={i} className="card" style={{ marginBottom: 0, padding: '1.25rem' }}>
            <div style={{ fontSize: '0.6875rem', fontWeight: '700', color: 'var(--text-subtle)', fontFamily: 'var(--font-mono)' }}>
              {k.label}
            </div>
            <div style={{ fontSize: '1.875rem', fontWeight: '800', color: 'var(--text-main)', margin: '0.25rem 0' }}>
              {k.value}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
              {k.sub}
            </div>
          </div>
        ))}
      </div>

      {/* 3 Core Value Pillars */}
      <div>
        <div style={{ marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1.35rem', fontWeight: '800', letterSpacing: '-0.02em' }}>Platform Core Capabilities</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-subtle)' }}>Built from the ground up to solve informal Dravidian language processing challenges</p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.25rem'
        }}>
          {pillarCards.map((p, i) => (
            <div key={i} className="card" style={{
              marginBottom: 0,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              padding: '1.75rem',
              borderRadius: '14px'
            }}>
              <div>
                <span style={{
                  display: 'inline-block',
                  backgroundColor: p.badgeBg,
                  color: p.badgeColor,
                  fontSize: '0.6875rem',
                  fontWeight: '700',
                  fontFamily: 'var(--font-mono)',
                  padding: '0.25rem 0.6rem',
                  borderRadius: '6px',
                  marginBottom: '1rem'
                }}>
                  {p.badge}
                </span>
                <h3 style={{ fontSize: '1.15rem', fontWeight: '750', marginBottom: '0.65rem', lineHeight: 1.3 }}>
                  {p.title}
                </h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                  {p.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5-Stage Processing Lifecycle */}
      <div className="card" style={{ padding: '2rem' }}>
        <div className="card-header" style={{ marginBottom: '1.75rem' }}>
          <div className="card-title" style={{ fontSize: '1.25rem' }}>End-to-End Processing Architecture</div>
          <div className="card-subtitle" style={{ fontSize: '0.875rem' }}>
            The autonomous transformation pipeline executed from unstructured social commentary to executive intelligence
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem'
        }}>
          {pipelineStages.map((stage, i) => (
            <div key={i} style={{
              backgroundColor: 'var(--bg-subtle)',
              border: '1px solid var(--border-color)',
              borderRadius: '10px',
              padding: '1.25rem',
              position: 'relative'
            }}>
              <div style={{
                fontSize: '0.75rem',
                fontWeight: '800',
                fontFamily: 'var(--font-mono)',
                color: 'var(--primary)',
                marginBottom: '0.5rem'
              }}>
                STAGE {stage.num}
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: '750', color: 'var(--text-main)', marginBottom: '0.4rem' }}>
                {stage.title}
              </div>
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                {stage.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}