import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# ===== Config =====
DATA_DIR = "data"
DB_DIR = "db"
CHUNK_SIZE = 500  # tokens/words
CHUNK_OVERLAP = 100

# ===== Helper: Split text into chunks =====
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# ===== PDF Text Extraction =====
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# ===== Ingestion for one PDF =====
def process_pdf(pdf_path: str):
    """Process a single PDF and add its chunks to the vector DB."""
    os.makedirs(DB_DIR, exist_ok=True)

    print("Loading embedding model...")
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')

    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(
        name="documents",
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    )

    print(f"Processing {pdf_path}...")
    raw_text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(raw_text)
    print(f"Extracted {len(chunks)} chunks.")

    for idx, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{os.path.basename(pdf_path)}_{idx}"],
            documents=[chunk],
            metadatas=[{"source": os.path.basename(pdf_path)}]
        )

    print(f"PDF {pdf_path} added to vector DB at {DB_DIR}.")

# ===== Bulk ingestion =====
def main():
    os.makedirs(DB_DIR, exist_ok=True)
    for filename in os.listdir(DATA_DIR):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(DATA_DIR, filename)
            process_pdf(filepath)
    print("All PDFs processed.")

if __name__ == "__main__":
    main()
