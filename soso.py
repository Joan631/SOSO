import json
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDTextButton, MDRaisedButton
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button  # needed for items inside dropdown
from kivy.metrics import dp 
from kivy.clock import Clock # <-- Needed for the 3-second delay
from kivy.uix.widget import Widget # Explicit import for Widget
from kivy.uix.screenmanager import Screen

from main import MainScreen
from main import MapEditorScreen
from contacts import ContactsScreen
from spam_detail import SpamDetailScreen
from button_settings import ButtonSettingsScreen
from help import HelpScreen
from profile import ProfileScreen
from kivy.app import App
from country_codes import COUNTRY_CODES 
from accounts import load_accounts, save_accounts
import json

# --- Screen Definitions ---
class LoadingScreen(Screen):
    """Screen displayed for a fixed duration before LoginScreen."""
    def on_enter(self, *args):
        # Schedule the transition to the login screen after 3 seconds (3.0)
        Clock.schedule_once(self.switch_to_login, 3.0)

    def switch_to_login(self, dt):
        """Switches the screen manager to the login screen."""
        self.manager.current = 'login'

class LoginScreen(Screen):
    pass

class SignupScreen(Screen):
    pass

class ForgotPasswordScreen(Screen):
    pass

# --- KivyMD (KV) Design Language ---
KV = r'''
ScreenManager:
    id: screen_manager
    current: "loading"  # Start on the loading screen
    LoadingScreen:      # New loading screen definition
    LoginScreen:
    SignupScreen:
    ForgotPasswordScreen:
    MainScreen:
    ContactsScreen:
    SettingsScreen:
    SpamDetailScreen:
    MapEditorScreen:
    ProfileScreen:
    HelpScreen:

# ---------------- Loading Screen ----------------
<LoadingScreen>:
    name: "loading"

    MDBoxLayout:
        orientation: "vertical"
        halign: "center"
        valign: "center"
        md_bg_color: 1, 1, 1, 1
        spacing: dp(30)
        padding: dp(40)

        Widget:
            size_hint_y: 0.1

        FloatLayout:
            size_hint: 1, 1
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Image:
                source: "img/logo.png.jpg"
                size_hint: None, None
                size: min(self.parent.width * 0.8, self.parent.height * 0.8), min(self.parent.width * 0.8, self.parent.height * 0.8)
                allow_stretch: True
                keep_ratio: True
                mipmap: True
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}

        MDLabel:
            text: "Loading Application..."
            font_style: 'H6'
            halign: 'center'
            color: app.MAROON_COLOR
            size_hint_y: None
            height: dp(30)

        MDLabel:
            text: "Please wait"
            font_style: 'Caption'
            halign: 'center'
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: dp(20)

# ---------------- Login Screen ----------------
<LoginScreen>:
    name: "login"
    
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 1, 1, 1, 1
        
        # 1. Top Header Area (Logo and Title)
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: 0.15
            padding: [dp(20), dp(10), dp(20), dp(10)]
            spacing: dp(10)
            
            FloatLayout:
                size_hint: (None, 1)
                width: dp(40)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                Image:
                    source: "img/logo.png.jpg"
                    size_hint: (None, None)
                    size: dp(40), dp(40)
                    allow_stretch: True
                    mipmap: True
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                
            MDLabel:
                text: "SAVE OTHERS [b]SIGNAL ONCE[/b]"
                font_style: 'H6'
                markup: True
                halign: 'left'
                valign: 'center'
                color: app.MAROON_COLOR
                size_hint_y: 1
                
        # 2. Main Login Content Area (Inputs and Buttons)
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(40)
            spacing: dp(20) 
            size_hint_y: 0.85
            
            MDLabel:
                text: "LOGIN INTERFACE"
                font_style: 'H5'
                halign: 'center'
                color: app.MAROON_COLOR
            
            MDLabel:
                text: "Welcome back. Please login to your account!"
                font_style: 'Caption'
                halign: 'center'
                color: 0.3, 0.3, 0.3, 1 
            
            # Input Fields container
            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(20)
                size_hint_y: None
                height: self.minimum_height
                
                MDTextField:
                    id: login_username
                    hint_text: "Username"
                    mode: "rectangle" 
                    line_color_normal: 0.5, 0.5, 0.5, 1 
                    line_color_focus: app.MAROON_COLOR
                    icon_left: "account" 
                    icon_left_color: app.MAROON_COLOR

                MDTextField:
                    id: login_password
                    hint_text: "Password"
                    password: True
                    mode: "rectangle"
                    line_color_normal: 0.5, 0.5, 0.5, 1
                    line_color_focus: app.MAROON_COLOR
                    icon_left: "lock-outline"
                    icon_left_color: app.MAROON_COLOR
                    
                    # Password Visibility Toggle Fix
                    icon_right: "eye-off"
                    icon_right_color: app.MAROON_COLOR
                    on_touch_down: app.toggle_password_visibility(self, args[1])

            # Forgot Password Link
            MDTextButton:
                text: "[font=Icons]lock-reset[/font] Forgot Password?"
                markup: True
                font_style: 'Caption'
                color: app.MAROON_COLOR
                halign: 'right'
                size_hint_y: None
                height: dp(20)
                on_release: app.root.current = "forgot_password"

            # Login Button (Primary CTA)
            MDRaisedButton:
                text: "Login →"
                text_color: 1, 1, 1, 1 
                md_bg_color: app.MAROON_COLOR
                size_hint_x: 1
                height: dp(50)
                on_release: app.login_user(login_username.text, login_password.text)

            # Sign Up prompt
            MDBoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(20)
                
                MDLabel:
                    text: "Don't have an account?"
                    font_style: 'Caption'
                    halign: 'center'
                    color: 0.3, 0.3, 0.3, 1
                    size_hint_x: 0.6

                MDTextButton: 
                    text: "Sign up now!"
                    font_style: 'Caption'
                    color: app.MAROON_COLOR
                    on_release: app.root.current = "signup"
                    size_hint_x: 0.4
            
            # Spacer
            Widget:
                size_hint_y: 0.3
                
            # 3. Small icon at the bottom left
            MDBoxLayout:
                size_hint_y: None
                height: dp(40)
                padding: dp(10)
                MDLabel:
                    text: '[font=Icons]{}[/font]'.format('dots-grid') 
                    markup: True
                    font_style: 'H4'
                    size_hint_x: None
                    width: dp(40)
                    halign: 'left'

# ---------------- Signup Screen ----------------
<SignupScreen>:
    name: "signup"

    ScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20), dp(20), dp(20), dp(40)  # top, right, bottom, left
            spacing: dp(20)
            size_hint_y: None
            height: self.minimum_height

            MDLabel:
                text: "Create Account"
                font_style: "H5"
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
                color: app.MAROON_COLOR

            MDTextField:
                id: full_name
                hint_text: "Full Name"
                helper_text_mode: "on_focus"
                size_hint_y: None
                height: dp(60)
                mode: "rectangle"
                required: True

            MDTextField:
                id: username
                hint_text: "Username"
                helper_text_mode: "on_focus"
                size_hint_y: None
                height: dp(60)
                mode: "rectangle"
                required: True

            MDTextField:
                id: email
                hint_text: "Email"
                helper_text_mode: "on_focus"
                size_hint_y: None
                height: dp(60)
                mode: "rectangle"
                required: True

            # -------- Phone number + Country --------
            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(10)
                size_hint_y: None
                height: dp(60)

                MDTextField:
                    id: contact_number
                    hint_text: "Phone number"
                    text: app.selected_country_code + " "  # always show code
                    mode: "rectangle"
                    helper_text_mode: "on_focus"
                    required: True
                    multiline: False
                    input_filter: app.contact_input_filter
                    size_hint_x: 0.7
                    on_text:
                        app.update_contact_text(self)
                
                MDRaisedButton:
                    id: country_btn
                    text: "Select Country Code"
                    size_hint_x: 0.3
            
                    pos_hint: {"center_y": 0.5}


            MDTextField:
                id: address_field
                hint_text: "Address"
                helper_text_mode: "on_focus"
                mode: "rectangle"
                size_hint_y: None
                height: dp(60)
                required: True

            MDTextField:
                id: signup_password
                hint_text: "Password"
                helper_text_mode: "on_focus"
                password: True
                mode: "rectangle"
                size_hint_y: None
                height: dp(60)
                required: True

            MDTextField:
                id: signup_repeat
                hint_text: "Repeat Password"
                helper_text_mode: "on_focus"
                password: True
                mode: "rectangle"
                size_hint_y: None
                height: dp(60)
                required: True

            MDRaisedButton:
                text: "Create Account"
                md_bg_color: app.MAROON_COLOR
                size_hint_y: None
                height: dp(50)
                on_release: app.create_account(full_name.text, username.text, email.text, contact_number.text, address_field.text, signup_password.text, signup_repeat.text)

            MDTextButton:
                text: "Back to Login"
                theme_text_color: "Custom"
                text_color: app.MAROON_COLOR
                halign: "center"
                size_hint_y: None
                height: dp(20)
                on_release: app.root.current = "login"

# ---------------- Forgot Password Screen ----------------
<ForgotPasswordScreen>:
    name: "forgot_password"

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(30)
        spacing: dp(15)
        md_bg_color: 1, 1, 1, 1

        MDLabel:
            text: "FORGOT PASSWORD"
            font_style: "H5"
            halign: "center"
            theme_text_color: "Custom"
            text_color: app.MAROON_COLOR

        MDLabel:
            text: "Enter your registered email address to reset your password."
            font_style: "Caption"
            halign: "center"
            theme_text_color: "Secondary"

        MDTextField:
            id: fp_email
            hint_text: "Email Address"
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            icon_left: "email"
            icon_left_color: app.MAROON_COLOR

        MDRaisedButton:
            text: "Reset Password"
            md_bg_color: app.MAROON_COLOR
            size_hint_y: None
            height: dp(50)
            on_release: app.reset_password(fp_email.text)

        MDTextButton:
            text: "Back to Login"
            theme_text_color: "Custom"
            text_color: app.MAROON_COLOR
            halign: "center"
            size_hint_y: None
            height: dp(20)
            on_release: app.root.current = "login"

<MainScreen>:
    name: "main"

    BoxLayout:
        orientation: "vertical"

        # Top bar
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 10
            padding: 10
            canvas.before:
                Color:
                    rgba: 1,1,1,1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: "≡"
                size_hint_x: None
                width: 50
                background_normal: ""
                background_color: 0,0,0,0
                font_size: 24
                color: 0,0,0,1
                on_release: root.toggle_dashboard()

            Label:
                text: "Dashboard"
                font_size: 20
                color: 0,0,0,1
                halign: "left"
                valign: "middle"
                text_size: self.size

        # Map area
        FloatLayout:
            id: map_region
            size_hint_y: 0.5
            canvas.before:
                Color:
                    rgba: 0,0,0,0
                Rectangle:
                    pos: self.pos
                    size: self.size

            MapView:
                id: map_widget
                lat: root.current_lat
                lon: root.current_lon
                zoom: 12
                size_hint: 1, 1
                pos_hint: {"x":0, "y":0}

            # Search bar inside map
            MDTextField:
                id: search_field
                hint_text: "Search location or category"
                size_hint_x: 0.6
                size_hint_y: None
                height: 40
                pos_hint: {"x":0.05, "top":0.95}
                on_text_validate: root.on_search_entered(self)

            BoxLayout:
                id: suggestions_box
                orientation: "vertical"
                size_hint: 0.6, None
                height: 150
                pos_hint: {"x":0.05, "top":0.9}

            Button:
                text: "Update"
                size_hint: None, None
                size: 85, 38
                pos_hint: {"right": 0.98, "top": 0.98}
                background_color: 0,0,0,0            
                background_normal: ''
                background_down: ''
                canvas.before:
                    Color:
                        rgba: 0.5, 0.0, 0.0, 1      
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10]                 
                color: 1, 1, 1, 1
                on_release: root.open_map_editor()

        # One Tap + Spam Detector
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: 160
            padding: 10
            spacing: 10

            BoxLayout:
                orientation: "vertical"
                padding: 10
                spacing: 10
                canvas.before:
                    Color:
                        rgba: 1,1,1,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20]

                Label:
                    text: "One Tap Emergency"
                    size_hint_y: None
                    height: 25
                    font_size: 14
                    color: 0,0,0,1

                FloatLayout:
                    Button:
                        text: ""
                        size_hint: None, None
                        size: 70, 70
                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                        background_normal: ""
                        background_color: 1, 0, 0, 1
                        on_release: root.on_sos_pressed("ONE TAP EMERGENCY")
                        canvas.before:
                            Color:
                                rgba: 1,0,0,1
                            Ellipse:
                                pos: self.pos
                                size: self.size

            BoxLayout:
                id: spam_placeholder
                orientation: "vertical"
                padding: 5
                spacing: 10
                canvas.before:
                    Color:
                        rgba: 0.3, 0.5, 1, 1  
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20]

                # ------- HEADER -------
                Label:
                    id: header
                    text: "Spam: 0 | Threats: 0"
                    size_hint_y: None
                    height: 40
                    font_size: 18
                    bold: True
                    color: 0,0,0,1
                    on_touch_down:
                        if self.collide_point(*args[1].pos): app.root.get_screen('main').on_header_click()

                # ------- BUTTON TO SPAM DETAIL -------
                Button:
                    text: "Open Spam Details"
                    size_hint_y: None
                    height: dp(40)
                    background_normal: ""
                    background_color: 0, 0.3, 0.6, 1
                    color: 1,1,1,1
                    on_release: app.root.current = "spam"

                # ------- LIST SCROLLVIEW -------
                ScrollView:
                    bar_width: 6
                    GridLayout:
                        id: full_list
                        cols: 1
                        size_hint_y: None
                        height: self.minimum_height
                        row_default_height: 35
                        spacing: 7

        # SOS Categories
        GridLayout:
            cols: 2
            size_hint_y: None
            height: 130
            padding: 10
            spacing: 10

            Button:
                text: "THREATS"
                background_normal: ""
                background_color: 0,0.6,0,1
                on_release: root.on_sos_pressed("THREATS")

            Button:
                text: "ACCIDENTS"
                background_normal: ""
                background_color: 0,0.6,0,1
                on_release: root.on_sos_pressed("ACCIDENTS")

            Button:
                text: "FIRE"
                background_normal: ""
                background_color: 0,0.6,0,1
                on_release: root.on_sos_pressed("FIRE")

            Button:
                text: "MEDICAL"
                background_normal: ""
                background_color: 0,0.6,0,1
                on_release: root.on_sos_pressed("MEDICAL")

    # Side Dashboard (hidden by default)
    BoxLayout:
        id: dashboard_menu
        orientation: "vertical"
        size_hint: None, 1
        width: 0
        pos_hint: {"x": -1}
        padding: 10
        spacing: 10
        canvas.before:
            Color:
                rgba: 1,1,1,1
            Rectangle:
                pos: self.pos
                size: self.size

        Button:
            text: "Contacts"
            size_hint_y: None
            height: 40
            background_color: 0,0,0,0            
            background_normal: ''
            background_down: ''
            canvas.before:
                Color:
                    rgba: 0.5, 0.0, 0.0, 1      
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10]                 
            color: 1, 1, 1, 1
            on_release: root.open_contacts()
            

        Button:
            text: "Profile"
            size_hint_y: None
            height: 40
            background_color: 0,0,0,0            
            background_normal: ''
            background_down: ''
            canvas.before:
                Color:
                    rgba: 0.5, 0.0, 0.0, 1      
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10]                 
            color: 1, 1, 1, 1
            on_release: root.open_profile()

        Button:
            text: "Settings"
            size_hint_y: None
            height: 40
            background_color: 0,0,0,0            
            background_normal: ''
            background_down: ''
            canvas.before:
                Color:
                    rgba: 0.5, 0.0, 0.0, 1      
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10]                 
            color: 1, 1, 1, 1
            on_release: root.open_settings()

        Button:
            text: "Help"
            size_hint_y: None
            height: 40
            background_color: 0,0,0,0            
            background_normal: ''
            background_down: ''
            canvas.before:
                Color:
                    rgba: 0.5, 0.0, 0.0, 1      
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10]                 
            color: 1, 1, 1, 1
            on_release: root.open_help()

<ContactsScreen>:
    name: "contacts"

    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(5)
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        # Top Bar
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(5)

            MDRaisedButton:
                text: "← Back"
                size_hint_x: None
                width: dp(80)
                on_release: app.root.current = "main"

            Label:
                text: "[b]CONTACT MANAGER[/b]"
                markup: True
                color: 1,1,1,1
                halign: "center"

        # Categories Header with Add/Delete
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(5)

            Label:
                text: "[b]CONTACT CATEGORIES[/b]"
                markup: True
                color: 1,1,1,1
                halign: "left"

            Button:
                id: add_contact_btn
                text: "Add Contact"
                size_hint_x: None
                width: dp(120)
                background_color: 1,0,0,1
                color: 1,1,1,1
                on_release: root.show_add_form()

            Button:
                text: "-"
                size_hint_x: None
                width: dp(50)
                background_color: 1,0,0,1
                color: 1,1,1,1
                on_release: root.delete_saved_contact()

        # Categories Grid
        GridLayout:
            id: cat_layout
            cols: 2
            spacing: dp(5)
            size_hint_y: None
            height: self.minimum_height
            padding: dp(5)
            canvas.before:
                Color:
                    rgba: 0.5,0,0,1
                Rectangle:
                    pos: self.pos
                    size: self.size

        # Separator
        Widget:
            size_hint_y: None
            height: dp(2)
            canvas.before:
                Color:
                    rgba: 1,0,0,1
                Rectangle:
                    pos: self.pos
                    size: self.size

        # Scrollable Contact List
        ScrollView:
            size_hint_y: 1
            do_scroll_x: False

            GridLayout:
                id: contacts_grid
                cols: 1
                spacing: dp(5)
                size_hint_y: None
                height: self.minimum_height
                padding: dp(5)

        # Add Contact Form (hidden by default)
        BoxLayout:
            id: add_form
            orientation: "vertical"
            size_hint_y: None
            height: dp(200)
            spacing: dp(5)
            padding: dp(5)
            opacity: 0
            disabled: True
            canvas.before:
                Color:
                    rgba: 0.2,0,0,1
                Rectangle:
                    pos: self.pos
                    size: self.size

            # Name Input
            TextInput:
                id: name_input
                hint_text: "Name"
                size_hint_y: None
                height: dp(40)
                background_color: 1,1,1,1
                foreground_color: 0,0,0,1

            # Phone Input
            TextInput:
                id: phone_input
                hint_text: "Phone Number"
                input_filter: "int"
                size_hint_y: None
                height: dp(40)
                background_color: 1,1,1,1
                foreground_color: 0,0,0,1

            # Category Selection (Checkboxes)
            GridLayout:
                id: add_cat_grid
                cols: 2
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(5)

            # Add / Clear / Back Buttons
            BoxLayout:
                size_hint_y: None
                height: dp(40)
                spacing: dp(5)

                Button:
                    text: "Add Contact"
                    size_hint_x: None
                    width: dp(120)
                    background_color: 1,0,0,1
                    color: 1,1,1,1
                    on_release: root.add_or_update_contact()

                Button:
                    text: "Clear"
                    background_color: 0.5,0,0,1
                    color: 1,1,1,1
                    on_release: root.clear_fields()

                Button:
                    text: "Back"
                    background_color: 0.2,0,0,1
                    color: 1,1,1,1
                    size_hint_x: None
                    width: dp(80)
                    on_release: root.show_add_form()  # toggles form visibility



<SettingsScreen>:
    name: "settings"

    BoxLayout:
        orientation: "vertical"

        # Back button
        MDRaisedButton:
            text: "← Back"
            size_hint_y: None
            height: dp(40)
            on_release: app.root.current = "main"

        ScrollView:
            do_scroll_x: False

            MDBoxLayout:
                id: settings_layout
                orientation: "vertical"
                spacing: dp(20)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height

                # --- Activation Methods ---
                MDLabel:
                    text: "Activation Methods"
                    font_style: "H5"
                    halign: "left"

                # Shake Activation
                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(8)
                    size_hint_y: None
                    height: self.minimum_height

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(12)
                        size_hint_y: None
                        height: dp(35)

                        MDLabel:
                            text: "Shake Activation"
                        CheckBox:
                            id: shake_chk
                            on_active: root.toggle_shake_settings(self, self.active)

                    MDBoxLayout:
                        id: shake_settings_box
                        orientation: "vertical"
                        spacing: dp(5)
                        size_hint_y: None
                        height: 0
                        opacity: 0
                        disabled: True

                        MDLabel:
                            text: "Shake Sensitivity"
                        Slider:
                            id: shake_slider
                            min: 1
                            max: 10
                            step: 1
                            value: 5
                            size_hint_y: None
                            height: dp(50)
                            on_value: root.update_shake_sensitivity(self, self.value)

                # Voice Activation
                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(8)
                    size_hint_y: None
                    height: self.minimum_height

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(12)
                        size_hint_y: None
                        height: dp(35)

                        MDLabel:
                            text: "Voice Activation"
                        CheckBox:
                            id: voice_chk
                            on_active: root.toggle_voice_settings(self, self.active)

                    MDBoxLayout:
                        id: voice_settings_box
                        orientation: "vertical"
                        spacing: dp(5)
                        size_hint_y: None
                        height: 0
                        opacity: 0
                        disabled: True

                        MDLabel:
                            text: "Activation Phrase"
                        TextInput:
                            id: voice_input
                            multiline: False
                            size_hint_y: None
                            height: dp(45)
                            on_text: root.update_voice_phrase(self, self.text)

                        MDLabel:
                            text: "Voice Sensitivity"
                        Slider:
                            id: voice_slider
                            min: 1
                            max: 10
                            step: 1
                            value: 5
                            size_hint_y: None
                            height: dp(50)
                            on_value: root.update_voice_sensitivity(self, self.value)

                # --- Button Customization ---
                MDLabel:
                    text: "Button Customization"
                    font_style: "H5"
                    halign: "left"

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(8)
                    size_hint_y: None
                    height: self.minimum_height

                    # Floating Button
                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(12)
                        size_hint_y: None
                        height: dp(35)

                        MDLabel:
                            text: "Floating Button Enabled"
                        CheckBox:
                            id: floating_chk
                            on_active: root.toggle_floating_settings(self, self.active)

                    MDBoxLayout:
                        id: floating_size_box
                        orientation: "horizontal"
                        spacing: dp(12)
                        size_hint_y: None
                        height: 0
                        opacity: 0
                        disabled: True

                        MDLabel:
                            text: "Button Size (1-100)"
                        TextInput:
                            id: size_input
                            multiline: False
                            height: dp(45)
                            on_text: root.update_floating_size(self, self.text)

                    # Lock Screen
                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(12)
                        size_hint_y: None
                        height: dp(35)

                        MDLabel:
                            text: "Lock Screen Activation"
                        CheckBox:
                            id: lock_chk

                # --- Security / Countdown ---
                MDLabel:
                    text: "Security / Countdown"
                    font_style: "H5"
                    halign: "left"

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(8)
                    size_hint_y: None
                    height: self.minimum_height

                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: dp(12)
                        size_hint_y: None
                        height: dp(35)

                        MDLabel:
                            text: "Enable Countdown"
                        CheckBox:
                            id: countdown_chk
                            on_active: root.toggle_countdown_settings(self, self.active)

                    MDBoxLayout:
                        id: countdown_input_box
                        orientation: "horizontal"
                        spacing: dp(12)
                        size_hint_y: None
                        height: 0
                        opacity: 0
                        disabled: True

                        MDLabel:
                            text: "Countdown Seconds"
                        TextInput:
                            id: countdown_input
                            multiline: False
                            height: dp(45)

                # Save Button
                MDRaisedButton:
                    text: "Save Settings"
                    size_hint_y: None
                    height: dp(55)
                    on_release: root.save_settings()

<SpamDetailScreen>:
    name: "spam"

    BoxLayout:
        orientation: "vertical"
        spacing: dp(5)
        padding: dp(10)

        # ----- Back Button -----
        MDRaisedButton:
            text: "← Back"
            size_hint_y: None
            height: dp(40)
            on_release: app.root.current = "main"

        # ----- Header -----
        Label:
            text: "SOS SMS DETECTOR"
            color: 0.5, 0, 0, 1  # Maroon
            bold: True
            font_size: dp(18)
            size_hint_y: None
            height: dp(40)
            halign: "center"
            valign: "middle"
            text_size: self.size

        # ----- Counters Row -----
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(10)

            Label:
                text: "SPAM: " + str(root.spam_count)
                color: 1, 0.9, 0, 1  # Yellow
                halign: "center"
                valign: "middle"
                text_size: self.size

            Label:
                text: "THREAT: " + str(root.threat_count)
                color: 1, 0.3, 0.3, 1  # Red
                halign: "center"
                valign: "middle"
                text_size: self.size

        # ----- Scrollable list of messages -----
        ScrollView:
            do_scroll_x: False

            BoxLayout:
                id: spam_container
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                padding: dp(5)

        # ----- Bottom buttons -----
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)

            Button:
                text: "Manage Keywords"
                on_release: root.show_keywords_popup()

            Button:
                text: "Block Spam: " + ("ON" if root.block_enabled else "OFF")
                on_release: root.toggle_block(self)

# ----- Style for individual spam/threat messages -----
<SpamMessageButton@Button>:
    size_hint_y: None
    height: dp(60)
    background_normal: ""
    background_color: (0.2, 0.2, 0.2, 1)
    color: 1,1,1,1
    bold: True
    text_size: self.width - dp(20), None
    halign: "left"
    valign: "middle"
    padding: dp(10), dp(10)
    canvas.before:
        Color:
            rgba: self.bg_color if hasattr(self, "bg_color") else self.background_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
 
<MapEditorScreen>:
    name: "map_editor"
    FloatLayout:

        # ----- MapView as background -----
        MapView:
            id: editor_map
            zoom: 12
            lat: 14.5995
            lon: 120.9842
            size_hint: 1, 1
            pos_hint: {"x":0, "y":0}

        # ----- Back Button (top-left) -----
        MDRaisedButton:
            text: "← Back"
            size_hint: None, None
            size: 100, 40
            pos_hint: {"x":0.05, "top":0.98}
            on_release: app.root.current = "main"

        # ----- Search Bar (below Back Button) -----
        MDTextField:
            id: search_field_editor
            hint_text: "Search location or category"
            size_hint_x: 0.6
            size_hint_y: None
            height: 40
            pos_hint: {"x":0.05, "top":0.90}  # slightly below back button
            on_text_validate: root.on_search_entered(self)

        # ----- Suggestions box floating below search bar -----
        BoxLayout:
            id: suggestions_box_editor
            orientation: "vertical"
            size_hint: 0.6, None
            height: 150
            pos_hint: {"x":0.05, "top":0.84}

        # ----- Save Changes button (bottom-right) -----
        Button:
            text: "Save Changes"
            size_hint: None, None
            size: 120, 40
            pos_hint: {"right":0.98, "y":0.02}
            background_color: 0, 0.6, 0, 1
            on_release: root.save_temp_changes()

<ProfileScreen>:
    name: "profile"
    user_data: root.user_data

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(30)
        spacing: dp(20)
        md_bg_color: 1, 1, 1, 1  # White background

                # Back button
        MDRaisedButton:
            text: "← Back"
            size_hint_y: None
            height: dp(40)
            on_release: app.root.current = "main"

        MDLabel:
            text: "USER PROFILE"
            font_style: "H5"
            halign: "center"
            theme_text_color: "Custom"
            text_color: app.MAROON_COLOR

        MDTextField:
            id: profile_name
            hint_text: "Full Name"
            text: ""  # leave empty
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            cursor_color: app.MAROON_COLOR
            readonly: True
            on_focus: root.ask_edit(self, "name") if self.focus else None
            on_text_validate: root.ask_save(self, "name")

        MDTextField:
            id: profile_contact
            hint_text: "Contact Number"
            text: ""  # leave empty
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            cursor_color: app.MAROON_COLOR
            readonly: True
            on_focus: root.ask_edit(self, "contact_number") if self.focus else None
            on_text_validate: root.ask_save(self, "contact_number")

        MDTextField:
            id: profile_location
            hint_text: "Location"
            text: ""  # leave empty
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

<HelpScreen>:
    name: "help"

    BoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        padding: dp(15)

                # Back button
        MDRaisedButton:
            text: "← Back"
            size_hint_y: None
            height: dp(40)
            on_release: app.root.current = "main"

        # ---------------- SEARCH BAR ----------------
        TextInput:
            id: search_bar
            hint_text: "What are you looking for?"
            size_hint_y: None
            height: dp(45)
            multiline: False
            focus: True                         # ★ allows typing
            write_tab: False                    # ★ prevents tab from blocking input
            on_text: root.filter_faqs(self.text)
            background_normal: ""
            background_color: 1, 1, 1, 1
            foreground_color: 0, 0, 0, 1
            padding: dp(10), dp(10)

        # ---------------- TITLE ----------------
        Label:
            text: "[b]HELP FAQ[/b]"
            markup: True
            color: 0, 0, 0, 1
            size_hint_y: None
            height: dp(40)
            halign: "center"
            valign: "middle"
            text_size: self.size

        # ---------------- SCROLL AREA ----------------
        ScrollView:
            do_scroll_x: False

            BoxLayout:
                id: faq_list_container
                orientation: "vertical"
                size_hint_y: None
                spacing: dp(10)
                padding: dp(10)
                height: self.minimum_height


'''

