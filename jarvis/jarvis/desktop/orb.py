from __future__ import annotations

import math
import queue
import sys
import threading
import time
import traceback
from typing import Callable, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageTk


# Golden ratio angle for uniform spherical particle distribution (exact web component algorithm)
PARTICLE_COUNT = 360
TWO_PI = math.pi * 2.0
GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))
ANGLE_X = 0.32
TIME_OFFSET = 1.7

# Color definitions matching frontend particles-orb.tsx
COLOR_FROM = (240, 171, 252)    # #f0abfc (fuchsia/lavender)
COLOR_TO = (129, 140, 248)      # #818cf8 (indigo)
ERROR_FROM = (251, 113, 133)    # #fb7185 (rose)
ERROR_TO = (244, 63, 94)        # #f43f5e (red)
LISTEN_FROM = (52, 211, 153)    # #34d399 (emerald)
LISTEN_TO = (96, 165, 250)      # #60a5fa (blue)
THINK_FROM = (251, 191, 36)     # #fbbf24 (amber)
THINK_TO = (245, 158, 11)       # #f59e0b (orange)
SPEAK_FROM = (192, 132, 252)    # #c084fc (violet)
SPEAK_TO = (129, 140, 248)      # #818cf8 (indigo)
IDLE_FROM = (240, 171, 252)
IDLE_TO = (129, 140, 248)

# State dynamics matrix from frontend web component
STATE_PARAMS = {
    "idle": {
        "tempo": 1.0, "spin": 0.14, "breathe": 0.05, "drift": 1.0,
        "ripple": 0.0, "swell": 0.04, "flow": 0.0, "swirl": 0.0,
        "pulse": 0.0, "pulseRate": 1.0, "ring": 0.0, "jitter": 0.0,
        "shake": 0.0, "alpha": 0.85, "rest": 0.0,
        "from_rgb": IDLE_FROM, "to_rgb": IDLE_TO,
    },
    "connecting": {
        "tempo": 1.0, "spin": 0.30, "breathe": 0.02, "drift": 0.2,
        "ripple": 0.0, "swell": 0.0, "flow": 0.0, "swirl": 0.0,
        "pulse": 0.06, "pulseRate": 0.5, "ring": 1.0, "jitter": 0.0,
        "shake": 0.0, "alpha": 0.90, "rest": 0.12,
        "from_rgb": THINK_FROM, "to_rgb": THINK_TO,
    },
    "listening": {
        "tempo": 1.0, "spin": 0.55, "breathe": 0.012, "drift": 0.0,
        "ripple": 1.0, "swell": 0.14, "flow": 0.0, "swirl": 0.0,
        "pulse": 0.0, "pulseRate": 1.0, "ring": 0.0, "jitter": 0.0,
        "shake": 0.0, "alpha": 0.95, "rest": 0.55,
        "from_rgb": LISTEN_FROM, "to_rgb": LISTEN_TO,
    },
    "thinking": {
        "tempo": 1.0, "spin": 0.32, "breathe": 0.01, "drift": 0.0,
        "ripple": 0.0, "swell": 0.0, "flow": 0.0, "swirl": 0.0,
        "pulse": 1.0, "pulseRate": 1.0, "ring": 0.0, "jitter": 0.0,
        "shake": 0.0, "alpha": 0.90, "rest": 0.30,
        "from_rgb": THINK_FROM, "to_rgb": THINK_TO,
    },
    "speaking": {
        "tempo": 1.0, "spin": 0.24, "breathe": 0.01, "drift": 0.0,
        "ripple": 0.0, "swell": 0.06, "flow": 1.0, "swirl": 1.0,
        "pulse": 0.0, "pulseRate": 1.0, "ring": 0.0, "jitter": 0.6,
        "shake": 0.0, "alpha": 0.95, "rest": 0.55,
        "from_rgb": SPEAK_FROM, "to_rgb": SPEAK_TO,
    },
    "error": {
        "tempo": 1.0, "spin": 0.08, "breathe": 0.0, "drift": 0.0,
        "ripple": 0.0, "swell": 0.0, "flow": 0.0, "swirl": 0.0,
        "pulse": 0.0, "pulseRate": 1.0, "ring": 0.0, "jitter": 0.7,
        "shake": 1.0, "alpha": 0.90, "rest": 0.20,
        "from_rgb": ERROR_FROM, "to_rgb": ERROR_TO,
    },
    "paused": {
        "tempo": 0.04, "spin": 0.0, "breathe": 0.0, "drift": 0.0,
        "ripple": 0.0, "swell": 0.0, "flow": 0.0, "swirl": 0.0,
        "pulse": 0.0, "pulseRate": 1.0, "ring": 0.0, "jitter": 0.0,
        "shake": 0.0, "alpha": 0.45, "rest": 0.0,
        "from_rgb": (100, 116, 139), "to_rgb": (71, 85, 105),
    },
    "disabled": {
        "tempo": 0.04, "spin": 0.0, "breathe": 0.0, "drift": 0.0,
        "ripple": 0.0, "swell": 0.0, "flow": 0.0, "swirl": 0.0,
        "pulse": 0.0, "pulseRate": 1.0, "ring": 0.0, "jitter": 0.0,
        "shake": 0.0, "alpha": 0.45, "rest": 0.0,
        "from_rgb": (100, 116, 139), "to_rgb": (71, 85, 105),
    },
}


