# Mayuri's Yarn Tales — Android app

A Flutter app for the shop. It shows the same products as the website by
reading the live `index.html` (the `PRODUCTS` list between the markers), so
anything the Telegram bot publishes appears in the app on the next refresh.
No separate product list to keep in step.

- **Order this** opens the website's order form with the piece filled in
  (`https://mayurisyarntales.online/?order=<product id>#order`).
- **Ask by email** opens an email to Mayuri with the product name and code.
- Offline: shows the last saved collection (or the copy bundled in
  `assets/site_snapshot.html` on a first start without internet).

## Build (Windows, this PC)

Flutter is in `E:\dev\flutter`, the Android SDK in `E:\dev\android-sdk`
(both on the user PATH; `ANDROID_HOME` is set). Java 17 is the portable
zip in `E:\dev\jdk-17.0.21.0.2+1` (`flutter config --jdk-dir` points at it).

```
cd app
flutter test                 # product reader checks
flutter build apk --release --split-per-abi   # one small APK per phone type
# app-arm64-v8a-release.apk (~17 MB) fits almost every phone;
# armeabi-v7a is for old 32-bit phones. Plain --release makes one 47 MB APK.
```

Refresh the bundled snapshot now and then: copy `../index.html` to
`assets/site_snapshot.html`.

Icons come from `media/brand/` (the logo kit). The release build is signed
with the debug key for now: fine for sharing the APK directly, but the Play
Store needs a proper upload key first.
