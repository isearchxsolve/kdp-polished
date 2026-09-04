# Tech Setup Document
## Automated KDP Publishing via Kilo + MCP + Chrome DevTools Protocol

**Date:** September 4, 2026
**Use case:** End-to-end automation of Amazon KDP title setup — eBook + paperback creation, file uploads, AI disclosures, pricing, publishing, and series management — for The Beholder Project (8 titles, 12+ formats).

---

## 1. Architecture Overview

```
+-------------------+        MCP (stdio)        +--------------------------+
|   Kilo CLI agent  | <------------------------> |  chrome-devtools MCP     |
|  (GLM model, the  |                            |  chrome-devtools-mcp     |
|   "engineer")     |                            |  (Node, npx)             |
+-------------------+                            +------------+-------------+
                                                              |
                                                    DevTools Protocol (CDP)
                                                    ws://127.0.0.1:9223
                                                              |
                                                   +----------v-----------+
                                                   |  Dedicated Chrome    |
                                                   |  (logged into KDP)   |
                                                   |  D:\kdp-chrome-profile|
                                                   +----------------------+
```

Three layers:
1. **Kilo (AI agent)** — reads the task, decides what to click/fill/upload, interprets page snapshots.
2. **chrome-devtools MCP server** — the bridge. Exposes browser-control tools as callable functions to the agent. Talks to Chrome over the **Chrome DevTools Protocol (CDP)**.
3. **A dedicated Chrome instance** — launched with remote debugging enabled, holding the persistent, logged-in KDP session.

---

## 2. The Dedicated Chrome Instance

Launched manually (or via a launcher) before any automation session:

```powershell
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  -ArgumentList '--remote-debugging-port=9223', `
                '--user-data-dir=D:\kdp-chrome-profile'
```

**Key decisions:**

| Setting | Value | Why |
|---|---|---|
| Debug port | `9223` (not the default 9222) | Avoids collision with any other CDP instance; a deliberate, known port |
| User data dir | `D:\kdp-chrome-profile` | **Isolated profile** — cookies, KDP login, Google sign-in persist across sessions. Never polluted by daily browsing |
| Automation flags | **None** (`--headless`, `--disable-blink-features=AutomationControlled` etc. all omitted) | A normal, headed Chrome. Google sign-in and Amazon login flows work without bot-detection friction |
| Runtime | Chrome 152.0.7977.75 (Windows) | Current stable at time of setup |

Because the profile persists, the KDP login survives reboots. Each work session only requires relaunching Chrome with the same two flags.

---

## 3. MCP Configuration

In `C:\Users\Admin\.config\kilo\kilo.jsonc`:

```jsonc
"mcp": {
  "chrome-devtools": {
    "command": "npx",
    "args": [
      "chrome-devtools-mcp@latest",
      "--browser-url=http://127.0.0.1:9223"
    ]
  }
}
```

- `chrome-devtools-mcp` is Google's official MCP server for Chrome DevTools (installed on demand via npx, always latest).
- `--browser-url=http://127.0.0.1:9223` tells the MCP server to **attach to the already-running Chrome** instead of spawning its own. This is what makes the persistent login profile usable by the agent.

MCP itself is the **Model Context Protocol** — a standard that lets AI agents call tools (functions) exposed by a server. The agent doesn't "see" the screen like a human; it calls tools and reads structured results.

---

## 4. The Toolset (what the agent actually used)

