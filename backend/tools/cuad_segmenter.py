# backend/tools/cuad_segmenter.py
import re
from typing import List

class CUADSegmenter:
    """Tool 1: CUAD-based Legal Document Segmentation"""
    
    def __init__(self):
        self.name = "CUAD Segmenter"
        
        # Legal section patterns
        self.section_patterns = [
            r'\b(Section|Article|Clause)\s+\d+[.:]',  # Section 1:
            r'\b\d+\.\s+[A-Z]',  # 1. TERMS
            r'\b[A-Z][A-Z\s]+\b:',  # GOVERNING LAW:
            r'\n\s*[A-Z][A-Z\s]+\n',  # New line with caps
        ]
        
        # Legal clause markers
        self.clause_markers = [
            'shall', 'must', 'will', 'agree to', 'acknowledge that',
            'represent and warrant', 'covenant', 'undertake to'
        ]
    
    def segment(self, text: str) -> List[str]:
        """Segment text into legal clauses"""
        # Clean text
        text = self._clean_text(text)
        
        # First, try to find sections
        sections = self._split_by_sections(text)
        
        if len(sections) > 1:
            # Further split sections into clauses
            clauses = []
            for section in sections:
                clauses.extend(self._split_into_clauses(section))
            return clauses
        else:
            # No clear sections, split by sentences
            return self._split_by_sentences(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML/formatting from text"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
        return text.strip()
    
    def _split_by_sections(self, text: str) -> List[str]:
        """Split text by section markers"""
        sections = []
        current = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts a new section
            is_section = any(re.search(pattern, line) for pattern in self.section_patterns)
            
            if is_section and current:
                sections.append(' '.join(current))
                current = [line]
            else:
                current.append(line)
        
        if current:
            sections.append(' '.join(current))
        
        return sections if len(sections) > 1 else [text]
    
    def _split_into_clauses(self, text: str) -> List[str]:
        """Split section into individual clauses"""
        # Split by clause markers
        clauses = []
        current = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if this sentence starts a new clause
            starts_clause = any(marker in sentence.lower() for marker in self.clause_markers)
            
            if starts_clause and current:
                clauses.append(' '.join(current))
                current = [sentence]
            else:
                current.append(sentence)
        
        if current:
            clauses.append(' '.join(current))
        
        return clauses if clauses else [text]
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Fallback: split by sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def analyze_structure(self, text: str) -> Dict:
        """Analyze document structure"""
        segments = self.segment(text)
        
        return {
            "total_segments": len(segments),
            "avg_segment_length": sum(len(s.split()) for s in segments) / max(1, len(segments)),
            "segment_types": {
                "likely_sections": len([s for s in segments if any(p in s for p in self.section_patterns)]),
                "likely_clauses": len([s for s in segments if any(m in s.lower() for m in self.clause_markers)]),
                "other": len(segments) - len([s for s in segments if any(p in s for p in self.section_patterns)]) - len([s for s in segments if any(m in s.lower() for m in self.clause_markers)])
            },
            "segments_preview": [s[:100] + "..." if len(s) > 100 else s for s in segments[:5]]
        }