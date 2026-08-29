import os
import shutil
import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from agent_router import execute_satquery_agent

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SatQuery AI Backend", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "SatQuery AI Backend is running"}

from image_processor import create_web_preview # ADD THIS IMPORT AT THE TOP

# ... (keep all your setup code) ...

@app.post("/api/v1/analyze")
async def analyze_query(
    query: str = Form(...),
    image1: UploadFile = File(...),
    image2: UploadFile = File(None)
):
    try:
        saved_files = []

        file1_path = UPLOAD_DIR / f"{int(time.time())}_{image1.filename}"
        with open(file1_path, "wb") as buffer:
            shutil.copyfileobj(image1.file, buffer)
        saved_files.append(str(file1_path))

        if image2:
            file2_path = UPLOAD_DIR / f"{int(time.time())}_{image2.filename}"
            with open(file2_path, "wb") as buffer:
                shutil.copyfileobj(image2.file, buffer)
            saved_files.append(str(file2_path))

        modality = "SAR/Optical Pair" if image2 else "Single Optical"
        metadata_str = f"User uploaded {len(saved_files)} image(s). Modality: {modality}."

        answer, trace, bounding_box, agent_image_urls = execute_satquery_agent(
            metadata_str, query, saved_image_path=saved_files[0] if saved_files else None
        )

        # --- NEW LOGIC: GUARANTEE PNG URLs FOR REACT ---
        final_image_urls = []
        for url in agent_image_urls:
            if url.lower().endswith('.tif') or url.lower().endswith('.tiff'):
                # Convert the TIF to a PNG preview and append the new web-friendly URL
                filename = url.split('/')[-1]
                local_path = str(UPLOAD_DIR / filename)
                web_url = create_web_preview(local_path)
                final_image_urls.append(web_url)
            else:
                final_image_urls.append(url)

        if image2:
            web_url2 = create_web_preview(str(file2_path))
            final_image_urls.append(web_url2)

        return {
            "status": "success",
            "interaction_id": f"sih_{int(time.time())}",
            "answer": answer,
            "bounding_box": bounding_box,
            "execution_trace": trace,
            "image_urls": final_image_urls # Now guaranteed to be displayable in the browser!
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))