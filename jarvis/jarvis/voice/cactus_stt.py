"""
Cactus Whistle Speech-to-Text Service
Local, privacy-first STT using Cactus Whistle (16.9MB model)
"""
from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Dict
import wave

try:
    import cactus
    CACTUS_AVAILABLE = True
except ImportError:
    CACTUS_AVAILABLE = False
    cactus = None


class CactusSTTService:
    """
    Speech-to-Text service using Cactus Whistle.
    
    Features:
    - 100% local inference (no API calls)
    - 16.9MB model (9x smaller than Whisper base)
    - 7 languages supported
    - Word timestamps
    - Speech embeddings
    """
    
    def __init__(self):
        if not CACTUS_AVAILABLE:
            raise RuntimeError("cactus-compute not installed. Run: pip install -U cactus-compute")
        
        self.model_loaded = False
        print("[Cactus STT] Initializing Whistle model...")
    
    async def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, any]:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_data: Audio bytes (WAV format)
            sample_rate: Sample rate in Hz (default 16000)
        
        Returns:
            {
                "text": str,
                "confidence": float,
                "words": [...],  # Optional word timestamps
                "language": str
            }
        """
        # Save to temp WAV file (Cactus requires file path)
        temp_path = None
        try:
            temp_path = await self._save_to_wav(audio_data, sample_rate)
            
            # Transcribe using Cactus
            result = await asyncio.to_thread(cactus.transcribe, str(temp_path))
            
            if not self.model_loaded:
                self.model_loaded = True
                print("[Cactus STT] Whistle model loaded successfully")
            
            return {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 1.0),
                "words": result.get("words", []),
                "language": result.get("language", "en"),
                "method": "cactus_whistle"
            }
        
        except Exception as e:
            print(f"[Cactus STT] Transcription failed: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "error": str(e),
                "method": "cactus_whistle"
            }
        
        finally:
            # Cleanup temp file
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
    
    async def transcribe_file(self, audio_path: str) -> Dict[str, any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV, 16kHz recommended)
        
        Returns:
            Transcription result dict
        """
        try:
            # Verify file exists
            path = Path(audio_path)
            if not path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Transcribe
            result = await asyncio.to_thread(cactus.transcribe, str(path))
            
            if not self.model_loaded:
                self.model_loaded = True
                print("[Cactus STT] Whistle model loaded successfully")
            
            return {
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 1.0),
                "words": result.get("words", []),
                "language": result.get("language", "en"),
                "method": "cactus_whistle"
            }
        
        except Exception as e:
            print(f"[Cactus STT] File transcription failed: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "error": str(e),
                "method": "cactus_whistle"
            }
    
    async def _save_to_wav(self, audio_data: bytes, sample_rate: int) -> Path:
        """Save audio bytes to temporary WAV file"""
        # Create temp file
        temp_fd, temp_path_str = tempfile.mkstemp(suffix=".wav")
        temp_path = Path(temp_path_str)
        
        try:
            # Write WAV file
            with wave.open(str(temp_path), 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data)
            
            return temp_path
        
        except Exception as e:
            # Cleanup on error
            if temp_path.exists():
                temp_path.unlink()
            raise e
        
        finally:
            # Close file descriptor
            try:
                import os
                os.close(temp_fd)
            except Exception:
                pass
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return ["en", "es", "fr", "de", "it", "pt", "pl"]  # Whistle supports 7 languages
    
    def get_model_info(self) -> Dict[str, any]:
        """Get model information"""
        return {
            "name": "Cactus Whistle",
            "size_mb": 16.9,
            "languages": 7,
            "features": ["transcription", "timestamps", "embeddings"],
            "local": True,
            "privacy": "complete"
        }


# Singleton instance
_service = None

def get_stt_service() -> CactusSTTService:
    """Get singleton STT service instance"""
    global _service
    if _service is None:
        _service = CactusSTTService()
    return _service


async def transcribe(audio_data: bytes, sample_rate: int = 16000) -> str:
    """Convenience function to transcribe audio"""
    service = get_stt_service()
    result = await service.transcribe(audio_data, sample_rate)
    return result.get("text", "")
