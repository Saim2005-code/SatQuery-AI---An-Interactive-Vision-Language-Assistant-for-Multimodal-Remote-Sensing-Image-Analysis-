function ChatPanel() {
  return (
    <div className="bg-gray-900 text-white p-4 rounded-lg flex-1 min-h-0 flex flex-col">
      <h2 className="font-semibold mb-2">Query & Chat Panel</h2>

      <div className="flex-1 space-y-2 mb-3 overflow-y-auto min-h-0">
        <div className="bg-gray-800 rounded-lg p-3 text-sm">
          <span className="text-gray-400 block mb-1">User Query</span>
          What changed in the river basin between these dates?
        </div>

        <div className="bg-green-900/30 rounded-lg p-3 text-sm">
          <span className="text-gray-400 block mb-1">SatQuery AI Response</span>
          Urban construction expanded into the flood plain by 14.2%.
        </div>
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Ask a question about your image..."
          className="flex-1 bg-gray-800 text-white rounded-lg px-3 py-2 text-sm outline-none"
        />
        <button className="bg-cyan-600 px-4 py-2 rounded-lg text-sm">
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatPanel;
