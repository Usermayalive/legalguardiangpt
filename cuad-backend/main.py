from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import asyncio
from datetime import datetime

from cuad_loader import CUADLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CUAD Legal RAG API", 
    description="RAG backend for legal document analysis using CUAD dataset",
    version="2.0.0"
)

# CORS middleware - ALLOW ALL for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize loader with error handling
loader = None
try:
    loader = CUADLoader()
    logger.info("✅ CUADLoader initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize CUADLoader: {e}")
    loader = None

class SearchQuery(BaseModel):
    query: str
    n_results: Optional[int] = 5
    min_similarity: Optional[float] = 0.3

class DocumentAnalysisRequest(BaseModel):
    document_text: str
    question: Optional[str] = None
    n_references: Optional[int] = 3

class Clause(BaseModel):
    text: str
    clause_type: str
    similarity_score: float
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    collection_info: Dict[str, Any]
    version: str = "2.0.0"

@app.get("/")
async def root():
    return {
        "service": "CUAD Legal RAG API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/health": "Service health check",
            "/search": "Search similar legal clauses",
            "/analyze": "Analyze document with CUAD context",
            "/init": "Initialize database"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    """Service health check with detailed status"""
    collection_info = {"status": "not_initialized", "document_count": 0}
    
    if loader:
        try:
            collection_info = loader.get_collection_info()
        except Exception as e:
            logger.error(f"Health check error: {e}")
    
    return HealthResponse(
        status="healthy" if loader else "degraded",
        service="CUAD Legal RAG",
        timestamp=datetime.now().isoformat(),
        collection_info=collection_info,
        version="2.0.0"
    )

@app.post("/search", response_model=List[Clause])
async def search_clauses(search: SearchQuery):
    """Search for similar legal clauses in CUAD database"""
    if not loader:
        raise HTTPException(status_code=503, detail="CUADLoader not initialized")
    
    try:
        logger.info(f"Search request: '{search.query[:50]}...'")
        
        # Add artificial delay to simulate processing (remove in production)
        await asyncio.sleep(0.1)
        
        results = loader.search_similar_clauses(
            query=search.query,
            n_results=search.n_results,
            min_score=search.min_similarity
        )
        
        formatted_results = []
        for r in results:
            formatted_results.append(Clause(
                text=r['text'],
                clause_type=r['metadata']['clause_type'],
                similarity_score=r['similarity_score'],
                metadata=r['metadata']
            ))
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/analyze")
async def analyze_document(request: DocumentAnalysisRequest):
    """Analyze a legal document with CUAD context"""
    if not loader:
        raise HTTPException(status_code=503, detail="CUADLoader not initialized")
    
    try:
        logger.info(f"Analyze request: document={len(request.document_text)} chars, question={request.question}")
        
        # Add artificial delay
        await asyncio.sleep(0.2)
        
        search_text = request.document_text[:1000] if request.document_text else ""
        relevant_clauses = loader.search_similar_clauses(
            query=search_text,
            n_results=request.n_references
        )
        
        question_clauses = []
        if request.question:
            question_clauses = loader.search_similar_clauses(
                query=request.question,
                n_results=2
            )
        
        all_clauses = relevant_clauses + question_clauses
        unique_clauses = []
        seen_texts = set()
        
        for clause in all_clauses:
            if clause['text'] not in seen_texts:
                seen_texts.add(clause['text'])
                unique_clauses.append(clause)
        
        context_text = ""
        if unique_clauses:
            context_text = "\n\n".join([
                f"CUAD Reference {i+1} [{c['metadata']['clause_type']} - Similarity: {c['similarity_score']:.2f}]:\n{c['text']}"
                for i, c in enumerate(unique_clauses)
            ])
        
        document_preview = request.document_text[:500] + "..." if len(request.document_text) > 500 else request.document_text
        
        # Simplified analysis prompt
        analysis_prompt = f"""Analyze this legal document excerpt."""
        
        if context_text:
            analysis_prompt += f"\n\nRelevant legal references:\n{context_text}"
        
        if request.question:
            analysis_prompt += f"\n\nQuestion: {request.question}"
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "document_preview": document_preview,
            "document_length": len(request.document_text),
            "relevant_clauses_found": len(unique_clauses),
            "cuad_context": context_text,
            "clauses": unique_clauses,
            "analysis_prompt": analysis_prompt,
            "analysis_ready": len(unique_clauses) > 0
        }
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/init")
async def initialize_database():
    """Initialize or reinitialize the CUAD database"""
    global loader
    
    try:
        logger.info("Initializing database...")
        
        # Reinitialize loader
        loader = CUADLoader()
        
        # Load and process clauses
        clauses = loader.load_and_process_cuad()
        collection = loader.create_embeddings(clauses)
        
        return {
            "status": "initialized",
            "timestamp": datetime.now().isoformat(),
            "clauses_loaded": len(clauses),
            "collection": "legal_clauses",
            "message": f"Database initialized with {len(clauses)} legal clauses"
        }
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Initialization error: {str(e)}")

@app.get("/simple-test")
async def simple_test():
    """Simple test endpoint for debugging"""
    return {
        "status": "ok",
        "message": "CUAD API is working",
        "timestamp": datetime.now().isoformat(),
        "loader_initialized": loader is not None
    }

if __name__ == "__main__":
    # Start server with detailed logging
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )