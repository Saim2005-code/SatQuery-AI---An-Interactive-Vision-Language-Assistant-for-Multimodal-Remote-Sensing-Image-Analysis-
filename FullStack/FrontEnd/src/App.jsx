import { useState } from "react";
import "./App.css";


import UploadPanel from "./components/UploadPanel";
import MapViewer from "./components/MapViewer";
import ChatPanel from "./components/ChatPanel";
import Header from "./components/Header";
import ExecutionSummaryPanel from "./components/ExecutionSummaryPanel";
import AuditTracePanel from "./components/AuditTracePanel";
import ConfidencePanel from "./components/ConfidencePanel";


function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <div className="bg-black h-screen p-3 text-white flex flex-col overflow-hidden">
        <Header />
        <div className="grid grid-cols-3 grid-rows-[1fr_auto] gap-3 mt-3 flex-1 min-h-0">

          {/* Left column — spans both rows */}
          <div className="col-span-1 row-span-2 flex flex-col gap-3 min-h-0">
            <UploadPanel />
            <ChatPanel />
            <AuditTracePanel />
          </div>

          {/* Map Viewer — row 1, cols 2-3 */}
          <div className="col-span-2 min-h-0">
            <MapViewer />
          </div>

          {/* Bottom panels — row 2, cols 2-3 */}
          <ConfidencePanel />
          <ExecutionSummaryPanel />

        </div>
      </div>
    </>
  );
}

export default App;
