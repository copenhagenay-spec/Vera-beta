# Troubleshooting

Common issues and how to fix them. If your problem isn't listed here, submit a bug report via **Settings → Utilities → Bug Report**.

---

## SH|RA Won't Start

**"Run_ipa.cmd opens and closes immediately"**
- Open a terminal, navigate to your SH|RA folder, and run `run_ipa.cmd` directly to see the full error output
- Run the installer again to repair missing files or dependencies

**"Missing dependency" error on launch**
- Run the SH|RA installer again — it will repair any missing packages automatically

---

## Microphone / Not Hearing Commands

**"SH|RA doesn't respond to anything I say"**
- Check Windows microphone permissions: **Settings → Privacy & Security → Microphone** — make sure microphone access is on
- Open the SH|RA UI and check **Last Transcript** in the status bar — if it's blank, SH|RA isn't hearing you
- Go to **Settings → Recording** and make sure the correct input device is selected
- Try speaking closer to your microphone or increasing your mic volume in Windows Sound settings

**"SH|RA hears me but gets the words wrong"**
- Check **Last Transcript** in the SH|RA UI to see what was transcribed
- Speak more slowly and clearly
- Use the **Training** tab to add corrections for commonly misheard words
- Try a different listening mode — Hold-to-talk reduces background noise compared to Wake Word

**"Wake word isn't triggering"**
- Make sure you're saying "shira" clearly before your command
- Background noise can prevent wake word detection — try Hold-to-talk mode instead
- Check that your microphone input level is sufficient in Windows Sound settings

---

## Commands Not Working

**"SH|RA says she doesn't understand"**
- Check **Last Transcript** to see what was heard — the issue may be a mishearing
- Say **"what can I say"** to review all available commands
- Make sure the command you're using matches the format in the [Command Reference](commands.md)

**"Open \<app\> doesn't work"**
- The app may not be in SH|RA's list — check the **Apps** tab in the UI
- If it's a Steam game, SH|RA syncs your Steam library automatically on every launch — restart SH|RA and try again
- If it's not on Steam, add it manually — see [Adding Apps](adding-apps.md)
- Spotify and Discord are not auto-discovered and must be added manually

**"Close this hung up SH|RA"**
- This was fixed in v0.97.7.1 — update SH|RA via **Settings → Utilities → Check Updates**

**"Key binds aren't working in my game"**
- Some games with anti-cheat (EasyAntiCheat, BattlEye) block synthetic keypresses — see [Key Binds](keybinds.md) for details
- Make sure the game window is focused when the command fires

**"Macros aren't triggering"**
- Command Macros require Premium — check that Premium is enabled in Settings
- Make sure the macro is listed under Command Macros in the Integrations tab

---

## Audio / TTS

**"SH|RA isn't speaking"**
- Make sure your speakers or headset aren't muted
- Check your Windows default audio output device in Sound Settings
- Try a different TTS voice in **Settings → Voice**

**"SH|RA's voice sounds wrong or robotic"**
- Try a different voice in **Settings → Voice** — there are 11 Kokoro voices available
- Run `setup_installer.cmd` to reinstall dependencies

---

## AI / Ask Command

**"SH|RA says it can't reach the AI"**
- Check your API key in **Integrations → AI API Key** — make sure there are no extra spaces
- Make sure you have an active internet connection
- If using Groq, check you haven't exceeded the free tier daily limit (14,400 requests/day)

**"My Anthropic key isn't being recognized"**
- Make sure the key starts with `sk-ant-` — if it doesn't, it may be an OpenAI or Groq key
- Re-paste the key from your Anthropic console to avoid clipboard artifacts

---

## Discord

**"SH|RA said she doesn't have that person in contacts"**
- Add the contact in Settings → Discord → DM Contacts or Channel Aliases
- Make sure the nickname you said matches what you configured

**"Messages aren't sending"**
- Make sure Discord is open and not minimized
- Check the alias is listed in the Discord tab
- See [Discord Setup](discord.md) for configuration details

**"Read discord isn't navigating"**
- Discord must be open and visible — it won't work if Discord is minimized
- Check the contact or channel alias is configured in the Discord tab

---

## Overlay

**"The widgets aren't showing"**
- Say `show overlay` or press your hotkey to enter edit mode
- If cards appear off-screen, enter edit mode and drag them back into view

**"My widget positions reset after restart"**
- Positions save when you hide the overlay — make sure you said `hide overlay` or pressed the hotkey to lock them, rather than closing the app directly

**"The overlay is blocking my game input"**
- Overlay cards are click-through by default — only the Now Playing card is interactive (so the buttons work)
- Pin the Now Playing card to a corner out of your main play area

---

## Updates

**"Check Updates says I'm up to date but I'm not on the latest version"**
- SH|RA compares versions against the GitHub releases page — make sure you have an internet connection
- You can always download the latest installer manually from the [releases page](https://github.com/copenhagenay-spec/Vera-beta/releases)

---

## Crash Logs

If SH|RA crashes, logs are saved to:
```
<SH|RA install folder>\data\logs\assistant.log
```
The default install location is `C:\Program Files\SHRA\`. You can include this file when submitting a bug report via **Settings → Utilities → Bug Report**.
