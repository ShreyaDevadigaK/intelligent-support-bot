 # Chunk + embed + store docs

from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from pathlib import Path
import hashlib

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")  # fast, good quality
CHUNK_SIZE  = 400   # characters
CHUNK_OVERLAP = 80

def chunk_text(text: str) -> list[str]:
    """Simple overlapping chunker."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if len(c) > 50]  # drop tiny fragments

def index_documents(docs_dir: str = "data/docs"):
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    # Create index if it doesn't exist
    if "support-kb" not in pc.list_indexes().names():
        pc.create_index(
            name="support-kb",
            dimension=384,   # matches all-MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    index = pc.Index("support-kb")
    
    for doc_path in Path(docs_dir).rglob("*.txt"):
        text = doc_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = EMBED_MODEL.encode(chunk).tolist()
            doc_id = hashlib.md5(f"{doc_path.name}-{i}".encode()).hexdigest()
            vectors.append({
                "id":     doc_id,
                "values": embedding,
                "metadata": {
                    "text":     chunk,
                    "source":   doc_path.name,
                    "chunk_id": i
                }
            })
        
        # Upsert in batches of 100
        for i in range(0, len(vectors), 100):
            index.upsert(vectors=vectors[i:i+100])
        
        print(f"Indexed {len(vectors)} chunks from {doc_path.name}")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    index_documents()