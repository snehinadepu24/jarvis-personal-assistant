import io
import pytest
from backend.services.stt_service import MoonshineSTTService
from backend.services.tts_service import PocketTTSService
from backend.services.wakeword_service import WakeWordService
from jarvis.jarvis.voice.wakeword import WakeWord
from jarvis.jarvis.voice.stt import Transcriber


def test_stt_service_initialization():
    stt = MoonshineSTTService.get_instance()
    assert stt is not None
    assert stt.is_ready()
    dummy_pcm = b"\x00" * 3200
    result = stt.transcribe_bytes(dummy_pcm)
    assert "text" in result
    assert "duration" in result
    assert "model" in result


def test_tts_service_initialization():
    tts = PocketTTSService.get_instance()
    assert tts is not None
    assert tts.is_ready()
    wav_bytes = tts.generate_speech("Hello, this is a test.", voice="alba")
    assert isinstance(wav_bytes, bytes)
    assert len(wav_bytes) > 44
    assert wav_bytes.startswith(b"RIFF")


def test_wakeword_service_toggle():
    ww = WakeWordService.get_instance(enabled=False)
    assert not ww.enabled

    ww.set_enabled(True)
    assert ww.enabled

    dummy_chunk = b"\x00" * 2560
    pred = ww.predict_chunk(dummy_chunk)
    assert "detected" in pred
    assert "confidence" in pred
    assert pred["enabled"] is True

    ww.set_enabled(False)
    assert not ww.enabled
    pred_disabled = ww.predict_chunk(dummy_chunk)
    assert pred_disabled["detected"] is False
    assert pred_disabled["enabled"] is False


def test_jarvis_wakeword_desktop():
    ww_desktop = WakeWord(keyword="hey_jarvis", enabled=False)
    assert not ww_desktop.enabled
    assert ww_desktop.toggle() is True
    assert ww_desktop.enabled is True
    assert ww_desktop.toggle() is False
    assert ww_desktop.enabled is False


def test_jarvis_stt_desktop():
    transcriber = Transcriber(model_size="small-streaming", device="cpu")
    assert transcriber is not None
    dummy_pcm = b"\x00" * 1600
    res = transcriber.transcribe(dummy_pcm)
    assert isinstance(res, str)


def test_voice_config_api_functions():
    from backend.server import get_voice_config, update_voice_config, VoiceConfigUpdate

    cfg = get_voice_config()
    assert cfg.hotkey == "<ctrl_r>+<space>"
    assert hasattr(cfg, "wakeword_enabled")

    updated_on = update_voice_config(VoiceConfigUpdate(wakeword_enabled=True))
    assert updated_on.wakeword_enabled is True

    updated_off = update_voice_config(VoiceConfigUpdate(wakeword_enabled=False))
    assert updated_off.wakeword_enabled is False
