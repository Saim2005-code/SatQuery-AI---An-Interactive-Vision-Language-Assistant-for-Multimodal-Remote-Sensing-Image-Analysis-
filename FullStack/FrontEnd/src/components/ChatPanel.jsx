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
    <div className="h-full w-full bg-[#0b1325]/60 backdrop-blur-xl border border-cyan-900/50 hover:border-cyan-500/50 transition-colors duration-500 rounded-2xl p-5 flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.8)] min-h-0">
      <h3 className="text-xs font-bold text-gray-300 uppercase tracking-widest mb-4 shrink-0">Command Interface</h3>
      
      {/* Scrollable Chat Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-3 text-xs scrollbar-thin scrollbar-thumb-cyan-900/50 scrollbar-track-transparent min-h-0">
        {chatHistory.map((msg, index) => (
          <div 
            key={index} 
            className={`pl-4 border-l-2 transition-all duration-300 ${
              msg.role === 'user' 
                ? 'border-gray-500 text-gray-300' 
                : 'border-cyan-400 text-cyan-50 drop-shadow-[0_0_8px_rgba(34,211,238,0.2)]'
            }`}
          >
            <span className={`text-[9px] font-bold block mb-1.5 uppercase tracking-widest ${msg.role === 'user' ? 'text-gray-500' : 'text-cyan-400'}`}>
              {msg.role === 'user' ? 'Operator' : 'SatQuery Agent'}
            </span>
            <p className="leading-relaxed text-[12px] font-light tracking-wide">{msg.text}</p>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex gap-3 mt-4 shrink-0 relative">
        <input 
          type="text" 
          placeholder="Enter analytical query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          className="flex-1 bg-black/30 backdrop-blur-md border border-white/10 rounded-xl px-4 py-3 text-xs text-white placeholder-gray-500 outline-none focus:border-cyan-400 focus:bg-white/[0.05] transition-all duration-300 shadow-inner"
        />
        <button 
          onClick={onSubmit}
          disabled={isLoading}
          className={`px-6 py-3 rounded-xl text-xs font-bold tracking-widest uppercase transition-all duration-300 shadow-[0_0_20px_rgba(34,211,238,0.2)] hover:shadow-[0_0_30px_rgba(34,211,238,0.5)] ${
            isLoading 
              ? 'bg-cyan-900/40 text-cyan-500/50 cursor-not-allowed border border-cyan-900/50' 
              : 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white border border-white/20'
          }`}
        >
          {isLoading ? "..." : "Execute"}
        </button>
      </div>
    </div>
  );
}