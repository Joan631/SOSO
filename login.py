import json
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from google_auth_oauthlib.flow import InstalledAppFlow


ACCOUNTS_FILE = "accounts.json"
REMEMBER_FILE = "remember.json"
GOOGLE_CLIENT_SECRET = "client_secret.json"  # Your Google OAuth client secret

# ----------------- Helpers -----------------
def load_accounts():
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

def load_remembered():
    try:
        with open(REMEMBER_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_remembered(username):
    with open(REMEMBER_FILE, "w") as f:
        json.dump({"username": username}, f)


# ----------------- Screens -----------------
class LoginScreen(Screen):
    pass

class SignupScreen(Screen):
    pass

class MainScreen(Screen):
    pass


# ----------------- KV -----------------
KV = '''
ScreenManager:
    id: screen_manager

    LoginScreen:
        name: "login"

        BoxLayout:
            orientation: "vertical"
            padding: 50
            spacing: 20

            Image:
                source: "logo.png"
                size_hint: (1, 0.4)
                allow_stretch: True

            MDTextField:
                id: login_username
                hint_text: "Username"
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.8

            MDTextField:
                id: login_password
                hint_text: "Password"
                password: True
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.8

            MDCheckbox:
                id: remember_checkbox
                size_hint: None, None
                size: 48, 48
                pos_hint: {"center_x": 0.5}
            Label:
                text: "Remember Me"
                size_hint_y: None
                height: 30
                pos_hint: {"center_x": 0.5}

            MDRaisedButton:
                text: "Login"
                pos_hint: {"center_x": 0.5}
                on_release: app.login_user(login_username.text, login_password.text, remember_checkbox.active)

            MDRaisedButton:
                text: "Login with Google"
                pos_hint: {"center_x": 0.5}
                on_release: app.google_login_button()

            MDRaisedButton:
                text: "Sign Up"
                pos_hint: {"center_x": 0.5}
                on_release: screen_manager.current = "signup"

    SignupScreen:
        name: "signup"

        BoxLayout:
            orientation: "vertical"
            padding: 50
            spacing: 20

            MDTextField:
                id: signup_name
                hint_text: "First Name"
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.8

            MDTextField:
                id: signup_lastname
                hint_text: "Last Name"
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.8

            MDTextField:
                id: signup_email
                hint_text: "Email"
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.8

            MDTextField:
                id: signup_username
                hint_text: "Username"
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.8

            MDTextField:
                id: signup_password
                hint_text: "Password"
                password: True
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.8

            MDTextField:
                id: signup_repeat
                hint_text: "Repeat Password"
                password: True
                pos_hint: {"center_x": 0.5}
                size_hint_x: 0.8

            MDRaisedButton:
                text: "Create Account"
                pos_hint: {"center_x": 0.5}
                on_release: app.create_account(signup_name.text, signup_lastname.text, signup_email.text, signup_username.text, signup_password.text, signup_repeat.text)

            MDRaisedButton:
                text: "Back to Login"
                pos_hint: {"center_x": 0.5}
                on_release: screen_manager.current = "login"

    MainScreen:
        name: "main"

        BoxLayout:
            orientation: "vertical"
            Label:
                text: "Welcome to Main Dashboard"
'''

# ----------------- App -----------------
class LoginApp(MDApp):
    def build(self):
        screen = Builder.load_string(KV)

        # Load remembered username
        remembered = load_remembered()
        if remembered:
            screen.get_screen("login").ids.login_username.text = remembered.get("username", "")
            screen.get_screen("login").ids.remember_checkbox.active = True

        return screen

    # ----------------- Functions -----------------
    def login_user(self, username, password, remember):
        accounts = load_accounts()
        if username in accounts and accounts[username] == password:
            if remember:
                save_remembered(username)
            else:
                save_remembered("")  # Clear remembered account
            self.root.current = "main"
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

        accounts[username] = password
        save_accounts(accounts)
        self.show_message("Account created successfully")
        self.root.current = "login"

    def google_login_button(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CLIENT_SECRET,
                scopes=['openid', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']
            )
            creds = flow.run_local_server(port=0)
            # creds.id_token contains the user's Google account info
            print("Google login successful:", creds.id_token)
            self.root.current = "main"
        except Exception as e:
            self.show_message(f"Google login failed: {e}")

    def show_message(self, message):
        dialog = MDDialog(text=message, size_hint=(0.8, None), height=100)
        dialog.open()


if __name__ == "__main__":
    LoginApp().run()
