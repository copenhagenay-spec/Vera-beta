# SH|RA Voice Command Reference

A full list of everything you can say to SH|RA. Say **"what can I say"** at any time to see a summary inside the app.

---

## Apps

| What to say | What happens |
|---|---|
| `open <app name>` | Opens the app |
| `launch <app name>` | Same as open |
| `open that again` | Reopens the last app you opened with SH|RA |
| `close <app name>` | Closes the app |
| `close this` | Closes the currently active window |
| `add alias <shortcut> for <app name>` | Creates a shorter name you can use to open an app |

> **Examples:** "open discord", "open rust", "launch opera gx", "close steam"
>
> **Alias example:** "add alias music for spotify" — then say "open music" to launch Spotify

---

## Web

| What to say | What happens |
|---|---|
| `search for <query>` | Opens a web search in your preferred browser |
| `web search for <query>` | Same as above |

> **Example:** "search for best graphics settings for rust"
>
> **Preferred browser:** Configurable in Settings → General. SH\|RA will use that browser for searches and YouTube. Falls back to your system default if the selected browser isn't found.

---

## YouTube

| What to say | What happens |
|---|---|
| `open youtube` | Opens YouTube homepage |
| `youtube <query>` | Searches YouTube for your query |
| `youtube play <query>` | Same as above |
| `youtube play` | Play / resume |
| `youtube pause` | Pause |
| `youtube next` / `youtube skip` | Next video |
| `youtube back` / `youtube previous` | Previous video |

> **Example:** "youtube play blinding lights"

---

## Spotify

| What to say | What happens |
|---|---|
| `spotify <query>` | Opens Spotify and searches for your query |
| `spotify play <query>` | Same as above |
| `play` / `pause` | Play or pause current track |
| `skip` / `next` | Skip to next track |
| `back` / `previous` | Go to previous track |

> **Example:** "spotify play eye of the tiger"

---

## Volume

| What to say | What happens |
|---|---|
| `volume up` | Increases system volume by 10% |
| `volume down` | Decreases system volume by 10% |
| `set volume <number>` | Sets system volume to a specific level (0–100) |
| `set volume max` | Sets system volume to 100% |
| `set <app> volume <number>` | Sets the volume for a specific app (0–100) |

> **Example:** "set spotify volume 50", "set discord volume 20"

---

## Muting SH|RA

| What to say | What happens |
|---|---|
| `mute` / `be quiet` | SH|RA stops responding to commands until unmuted |
| `unmute` / `okay shira` | SH|RA resumes responding |

> This mutes SH|RA's responses — it does not affect your system volume.

---

## Weather & Date

| What to say | What happens |
|---|---|
| `weather in <city>` | Reads the current weather for that city |
| `what's the weather in <city>` | Same as above |
| `what's the date` / `what day is it` | Reads the current date |
| `what time is it` | Reads the current time |

> **Example:** "weather in new york", "what's the date", "what time is it"

> **Tip:** If the game overlay is visible, weather results are also pinned to the top of the overlay in real time.

---

## News

| What to say | What happens |
|---|---|
| `give me the news` | Reads top headlines from your selected news source |
| `news briefing` | Same as above |

> News source is configurable in Settings.

---

## Timers

| What to say | What happens |
|---|---|
| `set a timer <n> minutes` | Sets a timer for n minutes |
| `set a timer <n> seconds` | Sets a timer for n seconds |
| `set a timer <n> hours` | Sets a timer for n hours |
| `cancel timer` / `stop timer` | Cancels all running timers |

> **Examples:** "set a timer 10 minutes", "cancel timer"

---

## Reminders

| What to say | What happens |
|---|---|
| `remind me to <thing> at <time>` | Sets a reminder |
| `remind me at <time> to <thing>` | Same as above |
| `what are my reminders` | Lists all upcoming reminders |
| `cancel all reminders` | Removes all reminders |

> **Examples:** "remind me to take my meds at 9pm", "what are my reminders"

---

## Notes

| What to say | What happens |
|---|---|
| `note <text>` | Saves a note |
| `open notes` | Opens your notes file |
| `list notes` / `show notes` | Reads your notes aloud |
| `delete last note` | Deletes the most recent note |
| `clear all notes` | Deletes all notes |

> **Example:** "note pick up milk on the way home"

