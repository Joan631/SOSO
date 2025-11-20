from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
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
            readonly: True
            on_focus: root.ask_edit(self, "name") if self.focus else None
            on_text_validate: root.ask_save(self, "name")

        MDTextField:
            id: profile_contact
            hint_text: "Contact Number"
            text: root.user_data['contact_number']
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            cursor_color: app.MAROON_COLOR
            readonly: True
            on_focus: root.ask_edit(self, "contact_number") if self.focus else None
            on_text_validate: root.ask_save(self, "contact_number")

        MDTextField:
            id: profile_location
            hint_text: "Location"
            text: root.user_data['location']
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            cursor_color: app.MAROON_COLOR
            readonly: True
            on_focus: root.ask_edit(self, "location") if self.focus else None
            on_text_validate: root.ask_save(self, "location")

        MDBoxLayout:
            orientation: "horizontal"
            spacing: dp(15)
            size_hint_y: None
            height: dp(50)

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

    edit_field = None  # Track which field is being edited
    dialog = None

    def ask_edit(self, field_widget, key):
        """Ask if the user wants to edit the field."""
        if not field_widget.readonly:
            return  # Already editable

        def confirm_edit(*args):
            field_widget.readonly = False
            field_widget.focus = True
            self.edit_field = key
            dialog.dismiss()

        dialog = MDDialog(
            title="Edit Field",
            text=f"Do you want to edit {key.replace('_', ' ').title()}?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="EDIT", on_release=confirm_edit)
            ]
        )
        dialog.open()

    def ask_save(self, field_widget, key):
        """Ask if the user wants to save the changes after editing."""
        if self.edit_field != key:
            return  # Not currently editing this field

        def save_changes(*args):
            self.user_data[key] = field_widget.text
            field_widget.readonly = True
            self.edit_field = None
            dialog.dismiss()
            print(f"{key} updated to:", field_widget.text)

        dialog = MDDialog(
            title="Save Changes",
            text=f"Do you want to save changes to {key.replace('_', ' ').title()}?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="SAVE", on_release=save_changes)
            ]
        )
        dialog.open()

    def go_to_login(self):
        print("Redirecting to login screen...")

    def delete_account(self):
        print("Account deletion triggered!")

class ProfileApp(MDApp):
    MAROON_COLOR = (0.5, 0, 0, 1)

    def build(self):
        Builder.load_string(KV)
        return ProfileScreen()

if __name__ == "__main__":
    ProfileApp().run()

