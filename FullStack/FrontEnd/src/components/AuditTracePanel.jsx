import React from 'react';

export default function AuditTracePanel({ trace }) {
  return (
    <div className="h-full bg-[#0b1325]/60 backdrop-blur-xl border border-cyan-900/50 hover:border-cyan-500/50 transition-colors duration-500 rounded-2xl p-5 flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.8)] min-h-0">
      
      {/* Updated to mb-3 for perfect alignment */}
      <h3 className="text-xs font-bold text-gray-300 uppercase tracking-widest mb-3 shrink-0">Auditable Trace</h3>
      
      <div className="flex-1 flex flex-col justify-between py-2 min-h-0">
        
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-[10px] text-gray-500 font-mono uppercase tracking-wider">Task</span>
          <span className="text-[11px] text-gray-200 font-medium tracking-wide drop-shadow-md truncate ml-2 text-right">
            {trace?.task || "STANDBY"}
          </span>
        </div>
        
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-[10px] text-gray-500 font-mono uppercase tracking-wider">Tool</span>
          <span className="text-[11px] text-cyan-400 font-mono tracking-wide drop-shadow-[0_0_5px_rgba(34,211,238,0.5)] truncate ml-2 text-right">
            {trace?.tool || "N/A"}
          </span>
        </div>
        
        <div className="flex justify-between items-center pt-1">
          <span className="text-[10px] text-gray-500 font-mono uppercase tracking-wider">Latency</span>
          <span className="text-[11px] text-emerald-400 font-mono tracking-wide drop-shadow-[0_0_5px_rgba(52,211,153,0.5)] text-right">
            {trace?.time || "0.00s"}
          </span>
        </div>

      </div>
    </div>
  );
}