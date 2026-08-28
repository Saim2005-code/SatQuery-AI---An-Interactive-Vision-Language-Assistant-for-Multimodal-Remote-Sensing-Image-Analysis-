import React from 'react';

export default function ExecutionSummaryPanel({ trace }) {
  return (
    <div className="h-full bg-[#0b1325]/60 backdrop-blur-xl border border-cyan-900/50 hover:border-cyan-500/50 transition-colors duration-500 rounded-2xl p-5 flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.8)] min-h-0">
      <h3 className="text-xs font-bold text-gray-300 uppercase tracking-widest mb-3 shrink-0">Execution Payload</h3>
      
      <div className="flex-1 bg-black/50 border border-white/5 shadow-inner rounded-xl p-3 font-mono text-[10px] text-emerald-400/90 overflow-y-auto scrollbar-thin scrollbar-thumb-cyan-900/50 min-h-0">
        <pre className="drop-shadow-[0_0_8px_rgba(52,211,153,0.2)]">{JSON.stringify(trace, null, 2)}</pre>
      </div>
    </div>
  );
}