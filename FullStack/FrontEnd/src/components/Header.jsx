import React from 'react';
import kaizenLogo from '../assets/KAIZEN.png';

export default function Header() {
  return (
    <header className="min-h-[60px] py-3.5 px-5 flex items-center justify-between border border-cyan-900/50 shrink-0 bg-[#0b1325]/80 backdrop-blur-xl rounded-2xl shadow-[0_0_20px_rgba(0,0,0,0.5)]">
      <div className="flex items-center space-x-3">
        <span className="font-extrabold text-base tracking-widest text-white uppercase mt-0.5">
          SatQuery <span className="text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]">AI</span>
        </span>
        <span className="text-xs text-gray-500 uppercase tracking-widest mt-1">| Earth Observation Intelligence System</span>
      </div>
      <div className="flex items-center space-x-2.5 mt-0.5">
        <img 
          src={kaizenLogo} 
          alt="Team Kaizen Logo" 
          className="h-5 w-auto object-contain brightness-95 hover:brightness-110 transition-all rounded-sm" 
        />
        <span className="text-xs text-gray-400 uppercase tracking-widest font-bold">Team Kaizen</span>
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" title="System Online"></span>
      </div>
    </header>
  );
}