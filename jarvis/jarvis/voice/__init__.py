"""Voice pipeline integration for JARVIS agent"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Callable
import asyncio

@dataclass
class VoiceConfig:
    """Voice pipeline configuration"""
    enabled: bool = False
    stt_enabled: bool = True
    tts_enabled: bool = True
    wakeword_enabled: bool = False
    
    # Endpoints
    backend_url: str = "http://127.0.0.1:8000"
    
    # Voice settings
    voice: str = "alba"
    speech_rate: float = 1.0
    volume: float = 1.0


class VoiceConnector:
    """
    Connects JARVIS agent to voice pipeline (STT/TTS/Wakeword).
    
    This is a bridge between the agent execution and the backend voice services.
    Phase 7 implementation - connects agent context to voice pipeline.
    """
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.is_listening = False
        self.is_speaking = False
        self._callbacks = {}
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for voice events"""
        self._callbacks[event] = callback
    
    async def speak(self, text: str) -> bool:
        """
        Synthesize and play speech.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful
        """
        if not self.config.tts_enabled:
            return False
        
        try:
            import httpx
            self.is_speaking = True
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.backend_url}/api/tts/speech",
                    json={
                        "text": text,
                        "voice": self.config.voice,
                        "format": "wav"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    # In full implementation, would play audio
                    # For now, just signal completion
                    if "tts_complete" in self._callbacks:
                        self._callbacks["tts_complete"](text)
                    return True
                    
        except Exception as e:
            print(f"[Voice] TTS error: {e}")
        finally:
            self.is_speaking = False
        
        return False
    
    async def listen(self, timeout: float = 10.0) -> Optional[str]:
        """
        Listen for voice input and transcribe.
        
        Args:
            timeout: Maximum time to listen
            
        Returns:
            Transcribed text or None
        """
        if not self.config.stt_enabled:
            return None
        
        try:
            self.is_listening = True
            
            # In full implementation:
            # 1. Start audio capture
            # 2. Stream to STT service
            # 3. Return transcription
            
            # For now, signal that we're listening
            if "listening_started" in self._callbacks:
                self._callbacks["listening_started"]()
            
            # Placeholder: would actually capture and transcribe
            await asyncio.sleep(0.1)
            
            if "listening_complete" in self._callbacks:
                self._callbacks["listening_complete"](None)
                
        except Exception as e:
            print(f"[Voice] STT error: {e}")
        finally:
            self.is_listening = False
        
        return None
    
    async def ask_user(self, question: str) -> str:
        """
        Ask user a question via voice and get response.
        
        This is the voice_ask callback for AgentContext.
        
        Args:
            question: Question to ask
            
        Returns:
            User's response text
        """
        # Speak the question
        await self.speak(question)
        
        # Listen for answer
        response = await self.listen(timeout=15.0)
        
        # If no voice response, return empty (will trigger other input methods)
        return response or ""


# Factory function
def create_voice_connector(config: Optional[VoiceConfig] = None) -> VoiceConnector:
    """Create voice connector instance"""
    if config is None:
        config = VoiceConfig()
    return VoiceConnector(config)
