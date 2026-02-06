# backend/agents/embedding_agent.py
from datetime import datetime
import numpy as np

class EmbeddingAgent:
    """Agent 3: Semantic Vector Generation - Creates embeddings for legal text"""
    
    def __init__(self):
        self.name = "Embedding Agent"
        self.role = "Semantic Vector Generation"
        self.status = "active"
        self.last_active = datetime.now().isoformat()
        
        # For demo purposes - in real implementation, use LegalBERT
        self.vocab = {
            "indemnify": [0.9, 0.1, 0.2],
            "liability": [0.8, 0.3, 0.1],
            "termination": [0.2, 0.7, 0.4],
            "jurisdiction": [0.3, 0.1, 0.9],
            "arbitration": [0.7, 0.5, 0.2],
            "confidential": [0.4, 0.8, 0.3],
            "damages": [0.9, 0.2, 0.1],
            "waiver": [0.2, 0.6, 0.7],
            "default": [0.8, 0.4, 0.3],
            "breach": [0.7, 0.3, 0.5],
        }
    
    def encode(self, text: str) -> list:
        """Generate semantic embedding for text"""
        self.last_active = datetime.now().isoformat()
        
        words = text.lower().split()
        vectors = []
        
        for word in words:
            if word in self.vocab:
                vectors.append(self.vocab[word])
            else:
                # Random vector for unknown words
                vectors.append([np.random.random() for _ in range(3)])
        
        if vectors:
            # Average all word vectors
            avg_vector = np.mean(vectors, axis=0).tolist()
        else:
            avg_vector = [0.0, 0.0, 0.0]
        
        return {
            "vector": avg_vector,
            "dimension": len(avg_vector),
            "words_processed": len(words),
            "model": "LegalBERT-Sim (Demo)"
        }
    
    def encode_batch(self, texts: list) -> list:
        """Encode multiple texts"""
        self.last_active = datetime.now().isoformat()
        
        embeddings = []
        for text in texts:
            embeddings.append(self.encode(text))
        
        return embeddings
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        emb1 = self.encode(text1)["vector"]
        emb2 = self.encode(text2)["vector"]
        
        # Cosine similarity
        dot_product = sum(a*b for a, b in zip(emb1, emb2))
        norm1 = sum(a*a for a in emb1) ** 0.5
        norm2 = sum(b*b for b in emb2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)