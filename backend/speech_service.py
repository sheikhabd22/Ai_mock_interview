"""Speech-to-Text service using SpeechRecognition library."""
import os
import speech_recognition as sr
from pathlib import Path


class SpeechToTextService:
    """Handles audio file transcription."""

    def __init__(self):
        self.recognizer = sr.Recognizer()

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

        # Transcribe using SpeechRecognition with Google Web Speech API
        with sr.AudioFile(str(file_path)) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = self.recognizer.record(source)

        try:
            # Use Google's free Web Speech API
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "[Could not understand audio]"
        except sr.RequestError as e:
            raise RuntimeError(f"Speech recognition service error: {e}")

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
