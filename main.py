from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
from minimal_tts_rvc.tts_rvc_cli import tts_rvc_pipeline, list_models
from minimal_tts_rvc.models_config import MODELS

app = FastAPI(title="Minimal TTS + RVC API", description="Text-to-Speech and RVC voice conversion backend.")

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SynthesizeRequest(BaseModel):
    text: str
    model: str

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Minimal TTS + RVC API</h1>
    <p>Use <a href='/docs'>/docs</a> for Swagger UI.</p>
    <ul>
      <li>GET /models - List available models</li>
      <li>POST /synthesize - Synthesize speech (see docs)</li>
      <li>GET /health - Health check</li>
    </ul>
    """

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/models")
def get_models():
    models = list_models()
    return {"models": models}

@app.post("/synthesize")
def synthesize(req: SynthesizeRequest):
    if req.model not in MODELS:
        raise HTTPException(status_code=400, detail=f"Model '{req.model}' not found.")
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")
    # Generate unique output file per request
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    unique_id = uuid.uuid4().hex[:8]
    model_choice = req.model
    out_path = os.path.join(output_dir, f"{model_choice}_{unique_id}_rvc.mp3")
    try:
        # Patch tts_rvc_pipeline to allow custom output path
        rvc_path = tts_rvc_pipeline(req.text, model_choice, output_dir=output_dir)
        # Rename to unique file for download
        os.rename(rvc_path, out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {e}")
    # Return as file response
    return FileResponse(out_path, media_type="audio/mpeg", filename=os.path.basename(out_path)) 