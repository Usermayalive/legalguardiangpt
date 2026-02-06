# backend/agents/threat_agent.py - CORRECTED
from datetime import datetime
from typing import Dict, List

class ThreatAgent:
    """Agent 5: Threat Chain Detection - Identifies risk propagation paths"""
    
    def __init__(self):
        self.name = "Threat Agent"
        self.role = "Threat Chain Detection"
        self.status = "active"
        self.last_active = datetime.now().isoformat()
        
        # Threat relationships
        self.threat_relationships = {
            "indemnification": ["financial_loss", "lawsuit"],
            "jurisdiction": ["travel_costs", "legal_disadvantage"],
            "arbitration": ["no_jury_trial", "confidential_process"],
            "liability_cap": ["limited_compensation"],
            "termination": ["service_disruption", "penalty_fees"],
        }
    
    def analyze(self, matches: Dict) -> List[str]:
        """Analyze threat chains"""
        self.last_active = datetime.now().isoformat()
        
        threats = []
        if "indemnification" in matches:
            threats.append("High financial liability risk")
        if "jurisdiction" in matches:
            threats.append("May have to travel for legal proceedings")
        if "arbitration" in matches:
            threats.append("Legal disputes may bypass courts")
        if "liability" in matches:
            threats.append("Compensation may be limited")
        
        return threats
    
    def get_threat_chains(self, matches: Dict) -> List[Dict]:
        """Get threat chains as structured data"""
        chains = []
        
        if "indemnification" in matches:
            chains.append({
                "source": "Indemnification clause",
                "threat": "Financial liability",
                "consequence": "Could be responsible for others' legal costs",
                "severity": "HIGH"
            })
        
        if "arbitration" in matches:
            chains.append({
                "source": "Arbitration clause", 
                "threat": "Limited legal recourse",
                "consequence": "No right to jury trial, limited appeals",
                "severity": "HIGH"
            })
        
        return chains