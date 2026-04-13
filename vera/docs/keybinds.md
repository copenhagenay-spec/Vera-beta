# Key Binds

Key binds let you map a spoken phrase to a keypress or macro sequence, so you can trigger in-game actions or shortcuts by voice.

---

## Anti-Cheat Warning

> ⚠️ **Use at your own risk in games with anti-cheat software.**
>
> Key binds work by simulating synthetic input. Some anti-cheat implementations (EasyAntiCheat, BattlEye) may detect and flag synthetic keypresses. Behavior varies by game — some titles are permissive, others are not. We are not responsible for any bans or flags resulting from use of this feature in protected games. Use outside of protected games is safe.

---

## Setting Up a Key Bind

1. Open the VERA UI and go to the **Integrations** tab
2. Enter a **Phrase** — what you'll say to trigger the bind (e.g. `reload`, `map`, `hail hangar`)
3. Click **+ Step** to record a key or combo — press the key or hold modifiers (Alt, Ctrl, Shift) then press the key
4. Click **+ Step** again to add more steps to create a macro sequence
5. Set a **Count** if the key needs to be pressed multiple times
6. Click **Add Key Bind**

---

## Key Combos

Hold modifier keys while pressing the main key to record a combo:

> **Examples:** `alt+n`, `ctrl+shift+f`, `ctrl+z`

---

## Macro Sequences

Click **+ Step** multiple times to chain keypresses together. Each step fires in order with a short delay between them.

> **Example:** `x1 > q` — presses mouse side button, then presses Q

This is useful for multi-step in-game actions like selecting a building then queuing a unit.

---

## Mouse Side Buttons

The side buttons on your mouse can be recorded as steps:

- **Mouse Back** — recorded as `x1`
- **Mouse Forward** — recorded as `x2`

---

## Managing Binds

- Click a bind in the list to select it
- Click **Remove Selected** to delete it
- If nothing is selected, the last bind is removed

---

## Troubleshooting

**"VERA says the phrase but nothing happens"**
- The game may be blocking synthetic input (anti-cheat)
- Make sure the game window is focused when the bind fires
- Re-record the key bind using the **+ Step** button

**"The wrong key is being pressed"**
- Delete the bind and re-record it using the **+ Step** button
