# main.py
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivymd.uix.textfield import MDTextField
from kivy.uix.button import Button
from kivymd.app import MDApp
from plyer import notification
from kivy.factory import Factory
from kivy.utils import platform
from sms_manager import init_db, read_sms_inbox, filter_messages, save_spam, get_grouped_spam, SMSReceiver
import json, os

from geopy.geocoders import Nominatim
from contacts import ContactsScreen, send_sms_to_category
from button_settings import ButtonSettingsScreen
from help import HelpScreen
from profile import ProfileScreen

MARKERS_FILE = "markers.json"

# ---------------- Custom Widgets ----------------
class ClickableOverlay(ButtonBehavior, BoxLayout):
    pass

class ColoredMarker(MapMarkerPopup):
    def __init__(self, category="safe", **kwargs):
        super().__init__(**kwargs)
        self.category = category
        self.size = (30, 30)
        self.bind(pos=self.update_dot, size=self.update_dot)
        self.update_dot()

    def update_dot(self, *args):
        self.canvas.clear()
        with self.canvas:
            if self.category == "safe":
                Color(0, 0.8, 0, 1)
            elif self.category == "moderate":
                Color(1, 0.6, 0, 1)
            else:
                Color(0.9, 0, 0, 1)
            Ellipse(pos=(self.x-15, self.y-15), size=self.size)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_lat = 14.5995
        self.current_lon = 120.9842
        self.dashboard_open = False
        self.countdown_event = None
        self.popup = None
        self.current_category = ""
        self.geolocator = Nominatim(user_agent="safe_map_app")
        self.recent_searches = []
        self.sms_receiver = None

    # ---------------- Marker Reload ----------------
    def reload_markers(self):
        map_widget = self.ids.map_widget

        # Remove all previous ColoredMarkers and "You are here" marker
        for child in list(map_widget.children):
            if isinstance(child, ColoredMarker) or getattr(child, "you_marker", False):
                map_widget.remove_widget(child)

        # Load markers from file
        if os.path.exists(MARKERS_FILE):
            with open(MARKERS_FILE, "r") as f:
                for m in json.load(f):
                    marker = ColoredMarker(lat=m["lat"], lon=m["lon"], category=m["category"])
                    map_widget.add_widget(marker)

        # Add "You are here"
        you_marker = MapMarkerPopup(lat=self.current_lat, lon=self.current_lon)
        you_marker.add_widget(Label(text="You are here"))
        you_marker.you_marker = True
        map_widget.add_widget(you_marker)

    def on_kv_post(self, base_widget):
        # Get reference to spam screen
        self.spam_screen = self.manager.get_screen("spam")

        Clock.schedule_once(lambda dt: self.reload_markers(), 0)

        if platform == "android":
            Clock.schedule_once(lambda dt: self.setup_sms_monitoring(), 0)
        else:
            print("Skipping SMS setup (Windows mode)")

    # ---------------- Spam/Threat Setup ----------------

    def setup_sms_monitoring(self):
        init_db()
        
        # Read inbox once
        all_sms = read_sms_inbox()
        filtered = filter_messages(all_sms)
        save_spam(filtered)
        self.update_counter()

        # Real-time SMS listener (Android only)
        if platform == "android":
            from jnius import autoclass
            self.sms_receiver = SMSReceiver(update_callback=self.on_sms_received)
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            IntentFilter = autoclass('android.content.IntentFilter')
            activity = PythonActivity.mActivity
            filter = IntentFilter("android.provider.Telephony.SMS_RECEIVED")
            activity.registerReceiver(self.sms_receiver, filter)
            print("SMS monitoring started (Android).")
        else:
            print("SMS monitoring skipped (not running on Android).")
    
    def on_sms_received(self, sms_message):
        """
        Called by SMSReceiver when a new SMS arrives.
        sms_message: dict with keys 'sender', 'message'
        """
        # Check if spam using SpamDetailScreen keywords
        if self.spam_screen and self.spam_screen.detect_spam(sms_message["message"]):
            print("Blocked spam SMS:", sms_message["message"])
            # Save spam locally
            data = load_spam()
            data.append({"message": sms_message["message"], "category": "spam"})
            save_spam(data)
            self.update_counter()

    def update_counter(self):
        data = get_grouped_spam()
        if hasattr(self.ids, "spam_header"):
            header = self.ids.spam_header
            header.text = f"Spam: {data['spam']} | Threats: {data['threat']}"
            if data['threat'] > 0:
                header.color = (1, 0.3, 0.3, 1)
            elif data['spam'] > 0:
                header.color = (1, 0.9, 0, 1)
            else:
                header.color = (0, 0, 0, 1)

    def on_spam_header_click(self):
        self.manager.current = "spam_detail"
    # ---------------- Search ----------------
    def on_search_entered(self, instance):
        query = self.ids.search_field.text.strip()
        if query:
            self.goto_location(query)

    def goto_location(self, query):
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="safe_map_app")
            location = geolocator.geocode(query)
            if location:
                self.mapview.center_on(location.latitude, location.longitude)
                self.mapview.zoom = 15

                # Save search to suggestions
                if query not in self.recent_searches:
                    self.recent_searches.insert(0, query)
                    if len(self.recent_searches) > 5:
                        self.recent_searches.pop()

                self.update_suggestions()
                return
        except:
            pass

        # If place search fails → search category markers
        self.search_markers(query)


    def update_suggestions(self):
        box = self.ids.suggestions_box
        box.clear_widgets()
        for s in self.recent_searches:
            btn = Button(text=s, size_hint_y=None, height=30,
                         on_release=lambda x, s=s: self.goto_location(s))
            box.add_widget(btn)

    def search_markers(self, category):
        map_widget = self.ids.map_widget
        target_marker = None
        for child in map_widget.children:
            if isinstance(child, ColoredMarker):
                if not category.strip():
                    child.opacity = 1
                elif child.category.lower() == category.lower():
                    child.opacity = 1
                    if not target_marker:
                        target_marker = child
                else:
                    child.opacity = 0.2
        if target_marker:
            map_widget.center_on(target_marker.lat, target_marker.lon)

    # ---------------- SOS ----------------
    def on_sos_pressed(self, category):
        self.current_category = category
        if self.countdown_event:
            Clock.unschedule(self.countdown_event)
        self.remaining_time = 5
        layout = BoxLayout(orientation="vertical", spacing=10)
        self.countdown_label = Label(text=f"Sending {category} alert in {self.remaining_time} sec")
        layout.add_widget(self.countdown_label)
        cancel_btn = Button(text="Cancel", size_hint_y=None, height=40)
        cancel_btn.bind(on_release=self.cancel_countdown)
        layout.add_widget(cancel_btn)
        self.popup = Popup(title=f"{category} SOS Countdown", content=layout, size_hint=(0.8,0.4))
        self.popup.open()
        self.countdown_event = Clock.schedule_interval(self._countdown_tick, 1)

    def _countdown_tick(self, dt):
        self.remaining_time -= 1
        self.countdown_label.text = f"Sending {self.current_category} alert in {self.remaining_time} sec"
        if self.remaining_time <= 0:
            Clock.unschedule(self.countdown_event)
            if self.popup:
                self.popup.dismiss()
            self.report_all()
        return True

    def cancel_countdown(self, instance):
        Clock.unschedule(self.countdown_event)
        if self.popup:
            self.popup.dismiss()
        print(f"{self.current_category} SOS cancelled.")

    def report_all(self):
        msg = f"EMERGENCY ({self.current_category})! Location: https://maps.google.com/?q={self.current_lat},{self.current_lon}"
        print(msg)
        send_sms_to_category(self.current_category, msg)  # <-- this is the key
        notification.notify(
            title=f"SOS Sent: {self.current_category}",
            message="Your alert and location have been sent.",
            timeout=5
        )


    # ---------------- Dashboard ----------------
    def toggle_dashboard(self):
        menu = self.ids.dashboard_menu
        if self.dashboard_open:
            Animation(width=0, pos_hint={"x": -1}, duration=0.3).start(menu)
            self.dashboard_open = False
        else:
            Animation(width=200, pos_hint={"x": 0}, duration=0.3).start(menu)
            self.dashboard_open = True

    def open_map_editor(self): self.manager.current = "map_editor"
    
    def open_profile(self):
        app = MDApp.get_running_app()

        # Pass user data to profile screen (if available)
        profile_screen = self.manager.get_screen("profile")
        profile_screen.user_data = getattr(app, "current_user_data", {})
        self.manager.current = "profile"

        # Close dashboard menu smoothly
        if hasattr(self.ids, "dashboard_menu"):
            Animation(width=0, pos_hint={"x": -1}, duration=0.3).start(self.ids.dashboard_menu)


    def open_settings(self):
        self.manager.current = "settings"
        if hasattr(self.ids, "dashboard_menu"):
            Animation(width=0, pos_hint={"x": -1}, duration=0.3).start(self.ids.dashboard_menu)


    def open_contacts(self):
        self.manager.current = "contacts"
        if hasattr(self.ids, "dashboard_menu"):
            Animation(width=0, pos_hint={"x": -1}, duration=0.3).start(self.ids.dashboard_menu)


    def open_help(self):
        self.manager.current = "help"
        if hasattr(self.ids, "dashboard_menu"):
            Animation(width=0, pos_hint={"x": -1}, duration=0.3).start(self.ids.dashboard_menu)


    def on_pre_enter(self):
        Clock.schedule_once(lambda dt: self.reload_markers(), 0)

