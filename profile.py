from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivy.lang import Builder

KV = """
<ProfileScreen>:
    name: "profile"
    user_data: root.user_data

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(30)
        spacing: dp(20)
        md_bg_color: 1, 1, 1, 1  # White background

        MDLabel:
            text: "USER PROFILE"
            font_style: "H5"
            halign: "center"
            theme_text_color: "Custom"
            text_color: app.MAROON_COLOR

        MDTextField:
            id: profile_name
            hint_text: "Full Name"
            text: root.user_data['name']
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            cursor_color: app.MAROON_COLOR

        MDRaisedButton:
            id: status_btn
            text: "Status: " + root.user_data['status']
            md_bg_color: app.MAROON_COLOR
            on_release: root.cycle_status()
            size_hint_y: None
            height: dp(45)

        MDTextField:
            id: profile_contact
            hint_text: "Contact Number"
            text: root.user_data['contact_number']
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            cursor_color: app.MAROON_COLOR

        MDTextField:
            id: profile_location
            hint_text: "Location"
            text: root.user_data['location']
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            cursor_color: app.MAROON_COLOR

        # Horizontal button row
        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(15)
            size_hint_y: None
            height: dp(50)

            MDRaisedButton:
                text: "Save"
                md_bg_color: app.MAROON_COLOR
                on_release: root.save_profile(profile_name.text, profile_contact.text, profile_location.text, root.user_data['status'])

            MDRaisedButton:
                text: "Log Out"
                md_bg_color: app.MAROON_COLOR
                on_release: root.go_to_login()

            MDRaisedButton:
                text: "Delete"
                md_bg_color: app.MAROON_COLOR
                on_release: root.delete_account()
"""

class ProfileScreen(Screen):
    user_data = ObjectProperty({
        "name": "Jane Doe",
        "status": "Okay",
        "contact_number": "(555) 123-4567",
        "location": "New York, USA"
    })
    STATUS_OPTIONS = ["Okay", "Not Okay", "Outside", "At Home"]

    def cycle_status(self):
        """Cycle the status when the status button is clicked"""
        current = self.user_data['status']
        next_index = (self.STATUS_OPTIONS.index(current) + 1) % len(self.STATUS_OPTIONS)
        self.user_data['status'] = self.STATUS_OPTIONS[next_index]
        self.ids.status_btn.text = f"Status: {self.user_data['status']}"
        print("Status changed:", self.user_data['status'])

    def save_profile(self, name, contact, location, status):
        self.user_data['name'] = name
        self.user_data['contact_number'] = contact
        self.user_data['location'] = location
        self.user_data['status'] = status
        print("Profile saved:", self.user_data)

    def go_to_login(self):
        print("Redirecting to login screen...")
        # TODO: Replace with actual ScreenManager navigation

    def delete_account(self):
        print("Account deletion triggered!")

class ProfileApp(MDApp):
    MAROON_COLOR = (0.5, 0, 0, 1)

    def build(self):
        Builder.load_string(KV)
        return ProfileScreen()

if __name__ == "__main__":
    ProfileApp().run()