class LoginApp(MDApp):
    current_user = None
    MAROON_COLOR = (0.5, 0.0, 0.0, 1)
    selected_country_code = "+63"

    def login_user(self, username, password):
        if not username or not password:
            self.show_message("Please enter both username and password")
            return

        accounts = load_accounts()
        user_data = accounts.get(username)

        if user_data and user_data.get('password') == password:
            self.current_user_data = user_data  # <-- store current user
            self.show_message(f"Welcome back, {user_data.get('full name')}!")
            self.root.current = "main"
        else:
            self.login_attempts += 1
            if self.login_attempts >= 3:
                self.show_forgot_password_dialog()
            else:
                self.show_message("Invalid username or password")


    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.primary_hue = "800"
        self.theme_cls.theme_style = "Light"
        self.login_attempts = 0

        self.screen_manager = Builder.load_string(KV)

        # Setup country dropdown
        self.country_dropdown = DropDown()
        for country in COUNTRY_CODES:
            btn = Button(
                text=f"{country['code']} | {country['name']}",
                size_hint_y=None,
                height=dp(40)
            )
            btn.bind(on_release=lambda btn, c=country['code']: self.select_country_code(c))
            self.country_dropdown.add_widget(btn)

        return self.screen_manager  # <--- THIS IS CRUCIAL

