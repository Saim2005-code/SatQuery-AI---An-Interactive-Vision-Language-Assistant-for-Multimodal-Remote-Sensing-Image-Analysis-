import React from 'react';
import { useNavigate } from 'react-router-dom';
import InteractiveStarfield from './InteractiveStarfield';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="relative w-full h-screen bg-[#070b12] flex flex-col items-center justify-center overflow-hidden">
      {/* Dynamic Cursor Canvas */}
      <InteractiveStarfield />

      {/* Foreground Content */}
      <div className="z-10 flex flex-col items-center space-y-8 px-4 text-center">
        
        <div className="space-y-4">
          <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight">
            SatQuery <span className="text-cyan-400">AI</span>
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
      <div className="absolute bottom-6 z-10">
        <p className="text-xs text-gray-600 tracking-widest uppercase font-mono">
          Engineered by Team Kaizen
        </p>
      </div>
    </div>
  );
}