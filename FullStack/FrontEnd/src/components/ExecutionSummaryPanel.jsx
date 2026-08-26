import React from 'react';

export default function ExecutionSummaryPanel({ trace }) {
  return (
    <div className="bg-[#111827]/80 border border-gray-800/80 rounded-xl p-3.5 flex flex-col min-h-0">
      <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-1">Execution Summary</h3>
      <div className="flex-1 bg-[#070b12] border border-gray-800/80 rounded-lg p-2.5 font-mono text-[11px] text-emerald-400 overflow-auto">
        <pre>{JSON.stringify(trace, null, 2)}</pre>
      </div>
    </div>
  );
}