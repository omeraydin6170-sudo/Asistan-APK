[app]
title = Asistan
package.name = asistanapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,requests,pyjnius
orientation = portrait
osx.kivy_version = 2.2.1
fullscreen = 0

# Hataları engelleyen en kararlı Android API ve NDK kombinasyonu:
android.api = 31
android.minapi = 21
android.ndk = 23b
android.archs = arm64-v8a
android.allow_backup = True
