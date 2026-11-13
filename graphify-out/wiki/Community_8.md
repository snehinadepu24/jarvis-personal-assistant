# Community 8

> 13 nodes

## Key Concepts

- **WakeWord** (16 connections) — `jarvis/jarvis/voice/wakeword.py`
- **.listen()** (4 connections) — `jarvis/jarvis/voice/wakeword.py`
- **audio_callback()** (3 connections) — `jarvis/jarvis/voice/wakeword.py`
- **.process_frame()** (3 connections) — `jarvis/jarvis/voice/wakeword.py`
- **test_jarvis_wakeword_desktop()** (3 connections) — `tests/test_voice_pipeline.py`
- **.__init__()** (2 connections) — `jarvis/jarvis/voice/wakeword.py`
- **._init_engine()** (2 connections) — `jarvis/jarvis/voice/wakeword.py`
- **run_loop()** (2 connections) — `jarvis/jarvis/voice/wakeword.py`
- **.toggle()** (2 connections) — `jarvis/jarvis/voice/wakeword.py`
- **.set_enabled()** (1 connections) — `jarvis/jarvis/voice/wakeword.py`
- **Continuously listen from sounddevice audio input in a background thread.** (1 connections) — `jarvis/jarvis/voice/wakeword.py`
- **Offline wake-word detector with runtime enable/disable toggling. Defaults to…** (1 connections) — `jarvis/jarvis/voice/wakeword.py`
- **Process a chunk of 16kHz 16-bit mono PCM. Returns True if wake word detected.** (1 connections) — `jarvis/jarvis/voice/wakeword.py`

## Relationships

- [Community 11](Community_11.md) (3 shared connections)
- [Community 37](Community_37.md) (2 shared connections)
- [Community 68](Community_68.md) (2 shared connections)
- [Community 16](Community_16.md) (1 shared connections)
- [Cli Module](Cli_Module.md) (1 shared connections)

## Source Files

- `jarvis/jarvis/voice/wakeword.py`
- `tests/test_voice_pipeline.py`

## Audit Trail

- EXTRACTED: 21 (84%)
- INFERRED: 4 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*