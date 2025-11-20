from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button

class SpamDetector(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 1  # Add some spacing between widgets
        self.padding = 0.9
        
        # Message state
        self.message = ""
        self.is_spam = False

        # Spam keywords
        self.spam_keywords = [
            {"id": "1", "keyword": "free"},
            {"id": "2", "keyword": "win"},
            {"id": "3", "keyword": "click here"},
            {"id": "4", "keyword": "urgent"},
            {"id": "5", "keyword": "limited time"},
        ]

        # TextInput (larger)
        self.input = TextInput(
            hint_text="Enter message",
            size_hint_y=0.1,   # Takes 60% of vertical space
            multiline=True,
        )

        # Check button (lower)
        self.check_btn = Button(
            text="Check Spam",
            size_hint_y=0.1,
            height=50          # Makes the button bigger and lower
        )
        self.check_btn.bind(on_press=self.check_spam)

        # Result label
        self.result_label = Label(
            text="",
            size_hint_y=None,
            height=10
        )
        

        # Add widgets
        self.add_widget(self.input)
        self.add_widget(self.check_btn)
        self.add_widget(self.result_label)

    def check_spam(self, instance):
        self.message = self.input.text.strip().lower()
        self.is_spam = any(
            keyword["keyword"] in self.message for keyword in self.spam_keywords
        )
        if self.is_spam:
            self.result_label.text = "⚠️ Spam detected!"
        else:
            self.result_label.text = "✅ Not spam"


class SpamApp(App):
    def build(self):
        return SpamDetector()


if __name__ == "__main__":
    SpamApp().run()
