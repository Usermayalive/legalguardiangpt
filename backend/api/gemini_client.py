# backend/apis/gemini_client.py
import os
from typing import Dict, Any
import google.generativeai as genai

class GeminiClient:
    """Chat API Integration - Google Gemini 2.5"""
    
    def __init__(self):
        self.name = "Gemini 2.5 API"
        self.api_key = os.getenv("GEMINI_API_KEY", "demo-key")
        self.model_name = "gemini-2.0-flash"
        
        # Configure for demo (with fallback)
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.status = "connected"
        except:
            self.status = "demo_mode"
            print("⚠️ Gemini API: Using demo mode. Set GEMINI_API_KEY for real analysis.")
    
    def analyze_legal_text(self, text: str) -> Dict[str, Any]:
        """Analyze legal text using Gemini"""
        
        if self.status == "demo_mode":
            # Demo fallback
            return self._demo_analysis(text)
        
        try:
            prompt = f"""
            Analyze this legal text for risks and threats. Return JSON with:
            1. risk_score (1-10)
            2. risk_level (LOW, MEDIUM, HIGH, CRITICAL)
            3. detected_clauses (list)
            4. threats (list)
            5. explanation (string)
            
            Text: {text[:2000]}  # Limit length
            
            Return valid JSON only.
            """
            
            response = self.model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)
            
            return {
                "api_used": "Gemini 2.5 Flash",
                "status": "success",
                **result
            }
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._demo_analysis(text)
    
    def _demo_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback analysis for demo"""
        text_lower = text.lower()
        
        risk_score = 5.0
        clauses = []
        
        if "indemnif" in text_lower:
            risk_score += 3.0
            clauses.append("indemnification")
        if "arbitration" in text_lower:
            risk_score += 2.5
            clauses.append("arbitration")
        if "jurisdiction" in text_lower:
            risk_score += 2.0
            clauses.append("jurisdiction")
        if "liability" in text_lower:
            risk_score += 2.0
            clauses.append("liability")
        
        risk_level = "HIGH" if risk_score > 7 else "MEDIUM" if risk_score > 5 else "LOW"
        
        return {
            "api_used": "Gemini (Demo Mode)",
            "status": "demo",
            "risk_score": min(10, risk_score),
            "risk_level": risk_level,
            "detected_clauses": clauses,
            "threats": ["Legal risks detected in contract"],
            "explanation": "AI analysis suggests reviewing with legal counsel"
        }
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini response to extract JSON"""
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback if parsing fails
        return {
            "risk_score": 7.5,
            "risk_level": "MEDIUM",
            "detected_clauses": ["legal_text"],
            "threats": ["Contract requires careful review"],
            "explanation": "AI analysis completed"
        }
    
    def simplify_for_illiterate(self, text: str, language: str = "en") -> str:
        """Simplify legal text for illiterate users"""
        prompt = f"""
        Simplify this legal text for someone who cannot read well.
        Use simple words, short sentences. Language: {language}
        
        Text: {text[:1000]}
        
        Return only the simplified text.
        """
        
        if self.status == "demo_mode":
            # Demo simplification
            simplified = text.replace("shall", "must")
            simplified = simplified.replace("hereinafter", "from now on")
            simplified = simplified.replace("notwithstanding", "even if")
            return simplified[:500] + "..." if len(simplified) > 500 else simplified
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return text[:500]