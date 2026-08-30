import React, { useState, useEffect, useRef } from 'react';
import { fromBlob } from 'geotiff';

/**
 * Read a GeoTIFF File object, render the first image to an off-screen canvas,
 * and return a data-URL string that <img> can display.
 *
 * Supports:
 *  - 3+ band images  → uses bands 0, 1, 2 as RGB
 *  - 1 band (greyscale) → maps to R=G=B
 *  - Auto min/max contrast stretch per band
 */
async function geotiffToDataUrl(file) {
  const tiff = await fromBlob(file);
  const image = await tiff.getImage();
  const width = image.getWidth();
  const height = image.getHeight();
  const rasters = await image.readRasters();
  const numBands = rasters.length;

  // Helper – compute min/max for a typed-array band, ignoring NaN / noData
  const bandStats = (band) => {
    let min = Infinity;
    let max = -Infinity;
    for (let i = 0; i < band.length; i++) {
      const v = band[i];
      if (Number.isFinite(v)) {
        if (v < min) min = v;
        if (v > max) max = v;
      }
    }
    return { min, max };
  };

  // Pick band indices for RGB (fall back to greyscale)
  const bandIndices = numBands >= 3 ? [0, 1, 2] : [0, 0, 0];
  const bands = bandIndices.map((i) => rasters[i]);
  const stats = bands.map(bandStats);

  // Build RGBA ImageData
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  const imgData = ctx.createImageData(width, height);
  const data = imgData.data;

  for (let px = 0; px < width * height; px++) {
    for (let c = 0; c < 3; c++) {
      const { min, max } = stats[c];
      const range = max - min || 1;
      const raw = bands[c][px];
      const normalized = Number.isFinite(raw) ? ((raw - min) / range) * 255 : 0;
      data[px * 4 + c] = Math.round(Math.min(255, Math.max(0, normalized)));
    }
    data[px * 4 + 3] = 255; // alpha
  }

  ctx.putImageData(imgData, 0, 0);
  return canvas.toDataURL('image/png');
}

