# contacts.py (with Back button)
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
import json
import os

DATA_FILE = "contacts.json"
CATEGORIES = ["THREATS", "ACCIDENTS", "FIRE", "MEDICAL", "ONE TAP EMERGENCY"]

def load_contacts_file():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        safe = [c for c in data if isinstance(c, dict)
                and "name" in c and "phone" in c and "categories" in c]
        return safe
    except:
        return []

contacts = load_contacts_file()

class ContactsManager(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.selected_contact = None

        # ---------- BACK BUTTON ----------
        back_btn = Button(text="← Back to Main", size_hint_y=None, height=40)
        back_btn.bind(on_release=self.go_back)
        self.add_widget(back_btn)

        # ---------- TITLE ----------
        self.add_widget(Label(text="Contact Manager", font_size=22,
                              size_hint_y=None, height=40))

        # ---------- FORM INPUTS ----------
        self.name_input = TextInput(hint_text="Name", size_hint_y=None, height=40)
        self.phone_input = TextInput(hint_text="Phone Number", size_hint_y=None,
                                     height=40, input_filter="int")
        self.add_widget(self.name_input)
        self.add_widget(self.phone_input)

        # ---------- CATEGORY CHECKBOXES ----------
        self.category_checks = {}
        cat_layout = GridLayout(cols=2, spacing=5, size_hint_y=None)
        cat_layout.bind(minimum_height=cat_layout.setter("height"))

        for cat in CATEGORIES:
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=30)
            chk = CheckBox(size_hint_x=None, width=40)
            self.category_checks[cat] = chk
            box.add_widget(chk)
            box.add_widget(Label(text=cat, halign="left"))
            cat_layout.add_widget(box)

        self.add_widget(cat_layout)

        # ---------- BUTTONS ----------
        btn_row = BoxLayout(size_hint_y=None, height=45, spacing=5)
        self.add_btn = Button(text="Add Contact")
        clear_btn = Button(text="Clear")

        self.add_btn.bind(on_press=self.add_or_update_contact)
        clear_btn.bind(on_press=self.clear_fields)

        btn_row.add_widget(self.add_btn)
        btn_row.add_widget(clear_btn)

        self.add_widget(btn_row)

        # ---------- CONTACTS LIST ----------
        self.add_widget(Label(text="Contacts List", font_size=18,
                              size_hint_y=None, height=30))

        self.scroll = ScrollView(size_hint=(1, 0.55))
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)

        self.load_contacts()

    # -------------------- BACK TO MAIN --------------------
    def go_back(self, instance):
        app = App.get_running_app()
        if hasattr(app, "root") and hasattr(app.root, "current"):
            app.root.current = "main"

    # -------------------- CONTACT MANAGEMENT --------------------
    def add_or_update_contact(self, instance):
        name = self.name_input.text.strip()
        phone = self.phone_input.text.strip()
        categories = [cat for cat, chk in self.category_checks.items() if chk.active]

        if not name or not phone or not categories:
            print("Name, phone and category required.")
            return

        contact_data = {"name": name, "phone": phone, "categories": categories}

        global contacts
        if self.selected_contact is not None:
            contacts[self.selected_contact] = contact_data
            self.selected_contact = None
            self.add_btn.text = "Add Contact"
        else:
            contacts.append(contact_data)

        self.save_contacts()
        self.clear_fields()
        self.load_contacts()

    def clear_fields(self, instance=None):
        self.name_input.text = ""
        self.phone_input.text = ""
        for chk in self.category_checks.values():
            chk.active = False
        self.selected_contact = None
        self.add_btn.text = "Add Contact"

    def edit_contact(self, index):
        contact = contacts[index]
        self.selected_contact = index
        self.name_input.text = contact["name"]
        self.phone_input.text = contact["phone"]
        for cat, chk in self.category_checks.items():
            chk.active = cat in contact["categories"]
        self.add_btn.text = "Update Contact"

    def remove_contact(self, index):
        global contacts
        contacts.pop(index)
        self.save_contacts()
        self.load_contacts()

    def save_contacts(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(contacts, f, indent=4)
        except Exception as e:
            print(f"Error writing contacts.json: {e}")

    def load_contacts(self):
        self.grid.clear_widgets()
        if not contacts:
            self.grid.add_widget(Label(text="No contacts yet.",
                                       size_hint_y=None, height=30))
            return

        for i, c in enumerate(contacts):
            cat_text = ", ".join(c["categories"])
            lbl = Label(text=f"{c['name']} ({c['phone']})\n[{cat_text}]",
                        size_hint_y=None, height=50)
            self.grid.add_widget(lbl)

            btn_row = BoxLayout(size_hint_y=None, height=40, spacing=5)
            edit_btn = Button(text="Edit")
            del_btn = Button(text="Delete")

            edit_btn.bind(on_press=lambda inst, idx=i: self.edit_contact(idx))
            del_btn.bind(on_press=lambda inst, idx=i: self.remove_contact(idx))

            btn_row.add_widget(edit_btn)
            btn_row.add_widget(del_btn)
            self.grid.add_widget(btn_row)


# ---------- APP WRAPPER ----------
class ContactsApp(App):
    def build(self):
        return ContactsManager()


if __name__ == "__main__":
    ContactsApp().run()