---

## Clipboard

| What to say | What happens |
|---|---|
| `copy <text>` | Copies the text to your clipboard |
| `paste` / `paste that` / `paste clipboard` | Pastes whatever is in your clipboard |
| `read clipboard` | Reads your clipboard contents aloud |
| `clear clipboard` | Clears your clipboard |

> **Example:** "copy hello world", "paste that"

---

## System

| What to say | What happens |
|---|---|
| `type <text>` | Types the text as keyboard input |
| `send message <text>` | Types the text and presses Enter |
| `sleep computer` | Puts your PC to sleep |
| `restart computer` | Restarts your PC after a 5 second delay |
| `shut down computer` | Shuts down your PC after a 5 second delay |
| `restart assistant` | Restarts SH|RA |

> **Important:** For `type` and `send message` to work, your cursor must be in a text field — SH|RA types into whatever is currently focused.

---

## Gaming Mode

| What to say | What happens |
|---|---|
| `start gaming mode` | Strips responses to ultra-short, silences idle chatter, suppresses unrecognized command feedback |
| `stop gaming mode` | Returns SH|RA to normal behavior |

> **"Gaming Mode"** appears in the status bar while active.
>
> **Steam users:** Gaming mode activates and deactivates automatically when a Steam game is launched or closed. Manual commands still work as normal.

---

## Game Overlay

| What to say | What happens |
|---|---|
| `show overlay` / `overlay edit` | Shows all widget cards in edit mode — drag to reposition, click PIN to keep visible |
| `hide overlay` / `overlay lock` | Locks positions, saves, and hides unpinned cards. Pinned cards stay on screen. |

> The overlay hotkey (configurable in Settings → Game Overlay) does the same thing — press to show, press again to hide and lock.
>
> See the [Overlay Guide](overlay.md) for full details on widgets, pinning, and the Now Playing controls.

---

## Discord

| What to say | What happens |
|---|---|
| `discord dm <name> <message>` | Sends a DM to a contact in your alias list |
| `discord <name> <message>` | Sends to a contact or channel alias |
| `discord read <name>` | Navigates to the contact or channel so you can read it, then tabs back |

> Contacts and channel aliases are configured in Settings → Discord. SH\|RA will not send to anyone not in your alias list — if the name isn't recognized she'll tell you instead of guessing.
>
> See the [Discord Setup Guide](discord.md) for details.

---

## AI

| What to say | What happens |
|---|---|
| `ask <question>` | Sends your question to the AI and reads the answer aloud |

> Requires an API key in the Integrations tab. See the [AI Setup Guide](ai-setup.md) for details.
>
> **Example:** "ask what is the capital of France"
>
> **Conversational memory:** SH|RA remembers the last 5 exchanges within a session, so follow-up questions work naturally. Context clears on restart.

---

## Memory

| What to say | What happens |
|---|---|
| `my name is <name>` | Saves your name so SH|RA remembers it |
| `what is my name` | SH|RA tells you your saved name |
| `remember <fact>` | Saves a fact for later |
| `forget <thing>` | Removes a saved fact |
| `what do you know about me` | SH|RA reads back everything she remembers |

> **Examples:** "my name is Alex", "remember my birthday is March 5th", "forget my birthday"

---

## Key Binds

Custom phrases mapped to keypresses — configured in the **Integrations** tab.

> **Example:** Bind "reload" to R so saying "reload" presses R in-game.
>
> ⚠ May be flagged by EAC/BattlEye anti-cheat. See the [Key Binds Guide](keybinds.md).

---

## Command Macros (Premium)

Chain multiple commands into one phrase — configured in the **Integrations** tab.

> **Example:** Say "good morning" → SH|RA opens Spotify, reads the weather, and checks your reminders — each step waits for SH|RA to finish speaking before the next begins.

---

## Conversation

| What to say | What happens |
|---|---|
| `I'm tired` / `I'm stressed` / `I'm happy` | SH|RA responds to your mood |
| `I'm playing <game>` | Sets your activity so SH|RA is context-aware |
| `tell me a joke` | SH|RA tells you a joke |

---

## Help

| What to say | What happens |
|---|---|
| `what can I say` | Opens the command reference window |
| `show commands` | Same as above |
| `show help` | Same as above |
