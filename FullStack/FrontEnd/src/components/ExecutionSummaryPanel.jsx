function ExecutionSummaryPanel() {
    return (
      <div className="bg-gray-900 text-white p-4 rounded-lg">
        <h2 className="font-semibold mb-3">Execution Summary</h2>
        <pre className="bg-black/40 rounded-lg p-3 text-xs text-green-400 overflow-x-auto">
  {`{
    "task": "Bi-Temporal Change",
    "tool": "Change-Adapter-v2",
    "time": "0.82s",
    "confidence": "91.8%"
  }`}
        </pre>
      </div>
    )
  }
  
  export default ExecutionSummaryPanel