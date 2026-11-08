from __future__ import annotations

import asyncio
import random
import sys
import threading
import struct
import traceback

from jarvis.agent.state_machine import AgentContext, run_task
from jarvis.config import Config
from jarvis.connectors.files import FilesConnector
from jarvis.desktop.orb import Orb
from jarvis.desktop.permissions import check_permissions
from jarvis.llm.gemini import GeminiLLM
from jarvis.llm.router import LlmRouter
from jarvis.safety.audit import Audit
from jarvis.safety.gate import ConfirmationGate


STARTUP_GREETINGS = (
    "Hey, I'm ready. How may I help you?",
    "Good to see you. What can I take care of?",
    "I'm online and ready when you are.",
    "Welcome back. What would you like me to do?",
    "All set, buddy. How can I help?",
)


class DesktopHost:
    def __init__(self, cfg: Config, *, wakeword_required: bool = True) -> None:
        if sys.platform != "win32":
            raise RuntimeError("Desktop mode is supported only on Windows.")
        self.cfg = cfg
        self.status = check_permissions(wakeword_required=wakeword_required)
        if not self.status.ready:
            raise RuntimeError("Desktop prerequisites are not ready:\n- " + "\n- ".join(self.status.details))
        from jarvis.desktop.uia_bootstrap import ensure_uia_type_library

        try:
            ensure_uia_type_library()
        except Exception as error:
            raise RuntimeError(
                "Windows UI Automation type-library initialization failed. "
                "Run the desktop command once as the same user to generate COM bindings: "
                f"{error}"
            ) from error
        from jarvis.actions.uia_executor import UiaExecutor
        from jarvis.perception.base import build_backend

        self.backend = build_backend(cfg)
        self.executor = UiaExecutor(self.backend, FilesConnector(cfg.data_dir / "fs"))
        self.orb = Orb()
        self.orb.ready.wait(timeout=5)
        if self.orb.error:
            raise RuntimeError(f"Floating orb could not start: {self.orb.error}") from self.orb.error
        self._stop = threading.Event()

    def run(self) -> None:
        from jarvis.ui.tray import Tray
        from jarvis.voice.audio import AudioWorker
        from jarvis.voice.ptt import PushToTalk
        from jarvis.voice.stt import Transcriber
        from jarvis.voice.tts import speak
        from jarvis.voice.wakeword import WakeWord

        wakeword = WakeWord(enabled=True)
        transcriber = Transcriber(
            engine="faster-whisper" if getattr(sys, "frozen", False) else "moonshine",
            model_size="small-streaming",
            device="cpu",
            compute_type="int8",
        )
        paused = threading.Event()

        def start() -> None:
            if paused.is_set():
                return
            self.orb.set_state("listening", "Speak now")

        def on_frame(frame: bytes) -> None:
            samples = struct.unpack(f"<{len(frame) // 2}h", frame)
            if samples:
                rms = (sum(sample * sample for sample in samples) / len(samples)) ** 0.5
                # Speech-level scaling for int16 microphone samples.
                level = min(1.0, max(0.0, (rms - 180.0) / 4200.0))
                self.orb.set_level(level)
            if wakeword.process_frame(frame):
                start()

        audio = AudioWorker(
            on_frame=on_frame
        )
        try:
            audio.start()
        except Exception as error:
            self._report_error("Audio capture failed", error)
            self.orb.set_state("error", "Microphone unavailable")
            raise

        def stop() -> None:
            self.orb.set_state("thinking", "Processing")
            pcm = audio.ring.read_all()
            audio.ring.clear()
            threading.Thread(target=self._process, args=(pcm, transcriber, speak), daemon=True).start()

        recording = False

        def tap_to_speak() -> None:
            nonlocal recording
            if recording:
                recording = False
                stop()
            else:
                recording = True
                start()

        self.orb.set_click_handler(tap_to_speak)

        def quit_host() -> None:
            self._stop.set()
            wakeword.stop()
            audio.stop()
            self.orb.close()

        def cancel() -> None:
            paused.set()
            self.orb.set_state("paused", "Stopped")

        def toggle_pause() -> None:
            if paused.is_set():
                paused.clear()
                self.orb.set_state("idle", "Ready")
            else:
                paused.set()
                self.orb.set_state("paused", "Paused")

        tray = Tray(start, cancel, toggle_pause, quit_host, wakeword_enabled=True)
        tray.run()
        ptt = PushToTalk(start, stop)
        threading.Thread(target=ptt.run, name="jarvis-ptt", daemon=True).start()
        print("JARVIS desktop host is running.", flush=True)
        print("Floating orb: active | System tray: active | Wake word: Hey Jarvis", flush=True)
        print("Push-to-talk: Left Ctrl + Space or Right Ctrl + Space | Close with the tray Quit menu.", flush=True)
        self._greet(speak)
        while not self._stop.wait(0.5):
            pass

    def _greet(self, speak) -> None:
        greeting = random.SystemRandom().choice(STARTUP_GREETINGS)
        self.orb.set_state("speaking", greeting)

        def speak_greeting() -> None:
            try:
                speak(greeting)
                self.orb.set_state("idle", "Ready")
            except Exception as error:
                self._report_error("Startup greeting TTS failed", error)
                self.orb.set_state("error", "Greeting audio failed")

        threading.Thread(target=speak_greeting, name="jarvis-greeting", daemon=True).start()

    def _process(self, pcm: bytes, transcriber, speak) -> None:
        if pcm:
            samples = struct.unpack(f"<{len(pcm) // 2}h", pcm)
            rms = (sum(sample * sample for sample in samples) / len(samples)) ** 0.5
            peak = max(abs(sample) for sample in samples)
            print(
                f"JARVIS audio: {len(pcm) / 32000:.2f}s, RMS={rms:.0f}, peak={peak}",
                flush=True,
            )
        try:
            text = transcriber.transcribe(pcm)
        except Exception as error:
            self._report_error("Speech transcription failed", error)
            self.orb.set_state("error", "Transcription failed")
            return
        if not text:
            print("JARVIS: no speech detected in the recording.", flush=True)
            self.orb.set_state("error", "No speech detected")
            return
        print(f"\n[JARVIS USER] {text}", flush=True)
        try:
            self.orb.set_state("thinking", text)
            result = asyncio.run(self._run_goal(text))
            response = result.summary or ("Task completed." if result.status == "done" else result.error)
            print(f"[JARVIS RESPONSE] {response}", flush=True)
            self.orb.set_state("speaking", response)
            speak(response)
            self.orb.set_state("idle", "Ready")
        except Exception as error:
            self._report_error("Assistant task failed", error)
            message = str(error)
            if "quota exhausted" in message.lower():
                message = "Gemini quota exhausted"
                print(
                    "JARVIS HINT: Gemini free-tier quota is exhausted. "
                    "Wait for reset or configure another API key/project.",
                    flush=True,
                )
            self.orb.set_state("error", message)
            if "COMError" in type(error).__name__:
                print(
                    "JARVIS hint: Windows UI Automation returned a transient COM "
                    "event error; the request was not executed.",
                    flush=True,
                )
            try:
                speak("I could not complete that request.")
            except Exception as speech_error:
                self._report_error("Error response TTS failed", speech_error)

    async def _run_goal(self, goal: str):
        planner = LlmRouter(GeminiLLM(self.cfg.planner_model), thinking=self.cfg.thinking)
        planner.set_goal(goal)
        audit = Audit(self.cfg.audit_db)
        gate = ConfirmationGate(
            cancel_window_s=self.cfg.gate_cancel_window_s,
            timeout_s=self.cfg.gate_timeout_s,
            speak_summary=self.cfg.gate_speak,
        )
        ctx = AgentContext(
            llm=planner,
            backend=self.backend,
            executor=self.executor,
            gate=gate,
            audit=audit,
            budgets=self.cfg.budgets,
            task_name="desktop_voice",
            allow_connectors=True,
            allow_vlm=False,
        )
        try:
            return await run_task(goal, ctx)
        finally:
            audit.close()

    @staticmethod
    def _report_error(context: str, error: BaseException) -> None:
        print(f"JARVIS ERROR: {context}: {error}", flush=True)
        traceback.print_exception(type(error), error, error.__traceback__)
