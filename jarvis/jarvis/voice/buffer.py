from __future__ import annotations

from collections import deque


class RingBuffer:
    def __init__(self, capacity_frames: int, frame_size: int):
        self.capacity = capacity_frames
        self.frame_size = frame_size
        self._buf: deque[bytes] = deque(maxlen=capacity_frames)

    def push(self, frame: bytes) -> None:
        self._buf.append(frame)

    def read_all(self) -> bytes:
        return b"".join(self._buf)

    def clear(self) -> None:
        self._buf.clear()

    def __len__(self) -> int:
        return len(self._buf) * self.frame_size
