import React from 'react';

export default function UploadPanel({ file1, setFile1, file2, setFile2, analysisMode, setAnalysisMode }) {
  const isBitemporal = analysisMode === "bitemporal";

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      !file1 ? setFile1(e.dataTransfer.files[0]) : setFile2(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="bg-[#0b1325]/60 backdrop-blur-xl border border-cyan-900/50 hover:border-cyan-500/50 transition-colors duration-500 rounded-2xl p-4 flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.8)]">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-bold text-gray-300 tracking-widest uppercase">Upload Panel</h3>
        <span className="text-[11px] text-gray-500 font-mono tracking-widest uppercase">GeoTIFF / TIFF / PNG</span>
      </div>

      {/* ── Analysis Mode Toggle ── */}
      <div className="flex items-center gap-1 mb-3 bg-black/30 rounded-lg p-0.5 border border-white/5">
        <button
          onClick={() => { setAnalysisMode("single"); setFile2(null); }}
          className={`flex-1 text-[11px] font-bold uppercase tracking-widest py-1.5 rounded-md transition-all duration-300 ${
            !isBitemporal
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-[0_0_10px_rgba(34,211,238,0.15)]'
              : 'text-gray-500 hover:text-gray-300'
          }`}
        >
          🖼️ Single
        </button>
        <button
          onClick={() => setAnalysisMode("bitemporal")}
          className={`flex-1 text-[11px] font-bold uppercase tracking-widest py-1.5 rounded-md transition-all duration-300 ${
            isBitemporal
              ? 'bg-purple-500/20 text-purple-400 border border-purple-500/40 shadow-[0_0_10px_rgba(168,85,247,0.15)]'
              : 'text-gray-500 hover:text-gray-300'
          }`}
        >
          🕓 Bi-Temporal
        </button>
      </div>

      {!isBitemporal ? (
        /* ── Single Image Upload ── */
        <div 
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="group border border-dashed border-cyan-900/50 hover:border-cyan-400/50 rounded-xl py-3 px-2 text-center transition-all duration-300 bg-black/20 flex flex-col items-center justify-center relative cursor-pointer min-h-[64px] shadow-inner"
        >
          <input 
            type="file" 
            accept=".tif,.tiff,.png,.jpg,.jpeg" 
            onChange={(e) => {
              if (e.target.files[0]) setFile1(e.target.files[0]);
            }}
            className="absolute inset-0 opacity-0 cursor-pointer z-10" 
          />
          <p className="text-[13px] font-medium tracking-wide transition-colors duration-300 z-0">
            {file1 ? (
              <span className="text-cyan-50">
                <span className="text-cyan-500/70 mr-1">PRIMARY:</span> {file1.name}
              </span>
            ) : (
              <span className="text-gray-400 group-hover:text-cyan-400/80 drop-shadow-md">
                Drop GeoTIFF / TIFF files here
              </span>
            )}
          </p>
        </div>
      ) : (
        /* ── Bi-Temporal: Before + After Uploads ── */
        <div className="flex gap-2">
          {/* BEFORE slot */}
          <div className="flex-1 group border border-dashed border-cyan-900/50 hover:border-cyan-400/50 rounded-xl py-2.5 px-2 text-center transition-all duration-300 bg-black/20 flex flex-col items-center justify-center relative cursor-pointer min-h-[58px] shadow-inner">
            <input
              type="file"
              accept=".tif,.tiff,.png,.jpg,.jpeg"
              onChange={(e) => {
                if (e.target.files[0]) setFile1(e.target.files[0]);
              }}
              className="absolute inset-0 opacity-0 cursor-pointer z-10"
            />
            <span className="text-[9px] font-bold uppercase tracking-widest text-cyan-500/60 mb-1 z-0">Before</span>
            <p className="text-[11px] font-medium tracking-wide z-0 truncate max-w-full px-1">
              {file1 ? (
                <span className="text-cyan-50">{file1.name}</span>
              ) : (
                <span className="text-gray-500 group-hover:text-cyan-400/70">Upload .tif</span>
              )}
            </p>
          </div>

          {/* AFTER slot */}
          <div className="flex-1 group border border-dashed border-purple-900/50 hover:border-purple-400/50 rounded-xl py-2.5 px-2 text-center transition-all duration-300 bg-black/20 flex flex-col items-center justify-center relative cursor-pointer min-h-[58px] shadow-inner">
            <input
              type="file"
              accept=".tif,.tiff,.png,.jpg,.jpeg"
              onChange={(e) => {
                if (e.target.files[0]) setFile2(e.target.files[0]);
              }}
              className="absolute inset-0 opacity-0 cursor-pointer z-10"
            />
            <span className="text-[9px] font-bold uppercase tracking-widest text-purple-500/60 mb-1 z-0">After</span>
            <p className="text-[11px] font-medium tracking-wide z-0 truncate max-w-full px-1">
              {file2 ? (
                <span className="text-purple-50">{file2.name}</span>
              ) : (
                <span className="text-gray-500 group-hover:text-purple-400/70">Upload .tif</span>
              )}
            </p>
          </div>
        </div>
      )}

      {(file1 || file2) && (
        <div className="flex justify-end mt-2">
          <button 
            onClick={() => { setFile1(null); setFile2(null); }}
            className="text-[11px] text-red-400/70 hover:text-red-400 uppercase tracking-widest transition-colors duration-200 hover:drop-shadow-[0_0_5px_rgba(248,113,113,0.8)]"
          >
            Clear Uploads
          </button>
        </div>
      )}
    </div>
  );
}