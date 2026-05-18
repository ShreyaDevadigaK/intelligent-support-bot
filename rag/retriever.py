# Vector search

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import os

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query: str, top_k: int = 4) -> list[dict]:
    """
    Embed the query and find the most relevant doc chunks.
    Returns list of { text, source, score }
    """
    pc     = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index  = pc.Index("support-kb")
    
    embedding = EMBED_MODEL.encode(query).tolist()
    
    results = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    chunks = []
    for match in results.matches:
        if match.score > 0.4:   # confidence threshold — drop weak matches
            chunks.append({
                "text":   match.metadata["text"],
                "source": match.metadata["source"],
                "score":  round(match.score, 3)
            })
    
    return chunks