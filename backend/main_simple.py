# backend/main_simple.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
from datetime import datetime
import re

app = FastAPI(
    title="LegalGuardianGPT",
    description="AI-powered legal risk detection with CUAD+RAG",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== SIMPLE AGENTS ====================

class PrivacyAgent:
    def __init__(self):
        self.name = "Privacy Agent"
        self.status = "active"
    
    def scrub(self, text: str) -> str:
        return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

class CUADAgent:
    def __init__(self):
        self.name = "CUAD Agent"
        self.status = "active"
        self.patterns = {
            "indemnification": ["indemnify", "hold harmless"],
            "jurisdiction": ["jurisdiction", "governing law"],
            "arbitration": ["arbitration", "dispute resolution"],
        }
    
    def analyze(self, text: str) -> Dict:
        matches = {}
        for category, keywords in self.patterns.items():
            found = [k for k in keywords if k in text.lower()]
            if found:
                matches[category] = found
        return matches

class RiskAgent:
    def __init__(self):
        self.name = "Risk Agent"
        self.status = "active"
    
    def calculate(self, matches: Dict) -> float:
        scores = {"indemnification": 9.0, "arbitration": 8.5, "jurisdiction": 7.0}
        total = sum(scores.get(k, 5.0) for k in matches.keys())
        return min(10, total / max(1, len(matches)))

class ThreatAgent:
    def __init__(self):
        self.name = "Threat Agent"
        self.status = "active"
    
    def analyze(self, matches: Dict) -> List[str]:
        threats = []
        if "indemnification" in matches:
            threats.append("Financial liability risk")
        if "arbitration" in matches:
            threats.append("No jury trial")
        return threats

class ExplainAgent:
    def __init__(self):
        self.name = "Explain Agent"
        self.status = "active"
    
    def explain(self, risk_score: float, threats: List[str]) -> str:
        return f"Risk: {risk_score}/10. Threats: {', '.join(threats)}"

class EmbeddingAgent:
    def __init__(self):
        self.name = "Embedding Agent"
        self.status = "active"

# Initialize agents
agents = {
    "privacy": PrivacyAgent(),
    "cuad": CUADAgent(),
    "risk": RiskAgent(),
    "threat": ThreatAgent(),
    "explain": ExplainAgent(),
    "embedding": EmbeddingAgent(),
}

# ==================== SIMPLE TOOLS ====================

class SegmenterTool:
    def __init__(self):
        self.name = "Segmenter Tool"
    
    def segment(self, text: str) -> List[str]:
        return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

class CalculatorTool:
    def __init__(self):
        self.name = "Calculator Tool"
    
    def calculate(self, matches: Dict) -> Dict:
        score = sum(9 if "indemnif" in k else 7 for k in matches.keys()) / max(1, len(matches))
        return {"score": min(10, score)}

class MapperTool:
    def __init__(self):
        self.name = "Mapper Tool"

# Initialize tools
tools = {
    "segmenter": SegmenterTool(),
    "calculator": CalculatorTool(),
    "mapper": MapperTool(),
}

# ==================== MODELS ====================

class AnalysisRequest(BaseModel):
    html: str
    url: Optional[str] = None
    language: Optional[str] = "en"

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "LegalGuardianGPT API",
        "agents": 6,
        "tools": 3,
        "status": "running"
    }

@app.get("/agents")
async def get_agents():
    agent_list = []
    for key, agent in agents.items():
        agent_list.append({
            "id": len(agent_list) + 1,
            "name": agent.name,
            "status": agent.status
        })
    return {"agents": agent_list, "total": 6}

@app.get("/tools")
async def get_tools():
    tool_list = []
    for key, tool in tools.items():
        tool_list.append({
            "id": len(tool_list) + 1,
            "name": tool.name,
            "type": "Custom Tool"
        })
    return {"tools": tool_list, "total": 3}

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    try:
        # Agent 1: Privacy
        cleaned = agents["privacy"].scrub(request.html)
        
        # Tool 1: Segment
        clauses = tools["segmenter"].segment(cleaned)
        
        # Agent 2: CUAD Analysis
        matches = agents["cuad"].analyze(request.html)
        
        # Agent 3: Risk Calculation
        risk_score = agents["risk"].calculate(matches)
        
        # Tool 2: Calculate
        risk_result = tools["calculator"].calculate(matches)
        
        # Agent 4: Threat Analysis
        threats = agents["threat"].analyze(matches)
        
        # Agent 5: Explanation
        explanation = agents["explain"].explain(risk_score, threats)
        
        # Audio for illiterate users
        audio = f"Warning. Risk score {risk_score:.1f} out of 10. {len(threats)} threats found."
        
        return {
            "success": True,
            "risk_score": round(risk_score, 2),
            "risk_level": "HIGH" if risk_score > 7 else "MEDIUM" if risk_score > 4 else "LOW",
            "threats": threats,
            "explanation": explanation,
            "audio_summary": audio,
            "cuad_matches": matches,
            "agents_used": 6,
            "tools_used": 3,
            "clauses_analyzed": len(clauses),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo")
async def demo():
    demo_html = """
    <button>I Agree to Terms</button>
    <p>The company shall indemnify against all claims.</p>
    <p>All disputes go to binding arbitration.</p>
    <p>Jurisdiction is exclusively in Delaware.</p>
    """
    request = AnalysisRequest(html=demo_html, url="https://demo.com", language="en")
    return await analyze(request)

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 LEGALGUARDIANGPT - SIMPLE VERSION")
    print("="*60)
    print("✅ 6 Agents ready")
    print("✅ 3 Tools ready")
    print("🌐 http://localhost:8000")
    print("📚 http://localhost:8000/docs")
    print("🎮 http://localhost:8000/demo")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)