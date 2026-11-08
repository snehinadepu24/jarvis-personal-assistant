"""
STT Service powered by Moonshine Small Streaming (123M ONNX) with faster-whisper fallback.
"""
from __future__ import annotations

import io
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MoonshineStreamSession:
    """Manages an active streaming transcription session."""
    def __init__(self, transcriber, sample_rate: int = 16000):
        self.transcriber = transcriber
        self.sample_rate = sample_rate
        self.buffer = bytearray()
        self.full_transcript = []
        self._started = False

    def add_chunk(self, chunk: bytes) -> str:
        self.buffer.extend(chunk)
        # If transcriber supports live streaming sessions (start/add_audio/stop)
        if hasattr(self.transcriber, "add_audio"):
            try:
                import numpy as np
                audio_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
                if not self._started and hasattr(self.transcriber, "start"):
                    self.transcriber.start()
                    self._started = True
                result = self.transcriber.add_audio(audio_np)
                if result and hasattr(result, "text"):
                    return result.text
            except Exception as e:
                logger.debug(f"Streaming chunk error: {e}")
        return ""

    def finish(self) -> str:
        if self._started and hasattr(self.transcriber, "stop"):
            try:
                final = self.transcriber.stop()
                if final and hasattr(final, "text"):
                    return final.text
            except Exception as e:
                logger.debug(f"Streaming stop error: {e}")

        # Fallback to transcribe_without_streaming over the accumulated buffer
        if len(self.buffer) > 0 and hasattr(self.transcriber, "transcribe_without_streaming"):
            try:
                import numpy as np
                audio_np = np.frombuffer(bytes(self.buffer), dtype=np.int16).astype(np.float32) / 32768.0
                result = self.transcriber.transcribe_without_streaming(audio_np, sample_rate=self.sample_rate, flags=0)
                if hasattr(result, "lines"):
                    return " ".join(line.text for line in result.lines).strip()
            except Exception as e:
                logger.error(f"Finish transcribe error: {e}")
        return ""


class MoonshineSTTService:
    _instance: Optional[MoonshineSTTService] = None

    def __init__(self, model_size: str = "small-streaming"):
        self.model_size = model_size
        self.engine = "none"
        self.transcriber = None
        self._init_model()

    @classmethod
    def get_instance(cls, model_size: str = "small-streaming") -> MoonshineSTTService:
        if cls._instance is None:
            cls._instance = MoonshineSTTService(model_size=model_size)
        return cls._instance

    def _init_model(self) -> None:
        # Try Moonshine Voice first
        try:
            from moonshine_voice import Transcriber, ModelArch, get_model_for_language
            arch = ModelArch.SMALL_STREAMING
            if self.model_size == "medium-streaming":
                arch = ModelArch.MEDIUM_STREAMING
            elif self.model_size == "tiny-streaming":
                arch = ModelArch.TINY_STREAMING

            model_path, model_arch = get_model_for_language("en", arch)
            self.transcriber = Transcriber(model_path=model_path, model_arch=model_arch)
            self.engine = "moonshine-small-streaming"
            logger.info("Moonshine Small Streaming STT initialized successfully.")
            return
        except ImportError:
            logger.warning("moonshine-voice package not installed. Checking faster-whisper fallback...")
        except Exception as e:
            logger.warning(f"Failed to initialize moonshine-voice: {e}. Checking faster-whisper fallback...")

        # Fallback to faster-whisper on CPU
        try:
            from faster_whisper import WhisperModel
            import urllib.request
            # Check if network is available before attempting download
            self.transcriber = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=4, local_files_only=True)
            self.engine = "faster-whisper-small-int8"
            logger.info("faster-whisper small.en (INT8 CPU) fallback initialized.")
            return
        except ImportError:
            logger.warning("faster-whisper not installed. Running in mock/development mode.")
        except Exception as e:
            logger.warning(f"Failed to initialize faster-whisper: {e}. Running in mock/development mode.")

        self.engine = "mock"

    def transcribe_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
        t0 = time.time()
        text = ""

        if self.engine.startswith("moonshine") and self.transcriber is not None:
            import numpy as np
            # Check if WAV or raw PCM
            if audio_bytes.startswith(b"RIFF"):
                import scipy.io.wavfile as wav
                sr, pcm = wav.read(io.BytesIO(audio_bytes))
                sample_rate = sr
                if pcm.dtype == np.int16:
                    audio_np = pcm.astype(np.float32) / 32768.0
                else:
                    audio_np = pcm.astype(np.float32)
            else:
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            result = self.transcriber.transcribe_without_streaming(audio_np, sample_rate=sample_rate, flags=0)
            if hasattr(result, "lines"):
                text = " ".join(line.text for line in result.lines).strip()
            elif hasattr(result, "text"):
                text = result.text.strip()

        elif self.engine.startswith("faster-whisper") and self.transcriber is not None:
            import numpy as np
            if audio_bytes.startswith(b"RIFF"):
                import scipy.io.wavfile as wav
                _, pcm = wav.read(io.BytesIO(audio_bytes))
                audio_np = pcm.astype(np.float32) / 32768.0 if pcm.dtype == np.int16 else pcm
            else:
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            segs, _ = self.transcriber.transcribe(audio_np, beam_size=1)
            text = " ".join(s.text.strip() for s in segs).strip()

        else:
            # Mock transcription for testing
            text = "Hello JARVIS, testing voice transcription."

        duration = round(time.time() - t0, 3)
        return {
            "text": text,
            "language": "en",
            "duration": duration,
            "model": self.engine,
            "sample_rate": sample_rate,
        }

    def create_streaming_session(self, sample_rate: int = 16000) -> MoonshineStreamSession:
        return MoonshineStreamSession(self.transcriber, sample_rate=sample_rate)

    def is_ready(self) -> bool:
        return self.transcriber is not None or self.engine == "mock"

