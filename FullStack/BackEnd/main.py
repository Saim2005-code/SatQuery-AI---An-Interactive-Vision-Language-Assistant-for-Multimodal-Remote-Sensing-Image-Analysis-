import os
import shutil
import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from database import ping_database, client
from fastapi.staticfiles import StaticFiles

# IMPORT YOUR NEW AGENT!
from agent_router import execute_satquery_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await ping_database()
    yield
    client.close()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SatQuery AI Backend", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/analyze")
async def analyze_query(
    query: str = Form(...),
    image1: UploadFile = File(...),
    image2: UploadFile = File(None)
):
    try:
        saved_files = []
        
        # Save images securely
        file1_path = UPLOAD_DIR / f"{int(time.time())}_{image1.filename}"
        with open(file1_path, "wb") as buffer:
            shutil.copyfileobj(image1.file, buffer)
        saved_files.append(str(file1_path))

        if image2:
            file2_path = UPLOAD_DIR / f"{int(time.time())}_{image2.filename}"
            with open(file2_path, "wb") as buffer:
                shutil.copyfileobj(image2.file, buffer)
            saved_files.append(str(file2_path))

        # --- THE AI BRAIN INTEGRATION ---
        # 1. Build metadata string for the LLM
        modality = "SAR/Optical Pair" if image2 else "Single Optical"
        metadata_str = f"User uploaded {len(saved_files)} image(s). Modality: {modality}."
        
        # 2. Trigger LangChain!
        answer, trace, bounding_box = execute_satquery_agent(metadata_str, query)

        # 3. Send payload back to React
        return {
            "status": "success",
            "interaction_id": f"sih_{int(time.time())}",
            "answer": answer,
            "bounding_box": bounding_box,
            "execution_trace": trace,
            "image_urls": [f"/static/uploads/{Path(f).name}" for f in saved_files]
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))