import React, { useState } from 'react';

export default function MapViewer({ file1, imageUrl, boundingBox }) {
  const displaySrc = imageUrl || (file1 ? URL.createObjectURL(file1) : null);

  // --- ZOOM & PAN ENGINE STATE ---
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Handle Scroll to Zoom
  const handleWheel = (e) => {
    const scaleAmount = -e.deltaY * 0.005;
    let newScale = scale + scaleAmount;
    newScale = Math.min(Math.max(0.5, newScale), 10);
    setScale(newScale);
  };

  // Button Zoom Handlers
  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.5, 10));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.5, 0.5));
  };

  // Handle Click to Pan
  const handleMouseDown = (e) => {
    if (e.button !== 0) return; 
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetView = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };

  return (
    <div className="h-full bg-[#0b1325]/60 backdrop-blur-xl border border-cyan-900/50 hover:border-cyan-500/50 transition-colors duration-500 rounded-2xl p-5 flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.8)] min-h-0">
      
      {/* Header with Zoom Controls (+, -, Reset) */}
      <div className="flex justify-between items-center mb-4 z-20 shrink-0">
        <h3 className="text-xs font-bold text-gray-300 tracking-widest uppercase flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,1)]"></span>
          Geospatial Map Viewer
        </h3>
        
        <div className="flex items-center gap-2">
          {displaySrc && (
            <div className="flex items-center bg-cyan-950/40 border border-cyan-800/50 rounded overflow-hidden">
              <button 
                onClick={handleZoomOut}
                title="Zoom Out"
                className="px-2 py-1 text-cyan-400 hover:text-white hover:bg-cyan-800/60 transition-colors font-mono font-bold text-xs border-r border-cyan-800/50"
              >
                -
              </button>
              <button 
                onClick={handleZoomIn}
                title="Zoom In"
                className="px-2 py-1 text-cyan-400 hover:text-white hover:bg-cyan-800/60 transition-colors font-mono font-bold text-xs border-r border-cyan-800/50"
              >
                +
              </button>
              <button 
                onClick={resetView}
                className="px-2 py-1 text-[9px] text-cyan-400 hover:text-white uppercase tracking-widest hover:bg-cyan-800/60 transition-colors"
              >
                Reset
              </button>
            </div>
          )}
          <span className="text-[10px] text-cyan-400 font-mono tracking-wider bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/20 shadow-inner">
            Viewport: EPSG:4326
          </span>
        </div>
      </div>

      {/* Interactive Map Grid Container */}
      <div 
        className="flex-1 rounded-xl border border-cyan-900/30 relative overflow-hidden bg-[linear-gradient(to_right,#06b6d415_1px,transparent_1px),linear-gradient(to_bottom,#06b6d415_1px,transparent_1px)] bg-[size:24px_24px] shadow-inner"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {displaySrc ? (
          <div 
            className={`relative w-full h-full flex items-center justify-center z-10 transition-transform duration-75 ease-out ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
            style={{
              transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
              transformOrigin: 'center center'
            }}
          >
            <div className="relative inline-block max-h-full max-w-full p-2">
              <img 
                src={displaySrc} 
                alt="Satellite Scene" 
                draggable="false" 
                className="max-h-full max-w-full object-contain rounded-lg shadow-2xl ring-1 ring-white/10 select-none" 
              />
              
              {boundingBox && boundingBox.length === 4 && (
                <div 
                  className="absolute border-2 border-cyan-400 bg-cyan-400/10 rounded pointer-events-none transition-all duration-700 shadow-[0_0_20px_rgba(34,211,238,0.4)]"
                  style={{
                    top: `calc(${(boundingBox[0] / 1000) * 100}% + 8px)`, 
                    left: `calc(${(boundingBox[1] / 1000) * 100}% + 8px)`,
                    height: `${((boundingBox[2] - boundingBox[0]) / 1000) * 100}%`,
                    width: `${((boundingBox[3] - boundingBox[1]) / 1000) * 100}%`,
                  }}
                >
                  <span className="absolute -top-6 left-0 bg-cyan-400 text-black text-[10px] font-bold px-2 py-0.5 rounded-sm tracking-wider uppercase shadow-[0_0_10px_rgba(34,211,238,0.8)] whitespace-nowrap">
                    Target Detected
                  </span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 z-10 pointer-events-none">
            <svg className="w-12 h-12 mb-3 opacity-30 drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <p className="text-sm font-medium tracking-widest text-gray-400 uppercase">Awaiting Telemetry</p>
            <p className="text-[11px] mt-2 font-light text-gray-600 tracking-wide">Upload GeoTIFF to render Earth Observation imagery</p>
          </div>
        )}
      </div>
    </div>
  );
}