# ---------------- Country Code Selection ----------------
    def on_start(self):
        """Bind dropdown button after root is ready."""
        signup_screen = self.root.get_screen("signup")

        # Open dropdown when country button is clicked
        signup_screen.ids.country_btn.bind(on_release=self.country_dropdown.open)

        # Prefill contact field with default code
        contact_field = signup_screen.ids.contact_number
        contact_field.text = self.selected_country_code + " "
        contact_field.cursor = (len(contact_field.text), 0)  # place cursor at end

    def select_country_code(self, code):
        """Called when a country is selected from dropdown."""
        self.selected_country_code = code
        signup_screen = self.root.get_screen("signup")
        contact_field = signup_screen.ids.contact_number

        # Keep only the local number part
        local_number = contact_field.text.split(" ", 1)[-1] if " " in contact_field.text else ""
        contact_field.text = f"{code} {local_number}"
        contact_field.cursor = (len(contact_field.text), 0)
        self.country_dropdown.dismiss()

    def is_valid_contact(self, contact):
        for code in [c['code'] for c in COUNTRY_CODES]:
            if contact.startswith(code):
                local_number = contact[len(code):].strip()
                return local_number.isdigit() and 7 <= len(local_number) <= 12
        return False
    
    # Prevent editing the +country_code part
    def contact_input_filter(self, text, from_undo):
        """
        Only allow digits after the country code.
        """
        if text.isdigit():
            return text
        return ""
    
    def update_contact_text(self, field):
        """
        Ensure only one country code exists, local number is editable, max length enforced.
        """
        code = self.selected_country_code

        # Remove code and spaces to get only local number
        text = field.text.strip()
        if text.startswith(code):
            local_number = text[len(code):].strip()
        else:
            local_number = text

        # Limit local number to max allowed for the country
        max_len = next((c["number_length"] for c in COUNTRY_CODES if c["code"] == code), 10)
        local_number = ''.join(filter(str.isdigit, local_number))[:max_len]

        # Set text: only one code at start + local number
        field.text = f"{code} {local_number}"

        # Move cursor to end
        field.cursor = (len(field.text), 0)


    # --- New Function for Password Visibility Toggle ---
    def toggle_password_visibility(self, instance, touch):
        """
        Handles the on_touch_down event for the password field to toggle
        password visibility only if the touch is on the right icon.
        """
        icon_size = dp(48)
        
        # Check if the touch is within the MDTextField bounds AND within the icon area
        if instance.collide_point(*touch.pos) and (touch.pos[0] > instance.x + instance.width - icon_size):
            instance.password = not instance.password
            instance.icon_right = 'eye' if not instance.password else 'eye-off'
            return True 
        return False

    # --- Functions ---
    def create_account(self, full_name, username, email, contact, address, password, repeat):
        if not all([full_name, username, email, contact, address, password, repeat]):
            self.show_message("All fields are required")
            return
        if password != repeat:
            self.show_message("Passwords do not match")
            return

        accounts = load_accounts()
        if username in accounts:
            self.show_message("Username already exists")
            return

        if "@" not in email or "." not in email:
            self.show_message("Please enter a valid email address.")
            return

        if not contact.startswith("+") or not self.is_valid_contact(contact):
            return

        # Check if email or contact already registered
        for user_data in accounts.values():
            if user_data.get('email', '').lower() == email.lower():
                self.show_message("Email already registered with another account.")
                return
            if user_data.get('contact_number', '') == contact:
                self.show_message("Contact number already registered with another account.")
                return

        # Store the full user profile
        accounts[username] = {
            'full name': full_name,
            'email': email,
            'contact_number': contact,
            'location': address,
            'password': password
        }

        save_accounts(accounts)
        self.show_message("Account created successfully. You can now log in.")
        self.root.current = "login"

    def show_message(self, message):
        """Displays a simple dialog message."""
        dialog = MDDialog(text=message, size_hint=(0.8, None), height=dp(100))
        dialog.open()

    def show_forgot_password_dialog(self):
        """Displays a dialog with the option to reset password after 2 failures."""
        self.login_attempts = 0 
        
        def go_to_forgot_password(instance):
            self.dialog.dismiss()
            self.root.current = "forgot_password"
            
        def close_dialog(instance):
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Login Failed",
            text="You have entered incorrect credentials multiple times. Would you like to reset your password?",
            buttons=[
                MDTextButton(text="CANCEL", on_release=close_dialog),
                MDRaisedButton(text="RESET PASSWORD", on_release=go_to_forgot_password, md_bg_color=self.MAROON_COLOR),
            ],
            size_hint=(0.8, None)
        )
        self.dialog.open()

    def login_success(self, user_data):
        # Example user_data contains: {"username": "...", "contact": "+639123456789"}

        from kivy.app import App
        app = App.get_running_app()

        # Store logged in user's phone/contact number
        app.current_user_contact = user_data["contact"]

        # Redirect to main screen
        self.manager.current = "MainScreen"


    def reset_password(self, email):
        """Handles password reset logic based on email."""
        accounts = load_accounts()
        
        # Function to find username associated with the email
        def get_username_by_email(email_to_find, accounts_data):
            for username, user_data in accounts_data.items():
                if user_data.get('email', '').lower() == email_to_find.lower():
                    return username
            return None

        username = get_username_by_email(email, accounts)

        if username:
            self.show_message(f"Password reset initiated for {email}. A reset link has been sent (placeholder action).")
            self.root.current = "login"
        else:
            self.show_message("Email address not found. Please try again or sign up.")
        
        # Clear the field. Note: The ID is now fp_email
        self.root.get_screen('forgot_password').ids.fp_email.text = ''

    def open_main_app(self):
        self.show_message("Successfully logged in.")


class MainScreen(Screen):
    pass

class ContactsScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class MapEditorScreen(Screen):
    pass
 
class ProfileScreen(Screen):
    
    pass

class SpamScreen(Screen): 
    pass

if __name__ == "__main__":
    LoginApp().run()