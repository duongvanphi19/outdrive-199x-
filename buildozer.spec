[app]
title = Outdrive 199X
package.name = outdrive199x
package.domain = com.phiduong
source.dir = .
source.include_exts = py,png,jpg,ttf,json,ogg
version = 1.0
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
presplash.color = #0e0c1c
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,CHANGE_WIFI_MULTICAST_STATE
requirements = python3,pygame==2.1.2
orientation = landscape
fullscreen = 1
android.archs = arm64-v8a
android.accept_sdk_license = True
android.ndk = 25b
p4a.branch = v2023.09.16

