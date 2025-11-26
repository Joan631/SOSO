from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import json
import os
import platform

from floating_button import enable_floating, send_sos_message


DATA_FILE = "contacts.json"
CATEGORIES = ["THREATS", "ACCIDENTS", "FIRE", "MEDICAL", "ONE TAP EMERGENCY"]

# -------------------- Load Contacts --------------------
def load_contacts_file():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return [c for c in data if isinstance(c, dict) and "name" in c and "phone" in c and "categories" in c]
    except:
        return []

contacts = load_contacts_file()

# -------------------- SMS Sending --------------------
def send_sms_to_category(category, message):
    is_android = (platform.system() == "Linux")
    if not is_android:
        print("SMS sending works only on Android.")
        return
    try:
        from jnius import autoclass
        SmsManager = autoclass("android.telephony.SmsManager").getDefault()
    except Exception as e:
        print("Error initializing SMS API:", e)
        return
    group = [c for c in contacts if category in c["categories"]]
    if not group:
        print("No contacts found for category:", category)
        return
    for c in group:
        try:
            SmsManager.sendTextMessage(c["phone"], None, message, None, None)
            print("SMS sent to:", c["name"], c["phone"])
        except Exception as e:
            print("Failed sending to", c["phone"], ":", e)


# -------------------- Contacts Screen --------------------
class ContactsScreen(Screen):
    selected_contact = None

    def on_kv_post(self, base_widget):
        self.category_checks = {}
        self.add_form_categories_dict = {}
        self.inputs_visible = False
        self.setup_category_checkboxes()
        self.load_contacts()
        # Enable SOS floating button with live contacts
        enable_floating(size=80, callback=lambda: send_sos_message(contacts))


    # -------------------- Setup Main Category Checkboxes --------------------
    def setup_category_checkboxes(self):
        layout = self.ids.cat_layout
        layout.clear_widgets()

        # ALL checkbox
        all_chk = CheckBox(active=True)
        all_lbl = Label(text="ALL", size_hint_x=None, width=150, color=(1,1,1,1))
        box = BoxLayout(size_hint_y=None, height=30)
        box.add_widget(all_chk)
        box.add_widget(all_lbl)
        layout.add_widget(box)
        all_chk.bind(active=self.on_all_checkbox)
        self.category_checks["ALL"] = all_chk

        # Individual categories
        for cat in CATEGORIES:
            chk = CheckBox(active=True)
            lbl = Label(text=cat, size_hint_x=None, width=150, color=(1,1,1,1))
            box = BoxLayout(size_hint_y=None, height=30)
            box.add_widget(chk)
            box.add_widget(lbl)
            layout.add_widget(box)
            chk.bind(active=self.update_contacts_display)
            self.category_checks[cat] = chk

    # -------------------- Load / Update Contacts --------------------
    def load_contacts(self):
        self.update_contacts_display()

    def update_contacts_display(self, *args):
        grid = self.ids.contacts_grid
        grid.clear_widgets()

        active_cats = [cat for cat, chk in self.category_checks.items() if chk.active]
        show_all = "ALL" in active_cats

        filtered = [c for c in contacts if show_all or any(cat in c["categories"] for cat in active_cats)]
        if not filtered:
            grid.add_widget(Label(text="No contacts to display.", size_hint_y=None, height=30, color=(1,1,1,1)))
            return

        for i, c in enumerate(filtered):
            cat_text = ", ".join(c["categories"])
            btn = Button(text=f"{c['name']} ({c['phone']})\n[{cat_text}]",
                         size_hint_y=None, height=60,
                         background_color=(0.5,0,0,1), color=(1,1,1,1))
            btn.bind(on_release=lambda inst, idx=i: self.contact_options(idx, filtered))
            grid.add_widget(btn)

    def on_all_checkbox(self, checkbox, value):
        if value:
            for cat, chk in self.category_checks.items():
                if cat != "ALL":
                    chk.active = True
        else:
            if not any(chk.active for cat, chk in self.category_checks.items() if cat != "ALL"):
                checkbox.active = True
        self.update_contacts_display()

    # -------------------- Toggle Add Contact Form --------------------
    def show_add_form(self):
        self.inputs_visible = not self.inputs_visible
        self.ids.add_form.opacity = 1 if self.inputs_visible else 0
        self.ids.add_form.disabled = not self.inputs_visible
        if self.inputs_visible:
            self.clear_fields()
            self.setup_add_form_categories()


    # -------------------- Setup Categories for Add Form --------------------
    def setup_add_form_categories(self):
        grid = self.ids.add_cat_grid
        grid.clear_widgets()
        self.add_form_categories_dict = {}

        for cat in CATEGORIES:
            box = BoxLayout(size_hint_y=None, height=30, spacing=5)
            chk = CheckBox(active=False)
            lbl = Label(text=cat, size_hint_x=None, width=150, color=(1,1,1,1))
            box.add_widget(chk)
            box.add_widget(lbl)
            grid.add_widget(box)
            self.add_form_categories_dict[cat] = chk

    # -------------------- Add / Update Contact --------------------
    def add_or_update_contact(self):
        name = self.ids.name_input.text.strip()
        phone = self.ids.phone_input.text.strip()
        categories = [cat for cat, chk in self.add_form_categories_dict.items() if chk.active]

        if not name or not phone or not categories:
            self.show_popup("Error", "Name, phone, and at least one category required!")
            return

        global contacts
        data = {"name": name, "phone": phone, "categories": categories}

        if self.selected_contact is not None:
            contacts[self.selected_contact] = data
            self.selected_contact = None
            self.ids.add_contact_btn.text = "Add Contact"
        else:
            contacts.append(data)

        self.save_contacts()
        self.clear_fields()
        self.show_add_form()  # hide form
        self.load_contacts()

    def clear_fields(self):
        self.ids.name_input.text = ""
        self.ids.phone_input.text = ""
        self.selected_contact = None
        self.ids.add_contact_btn.text = "Add Contact"

    # -------------------- Contact Options --------------------
    def contact_options(self, index, contact_list):
        contact = contact_list[index]
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"{contact['name']} ({contact['phone']})\nCategories: {', '.join(contact['categories'])}",
                                 color=(1,1,1,1)))

        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=5)
        edit_btn = Button(text="Edit", background_color=(1,0,0,1), color=(1,1,1,1))
        del_btn = Button(text="Delete", background_color=(0.5,0,0,1), color=(1,1,1,1))
        sms_btn = Button(text="Send SMS", background_color=(1,0,0,1), color=(1,1,1,1))
        cancel_btn = Button(text="Cancel", background_color=(0.2,0,0,1), color=(1,1,1,1))
        btn_row.add_widget(edit_btn)
        btn_row.add_widget(del_btn)
        btn_row.add_widget(sms_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Contact Options", content=content, size_hint=(0.8, 0.5))
        edit_btn.bind(on_release=lambda inst: (self.edit_contact(contact), popup.dismiss()))
        del_btn.bind(on_release=lambda inst: (self.remove_contact(contact), popup.dismiss()))
        sms_btn.bind(on_release=lambda inst: (self.send_sms(contact), popup.dismiss()))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def edit_contact(self, contact):
        idx = contacts.index(contact)
        self.selected_contact = idx
        self.ids.name_input.text = contact["name"]
        self.ids.phone_input.text = contact["phone"]
        self.show_add_form()
        for cat, chk in self.add_form_categories_dict.items():
            chk.active = cat in contact["categories"]
        self.ids.add_contact_btn.text = "Update"

    def remove_contact(self, contact):
        global contacts
        contacts.remove(contact)
        self.save_contacts()
        self.load_contacts()

    def delete_saved_contact(self):
        if not contacts:
            self.show_popup("Info", "No saved contacts to delete.")
            return
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        for i, c in enumerate(contacts):
            btn = Button(text=f"{c['name']} ({c['phone']})", size_hint_y=None, height=40,
                         background_color=(1,0,0,1), color=(1,1,1,1))
            btn.bind(on_release=lambda inst, idx=i: self.confirm_delete(idx))
            content.add_widget(btn)
        popup = Popup(title="Select Contact to Delete", content=content, size_hint=(0.8, 0.6))
        popup.open()
        self._delete_popup = popup

    def confirm_delete(self, index):
        contact = contacts.pop(index)
        self.save_contacts()
        self.load_contacts()
        if hasattr(self, "_delete_popup"):
            self._delete_popup.dismiss()
        self.show_popup("Deleted", f"{contact['name']} removed successfully.")

    def send_sms(self, contact):
        is_android = (platform.system() == "Linux")
        if not is_android:
            self.show_popup("Info", f"SMS sending only works on Android. Would send to: {contact['phone']}")
            return
        try:
            from jnius import autoclass
            SmsManager = autoclass("android.telephony.SmsManager").getDefault()
            SmsManager.sendTextMessage(contact['phone'], None, "Hello from app!", None, None)
            self.show_popup("Success", f"SMS sent to {contact['name']}!")
        except Exception as e:
            self.show_popup("Error", f"Failed to send SMS: {e}")

    # -------------------- Save Contacts --------------------
    def save_contacts(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(contacts, f, indent=4)
        except Exception as e:
            self.show_popup("Error", f"Failed to save contacts: {e}")

    # -------------------- Popup --------------------
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message, color=(0,0,0,1)), size_hint=(0.7, 0.3))
        popup.open()
