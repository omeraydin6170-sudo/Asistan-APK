[app]
title = Asistan
package.name = asistanapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,requests
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
# Telefonun internete bağlanmasını sağlayan sihirli satır:
android.permissions = INTERNET
