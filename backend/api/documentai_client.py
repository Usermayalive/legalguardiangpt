# backend/apis/documentai_client.py
import os
import base64
from typing import Dict, Any
import requests

class DocumentAIClient:
    """External Service - Google Document AI for OCR/Text Extraction"""
    
    def __init__(self):
        self.name = "Google Document AI"
        self.project_id = os.getenv("GOOGLE_PROJECT_ID", "demo-project")
        self.location = "us"
        self.processor_id = os.getenv("DOCAI_PROCESSOR_ID", "demo-processor")
        
        if self.project_id == "demo-project":
            self.status = "demo_mode"
            print("⚠️ DocumentAI: Using demo mode. Set GOOGLE_PROJECT_ID for OCR.")
        else:
            self.status = "connected"
    
    def process_document(self, file_path: str = None, content: bytes = None) -> Dict[str, Any]:
        """Process document with Document AI"""
        
        if self.status == "demo_mode":
            return self._demo_processing(file_path, content)
        
        try:
            # Google Document AI API endpoint
            endpoint = f"https://{self.location}-documentai.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}:process"
            
            # Prepare document
            if content:
                encoded_content = base64.b64encode(content).decode()
            elif file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    encoded_content = base64.b64encode(f.read()).decode()
            else:
                return {"error": "No document provided"}
            
            # API request
            document = {
                "content": encoded_content,
                "mimeType": "application/pdf"
            }
            
            request = {"rawDocument": document}
            
            # Make request (simplified - needs proper auth)
            # In real implementation, use Google Cloud client library
            response = requests.post(
                endpoint,
                json=request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"DocumentAI error: {response.status_code}")
                return self._demo_processing(file_path, content)
                
        except Exception as e:
            print(f"DocumentAI API error: {e}")
            return self._demo_processing(file_path, content)
    
    def _demo_processing(self, file_path: str = None, content: bytes = None) -> Dict[str, Any]:
        """Demo document processing"""
        demo_text = """
        DEMO DOCUMENT ANALYSIS:
        - Document type: Contract/Agreement
        - Pages: 5
        - Text extracted: Yes
        - Entities found: Parties, Dates, Amounts
        - Confidence: 95%
        
        This is a demo response. For real OCR, configure Google Document AI.
        """
        
        return {
            "api_used": "Google Document AI (Demo)",
            "status": "demo",
            "text": demo_text,
            "entities": [
                {"type": "PARTY", "mention": "Company Inc."},
                {"type": "PARTY", "mention": "Client Name"},
                {"type": "DATE", "mention": "2024-01-01"},
                {"type": "AMOUNT", "mention": "$10,000"}
            ],
            "pages": 5,
            "confidence": 0.95
        }
    
    def extract_legal_clauses(self, document_text: str) -> Dict[str, Any]:
        """Extract legal clauses from document text"""
        
        # Simple clause extraction (demo)
        clauses = []
        lines = document_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                "shall", "agree to", "warrant", "represent",
                "indemnif", "liability", "jurisdiction", "arbitration"
            ]):
                clauses.append({
                    "text": line[:200],
                    "type": "legal_clause",
                    "confidence": 0.8
                })
        
        return {
            "total_clauses": len(clauses),
            "clauses": clauses[:10],  # Limit to 10
            "method": "keyword_based_extraction"
        }