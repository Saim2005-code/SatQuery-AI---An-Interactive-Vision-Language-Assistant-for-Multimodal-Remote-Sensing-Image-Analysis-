import streamlit as st
import numpy as np
import os
import sys
import tempfile
import time
import re
from PIL import Image, ImageDraw
from pathlib import Path
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()

# --- DYNAMIC PATH RESOLUTION ---
SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR / "data_pipeline"))
sys.path.append(str(SRC_DIR / "agent_controller"))

# 1. Real Preprocessor Pipeline (Module 2)
from ingest_validator import validate_geotiff
from memory_safe_reader import safe_read_geotiff
from radiometric_scaler import scale_to_tensor

# 2. Real Agentic Router (Module 4)
from agent_router import execute_agent_route

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SatQuery AI | Mission Operations HUD",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AEROSPACE MISSION OPS STYLING (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #07090e;
        --bg-secondary: #0d121d;
        --card-bg: rgba(17, 24, 39, 0.75);
        --border-color: rgba(56, 189, 248, 0.15);
        --accent-cyan: #38bdf8;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --accent-purple: #a855f7;
    }

    .stApp {
        background-color: var(--bg-primary);
        background-image:
            radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.05) 0px, transparent 50%);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }

    .top-telemetry-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 10px 18px;
        margin-bottom: 20px;
    }

    .brand-title {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .status-pill-container {
        display: flex;
        gap: 12px;
        font-family: 'Fira Code', monospace;
        font-size: 0.75rem;
    }

    .status-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 4px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #94a3b8;
    }

    .dot { width: 6px; height: 6px; border-radius: 50%; }
    .dot-green { background-color: var(--accent-emerald); box-shadow: 0 0 6px var(--accent-emerald); }
    .dot-cyan { background-color: var(--accent-cyan); box-shadow: 0 0 6px var(--accent-cyan); }
    .dot-amber { background-color: var(--accent-amber); box-shadow: 0 0 6px var(--accent-amber); }

    .tactical-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        backdrop-filter: blur(8px);
    }

    .card-label {
        font-family: 'Fira Code', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: var(--accent-cyan);
        margin-bottom: 10px;
    }

    .terminal-window {
        background: #04070d;
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 6px;
        padding: 14px;
        font-family: 'Fira Code', monospace;
        font-size: 0.78rem;
        line-height: 1.6;
        color: #cbd5e1;
    }

    .trace-key { color: var(--accent-cyan); font-weight: 600; }
    .trace-val { color: #f8fafc; }
    .trace-success { color: var(--accent-emerald); }

    .stTextInput input {
        background-color: #0b111e !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        color: #f8fafc !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif;
    }

    .stTextInput input:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.25) !important;
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 6px !important;
        font-family: 'Fira Code', monospace !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- TOP TELEMETRY RIBBON ---
st.markdown("""
<div class="top-telemetry-bar">
    <div class="brand-title">
        <span>🛰️</span>
        <span>SATQUERY <span style="color:#38bdf8;">MISSION OPS</span></span>
        <span style="font-size:0.75rem; font-weight:400; color:#64748b; margin-left:8px;">| SIH-2026 GEOSPATIAL CORE</span>
    </div>
    <div class="status-pill-container">
        <div class="status-pill"><span class="dot dot-green"></span>MODULE 2: ACTIVE</div>
        <div class="status-pill"><span class="dot dot-cyan"></span>MODULE 4 (ROUTER): CONNECTED</div>
        <div class="status-pill"><span class="dot dot-amber"></span>VRAM LOAD: 8%</div>
    </div>
</div>
""", unsafe_allow_html=True)


