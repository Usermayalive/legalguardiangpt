# backend/agents/explain_agent.py - Should be separate
from datetime import datetime
from typing import Dict, List

class ExplainAgent:
    """Agent 6: RAG-based Explanations"""
    
    def __init__(self):
        self.name = "Explain Agent"
        self.role = "RAG-based Explanations"
        self.status = "active"
        self.last_active = datetime.now().isoformat()
    
    def explain(self, risk_score: float, threats: List[str], language: str) -> str:
        summary = f"Risk Score: {risk_score}/10. "
        if threats:
            summary += f"Threats: {'; '.join(threats)}. "
        summary += "Review recommended before signing."
        return summary