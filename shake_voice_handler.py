# shake_voice_handler.py
import math, json, os
from kivy.clock import Clock
from kivy.utils import platform
from plyer import notification
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

# GPS (cross-platform)
if platform in ("android", "ios"):
    from plyer import gps
else:
    gps = None

# Android SMS
if platform == "android":
    from jnius import autoclass

# Voice recognition
import pyaudio
from vosk import Model, KaldiRecognizer

# Accelerometer (mobile only)
if platform in ("android", "ios"):
    from plyer import accelerometer
else:
    accelerometer = None


class ShakeVoiceHandler:
    """
    Detects shake or voice activation and triggers a countdown SOS
    (like the one-tap emergency button) automatically.
    """

    def __init__(self, app, button_settings):
        self.app = app
        self.settings = button_settings

        # --- Shake ---
        self.last_x = self.last_y = self.last_z = None
        self.shake_threshold = 10.0
        self._shake_event = None
        self._shake_count = 0
        self._required_consecutive = 2
        self.is_monitoring = False

        # --- Voice ---
        self.is_listening = False
        self._voice_event = None
        self.vosk_initialized = False
        self.p = None
        self.stream = None
        self.rec = None

        # --- GPS ---
        self.current_location = {"lat": None, "lon": None}
        self._gps_started = False
        self.start_gps()

        # Countdown popup
        self.countdown_popup = None
        self.remaining_time = 5
        self.countdown_event = None

        # Initialize Vosk if enabled
        if self.settings.get("voice_enabled", False):
            self.init_vosk()

    # ---------------- GPS ----------------
    def start_gps(self):
        if gps:
            try:
                gps.configure(on_location=self.on_location_update)
                gps.start(minTime=1000, minDistance=0)
                self._gps_started = True
            except Exception:
                self.current_location["lat"], self.current_location["lon"] = 14.5995, 120.9842
        else:
            self.current_location["lat"], self.current_location["lon"] = 14.5995, 120.9842

    def on_location_update(self, **kwargs):
        self.current_location["lat"] = kwargs.get("lat")
        self.current_location["lon"] = kwargs.get("lon")

    def get_location(self):
        return self.current_location

    # ---------------- SHAKE ----------------
    def start_shake_monitoring(self):
        if not accelerometer:
            print("Shake detection not supported on this platform")
            return

        try:
            accelerometer.enable()
        except Exception:
            pass

        s = int(self.settings.get("shake_sensitivity", 5))
        self.shake_threshold = max(2.0, 15.0 - (s * 1.2))
        self.last_x = self.last_y = self.last_z = None
        self._shake_count = 0
        self.is_monitoring = True

        if self._shake_event:
            self._shake_event.cancel()
        self._shake_event = Clock.schedule_interval(self.check_shake, 0.1)

    def stop_shake_monitoring(self):
        self.is_monitoring = False
        if self._shake_event:
            try:
                self._shake_event.cancel()
            except Exception:
                pass
        if accelerometer:
            try:
                accelerometer.disable()
            except Exception:
                pass

    def check_shake(self, dt):
        if not self.is_monitoring or not accelerometer:
            return

        try:
            val = accelerometer.acceleration
            if not val or any(v is None for v in val[:3]):
                return
            x, y, z = val[:3]
            if self.last_x is None:
                self.last_x, self.last_y, self.last_z = x, y, z
                return

            dx, dy, dz = x - self.last_x, y - self.last_y, z - self.last_z
            total = math.sqrt(dx*dx + dy*dy + dz*dz)
            if total > self.shake_threshold:
                self._shake_count += 1
                if self._shake_count >= self._required_consecutive:
                    self.on_trigger_detected("Shake")
                    self._shake_count = 0
            else:
                self._shake_count = 0

            self.last_x, self.last_y, self.last_z = x, y, z

        except Exception as e:
            print("Shake error:", e)

    # ---------------- VOSK VOICE ----------------
    def init_vosk(self):
        model_path = "model"
        if not os.path.exists(model_path):
            print("Vosk model missing!")
            return

        self.vosk_initialized = True
        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, 16000)
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16, channels=1, rate=16000,
            input=True, frames_per_buffer=8192
        )
        self.stream.start_stream()
        self.is_listening = True
        self._voice_event = Clock.schedule_interval(self.check_voice, 0.5)

    def check_voice(self, dt):
        if not self.is_listening:
            return

        try:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                text = result.get("text", "").lower()
                phrase = self.settings.get("voice_phrase", "help").lower()
                if phrase in text:
                    self.on_trigger_detected("Voice")
        except Exception as e:
            print("Voice recognition error:", e)

    def stop_voice_listening(self):
        self.is_listening = False
        if self._voice_event:
            try:
                self._voice_event.cancel()
            except Exception:
                pass

    # ---------------- TRIGGER ----------------
    def on_trigger_detected(self, trigger):
        print(f"{trigger} detected! Starting SOS countdown...")
        self.show_countdown_popup(trigger)

    # ---------------- COUNTDOWN ----------------
    def show_countdown_popup(self, trigger):
        # Prevent multiple popups
        if self.countdown_popup:
            return

        self.remaining_time = 5
        layout = BoxLayout(orientation="vertical", spacing=10)
        self.countdown_label = Label(text=f"Sending {trigger} alert in {self.remaining_time} sec")
        layout.add_widget(self.countdown_label)
        cancel_btn = Button(text="Cancel", size_hint_y=None, height=40)
        cancel_btn.bind(on_release=self.cancel_countdown)
        layout.add_widget(cancel_btn)

        self.countdown_popup = Popup(title=f"{trigger} SOS Countdown",
                                     content=layout,
                                     size_hint=(0.8,0.4))
        self.countdown_popup.open()
        self.countdown_event = Clock.schedule_interval(lambda dt: self._countdown_tick(trigger), 1)

    def _countdown_tick(self, trigger):
        self.remaining_time -= 1
        if self.countdown_label:
            self.countdown_label.text = f"Sending {trigger} alert in {self.remaining_time} sec"
        if self.remaining_time <= 0:
            self.cancel_countdown()
            self.send_alert(trigger)
        return True

    def cancel_countdown(self, *args):
        if self.countdown_event:
            Clock.unschedule(self.countdown_event)
        if self.countdown_popup:
            self.countdown_popup.dismiss()
            self.countdown_popup = None
        print("SOS countdown cancelled.")

    # ---------------- ALERT ----------------
    def send_alert(self, trigger="Unknown"):
        """Trigger MainScreen report_all() like one-tap SOS."""
        try:
            main_screen = self.app.root.get_screen("main")
            main_screen.current_category = trigger
            main_screen.report_all()
        except Exception as e:
            print("Failed to trigger SOS:", e)

        # Desktop/mobile notification
        if notification:
            try:
                notification.notify(title="Emergency Alert",
                                    message=f"{trigger} triggered emergency!",
                                    timeout=3)
            except Exception:
                pass

    # ---------------- SETTINGS ----------------
    def update_settings(self, settings):
        self.settings = settings

        if self.settings.get("shake_enabled", False):
            self.start_shake_monitoring()
        else:
            self.stop_shake_monitoring()

        if self.settings.get("voice_enabled", False):
            if not self.vosk_initialized:
                self.init_vosk()
            self.is_listening = True
        else:
            self.stop_voice_listening()
