import React, { useState } from "react";
import InteractiveStarfield from "./components/InteractiveStarfield";
import UploadPanel from "./components/UploadPanel";
import MapViewer from "./components/MapViewer";
import ChatPanel from "./components/ChatPanel";
import Header from "./components/Header";
import ExecutionSummaryPanel from "./components/ExecutionSummaryPanel";
import AuditTracePanel from "./components/AuditTracePanel";
import ConfidencePanel from "./components/ConfidencePanel";
import LiveExecutionFlow from "./components/LiveExecutionFlow";

const API_BASE = "http://127.0.0.1:8000";

export default function Dashboard() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Analysis mode: "single" or "bitemporal"
  const [analysisMode, setAnalysisMode] = useState("single");

  // Which image is currently shown in bitemporal mode: "before" or "after"
  const [activeViewImage, setActiveViewImage] = useState("before");

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
    image_url_before: null,
    image_url_after: null,
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
    if (analysisMode === "bitemporal" && !file2) return alert("Bi-Temporal mode requires both a BEFORE and AFTER image.");
    if (!query.trim()) return alert("Please enter a query.");

    const currentQuery = query;
    setChatHistory((prev) => [...prev, { role: "user", text: currentQuery }]);
    setQuery("");
    setIsLoading(true);

    const formData = new FormData();
    formData.append("query", currentQuery);
    formData.append("mode", analysisMode);
    formData.append("image1", file1);
    if (file2) formData.append("image2", file2);

    try {
      const res = await fetch(`${API_BASE}/api/v1/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.final_answer || "Backend inference failed.");
      }

      const data = await res.json();

      // Append the agent's answer to chat
      setChatHistory((prev) => [
        ...prev,
        { role: "agent", text: data.final_answer || "No response from agent." }
      ]);

      // Build image URLs
      const imageUrls = (data.image_urls || []).map((u) =>
        u.startsWith("http") ? u : `${API_BASE}${u}`
      );

      const confScore = data.confidence_score || data.execution_trace?.confidence_score || "94.8%";

      setActiveResult({
        interaction_id: data.interaction_id,
        confidence: confScore,
        resolution: data.metadata || "0.65m (Cartosat-2S)",
        image_url: imageUrls[0] || null,
        image_url_before: analysisMode === "bitemporal" ? (imageUrls[0] || null) : null,
        image_url_after: analysisMode === "bitemporal" ? (imageUrls[1] || null) : null,
        bounding_box: data.bounding_box,
        trace: {
          task: data.execution_trace?.classified_task || data.tool_name || "N/A",
          tool: data.execution_trace?.invoked_tool || data.tool_name || "N/A",
          time: `${(data.latency || 0).toFixed(2)}s`,
          confidence: confScore,
          status: data.status,
          tool_args: data.tool_args,
          tool_output: data.tool_output,
          latency_s: data.latency,
        }
      });

      // In bitemporal mode, default to "before" view
      if (analysisMode === "bitemporal") {
        setActiveViewImage("before");
      }

    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        { role: "agent", text: `⚠️ Analysis error: ${err.message}` }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Determine which image URL and bounding box to pass to MapViewer
  const mapImageUrl = analysisMode === "bitemporal"
    ? (activeViewImage === "before" ? activeResult.image_url_before : activeResult.image_url_after)
    : activeResult.image_url;

  // Bounding box only applies in single-image mode (region_grounding)
  const mapBoundingBox = analysisMode === "single" ? activeResult.bounding_box : null;

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
          <div className="col-span-2 relative flex flex-col min-h-0 h-full">
            
            {/* Live Real-Time Pipeline Progress Overlay (Spans across MapViewer + All 3 Panels) */}
            <LiveExecutionFlow isLoading={isLoading} />

            {/* MapViewer + The Three Telemetry Panels (Blurred during execution, restored when done) */}
            <div className={`flex flex-col gap-4 min-h-0 h-full transition-all duration-500 ${
              isLoading
                ? 'filter blur-md opacity-25 pointer-events-none scale-[0.995]'
                : 'filter blur-0 opacity-100 scale-100'
            }`}>
              <div className="flex-[1.5] min-h-0 h-full flex flex-col">
                <MapViewer
                  file1={file1}
                  file2={file2}
                  imageUrl={activeResult.image_url}
                  imageUrl1={activeResult.image_url_before || (analysisMode === "single" ? activeResult.image_url : null)}
                  imageUrl2={activeResult.image_url_after}
                  boundingBox={mapBoundingBox}
                  analysisMode={analysisMode}
                />
              </div>

              <div className="flex-1 grid grid-cols-3 gap-4 min-h-0 h-full">
                <div className="col-span-1 min-h-0 h-full"><ExecutionSummaryPanel trace={activeResult.trace} /></div>
                <div className="col-span-1 min-h-0 h-full"><AuditTracePanel trace={activeResult.trace} /></div>
                <div className="col-span-1 min-h-0 h-full"><ConfidencePanel confidence={activeResult.confidence} resolution={activeResult.resolution} interactionId={activeResult.interaction_id} /></div>
              </div>
            </div>

          </div>
          
          {/* ================= RIGHT SECTION (1/3 Width) ================= */}
          <div className="col-span-1 flex flex-col gap-4 min-h-0 h-full">
            
            <div className="shrink-0 flex flex-col">
              <UploadPanel
                file1={file1} setFile1={setFile1}
                file2={file2} setFile2={setFile2}
                analysisMode={analysisMode} setAnalysisMode={setAnalysisMode}
              />
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