class SphereGeometry:
    """Precomputed 3D sphere points using Fibonacci golden angle spiral."""

    def __init__(self, count: int = PARTICLE_COUNT):
        self.count = count
        i = np.arange(count, dtype=np.float32)
        self.y = 1.0 - (i / max(1.0, count - 1.0)) * 2.0
        self.radius_at_y = np.sqrt(np.maximum(0.0, 1.0 - self.y * self.y))
        theta = GOLDEN_ANGLE * i
        self.x = np.cos(theta) * self.radius_at_y
        self.z = np.sin(theta) * self.radius_at_y
        self.ring_frac = (i * 0.61803398875) % 1.0
        self.seed = ((i * 0.7548776662) % 1.0) * TWO_PI
        self.tone = (i * 0.5436890126) % 1.0


SPHERE = SphereGeometry()


class Orb:
    """
    Transparent floating desktop assistant overlay rendering the exact Particles Orb
    animated component from the web frontend in real time on Windows.
    """

    def __init__(self, size: int = 140) -> None:
        if sys.platform != "win32":
            raise RuntimeError("The desktop orb requires Windows.")
        self.size = size
        self._events: queue.Queue[tuple[str, str, object]] = queue.Queue()
        self.ready = threading.Event()
        self.error: BaseException | None = None
        self._click_handler: Optional[Callable[[], None]] = None
        self._thread = threading.Thread(target=self._run, name="jarvis-particles-orb", daemon=True)
        self._thread.start()

    def set_state(self, state: str, message: str = "") -> None:
        self._events.put(("state", state, message))

    def set_level(self, level: float) -> None:
        self._events.put(("level", "", max(0.0, min(1.0, float(level)))))

    def set_click_handler(self, handler: Callable[[], None]) -> None:
        self._click_handler = handler

    def close(self) -> None:
        self._events.put(("__close__", "", None))

    def _run(self) -> None:
        try:
            self._run_tk()
        except BaseException as error:
            self.error = error
            print(f"JARVIS Particles Orb failed to initialize: {error}", flush=True)
            traceback.print_exc()
            self.ready.set()

    def _run_tk(self) -> None:
        import tkinter as tk

        root = tk.Tk()
        root.title("JARVIS Assistant")
        root.overrideredirect(True)
        root.attributes("-topmost", True)

        # Transparent background color key: #010101 is 100% transparent on Windows
        TRANS_BG = "#010101"
        try:
            root.attributes("-transparentcolor", TRANS_BG)
        except tk.TclError:
            root.attributes("-alpha", 0.95)

        # Enable non-activating toolwindow style so it doesn't steal focus from active apps
        try:
            import ctypes
            hwnd = root.winfo_id()
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, -20)
            user32.SetWindowLongW(hwnd, -20, style | 0x00000080 | 0x08000000)  # WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
        except Exception:
            pass

        orb_size = self.size
        win_w = orb_size + 180
        win_h = orb_size + 10
        root.geometry(f"{win_w}x{win_h}+40+40")

        canvas = tk.Canvas(root, bg=TRANS_BG, highlightthickness=0, width=win_w, height=win_h)
        canvas.pack(fill="both", expand=True)

        # Window dragging state
        drag_data = {"x": 0, "y": 0, "dragging": False}

        def on_mouse_down(event):
            drag_data["x"] = event.x_root - root.winfo_x()
            drag_data["y"] = event.y_root - root.winfo_y()
            drag_data["dragging"] = False

        def on_mouse_drag(event):
            drag_data["dragging"] = True
            new_x = event.x_root - drag_data["x"]
            new_y = event.y_root - drag_data["y"]
            root.geometry(f"+{new_x}+{new_y}")

        def on_mouse_up(event):
            if not drag_data["dragging"]:
                if self._click_handler:
                    self._click_handler()

        canvas.bind("<ButtonPress-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)

        # Labels for JARVIS status and subtitle
        lbl_x = orb_size + 10
        label_title = canvas.create_text(
            lbl_x, orb_size // 2 - 12, anchor="w",
            fill="#E2E8F0", text="JARVIS", font=("Segoe UI", 12, "bold")
        )
        label_detail = canvas.create_text(
            lbl_x, orb_size // 2 + 10, anchor="w",
            fill="#94A3B8", text="Ready", font=("Segoe UI", 9)
        )

        image_item = canvas.create_image(0, 0, anchor="nw")

        self.ready.set()
        root.lift()

        # Animation states
        current_state = "idle"
        display_message = "Ready"
        mic_level = 0.0
        smoothed_level = 0.0
        phase = 0.0
        clock = 0.0
        pulse_clock = 0.0
        angle_y = 0.0
        ring_phase = 0.0
        last_time = time.perf_counter()

        # Canvas image holder
        photo_ref = [None]

        def render_frame():
            nonlocal current_state, display_message, mic_level, smoothed_level
            nonlocal phase, clock, pulse_clock, angle_y, ring_phase, last_time

            now = time.perf_counter()
            dt = min(0.1, max(0.001, now - last_time))
            last_time = now

            # Poll incoming state events
            try:
                while True:
                    evt, val, payload = self._events.get_nowait()
                    if evt == "__close__":
                        root.destroy()
                        return
                    if evt == "state":
                        current_state = val
                        if payload:
                            display_message = str(payload)
                    elif evt == "level":
                        mic_level = float(payload)
            except queue.Empty:
                pass

            params = STATE_PARAMS.get(current_state, STATE_PARAMS["idle"])

            # Smooth audio level reactivity
            target_level = mic_level if current_state == "listening" else params["rest"]
            smoothed_level += (target_level - smoothed_level) * min(1.0, 14.0 * dt)

            # Time progression
            speed = 1.0
            d_phase = dt * speed
            phase += d_phase
            clock += d_phase * params["tempo"]
            pulse_clock += d_phase * params["tempo"] * params["pulseRate"]
            angle_y += d_phase * params["spin"] * (1.0 + params["ripple"] * smoothed_level * 1.8)
            ring_phase = (ring_phase + d_phase * 0.7) % TWO_PI

            t = clock + TIME_OFFSET
            pt = pulse_clock + TIME_OFFSET

            # Core particle math (vectorized with numpy for 60+ FPS)
            center = orb_size / 2.0
            base_radius = center * 0.62

            beat = math.sin(pt * 2.6) * 0.5 + 0.5
            beat_sharp = beat * beat * beat
            breathe = params["breathe"] * math.sin(t * 1.1)
            conv = params["pulse"] * (0.06 + 0.12 * beat_sharp)
            radius = base_radius * (1.0 + breathe + smoothed_level * params["swell"] - conv)

            shake_amp = params["shake"] * radius * 0.05
            shake_x = shake_amp * (math.sin(t * 26.0) + 0.5 * math.sin(t * 15.7))
            shake_y = shake_amp * (math.cos(t * 22.5) + 0.5 * math.sin(t * 13.1))

            drift_amp = params["drift"] * radius * 0.055
            jitter_amp = params["jitter"] * radius * (0.012 + smoothed_level * 0.07)
            ripple_amp = params["ripple"] * (0.04 + smoothed_level * 0.22)
            pulse_amp = params["pulse"] * 0.16 * (0.4 + 0.6 * beat)
            flow_amp = params["flow"] * (0.18 + smoothed_level * 0.40)
            swirl_amp = params["swirl"] * (0.35 + smoothed_level * 0.90)
            ring_w = params["ring"]
            ring_breath = 1.0 + params["pulse"] * 0.4 * math.sin(pt * 2.6)

            cos_x = math.cos(ANGLE_X)
            sin_x = math.sin(ANGLE_X)

            # Rotation and twists
            if swirl_amp > 0.002:
                twist = angle_y + swirl_amp * np.sin(SPHERE.y * 2.4 + t * 1.6)
            else:
                twist = np.full(PARTICLE_COUNT, angle_y, dtype=np.float32)

            cy = np.cos(twist)
            sny = np.sin(twist)

            x1 = SPHERE.x * cy - SPHERE.z * sny
            z1 = SPHERE.x * sny + SPHERE.z * cy
            y1 = SPHERE.y * cos_x - z1 * sin_x
            z2 = SPHERE.y * sin_x + z1 * cos_x

            depth = (z2 + 1.0) / 2.0
            perspective = 0.65 + depth * 0.45

            point_radius = np.full(PARTICLE_COUNT, radius, dtype=np.float32)
            if ripple_amp > 0.002:
                point_radius *= 1.0 + ripple_amp * (0.5 + 0.5 * np.sin(SPHERE.y * 4.5 - t * 6.5))
            if pulse_amp > 0.002:
                point_radius *= 1.0 - pulse_amp * (0.5 + 0.5 * np.sin(SPHERE.ring_frac * TWO_PI + pt * 3.1))
            if flow_amp > 0.002:
                stream = 0.5 + 0.5 * np.sin(SPHERE.seed * 3.0 - t * 3.4)
                point_radius *= 1.0 - flow_amp * stream * stream

            ox = np.full(PARTICLE_COUNT, shake_x, dtype=np.float32)
            oy = np.full(PARTICLE_COUNT, shake_y, dtype=np.float32)
            if drift_amp > 0.01:
                ox += drift_amp * (np.sin(t * 0.55 + SPHERE.seed * 3.7) + 0.5 * np.sin(t * 1.3 + SPHERE.seed * 1.3))
                oy += drift_amp * (np.cos(t * 0.62 + SPHERE.seed * 2.9) + 0.5 * np.sin(t * 1.05 + SPHERE.seed * 5.1))
            if jitter_amp > 0.01:
                ox += jitter_amp * np.sin(t * 14.0 + SPHERE.seed * 9.3)
                oy += jitter_amp * np.cos(t * 17.0 + SPHERE.seed * 6.1)

            screen_x = center + x1 * point_radius * perspective + ox
            screen_y = center + y1 * point_radius * perspective + oy
            dot = 0.6 + depth * 1.6

            if ring_w > 0.004:
                ring_angle = (np.arange(PARTICLE_COUNT) / PARTICLE_COUNT) * TWO_PI + ring_phase + 0.05 * np.sin(t * 1.3 + SPHERE.seed)
                ring_r = center * (0.58 + 0.13 * SPHERE.ring_frac) * (1.0 + 0.05 * np.sin(t + SPHERE.seed * 1.7)) * ring_breath
                circle_x = center + np.cos(ring_angle) * ring_r
                circle_y = center + np.sin(ring_angle) * ring_r
                screen_x += (circle_x - screen_x) * ring_w
                screen_y += (circle_y - screen_y) * ring_w

            # Render to PIL Image on transparent key background
            img = Image.new("RGB", (orb_size, orb_size), (1, 1, 1))
            draw = ImageDraw.Draw(img)

            # Color interpolation across depth and state
            from_col = params["from_rgb"]
            to_col = params["to_rgb"]

            # Sort indices by depth for painter's algorithm
            sort_order = np.argsort(depth)
            for idx in sort_order:
                sx = float(screen_x[idx])
                sy = float(screen_y[idx])
                r = float(dot[idx])
                if r <= 0.2 or sx < -5 or sx > orb_size + 5 or sy < -5 or sy > orb_size + 5:
                    continue

                d_val = float(depth[idx])
                # Interpolate color between from_rgb and to_rgb with tone
                tone = float(SPHERE.tone[idx])
                t_mix = 0.5 * (d_val + tone)
                cr = int(from_col[0] + (to_col[0] - from_col[0]) * t_mix)
                cg = int(from_col[1] + (to_col[1] - from_col[1]) * t_mix)
                cb = int(from_col[2] + (to_col[2] - from_col[2]) * t_mix)

                # Scale intensity with depth to simulate opacity
                alpha = 0.35 + d_val * 0.65
                cr = max(2, min(255, int(cr * alpha)))
                cg = max(2, min(255, int(cg * alpha)))
                cb = max(2, min(255, int(cb * alpha)))

                draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(cr, cg, cb))

            # Put image on Tkinter canvas
            photo = ImageTk.PhotoImage(img)
            photo_ref[0] = photo
            canvas.itemconfig(image_item, image=photo)

            # Update status text
            state_text = current_state.capitalize()
            canvas.itemconfig(label_title, text=f"JARVIS · {state_text}")
            detail = display_message[:30] if display_message else "Ready"
            canvas.itemconfig(label_detail, text=detail)

            root.after(30, render_frame)

        root.after(50, render_frame)
        root.mainloop()
