"""
Wake Word Service powered by openWakeWord ('hey_jarvis' ONNX) with toggle support.
"""
from __future__ import annotations

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WakeWordService:
    _instance: Optional[WakeWordService] = None

    def __init__(self, model_name: str = "hey_jarvis", threshold: float = 0.50, enabled: bool = False):
        self.model_name = model_name
        self.threshold = threshold
        self.enabled = enabled
        self.oww_model = None
        self.engine = "none"
        self._init_model()

    @classmethod
    def get_instance(cls, model_name: str = "hey_jarvis", threshold: float = 0.50, enabled: bool = False) -> WakeWordService:
        if cls._instance is None:
            cls._instance = WakeWordService(model_name=model_name, threshold=threshold, enabled=enabled)
        return cls._instance

    def _init_model(self) -> None:
        try:
            from openwakeword.model import Model
            # Load specific openWakeWord model
            self.oww_model = Model(wakeword_models=[self.model_name], inference_framework="onnx")
            self.engine = "openwakeword-onnx"
            logger.info("openWakeWord ('hey_jarvis' ONNX) initialized.")
            return
        except ImportError:
            logger.warning("openwakeword not installed. Running in heuristic/mock mode.")
        except Exception as e:
            logger.warning(f"Could not load openwakeword model: {e}. Running in heuristic/mock mode.")

        self.engine = "mock"

    def set_enabled(self, enabled: bool) -> bool:
        self.enabled = enabled
        logger.info(f"Wake word detection set to: {self.enabled}")
        return self.enabled

    def predict_chunk(self, pcm_chunk: bytes) -> Dict[str, Any]:
        """
        Takes raw 16kHz 16-bit mono PCM bytes (typically 80ms/1280 samples or similar).
        Returns whether the target wake word was detected above threshold.
        """
        if not self.enabled:
            return {"detected": False, "confidence": 0.0, "keyword": self.model_name, "enabled": False}

        import numpy as np
        audio_int16 = np.frombuffer(pcm_chunk, dtype=np.int16)

        if self.engine == "openwakeword-onnx" and self.oww_model is not None:
            try:
                # openwakeword prediction returns dict of {model_name: score}
                prediction = self.oww_model.predict(audio_int16)
                # Find matching model score
                for key, score in prediction.items():
                    if self.model_name.lower() in key.lower() or "jarvis" in key.lower():
                        detected = float(score) >= self.threshold
                        return {
                            "detected": detected,
                            "confidence": float(score),
                            "keyword": key,
                            "enabled": True,
                        }
            except Exception as e:
                logger.debug(f"openWakeWord predict error: {e}")

        # Default non-detection
        return {"detected": False, "confidence": 0.0, "keyword": self.model_name, "enabled": True}

    def reset(self) -> None:
        if self.oww_model and hasattr(self.oww_model, "reset"):
            self.oww_model.reset()

