# backend/apis/assemblyai_client.py
import os
import requests
from typing import Optional

class AssemblyAIClient:
    """Media API Integration - AssemblyAI for Text-to-Speech"""
    
    def __init__(self):
        self.name = "AssemblyAI API"
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY", "demo-key")
        self.base_url = "https://api.assemblyai.com/v2"
        
        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json"
        }
        
        # Check connection
        if self.api_key == "demo-key":
            self.status = "demo_mode"
            print("⚠️ AssemblyAI: Using demo mode. Set ASSEMBLYAI_API_KEY for real audio.")
        else:
            self.status = "connected"
    
    def text_to_speech(self, text: str, language: str = "en") -> Optional[str]:
        """Convert text to speech audio URL"""
        
        if self.status == "demo_mode":
            # Return demo audio or use browser TTS
            return self._demo_audio_response(text, language)
        
        try:
            # AssemblyAI text-to-speech
            url = f"{self.base_url}/text-to-speech"
            
            # Choose voice based on language
            voice_id = self._get_voice_id(language)
            
            payload = {
                "text": text[:500],  # Limit length
                "voice": voice_id,
                "speed": 0.9,  # Slightly slower for clarity
                "sample_rate": 24000,
                "output_format": "mp3"
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("audio_url")
            else:
                print(f"AssemblyAI error: {response.status_code}")
                return self._demo_audio_response(text, language)
                
        except Exception as e:
            print(f"AssemblyAI API error: {e}")
            return self._demo_audio_response(text, language)
    
    def _get_voice_id(self, language: str) -> str:
        """Get appropriate voice for language"""
        voices = {
            "en": "eleven_multilingual_v2",  # English
            "hi": "eleven_multilingual_v2",  # Hindi (multilingual)
            "es": "eleven_multilingual_v2",  # Spanish
            "fr": "eleven_multilingual_v2",  # French
            "de": "eleven_multilingual_v2",  # German
        }
        return voices.get(language, "eleven_multilingual_v2")
    
    def _demo_audio_response(self, text: str, language: str) -> str:
        """Demo response suggesting browser TTS"""
        return f"audio_demo:{language}:{hash(text) % 10000}"
    
    def generate_audio_summary(self, analysis: Dict, language: str = "en") -> str:
        """Generate audio summary for illiterate users"""
        
        if language == "hi":  # Hindi
            summary = f"चेतावनी। जोखिम स्कोर {analysis.get('risk_score', 5)} 10 में से। "
            if analysis.get('risk_level') in ["HIGH", "CRITICAL"]:
                summary += "उच्च जोखिम। वकील से सलाह लें।"
            else:
                summary += "सावधानी से जांचें।"
                
        elif language == "es":  # Spanish
            summary = f"Advertencia. Puntuación de riesgo {analysis.get('risk_score', 5)} de 10. "
            summary += "Revise cuidadosamente."
            
        else:  # English (default)
            summary = f"Warning. Risk score {analysis.get('risk_score', 5)} out of 10. "
            
            if analysis.get('risk_level') == "CRITICAL":
                summary += "Critical risk detected. Do not sign without legal advice."
            elif analysis.get('risk_level') == "HIGH":
                summary += "High risk. Review carefully with expert."
            elif analysis.get('risk_level') == "MEDIUM":
                summary += "Medium risk. Consider reviewing."
            else:
                summary += "Low risk detected."
        
        # Add threat count
        threats = analysis.get('threats', [])
        if threats:
            summary += f" Found {len(threats)} potential issues."
        
        return summary