from __future__ import annotations

import audioop
import struct


class EnergyVAD:
    def __init__(self, threshold: int = 500, silence_ms: int = 500, frame_ms: int = 32):
        self.threshold = threshold
        self.silence_ms = silence_ms
        self.frame_ms = frame_ms

    def is_speech(self, pcm16: bytes) -> bool:
        try:
            return audioop.rms(pcm16, 2) > self.threshold
        except Exception:
            return False

    def utterance_end(self, silence_frames: int, sample_rate: int) -> bool:
        frames_per_ms = sample_rate / 1000
        return silence_frames * self.frame_ms * frames_per_ms >= self.silence_ms * frames_per_ms / self.frame_ms


class SileroVAD:
    def __init__(self):
        import onnxruntime

        self.model = onnxruntime.InferenceSession("silero_vad.onnx")

    def is_speech(self, pcm16: bytes, sample_rate: int = 16000) -> bool:
        import numpy as np

        x = np.frombuffer(pcm16, np.int16).astype(np.float32) / 32768.0
        out = self.model.run(None, {"input": x[None, :], "sr": np.array([sample_rate], dtype=np.int64)})
        return float(out[0][0][0]) > 0.5