def ingest_single_geotiff(uploaded_file):
    """
    Runs one uploaded file through the Module 2 pipeline and returns
    (display_image, meta, meta_str, persisted_path) or raises on failure.
    Shared helper so single-image and before/after uploads use identical logic.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        meta = validate_geotiff(tmp_path)
        raw_array = safe_read_geotiff(tmp_path)
        scaled_tensor = scale_to_tensor(raw_array, meta["modality"])

        if scaled_tensor.shape[0] >= 3:
            rgb_disp = (np.transpose(scaled_tensor[:3, :, :], (1, 2, 0)) * 255).astype(np.uint8)
        else:
            gray = (scaled_tensor[0, :, :] * 255).astype(np.uint8)
            rgb_disp = np.stack([gray, gray, gray], axis=-1)

        display_image = Image.fromarray(rgb_disp)
        meta_str = (
            f"Modality: {meta['modality']}, "
            f"Bands: {meta['band_count']}, "
            f"CRS: {meta['crs']}, "
            f"Grid: {meta['width']}x{meta['height']}"
        )
        return display_image, meta, meta_str
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# --- MAIN WORKSPACE LAYOUT ---
left_rail, main_viewport = st.columns([1.1, 2.1], gap="medium")

# ==========================================
# LEFT RAIL: INGESTION & SPATIAL CONTRACT
# ==========================================
with left_rail:
    st.markdown('<div class="card-label">01. Data Ingestion Gatekeeper</div>', unsafe_allow_html=True)

    # --- ANALYSIS MODE TOGGLE ---
    analysis_mode = st.radio(
        "Analysis Mode",
        options=["🖼️ Single Image", "🕓 Bi-Temporal (Before/After)"],
        horizontal=True,
        label_visibility="collapsed",
    )
    is_bitemporal = analysis_mode.endswith("Before/After)")

    # Reset stale state when the mode changes so old overlays / images
    # from the other mode don't leak into a fresh run.
    if st.session_state.get("_last_mode") != analysis_mode:
        st.session_state["last_bbox"] = None
        st.session_state["_last_mode"] = analysis_mode

    # --- ENGINE PRE-WARM (for demos: load the VLM before judges arrive) ---
    engine_ready = st.session_state.get("_engine_warm", False)
    warm_col1, warm_col2 = st.columns([3, 1])
    with warm_col1:
        if engine_ready:
            st.success("✅ Neural Engine Online (cached)", icon="🟢")
        else:
            st.warning("⚠️ Neural Engine Cold — first query will be slow", icon="🟡")
    with warm_col2:
        if st.button("🚀 Initialize", use_container_width=True, disabled=engine_ready):
            with st.spinner("Loading Engine 1 (RS-VLM) + Engine 2 (Grounding DINO)... (~30-90s, one time)"):
                if str(SRC_DIR) not in sys.path:
                    sys.path.append(str(SRC_DIR))
                from ai_core.engine1_vlm import get_engine1_vlm
                from ai_core.engine2_vlm import get_engine2_grounding_dino
                get_engine1_vlm()
                get_engine2_grounding_dino()
                st.session_state["_engine_warm"] = True
            st.rerun()

    if not is_bitemporal:
        # ---------- SINGLE IMAGE MODE ----------
        uploaded_files = st.file_uploader(
            "Geospatial Raster Stream",
            type=["tif", "tiff"],
            accept_multiple_files=True,
            help="Upload .tif files conforming to SIH standards.",
            key="uploader_single",
        )

        if uploaded_files:
            latest_file = uploaded_files[-1]
            try:
                display_image, meta, meta_str = ingest_single_geotiff(latest_file)
                st.session_state["display_img"] = display_image
                st.session_state["meta"] = meta
                st.session_state["meta_str"] = meta_str

                persisted_img_path = os.path.abspath("active_spatial_render.jpg")
                display_image.save(persisted_img_path)
                st.session_state["persisted_img_path"] = persisted_img_path
            except Exception as e:
                st.error(f"Ingestion Rejected: {e}")

    else:
        # ---------- BI-TEMPORAL MODE ----------
        col_before, col_after = st.columns(2)
        with col_before:
            before_file = st.file_uploader(
                "Before Image (.tif)",
                type=["tif", "tiff"],
                accept_multiple_files=False,
                key="uploader_before",
            )
        with col_after:
            after_file = st.file_uploader(
                "After Image (.tif)",
                type=["tif", "tiff"],
                accept_multiple_files=False,
                key="uploader_after",
            )

        if before_file:
            try:
                before_img, before_meta, before_meta_str = ingest_single_geotiff(before_file)
                st.session_state["display_img_before"] = before_img
                st.session_state["meta_before"] = before_meta
                before_path = os.path.abspath("active_spatial_render_before.jpg")
                before_img.save(before_path)
                st.session_state["persisted_img_path_before"] = before_path
            except Exception as e:
                st.error(f"Before-image ingestion rejected: {e}")

        if after_file:
            try:
                after_img, after_meta, after_meta_str = ingest_single_geotiff(after_file)
                st.session_state["display_img_after"] = after_img
                st.session_state["meta_after"] = after_meta
                after_path = os.path.abspath("active_spatial_render_after.jpg")
                after_img.save(after_path)
                st.session_state["persisted_img_path_after"] = after_path
            except Exception as e:
                st.error(f"After-image ingestion rejected: {e}")

        # Combined metadata string used as router context in bi-temporal mode
        if "meta_before" in st.session_state and "meta_after" in st.session_state:
            mb, ma = st.session_state["meta_before"], st.session_state["meta_after"]
            st.session_state["meta_str_bitemporal"] = (
                f"BEFORE — Modality: {mb['modality']}, Bands: {mb['band_count']}, "
                f"CRS: {mb['crs']}, Grid: {mb['width']}x{mb['height']} | "
                f"AFTER — Modality: {ma['modality']}, Bands: {ma['band_count']}, "
                f"CRS: {ma['crs']}, Grid: {ma['width']}x{ma['height']}"
            )

    st.markdown('<div class="card-label" style="margin-top:20px;">02. Spatial Metadata Contract</div>', unsafe_allow_html=True)

    if not is_bitemporal:
        if "meta" in st.session_state:
            meta = st.session_state["meta"]
            st.markdown(f"""
            <div class="tactical-card" style="padding:12px;">
                <table style="width:100%; font-family:'Fira Code'; font-size:0.75rem; color:#cbd5e1;">
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.05);"><td style="padding:4px 0; color:#64748b;">FORMAT</td><td style="text-align:right;">{meta['driver']}</td></tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.05);"><td style="padding:4px 0; color:#64748b;">CRS</td><td style="text-align:right; color:#38bdf8;">{meta['crs']}</td></tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.05);"><td style="padding:4px 0; color:#64748b;">MODALITY</td><td style="text-align:right; color:#10b981;">{meta['modality']}</td></tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.05);"><td style="padding:4px 0; color:#64748b;">EXTENTS</td><td style="text-align:right;">{meta['width']} x {meta['height']} ({meta['band_count']} Bands)</td></tr>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.05);"><td style="padding:4px 0; color:#64748b;">DATATYPE</td><td style="text-align:right;">{meta['data_type']} → float32</td></tr>
                    <tr><td style="padding:4px 0; color:#64748b;">PIPELINE STATUS</td><td style="text-align:right; color:#38bdf8;">Memory-Safe Scaled</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tactical-card" style="text-align:center; padding:28px 10px; color:#475569; font-family:'Fira Code'; font-size:0.8rem;">
                NO RASTER STREAM DETECTED<br>
                <span style="font-size:0.7rem; color:#334155;">Upload .tif to initiate validation</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        if "meta_before" in st.session_state and "meta_after" in st.session_state:
            mb, ma = st.session_state["meta_before"], st.session_state["meta_after"]
            st.markdown(f"""
            <div class="tactical-card" style="padding:12px;">
                <table style="width:100%; font-family:'Fira Code'; font-size:0.72rem; color:#cbd5e1;">
                    <tr><td style="color:#64748b;">BEFORE</td><td style="text-align:right;">{mb['modality']} · {mb['width']}x{mb['height']} · {mb['band_count']}b</td></tr>
                    <tr><td style="color:#64748b;">AFTER</td><td style="text-align:right;">{ma['modality']} · {ma['width']}x{ma['height']} · {ma['band_count']}b</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tactical-card" style="text-align:center; padding:28px 10px; color:#475569; font-family:'Fira Code'; font-size:0.8rem;">
                AWAITING BEFORE + AFTER RASTERS<br>
                <span style="font-size:0.7rem; color:#334155;">Upload both .tif files to enable change detection</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="card-label">03. Registered Specialist Tools</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; flex-direction:column; gap:6px; font-family:'Fira Code'; font-size:0.75rem;">
        <div style="background:#0d1525; padding:6px 10px; border-radius:4px; border-left:2px solid #38bdf8; display:flex; justify-content:space-between;">
            <span>single_image_vqa</span><span style="color:#10b981;">ONLINE</span>
        </div>
        <div style="background:#0d1525; padding:6px 10px; border-radius:4px; border-left:2px solid #38bdf8; display:flex; justify-content:space-between;">
            <span>region_grounding</span><span style="color:#10b981;">ONLINE</span>
        </div>
        <div style="background:#0d1525; padding:6px 10px; border-radius:4px; border-left:2px solid #a855f7; display:flex; justify-content:space-between;">
            <span>bitemporal_change_analyzer</span><span style="color:#10b981;">ONLINE</span>
        </div>
        <div style="background:#0d1525; padding:6px 10px; border-radius:4px; border-left:2px solid #a855f7; display:flex; justify-content:space-between;">
            <span>optical_sar_fusion</span><span style="color:#10b981;">ONLINE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN VIEWPORT: TACTICAL CANVAS & AGENT CALL
# ==========================================
with main_viewport:
    tab_canvas, tab_meta_json = st.tabs(["🛰️ TACTICAL VIEWPORT", "📄 RAW SPATIAL JSON"])

    with tab_canvas:
        if not is_bitemporal:
            if "display_img" in st.session_state:
                active_render = st.session_state["display_img"].copy()

                if st.session_state.get("last_bbox"):
                    draw = ImageDraw.Draw(active_render)
                    ymin, xmin, ymax, xmax = st.session_state["last_bbox"]
                    draw.rectangle([xmin, ymin, xmax, ymax], outline="#38bdf8", width=3)

                st.image(active_render, caption="Tactical Sensor Viewport (Active GeoTIFF)", use_container_width=True)
            else:
                canvas = np.zeros((320, 700, 3), dtype=np.uint8) + [11, 17, 26]
                canvas[::40, :, :] = [20, 30, 45]
                canvas[:, ::40, :] = [20, 30, 45]
                st.image(canvas, caption="Viewport Standby: Awaiting Raster Ingestion", use_container_width=True)
        else:
            # Side-by-side before/after viewport
            col_b, col_a = st.columns(2)
            with col_b:
                if "display_img_before" in st.session_state:
                    st.image(st.session_state["display_img_before"], caption="BEFORE", use_container_width=True)
                else:
                    st.info("Awaiting BEFORE raster.")
            with col_a:
                if "display_img_after" in st.session_state:
                    st.image(st.session_state["display_img_after"], caption="AFTER", use_container_width=True)
                else:
                    st.info("Awaiting AFTER raster.")

    with tab_meta_json:
        if not is_bitemporal:
            if "meta" in st.session_state:
                st.json(st.session_state["meta"])
            else:
                st.info("No spatial header loaded.")
        else:
            if "meta_before" in st.session_state or "meta_after" in st.session_state:
                st.json({
                    "before": st.session_state.get("meta_before"),
                    "after": st.session_state.get("meta_after"),
                })
            else:
                st.info("No spatial header loaded.")

    st.markdown('<div class="card-label" style="margin-top:16px;">04. Mission Directive Input</div>', unsafe_allow_html=True)

    default_query = (
        "What changed between these two images?"
        if is_bitemporal else
        "Highlight the water body referred to in the query."
    )

    col_input, col_action = st.columns([3.5, 1])
    with col_input:
        user_directive = st.text_input(
            "Query Input",
            value=default_query,
            label_visibility="collapsed",
            key=f"query_input_{'bitemporal' if is_bitemporal else 'single'}",
        )
    with col_action:
        execute = st.button("RUN ROUTE", type="primary", use_container_width=True)

    # --- EXECUTE ROUTER DIRECTLY FROM agent_router.py ---
    if execute:
        if not is_bitemporal:
            meta_context = st.session_state.get(
                "meta_str",
                "User uploaded 1 image. Modality: OPTICAL_OR_MULTISPECTRAL."
            )

            if "persisted_img_path" in st.session_state and os.path.exists(st.session_state["persisted_img_path"]):
                active_img_path = st.session_state["persisted_img_path"]
            else:
                active_img_path = os.path.abspath("data/formatted/images/rsvqa_img_0.jpg")

            st.markdown('<div class="card-label" style="margin-top:20px;">05. SIH Auditable Execution Trace</div>', unsafe_allow_html=True)

            with st.status("Invoking Module 4 Agentic Router...", expanded=True) as status_box:
                route_result = execute_agent_route(meta_context, user_directive, image_path=active_img_path)
                status_box.update(label="Routing Complete — Trace Validated", state="complete")

        else:
            # Bi-temporal mode: require both images before allowing a run.
            has_before = "persisted_img_path_before" in st.session_state and os.path.exists(st.session_state["persisted_img_path_before"])
            has_after = "persisted_img_path_after" in st.session_state and os.path.exists(st.session_state["persisted_img_path_after"])

            if not (has_before and has_after):
                st.error("Bi-Temporal mode requires BOTH a Before and an After image before you can RUN ROUTE.")
                route_result = None
            else:
                meta_context = st.session_state.get(
                    "meta_str_bitemporal",
                    "User uploaded 2 images (before/after) for change detection."
                )

                st.markdown('<div class="card-label" style="margin-top:20px;">05. SIH Auditable Execution Trace</div>', unsafe_allow_html=True)

                with st.status("Invoking Module 4 Agentic Router (Bi-Temporal)...", expanded=True) as status_box:
                    route_result = execute_agent_route(
                        meta_context,
                        user_directive,
                        image_path_before=st.session_state["persisted_img_path_before"],
                        image_path_after=st.session_state["persisted_img_path_after"],
                    )
                    status_box.update(label="Routing Complete — Trace Validated", state="complete")

        if route_result is not None:
            tool_name = route_result.get("tool_name")
            tool_args = route_result.get("tool_args")
            tool_output = route_result.get("tool_output")
            latency = route_result.get("latency", 0.0)

            # Parse coordinates only in single-image mode (bounding boxes only
            # make sense for region_grounding on one active image).
            # FIX: match the explicit xmin=/ymin=/xmax=/ymax= keys Engine 2
            # (Grounding DINO) now emits, instead of grabbing every digit in
            # the string (which also caught stray digits from the confidence
            # score, e.g. "0.62").
            if not is_bitemporal and tool_name == "region_grounding" and tool_output:
                xmin_m = re.search(r"xmin=(\d+)", str(tool_output))
                ymin_m = re.search(r"ymin=(\d+)", str(tool_output))
                xmax_m = re.search(r"xmax=(\d+)", str(tool_output))
                ymax_m = re.search(r"ymax=(\d+)", str(tool_output))
                if xmin_m and ymin_m and xmax_m and ymax_m:
                    st.session_state["last_bbox"] = [
                        int(ymin_m.group(1)), int(xmin_m.group(1)),
                        int(ymax_m.group(1)), int(xmax_m.group(1)),
                    ]
                else:
                    st.session_state["last_bbox"] = None
            else:
                st.session_state["last_bbox"] = None

            st.markdown(f"""
            <div class="terminal-window">
                <div class="trace-step"><span class="trace-key">[ROUTER INTENT]</span> <span class="trace-val">DIRECTIVE_PARSED</span></div>
                <div class="trace-step"><span class="trace-key">[TOOL SELECTED]</span> <span class="trace-success">{tool_name}</span></div>
                <div class="trace-step"><span class="trace-key">[EXTRACTED ARGS]</span> <span class="trace-val">{tool_args}</span></div>
                <div class="trace-step"><span class="trace-key">[TOOL OUTPUT]</span> <span class="trace-val">{tool_output}</span></div>
                <div class="trace-step"><span class="trace-key">[BENCHMARK]</span> <span class="trace-val">Latency: {latency:.2f}s | Status: {route_result.get('status')}</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:rgba(16, 185, 129, 0.08); border:1px solid rgba(16, 185, 129, 0.3); border-radius:6px; padding:12px 16px; margin-top:14px; font-size:0.88rem;">
                <span style="color:#10b981; font-weight:600;">AGENT RESPONSE:</span><br>
                {route_result.get('final_answer')}
            </div>
            """, unsafe_allow_html=True)