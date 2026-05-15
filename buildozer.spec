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

# Robotun tam olarak istediği, uyuşmazlıkları bitiren altın kombinasyon:
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
