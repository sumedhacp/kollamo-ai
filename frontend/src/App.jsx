import React, { useState } from 'react';
import { Sparkles, MessageSquareCode } from 'lucide-react';
import Zone1Sandbox from './components/Zone1Sandbox';
import Zone2Extractor from './components/Zone2Extractor';
import Zone3Dashboard from './components/Zone3Dashboard';

export default function App() {
  const [batchTelemetry, setBatchTelemetry] = useState(null);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10 selection:bg-emerald-500 selection:text-black">
      {/* Global Navigation Header */}
      <header className="max-w-6xl mx-auto mb-10 flex flex-col items-center text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
          <MessageSquareCode className="w-3.5 h-3.5" />
          <span>Romanized Dravidian NLP Intelligence</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white flex items-center gap-3">
          <span>Kollamo.ai</span>
        </h1>
        <p className="text-slate-400 text-sm max-w-2xl">
          End-to-end sentiment classification dashboard for Malayalam-English (Manglish) social media text, powered by Google's MuRIL transformer architecture.
        </p>
      </header>

      {/* 3-Zone Interactive Workspace */}
      <main className="max-w-6xl mx-auto space-y-8">
        {/* ZONE 1: Direct Single-Text Sandbox */}
        <section>
          <Zone1Sandbox />
        </section>

        {/* ZONE 2: Social Media Link Ingestion & Auditor */}
        <section>
          <Zone2Extractor onBatchAnalyzed={(data) => setBatchTelemetry(data)} />
        </section>

        {/* ZONE 3: Visual Dashboard & Filtering Matrix */}
        <section>
          <Zone3Dashboard batchData={batchTelemetry} />
        </section>
      </main>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto mt-16 pt-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        Kollamo.ai &bull; Major Academic Project &bull; Federal Institute of Science and Technology (FISAT)
      </footer>
    </div>
  );
}