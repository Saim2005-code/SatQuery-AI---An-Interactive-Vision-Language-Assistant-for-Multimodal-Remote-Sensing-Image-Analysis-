import React from 'react';

export default function Header() {
  return (
    <header className="min-h-[60px] py-3.5 px-5 flex items-center justify-between border border-cyan-900/50 shrink-0 bg-[#0b1325]/80 backdrop-blur-xl rounded-2xl shadow-[0_0_20px_rgba(0,0,0,0.5)]">
      <div className="flex items-center space-x-3">
        <span className="font-extrabold text-sm tracking-widest text-white uppercase mt-0.5">
          SatQuery <span className="text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]">AI</span>
        </span>
        <span className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">| Earth Observation Intelligence System</span>
      </div>
      <div className="flex items-center space-x-3 mt-1">
        <span className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Team Kaizen</span>
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]"></span>
        <span className="text-[10px] font-mono text-emerald-400 tracking-wider">FastAPI Connected</span>
      </div>
    </header>
  );
}