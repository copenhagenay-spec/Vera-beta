# Game Overlay

The game overlay is a set of independent, draggable widget cards that sit over your game. Each card can be positioned anywhere on screen and pinned to stay visible permanently. Pinned cards are always-on-top and click-through — they display information without interfering with your game.

---

## Widgets

| Widget | What it shows |
|---|---|
| **Transcript** | Your last 3 voice exchanges with SH\|RA, plus current weather if active |
| **System** | Live CPU % and RAM usage, updated every 2 seconds |
| **Timers** | All active countdowns. Turns red when under 30 seconds |
| **Now Playing** | Current Spotify track and artist, with play/pause, skip, and back controls |

---

## Showing and Arranging

| What to say | What happens |
|---|---|
| `show overlay` | Shows all widgets in edit mode — drag them where you want |
| `hide overlay` | Locks positions, saves, and hides unpinned widgets |
| `overlay edit` | Same as show overlay |
| `overlay lock` | Same as hide overlay |

You can also assign a **hotkey** in Settings → Game Overlay. Press it once to show (edit mode), press again to hide and lock.

**To arrange your widgets:**
1. Say `show overlay` or press your hotkey
2. Drag each card to where you want it
3. Click **PIN** on any card you want to keep visible at all times
4. Say `hide overlay` or press your hotkey — unpinned cards hide, pinned cards stay

Positions and pin states are saved automatically and restored on every restart.

---

## Pinned Widgets

A pinned widget stays visible even when the overlay is hidden. It is fully click-through so it won't block game input (except the Now Playing card, which has interactive buttons).

To pin a widget:
1. Say `show overlay` to enter edit mode
2. Click the **PIN** button on the card — it turns gold and reads **PINNED**
3. Say `hide overlay` — the card stays on screen

To unpin, enter edit mode again and click the button to toggle it back to **PIN**.

---

## Now Playing Controls

The Now Playing card has **◀◀ ▶/▌▌ ▶▶** buttons that work directly — no voice command needed. Requires Spotify to be connected (Settings → Integrations → Connect Spotify).

---

## Weather on the Overlay

Saying `weather in <city>` pins current conditions to the Transcript card:

- **Line 1:** City, temperature, and description
- **Line 2:** Today's high, low, and rain chance

> **Example:** "weather in Birmingham" → `Birmingham Alabama · 79°F · Sunny` / `H: 84°F  L: 53°F · Rain: 0%`

The weather stays pinned until you ask for a new city or restart SH|RA.

---

## Hotkey

Assign a key to toggle the overlay without using your voice:

1. Open the SH|RA UI
2. Go to **Settings** → **Game Overlay**
3. Click **Record** next to Overlay Hotkey
4. Press the key you want to use
5. Click **Save**

The hotkey cycles: **hidden → edit mode → hidden**.

---

## Troubleshooting

**"The widgets aren't showing up"**
- Say `show overlay` or press your hotkey
- If they appeared off-screen, say `show overlay` to enter edit mode and drag them back into view

**"My widget positions reset"**
- Positions save when you hide the overlay — make sure you said `hide overlay` or pressed the hotkey to lock them rather than just closing the app

**"The Now Playing card is blocking my mouse"**
- This card is interactive (so the buttons work) — pin it to a corner of the screen out of the way of your main play area

**"Weather isn't showing on the overlay"**
- Say `weather in <city>` while the overlay is visible
- Make sure you have an active internet connection
