import React from 'react';

export default function AuditTracePanel({ trace }) {
  return (
    <div className="bg-[#111827]/80 border border-gray-800/80 rounded-xl p-3.5 space-y-1.5">
      <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-2">Auditable Execution Trace</h3>
      <div className="flex justify-between text-xs">
        <span className="text-gray-400 font-mono">Task:</span>
        <span className="text-gray-200 font-medium">{trace?.task || "Bi-Temporal Change"}</span>
      </div>
      <div className="flex justify-between text-xs">
        <span className="text-gray-400 font-mono">Tool:</span>
        <span className="text-cyan-400 font-mono">{trace?.tool || "Change-Adapter-v2"}</span>
      </div>
      <div className="flex justify-between text-xs">
        <span className="text-gray-400 font-mono">Execution Time:</span>
        <span className="text-emerald-400 font-mono">{trace?.time || "0.82s"}</span>
      </div>
    </div>
  );
}