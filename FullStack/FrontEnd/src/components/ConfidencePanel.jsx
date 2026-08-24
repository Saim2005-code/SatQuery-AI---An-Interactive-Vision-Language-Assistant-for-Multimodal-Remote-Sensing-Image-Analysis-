function ConfidencePanel() {
  return (
    <div className="bg-gray-900 text-white p-4 rounded-lg">
      <h2 className="font-semibold mb-3">Confidence & Actions</h2>
      <div className="flex justify-between items-center mb-3">
        <span className="text-gray-400 text-sm">Confidence Score</span>
        <span className="bg-green-900/40 text-green-400 px-3 py-1 rounded-lg text-sm">
          91.8%
        </span>
      </div>
      <div className="flex justify-between items-center mb-4">
        <span className="text-gray-400 text-sm">Resolution</span>
        <span className="text-sm">0.65m (Cartosat-2S)</span>
      </div>
      <button className="w-full bg-cyan-700 hover:bg-cyan-600 py-2 rounded-lg text-sm">
        Download Inspection PDF Report
      </button>
    </div>
  )
}

export default ConfidencePanel