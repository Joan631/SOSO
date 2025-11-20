
# Python requirements
requirements = python3,kivy,plyer,pyjnius,android

# Android permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,SEND_SMS,VIBRATE,WAKE_LOCK

# Services (for background operation)
services = ShakeVoiceService:shake_voice_service.py

# Keep app running in background
android.wakelock = True

# API level
android.api = 31
android.minapi = 21
android.ndk = 25b
