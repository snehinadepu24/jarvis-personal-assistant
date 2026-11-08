from __future__ import annotations

import logging
import sys

if sys.platform != "win32":
    raise ImportError("stt.py is Windows-only")

import numpy as np

logger = logging.getLogger(__name__)


class Transcriber:
    """
    STT Transcriber supporting Moonshine Small Streaming (primary)
    with automatic CPU-safe faster-whisper fallback.
    """
    def __init__(
        self,
        engine: str = "moonshine",
        model_size: str = "small-streaming",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.engine = engine
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.stt = None
        self._init_engine()

    def _init_engine(self) -> None:
        if self.engine == "moonshine":
            try:
                from moonshine_voice import Transcriber as MoonshineTranscriber, ModelArch, get_model_for_language
                arch = ModelArch.SMALL_STREAMING
                if "medium" in self.model_size:
                    arch = ModelArch.MEDIUM_STREAMING
                elif "tiny" in self.model_size:
                    arch = ModelArch.TINY_STREAMING
                model_path, model_arch = get_model_for_language("en", arch)
                self.stt = MoonshineTranscriber(model_path=model_path, model_arch=model_arch)
                logger.info("Moonshine Small Streaming STT initialized.")
                return
            except Exception as e:
                logger.warning(f"Moonshine STT unavailable ({e}), falling back to faster-whisper.")

        # Fallback to faster-whisper
        try:
            from faster_whisper import WhisperModel
            actual_model = "small.en" if self.model_size == "small-streaming" else self.model_size
            self.stt = WhisperModel(actual_model, device=self.device, compute_type=self.compute_type)
            self.engine = "faster-whisper"
            logger.info(f"faster-whisper STT initialized ({actual_model}, {self.device}).")
            return
        except Exception as e:
            logger.warning(f"faster-whisper initialization error: {e}")

        self.engine = "mock"

    def transcribe(self, pcm16: bytes, language: str = "en") -> str:
        if not pcm16:
            return ""

        audio = np.frombuffer(pcm16, np.int16).astype(np.float32) / 32768.0

        if self.engine == "moonshine" and self.stt is not None:
            try:
                result = self.stt.transcribe_without_streaming(
                    audio.tolist(), sample_rate=16000, flags=0
                )
                if hasattr(result, "lines"):
                    return " ".join(l.text.strip() for l in result.lines).strip()
                if hasattr(result, "text"):
                    return result.text.strip()
            except Exception as e:
                logger.error(f"Moonshine transcribe error: {e}")

        elif self.engine == "faster-whisper" and self.stt is not None:
            try:
                segs, _ = self.stt.transcribe(audio, language=language, beam_size=1, vad_filter=True)
                return " ".join(s.text.strip() for s in segs).strip()
            except Exception as e:
                logger.error(f"faster-whisper transcribe error: {e}")

        return ""