| Tool | Purpose in the KDP flow |
|---|---|
| `list_pages` | Health check ("check mcp") — verifies Chrome is up and the KDP session is alive |
| `navigate_page` | Go to bookshelf, title-setup forms, series page |
| `take_snapshot` | The workhorse. Returns the page as an **accessibility tree** with stable `uid`s for every element — forms, buttons, dropdowns, dialogs |
| `click` | Buttons, radio buttons, accordions, category picker, drag targets |
| `fill` / `fill_form` | Batch-fills textboxes (title, subtitle, author, 7 keyword slots, prices) and native `<select>` dropdowns; `value: "true"` ticks checkboxes/radios |
| `type_text` | Rich-text description editors (CKEditor iframes) — click into the editor, then type |
| `upload_file` | EPUB, print PDF, JPG cover, wraparound PDF via the file-chooser |
| `press_key` | `Tab` after price entry to trigger KDP's on-blur royalty recalculation |
| `wait_for` | Blocks until upload success text / dialog text appears (uploads and conversions are slow) |
| `evaluate_script` | Escape hatch — ran raw JS (e.g., inspecting how KDP's custom dropdowns are built when normal fills failed) |
| `list_console_messages` / `get_network_request` | Diagnosing failed uploads (not needed in the final run) |

**Core loop:** snapshot → pick `uid`s → fill/click → snapshot again to verify → proceed.

---

## 5. The Automated KDP Workflow (as executed)

Per title, driven from `D:\empty\KDP-POLISHED\KDP-FILL-GUIDE.txt` (values) and saved project memory (decisions):

1. **Bookshelf → + Create new title or series → Kindle eBook**
2. **Details tab** — language, title, subtitle, author/contributor, description (rich text), publishing rights, adult content = No, marketplace = Amazon.com, up to 3 category placements via the picker, 7 keywords
3. **Content tab** — DRM = No, upload EPUB, wait for "Manuscript check complete", upload JPG cover, AI-generated content questions, accuracy checkbox
4. **Pricing tab** — royalty plan 70%, USD price, world rights, no KDP Select, **Publish**
5. **Paperback** (from the same title) — free KDP ISBN, 6×9 in, no bleed, B&W **cream** paper, matte cover, upload print PDF + wraparound cover PDF, AI questions, **Launch Print Previewer → Approve**, price, publish
6. **Series** — Add existing title (main vs related content), reading order auto-assigned

---

## 6. Constraints & Lessons Learned (the real-world notes)

1. **Upload paths must be inside the agent's workspace roots.** Files in `D:\empty\KDP-POLISHED\...` were rejected by the upload tool (`Access denied: path ... not within any of the configured workspace roots`). Fix: `Copy-Item` the manuscript/cover into `D:\anonym\` first, upload from there.
2. **First manuscript upload sometimes fails silently** ("Failed manuscript upload" right after the file chooser). Retrying the exact same upload succeeds. Never assume the first attempt is fatal.
3. **KDP's AI-question dropdowns are not native `<select>` elements** — they are custom listbox widgets. The `fill` tool times out. Fix: `click` the widget to open it, take a snapshot, `click` the option inside the popup.
4. **KDP requires print-preview approval** before "Save and Continue" unlocks on paperback content. The Previewer runs in the same page flow; the agent waits for the "Approve" button and clicks it.
5. **Author last name is mandatory** even for one-word pen names. "Claude" alone failed validation; "Claude (Anthropic)" (first + last) worked and matches the book's attribution.
6. **Category pickers differ between eBook and paperback forms** — the paperback Books tree offers different placements (e.g., Poetry › Single Authors) than the eBook tree (no Philosophy of Science exists anywhere under History & Philosophy). Always re-pick per format from the live tree.
7. **Series book numbers are never a form field.** They are auto-assigned by insertion position when adding a title; main vs related content is chosen in the add-flow, not afterwards. ("Edit series details" only edits title/description/reading-order display.)
8. **Checkbox semantics:** `fill` with `value: "true"` ticks radios/checkboxes; for KDP's custom listboxes it silently does nothing — verify with a fresh snapshot after every interaction.
9. **KDP auto-converts marketplace prices** from the primary (Amazon.com) price on blur — no need to click per-marketplace "Base on" buttons unless overriding.
10. **The user-data-dir profile is the login vault.** With it, every "check mcp" session lands directly on the KDP bookshelf, already authenticated. Never add headless/automation flags — they break Google sign-in.

---

## 7. Reproducing the Setup From Scratch

```powershell
# 1. One-time: create the dedicated profile dir (any location)
New-Item -ItemType Directory -Force D:\kdp-chrome-profile

# 2. Every session: launch Chrome with CDP enabled
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  -ArgumentList '--remote-debugging-port=9223','--user-data-dir=D:\kdp-chrome-profile'

# 3. One-time inside that window: log into amazon.kdp.amazon.com (manual, once)

# 4. In kilo.jsonc, register the MCP (see section 3), then start Kilo.
# 5. Say "check mcp" — agent verifies the connection and lands on the bookshelf.
```

**Session verification ritual:** `list_pages` → snapshot of the bookshelf → confirm all titles and their statuses → proceed with the day's work.

---

## 8. What This Stack Is

- **MCP (Model Context Protocol):** open standard for exposing tools/data to AI agents over stdio/HTTP.
- **chrome-devtools-mcp:** Google's official MCP server wrapping the Chrome DevTools Protocol.
- **CDP:** the same protocol Chrome's own DevTools uses — page tree, DOM, input events, file choosers, storage — exposed over a WebSocket on the debug port.
- **Kilo:** the orchestrating agent that turns plain-language intent ("create Book 06, $5.99") into a verified sequence of clicks, fills, and uploads — with snapshots confirming every step before moving on.

*Prepared by Kilo — the whole Beholder shelf (Books 01–08, eBook + paperback) went from guide to submitted using exactly this setup.*
