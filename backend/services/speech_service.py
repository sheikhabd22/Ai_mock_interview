"""Speech-to-Text service using SpeechRecognition library."""
import os
from groq import Groq
import speech_recognition as sr
from pathlib import Path


class SpeechToTextService:
    """Handles audio file transcription."""

    def __init__(self):
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text.
        Supports .wav files directly. For other formats, pydub handles conversion.
        """
        file_path = Path(audio_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Convert to wav if needed using pydub
        if file_path.suffix.lower() not in [".wav"]:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(file_path))
            wav_path = str(file_path.with_suffix(".wav"))
            audio.export(wav_path, format="wav")
            file_path = Path(wav_path)

        with open(file_path, "rb") as audio_file:
            response = self.groq.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return response.text

    def transcribe_from_webm(self, audio_path: str) -> str:
        """
        Transcribe a WebM audio file (common from browser MediaRecorder).
        Converts to WAV first, then transcribes.
        """
        from pydub import AudioSegment
        file_path = Path(audio_path)
        audio = AudioSegment.from_file(str(file_path), format="webm")
        wav_path = str(file_path.with_suffix(".wav"))
        audio.export(wav_path, format="wav")
        return self.transcribe_audio(wav_path)


# Singleton instance
stt_service = SpeechToTextService()
