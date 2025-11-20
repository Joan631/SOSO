import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

kivy.require('1.9.0')

# Define the FAQ data structure
FAQ_DATA = [
    {"q": "How do I edit my profile information?", 
     "a": "Navigate to the Profile screen, tap the 'Edit Profile' button, modify the Name, Contact Number, or Location fields, and then tap 'Save Changes'. Ensure all fields are correctly formatted."},
    {"q": "What do the status options mean?", 
     "a": "The status options ('Okay', 'Not Okay', 'Outside', 'At Home') indicate your current availability or situation. They are designed to be a quick way to share your general status with contacts. Tap the status button to cycle through them."},
    {"q": "How can I log out of the application?", 
     "a": "You can log out by tapping the 'Log Out' button located at the bottom of the Profile screen. This will end your current session."},
    {"q": "Where is my data stored?", 
     "a": "Your profile data is stored securely locally on your device for quick access and minimal latency. Cloud synchronization is an optional feature."},
    {"q": "I forgot my password. What should I do?", 
     "a": "This application typically uses token-based or biometric authentication and does not require a traditional password. If you are having trouble logging in, please restart the application or check your device settings."},
    {"q": "How do I delete my account?", 
     "a": "Account deletion is permanent. On the Profile screen, tap the 'DELETE ACCOUNT' button. You will be prompted for confirmation before the deletion is executed to prevent accidental loss of data."},
    {"q": "Can I change my profile picture (logo)?", 
     "a": "Yes, you can change your profile image by placing a new file named 'logo.png.jpg' (or the specified file path) in the application's resources folder. The app will automatically detect and display the new image."},
    {"q": "The Edit/Save button is blue. What does that mean?",
     "a": "When the button is blue and says 'Save Changes', it means you are currently in Edit Mode. Tap it to save your changes and switch back to View Mode (where it will be green and say 'Edit Profile')."}
]

class HelpScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # 1. Search Input
        self.search_input = TextInput(
            # Updated hint_text as requested
            hint_text="What are you looking for?",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[dp(10), dp(10)],
            background_color=get_color_from_hex('#ECF0F1') # Light background for search
        )
        # Bind the text property to the filter function
        self.search_input.bind(text=self.filter_faqs)
        self.add_widget(self.search_input)
        
        # 2. Scrollable Container for FAQs
        self.faq_list_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        # Ensure the BoxLayout recalculates height based on its children
        self.faq_list_container.bind(minimum_height=self.faq_list_container.setter('height'))
        
        scroll_view = ScrollView(do_scroll_x=False)
        scroll_view.add_widget(self.faq_list_container)
        self.add_widget(scroll_view)
        
        # 3. Initially populate the list
        self.populate_faqs(FAQ_DATA)

    def _create_faq_entry(self, question, answer):
        """Creates a BoxLayout widget for a single FAQ item."""
        entry = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(5), padding=[dp(5), 0])
        entry.question_label = Label(
            text=f"[b]Q: {question}[/b]", 
            markup=True,
            halign='left',
            valign='top',
            size_hint_y=None, 
            height=dp(30),
            color=get_color_from_hex('#34495E'), # Dark text color
            text_size=(self.width - dp(30), None) # Use actual width for wrapping
        )
        
        entry.answer_label = Label(
            text=f"A: {answer}",
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(70), # Give ample space for the answer
            color=get_color_from_hex('#7F8C8D'), # Lighter text color
            text_size=(self.width - dp(30), None)
        )
        
        # Bind text_size update to width changes to ensure text wrapping works
        entry.bind(width=lambda instance, value: self._update_label_text_size(instance.question_label, value))
        entry.bind(width=lambda instance, value: self._update_label_text_size(instance.answer_label, value))
        
        entry.add_widget(entry.question_label)
        entry.add_widget(entry.answer_label)
        
        # Force height update after labels have calculated their size
        entry.question_label.bind(texture_size=lambda instance, value: self._update_entry_height(entry, instance))
        entry.answer_label.bind(texture_size=lambda instance, value: self._update_entry_height(entry, instance))
        
        entry.faq_data = {"q": question, "a": answer} # Store original data for filtering
        return entry

    def _update_label_text_size(self, label, width):
        """Helper function to update text_size when width changes."""
        label.text_size = (width - dp(30), None)

    def _update_entry_height(self, entry, label_instance):
        """Dynamically adjusts the BoxLayout height based on content size."""
        # Calculate new height based on texture_size + spacing + padding
        q_height = entry.question_label.texture_size[1]
        a_height = entry.answer_label.texture_size[1]
        
        # Set the minimum height for the entry (question + answer + spacing)
        entry.height = q_height + a_height + dp(10)

    def populate_faqs(self, faqs_to_display):
        """Clears and repopulates the list with the given FAQ data."""
        self.faq_list_container.clear_widgets()
        for faq in faqs_to_display:
            faq_widget = self._create_faq_entry(faq['q'], faq['a'])
            self.faq_list_container.add_widget(faq_widget)
            
        # Add a final spacer for good measure
        self.faq_list_container.add_widget(Label(size_hint_y=None, height=dp(20)))

    def filter_faqs(self, instance, search_text):
        """Filters the displayed FAQs based on the search input."""
        search_term = search_text.lower().strip()
        
        if not search_term:
            # If search term is empty, show all FAQs
            self.populate_faqs(FAQ_DATA)
            return

        filtered_list = []
        for faq in FAQ_DATA:
            # Check if the search term is in the question OR the answer
            if search_term in faq['q'].lower() or search_term in faq['a'].lower():
                filtered_list.append(faq)

        self.populate_faqs(filtered_list)

class HelpApp(App):
    def build(self):
        self.title = 'Help and FAQs'
        return HelpScreen()

if __name__ == '__main__':
    HelpApp().run()
