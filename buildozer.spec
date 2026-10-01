[app]
title = Temuco Retira
package.name = temucoretira
package.domain = cl.temuco
source.dir = .
source.include_exts = py,db,png,jpg,jpeg
requirements = python3,kivy==2.3.0,kivymd==1.2.0
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 33
android.minapi = 21
android.accept_sdk_license = True