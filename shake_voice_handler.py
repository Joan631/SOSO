"""
Improved Shake & Voice Handler
- More robust shake detection (debounce, first-sample handling)
- Stores Clock events for safe cancel
- Debug prints included
- Keeps original voice/gps structure but warns about plyer availability
"""

from kivy.clock import Clock
from kivy.utils import platform
import math
import time

# Try to import platform-specific libraries
try:
    from plyer import accelerometer, stt, gps
    from plyer import notification
    PLYER_AVAILABLE = True
except Exception:
    PLYER_AVAILABLE = False
    accelerometer = None
    stt = None
    gps = None
    notification = None
    print("Warning: plyer not available. Install with: pip install plyer")

if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        ANDROID_PERMISSIONS = True
    except Exception:
        ANDROID_PERMISSIONS = False
        print("Warning: Android permissions not available")


class ShakeVoiceHandler:
    def __init__(self, app_instance, button_settings):
        self.app = app_instance
        self.settings = button_settings

        # last accelerometer values (None means not initialized)
        self.last_x = None
        self.last_y = None
        self.last_z = None

        # threshold and debounce
        self.shake_threshold = 10.0
        self._shake_event = None
        self._shake_count = 0
        self._required_consecutive = 2  # require 2 consecutive readings above threshold

        # monitoring flags
        self.is_monitoring = False

        # voice
        self.is_listening = False
        self._voice_event = None

        # gps
        self.current_location = None
        self._gps_started = False

        # Request permissions on Android if available
        if platform == 'android' and ANDROID_PERMISSIONS:
            self.request_android_permissions()

    def request_android_permissions(self):
        permissions = [
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.RECORD_AUDIO,
            Permission.SEND_SMS
        ]
        request_permissions(permissions)

    # ----------------- SHAKE -----------------
    def start_shake_monitoring(self):
        if not PLYER_AVAILABLE or accelerometer is None:
            print("Cannot start shake monitoring: plyer accelerometer not available on this platform.")
            return False

        if not self.settings.get("shake_enabled", False):
            print("Shake disabled in settings.")
            return False

        try:
            accelerometer.enable()
        except Exception as e:
            print("accelerometer.enable() failed:", e)
            # continue; some plyer backends enable implicitly

        # Map sensitivity (1..10) -> threshold (higher sensitivity => smaller threshold)
        s = int(self.settings.get("shake_sensitivity", 5))
        # Example mapping: sensitivity 10 -> threshold 4.0 (easier), sensitivity 1 -> threshold 14.0 (harder)
        self.shake_threshold = max(2.0, 15.0 - (s * 1.2))
        print(f"[Shake] sensitivity={s} -> threshold={self.shake_threshold:.2f}")

        # Reset last-known values so we initialize on first real reading
        self.last_x = None
        self.last_y = None
        self.last_z = None
        self._shake_count = 0

        # schedule with stored event so we can cancel reliably
        if self._shake_event:
            try:
                self._shake_event.cancel()
            except Exception:
                pass

        self.is_monitoring = True
        self._shake_event = Clock.schedule_interval(self.check_shake, 0.1)
        print("Shake monitoring started.")
        return True

    def stop_shake_monitoring(self):
        self.is_monitoring = False
        if self._shake_event:
            try:
                self._shake_event.cancel()
            except Exception as e:
                print("Error cancelling shake event:", e)
            self._shake_event = None
        try:
            if accelerometer:
                accelerometer.disable()
        except Exception:
            pass
        print("Shake monitoring stopped.")

    def check_shake(self, dt):
        if not self.is_monitoring:
            return

        try:
            if not accelerometer:
                return

            val = accelerometer.acceleration
            # plyer sometimes returns None or a tuple with None elements
            if not val or any(v is None for v in val[:3]):
                # Debug prints can help:
                # print("Accel read returned None or partial None:", val)
                return

            x, y, z = val[:3]

            # initialize last values on first valid sample
            if self.last_x is None:
                self.last_x, self.last_y, self.last_z = x, y, z
                # don't evaluate on the first sample
                return

            # compute deltas
            dx = x - self.last_x
            dy = y - self.last_y
            dz = z - self.last_z

            total_delta = math.sqrt(dx * dx + dy * dy + dz * dz)

            # Debug
            # print(f"[Accel] dx={dx:.2f} dy={dy:.2f} dz={dz:.2f} total={total_delta:.2f}")

            if total_delta > self.shake_threshold:
                self._shake_count += 1
                # if enough consecutive high deltas, consider it a shake
                if self._shake_count >= self._required_consecutive:
                    print(f"SHAKE DETECTED! total_delta={total_delta:.2f} count={self._shake_count}")
                    self.on_shake_detected()
                    # reset counter
                    self._shake_count = 0
            else:
                # decay counter if value below threshold
                self._shake_count = 0

            # update last values
            self.last_x, self.last_y, self.last_z = x, y, z

        except Exception as e:
            print("Error checking shake:", e)

    def on_shake_detected(self):
        # Prevent immediate retriggering
        self.is_monitoring = False
        # immediate action
        self.send_emergency_alert("Shake activation detected")
        if notification:
            try:
                notification.notify(title="Emergency Alert", message="Shake activation detected", timeout=3)
            except Exception:
                pass
        # cooldown then resume
        Clock.schedule_once(lambda dt: self._resume_shake_after_cooldown(), 3)

    def _resume_shake_after_cooldown(self):
        # re-enable monitoring if still enabled in settings
        if self.settings.get("shake_enabled", False):
            self.is_monitoring = True

    # ----------------- VOICE -----------------
    def start_voice_listening(self):
        if not PLYER_AVAILABLE or stt is None:
            print("Voice (stt) not available on this platform.")
            return False

        if not self.settings.get("voice_enabled", False):
            print("Voice disabled in settings.")
            return False

        # Reset and schedule
        self.is_listening = True
        if self._voice_event:
            try:
                self._voice_event.cancel()
            except Exception:
                pass
        self._voice_event = Clock.schedule_interval(self.check_voice, 2.0)
        print("Voice listening started.")
        return True

    def stop_voice_listening(self):
        self.is_listening = False
        if self._voice_event:
            try:
                self._voice_event.cancel()
            except Exception:
                pass
            self._voice_event = None
        print("Voice listening stopped.")

    def check_voice(self, dt):
        if not self.is_listening or stt is None:
            return
        try:
            # note: plyer.stt implementations vary — this is best-effort
            stt.start()
            # process results shortly after (some backends are synchronous)
            Clock.schedule_once(self.process_voice_result, 1.5)
        except Exception as e:
            print("Error starting stt:", e)

    def process_voice_result(self, dt):
        try:
            results = []
            try:
                results = stt.results() or []
            except Exception:
                # Some plyer stt implementations may provide text differently
                # Try stt.get_text() or stt.text if available
                if hasattr(stt, "get_text"):
                    try:
                        results = [stt.get_text()]
                    except Exception:
                        results = []
                elif hasattr(stt, "text"):
                    try:
                        results = [stt.text]
                    except Exception:
                        results = []

            if results:
                recognized_text = results[0].lower()
                activation_phrase = self.settings.get("voice_phrase", "").lower()
                print(f"[STT] recognized: '{recognized_text}' looking for '{activation_phrase}'")
                if activation_phrase and activation_phrase in recognized_text:
                    print("VOICE ACTIVATION DETECTED!")
                    self.on_voice_activated()

            # stop if supported
            try:
                stt.stop()
            except Exception:
                pass

        except Exception as e:
            print("Error processing voice result:", e)

    def on_voice_activated(self):
        self.is_listening = False
        self.send_emergency_alert("Voice activation detected")
        if notification:
            try:
                notification.notify(title="Voice Detected", message="Emergency alert sent", timeout=3)
            except Exception:
                pass
        Clock.schedule_once(lambda dt: self._resume_voice_after_cooldown(), 5)

    def _resume_voice_after_cooldown(self):
        if self.settings.get("voice_enabled", False):
            self.is_listening = True

    # ----------------- GPS & EMERGENCY -----------------
    def start_location_tracking(self):
        if not PLYER_AVAILABLE or gps is None:
            print("GPS not available on this platform.")
            return False
        try:
            if not self._gps_started:
                gps.configure(on_location=self.on_location_update)
                gps.start(minTime=1000, minDistance=0)
                self._gps_started = True
            print("GPS started.")
            return True
        except Exception as e:
            print("Error starting GPS:", e)
            return False

    def stop_location_tracking(self):
        if gps and self._gps_started:
            try:
                gps.stop()
            except Exception:
                pass
            self._gps_started = False

    def on_location_update(self, **kwargs):
        self.current_location = {
            'lat': kwargs.get('lat'),
            'lon': kwargs.get('lon'),
            'accuracy': kwargs.get('accuracy')
        }
        print("Location update:", self.current_location)

    def get_current_location(self):
        if self.current_location:
            return self.current_location
        # try to start gps briefly (non-blocking)
        try:
            self.start_location_tracking()
            # allow some time for update; in a real app use event-driven approach
            time.sleep(2)
        except Exception:
            pass
        return self.current_location

    def send_emergency_alert(self, trigger_method):
        location = self.get_current_location()
        if location and location.get('lat') and location.get('lon'):
            lat, lon = location['lat'], location['lon']
            message = f"EMERGENCY: {trigger_method} at {lat},{lon}"
        else:
            message = f"EMERGENCY: {trigger_method} (location unknown)"
        print("=== EMERGENCY ===")
        print(message)
        # send to contacts (app-dependent)
        self.send_to_emergency_contacts(message)
        return message

    def send_to_emergency_contacts(self, message):
        try:
            contacts = getattr(self.app, "emergency_contacts", []) or []
            for c in contacts:
                phone = c.get("phone")
                if phone:
                    self.send_sms(phone, message)
        except Exception as e:
            print("Error sending to contacts:", e)

    def send_sms(self, phone_number, message):
        if platform == 'android':
            try:
                from jnius import autoclass
                SmsManager = autoclass('android.telephony.SmsManager')
                sms = SmsManager.getDefault()
                sms.sendTextMessage(phone_number, None, message, None, None)
                print("SMS sent to", phone_number)
                return True
            except Exception as e:
                print("SMS error:", e)
                return False
        else:
            print(f"SMS not supported on {platform}. Would send to {phone_number}: {message}")
            return False

    # control helpers
    def start_all_monitoring(self):
        started = []
        if self.settings.get("shake_enabled", False):
            if self.start_shake_monitoring():
                started.append("shake")
        if self.settings.get("voice_enabled", False):
            if self.start_voice_listening():
                started.append("voice")
        self.start_location_tracking()
        return started

    def stop_all_monitoring(self):
        self.stop_shake_monitoring()
        self.stop_voice_listening()
        self.stop_location_tracking()

    def update_settings(self, new_settings):
        self.settings = new_settings
        # restart monitors
        self.stop_all_monitoring()
        self.start_all_monitoring()

from plyer import accelerometer
print("accelerometer attr:", hasattr(accelerometer, "acceleration"))
