# backend/tools/hybrid_calculator.py
from typing import Dict, List

class HybridCalculator:
    """Tool 2: Proprietary Hybrid Risk Calculation Algorithm"""
    
    def __init__(self):
        self.name = "Hybrid Risk Calculator"
        
        # Algorithm components and their weights
        self.components = {
            "cuad_pattern_score": 0.35,
            "semantic_risk_score": 0.25,
            "structural_risk_score": 0.20,
            "historical_precedent_score": 0.20
        }
    
    def calculate(self, clauses: List[str], cuad_results: Dict, embeddings: List) -> Dict:
        """Calculate comprehensive risk scores"""
        
        # Calculate each component score
        cuad_score = self._calculate_cuad_score(cuad_results)
        semantic_score = self._calculate_semantic_score(clauses, embeddings)
        structural_score = self._calculate_structural_score(clauses)
        precedent_score = self._calculate_precedent_score(clauses)
        
        # Combine scores
        total_score = (
            cuad_score * self.components["cuad_pattern_score"] +
            semantic_score * self.components["semantic_risk_score"] +
            structural_score * self.components["structural_risk_score"] +
            precedent_score * self.components["historical_precedent_score"]
        )
        
        # Calculate per-clause scores
        clause_scores = self._calculate_clause_scores(clauses)
        
        return {
            "overall_score": min(10, round(total_score, 2)),
            "component_scores": {
                "cuad_pattern": round(cuad_score, 2),
                "semantic_analysis": round(semantic_score, 2),
                "structural_analysis": round(structural_score, 2),
                "historical_precedent": round(precedent_score, 2)
            },
            "clause_scores": clause_scores,
            "algorithm_version": "v2.1-hybrid",
            "weights_used": self.components
        }
    
    def _calculate_cuad_score(self, cuad_results: Dict) -> float:
        """Score based on CUAD pattern matches"""
        matches = cuad_results.get("matches", [])
        if not matches:
            return 2.0  # Baseline
        
        total_severity = 0
        for match_list in matches:
            for match in match_list.get("matches", []):
                category = match.get("category", "")
                if "indemnif" in category.lower():
                    total_severity += 9.0
                elif "arbitration" in category.lower():
                    total_severity += 8.5
                elif "liability" in category.lower():
                    total_severity += 8.0
                else:
                    total_severity += 6.0
        
        avg_severity = total_severity / max(1, len(matches))
        return min(10, avg_severity)
    
    def _calculate_semantic_score(self, clauses: List[str], embeddings: List) -> float:
        """Score based on semantic analysis"""
        if not clauses:
            return 0.0
        
        # Analyze for negative sentiment/risk language
        risk_indicators = [
            "not responsible", "disclaim", "exclude", "limit",
            "sole discretion", "irrevocable", "binding", "waive",
            "assume all risk", "at your own risk"
        ]
        
        risk_count = 0
        for clause in clauses:
            for indicator in risk_indicators:
                if indicator in clause.lower():
                    risk_count += 1
                    break
        
        risk_density = risk_count / len(clauses)
        return min(10, risk_density * 15)  # Scale appropriately
    
    def _calculate_structural_score(self, clauses: List[str]) -> float:
        """Score based on document structure"""
        if not clauses:
            return 0.0
        
        # Longer documents are riskier
        total_length = sum(len(c.split()) for c in clauses)
        
        # Count complex sentences (multiple clauses, semicolons)
        complex_count = 0
        for clause in clauses:
            if ';' in clause or len(clause.split()) > 50:
                complex_count += 1
        
        complexity_ratio = complex_count / len(clauses)
        length_factor = min(1.0, total_length / 1000)  # Normalize
        
        return min(10, (complexity_ratio * 7 + length_factor * 3))
    
    def _calculate_precedent_score(self, clauses: List[str]) -> float:
        """Score based on historical precedent (simulated)"""
        # Simulated precedent database
        precedent_cases = {
            "indemnify": 8.5,
            "arbitration": 8.0,
            "jurisdiction": 7.0,
            "liability cap": 7.5,
            "termination for convenience": 6.5
        }
        
        total_score = 0
        matches = 0
        
        for clause in clauses:
            clause_lower = clause.lower()
            for key, score in precedent_cases.items():
                if key in clause_lower:
                    total_score += score
                    matches += 1
        
        if matches > 0:
            return min(10, total_score / matches)
        return 3.0  # Default moderate risk
    
    def _calculate_clause_scores(self, clauses: List[str]) -> List[Dict]:
        """Calculate individual clause scores"""
        clause_scores = []
        
        for i, clause in enumerate(clauses):
            score = 0
            
            # Base score based on length
            word_count = len(clause.split())
            if word_count > 100:
                score += 3
            elif word_count > 50:
                score += 2
            elif word_count > 25:
                score += 1
            
            # Add for complex language
            if ';' in clause or ('shall' in clause.lower() and 'not' in clause.lower()):
                score += 2
            
            # Add for risk indicators
            risk_words = ['indemnif', 'waive', 'liable', 'arbitration', 'jurisdiction']
            for word in risk_words:
                if word in clause.lower():
                    score += 3
                    break
            
            clause_scores.append({
                "clause_id": i,
                "score": min(10, score),
                "word_count": word_count,
                "complexity": "high" if score > 5 else "medium" if score > 3 else "low"
            })
        
        return clause_scores