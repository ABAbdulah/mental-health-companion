import chromadb
from chromadb.utils import embedding_functions

# ===== Config =====
DB_DIR = "db"
COLLECTION_NAME = "documents"
EMBED_MODEL = "all-MiniLM-L6-v2"

# ===== Load the DB and embedding model =====
client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
)

# ===== Retrieval function =====
def retrieve(query: str, k: int = 5):
    """
    Retrieves top-k relevant document chunks from ChromaDB.
    """
    results = collection.query(
        query_texts=[query],
        n_results=k
    )

    docs = results.get("documents", [[]])[0]  # Flatten first batch
    metas = results.get("metadatas", [[]])[0]

    return [{"text": doc, "metadata": meta} for doc, meta in zip(docs, metas)]

# ===== Test run =====
if __name__ == "__main__":
    query = "What is artificial intelligence?"
    matches = retrieve(query, k=3)
    print("\nTop matches:")
    for match in matches:
        print(f"- {match['text'][:200]}... (source: {match['metadata'].get('source')})")
