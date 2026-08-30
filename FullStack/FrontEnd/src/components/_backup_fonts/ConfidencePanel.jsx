import React from 'react';

export default function ConfidencePanel({ confidence, resolution, interactionId }) {
  const handleDownloadPDF = () => {
    if (!interactionId) return alert("Execute an AI query first to generate report.");
    window.open(`http://127.0.0.1:8000/api/v1/export-report/${interactionId}`, "_blank");
  };

  return (
    <div className="h-full bg-[#0b1325]/60 backdrop-blur-xl border border-cyan-900/50 hover:border-cyan-500/50 transition-colors duration-500 rounded-2xl p-5 flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.8)] min-h-0">
      
      {/* Aligned Heading (mb-3 exactly matches the other panels) */}
      <h3 className="text-xs font-bold text-gray-300 uppercase tracking-widest mb-3 shrink-0">Telemetry & Actions</h3>
      
      <div className="flex-1 flex flex-col justify-between py-2 min-h-0">
        
        <div className="flex justify-between items-center border-b border-white/5 pb-2">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Confidence Score</span>
          <span className="text-[11px] font-bold font-mono text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-md border border-emerald-500/30 shadow-[0_0_10px_rgba(52,211,153,0.2)]">
            {confidence || "00.0%"}
          </span>
        </div>
        
        <div className="flex justify-between items-center pt-1">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Resolution Match</span>
          <span className="text-[10px] font-mono text-gray-300 tracking-wide text-right">
            {resolution || "PENDING"}
          </span>
        </div>
        
      </div>

      <button 
        onClick={handleDownloadPDF}
        className="mt-3 shrink-0 w-full bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 hover:border-cyan-400 font-bold py-2.5 rounded-xl text-[9px] tracking-widest uppercase transition-all duration-300 shadow-[0_0_15px_rgba(34,211,238,0.1)] hover:shadow-[0_0_20px_rgba(34,211,238,0.3)] backdrop-blur-sm"
      >
        Export PDF
      </button>
    </div>
  );
}