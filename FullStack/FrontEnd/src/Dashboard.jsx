import { useState } from "react";
import "./App.css";

import UploadPanel from "./components/UploadPanel";
import MapViewer from "./components/MapViewer";
import ChatPanel from "./components/ChatPanel";
import Header from "./components/Header";
import ExecutionSummaryPanel from "./components/ExecutionSummaryPanel";
import AuditTracePanel from "./components/AuditTracePanel";
import ConfidencePanel from "./components/ConfidencePanel";

function Dashboard() {
  // Master State
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Chat History
  const [chatHistory, setChatHistory] = useState([
    {
      role: "agent",
      text: "SatQuery AI active. Upload satellite imagery (GeoTIFF/PNG) and enter an analytical query to begin.",
    },
  ]);

  // Active AI Result Data
  const [activeResult, setActiveResult] = useState({
    interaction_id: null,
    confidence: "91.8%",
    resolution: "0.65m (Cartosat-2S)",
    image_url: null,
    bounding_box: null,
    trace: {
      task: "Bi-Temporal Change",
      tool: "Change-Adapter-v2",
      time: "0.82s",
      confidence: "91.8%",
    },
  });

  const handleAnalyzeSubmission = async () => {
    if (!file1) {
      alert("Please upload at least one satellite image in the Upload Panel.");
      return;
    }
    if (!query.trim()) {
      alert("Please enter a query before sending.");
      return;
    }

    const currentQuery = query;
    // Add user query to conversation instantly
    setChatHistory((prev) => [...prev, { role: "user", text: currentQuery }]);
    setQuery("");
    setIsLoading(true);

    const formData = new FormData();
    formData.append("query", currentQuery);
    formData.append("image1", file1);
    if (file2) formData.append("image2", file2);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/analyze", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Backend inference failed.");
      const data = await res.json();

      // Append Agent Response
      setChatHistory((prev) => [
        ...prev,
        { role: "agent", text: data.answer || data.message },
      ]);

      // Update Live Telemetry & Map Data
      setActiveResult({
        interaction_id: data.interaction_id,
        confidence:
          data.execution_trace?.confidence_score ||
          `${(data.confidence * 100).toFixed(1)}%`,
        resolution:
          data.execution_trace?.parameters_applied?.spatial_alignment_crs ||
          "0.65m (Cartosat-2S)",
        image_url: data.image_urls?.[0]
          ? `http://127.0.0.1:8000${data.image_urls[0]}`
          : null,
        bounding_box: data.bounding_box,
        trace: {
          task:
            data.execution_trace?.classified_task ||
            "Temporal Change Detection",
          tool: data.execution_trace?.invoked_tool || "Change-Adapter-v2",
          time: `${((data.execution_trace?.latency_ms || 820) / 1000).toFixed(2)}s`,
          confidence: data.execution_trace?.confidence_score || "91.8%",
          ...data.execution_trace,
        },
      });
    } catch (err) {
      console.error(err);
      setChatHistory((prev) => [
        ...prev,
        {
          role: "agent",
          text: "⚠️ Analysis error: Ensure the FastAPI server is running on port 8000.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#0b0f17] h-screen p-3 text-white flex flex-col overflow-hidden font-sans">
      <Header />
      <div className="grid grid-cols-3 grid-rows-[1fr_auto] gap-3 mt-3 flex-1 min-h-0">
        {/* Left column */}
        <div className="col-span-1 row-span-2 flex flex-col gap-3 min-h-0">
          <UploadPanel
            file1={file1}
            setFile1={setFile1}
            file2={file2}
            setFile2={setFile2}
          />
          <ChatPanel
            query={query}
            setQuery={setQuery}
            chatHistory={chatHistory}
            onSubmit={handleAnalyzeSubmission}
            isLoading={isLoading}
          />
          <AuditTracePanel trace={activeResult.trace} />
        </div>

        {/* Map Viewer */}
        <div className="col-span-2 min-h-0">
          <MapViewer
            file1={file1}
            imageUrl={activeResult.image_url}
            boundingBox={activeResult.bounding_box}
          />
        </div>

        {/* Bottom panels */}
        <ConfidencePanel
          confidence={activeResult.confidence}
          resolution={activeResult.resolution}
          interactionId={activeResult.interaction_id}
        />
        <ExecutionSummaryPanel trace={activeResult.trace} />
      </div>
    </div>
  );
}

export default Dashboard;
