import sys, platform, json, os

IS_ANDROID = platform.system() == "Linux" and "ANDROID_ARGUMENT" in sys.argv
IS_WINDOWS = platform.system() == "Windows"

# -------------------- GLOBALS --------------------
floating_btn = None      # Kivy button (Windows/Desktop)
layout = None            # Kivy FloatLayout
android_btn = None       # Android overlay button
wm = None                # Android WindowManager

# -------------------- ANDROID OVERLAY --------------------
if IS_ANDROID:
    from jnius import autoclass, cast
    from android import activity

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    WindowManagerLayoutParams = autoclass('android.view.WindowManager$LayoutParams')
    Button = autoclass('android.widget.Button')
    Gravity = autoclass('android.view.Gravity')
    PixelFormat = autoclass('android.graphics.PixelFormat')

    activity = PythonActivity.mActivity
    wm = cast('android.view.WindowManager', activity.getSystemService(Context.WINDOW_SERVICE))

# -------------------- SMS SENDING --------------------
def send_sms(number, message):
    """Send SMS to a phone number. Works on Android only; prints on Windows."""
    if IS_ANDROID:
        try:
            from jnius import autoclass
            SmsManager = autoclass("android.telephony.SmsManager").getDefault()
            SmsManager.sendTextMessage(number, None, message, None, None)
            print(f"SMS sent to {number}")
        except Exception as e:
            print(f"Failed to send SMS to {number}: {e}")
    else:
        print(f"[SIMULATION] SMS to {number}: {message}")

# -------------------- LOCATION FETCHING --------------------
def fetch_current_location(callback=None):
    if IS_ANDROID:
        try:
            from plyer import gps

            def on_location(**kwargs):
                lat = kwargs.get("lat")
                lon = kwargs.get("lon")
                if callback and lat and lon:
                    callback(lat, lon)

            gps.configure(on_location=on_location)
            gps.start(minTime=1000, minDistance=1)

        except Exception as e:
            print("Android GPS error:", e)
            if callback: callback(None, None)
    elif IS_WINDOWS:
        try:
            import geocoder
            g = geocoder.ip("me")
            if g.ok:
                lat, lon = g.latlng
                if callback: callback(lat, lon)
            else:
                if callback: callback(None, None)
        except:
            if callback: callback(None, None)

# -------------------- CONTACTS --------------------
def fetch_contacts():
    path = "contacts.json"
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def fetch_one_tap_emergency(contacts_list=None):
    if contacts_list is None: contacts_list = fetch_contacts()
    return [c for c in contacts_list if "ONE TAP EMERGENCY" in c.get("categories", [])]

def send_sos_message(contacts_list=None):
    def send(lat, lon):
        message = f"SOS! My location: {lat},{lon}" if lat and lon else "SOS! Location unknown."
        for c in fetch_one_tap_emergency(contacts_list):
            send_sms(c["phone"], message)
    fetch_current_location(send)

# -------------------- FLOATING BUTTON --------------------
def enable_floating(size=80, callback=None):
    """Create floating button on Android overlay or Windows Kivy window."""
    global floating_btn, layout, android_btn, wm

    # ----- Android Overlay -----
    if IS_ANDROID:
        if android_btn is None:
            android_btn = Button(activity)
            android_btn.setText("SOS")
            android_btn.setBackgroundColor(0xFFFF0000)

            # Layout params
            params = WindowManagerLayoutParams(
                size, size,
                WindowManagerLayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManagerLayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT
            )
            params.gravity = Gravity.TOP | Gravity.LEFT
            params.x = 100
            params.y = 300
            wm.addView(android_btn, params)

            # Click listener
            class ClickListener(autoclass('android.view.View$OnClickListener')):
                def onClick(self, v):
                    print("SOS pressed!")
                    if callback: callback()
            android_btn.setOnClickListener(ClickListener())

            # ----------------- Drag listener -----------------
            MotionEvent = autoclass('android.view.MotionEvent')

            class DragListener(autoclass('android.view.View$OnTouchListener')):
                def __init__(self):
                    super().__init__()
                    self.startX = 0
                    self.startY = 0
                    self.origX = 0
                    self.origY = 0

                def onTouch(self, v, event):
                    action = event.getAction()
                    if action == MotionEvent.ACTION_DOWN:
                        self.startX = event.getRawX()
                        self.startY = event.getRawY()
                        self.origX = params.x
                        self.origY = params.y
                        return True
                    elif action == MotionEvent.ACTION_MOVE:
                        dx = int(event.getRawX() - self.startX)
                        dy = int(event.getRawY() - self.startY)
                        params.x = self.origX + dx
                        params.y = self.origY + dy
                        wm.updateViewLayout(android_btn, params)
                        return True
                    return False

            android_btn.setOnTouchListener(DragListener())

        return


    # ----- Windows/Desktop -----
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.button import Button as KivyButton

    if layout is None:
        layout = FloatLayout()

    if floating_btn is None:
        floating_btn = KivyButton(
            text="SOS",
            size_hint=(None, None),
            size=(size, size),
            pos=(10, 10),
            background_color=(1, 0, 0, 1)
        )
        floating_btn.bind(on_press=lambda i: on_click(callback))
        floating_btn.bind(on_touch_move=drag_button)
        layout.add_widget(floating_btn)
    else:
        floating_btn.size = (size, size)
        floating_btn.opacity = 1

def disable_floating():
    global floating_btn, android_btn, wm
    if IS_ANDROID and android_btn and wm:
        try:
            wm.removeView(android_btn)
            android_btn = None
        except: pass
    if floating_btn: floating_btn.opacity = 0

# -------------------- EVENT HANDLERS --------------------
def drag_button(instance, touch):
    if instance.collide_point(*touch.pos):
        instance.pos = (touch.x - instance.width/2, touch.y - instance.height/2)

def on_click(callback):
    print("SOS pressed!")
    if callback: callback()

# -------------------- TEST APP --------------------
if __name__ == "__main__":
    from kivy.app import App

    class TestApp(App):
        def build(self):
            def sos(): send_sos_message()

            enable_floating(90, callback=sos)
            fetch_current_location(lambda lat, lon: print("Your location:", lat, lon))
            return layout

    TestApp().run()
