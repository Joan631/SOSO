import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex # Utility for cleaner color definitions

kivy.require('1.9.0')

class ProfileScreen(BoxLayout):
    # Define the possible status options
    STATUS_OPTIONS = ["Okay", "Not Okay", "Outside", "At Home"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)
        
        # Initial data storage
        self.user_data = {
            'name': 'Jane Doe',
            'status': self.STATUS_OPTIONS[0], # Start with "Okay"
            'contact_number': '(555) 123-4567', 
            'location': 'New York, USA'
        }
        
        # State tracker and widget storage
        self.editing = False 
        self.edit_widgets = {} # Stores Contact and Location TextInputs

        self.build_ui()
        
    def build_ui(self):
        self.clear_widgets()

        # 1. Profile Logo/Image and Name
        try:
            # Changed source reference to 'company_logo.png'
            self.profile_image = Image(
                source='company_logo.png', 
                size_hint=(None, None),
                size=(dp(100), dp(100)),
                pos_hint={'center_x': 0.5},
                allow_stretch=True
            )
            self.add_widget(self.profile_image)
        except Exception:
            # Updated fallback text to [Logo Placeholder]
            self.add_widget(Label(text='[Logo Placeholder]', size_hint_y=None, height=dp(100), markup=True))

        # Name Input (Still Editable in the main Edit Mode)
        self.name_input = TextInput(
            text=self.user_data['name'], 
            font_size=dp(24), 
            multiline=False, 
            size_hint_y=None, 
            height=dp(40), 
            readonly=True, 
            background_color=get_color_from_hex('#F0F0F0') # Light grey background
        )
        self.edit_widgets['name'] = self.name_input
        self.add_widget(self.name_input)

        # 2. Status Selector (Replaces Bio)
        # Button to cycle the status quickly.
        self.status_button = Button(
            text=f"Status: {self.user_data['status']}",
            font_size=dp(18),
            size_hint_y=None, 
            height=dp(40),
            background_color=get_color_from_hex('#3498DB'), # Blue background
            color=get_color_from_hex('#FFFFFF')
        )
        self.status_button.bind(on_press=self.cycle_status)
        self.add_widget(self.status_button)

        self.add_widget(Label(text='--- [ Account Details ] ---', size_hint_y=None, height=dp(20)))

        # 3. Core Information Fields
        self._add_info_field('Contact Number', 'contact_number') 
        self._add_info_field('Location', 'location')

        # Add a flexible spacer
        self.add_widget(Label(text='')) 

        # 4. Action Buttons
        
        # Edit/Save Button
        self.edit_button = Button(
            text='Edit Profile', 
            size_hint_y=None, 
            height=dp(50),
            background_color=get_color_from_hex('#2ECC71') # Green for primary action
        )
        self.edit_button.bind(on_press=self.switch_mode) 
        self.add_widget(self.edit_button)

        # Log Out Button
        logout_button = Button(
            text='Log Out', 
            size_hint_y=None, 
            height=dp(50),
            background_color=get_color_from_hex('#F39C12') # Orange/Warning color
        )
        # Note: In a real app, this should navigate back to a login screen.
        logout_button.bind(on_press=App.get_running_app().stop) 
        self.add_widget(logout_button)
        
        # DELETE ACCOUNT Button 
        delete_button = Button(
            text='DELETE ACCOUNT', 
            size_hint_y=None, 
            height=dp(50),
            background_color=get_color_from_hex('#E74C3C'), # Red for destructive action
            color=get_color_from_hex('#FFFFFF'),
            bold=True
        )
        delete_button.bind(on_press=self.delete_account)
        self.add_widget(delete_button)
    
    def _add_info_field(self, label_text, data_key):
        """Helper to create and add the label/input pair for core info."""
        container = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        
        # Make Label right-aligned for better visual flow
        container.add_widget(Label(text=label_text + ':', halign='right', size_hint_x=0.3, text_size=(dp(100), dp(40))))
        
        input_field = TextInput(
            text=self.user_data[data_key], 
            halign='left', 
            size_hint_x=0.7, 
            multiline=False,
            input_type='tel' if data_key == 'contact_number' else 'text',
            readonly=True, 
            background_color=get_color_from_hex('#F0F0F0') # Light grey background
        )
        
        self.edit_widgets[data_key] = input_field
        container.add_widget(input_field)
        self.add_widget(container)

    def cycle_status(self, instance):
        """Cycles the user status through the predefined options."""
        current_status = self.user_data['status']
        try:
            # Find the index of the current status
            current_index = self.STATUS_OPTIONS.index(current_status)
            # Calculate the index of the next status (wraps around using modulo)
            next_index = (current_index + 1) % len(self.STATUS_OPTIONS)
            new_status = self.STATUS_OPTIONS[next_index]
            
            # Update data and button text
            self.user_data['status'] = new_status
            instance.text = f"Status: {new_status}"
            print(f"Status changed to: {new_status}")
            
        except ValueError:
            # Should only happen if status is somehow corrupt; reset to first option
            self.user_data['status'] = self.STATUS_OPTIONS[0]
            instance.text = f"Status: {self.STATUS_OPTIONS[0]}"


    def switch_mode(self, instance):
        """Toggles the UI between View Mode and Edit Mode for Contact and Location."""
        if not self.editing:
            # --- Entering Edit Mode ---
            self.editing = True
            instance.text = 'Save Changes'
            instance.background_color = get_color_from_hex('#3498DB') # Blue when saving
            
            # Make TextInputs editable
            for key, widget in self.edit_widgets.items():
                widget.readonly = False
                widget.background_color = get_color_from_hex('#FFFFFF') # White for active input
            
        else:
            # --- Exiting Edit Mode (Saving) ---
            self.editing = False
            instance.text = 'Edit Profile'
            instance.background_color = get_color_from_hex('#2ECC71') # Green when in view mode
            
            # Update data, disable editing, and revert background
            for key, widget in self.edit_widgets.items():
                self.user_data[key] = widget.text
                widget.readonly = True
                widget.background_color = get_color_from_hex('#F0F0F0') # Light grey background
                
            print("Changes Saved:", self.user_data)
            
    def delete_account(self, instance):
        """Placeholder for the account deletion logic."""
        # TODO: In a real application, you would add a confirmation popup here.
        print("\n!!! ACCOUNT DELETION TRIGGERED !!!")
        print("--- Initiating user data cleanup and application shutdown. ---")
        
        # For this example, we'll just stop the app after a simulated deletion.
        # In a real app, you would perform the deletion then navigate to a start screen.
        App.get_running_app().stop()

class ProfileApp(App):
    def build(self):
        self.title = 'Editable User Profile'
        return ProfileScreen()

if __name__ == '__main__':
    ProfileApp().run()
