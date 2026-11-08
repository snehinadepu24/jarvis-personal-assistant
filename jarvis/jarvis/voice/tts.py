from __future__ import annotations

import logging
import sys

if sys.platform != "win32":
    raise ImportError("tts.py is Windows-only")

logger = logging.getLogger(__name__)

_pocket_model = None
_pocket_voice = None


def speak_pocket_tts(text: str, voice: str = "alba") -> bool:
    """Generate and play speech using Pocket TTS 7M INT8."""
    global _pocket_model, _pocket_voice
    try:
        if _pocket_model is None:
            import os
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            from pocket_tts import TTSModel
            _pocket_model = TTSModel.load_model(language="english_7m_refl_2026-10", quantize=True)
            _pocket_voice = _pocket_model.get_state_for_audio_prompt(voice)

        import sounddevice as sd
        audio = _pocket_model.generate_audio(_pocket_voice, text)
        audio_array = audio.detach().cpu().numpy()
        sd.play(audio_array, _pocket_model.sample_rate)
        sd.wait()
        return True
    except Exception as e:
        logger.debug(f"Pocket TTS error: {e}")
        return False


def speak_winrt(text: str) -> None:
    import asyncio
    from winrt.windows.media.playback import MediaPlayer
    from winrt.windows.media.speechsynthesis import SpeechSynthesizer

    async def run():
        synth = SpeechSynthesizer()
        stream = await synth.synthesize_text_to_stream_async(text)
        player = MediaPlayer()
        if not hasattr(player, "set_source_from_stream_async"):
            raise RuntimeError("installed WinRT MediaPlayer does not support stream playback")
        await player.set_source_from_stream_async(stream)
        player.play()

    asyncio.run(run())


def speak_pyttsx3(text: str) -> None:
    import pyttsx3
    pyttsx3.speak(text)


def speak(text: str, voice: str = "alba") -> None:
    """
    Synthesize and speak text.
    Cascade: Pocket TTS 7M INT8 -> compatible WinRT -> pyttsx3
    """
    if getattr(sys, "frozen", False):
        try:
            speak_pyttsx3(text)
            return
        except Exception as error:
            logger.warning("Portable TTS backend unavailable: %s", error)
    if speak_pocket_tts(text, voice=voice):
        return
    try:
        from winrt.windows.media.playback import MediaPlayer

        if not hasattr(MediaPlayer(), "set_source_from_stream_async"):
            raise RuntimeError("installed WinRT MediaPlayer does not support stream playback")
        speak_winrt(text)
        return
    except Exception as error:
        logger.debug("WinRT TTS unavailable: %s", error)
    try:
        speak_pyttsx3(text)
    except Exception as error:
        logger.error("All TTS backends failed: %s", error)
