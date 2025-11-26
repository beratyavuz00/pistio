[app]

# (str) Oyunun başlığı
title = Acik Pisti

# (str) Paket ismi (boşluksuz, küçük harf)
package.name = acikpisti

# (str) Paket domaini (benzersiz olması için kendi adını yazabilirsin)
package.domain = org.pisti

# (str) Kaynak dosyaların olduğu yer
source.dir = .

# (list) Kaynak uzantıları
source.include_exts = py,png,jpg,kv,atlas

# (list) Uygulamanın çalışması için gerekenler (ÇOK ÖNEMLİ)
requirements = python3,kivy,flet

# (str) Versiyon
version = 0.1

# (list) Android izinleri (Flet için internet izni genelde iyidir)
android.permissions = INTERNET

# (int) Hedef Android API (33 = Android 13)
android.api = 33

# (int) Minimum API
android.minapi = 21

# (bool) Android logcat'i göster (Hata ayıklama için)
android.logcat_filters = *:S python:D

# (str) Ekran yönü (portrait, landscape, sensor...)
orientation = portrait

# (bool) Tam ekran olsun mu?
fullscreen = 1

# (string) Presplash arka plan rengi (Açılış ekranı)
android.presplash_color = #1B5E20

[buildozer]

# (int) Log seviyesi (0-2)
log_level = 2

# (int) Paketleme sırasında uyarıları hata sayma
warn_on_root = 1
