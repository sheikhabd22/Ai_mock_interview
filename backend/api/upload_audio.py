from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import uuid
from backend.services.speech_service import stt_service
from backend.core.config import UPLOAD_DIR
from fastapi import HTTPException

router = APIRouter(tags=["Upload"])

@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """Upload an audio file and return the saved file path."""
    allowed_extensions = {".wav", ".mp3", ".webm", ".ogg", ".m4a"}
    ext = Path(file.filename).suffix.lower() if file.filename else ".webm"
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {ext}")

    filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {"filename": filename, "path": str(file_path)}


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Upload audio and transcribe it to text."""
    ext = Path(file.filename).suffix.lower() if file.filename else ".webm"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        if ext == ".webm":
            transcript = stt_service.transcribe_from_webm(str(file_path))
        else:
            transcript = stt_service.transcribe_audio(str(file_path))
        return {"transcript": transcript, "filename": filename}
    except Exception as e:
        # Keep interview flow usable even when local audio codecs/services are unavailable.
        return {
            "transcript": "[Transcription unavailable. Please type or retry after configuring ffmpeg/speech service.]",
            "filename": filename,
            "warning": f"Transcription failed: {str(e)}",
        }

