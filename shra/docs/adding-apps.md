# Adding Apps to SH|RA

This guide covers the different ways to add apps to SH|RA so you can open them by voice.

---

## How It Works

When you say **"open \<app name\>"**, SH|RA looks up that name in its app list and launches whatever is assigned to it. There are five ways apps get added to that list:

1. **Auto-discovered** — common apps SH|RA finds automatically on startup
2. **Start Menu scan** — SH|RA scans your Start Menu on every launch and adds any installed apps it finds
3. **Steam Import** — your entire Steam library added in one click
4. **Voice alias** — you define a shortcut name for any app by voice
5. **Manually via the UI** — type in an app name and path directly in the SH|RA settings

---

## Auto-Discovered Apps

On every startup SH|RA scans your PC for common apps and adds any it finds automatically. These include:

- Chrome, Firefox, Edge, Opera, Opera GX
- Steam, VLC, OBS
- Notepad, Calculator, Task Manager, File Explorer

You don't need to do anything — if the app is installed it will just work.

SH|RA also scans your **Start Menu** on every launch and picks up any other installed software automatically — including apps like Spotify, Discord, and most third-party programs that create Start Menu shortcuts.

---

## Steam Library Import

To add all your Steam games at once:

1. Open the SH|RA UI
2. Go to the **Apps** tab
3. Click **Import Steam**

SH|RA will scan your Steam installation and add every game in your library. Once imported, say **"open \<game name\>"** to launch any of them.

> **Example:** "open hell divers 2", "open rust", "open grey hack"

> **Note:** The game name you say should match the Steam title. If a game has a long or unusual name and SH|RA doesn't recognize it, try adding an alias for it (see below).

---

## Adding an App Manually via the UI

If an app wasn't auto-discovered and isn't on Steam, you can add it manually:

1. Open the SH|RA UI
2. Go to the **Apps** tab
3. Fill in **App name** — this is what you'll say out loud
4. Fill in **App command** — the full path to the executable or a launch command
5. Click **Add App**

> **Example:** App name: `signal` — App command: `C:\Users\You\AppData\Local\Signal\signal.exe`

**Common paths for apps not auto-discovered:**

| App | App command |
|---|---|
| Spotify | `C:\Users\<YourName>\AppData\Roaming\Spotify\Spotify.exe` |
| Discord | `C:\Users\<YourName>\AppData\Local\Discord\Update.exe --processStart Discord.exe` |

Replace `<YourName>` with your Windows username.

You can also use this to open websites by voice — just put a URL as the app command:

> **Example:** App name: `reddit` — App command: `https://www.reddit.com`

Say **"open reddit"** and SH|RA will open it in your default browser.

Once added, say **"open \<name\>"** to launch it. You can also click **Test App** to verify it opens correctly before using it by voice.

---

## Adding an Alias by Voice

If an app name is hard to say, too long, or keeps getting misheard, you can create a shorter alias for it.

**Say:** `add alias <your shortcut> for <app name>`

> **Examples:**
> - "add alias hell divers for helldivers 2"
> - "add alias music for spotify"
> - "add alias browser for opera gx"

You can then say **"open \<your shortcut\>"** to launch the app — no restart needed.

---

## Troubleshooting

**"SH|RA opened the wrong app"**
The app name you said was too close to another app in the list. Try adding an alias with a more unique name.

**"SH|RA didn't open anything"**
- The app may not be in the list — check if it's a Steam game (run Steam Import) or a common app (restart SH|RA to trigger auto-discovery)
- Try saying the name more clearly or add an alias

**"My game isn't showing up after Steam Import"**
- Make sure the game is fully installed, not just in your library
- Run Steam Import again after installing the game
