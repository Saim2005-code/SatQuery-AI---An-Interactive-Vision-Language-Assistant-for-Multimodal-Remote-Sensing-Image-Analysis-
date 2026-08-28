import React, { useState } from "react";
import InteractiveStarfield from "./components/InteractiveStarfield";
import UploadPanel from "./components/UploadPanel";
import MapViewer from "./components/MapViewer";
import ChatPanel from "./components/ChatPanel";
import Header from "./components/Header";
import ExecutionSummaryPanel from "./components/ExecutionSummaryPanel";
import AuditTracePanel from "./components/AuditTracePanel";
import ConfidencePanel from "./components/ConfidencePanel";

export default function Dashboard() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const [chatHistory, setChatHistory] = useState([
    {
      role: "agent",
      text: "SatQuery AI active. Upload satellite imagery (GeoTIFF/PNG) and enter an analytical query to begin.",
    }
  ]);

  const [activeResult, setActiveResult] = useState({
    interaction_id: null,
    confidence: "00.0%",
    resolution: "PENDING",
    image_url: null,
    bounding_box: null,
    trace: {
      task: "STANDBY",
      tool: "N/A",
      time: "0.00s",
      confidence: "00.0%"
    }
  });

  const handleAnalyzeSubmission = async () => {
    if (!file1) return alert("Please upload at least one satellite image.");
    if (!query.trim()) return alert("Please enter a query.");

    const currentQuery = query;
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

      setChatHistory((prev) => [...prev, { role: "agent", text: data.answer || data.message }]);

      setActiveResult({
        interaction_id: data.interaction_id,
        confidence: data.execution_trace?.confidence_score || "94.8%",
        resolution: "0.65m (Cartosat-2S)",
        image_url: data.image_urls?.[0] ? `http://127.0.0.1:8000${data.image_urls[0]}` : null,
        bounding_box: data.bounding_box,
        trace: {
          task: data.execution_trace?.classified_task || "Temporal Change Detection",
          tool: data.execution_trace?.invoked_tool || "Change-Adapter-v2",
          time: `${((data.execution_trace?.latency_ms || 820) / 1000).toFixed(2)}s`,
          confidence: data.execution_trace?.confidence_score || "94.8%",
          ...data.execution_trace
        }
      });
    } catch (err) {
      setChatHistory((prev) => [...prev, { role: "agent", text: "⚠️ Analysis error: Connection failed." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-screen h-screen bg-[#02050a] text-white font-sans overflow-hidden">
      <div className="absolute inset-0 z-0 opacity-70 pointer-events-none">
        <InteractiveStarfield />
      </div>

      <div className="absolute inset-0 z-10 flex flex-col p-4 sm:p-5 pointer-events-none">
        
        <div className="pointer-events-auto shrink-0 mb-4">
          <Header />
        </div>
        
        <div className="grid grid-cols-3 gap-4 flex-1 min-h-0 h-full pointer-events-auto">
          
          {/* ================= LEFT SECTION (2/3 Width) ================= */}
          <div className="col-span-2 flex flex-col gap-4 min-h-0 h-full">
            
            <div className="flex-[1.5] min-h-0 h-full flex flex-col">
              <MapViewer file1={file1} imageUrl={activeResult.image_url} boundingBox={activeResult.bounding_box} />
            </div>

            <div className="flex-1 grid grid-cols-3 gap-4 min-h-0 h-full">
              <div className="col-span-1 min-h-0 h-full"><ExecutionSummaryPanel trace={activeResult.trace} /></div>
              <div className="col-span-1 min-h-0 h-full"><AuditTracePanel trace={activeResult.trace} /></div>
              <div className="col-span-1 min-h-0 h-full"><ConfidencePanel confidence={activeResult.confidence} resolution={activeResult.resolution} interactionId={activeResult.interaction_id} /></div>
            </div>
          </div>
          
          {/* ================= RIGHT SECTION (1/3 Width) ================= */}
          <div className="col-span-1 flex flex-col gap-4 min-h-0 h-full">
            
            <div className="shrink-0 flex flex-col">
              <UploadPanel file1={file1} setFile1={setFile1} file2={file2} setFile2={setFile2} />
            </div>
            
            <div className="flex-1 min-h-0 h-full w-full flex flex-col">
              <ChatPanel query={query} setQuery={setQuery} chatHistory={chatHistory} onSubmit={handleAnalyzeSubmission} isLoading={isLoading} />
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}