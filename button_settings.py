# button_settings.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.app import App

from shake_voice_handler import ShakeVoiceHandler
import floating_button   # Floating button module

# Global button settings
BUTTON_SETTINGS = {
    "shake_enabled": False,
    "shake_sensitivity": 5,
    "voice_enabled": False,
    "voice_phrase": "help me",
    "voice_sensitivity": 5,
    "tap_enabled": True,
    "tap_count": 1,
    "floating_enabled": True,
    "button_size": 50,
    "lock_screen": False,
    "countdown_enabled": True,
    "countdown_seconds": 5
}


class ButtonSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

        # Scrollable layout
        scroll = ScrollView()
        layout = BoxLayout(orientation="vertical", spacing=20, padding=20, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        scroll.add_widget(layout)
        self.add_widget(scroll)

        # --- Activation Methods ---
        layout.add_widget(Label(text="Activation Methods", font_size=22, bold=True))

        # Shake Activation
        shake_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        shake_chk_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=35)
        shake_chk_box.add_widget(Label(text="Shake Activation"))
        self.shake_chk = CheckBox(active=BUTTON_SETTINGS["shake_enabled"])
        self.shake_chk.bind(active=self.toggle_shake_settings)
        shake_chk_box.add_widget(self.shake_chk)
        shake_box.add_widget(shake_chk_box)

        self.shake_settings_box = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None)
        self.shake_settings_box.add_widget(Label(text="Shake Sensitivity"))
        self.shake_slider = Slider(min=1, max=10, value=BUTTON_SETTINGS["shake_sensitivity"], step=1,
                                   size_hint_y=None, height=50)
        self.shake_slider.bind(value=self.update_shake_sensitivity)
        self.shake_settings_box.add_widget(self.shake_slider)
        shake_box.add_widget(self.shake_settings_box)
        layout.add_widget(shake_box)

        # Voice Activation
        voice_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        voice_chk_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=35)
        voice_chk_box.add_widget(Label(text="Voice Activation"))
        self.voice_chk = CheckBox(active=BUTTON_SETTINGS["voice_enabled"])
        self.voice_chk.bind(active=self.toggle_voice_settings)
        voice_chk_box.add_widget(self.voice_chk)
        voice_box.add_widget(voice_chk_box)

        self.voice_settings_box = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None)
        self.voice_settings_box.add_widget(Label(text="Activation Phrase"))
        self.voice_input = TextInput(text=BUTTON_SETTINGS["voice_phrase"], multiline=False, size_hint_y=None,
                                     height=45)
        self.voice_input.bind(text=self.update_voice_phrase)
        self.voice_settings_box.add_widget(self.voice_input)
        self.voice_settings_box.add_widget(Label(text="Voice Sensitivity"))
        self.voice_slider = Slider(min=1, max=10, value=BUTTON_SETTINGS["voice_sensitivity"], step=1,
                                   size_hint_y=None, height=50)
        self.voice_slider.bind(value=self.update_voice_sensitivity)
        self.voice_settings_box.add_widget(self.voice_slider)
        voice_box.add_widget(self.voice_settings_box)
        layout.add_widget(voice_box)

        # Tap Activation
        tap_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        tap_chk_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=35)
        tap_chk_box.add_widget(Label(text="Tap Activation"))
        self.tap_chk = CheckBox(active=BUTTON_SETTINGS["tap_enabled"])
        self.tap_chk.bind(active=self.toggle_tap_settings)
        tap_chk_box.add_widget(self.tap_chk)
        tap_box.add_widget(tap_chk_box)

        self.tap_settings_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=45)
        self.tap_settings_box.add_widget(Label(text="Number of Taps"))
        self.tap_count_input = TextInput(text=str(BUTTON_SETTINGS["tap_count"]), multiline=False,
                                         size_hint_y=None, height=45)
        tap_box.add_widget(self.tap_settings_box)
        self.tap_settings_box.add_widget(self.tap_count_input)
        layout.add_widget(tap_box)

        # --- Button Customization ---
        layout.add_widget(Label(text="Button Customization", font_size=22, bold=True))
        customize_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)

        # Floating Button
        float_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=35)
        float_box.add_widget(Label(text="Floating Button Enabled"))
        self.floating_chk = CheckBox(active=BUTTON_SETTINGS["floating_enabled"])
        self.floating_chk.bind(active=self.toggle_floating_settings)
        float_box.add_widget(self.floating_chk)
        customize_box.add_widget(float_box)

        self.floating_size_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=45)
        self.floating_size_box.add_widget(Label(text="Button Size (1-100)"))
        self.size_input = TextInput(text=str(BUTTON_SETTINGS["button_size"]), multiline=False, size_hint_y=None,
                                    height=45)
        self.size_input.bind(text=self.update_floating_size)
        self.floating_size_box.add_widget(self.size_input)
        customize_box.add_widget(self.floating_size_box)

        # Lock Screen
        lock_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=35)
        lock_box.add_widget(Label(text="Lock Screen Activation"))
        self.lock_chk = CheckBox(active=BUTTON_SETTINGS["lock_screen"])
        lock_box.add_widget(self.lock_chk)
        customize_box.add_widget(lock_box)
        layout.add_widget(customize_box)

        # --- Security / Countdown ---
        layout.add_widget(Label(text="Security / Countdown", font_size=22, bold=True))
        security_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)

        # Enable Countdown
        countdown_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=35)
        countdown_box.add_widget(Label(text="Enable Countdown"))
        self.countdown_chk = CheckBox(active=BUTTON_SETTINGS["countdown_enabled"])
        self.countdown_chk.bind(active=self.toggle_countdown_settings)
        countdown_box.add_widget(self.countdown_chk)
        security_box.add_widget(countdown_box)

        # Countdown seconds
        self.countdown_input_box = BoxLayout(orientation="horizontal", spacing=12, size_hint_y=None, height=45)
        self.countdown_input_box.add_widget(Label(text="Countdown Seconds"))
        self.countdown_input = TextInput(text=str(BUTTON_SETTINGS["countdown_seconds"]), multiline=False,
                                         size_hint_y=None, height=45)
        self.countdown_input_box.add_widget(self.countdown_input)
        security_box.add_widget(self.countdown_input_box)
        layout.add_widget(security_box)

        # --- Save Button ---
        save_btn = Button(text="Save Settings", size_hint_y=None, height=55)
        save_btn.bind(on_release=self.save_settings)
        layout.add_widget(save_btn)

