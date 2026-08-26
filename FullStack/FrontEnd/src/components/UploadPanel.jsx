import React from 'react';

export default function UploadPanel({ file1, setFile1, file2, setFile2 }) {
  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      if (!file1) {
        setFile1(e.dataTransfer.files[0]);
      } else {
        setFile2(e.dataTransfer.files[0]);
      }
    }
  };

  return (
    <div className="bg-[#111827]/80 border border-gray-800/80 rounded-xl p-3.5 flex flex-col justify-between">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-xs font-semibold text-gray-300 tracking-wide uppercase">Upload Panel</h3>
        <span className="text-[10px] text-gray-500 font-mono">GeoTIFF / TIFF / PNG</span>
      </div>

      <div 
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className="border border-dashed border-gray-700 hover:border-cyan-500/50 rounded-lg p-3 text-center transition bg-[#161f30]/40 flex flex-col items-center justify-center relative cursor-pointer"
      >
        <input 
          type="file" 
          accept=".tif,.tiff,.png,.jpg,.jpeg" 
          onChange={(e) => {
            if (e.target.files[0]) {
              if (!file1) setFile1(e.target.files[0]);
              else setFile2(e.target.files[0]);
            }
          }}
          className="absolute inset-0 opacity-0 cursor-pointer" 
        />
        <p className="text-xs text-gray-300 font-medium">
          {file1 ? `Primary: ${file1.name}` : "Drop GeoTIFF / TIFF files here"}
        </p>
        {file2 && (
          <p className="text-[11px] text-cyan-400 mt-1 truncate max-w-full">
            Secondary: {file2.name}
          </p>
        )}
      </div>

      {(file1 || file2) && (
        <div className="flex justify-end mt-2">
          <button 
            onClick={() => { setFile1(null); setFile2(null); }}
            className="text-[10px] text-red-400 hover:underline"
          >
            Clear Uploads
          </button>
        </div>
      )}
    </div>
  );
}