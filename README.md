# Tasks

A small task-list app for iPhone, built with Expo and React Native.

Add a task, tap it to mark it done, hit ✕ to delete it. Tasks are saved on the
device, so they survive closing the app. Follows the iPhone's light/dark setting.

## Run it on your iPhone

You need [Node.js](https://nodejs.org) on your computer. You do **not** need a
Mac or Xcode.

1. Install **Expo Go** from the App Store on your iPhone.
2. On your computer:

   ```sh
   git clone https://github.com/corruptchemist/claude-test.git
   cd claude-test
   npm install
   npx expo start
   ```

3. A QR code appears in the terminal. Open the iPhone **Camera** app, point it at
   the QR code, and tap the banner that appears.

The app opens in Expo Go. Edit any file and it reloads on the phone immediately.

### If the QR code doesn't connect

Your phone and computer must be on the same Wi-Fi network. If they aren't, or
the network blocks device-to-device traffic, start it through Expo's relay
instead:

```sh
npx expo start --tunnel
```

## Project layout

| File | Purpose |
| --- | --- |
| `App.tsx` | Screen layout and task state |
| `src/storage.ts` | Loading and saving tasks on the device |
| `src/TaskRow.tsx` | A single row in the list |
| `src/theme.ts` | Light and dark color palettes |

## Checks

```sh
npx tsc --noEmit                 # typecheck
npx expo export --platform ios   # verify it bundles
```

## Notes

Dependency versions are pinned to what Expo SDK 57 expects — in particular
`@react-native-async-storage/async-storage` is held at exactly `2.2.0`, which is
the version Expo Go ships native code for. Upgrading it to a newer major will
crash the app in Expo Go.

Built with Expo SDK 57, React Native 0.86, React 19, TypeScript.
