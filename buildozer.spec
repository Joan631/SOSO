[app]

# (str) Title of your application
title = SOSO

# (str) Package name
package.name = soso

# (str) Package domain (change to your own)
package.domain = org.example

# (str) Source code file to use as main entry point
source.include_exts = py,png,jpg,kv,json,ttf

# (list) Source files to include (optional)
source.include_patterns = img/*,fonts/*

# (str) Application version
version = 1.0.0

# (str) Application icon
icon.filename = img/logo.png

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (list) List of dependencies to install with pip
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,plyer,pyjnius,mapview,vosk

# (bool) Indicate if the app should be fullscreen
fullscreen = 1

# (str) Android API level
android.api = 33

# (int) Minimum API your app supports
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (int) NDK version to use
android.ndk = 25b

# (str) Presplash image (optional)
presplash.filename = img/logo.png

# (str) Android permissions
android.permissions = \
    INTERNET, \
    ACCESS_FINE_LOCATION, \
    ACCESS_COARSE_LOCATION, \
    ACCESS_NETWORK_STATE, \
    VIBRATE, \
    SEND_SMS, \
    READ_SMS, \
    RECEIVE_SMS, \
    RECORD_AUDIO, \
    WAKE_LOCK

# (bool) Permissions request at runtime
android.permissions_request = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (list) Orientation support
android.orientation = portrait

# (str) Additional source folders
android.add_src = 

# (bool) Whether to copy assets into the APK
android.copy_assets = True

# (str) Application data storage path
android.private_storage = True

# (str) Supported Android architectures
android.arch = armeabi-v7a, arm64-v8a

# (bool) Use SDL2 bootstrap
android.bootstrap = sdl2

# (str) Screen density
android.screen_density = 480

# (bool) Enable Android Kivy keyboard
android.kivy_keyboard = 1

# (list) Android additional Java classes (if any)
android.add_jars = 

# (str) Presplash color
presplash.color = #7F0000

# (bool) Show splashscreen
android.show_splash_screen = True
