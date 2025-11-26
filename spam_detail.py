from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from datetime import datetime

from sms_manager import load_spam, save_spam, get_grouped_spam, block_sms


class SpamDetailScreen(Screen):
    spam_messages = ListProperty([])
    spam_count = NumericProperty(0)
    threat_count = NumericProperty(0)

    # User-defined spam keywords
    spam_keywords = ListProperty(["free", "win", "prize", "claim", "₱", "lottery"])

    # Toggle blocking spam SMS
    block_enabled = BooleanProperty(False)

    def on_pre_enter(self):
        """Load spam + threat messages before screen appears."""
        data = get_grouped_spam()
        self.spam_messages = data["all"]
        self.spam_count = data["spam"]
        self.threat_count = data["threat"]
        self.load_list()

    def load_list(self):
        """Fill UI list with messages."""
        container = self.ids.spam_container
        container.clear_widgets()

        # Display spam messages
        for msg in self.spam_messages:
            text = msg["message"]
            category = msg["category"]
            color = (1, 0.9, 0, 1) if category == "spam" else (1, 0.3, 0.3, 1)

            btn = Button(
                text=text,
                size_hint_y=None,
                height=50,
                background_normal="",
                background_color=(0.2, 0.2, 0.2, 1),
                color=color
            )
            btn.bind(on_release=lambda b, t=text, c=category: self.open_popup(t, c))
            container.add_widget(btn)

    def open_popup(self, message, category):
        """Popup showing full message."""
        color = (1, 0.9, 0, 1) if category == "spam" else (1, 0.3, 0.3, 1)
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        lbl = Label(text=message, color=color)
        close_btn = Button(text="Close", size_hint_y=None, height=40)

        popup = Popup(
            title=f"Message ({category.upper()})",
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )

        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(lbl)
        content.add_widget(close_btn)
        popup.open()

    # ---------------- Keyword Management ----------------
    def show_keywords_popup(self, instance=None):
        """Popup to view/add/remove keywords."""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        keyword_input = TextInput(hint_text="Add keyword", size_hint_y=None, height=40)
        add_btn = Button(text="Add Keyword", size_hint_y=None, height=40)
        remove_all_btn = Button(text="Clear All Keywords", size_hint_y=None, height=40)
        close_btn = Button(text="Close", size_hint_y=None, height=40)

        content.add_widget(keyword_input)
        content.add_widget(add_btn)
        content.add_widget(remove_all_btn)
        content.add_widget(close_btn)

        popup = Popup(title="Spam Keywords", content=content, size_hint=(0.8, 0.5), auto_dismiss=False)

        def add_keyword(instance):
            kw = keyword_input.text.strip().lower()
            if kw and kw not in self.spam_keywords:
                self.spam_keywords.append(kw)
            keyword_input.text = ""

        def remove_all(instance):
            self.spam_keywords.clear()

        add_btn.bind(on_release=add_keyword)
        remove_all_btn.bind(on_release=remove_all)
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    # ---------------- Blocking Toggle ----------------
    def toggle_block(self, instance):
        self.block_enabled = not self.block_enabled
        instance.text = f"Block Spam: {'ON' if self.block_enabled else 'OFF'}"

    # ---------------- Spam Detection ----------------
    def detect_and_block(self, message, sender="Unknown"):
        """
        Detect spam using user-defined keywords.
        Save to spam DB and block if block_enabled is True.
        """
        msg_lower = message.lower()
        for kw in self.spam_keywords:
            if kw in msg_lower:
                # Add to spam DB
                spam_entry = {
                    "address": sender,
                    "message": message,
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "category": "spam"
                }
                save_spam([spam_entry])
                self.on_pre_enter()  # refresh UI list

                # Block if enabled
                if self.block_enabled:
                    block_sms(spam_entry)
                break
