import React from 'react';

export default function Header() {
  return (
    <header className="h-10 px-2 flex items-center justify-between border-b border-gray-800 shrink-0">
      <div className="flex items-center space-x-2">
        <span className="font-bold text-sm tracking-wide text-white">SatQuery <span className="text-cyan-400">AI</span></span>
        <span className="text-[10px] text-gray-500">| Earth Observation Intelligence System</span>
      </div>
      <div className="flex items-center space-x-2">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span className="text-[11px] font-mono text-emerald-400">FastAPI & Motor Connected</span>
      </div>
    </header>
  );
}