# Initialize handler first
        if not hasattr(self.app, "shake_voice_handler"):
            self.app.shake_voice_handler = ShakeVoiceHandler(self.app, BUTTON_SETTINGS)

        # Then toggle hidden sections
        self.toggle_shake_settings(self.shake_chk, self.shake_chk.active)
        self.toggle_voice_settings(self.voice_chk, self.voice_chk.active)
        self.toggle_tap_settings(self.tap_chk, self.tap_chk.active)
        self.toggle_floating_settings(self.floating_chk, self.floating_chk.active)
        self.toggle_countdown_settings(self.countdown_chk, self.countdown_chk.active)

        # Initialize floating button
        if BUTTON_SETTINGS["floating_enabled"]:
            floating_button.enable_floating(BUTTON_SETTINGS["button_size"])
        else:
            floating_button.disable_floating()

    # ---------------- Toggle / Live Update Functions ----------------
    def toggle_shake_settings(self, instance, value):
        self.shake_settings_box.height = self.shake_settings_box.minimum_height if value else 0
        self.shake_settings_box.opacity = 1 if value else 0
        self.shake_settings_box.disabled = not value

        BUTTON_SETTINGS["shake_enabled"] = value
        if self.app.shake_voice_handler:
            self.app.shake_voice_handler.update_settings({
                **BUTTON_SETTINGS,
                "shake_enabled": value,
                "shake_sensitivity": int(self.shake_slider.value)
            })

    def update_shake_sensitivity(self, instance, value):
        BUTTON_SETTINGS["shake_sensitivity"] = int(value)
        if self.app.shake_voice_handler and BUTTON_SETTINGS["shake_enabled"]:
            self.app.shake_voice_handler.update_settings(BUTTON_SETTINGS)

    def toggle_voice_settings(self, instance, value):
        self.voice_settings_box.height = self.voice_settings_box.minimum_height if value else 0
        self.voice_settings_box.opacity = 1 if value else 0
        self.voice_settings_box.disabled = not value

        BUTTON_SETTINGS["voice_enabled"] = value
        if self.app.shake_voice_handler:
            self.app.shake_voice_handler.update_settings({
                **BUTTON_SETTINGS,
                "voice_enabled": value,
                "voice_phrase": self.voice_input.text,
                "voice_sensitivity": int(self.voice_slider.value)
            })

    def update_voice_phrase(self, instance, value):
        BUTTON_SETTINGS["voice_phrase"] = value
        if self.app.shake_voice_handler and BUTTON_SETTINGS["voice_enabled"]:
            self.app.shake_voice_handler.update_settings(BUTTON_SETTINGS)

    def update_voice_sensitivity(self, instance, value):
        BUTTON_SETTINGS["voice_sensitivity"] = int(value)
        if self.app.shake_voice_handler and BUTTON_SETTINGS["voice_enabled"]:
            self.app.shake_voice_handler.update_settings(BUTTON_SETTINGS)

    def toggle_tap_settings(self, instance, value):
        self.tap_settings_box.height = 45 if value else 0
        self.tap_settings_box.opacity = 1 if value else 0
        self.tap_settings_box.disabled = not value
        BUTTON_SETTINGS["tap_enabled"] = value

    def toggle_floating_settings(self, instance, value):
        self.floating_size_box.height = 45 if value else 0
        self.floating_size_box.opacity = 1 if value else 0
        self.floating_size_box.disabled = not value
        BUTTON_SETTINGS["floating_enabled"] = value
        size = int(self.size_input.text)
        BUTTON_SETTINGS["button_size"] = size
        if value:
            floating_button.enable_floating(size)
        else:
            floating_button.disable_floating()

    def update_floating_size(self, instance, value):
        try:
            size = max(1, min(100, int(value)))
            BUTTON_SETTINGS["button_size"] = size
            if BUTTON_SETTINGS["floating_enabled"]:
                floating_button.set_button_size(size)
        except ValueError:
            pass

    def toggle_countdown_settings(self, instance, value):
        self.countdown_input_box.height = 45 if value else 0
        self.countdown_input_box.opacity = 1 if value else 0
        self.countdown_input_box.disabled = not value
        BUTTON_SETTINGS["countdown_enabled"] = value

    # ---------------- Save Settings ----------------
    def save_settings(self, instance):
        # Tap count
        try:
            BUTTON_SETTINGS["tap_count"] = max(1, int(self.tap_count_input.text))
        except ValueError:
            BUTTON_SETTINGS["tap_count"] = 1

        # Floating button size
        try:
            BUTTON_SETTINGS["button_size"] = max(1, min(100, int(self.size_input.text)))
        except ValueError:
            BUTTON_SETTINGS["button_size"] = 50

        # Lock screen
        BUTTON_SETTINGS["lock_screen"] = self.lock_chk.active

        # Countdown seconds
        try:
            BUTTON_SETTINGS["countdown_seconds"] = max(1, int(self.countdown_input.text))
        except ValueError:
            BUTTON_SETTINGS["countdown_seconds"] = 5

        # Update app-level settings
        self.app.button_settings = BUTTON_SETTINGS

        # Update handlers
        if self.app.shake_voice_handler:
            self.app.shake_voice_handler.update_settings(BUTTON_SETTINGS)
        if BUTTON_SETTINGS["floating_enabled"]:
            float.set_button_size(BUTTON_SETTINGS["button_size"])

        Popup(title="Saved",
              content=Label(text="Button settings saved and monitoring updated!"),
              size_hint=(0.6, 0.3)).open()
