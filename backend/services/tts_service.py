

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import os
from groq import Groq

router = APIRouter()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class SpeakRequest(BaseModel):
    text: str

@router.post("/speak")
def speak(data: SpeakRequest):
    try:
        filename = "temp.wav"

        response = client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice="troy",
            input=data.text,
            response_format="wav"
        )

        response.write_to_file(filename)

        with open(filename, "rb") as f:
            audio_bytes = f.read()

        return Response(content=audio_bytes, media_type="audio/wav")

    except Exception as e:
        print("TTS Error:", e)
        raise HTTPException(status_code=500, detail="TTS failed")