from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os

from scripts.ingest import process_pdf
from backend.model import ask_model

app = FastAPI()

# ==== CORS CONFIG ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== UPLOAD DIRECTORY ====
UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==== REQUEST MODELS ====
class ChatRequest(BaseModel):
    session_id: str
    question: str

# ==== ROUTES ====

@app.get("/status")
def status():
    return {"status": "Backend is running"}

@app.get("/ask")
def ask(session_id: str, query: str):
    """
    Simple GET-based query to the chatbot.
    """
    answer = ask_model(session_id, query)
    return {"answer": answer}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """
    Upload and process a PDF into the vector database.
    """
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process and store in vector DB
    process_pdf(file_path)
    return {"status": "Ingested", "file": file.filename}

@app.post("/chat")
def chat(req: ChatRequest):
    """
    POST-based chat endpoint for conversation memory.
    """
    answer = ask_model(req.session_id, req.question)
    return {"answer": answer}