class ContactsScreen(Screen): pass
class SettingsScreen(Screen): pass

class MapEditorScreen(Screen):
    def on_kv_post(self, base_widget):
        self.mapview = self.ids.editor_map
        self.all_markers = []
        self.unsaved_markers = []
        self.recent_searches = []
        self.changes_made = False
        self.last_selected_marker = None
        self.last_selected_location = None

        # Load markers from file
        self.load_markers_from_file()

        # Schedule reload to ensure MapView has correct size
        Clock.schedule_once(lambda dt: self.reload_markers(), 0.1)
        self.mapview.bind(on_touch_up=self.on_map_touch)

    # ---------------- Load / Reload ----------------
    def load_markers_from_file(self):
        if os.path.exists(MARKERS_FILE):
            with open(MARKERS_FILE, "r") as f:
                data = json.load(f)
                self.all_markers.clear()
                for m in data:
                    marker = ColoredMarker(lat=m["lat"], lon=m["lon"], category=m["category"])
                    self.mapview.add_widget(marker)
                    self.all_markers.append(marker)

    def reload_markers(self):
        # Clear existing ColoredMarkers
        for child in list(self.mapview.children):
            if isinstance(child, ColoredMarker):
                self.mapview.remove_widget(child)

        # Reload from all_markers + unsaved
        for m in self.all_markers + self.unsaved_markers:
            if m.parent:
                m.parent.remove_widget(m)
            self.mapview.add_widget(m)


    # ---------------- Map Touch ----------------
    def on_map_touch(self, instance, touch):
        if self.mapview.collide_point(*touch.pos) and touch.button == "right":
            lat, lon = self.mapview.get_latlon_at(touch.x - self.mapview.x, touch.y - self.mapview.y)
            
            # Select nearest marker if close enough
            selected_marker = None
            threshold = 0.001
            for m in self.all_markers + self.unsaved_markers:
                dist = (m.lat - lat)**2 + (m.lon - lon)**2
                if dist < threshold**2:
                    selected_marker = m
                    break

            if selected_marker:
                self.last_selected_marker = selected_marker
                self.last_selected_location = (selected_marker.lat, selected_marker.lon)
            else:
                self.last_selected_marker = None
                self.last_selected_location = (lat, lon)

            self.show_marker_popup(lat, lon)
            return True
        return False

    # ---------------- Marker Popup ----------------
    def show_marker_popup(self, lat, lon):
        if hasattr(self, "marker_popup") and self.marker_popup:
            self.marker_popup.dismiss()

        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        btn_add = Button(text="Add Marker", size_hint_y=None, height=40)
        btn_remove = Button(text="Remove Marker", size_hint_y=None, height=40)
        btn_remove.disabled = self.last_selected_marker is None
        box.add_widget(btn_add)
        box.add_widget(btn_remove)

        self.marker_popup = Popup(title="Marker Options", content=box, size_hint=(0.5, 0.3))
        self.marker_popup.open()

        btn_add.bind(on_release=lambda x: [self.marker_popup.dismiss(), self.show_add_dialog(lat, lon)])
        btn_remove.bind(on_release=lambda x: [self.marker_popup.dismiss(), self.remove_selected_marker()])

    # ---------------- Add Marker ----------------
    def show_add_dialog(self, lat, lon):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        btn_safe = Button(text="Safe", background_color=(0,1,0,1), size_hint_y=None, height=40)
        btn_mod = Button(text="Moderate", background_color=(1,0.6,0,1), size_hint_y=None, height=40)
        btn_danger = Button(text="Dangerous", background_color=(1,0,0,1), size_hint_y=None, height=40)
        box.add_widget(btn_safe)
        box.add_widget(btn_mod)
        box.add_widget(btn_danger)
        popup = Popup(title="Select Category", content=box, size_hint=(0.5,0.35))
        popup.open()
        btn_safe.bind(on_release=lambda x:self.add_temp_marker(lat, lon, "safe", popup))
        btn_mod.bind(on_release=lambda x:self.add_temp_marker(lat, lon, "moderate", popup))
        btn_danger.bind(on_release=lambda x:self.add_temp_marker(lat, lon, "dangerous", popup))

    def add_temp_marker(self, lat, lon, category, popup):
        marker = ColoredMarker(lat=lat, lon=lon, category=category)
        self.mapview.add_widget(marker)
        self.unsaved_markers.append(marker)
        self.changes_made = True
        popup.dismiss()
        self.refresh_main_screen()

    # ---------------- Remove Marker ----------------
    def remove_selected_marker(self):
        if not self.last_selected_location:
            self.show_notification("No marker selected!")
            return

        lat, lon = self.last_selected_location
        nearest_marker = None
        threshold = 0.002  # Slightly larger threshold
        min_dist = float('inf')

        # Search among all markers
        for m in self.all_markers + self.unsaved_markers:
            dist = (m.lat - lat)**2 + (m.lon - lon)**2
            if dist < min_dist and dist < threshold**2:
                nearest_marker = m
                min_dist = dist

        if nearest_marker:
            # Safely remove from parent
            if nearest_marker.parent:
                try:
                    nearest_marker.parent.remove_widget(nearest_marker)
                except Exception as e:
                    print("Error removing marker:", e)

            # Remove from lists
            if nearest_marker in self.all_markers:
                self.all_markers.remove(nearest_marker)
            if nearest_marker in self.unsaved_markers:
                self.unsaved_markers.remove(nearest_marker)

            self.save_markers_to_file()
            self.show_notification("Marker removed!")
            self.last_selected_location = None
            self.changes_made = True

            # Refresh main screen
            self.refresh_main_screen()
        else:
            self.show_notification("No marker found near this location.")

    # ---------------- Save Changes ----------------
    def save_temp_changes(self):
        for m in self.unsaved_markers:
            self.all_markers.append(m)
        self.unsaved_markers.clear()
        self.save_markers_to_file()
        self.changes_made = False
        self.show_notification("Markers Saved!")
        self.refresh_main_screen()

    def save_markers_to_file(self):
        data = [{"lat": m.lat, "lon": m.lon, "category": m.category} for m in self.all_markers + self.unsaved_markers]
        with open(MARKERS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # ---------------- Notifications ----------------
    def show_notification(self, message):
        popup = Popup(title="Info", content=Label(text=message), size_hint=(0.5,0.3))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    # ---------------- Main Screen Refresh ----------------
    def refresh_main_screen(self):
        if "main" in self.manager.screen_names:
            main_screen = self.manager.get_screen("main")
            Clock.schedule_once(lambda dt: main_screen.reload_markers(), 0.1)

    # ---------------- Search ----------------
    def on_search_entered(self, instance):
        query = self.ids.search_field_editor.text.strip()
        if query:
            self.goto_location(query)

    def goto_location(self, query):
        try:
            geolocator = Nominatim(user_agent="safe_map_app")
            location = geolocator.geocode(query)
            if location:
                self.mapview.center_on(location.latitude, location.longitude)
                self.mapview.zoom = 15
                if query not in self.recent_searches:
                    self.recent_searches.insert(0, query)
                    if len(self.recent_searches) > 5:
                        self.recent_searches.pop()
                self.update_suggestions()
                return
        except:
            pass
        self.search_markers(query)

    def update_suggestions(self):
        box = self.ids.suggestions_box_editor
        box.clear_widgets()
        for s in self.recent_searches:
            btn = Button(text=s, size_hint_y=None, height=30,
                         on_release=lambda x, s=s: self.goto_location(s))
            box.add_widget(btn)

    def search_markers(self, category):
        target_marker = None
        for child in self.mapview.children:
            if isinstance(child, ColoredMarker):
                if not category.strip():
                    child.opacity = 1
                elif child.category.lower() == category.lower():
                    child.opacity = 1
                    if not target_marker:
                        target_marker = child
                else:
                    child.opacity = 0.2
        if target_marker:
            self.mapview.center_on(target_marker.lat, target_marker.lon)

    # ---------------- Back Button ----------------
    def on_back_pressed(self):
        main_screen = self.manager.get_screen("main")

        def go_back():
            self.manager.current = "main"
            Clock.schedule_once(lambda dt: main_screen.reload_markers(), 0.1)
            main_screen.reload_markers()

        if self.changes_made:
            box = BoxLayout(orientation="vertical", spacing=10)
            box.add_widget(Label(text="Save changes before exiting?"))
            btn_save = Button(text="Save", size_hint_y=None, height=40)
            btn_discard = Button(text="Discard", size_hint_y=None, height=40)
            box.add_widget(btn_save)
            box.add_widget(btn_discard)
            popup = Popup(title="Confirm", content=box, size_hint=(0.5,0.4))
            popup.open()

            btn_save.bind(on_release=lambda x: [
                self.save_temp_changes(),
                popup.dismiss(),
                go_back()
            ])
            btn_discard.bind(on_release=lambda x: [
                popup.dismiss(),
                go_back()
            ])
        else:
            go_back()
    
    def on_pre_enter(self):
        Clock.schedule_once(lambda dt: self.reload_markers(), 0.1)
