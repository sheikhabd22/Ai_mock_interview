# AI Mock Interview (Voice-Based)

A voice-driven mock interview platform where users answer questions verbally, and the system evaluates responses using speech-to-text and LLM-based analysis.

This project explores how speech processing and large language models can be combined to simulate a realistic interview experience.

---

## Why this project

Most interview preparation tools are passive — reading or typing answers. This project focuses on a more realistic workflow:

- Speaking instead of typing  
- Thinking under time constraints  
- Receiving structured, actionable feedback  

---

## How it works

1. User selects role and interview type  
2. Backend generates questions using an LLM  
3. User records an audio response  
4. Audio is converted to text (speech-to-text)  
5. Transcript is evaluated using an LLM  
6. Feedback and scores are returned  

---

## System architecture

Frontend (React)  
↓  
FastAPI Backend  
↓  
Speech-to-Text (Whisper / SpeechRecognition)  
↓  
LLM Evaluation Engine  
↓  
Database (SQLite / PostgreSQL)

---

## Tech stack

- Frontend: React  
- Backend: FastAPI  
- AI: LLM (Groq / OpenAI / Ollama)  
- Speech-to-Text: Whisper / SpeechRecognition  
- Database: SQLite (development)  


---

## Evaluation approach

Each response is evaluated based on:

- Clarity  
- Technical accuracy  
- Completeness  
- Communication quality  

The system returns structured feedback along with a score.

---

## Local setup

### Clone repository
```bash
git clone <your-repo>
cd <project>
```

### Backend
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend
```bash
npm install
npm start
```

---

## API endpoints

- `/generate-questions` — Generate questions
- `/upload-audio` — Upload audio response
- `/transcribe` — Convert audio to text
- `/evaluate` — Evaluate answer
- `/final-report` — Get full report

---

## Future enhancements

- Real-time voice conversation  
- Emotion detection  
- Resume-based personalization  
- Performance analytics dashboard  

---

## License

MIT