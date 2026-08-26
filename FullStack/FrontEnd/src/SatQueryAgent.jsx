import React, { useState } from 'react';

export default function SatQueryAgent() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please upload a satellite image first!");
      return;
    }

    setIsLoading(true);
    setResponse(null);

    // 1. Pack the data into a FormData object
    const formData = new FormData();
    formData.append("query", query);
    formData.append("image1", file);

    try {
      // 2. Send the POST request to FastAPI
      const res = await fetch("http://127.0.0.1:8000/api/v1/analyze", {
        method: "POST",
        body: formData,
        // Notice we do NOT set 'Content-Type'. The browser handles the multipart boundaries automatically!
      });

      if (!res.ok) throw new Error("Server failed to respond.");

      // 3. Read the Python response
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      console.error(error);
      setResponse({ status: "error", message: "Failed to connect to the backend." });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-10 flex flex-col items-center">
      <div className="w-full max-w-2xl bg-gray-800 p-8 rounded-xl shadow-2xl border border-gray-700">
        <h1 className="text-2xl font-bold text-indigo-400 mb-6">SatQuery AI Ingestion System</h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload Input */}
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium text-gray-300">Upload GeoTIFF / PNG</label>
            <input 
              type="file" 
              accept=".tif,.tiff,.png,.jpg"
              onChange={(e) => setFile(e.target.files[0])}
              className="file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 text-gray-300 border border-gray-700 rounded bg-gray-900 p-2"
            />
          </div>

          {/* Text Query Input */}
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium text-gray-300">AI Query</label>
            <input 
              type="text" 
              placeholder="e.g. Highlight the new buildings in this region..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
              className="p-3 bg-gray-900 border border-gray-700 rounded text-white focus:ring-2 focus:ring-indigo-500 outline-none"
            />
          </div>

          {/* Submit Button */}
          <button 
            type="submit" 
            disabled={isLoading}
            className={`w-full py-3 rounded font-bold transition ${isLoading ? "bg-indigo-400 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-500"}`}
          >
            {isLoading ? "Transmitting to Python Backend..." : "Execute AI Analysis"}
          </button>
        </form>

        {/* Response Display Area */}
        {response && (
          <div className={`mt-8 p-4 rounded border ${response.status === 'success' ? 'bg-green-900/20 border-green-500/50' : 'bg-red-900/20 border-red-500/50'}`}>
            <h3 className="text-sm font-bold mb-2">Backend Response:</h3>
            <p className="font-mono text-sm text-gray-300">{response.message}</p>
          </div>
        )}
      </div>
    </div>
  );
}
