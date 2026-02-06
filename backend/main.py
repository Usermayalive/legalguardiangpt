# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
from datetime import datetime

app = FastAPI(
    title="LegalGuardianGPT",
    description="AI-powered legal risk detection with CUAD+RAG for illiterate users",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================
class AnalysisRequest(BaseModel):
    html: str
    url: Optional[str] = None
    language: Optional[str] = "en"

class AgentStatus(BaseModel):
    name: str
    role: str
    status: str
    last_active: str

# ==================== 6 AGENTS INITIALIZATION ====================
from agents.privacy_agent import PrivacyAgent
from agents.cuad_agent import CUADAgent
from agents.embedding_agent import EmbeddingAgent
from agents.risk_agent import RiskAgent
from agents.threat_agent import ThreatAgent
from agents.explain_agent import ExplainAgent

# ==================== 3 TOOLS INITIALIZATION ====================
from tools.cuad_segmenter import CUADSegmenter
from tools.hybrid_calculator import HybridCalculator
from tools.threat_mapper import ThreatMapper

# Initialize all components
print("🚀 Initializing LegalGuardianGPT...")

# 6 AGENTS
privacy_agent = PrivacyAgent()          # Agent 1
cuad_agent = CUADAgent()                # Agent 2
embedding_agent = EmbeddingAgent()      # Agent 3
risk_agent = RiskAgent()                # Agent 4
threat_agent = ThreatAgent()            # Agent 5
explain_agent = ExplainAgent()          # Agent 6

# 3 TOOLS
cuad_segmenter = CUADSegmenter()        # Tool 1
risk_calculator = HybridCalculator()    # Tool 2
threat_mapper = ThreatMapper()          # Tool 3

print("✅ 6 Agents initialized")
print("✅ 3 Tools initialized")

# ==================== API ENDPOINTS ====================
@app.get("/")
async def root():
    return {
        "message": "LegalGuardianGPT API",
        "version": "2.0",
        "agents": 6,
        "tools": 3,
        "status": "active",
        "features": [
            "CUAD-based legal pattern matching",
            "RAG-powered explanations", 
            "Threat chain visualization",
            "Audio summaries for illiterate users",
            "Real-time risk scoring"
        ]
    }

@app.get("/agents")
async def get_agents():
    """Returns all 6 agents with their status"""
    agents = [
        {
            "id": 1,
            "name": "Privacy Agent",
            "role": "PII Scrubber & Data Protection",
            "status": privacy_agent.status,
            "last_active": privacy_agent.last_active
        },
        {
            "id": 2, 
            "name": "CUAD Agent",
            "role": "Legal Pattern Matching (41 CUAD categories)",
            "status": cuad_agent.status,
            "last_active": cuad_agent.last_active
        },
        {
            "id": 3,
            "name": "Embedding Agent", 
            "role": "Semantic Vector Generation",
            "status": embedding_agent.status,
            "last_active": embedding_agent.last_active
        },
        {
            "id": 4,
            "name": "Risk Agent",
            "role": "Hybrid Risk Scoring",
            "status": risk_agent.status,
            "last_active": risk_agent.last_active
        },
        {
            "id": 5,
            "name": "Threat Agent",
            "role": "Threat Chain Detection",
            "status": threat_agent.status,
            "last_active": threat_agent.last_active
        },
        {
            "id": 6,
            "name": "Explain Agent",
            "role": "RAG-based Explanations",
            "status": explain_agent.status,
            "last_active": explain_agent.last_active
        }
    ]
    return {"agents": agents, "total": 6}

@app.get("/tools")
async def get_tools():
    """Returns all 3 custom tools"""
    tools = [
        {
            "id": 1,
            "name": "CUAD Segmenter",
            "description": "Custom legal document segmentation using CUAD patterns",
            "type": "Custom Tool",
            "status": "active"
        },
        {
            "id": 2,
            "name": "Hybrid Risk Calculator", 
            "description": "Proprietary risk scoring algorithm (CUAD + ML + Heuristics)",
            "type": "Custom Tool",
            "status": "active"
        },
        {
            "id": 3,
            "name": "Threat Mapper",
            "description": "Graph-based threat chain visualization",
            "type": "Custom Tool", 
            "status": "active"
        }
    ]
    return {"tools": tools, "total": 3}

@app.post("/analyze")
async def analyze_webpage(request: AnalysisRequest):
    """
    Complete analysis pipeline using all 6 agents and 3 tools
    """
    print(f"🔍 Analyzing content from {request.url or 'unknown'}")
    
    try:
        # ========== AGENT 1: PRIVACY PROTECTION ==========
        print("🛡️ Agent 1: Privacy Agent - Scrubbing PII...")
        cleaned_html = privacy_agent.scrub_pii(request.html)
        
        # ========== TOOL 1: CUAD SEGMENTATION ==========
        print("🔪 Tool 1: CUAD Segmenter - Extracting clauses...")
        clauses = cuad_segmenter.segment(cleaned_html)
        
        # ========== AGENT 2: CUAD PATTERN MATCHING ==========
        print("📊 Agent 2: CUAD Agent - Pattern matching...")
        cuad_results = cuad_agent.match_patterns(clauses)
        
        # ========== AGENT 3: SEMANTIC EMBEDDINGS ==========
        print("🔤 Agent 3: Embedding Agent - Generating vectors...")
        embeddings = embedding_agent.encode(clauses)
        
        # ========== TOOL 2: RISK CALCULATION ==========
        print("📈 Tool 2: Hybrid Calculator - Scoring risks...")
        risk_scores = risk_calculator.calculate(clauses, cuad_results, embeddings)
        
        # ========== AGENT 4: RISK ANALYSIS ==========
        print("⚠️ Agent 4: Risk Agent - Analyzing scores...")
        risk_analysis = risk_agent.analyze(risk_scores)
        
        # ========== TOOL 3: THREAT MAPPING ==========
        print("🔗 Tool 3: Threat Mapper - Building threat chains...")
        threat_chains = threat_mapper.map_threats(clauses, risk_scores)
        
        # ========== AGENT 5: THREAT ANALYSIS ==========
        print("🚨 Agent 5: Threat Agent - Analyzing chains...")
        threat_analysis = threat_agent.analyze(threat_chains)
        
        # ========== AGENT 6: EXPLANATION GENERATION ==========
        print("💡 Agent 6: Explain Agent - Generating explanations...")
        explanations = explain_agent.explain(
            clauses=clauses,
            risk_analysis=risk_analysis,
            threat_analysis=threat_analysis,
            language=request.language
        )
        
        # ========== COMPILE RESULTS ==========
        final_risk_score = risk_analysis.get("final_score", 0)
        risk_level = "HIGH" if final_risk_score > 7 else "MEDIUM" if final_risk_score > 4 else "LOW"
        
        # Generate audio summary for illiterate users
        audio_summary = f"Warning: {risk_level} risk detected. {len(threat_chains.get('chains', []))} threat chains found. Score: {final_risk_score}/10."
        
        return {
            "success": True,
            "risk_score": round(final_risk_score, 2),
            "risk_level": risk_level,
            "clauses_analyzed": len(clauses),
            "cuad_matches": len(cuad_results.get("matches", [])),
            "threat_chains": threat_chains.get("chains", []),
            "audio_summary": audio_summary,
            "explanations": explanations,
            "agents_used": 6,
            "tools_used": 3,
            "timestamp": datetime.now().isoformat(),
            "data_source": "CUAD Dataset + Custom RAG"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "backend": "running",
        "agents": "6/6 active",
        "tools": "3/3 active",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🚀 LEGALGUARDIANGPT BACKEND READY")
    print("="*50)
    print("📊 6 Agents Initialized")
    print("🛠️  3 Tools Initialized")
    print("🌐 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("="*50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)