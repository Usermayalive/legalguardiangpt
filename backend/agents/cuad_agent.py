# backend/agents/cuad_agent.py
import json
import re
from datetime import datetime
from typing import Dict, List

class CUADAgent:
    """Agent 2: CUAD Pattern Matcher - Uses CUAD legal patterns for analysis"""
    
    def __init__(self):
        self.name = "CUAD Agent"
        self.role = "Legal Pattern Matching (41 CUAD categories)"
        self.status = "active"
        self.last_active = datetime.now().isoformat()
        
        # Load CUAD sample data
        self.cuad_patterns = self.load_cuad_patterns()
        
        # CUAD's 41 legal categories (simplified for demo)
        self.legal_categories = [
            "Indemnification", "Jurisdiction", "Liability Cap", "Termination",
            "Confidentiality", "Arbitration", "Force Majeure", "Assignment",
            "Warranties", "Representations", "Governing Law", "Severability",
            "Notice", "Amendment", "Entire Agreement", "Counterparts"
        ]
    
    def load_cuad_patterns(self) -> Dict:
        """Load CUAD patterns from sample data"""
        try:
            with open('backend/data/cuad_sample.json', 'r') as f:
                return json.load(f)
        except:
            # Fallback patterns if file doesn't exist
            return self.get_fallback_patterns()
    
    def get_fallback_patterns(self) -> Dict:
        """Fallback CUAD patterns for demo"""
        return {
            "Indemnification": [
                "shall indemnify", "hold harmless", "defend and indemnify",
                "indemnification obligation", "indemnify against"
            ],
            "Jurisdiction": [
                "jurisdiction of", "courts of", "venue shall be",
                "exclusive jurisdiction", "governing jurisdiction"
            ],
            "Liability Cap": [
                "maximum liability", "cap on liability", "not exceed",
                "limit of liability", "aggregate liability"
            ],
            "Termination": [
                "terminate this agreement", "termination for cause",
                "right to terminate", "termination notice"
            ],
            "Arbitration": [
                "binding arbitration", "arbitration shall be",
                "dispute resolution", "arbitration agreement"
            ]
        }
    
    def match_patterns(self, clauses: List[str]) -> Dict:
        """Match clauses against CUAD patterns"""
        self.last_active = datetime.now().isoformat()
        
        matches = []
        for i, clause in enumerate(clauses):
            clause_matches = []
            
            for category, patterns in self.cuad_patterns.items():
                for pattern in patterns:
                    if isinstance(pattern, str) and pattern.lower() in clause.lower():
                        clause_matches.append({
                            "category": category,
                            "pattern": pattern,
                            "confidence": 0.85  # High confidence for exact match
                        })
                        break  # Only need one match per category
            
            if clause_matches:
                matches.append({
                    "clause_index": i,
                    "clause_preview": clause[:100] + "..." if len(clause) > 100 else clause,
                    "matches": clause_matches,
                    "total_matches": len(clause_matches)
                })
        
        return {
            "total_matches": len(matches),
            "matches": matches,
            "categories_found": list(set(
                match["category"] 
                for match_list in matches 
                for match in match_list["matches"]
            )),
            "data_source": "CUAD Legal Patterns"
        }
    
    def get_risk_level(self, category: str) -> str:
        """Get risk level for CUAD category"""
        high_risk = ["Indemnification", "Liability Cap", "Arbitration"]
        medium_risk = ["Jurisdiction", "Termination", "Confidentiality"]
        
        if category in high_risk:
            return "HIGH"
        elif category in medium_risk:
            return "MEDIUM"
        return "LOW"