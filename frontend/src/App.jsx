import React from 'react'
import { Sparkles, CheckCircle2 } from 'lucide-react'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full text-center shadow-2xl space-y-4">
        <div className="inline-flex p-3 rounded-full bg-emerald-500/10 text-emerald-400">
          <Sparkles className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Kollamo.ai</h1>
        <p className="text-slate-400 text-sm">
          Frontend client initialized with React, Vite & Tailwind CSS.
        </p>
        <div className="flex items-center justify-center gap-2 text-emerald-400 font-medium text-sm pt-4 border-t border-slate-800">
          <CheckCircle2 className="w-4 h-4" />
          <span>Milestone 5 Ready</span>
        </div>
      </div>
    </div>
  )
}