export default function MapViewer({ file1, imageUrl, boundingBox }) {
  const isLocalTiff =
    !imageUrl &&
    file1 &&
    (file1.name.toLowerCase().endsWith('.tif') ||
      file1.name.toLowerCase().endsWith('.tiff'));

  // State that holds the data-URL produced from a local GeoTIFF
  const [tiffDataUrl, setTiffDataUrl] = useState(null);
  const [tiffLoading, setTiffLoading] = useState(false);
  const [tiffError, setTiffError] = useState(null);
  const processedFileRef = useRef(null);

  // When a new TIFF file arrives, parse & render it
  useEffect(() => {
    if (!isLocalTiff) {
      // Not a local TIFF – clear any previous render
      setTiffDataUrl(null);
      setTiffLoading(false);
      setTiffError(null);
      processedFileRef.current = null;
      return;
    }

    // Avoid re-processing the same File object
    if (processedFileRef.current === file1) return;
    processedFileRef.current = file1;

    let cancelled = false;
    setTiffLoading(true);
    setTiffError(null);
    setTiffDataUrl(null);

    geotiffToDataUrl(file1)
      .then((url) => {
        if (!cancelled) {
          setTiffDataUrl(url);
          setTiffLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          console.error('GeoTIFF render error:', err);
          setTiffError(err.message || 'Failed to render GeoTIFF');
          setTiffLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [file1, isLocalTiff]);

  // Final display source: backend URL > rendered TIFF data-URL > non-TIFF ObjectURL
  const displaySrc =
    imageUrl ||
    tiffDataUrl ||
    (file1 && !isLocalTiff ? URL.createObjectURL(file1) : null);

  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleWheel = (e) => {
    const scaleAmount = -e.deltaY * 0.005;
    let newScale = scale + scaleAmount;
    newScale = Math.min(Math.max(0.5, newScale), 10);
    setScale(newScale);
  };

  const handleZoomIn = () => setScale((prev) => Math.min(prev + 0.5, 10));
  const handleZoomOut = () => setScale((prev) => Math.max(prev - 0.5, 0.5));

  const handleMouseDown = (e) => {
    if (e.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  };

  const handleMouseUp = () => setIsDragging(false);
  const resetView = () => { setScale(1); setPosition({ x: 0, y: 0 }); };

  // Determine whether to show the loading / error state for a local TIFF
  const showTiffProcessing = isLocalTiff && !tiffDataUrl;

  return (
    <div className="h-full bg-[#0b1325]/60 backdrop-blur-xl border border-cyan-900/50 hover:border-cyan-500/50 transition-colors duration-500 rounded-2xl p-5 flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.8)] min-h-0">
      
      <div className="flex justify-between items-center mb-4 z-20 shrink-0">
        <h3 className="text-xs font-bold text-gray-300 tracking-widest uppercase flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,1)]"></span>
          Geospatial Map Viewer
        </h3>
        
        <div className="flex items-center gap-2">
          {displaySrc && (
            <div className="flex items-center bg-cyan-950/40 border border-cyan-800/50 rounded overflow-hidden">
              <button onClick={handleZoomOut} className="px-2 py-1 text-cyan-400 hover:text-white hover:bg-cyan-800/60 transition-colors font-mono font-bold text-xs border-r border-cyan-800/50">-</button>
              <button onClick={handleZoomIn} className="px-2 py-1 text-cyan-400 hover:text-white hover:bg-cyan-800/60 transition-colors font-mono font-bold text-xs border-r border-cyan-800/50">+</button>
              <button onClick={resetView} className="px-2 py-1 text-[9px] text-cyan-400 hover:text-white uppercase tracking-widest hover:bg-cyan-800/60 transition-colors">Reset</button>
            </div>
          )}
          <span className="text-[10px] text-cyan-400 font-mono tracking-wider bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/20 shadow-inner">
            Viewport: EPSG:4326
          </span>
        </div>
      </div>

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
            style={{ transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`, transformOrigin: 'center center' }}
          >
            <div className="relative inline-block max-h-full max-w-full p-2">
              <img src={displaySrc} alt="Satellite Scene" draggable="false" className="max-h-full max-w-full object-contain rounded-lg shadow-2xl ring-1 ring-white/10 select-none" />
              
              {boundingBox && boundingBox.length === 4 && (
                <div 
                  className="absolute border-[1.5px] border-emerald-400 bg-emerald-400/10 pointer-events-none transition-all duration-700 shadow-[0_0_15px_rgba(52,211,153,0.3)] z-20"
                  style={{
                    top: `${(boundingBox[0] / 1000) * 100}%`, left: `${(boundingBox[1] / 1000) * 100}%`,
                    height: `${((boundingBox[2] - boundingBox[0]) / 1000) * 100}%`, width: `${((boundingBox[3] - boundingBox[1]) / 1000) * 100}%`,
                  }}
                >
                  <span className="absolute -top-6 left-[-1.5px] bg-emerald-400 text-black text-[9px] font-bold px-2 py-1 rounded-t-sm tracking-widest uppercase shadow-[0_0_10px_rgba(52,211,153,0.8)]">Target Acquired</span>
                  <div className="absolute top-0 left-0 w-2 h-2 border-t-[3px] border-l-[3px] border-white/80"></div>
                  <div className="absolute top-0 right-0 w-2 h-2 border-t-[3px] border-r-[3px] border-white/80"></div>
                  <div className="absolute bottom-0 left-0 w-2 h-2 border-b-[3px] border-l-[3px] border-white/80"></div>
                  <div className="absolute bottom-0 right-0 w-2 h-2 border-b-[3px] border-r-[3px] border-white/80"></div>
                </div>
              )}
            </div>
          </div>
        ) : showTiffProcessing ? (
          // --- GeoTIFF is being parsed / rendered ---
          <div className="absolute inset-0 flex flex-col items-center justify-center text-cyan-400 z-10 pointer-events-none bg-cyan-950/20 backdrop-blur-sm">
            {tiffLoading ? (
              <>
                <svg className="w-14 h-14 mb-4 opacity-80 drop-shadow-[0_0_15px_rgba(34,211,238,0.5)] animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
                <p className="text-sm font-bold tracking-widest uppercase drop-shadow-md">Rendering GeoTIFF…</p>
                <p className="text-[10px] mt-2 font-mono text-cyan-200/70 tracking-widest">Decoding spatial raster data</p>
              </>
            ) : tiffError ? (
              <>
                <svg className="w-14 h-14 mb-4 opacity-80 text-red-400 drop-shadow-[0_0_15px_rgba(248,113,113,0.5)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm font-bold tracking-widest uppercase text-red-400 drop-shadow-md">Render Failed</p>
                <p className="text-[10px] mt-2 font-mono text-red-300/70 tracking-widest max-w-[80%] text-center">{tiffError}</p>
              </>
            ) : null}
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