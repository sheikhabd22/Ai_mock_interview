import groq
import os
from groq import Groq

client = Groq(api_key="dummy")
print("Groq version:", groq.__version__)
print("Has audio:", hasattr(client, "audio"))
if hasattr(client, "audio"):
    print("Has audio.speech:", hasattr(client.audio, "speech"))
