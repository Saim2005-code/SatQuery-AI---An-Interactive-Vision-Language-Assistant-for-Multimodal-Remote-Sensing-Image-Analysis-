import React, { useState, useEffect } from 'react';

const PIPELINE_STEPS = [
  { id: 1, label: "1. Validating remote sensing image format & spatial CRS", short: "Ingest Validator", desc: "Validating GeoTIFF headers, GDAL drivers & spatial projections" },
  { id: 2, label: "2. Spatial raster metadata verified & bounds confirmed", short: "Spatial Contract", desc: "Extracted EPSG coordinates, band dimensions & sensor modality" },
  { id: 3, label: "3. Scaling radiometric data (16-bit to float32 tensor)", short: "Radiometric Scaler", desc: "2nd/98th percentile clipping & memory-safe normalization" },
  { id: 4, label: "4. Memory-safe tensor normalization complete", short: "Tensor Pipeline", desc: "AI-ready calibrated float32 spatial tensor generated" },
  { id: 5, label: "5. Agentic Orchestrator analyzing directive query", short: "Query Analysis", desc: "Parsing natural language intent with LangChain LLM router" },
  { id: 6, label: "6. Agent selecting optimal specialist neural tool", short: "Tool Selection", desc: "Routing between RS-VLM, Grounding DINO & Change Detection" },
  { id: 7, label: "7. Specialist tool selected & binding neural weights", short: "Engine Binding", desc: "Loading model adapters and executing specialized graph node" },
  { id: 8, label: "8. Specialist engine performing spatial inference", short: "Neural Inference", desc: "Executing vision-language attention or open-set detection" },
  { id: 9, label: "9. Spatial grounding & contextual verification", short: "Grounding Verification", desc: "Generating bounding coordinates & deterministic metrics" },
  { id: 10, label: "10. Synthesizing mission telemetry & generating answer", short: "Answer Synthesis", desc: "Formulating auditable explanation & confidence score" },
  { id: 11, label: "11. Final mission intelligence output ready", short: "Execution Complete", desc: "Streaming payload to tactical HUD & updating telemetry" }
];

