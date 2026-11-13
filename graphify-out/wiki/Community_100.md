# Community 100

> 10 nodes

## Key Concepts

- **WakeWordService** (11 connections) — `backend/services/wakeword_service.py`
- **test_wakeword_service_toggle()** (5 connections) — `tests/test_voice_pipeline.py`
- **.predict_chunk()** (4 connections) — `backend/services/wakeword_service.py`
- **.get_instance()** (2 connections) — `backend/services/wakeword_service.py`
- **.__init__()** (2 connections) — `backend/services/wakeword_service.py`
- **._init_model()** (2 connections) — `backend/services/wakeword_service.py`
- **.set_enabled()** (2 connections) — `backend/services/wakeword_service.py`
- **.reset()** (1 connections) — `backend/services/wakeword_service.py`
- **Any** (1 connections)
- **Takes raw 16kHz 16-bit mono PCM bytes (typically 80ms/1280 samples or similar).…** (1 connections) — `backend/services/wakeword_service.py`

## Relationships

- [Community 68](Community_68.md) (4 shared connections)
- [FastAPI Status & Server API](FastAPI_Status_&_Server_API.md) (1 shared connections)

## Source Files

- `backend/services/wakeword_service.py`
- `tests/test_voice_pipeline.py`

## Audit Trail

- EXTRACTED: 15 (83%)
- INFERRED: 3 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*