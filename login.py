import json
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDTextButton, MDRaisedButton
from kivy.metrics import dp 
from kivy.clock import Clock # <-- Needed for the 3-second delay
from kivy.uix.widget import Widget # Explicit import for Widget

# --- File Management ---
ACCOUNTS_FILE = "accounts.json"

def load_accounts():
    """Loads accounts from the JSON file."""
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        # Handles case where file exists but is empty/corrupt JSON
        return {}

def save_accounts(accounts):
    """Saves the current accounts dictionary to the JSON file."""
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=4)


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

# Define the template for the Loading Screen
<LoadingScreen>:
    name: "loading"
    
    MDBoxLayout:
        orientation: "vertical"
        halign: "center"
        valign: "center"
        md_bg_color: 1, 1, 1, 1  # White background
        spacing: dp(30)
        padding: dp(40) 
        
        # Spacer to help vertically center the logo and content
        Widget:
            size_hint_y: 0.1 

        FloatLayout:
            size_hint: (1, 1)
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Image:
                source: "img/logo.png.jpg" 
                size_hint: (None, None)
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

# Define the template for the Login Screen
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


# Define the template for the Signup Screen
<SignupScreen>:
    name: "signup"
    
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(50)
        spacing: dp(15) 
        
        MDLabel:
            text: "CREATE ACCOUNT"
            font_style: 'H5'
            halign: 'center'
            color: app.MAROON_COLOR
        
        MDTextField:
            id: signup_name
            hint_text: "First Name"
            mode: "rectangle"

        MDTextField:
            id: signup_lastname
            hint_text: "Last Name"
            mode: "rectangle"

        MDTextField:
            id: signup_email
            hint_text: "Email"
            mode: "rectangle"

        MDTextField:
            id: signup_username
            hint_text: "Username"
            mode: "rectangle"

        MDTextField:
            id: signup_password
            hint_text: "Password"
            password: True
            mode: "rectangle"

        MDTextField:
            id: signup_repeat
            hint_text: "Repeat Password"
            password: True
            mode: "rectangle"

        MDRaisedButton:
            text: "Create Account"
            md_bg_color: app.MAROON_COLOR
            size_hint_x: 1
            height: dp(50)
            on_release: app.create_account(signup_name.text, signup_lastname.text, signup_email.text, signup_username.text, signup_password.text, signup_repeat.text)

        MDTextButton:
            text: "Back to Login"
            color: app.MAROON_COLOR
            halign: 'center'
            size_hint_y: None
            height: dp(20)
            on_release: app.root.current = "login"

# Define the template for the Forgot Password Screen
<ForgotPasswordScreen>:
    name: "forgot_password"
    
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(50)
        spacing: dp(20) 
        
        MDLabel:
            text: "FORGOT PASSWORD"
            font_style: 'H5'
            halign: 'center'
            color: app.MAROON_COLOR
        
        MDLabel:
            text: "Enter your registered email address to reset your password."
            font_style: 'Caption'
            halign: 'center'
            color: 0.3, 0.3, 0.3, 1 

        MDTextField:
            id: fp_email  # Changed ID from fp_username to fp_email
            hint_text: "Email Address" # Changed hint text
            mode: "rectangle"
            line_color_focus: app.MAROON_COLOR
            icon_left: "email" # Changed icon to reflect email
            icon_left_color: app.MAROON_COLOR

        MDRaisedButton:
            text: "Reset Password"
            md_bg_color: app.MAROON_COLOR
            size_hint_x: 1
            height: dp(50)
            on_release: app.reset_password(fp_email.text) # Changed to use fp_email ID

        MDTextButton:
            text: "Back to Login"
            color: app.MAROON_COLOR
            halign: 'center'
            size_hint_y: None
            height: dp(20)
            on_release: app.root.current = "login"
'''


# --- App Class and Logic ---
class LoginApp(MDApp):
    # Define the custom maroon color as a normalized RGB tuple (R, G, B, A)
    # This color is dark maroon/burgundy (Hex #800000).
    MAROON_COLOR = (0.5, 0.0, 0.0, 1) 

    def build(self):
        self.theme_cls.primary_palette = "Red" 
        self.theme_cls.primary_hue = "800"
        self.theme_cls.theme_style = "Light"
        self.login_attempts = 0 
        
        return Builder.load_string(KV)

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
    def login_user(self, username, password):
        accounts = load_accounts()
        
        # Check if the username exists and the stored dictionary contains the correct password
        if username in accounts and accounts[username].get('password') == password:
            self.login_attempts = 0
            self.root.get_screen('login').ids.login_username.text = ''
            self.root.get_screen('login').ids.login_password.text = ''
            # In a real app, this would switch to the main app screen
            self.show_message(f"Login successful for user: {username}!") 
        else:
            self.login_attempts += 1
            if self.login_attempts >= 2:
                self.show_forgot_password_dialog()
            else:
                self.show_message("Invalid username or password")

    def create_account(self, name, lastname, email, username, password, repeat):
        if not all([name, lastname, email, username, password, repeat]):
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

        # Check if email is already registered (Crucial for password reset by email)
        for user_data in accounts.values():
            if user_data.get('email', '').lower() == email.lower():
                self.show_message("Email already registered with another account.")
                return

        # Store the full user profile (required for email-based lookup)
        accounts[username] = {
            'name': name,
            'lastname': lastname,
            'email': email,
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


if __name__ == "__main__":
    LoginApp().run()
