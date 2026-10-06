# firebase_messaging — pub

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). A plant can adopt this page instead of scouting
> the plugin's and Firebase Cloud Messaging's surface; it still runs
> `ingest-library` against its own `pubspec.lock` for the exact plugin and
> `firebase_core` versions.

## What it is
`firebase_messaging` is the FlutterFire plugin for Firebase Cloud Messaging
(FCM): it registers a device for push, receives messages in the foreground,
background and terminated states, and reports notification taps. It runs on
Android (Google Play services), Apple platforms (through APNs) and web (a VAPID
key plus a service worker), and it needs `firebase_core`
(`Firebase.initializeApp`). The server side sends through the FCM HTTP v1 API.

Upstream home: the plugin source at https://github.com/firebase/flutterfire ,
the package at https://pub.dev/packages/firebase_messaging , and the FCM docs
at https://firebase.google.com/docs/cloud-messaging/flutter/client .

## Install, setup and configuration
- Install and initialize Firebase first (the `flutterfire configure`
  workflow), then `flutter pub add firebase_messaging` and rebuild.
- Apple: enable the Push Notifications capability and the Background Modes
  "Background fetch" and "Remote notifications"; upload an APNs authentication
  key (`.p8`, with its key ID and team ID) in the Firebase console. Keep method
  swizzling on: without it the plugin's token handling does not work properly.
- Android: the device needs Google Play services. The plugin's manifest
  already declares `POST_NOTIFICATIONS`, and the app must target API 33 or
  later for it. The Flutter setup page lists the current Android and Apple
  minimums.
- Web: create or import a VAPID key pair (Cloud Messaging tab, Web Push
  certificates), pass it as `getToken(vapidKey: ...)`, and register a
  `firebase-messaging-sw.js` service worker (scope
  `/firebase-cloud-messaging-push-scope`) that imports the Firebase app and
  messaging SDKs and initializes Firebase.
- Auto-init: on by default, which uploads identifier and configuration data
  when the app starts. To defer it for a consent flow, set
  `FirebaseMessagingAutoInitEnabled` to `NO` in `Info.plist`, and on Android set
  both `firebase_messaging_auto_init_enabled` and
  `firebase_analytics_collection_enabled` to false in the manifest (both are
  needed). `setAutoInitEnabled(true)` turns it on at runtime and persists
  across restarts.

## Core API / usage shape
- Permission: `FirebaseMessaging.instance.requestPermission(alert:, badge:,
  sound:, provisional:, ...)` returns `NotificationSettings`; its
  `authorizationStatus` is `authorized`, `denied`, `notDetermined` or
  `provisional`. It is required on Apple platforms, web and Android 13 and
  later before messages arrive.
- Token: `getToken()` (asks for permission if needed); `getAPNSToken()` on
  Apple, where the APNs token must exist before FCM calls and is not
  guaranteed at the first call; `onTokenRefresh` (fires on each start and when
  the token changes); `deleteToken()`.
- Receiving: `FirebaseMessaging.onMessage` (foreground stream),
  `FirebaseMessaging.onBackgroundMessage(handler)` (background and terminated),
  `onMessageOpenedApp` (a tap that brings a background app forward) and
  `getInitialMessage()` (the tap that started the app from terminated,
  returned once).
- `RemoteMessage` carries `data`, `notification`, a message id and the sent
  time.
- Others: `setForegroundNotificationPresentationOptions` (Apple),
  `isSupported()` (web), `setDeliveryMetricsExportToBigQuery` (Android).
- Server send: `POST https://fcm.googleapis.com/v1/projects/{project}/messages:send`
  with `Authorization: Bearer <access token>` and a body
  `{"message": {"token" | "topic" | "condition": ..., "notification": {...},
  "data": {...}}}`. Exactly one target. Success returns the message name.

## Idioms & best practices
- Handle both open paths: `getInitialMessage()` for a cold start and
  `onMessageOpenedApp` for a background app (upstream: "It is recommended that
  both scenarios are handled"). Run the setup from an async method, not from
  `initState` itself.
- Register the background handler once, before `runApp`.
- Listen to `onTokenRefresh` and upload the new token every time. Observed in
  practice: an app that captured the token only at login silently lost pushes
  after rotation.
- Store each token on the server with a timestamp updated on every upload, and
  prune stale tokens (see Operational behaviour).
- Ask for permission at a moment the user understands; on Apple,
  `provisional: true` lets the user decide later.
- When the same codebase also builds a web client without push, initialize
  Firebase messaging only on the targets that use it, and cancel stream
  subscriptions on dispose (observed in practice).
- Localize on the device with `title_loc_key`/`body_loc_key` (Android) or
  `title-loc-key`/`loc-key` in the `apns` payload, or send per-language text
  from the server.

## General pitfalls
- Foreground notification messages are not displayed by default. Android needs
  a high-importance notification channel; Apple needs
  `setForegroundNotificationPresentationOptions`.
- The background handler must be a top-level function, not anonymous, and
  annotated `@pragma('vm:entry-point')` so release builds keep it. It runs
  outside the app's context, so it cannot update UI or app state (HTTP, IO and
  other plugins are fine); it must call `Firebase.initializeApp()` itself if it
  uses other Firebase services; and work beyond about 30 seconds may get the
  process killed. On Android it runs in its own isolate; Apple platforms need
  none.
