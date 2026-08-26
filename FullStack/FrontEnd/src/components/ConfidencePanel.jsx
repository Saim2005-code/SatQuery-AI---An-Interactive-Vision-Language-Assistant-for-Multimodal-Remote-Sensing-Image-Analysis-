import React from 'react';

export default function ConfidencePanel({ confidence, resolution, interactionId }) {
  const handleDownloadPDF = () => {
    if (!interactionId) {
      alert("Execute an AI query first to generate an auditable inspection report.");
      return;
    }
    window.open(`http://127.0.0.1:8000/api/v1/export-report/${interactionId}`, "_blank");
  };

  return (
    <div className="bg-[#111827]/80 border border-gray-800/80 rounded-xl p-3.5 flex flex-col justify-between">
      <div>
        <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-2">Confidence & Actions</h3>
        <div className="flex justify-between items-center py-1">
          <span className="text-xs text-gray-400">Confidence Score</span>
          <span className="text-xs font-bold font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            {confidence || "91.8%"}
          </span>
        </div>
        <div className="flex justify-between items-center py-1">
          <span className="text-xs text-gray-400">Resolution</span>
          <span className="text-xs font-mono text-gray-300">{resolution || "0.65m (Cartosat-2S)"}</span>
        </div>
      </div>

      <button 
        onClick={handleDownloadPDF}
        className="mt-3 w-full bg-cyan-700 hover:bg-cyan-600 text-white font-semibold py-2 rounded-lg text-xs shadow transition"
      >
        Download Inspection PDF Report
      </button>
    </div>
  );
}