export default function LiveExecutionFlow({ isLoading }) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setCurrentStep(0);
      return;
    }

    setCurrentStep(0);
    const intervals = [
      450,  // step 1: validating
      500,  // step 2: validated
      550,  // step 3: scaling
      600,  // step 4: done scaling
      700,  // step 5: analyzing query
      800,  // step 6: choosing tool
      850,  // step 7: tool selected
      1200, // step 8: analyzing image
      1100, // step 9: verifying
      950,  // step 10: generating answer
      700   // step 11: done
    ];

    let timerId = null;
    let stepIndex = 0;

    const nextStep = () => {
      if (stepIndex < PIPELINE_STEPS.length - 1) {
        stepIndex++;
        setCurrentStep(stepIndex);
        timerId = setTimeout(nextStep, intervals[stepIndex] || 800);
      }
    };

    timerId = setTimeout(nextStep, intervals[0]);

    return () => {
      if (timerId) clearTimeout(timerId);
    };
  }, [isLoading]);

  if (!isLoading) return null;

  const progressPct = Math.round(((currentStep + 1) / PIPELINE_STEPS.length) * 100);

  return (
    <div className="absolute inset-0 z-30 bg-[#060b16]/95 backdrop-blur-2xl border border-cyan-500/50 rounded-2xl p-6 flex flex-col justify-between shadow-[0_0_60px_rgba(6,182,212,0.3)] overflow-hidden animate-fadeIn">
      
      {/* ── Top Mission Control Telemetry Bar ── */}
      <div className="flex justify-between items-center shrink-0 border-b border-cyan-900/60 pb-3.5">
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center">
            <span className="w-4 h-4 rounded-full bg-cyan-400 animate-ping absolute opacity-75"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_15px_rgba(34,211,238,1)]"></span>
          </div>
          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-widest flex items-center gap-2.5">
              Autonomous Agent Orchestration Pipeline
              <span className="text-[10px] font-mono text-cyan-300 bg-cyan-500/15 px-2.5 py-0.5 rounded border border-cyan-500/40 shadow-[0_0_10px_rgba(34,211,238,0.2)]">
                LIVE STREAM
              </span>
            </h4>
            <p className="text-[11px] text-gray-400 font-mono mt-0.5">
              Real-time multi-stage neural execution & spatial preprocessing
            </p>
          </div>
        </div>

        <div className="flex items-center gap-5 font-mono">
          <div className="text-right">
            <span className="text-[10px] text-gray-400 uppercase tracking-widest mr-2">Step</span>
            <span className="text-sm font-bold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60">
              {String(currentStep + 1).padStart(2, '0')} / {String(PIPELINE_STEPS.length).padStart(2, '0')}
            </span>
          </div>
          <div className="text-right pl-4 border-l border-white/10">
            <span className="text-sm font-bold text-emerald-400 bg-emerald-950/60 px-2.5 py-0.5 rounded border border-emerald-800/60">
              {progressPct}%
            </span>
          </div>
        </div>
      </div>

      {/* ── Flowing Laser Beam Progress Bar (Left to Right) ── */}
      <div className="my-4 shrink-0">
        <div className="flex justify-between items-center text-[10px] font-mono text-gray-400 uppercase tracking-widest mb-1.5 px-1">
          <span className="text-cyan-400 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            Pipeline Ingress
          </span>
          <span className="text-purple-400 flex items-center gap-1.5">
            Telemetry Egress
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
          </span>
        </div>
        <div className="relative w-full h-3 bg-black/70 rounded-full overflow-hidden border border-cyan-900/60 p-0.5 shadow-inner">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-500 via-teal-400 to-purple-500 shadow-[0_0_25px_rgba(34,211,238,0.9)] transition-all duration-500 ease-out relative"
            style={{ width: `${progressPct}%` }}
          >
            {/* Pulsing leading laser tip */}
            <div className="absolute right-0 top-0 bottom-0 w-10 bg-white blur-[2px] rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* ── Revealed Process Cards (Only visible once the bar reaches them) ── */}
      <div className="flex-1 grid grid-cols-3 gap-3 min-h-0 overflow-y-auto py-1 pr-1 custom-scrollbar">
        {PIPELINE_STEPS.map((step, idx) => {
          const isCompleted = idx < currentStep;
          const isCurrent = idx === currentStep;
          const isRevealed = idx <= currentStep;

          // Steps that haven't been reached yet are hidden
          if (!isRevealed) return null;

          return (
            <div
              key={step.id}
              className={`rounded-xl p-3.5 flex items-start gap-3 transition-all duration-500 border animate-slideInLeft ${
                isCurrent
                  ? 'bg-cyan-500/15 border-cyan-400/90 shadow-[0_0_25px_rgba(6,182,212,0.35)] ring-1 ring-cyan-400/60'
                  : 'bg-black/40 border-cyan-900/40 text-gray-400'
              }`}
            >
              {/* Step Status Badge */}
              <div className="shrink-0 mt-0.5">
                {isCompleted ? (
                  <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 flex items-center justify-center text-xs font-bold shadow-[0_0_10px_rgba(52,211,153,0.3)]">
                    ✓
                  </span>
                ) : isCurrent ? (
                  <span className="w-5 h-5 rounded-full bg-cyan-500/30 text-cyan-300 border border-cyan-400 flex items-center justify-center text-xs font-bold animate-spin shadow-[0_0_12px_rgba(34,211,238,0.5)]">
                    ⚙
                  </span>
                ) : (
                  <span className="w-5 h-5 rounded-full bg-white/5 text-gray-500 border border-white/10 flex items-center justify-center text-[10px] font-mono">
                    {step.id}
                  </span>
                )}
              </div>

              {/* Step Text Info */}
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-1 mb-1">
                  <span className="text-[11px] font-mono tracking-widest uppercase font-bold text-gray-300 truncate">
                    {step.short}
                  </span>
                  {isCurrent && (
                    <span className="text-[9px] font-mono text-cyan-300 bg-cyan-400/15 px-2 py-0.5 rounded border border-cyan-400/40 animate-pulse">
                      PROCESSING
                    </span>
                  )}
                </div>
                <p className={`text-xs leading-snug font-medium ${isCurrent ? 'text-cyan-100 font-semibold' : 'text-gray-400'}`}>
                  {step.label}
                </p>
                <p className="text-[10px] text-gray-500 font-mono mt-1 leading-tight truncate">
                  {step.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Bottom Active Subsystem Terminal Bar ── */}
      <div className="shrink-0 pt-3 border-t border-cyan-900/50 flex items-center justify-between text-xs font-mono text-gray-400">
        <div className="flex items-center gap-2.5 truncate">
          <span className="text-cyan-400 font-bold">[ACTIVE SUBSYSTEM]:</span>
          <span className="text-cyan-200 font-semibold truncate">{PIPELINE_STEPS[currentStep]?.label}</span>
        </div>
        <span className="text-[11px] text-gray-500 uppercase tracking-widest shrink-0 ml-3">
          Auto-Restoring Telemetry on Completion
        </span>
      </div>

    </div>
  );
}
