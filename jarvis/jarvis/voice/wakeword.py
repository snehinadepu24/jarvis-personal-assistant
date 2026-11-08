from __future__ import annotations

import logging
import importlib
import sys
import threading
from typing import Callable, Optional

if sys.platform != "win32":
    raise ImportError("wakeword.py is Windows-only; push-to-talk is the v1 default, wake word optional")

import numpy as np

logger = logging.getLogger(__name__)

MODELS = {
    "openWakeWord": {"pkg": "openwakeword", "model": "hey_jarvis", "license": "Apache-2.0"},
    "porcupine": {"pkg": "pvporcupine", "license": "requires AccessKey"},
}


class WakeWord:
    """
    Offline wake-word detector with runtime enable/disable toggling.
    Defaults to openWakeWord with 'hey_jarvis' ONNX model.
    """
    def __init__(
        self,
        engine: str = "openWakeWord",
        keyword: str = "hey_jarvis",
        threshold: float = 0.50,
        access_key: str = "",
        enabled: bool = False,
    ):
        self.engine = engine
        self.keyword = keyword
        self.threshold = threshold
        self.access_key = access_key
        self.enabled = enabled
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._model = None
        self._init_engine()

    def _init_engine(self) -> None:
        if self.engine.lower() in ("openwakeword", "hey_jarvis"):
            try:
                Model = importlib.import_module("openwakeword.model").Model
                self._model = Model(wakeword_models=[self.keyword], inference_framework="onnx")
                self.engine = "openWakeWord"
                logger.info(f"openWakeWord initialized for keyword '{self.keyword}'")
                return
            except ImportError as error:
                logger.warning(
                    "OpenWakeWord could not be imported: %s. "
                    "Ensure the packaged OpenWakeWord and ONNX Runtime files are present.",
                    error,
                )
            except Exception as e:
                logger.warning(f"Could not load openWakeWord model: {e}")

        elif self.engine.lower() == "porcupine":
            if not self.access_key:
                logger.warning("Picovoice Porcupine selected but no access_key provided.")
            else:
                try:
                    import pvporcupine
                    self._model = pvporcupine.create(access_key=self.access_key, keywords=[self.keyword])
                    logger.info("Porcupine initialized.")
                    return
                except Exception as e:
                    logger.warning(f"Failed to initialize Porcupine: {e}")

        self.engine = "stub"

    def set_enabled(self, enabled: bool) -> bool:
        self.enabled = enabled
        logger.info(f"WakeWord enabled: {self.enabled}")
        return self.enabled

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        logger.info(f"WakeWord toggled to: {self.enabled}")
        return self.enabled

    def process_frame(self, pcm16_chunk: bytes) -> bool:
        """
        Process a chunk of 16kHz 16-bit mono PCM. Returns True if wake word detected.
        """
        if not self.enabled or self._model is None:
            return False

        audio_int16 = np.frombuffer(pcm16_chunk, dtype=np.int16)

        if self.engine == "openWakeWord":
            try:
                scores = self._model.predict(audio_int16)
                for k, v in scores.items():
                    if float(v) >= self.threshold:
                        return True
            except Exception as e:
                logger.debug(f"Prediction error: {e}")

        elif self.engine == "porcupine":
            try:
                res = self._model.process(audio_int16)
                if res >= 0:
                    return True
            except Exception as e:
                logger.debug(f"Porcupine process error: {e}")

        return False

    def listen(self, on_wake: Callable[[], None]) -> None:
        """Continuously listen from sounddevice audio input in a background thread."""
        import sounddevice as sd

        self._running = True
        sample_rate = 16000
        block_size = 1280  # 80ms chunks

        def audio_callback(indata, frames, time_info, status):
            if not self._running:
                return
            if self.enabled:
                if self.process_frame(bytes(indata)):
                    logger.info("Wake word detected!")
                    try:
                        on_wake()
                    except Exception as e:
                        logger.error(f"Error in on_wake callback: {e}")

        def run_loop():
            try:
                with sd.InputStream(samplerate=sample_rate, channels=1, dtype="int16", blocksize=block_size, callback=audio_callback):
                    while self._running:
                        sd.sleep(100)
            except Exception as e:
                logger.error(f"WakeWord listen error: {e}")

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
