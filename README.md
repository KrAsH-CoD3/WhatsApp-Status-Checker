# WhatsApp Status Checker

[![Anti-Detection](https://img.shields.io/badge/CamouChat-WhatsApp-orange?style=for-the-badge)](https://github.com/CamouChat-Team/CamouChat-WhatsApp)
[![Engine](https://img.shields.io/badge/API-WA--JS-blue?style=for-the-badge)](https://github.com/wppconnect-team/wa-js)
[![Status](https://img.shields.io/badge/Release-v0.2.0-green?style=for-the-badge)](#)

A modern, highly resilient, stealth-focused **WhatsApp Status Checker** which monitors target contacts, automatically views their status updates, and sends immediate encrypted notification alerts.

---

## Features

* **Camoufox Browser**: Advanced canvas, WebGL, screen, and user-agent spoofing to bypass modern anti-bot at the lowest levels.
* **WA-JS Internal Engine**: Interacts directly with WhatsApp's underlying React/Webpack context. Zero fragile XPath DOM scraping.
* **Dual Run Modes**: Choose between Auto-View (watches updates within seconds of upload) and Notification Mode (receive alerts via [CallMeBot](https://github.com/gabrielrih/callmebot)).
* **Smart Read Receipts**: Optimized non-blocking seen receipts utilizing accurate timestamp fallbacks for both text and media statuses.
* **Profile Isolation**: Fully managed, encrypted session profiles to secure your login state across application runs.
* **Organic Behavior Guardrails**: Randomized human-like action delays (2-5s) and strict rate limit checks to ensure safety.

---

## ⚙️ Configuration (`.env`)

Configure the application by creating a `.env` file in the root directory:

```env
MY_NUMBER = 234xxxxxxxxxx              # Your WhatsApp phone number (with country code excluding the + sign)
CALLMEBOT_APIKEY = xxxxxxx             # CallMeBot API key for notifications
STATUS_UPLOADER_NAME = "NameOfContact" # Contact name to monitor
HEADLESS = False                       # Set to True at first for QR login, then False after successful login to run in background
SCREEN_WIDTH = 800                     # Spoofed viewport width (min 800) - OPTIONAL
SCREEN_HEIGHT = 800                    # Spoofed viewport height - OPTIONAL
```

---

## Installation & Setup

### 1. Install Dependencies
This project uses `uv` to manage python environments and dependencies securely:
```bash
# Sync and install environment
uv sync
```

### 2. Fetch Hardened Browser (One-Time Setup)
Download the anti-detect CamouChat browser core engine:
```bash
uv run python -m camoufox fetch
```

### 3. Launch the Checker
Start the application CLI:
```bash
uv run wsc
```

---

## Running Modes

Upon executing `wsc`, you will configure the checking sequence interactively:

```
[Y] Notification Mode - Get alerted when they post.
[N] Auto-View Mode - Automatically 'watch' their stories.
```

### 1. Notification Mode (`Y`)
Checks the status feed of the target contact at scheduled intervals (30m, 1h, 3h, 6h). If updates are found, it triggers a [CallMeBot](https://github.com/KrAsH-CoD3/gabrielrih-callmebot) alert directly to your WhatsApp without marking their status as read.

### 2. Auto-View Mode (`N`)
Monitors the target feed continuously in the background (polling every 60 seconds). When a new story is uploaded, it views it automatically and registers your profile on the uploader's viewer list instantly.

---

## Stealth & Anti-Ban Measures

To keep automated accounts highly secure, the runtime implements:
* **Humanized View Delays**: Random pauses (2,000ms to 5,000ms) before clicking or marking updates read.
* **Strict Message Rate Limiting**: Minimum 10-second spacing between any outgoing message calls.
* **Min Viewport Size**: Spoofs realistic standard layout screens (800x800 minimum) to prevent responsive layout detection.
* **Hidden Global Namespace**: Deletes injected handles from `window.WPP` to ensure total code isolation.

---

## Migration History
For detailed engineering insights and architectural differences between the Selenium codebase and the CamouChat version, see [MIGRATION.md](MIGRATION.md).

---

## Credits & Acknowledgments
* **Heavy Lifter**: The bulk of the migration effort and infrastructure support was made possible by **[CamouChat-WhatsApp](https://github.com/CamouChat-Team/CamouChat-WhatsApp)**, a highly robust SDK designed for high-efficiency Webpack hijacking and anti-bot stealth.
* **Hardened Browser Core**: **CamouChat-WhatsApp** uses **[Camoufox](https://github.com/daijro/camoufox)** which provides advanced fingerprint masking and canvas/WebGL spoofing under the hood.
* **API Wrapper**: **[WA-JS (WPPConnect)](https://github.com/wppconnect-team/wa-js)** provides the JavaScript API hooks used to access WhatsApp Web internal stores.