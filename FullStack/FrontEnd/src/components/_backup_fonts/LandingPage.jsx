import React from 'react';
import { useNavigate } from 'react-router-dom';
import InteractiveStarfield from './InteractiveStarfield';
import kaizenLogo from '../assets/KAIZEN.png';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="relative w-full h-screen bg-[#070b12] flex flex-col items-center justify-center overflow-hidden">
      {/* Dynamic Cursor Canvas */}
      <InteractiveStarfield />

      {/* Top Navigation Bar */}
      <div className="absolute top-6 left-6 right-6 z-10 flex items-center justify-between pointer-events-none">
        <div className="flex items-center space-x-3 px-4 py-2 rounded-full bg-[#0b1325]/80 border border-cyan-900/50 backdrop-blur-md shadow-[0_0_20px_rgba(0,0,0,0.5)] pointer-events-auto">
          <img src={kaizenLogo} alt="Team Kaizen Logo" className="h-6 w-auto object-contain brightness-105" />
          <span className="text-xs font-mono font-bold tracking-widest text-cyan-300 uppercase">Team Kaizen</span>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-[#0b1325]/70 border border-cyan-900/40 backdrop-blur-md pointer-events-auto">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]"></span>
          <span className="text-[11px] font-mono text-emerald-400 tracking-wider">System Ready</span>
        </div>
      </div>

      {/* Foreground Content */}
      <div className="z-10 flex flex-col items-center space-y-7 px-4 text-center">
        
        {/* Prominent Center Team Kaizen Logo & Mission Badge */}
        <div className="flex flex-col items-center space-y-3">
          <div className="relative group">
            {/* Ambient Background Glow */}
            <div className="absolute -inset-2 bg-gradient-to-r from-cyan-500/30 via-blue-500/25 to-teal-400/30 rounded-3xl blur-xl opacity-70 group-hover:opacity-100 transition-all duration-500"></div>
            
            {/* Logo Container */}
            <div className="relative px-6 py-4 rounded-3xl bg-[#0b1325]/85 border border-cyan-500/40 backdrop-blur-xl shadow-[0_0_35px_rgba(34,211,238,0.25)] flex items-center justify-center transition-transform duration-300 group-hover:scale-105">
              <img 
                src={kaizenLogo} 
                alt="Team Kaizen Logo" 
                className="h-16 sm:h-20 md:h-24 w-auto object-contain brightness-110 drop-shadow-[0_0_15px_rgba(34,211,238,0.4)]" 
              />
            </div>
          </div>

          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-cyan-950/50 border border-cyan-500/30 backdrop-blur-md shadow-[0_0_15px_rgba(34,211,238,0.15)]">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="text-[11px] font-mono tracking-widest uppercase text-cyan-300 font-semibold">Earth Observation AI System</span>
          </div>
        </div>

        <div className="space-y-4">
          <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight">
            SatQuery <span className="text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.6)]">AI</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl font-light">
            Autonomous Multimodal Remote Sensing & Earth Observation Intelligence
          </p>
        </div>

        <button 
          onClick={() => navigate('/dashboard')}
          className="group relative px-8 py-4 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-lg rounded-full shadow-[0_0_20px_rgba(34,211,238,0.4)] transition-all duration-300 hover:scale-105"
        >
          Initialize Agent
          <span className="absolute inset-0 rounded-full border border-cyan-300 opacity-0 group-hover:animate-ping"></span>
        </button>

      </div>

      {/* Subtle Footer */}
      <div className="absolute bottom-6 z-10 flex items-center space-x-2.5 opacity-70 hover:opacity-100 transition-opacity">
        <img src={kaizenLogo} alt="Team Kaizen Logo" className="h-4 w-auto object-contain" />
        <p className="text-sm text-gray-500 tracking-widest uppercase font-mono">
          Engineered by Team Kaizen
        </p>
      </div>
    </div>
  );
}