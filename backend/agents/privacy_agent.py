# backend/agents/privacy_agent.py
import re
from datetime import datetime

class PrivacyAgent:
    """Agent 1: PII Scrubber - Removes sensitive information before processing"""
    
    def __init__(self):
        self.name = "Privacy Agent"
        self.role = "PII Scrubber & Data Protection"
        self.status = "active"
        self.last_active = datetime.now().isoformat()
        
        # PII patterns (simplified for demo)
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}[-]\d{2}[-]\d{4}\b',
            "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            "address": r'\b\d{1,5}\s+\w+\s+\w+\b',
        }
    
    def scrub_pii(self, text: str) -> str:
        """Remove PII from text"""
        self.last_active = datetime.now().isoformat()
        
        scrubbed_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            if pii_type == "email":
                scrubbed_text = re.sub(pattern, "[EMAIL_REDACTED]", scrubbed_text)
            elif pii_type == "phone":
                scrubbed_text = re.sub(pattern, "[PHONE_REDACTED]", scrubbed_text)
            elif pii_type == "ssn":
                scrubbed_text = re.sub(pattern, "[SSN_REDACTED]", scrubbed_text)
            elif pii_type == "credit_card":
                scrubbed_text = re.sub(pattern, "[CARD_REDACTED]", scrubbed_text)
            elif pii_type == "address":
                # Be more careful with addresses
                matches = list(re.finditer(pattern, scrubbed_text))
                for match in reversed(matches):
                    scrubbed_text = scrubbed_text[:match.start()] + "[ADDRESS_REDACTED]" + scrubbed_text[match.end():]
        
        return scrubbed_text
    
    def detect_pii(self, text: str) -> dict:
        """Detect and count PII types"""
        self.last_active = datetime.now().isoformat()
        
        pii_count = {}
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                pii_count[pii_type] = len(matches)
        
        return {
            "pii_detected": len(pii_count) > 0,
            "counts": pii_count,
            "total": sum(pii_count.values())
        }