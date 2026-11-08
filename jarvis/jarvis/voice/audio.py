from __future__ import annotations

import sys

if sys.platform != "win32":
    raise ImportError("audio.py is Windows-only (sounddevice/PortAudio capture)")

import sounddevice as sd

from jarvis.voice.buffer import RingBuffer

SAMPLE_RATE = 16000
BLOCK = 512


class AudioWorker:
    def __init__(self, on_frame=None):
        self.ring = RingBuffer(capacity_frames=16000 * 60 // BLOCK, frame_size=BLOCK * 2)
        self._stream = None
        self.on_frame = on_frame

    def start(self):
        def cb(indata, frames, time_info, status):
            frame = bytes(indata)
            self.ring.push(frame)
            if self.on_frame:
                self.on_frame(frame)

        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=BLOCK, callback=cb
        )
        self._stream.start()

    def restart_on_portaudio_error(self) -> None:
        try:
            sd.query_devices()
            self.start()
        except Exception as e:
            raise RuntimeError(f"no audio device available: {e}")

    def stop(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
