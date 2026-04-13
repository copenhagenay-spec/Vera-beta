# VERA Setup Guide

This guide walks you through getting VERA up and running from scratch.

---

## Step 1 — Download the Installer

1. Go to the [VERA releases page](https://github.com/copenhagenay-spec/Vera-beta/releases)
2. Download the latest `VERA_Setup_x.x.x.exe`

---

## Step 2 — Run the Installer

Double-click the installer and follow the prompts. The installer handles everything automatically:

- Python package dependencies
- espeak-ng voice engine
- Kokoro TTS model files (~310MB, downloaded once)

A progress screen shows each step. This takes a minute or two depending on your connection.

> **Note:** You do not need to install Python manually — VERA's installer finds your existing Python installation. If Python is not installed, get it from [python.org](https://python.org) (3.11 or newer, check **"Add Python to PATH"**).

---

## Step 3 — Setup Wizard

VERA opens the setup wizard automatically on first launch. Work through each section and click **Finish** when done.

### Listening Mode

Choose how VERA listens for your commands:

| Mode | How it works |
|---|---|
| **Wake Word** | Say "vera" to activate, then speak your command |
| **Hold-to-talk** | Hold a key or button while speaking, release when done |
| **Push to Toggle** | Press once to start listening, press again to stop |

Click **Record** to assign your key or button for Hold-to-talk or Push to Toggle.

### Steam Import (optional)

Click **Import Steam Apps** to add your entire Steam library so you can open games by voice.

### Desktop Shortcut (optional)

Check **Create desktop shortcut** to put VERA on your desktop.

---

## Step 4 — Finish

Click **Finish**. VERA launches and starts listening in the background — look for the icon in your system tray.

Say **"what can I say"** to see a full list of available commands.

---

## Running from Source

If you're running VERA from source instead of the installer, use `setup_installer.cmd` to install dependencies manually, then `run_ipa.cmd` to launch.

---

## Updating VERA

Open the VERA UI and click **Check for Updates** in Settings → Utilities. VERA will compare your version against the latest release and prompt you if an update is available.

Your settings, memory, and macros are preserved during updates.

---

## Uninstalling VERA

Use **Add/Remove Programs** in Windows Settings, or run `uninstall.cmd` in the VERA folder. Your `config.json` and `memory.json` are left behind so your settings are preserved if you reinstall.
