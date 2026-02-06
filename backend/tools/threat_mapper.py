# backend/tools/threat_mapper.py
from typing import Dict, List
import json

class ThreatMapper:
    """Tool 3: Graph-based Threat Chain Mapping"""
    
    def __init__(self):
        self.name = "Threat Mapper"
        
        # Threat taxonomy
        self.threat_taxonomy = {
            "financial": ["indemnification", "liquidated_damages", "penalties", "fees"],
            "legal": ["jurisdiction", "arbitration", "governing_law", "venue"],
            "operational": ["termination", "suspension", "modification", "renewal"],
            "data": ["confidentiality", "data_ownership", "privacy", "ip_rights"],
            "compliance": ["audit_rights", "reporting", "regulatory", "standards"]
        }
        
        # Threat relationships
        self.relationships = {
            "indemnification": ["financial_loss", "insurance_issues", "bankruptcy_risk"],
            "jurisdiction": ["legal_costs", "travel_burden", "unfamiliar_laws"],
            "arbitration": ["no_appeal", "confidential", "biased_process"],
            "termination": ["business_disruption", "data_loss", "replacement_costs"]
        }
    
    def map_threats(self, clauses: List[str], risk_scores: Dict) -> Dict:
        """Map threats and their relationships"""
        
        # Identify threats in clauses
        identified_threats = self._identify_threats(clauses)
        
        # Build threat chains
        threat_chains = self._build_threat_chains(identified_threats)
        
        # Calculate threat severity
        threat_severity = self._calculate_threat_severity(identified_threats, risk_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(identified_threats)
        
        return {
            "identified_threats": identified_threats,
            "threat_chains": threat_chains,
            "threat_severity": threat_severity,
            "recommendations": recommendations,
            "threat_categories": self._categorize_threats(identified_threats),
            "visualization_data": self._prepare_visualization_data(threat_chains)
        }
    
    def _identify_threats(self, clauses: List[str]) -> List[Dict]:
        """Identify potential threats in clauses"""
        threats = []
        
        threat_keywords = {
            "indemnification": ["indemnif", "hold harmless", "defend"],
            "jurisdiction": ["jurisdiction", "governing law", "venue"],
            "arbitration": ["arbitration", "dispute resolution"],
            "termination": ["terminate", "cancel", "expire"],
            "liability_cap": ["limit of liability", "maximum liability", "cap"],
            "confidentiality": ["confidential", "non-disclosure", "proprietary"],
            "auto_renewal": ["auto-renew", "automatic renewal", "evergreen"],
            "sole_discretion": ["sole discretion", "absolute discretion"],
            "assignment": ["assign", "transfer"],
            "modification": ["modify", "amend", "change"]
        }
        
        for i, clause in enumerate(clauses):
            clause_threats = []
            for threat_type, keywords in threat_keywords.items():
                for keyword in keywords:
                    if keyword in clause.lower():
                        clause_threats.append({
                            "type": threat_type,
                            "keyword": keyword,
                            "severity": self._get_threat_severity(threat_type)
                        })
                        break  # Found one keyword, move to next threat type
            
            if clause_threats:
                threats.append({
                    "clause_id": i,
                    "clause_preview": clause[:80] + "..." if len(clause) > 80 else clause,
                    "threats": clause_threats,
                    "threat_count": len(clause_threats)
                })
        
        return threats
    
    def _get_threat_severity(self, threat_type: str) -> str:
        """Get severity level for threat type"""
        high_severity = ["indemnification", "arbitration", "sole_discretion"]
        medium_severity = ["jurisdiction", "liability_cap", "auto_renewal"]
        
        if threat_type in high_severity:
            return "HIGH"
        elif threat_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _build_threat_chains(self, threats: List[Dict]) -> List[List[Dict]]:
        """Build chains showing how threats connect"""
        if len(threats) < 2:
            return []
        
        chains = []
        
        # Simple chaining: connect threats in sequence
        for i in range(len(threats) - 1):
            current = threats[i]
            next_threat = threats[i + 1]
            
            # Check if they're related
            if self._are_threats_related(current, next_threat):
                chain = [
                    {"step": 1, "threat": current["threats"][0]["type"], "clause": current["clause_id"]},
                    {"step": 2, "threat": next_threat["threats"][0]["type"], "clause": next_threat["clause_id"]},
                    {"relationship": "sequential_escalation", "risk": "increased"}
                ]
                chains.append(chain)
        
        # Also check for compounding threats (multiple in same clause)
        for threat in threats:
            if threat["threat_count"] > 1:
                compound_chain = []
                for i, t in enumerate(threat["threats"]):
                    compound_chain.append({
                        "step": i + 1,
                        "threat": t["type"],
                        "severity": t["severity"],
                        "location": "same_clause"
                    })
                compound_chain.append({
                    "relationship": "compounding",
                    "risk": "exponential",
                    "description": "Multiple threats in same clause amplify risk"
                })
                chains.append(compound_chain)
        
        return chains[:5]  # Return top 5 chains
    
    def _are_threats_related(self, threat1: Dict, threat2: Dict) -> bool:
        """Check if two threats are related"""
        t1_types = [t["type"] for t in threat1["threats"]]
        t2_types = [t["type"] for t in threat2["threats"]]
        
        # Related categories
        related_groups = [
            ["indemnification", "liability_cap"],  # Financial
            ["jurisdiction", "arbitration"],       # Legal process
            ["termination", "auto_renewal"],       # Contract life
            ["confidentiality", "assignment"]      # Data/rights
        ]
        
        for group in related_groups:
            t1_in_group = any(t in group for t in t1_types)
            t2_in_group = any(t in group for t in t2_types)
            if t1_in_group and t2_in_group:
                return True
        
        return False
    
    def _calculate_threat_severity(self, threats: List[Dict], risk_scores: Dict) -> Dict:
        """Calculate overall threat severity"""
        if not threats:
            return {"overall": "LOW", "score": 2.0}
        
        # Count threats by severity
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for threat in threats:
            for t in threat["threats"]:
                severity_counts[t["severity"]] += 1
        
        # Calculate weighted score
        total_score = (
            severity_counts["HIGH"] * 9 +
            severity_counts["MEDIUM"] * 6 +
            severity_counts["LOW"] * 3
        )
        total_threats = sum(severity_counts.values())
        
        if total_threats == 0:
            avg_score = 0
        else:
            avg_score = total_score / total_threats
        
        # Determine overall severity
        if avg_score >= 7.5 or severity_counts["HIGH"] >= 3:
            overall = "CRITICAL"
        elif avg_score >= 6 or severity_counts["HIGH"] >= 1:
            overall = "HIGH"
        elif avg_score >= 4 or severity_counts["MEDIUM"] >= 2:
            overall = "MEDIUM"
        else:
            overall = "LOW"
        
        return {
            "overall": overall,
            "score": round(avg_score, 2),
            "counts": severity_counts,
            "total_threats": total_threats
        }
    
    def _generate_recommendations(self, threats: List[Dict]) -> List[Dict]:
        """Generate mitigation recommendations"""
        recommendations = []
        
        # Group threats by type for consolidated recommendations
        threat_types = {}
        for threat in threats:
            for t in threat["threats"]:
                t_type = t["type"]
                if t_type not in threat_types:
                    threat_types[t_type] = []
                threat_types[t_type].append(threat["clause_id"])
        
        # Generate recommendations for each threat type
        recommendation_templates = {
            "indemnification": "Limit indemnification to direct damages only, exclude consequential damages",
            "jurisdiction": "Choose neutral, convenient jurisdiction for both parties",
            "arbitration": "Ensure fair arbitrator selection process and allow for appeal",
            "termination": "Add notice period and cure period before termination",
            "liability_cap": "Cap should be reasonable and reflect potential actual damages",
            "confidentiality": "Define clear exceptions and time limits for confidentiality",
            "auto_renewal": "Require written notice for renewal and limit auto-renewal periods",
            "sole_discretion": "Add 'reasonableness' standard to discretion clauses",
            "assignment": "Allow assignment with consent, not to be unreasonably withheld",
            "modification": "Require modifications to be in writing and signed by both parties"
        }
        
        for threat_type, clause_ids in threat_types.items():
            if threat_type in recommendation_templates:
                recommendations.append({
                    "threat_type": threat_type,
                    "recommendation": recommendation_templates[threat_type],
                    "clauses": clause_ids[:3],  # First 3 clauses with this threat
                    "priority": "HIGH" if threat_type in ["indemnification", "arbitration"] else "MEDIUM"
                })
        
        return recommendations
    
    def _categorize_threats(self, threats: List[Dict]) -> Dict:
        """Categorize threats by type"""
        categories = {}
        
        for threat in threats:
            for t in threat["threats"]:
                t_type = t["type"]
                t_severity = t["severity"]
                
                if t_type not in categories:
                    categories[t_type] = {
                        "count": 0,
                        "severities": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
                    }
                
                categories[t_type]["count"] += 1
                categories[t_type]["severities"][t_severity] += 1
        
        # Sort by count
        sorted_categories = dict(sorted(
            categories.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        ))
        
        return sorted_categories
    
    def _prepare_visualization_data(self, chains: List[List[Dict]]) -> Dict:
        """Prepare data for threat chain visualization"""
        nodes = []
        edges = []
        node_id = 0
        
        for chain in chains:
            for item in chain:
                if "step" in item:
                    node_id += 1
                    nodes.append({
                        "id": node_id,
                        "label": item["threat"],
                        "clause": item.get("clause", "unknown"),
                        "type": "threat"
                    })
                
                if "relationship" in item:
                    edges.append({
                        "from": node_id - 1,
                        "to": node_id,
                        "label": item["relationship"],
                        "risk": item.get("risk", "unknown")
                    })
        
        return {
            "nodes": nodes[:20],  # Limit for visualization
            "edges": edges[:30],
            "total_chains": len(chains)
        }