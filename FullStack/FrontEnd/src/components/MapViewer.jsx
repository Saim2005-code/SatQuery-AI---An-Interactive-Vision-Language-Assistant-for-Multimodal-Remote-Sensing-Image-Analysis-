import React from 'react';

export default function MapViewer({ file1, imageUrl, boundingBox }) {
  // If we have a remote image URL from backend, use it. Otherwise, create a temporary preview from file1.
  const displaySrc = imageUrl || (file1 ? URL.createObjectURL(file1) : null);

  return (
    <div className="bg-[#111827]/80 border border-gray-800/80 rounded-xl h-full flex flex-col p-3 relative overflow-hidden">
      <div className="flex justify-between items-center mb-2 z-10">
        <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wide">Geospatial Map Viewer</h3>
        <span className="text-[10px] text-gray-500 font-mono">Viewport: EPSG:4326</span>
      </div>

      <div className="flex-1 bg-[#070b12] rounded-lg border border-gray-800 flex items-center justify-center relative overflow-hidden">
        {displaySrc ? (
          <div className="relative w-full h-full flex items-center justify-center p-2">
            <img 
              src={displaySrc} 
              alt="Satellite Scene" 
              className="max-h-full max-w-full object-contain rounded"
            />
            {/* Visual Vector Bounding Box Overlay (0-1000 normalized coordinate system) */}
            {boundingBox && boundingBox.length === 4 && (
              <div 
                className="absolute border-2 border-red-500 bg-red-500/20 rounded pointer-events-none transition-all duration-500"
                style={{
                  top: `${(boundingBox[0] / 1000) * 100}%`,
                  left: `${(boundingBox[1] / 1000) * 100}%`,
                  height: `${((boundingBox[2] - boundingBox[0]) / 1000) * 100}%`,
                  width: `${((boundingBox[3] - boundingBox[1]) / 1000) * 100}%`,
                }}
              >
                <span className="bg-red-600 text-white text-[9px] font-bold px-1 rounded-br">
                  Target Region
                </span>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center text-gray-600">
            <p className="text-sm font-medium">Map Viewer</p>
            <p className="text-[11px]">Upload an image to render Earth Observation imagery</p>
          </div>
        )}
      </div>
    </div>
  );
}