# Discord Setup Guide

This guide explains how to set up the Discord voice commands in SH|RA.

---

## Overview

SH|RA sends Discord messages by controlling your open Discord client — no bots, no webhooks, no server permissions needed. It works for DMs, group DMs, and server channels.

| What to say | What happens |
|---|---|
| `discord dm <name> <message>` | Sends a DM to a contact in your alias list |
| `discord <name> <message>` | Sends to a contact or channel alias |
| `discord read <name>` | Navigates to the conversation so you can read it, then tabs back after a set delay |

> **Important:** SH|RA will only send to names you have configured in the Discord tab. If the name isn't recognized she will tell you and stop — she will not guess or fall back to sending to the wrong person.

---

## Requirements

- Discord must be **open** on your PC when you use these commands
- The contact or channel you want to message must be added to your alias list in the Discord tab

---

## Setting Up DM Contacts

DM contacts let you send direct messages by saying a person's name.

1. Open the SH|RA UI
2. Go to the **Discord** tab
3. Under **DM Contacts**, fill in:
   - **Nickname** — what you'll say out loud (e.g. `jake`)
   - **Discord Username** — their exact Discord username (e.g. `jake#1234` or `jake` for new-style usernames)
4. Click **Add**

**To send:** Say `discord dm jake hey are you on?` — SH|RA will open Discord, navigate to their DM, and send the message.

---

## Setting Up Channel & Group DM Aliases

Channel aliases let you send to server channels or group DMs by a spoken name.

1. Open the SH|RA UI
2. Go to the **Discord** tab
3. Under **Channel & Group DM Aliases**, fill in:
   - **Nickname** — what you'll say out loud (e.g. `general`, `squad chat`)
   - **Channel ID** — the channel or group DM ID from Discord
4. Click **Add**

**To get a Channel ID:**
1. Open Discord → **User Settings** → **Advanced** → enable **Developer Mode**
2. Right-click the channel or group DM → **Copy Channel ID**

**To send:** Say `discord general anyone on?` — SH|RA navigates to that channel and sends the message.

---

## Discord Read

The read command navigates Discord to the contact or channel so you can read recent messages yourself, then automatically tabs back to your game after a configurable delay.

| Setting | Location |
|---|---|
| Read duration | Discord tab → **Read Duration** (default: 5 seconds) |

**To use:** Say `discord read jake` or `discord read general`.

> **Note:** This navigates your Discord window — make sure Discord is visible (not minimized) or this command may not work as expected.

---

## Troubleshooting

**"SH|RA said she doesn't have that person in contacts"**
- Add them in Settings → Discord → DM Contacts or Channel Aliases
- Check that the nickname you said matches exactly what you configured (SH|RA normalizes common variations but exact matches are most reliable)

**"The message sent to the wrong place"**
- This shouldn't happen — SH|RA hard-fails if the name isn't in your alias list
- If it did happen, check for duplicate or similarly-named aliases in your list

**"Nothing happens when I say discord send"**
- Make sure Discord is open and not minimized
- Check that the alias is configured in the Discord tab
