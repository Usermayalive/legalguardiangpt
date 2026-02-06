# backend/agents/risk_agent.py
from datetime import datetime
from typing import Dict, List

class RiskAgent:
    """Agent 4: Hybrid Risk Scoring - Combines multiple factors for risk assessment"""
    
    def __init__(self):
        self.name = "Risk Agent"
        self.role = "Hybrid Risk Scoring"
        self.status = "active"
        self.last_active = datetime.now().isoformat()
        
        # Risk weights for different factors
        self.weights = {
            "cuad_match": 0.4,      # CUAD pattern matching
            "clause_length": 0.1,    # Longer clauses are riskier
            "keyword_density": 0.2,  # Density of risky keywords
            "ambiguity": 0.3,        # Ambiguous language
        }
        
        # High-risk keywords with severity scores
        self.risk_keywords = {
            "indemnify": 9.0,
            "waiver": 8.0,
            "liability": 7.5,
            "arbitration": 8.5,
            "jurisdiction": 7.0,
            "termination": 6.5,
            "confidential": 5.0,
            "damages": 8.0,
            "breach": 7.0,
            "default": 7.5,
            "exclusive": 6.0,
            "irrevocable": 8.0,
            "binding": 7.0,
            "sole discretion": 8.5,
        }
    
    def analyze(self, risk_data: Dict) -> Dict:
        """Analyze risk scores and generate final assessment"""
        self.last_active = datetime.now().isoformat()
        
        # Extract data
        cuad_matches = risk_data.get("cuad_matches", [])
        clauses = risk_data.get("clauses", [])
        
        # Calculate individual risk factors
        cuad_score = self._calculate_cuad_score(cuad_matches)
        length_score = self._calculate_length_score(clauses)
        keyword_score = self._calculate_keyword_score(clauses)
        ambiguity_score = self._calculate_ambiguity_score(clauses)
        
        # Combine scores with weights
        final_score = (
            cuad_score * self.weights["cuad_match"] +
            length_score * self.weights["clause_length"] +
            keyword_score * self.weights["keyword_density"] +
            ambiguity_score * self.weights["ambiguity"]
        )
        
        # Determine risk level
        risk_level = self._get_risk_level(final_score)
        
        return {
            "final_score": min(10, round(final_score, 2)),
            "risk_level": risk_level,
            "component_scores": {
                "cuad_pattern_matching": round(cuad_score, 2),
                "clause_complexity": round(length_score, 2),
                "keyword_density": round(keyword_score, 2),
                "language_ambiguity": round(ambiguity_score, 2),
            },
            "weights_used": self.weights,
            "high_risk_keywords_found": self._find_keywords(clauses)
        }
    
    def _calculate_cuad_score(self, cuad_matches: List) -> float:
        """Score based on CUAD pattern matches"""
        if not cuad_matches:
            return 0.0
        
        base_score = 0
        for match in cuad_matches:
            category = match.get("category", "").lower()
            if "indemnif" in category:
                base_score += 9.0
            elif "arbitration" in category:
                base_score += 8.5
            elif "liability" in category:
                base_score += 8.0
            else:
                base_score += 6.0
        
        return min(10, base_score / max(1, len(cuad_matches)))
    
    def _calculate_length_score(self, clauses: List[str]) -> float:
        """Longer clauses are riskier (more room for hidden terms)"""
        if not clauses:
            return 0.0
        
        avg_length = sum(len(c.split()) for c in clauses) / len(clauses)
        
        if avg_length > 100:
            return 9.0
        elif avg_length > 50:
            return 7.0
        elif avg_length > 25:
            return 5.0
        else:
            return 3.0
    
    def _calculate_keyword_score(self, clauses: List[str]) -> float:
        """Score based on density of risk keywords"""
        if not clauses:
            return 0.0
        
        total_keywords = 0
        total_words = 0
        
        for clause in clauses:
            words = clause.lower().split()
            total_words += len(words)
            
            for keyword, score in self.risk_keywords.items():
                if keyword in clause.lower():
                    total_keywords += 1
        
        density = total_keywords / max(1, total_words)
        return min(10, density * 100)  # Scale to 0-10
    
    def _calculate_ambiguity_score(self, clauses: List[str]) -> float:
        """Detect ambiguous language"""
        ambiguous_phrases = [
            "reasonable", "best efforts", "material", "substantial",
            "as soon as practicable", "to the extent", "including but not limited to",
            "etc.", "and/or", "may", "could", "should"
        ]
        
        if not clauses:
            return 0.0
        
        ambiguity_count = 0
        for clause in clauses:
            for phrase in ambiguous_phrases:
                if phrase in clause.lower():
                    ambiguity_count += 1
        
        return min(10, ambiguity_count * 2)
    
    def _get_risk_level(self, score: float) -> str:
        if score >= 8.0:
            return "CRITICAL"
        elif score >= 6.5:
            return "HIGH"
        elif score >= 4.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _find_keywords(self, clauses: List[str]) -> List[Dict]:
        """Find and categorize risk keywords"""
        found = []
        for clause in clauses:
            for keyword, score in self.risk_keywords.items():
                if keyword in clause.lower():
                    found.append({
                        "keyword": keyword,
                        "severity": score,
                        "risk_level": "HIGH" if score > 7.5 else "MEDIUM" if score > 6 else "LOW"
                    })
        return found