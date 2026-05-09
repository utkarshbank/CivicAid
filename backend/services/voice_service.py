"""
Voice Service for CivicAid
Handles text-to-speech using ElevenLabs API.
Falls back to a placeholder in demo mode.
"""

import os
import base64
import httpx


class VoiceService:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel
        self.base_url = "https://api.elevenlabs.io/v1"
        self.use_voice = bool(self.api_key)
    
    async def text_to_speech(self, text: str, voice_id: str = None) -> dict:
        """
        Convert text to speech using ElevenLabs API.
        Returns base64-encoded audio data.
        """
        if not self.use_voice:
            return {
                "success": False,
                "message": "ElevenLabs API key not configured. Add ELEVENLABS_API_KEY to your .env file.",
                "audio": None
            }
        
        vid = voice_id or self.voice_id
        url = f"{self.base_url}/text-to-speech/{vid}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    audio_base64 = base64.b64encode(response.content).decode("utf-8")
                    return {
                        "success": True,
                        "audio": audio_base64,
                        "content_type": "audio/mpeg"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"ElevenLabs API error: {response.status_code} — {response.text}",
                        "audio": None
                    }
        except Exception as e:
            return {
                "success": False,
                "message": f"Voice service error: {str(e)}",
                "audio": None
            }
    
    async def get_voices(self) -> list:
        """Get available voices from ElevenLabs."""
        if not self.use_voice:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers={"xi-api-key": self.api_key}
                )
                if response.status_code == 200:
                    data = response.json()
                    return [{"id": v["voice_id"], "name": v["name"]} for v in data.get("voices", [])]
        except Exception:
            pass
        return []
