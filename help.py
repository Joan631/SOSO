from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

FAQ_DATA = [
    {"q": "How do I edit my profile information?",
     "a": "Navigate to the Profile screen, tap the 'Edit Profile' button, modify the fields, then tap 'Save Changes'."},
    {"q": "What do the status options mean?",
     "a": "The status options indicate your current availability. Tap the status button to cycle through them."},
    {"q": "How can I log out of the application?",
     "a": "Tap the 'Log Out' button on the Profile screen to end your session."},
    {"q": "How do I enable the Shake feature?",
     "a": "In Settings, toggle the 'Shake to Alert' option. Shaking your device will send an alert to your contacts."},
    {"q": "How do I enable Voice alerts?",
     "a": "In Settings, turn on 'Voice Alerts'. Ensure microphone permissions are granted."},
    {"q": "How do I update my location?",
     "a": "On the Profile screen, tap 'Update Location'. The app will use GPS to update your location automatically."},
    {"q": "How do I add contacts?",
     "a": "Navigate to the Contacts tab, tap '+', enter contact details, and save."},
    {"q": "What happens when I delete a contact?",
     "a": "Deleted contacts are permanently removed. They no longer receive alerts or updates."},
    {"q": "Can I change my profile picture?",
     "a": "Place a new image named 'logo.png.jpg' in the resources folder. The app will display the new image automatically."},
    {"q": "What should I do if the app is not responding?",
     "a": "Close the app completely and reopen it. If the problem persists, restart your device or reinstall the app."},
    {"q": "How do I reset my preferences?",
     "a": "Go to Settings, then tap 'Reset Preferences' to restore default settings."}
]

class MinimalSearchBar(TextInput):
    """Minimalist search bar with rounded corners and maroon focus border."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex('#F8F8F8')  # light gray
        self.foreground_color = get_color_from_hex('#800000')  # maroon text
        self.cursor_color = get_color_from_hex('#800000')
        self.padding = [dp(12), dp(12)]
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = dp(16)
        self.hint_text = kwargs.get('hint_text', '')

        # Rounded rectangle background and border
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            self.border_color = Color(0, 0, 0, 0)
            self.border_line = Line(width=1.5, rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)))

        self.bind(pos=self.update_canvas, size=self.update_canvas, focus=self.on_focus_change)

    def update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))

    def on_focus_change(self, instance, value):
        self.border_color.rgb = (0.5, 0, 0) if value else (0.7, 0.7, 0.7)
        self.border_color.a = 1

class HelpScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)

        # White background
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Search Input
        self.search_input = MinimalSearchBar(hint_text="What are you looking for?")
        self.search_input.bind(text=self.filter_faqs)
        self.add_widget(self.search_input)

        # Scrollable FAQ Container
        self.scroll_view = ScrollView(do_scroll_x=False)
        self.faq_list_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(15)
        )
        self.faq_list_container.bind(minimum_height=self.faq_list_container.setter('height'))
        self.scroll_view.add_widget(self.faq_list_container)
        self.add_widget(self.scroll_view)

        # Populate FAQs initially
        self.populate_faqs(FAQ_DATA)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _create_faq_entry(self, question, answer):
        entry = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5), padding=[dp(5), 0])

        # Question
        question_label = Label(
            text=f"[b]Q: {question}[/b]",
            markup=True,
            halign='left',
            valign='top',
            size_hint_y=None,
            color=get_color_from_hex('#800000'),
            text_size=(self.width - dp(30), None)
        )
        question_label.bind(texture_size=lambda inst, val: setattr(inst, 'height', inst.texture_size[1]))

        # Answer
        answer_label = Label(
            text=f"A: {answer}",
            halign='left',
            valign='top',
            size_hint_y=None,
            color=get_color_from_hex('#800000'),
            text_size=(self.width - dp(30), None)
        )
        answer_label.bind(texture_size=lambda inst, val: setattr(inst, 'height', inst.texture_size[1] + dp(5)))

        # Update text_size on width change
        entry.bind(width=lambda instance, value: [
            setattr(question_label, 'text_size', (value - dp(30), None)),
            setattr(answer_label, 'text_size', (value - dp(30), None))
        ])

        entry.add_widget(question_label)
        entry.add_widget(answer_label)
        return entry

    def populate_faqs(self, faqs_to_display):
        self.faq_list_container.clear_widgets()
        for faq in faqs_to_display:
            faq_widget = self._create_faq_entry(faq['q'], faq['a'])
            self.faq_list_container.add_widget(faq_widget)
        self.faq_list_container.add_widget(Label(size_hint_y=None, height=dp(20)))

    def filter_faqs(self, instance, search_text):
        term = search_text.lower().strip()
        if not term:
            self.populate_faqs(FAQ_DATA)
            return
        filtered = [faq for faq in FAQ_DATA if term in faq['q'].lower() or term in faq['a'].lower()]
        self.populate_faqs(filtered)

class HelpApp(App):
    def build(self):
        self.title = "Help & FAQs"
        return HelpScreen()

if __name__ == "__main__":
    HelpApp().run()
