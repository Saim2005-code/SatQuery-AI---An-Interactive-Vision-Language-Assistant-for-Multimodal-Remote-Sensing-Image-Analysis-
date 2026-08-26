import React, { useRef, useEffect } from 'react';

export default function ChatPanel({ query, setQuery, chatHistory, onSubmit, isLoading }) {
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="bg-[#111827]/80 border border-gray-800/80 rounded-xl p-3.5 flex-1 flex flex-col min-h-0">
      <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wide mb-2">Query & Chat Panel</h3>
      
      {/* Dynamic Messages Container */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1 text-xs">
        {chatHistory.map((msg, index) => (
          <div 
            key={index} 
            className={`p-2.5 rounded-lg border ${
              msg.role === 'user' 
                ? 'bg-[#1e293b]/70 border-gray-700/60 text-gray-200' 
                : 'bg-[#064e3b]/30 border-emerald-500/30 text-emerald-200'
            }`}
          >
            <span className="text-[10px] font-bold block mb-1 uppercase tracking-wider text-gray-400">
              {msg.role === 'user' ? 'User Query' : 'SatQuery AI Response'}
            </span>
            <p className="leading-relaxed text-[11px]">{msg.text}</p>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input Bar */}
      <div className="flex gap-2 mt-3 pt-2 border-t border-gray-800/60">
        <input 
          type="text" 
          placeholder="e.g. what has changed"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          className="flex-1 bg-[#161f30] border border-gray-700/60 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-500 outline-none focus:border-cyan-500 transition"
        />
        <button 
          onClick={onSubmit}
          disabled={isLoading}
          className={`px-4 py-2 rounded-lg text-xs font-semibold tracking-wide transition ${
            isLoading 
              ? 'bg-cyan-800 text-gray-300 cursor-not-allowed animate-pulse' 
              : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-600/20'
          }`}
        >
          {isLoading ? "Analyzing..." : "Send"}
        </button>
      </div>
    </div>
  );
}