- Handling only `onMessageOpenedApp` misses taps that cold-start the app.
- Messages arrive only after the app has been opened once. On iOS a user who
  swipes the app away must reopen it before background messages resume; on
  Android a force stop from settings has the same effect.
- Android 13 and later: the app must request the runtime notification
  permission. If the first notification channel is created while the app is in
  the background (which the FCM SDK does for a notification message),
  notifications received before the user accepts are lost.
- On Android 13 and later `denied` means "denied or not yet decided", so the app
  must remember whether it already asked.
- Apple: calling `getToken()` before the APNs token exists can fail. Images in
  notifications need a Notification Service Extension, and image display must be
  tested on a physical device. Observed in practice: a simulator yielded no
  APNs token; the docs say only to test on a device.
- Observed in practice: the `aps-environment` entitlement must match the build
  (development or production); the docs reviewed are silent on it.
- `data` values are strings only, and keys must not be `from`,
  `message_type`, or start with `google.` or `gcm.` (which covers
  `gcm.notification.`). The payload, keys and values counted, is capped at
  4096 bytes for most messages and 2048 bytes for a message to a topic; the
  Firebase console enforces a 1000-character limit.

## Testing
- Upstream describes a manual test: install the app, background it, send a test
  message to its registration token from the console's Messaging composer, and
  read the Reports dashboard.
- The fetched upstream pages give no unit-test guidance. Wrapping the plugin
  behind an interface the app owns, so unit tests mock that interface, is the
  usual answer (derived, not upstream).

## Security defaults
- The server credential is the secret. Use Application Default Credentials
  where available; otherwise point `GOOGLE_APPLICATION_CREDENTIALS` at a
  service-account JSON file, which upstream calls "more secure and strongly
  recommended" than a path in code, and keep the key out of every repository.
  The OAuth2 scope is `https://www.googleapis.com/auth/firebase.messaging`.
- A service account of one project can send to another project only when it
  holds the Firebase Cloud Messaging API Admin role there.
- Registration tokens and installation IDs identify a device; auto-init
  uploads them, so turn auto-init off until consent where consent is required.
  Data-processing terms are a legal question and belong outside this page.

## Operational behaviour
- Token lifecycle: a registration counts as stale after about a month of
  inactivity; on Android FCM expires it after 270 days. Upload the token at
  least monthly from the client, and on the server delete it on
  `UNREGISTERED` (HTTP 404), or on `INVALID_ARGUMENT` (HTTP 400) when the
  payload is known to be valid, since that code also means a bad payload. Run a
  periodic prune.
- FCM is moving from registration tokens to Firebase Installation IDs (FIDs);
  both work. The Flutter docs reviewed still show the token API (`getToken`,
  `onTokenRefresh`), so check the plugin changelog before adopting FIDs.
- Message types: a notification message is displayed by the FCM SDK while the
  app is in the background and may carry a data payload; a data message is
  handled by app code.
- Other send errors: `SENDER_ID_MISMATCH` (403, the token belongs to another
  sender) and `QUOTA_EXCEEDED` (429). A message TTL runs from 0 to 28 days.
- Default tap behaviour opens the app (starting it if terminated).

## Interop
- `firebase_core` moves in step with the plugin: each plugin major expects a
  matching `firebase_core` major.
- On web, the messaging service worker coexists with Flutter's own service
  worker under its own scope.
- Server side: the Firebase Admin SDKs or the HTTP v1 API directly.
- Native-only initialization in a codebase that also builds for web:
  `library-corpus/language/flutter`.

## Major lines
### Before 9
The null-safety release replaced `requestNotificationPermissions`,
`autoInitEnabled()` and `deleteInstanceID()` with `requestPermission`,
`isAutoInitEnabled`/`setAutoInitEnabled` and `deleteToken`.

### 10 and 11
10 removed the `senderId` argument of `getToken` and `deleteToken`, and 11
raised the Android `minSdk`.

### 12
Web moved to the modular Firebase JS SDK, and `isSupported()` became
asynchronous.

### 13
Android 13 runtime notification permission; the app must target API 33.

### 14 and 15
Native Firebase SDK bumps; 15 raised the Android `minSdk` and the iOS floor and
documented service-worker loading for newer Flutter web bootstraps.

### 16
Newer native Firebase SDKs on both platforms, and the deprecated functions
removed. During this line Android stopped reporting terminated-state taps
through `onMessageOpenedApp`, so handle them through `getInitialMessage()`.

## Upstream docs
- https://firebase.google.com/docs/cloud-messaging/flutter/client
- https://firebase.google.com/docs/cloud-messaging/flutter/receive
- https://firebase.google.com/docs/cloud-messaging/manage-tokens
- https://firebase.google.com/docs/cloud-messaging/send/v1-api
- https://firebase.google.com/docs/cloud-messaging/error-codes
- https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages
- https://firebase.google.com/docs/flutter/setup
- https://github.com/firebase/flutterfire/tree/main/packages/firebase_messaging
- https://pub.dev/packages/firebase_messaging
