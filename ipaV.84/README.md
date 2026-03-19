# IPA Assistant

Offline personal assistant using Vosk.

## IPA (No Terminal)

### Quick Start

1. Install Python 3.10+:
   https://www.python.org/downloads/
2. Double‑click:
   `ipa/run_ipa.cmd`
3. The first‑run wizard will open:
   - Choose **Language** (English or Spanish)
   - Choose **Mode** (Hold‑to‑talk, Hotkey, or Timed)
   - Click **Install Dependencies** (one‑time)
   - If you don't have a model yet, click **Download English/Spanish Model**
   - Optional: **Import Steam Apps**
   - Click **Finish**

IPA will start listening in the background after the wizard finishes.

## Uninstall

Double-click:
`ipa/uninstall.cmd`

This removes the `data` folder (model, logs, settings). To fully remove IPA,
delete the `ipa` folder.

## Files

- `ipa/data/model` holds the Vosk model
- `ipa/data/model/en` English model
- `ipa/data/model/es` Spanish model (if installed)
- `ipa/data/assets` holds icons
- `ipa/data/logs` holds crash logs
- `ipa/data/config.json` holds your settings

## Features

- Open apps: say `open <app>`
- Web search: say `search for <query>`
- Timers: say `set a timer 5 minutes`
- Spotify media controls: say `play`, `pause`, `skip song`
- Steam import: adds games as `open <game>`
- English and Spanish recognition (per-language models)

## Steam Import

Use the "Import Steam" button in the Apps section to auto-add games
from your Steam library as voice commands.

## Models

Place models in:

```
ipa/data/model/en/<model-folder>
ipa/data/model/es/<model-folder>
```

Small English model example:
`vosk-model-small-en-us-0.15`

Small Spanish model example:
`vosk-model-small-es-0.42`

## Tips

- If audio isn’t detected, check Windows microphone permissions.
- If a command doesn’t trigger, check **Last Transcript** for misheard words and add aliases.
