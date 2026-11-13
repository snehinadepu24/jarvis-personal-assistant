# Agent Loop Detection

> 12 nodes

## Key Concepts

- **AudioWorker** (9 connections) — `jarvis/jarvis/voice/audio.py`
- **RingBuffer** (9 connections) — `jarvis/jarvis/voice/buffer.py`
- **audio.py** (5 connections) — `jarvis/jarvis/voice/audio.py`
- **buffer.py** (3 connections) — `jarvis/jarvis/voice/buffer.py`
- **.__init__()** (2 connections) — `jarvis/jarvis/voice/audio.py`
- **.stop()** (1 connections) — `jarvis/jarvis/voice/audio.py`
- **.clear()** (1 connections) — `jarvis/jarvis/voice/buffer.py`
- **.__init__()** (1 connections) — `jarvis/jarvis/voice/buffer.py`
- **.__len__()** (1 connections) — `jarvis/jarvis/voice/buffer.py`
- **.push()** (1 connections) — `jarvis/jarvis/voice/buffer.py`
- **.read_all()** (1 connections) — `jarvis/jarvis/voice/buffer.py`
- **sounddevice** (1 connections)

## Relationships

- [Community 37](Community_37.md) (2 shared connections)
- [Community 118](Community_118.md) (2 shared connections)
- [Community 16](Community_16.md) (1 shared connections)
- [Cli Module](Cli_Module.md) (1 shared connections)
- [Community 30](Community_30.md) (1 shared connections)

## Source Files

- `jarvis/jarvis/voice/audio.py`
- `jarvis/jarvis/voice/buffer.py`

## Audit Trail

- EXTRACTED: 19 (90%)
- INFERRED: 2 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*