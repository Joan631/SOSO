import json
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp

ACCOUNTS_FILE = "accounts.json"

def load_accounts():
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=4)


# ----------------- Screens -----------------
class LoginScreen(Screen):
    pass

class SignupScreen(Screen):
    pass

class MainScreen(Screen):
    pass


# ----------------- App -----------------
KV = '''
ScreenManager:
    id: screen_manager

    Screen:
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

            MDRaisedButton:
                text: "Login"
                pos_hint: {"center_x": 0.5}
                on_release: app.login_user(login_username.text, login_password.text)

            MDRaisedButton:
                text: "Sign Up"
                pos_hint: {"center_x": 0.5}
                on_release: screen_manager.current = "signup"

    Screen:
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
'''

class LoginApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    # ----------------- Functions -----------------
    def login_user(self, username, password):
        accounts = load_accounts()
        if username in accounts and accounts[username] == password:
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

    def show_message(self, message):
        from kivymd.uix.dialog import MDDialog
        dialog = MDDialog(text=message, size_hint=(0.8, None), height=100)
        dialog.open()


if __name__ == "__main__":
    LoginApp().run()
