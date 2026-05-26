<div align="center">

# WhatsApp Status Checker

<!-- [![Test PyPI](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ftest.pypi.org%2Fpypi%2Fwhatsapp-status-checker%2Fjson&query=%24.info.version&label=Test%20PyPI&color=blue&logo=pypi&style=for-the-badge)](https://test.pypi.org/project/whatsapp-status-checker/) -->
[![PyPI](https://img.shields.io/pypi/v/WhatsApp-Status-Checker?style=for-the-badge)](https://pypi.org/project/WhatsApp-Status-Checker/)
[![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white&style=for-the-badge)](https://python.org)
[![License](https://img.shields.io/github/license/KrAsH-CoD3/WhatsApp-Status-Checker?color=white&style=for-the-badge)](https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/blob/main/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/KrAsH-CoD3/WhatsApp-Status-Checker?style=for-the-badge)](https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker)

*A high-performance, automated tool to continuously monitor and interact with WhatsApp statuses.*

</div>

A stealth-first **WhatsApp Status Checker** that monitors target contacts using a real-time event-driven architecture. It automatically views status updates the instant they are posted, and sends you a WhatsApp message notification confirming the action — all without the target ever knowing.

Built on the [CamouChat-WhatsApp](https://github.com/CamouChat-Team/CamouChat-WhatsApp) SDK, which provides a hardened [Camoufox](https://github.com/daijro/camoufox) browser with advanced fingerprint masking and a [WA-JS](https://github.com/wppconnect-team/wa-js) bridge for direct access to WhatsApp Web's internal stores.

---

## Features

* **Real-Time Event-Driven**: Listens to WhatsApp's native WebSocket status store events. No polling loops needed — the checker reacts within seconds of a new status upload.
* **Health-Monitored Fallback**: A background health loop verifies listener integrity, automatically re-injects lost event handlers, and falls back to smart polling only when real-time goes stale.
* **Dual Run Modes**: Choose between **Auto-View** (watches and marks statuses as seen instantly) and **Notification** (alerts you without opening the status).
* **Self-Notification**: Both modes send you a WhatsApp message to your own number confirming the action taken — either via direct WA-JS messaging or [CallMeBot](https://github.com/gabrielrih/callmebot) as a fallback.
* **Anti-Detection Browser**: Uses [Camoufox](https://github.com/daijro/camoufox) with canvas, WebGL, screen, and user-agent spoofing to bypass modern anti-bot detection.
* **WA-JS Internal Engine**: Interacts directly with WhatsApp's underlying React/Webpack context. Zero fragile XPath or DOM scraping.
* **Smart Read Receipts**: Non-blocking viewed receipts with accurate timestamp fallbacks for both text and media statuses.
* **Profile Isolation**: Encrypted, persistent session profiles managed via `ProfileManager` to secure login state across runs.
* **Humanized Behavior**: Randomized delays (2–5s) and strict rate limiting (10s minimum between messages) to mimic organic usage patterns.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WhatsApp Web (Browser)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Status Store │  │ Contact List │  │  Chat Store       │  │
│  │  (wa-js)     │  │  (wa-js)     │  │  (wa-js)          │  │
│  └──────┬───────┘  └──────────────┘  └───────────────────┘  │
│         │ WebSocket event                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────┐                       │
│  │ JS Event Listener (Main World)   │                       │
│  │ window.__statusStoreAddHandler   │                       │
│  └──────┬───────────────────────────┘                       │
└─────────┼───────────────────────────────────────────────────┘
          │ console bridge → [StatusCheckerEvent]:jid
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python Application                       │
│                                                             │
│  ┌────────────────────┐    ┌─────────────────────────────┐  │
│  │  _handle_browser_  │───▶│   _handle_realtime_status_  │  │
│  │      console()     │    │         event(jid)          │  │
│  └────────────────────┘    └──────────┬──────────────────┘  │
│                                       │                     │
│                                       ▼                     │
│                            ┌─────────────────────┐          │
│                            │ _process_statuses() │          │
│                            │ ┌─────────────────┐ │          │
│                            │ │  autoview: view │ │          │
│                            │ │  notify_self()  │ │          │
│                            │ │                 │ │          │
│                            │ │  notification:  │ │          │
│                            │ │  notify_self()  │ │          │
│                            │ └─────────────────┘ │          │
│                            └─────────────────────┘          │
│                                       ▲                     │
│                                       │ fallback poll       │
│                            ┌──────────┴──────────┐          │
│                            │   _health_loop()    │          │
│                            │ _verify_listeners() │          │
│                            └─────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

Create a `.env` file in the project root:

```env
MY_NUMBER = 234xxxxxxxxxx              # Your WhatsApp number (with country code, no + sign)
CALLMEBOT_APIKEY = xxxxxxx             # CallMeBot API key (fallback notification method)
STATUS_UPLOADER_NAME = "ContactName"   # Contact name to monitor (case-sensitive, as saved on your phone)
AUTO_VIEW = True                       # True = Auto-View Mode, False = Notification Mode - Optional
REMINDER_TIME = 1                      # Notification interval: 1=30min, 2=1hr, 3=3hrs, 4=6hrs - Optional
HEADLESS = True                        # True to run in background/without opening browser window - Optional
SCREEN_WIDTH = 800                     # Spoofed viewport width (min 800) — optional
SCREEN_HEIGHT = 800                    # Spoofed viewport height (min 800) — optional
```

> **Note:** `STATUS_UPLOADER_NAME` must match exactly as saved in your phone contacts. The app resolves names to WhatsApp JIDs by searching both your Chat Store and Contact List. Ensure you have an active chat history with the target contact.

---

## Installation & Setup

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### 1. Install Dependencies

- <details open>
    <summary>Using UV(Recommended)</summary>
    
    - Install UV if you haven't using `pip install uv`
    - Initialize and create virtual environment using `uv init . && uv venv`
    - Install package using `uv add whatsapp-status-checker`
  </details>
  
- <details>
    <summary>Using PIP</summary>
    
    - Create a Virtual Environment using `py -m venv .venv`
    - Activate your virtual environment using `.venv\Scripts\activate`
    - Install dependencies using `pip install whatsapp-status-checker`
  </details>


### 2. Fetch Anti-Detect Browser (One-Time)
Download the hardened Camoufox browser engine:
```bash
uv run python -m camoufox fetch
```

### 3. Run
```bash
uv run wsc
```

---

## Running Modes

Both modes use the same real-time event-driven architecture. The mode is set via the `AUTO_VIEW` variable in your `.env`:

### ⚡ Auto-View Mode (`AUTO_VIEW = True`)

Monitors the target contact's status feed in real-time. When a new status is uploaded:
1. The JS event listener detects the WebSocket push instantly.
2. The Python callback fetches all unviewed statuses via the WA-JS bridge.
3. Each status is automatically viewed with humanized delays.
4. A confirmation message is sent to your own WhatsApp number:
   > ContactName: 2 new status updates viewed automatically!
   > 📅 06:42:27

### 🔔 Notification Mode (`AUTO_VIEW = False`)

Monitors the target contact without viewing their statuses. When updates are detected:
1. You receive a WhatsApp alert with the count and timestamp.
2. Statuses are **not** marked as viewed — your profile stays hidden.
3. Reminder alerts are sent at intervals defined by `REMINDER_TIME` for statuses that remain unviewed.
4. De-duplication logic prevents repeated alerts for the same status.

### Notification Delivery

Both modes send alerts via:
1. **Direct WhatsApp Message** (primary) — sent to your own number using the WA-JS `InteractionController`.
2. **CallMeBot** (fallback) — if direct messaging fails, alerts are routed through the [CallMeBot](https://github.com/gabrielrih/callmebot) API.

---

## Stealth & Anti-Ban Measures

| Layer | Protection |
|-------|-----------|
| **Browser** | Camoufox with canvas, WebGL, screen, and UA fingerprint spoofing |
| **View Delays** | Randomized 2,000ms–5,000ms pauses before marking statuses as viewed |
| **Rate Limiting** | 10-second minimum spacing between outgoing message calls |
| **Viewport** | Spoofed realistic screen dimensions (800×800 minimum) |
| **Namespace** | Injected WA-JS handles cleaned from `window` scope after use |
| **Patches** | Runtime monkey-patches fix QR code rendering, session detection, and wa-js edge cases without waiting for upstream releases |

---

## Project Structure

```
src/whatsapp_status_checker/
├── __init__.py
├── __main__.py                    # CLI entry point (wsc command)
├── config.py                      # Environment variable loader
├── core/
│   ├── app.py                     # WhatsAppStatusChecker — main controller
│   ├── patches.py                 # Runtime patches for QR, session management, and wa-js fixes
│   └── whatsapp_operations.py     # Status fetch, view, and receipt logic
└── utils/
    └── helpers.py                 # Scheduler and notification reminder helper functions
tests/
├── conftest.py                    # Shared fixtures, external dependency mocking
├── test_realtime.py               # Real-time event callback and integration tests
├── test_status_processing.py      # Status fetch, view, and error handling tests
├── test_health.py                 # Listener verification and health loop tests
└── test_modes.py                  # Mode entry point tests
```

---

## Testing

The test suite is fully mocked — no browser, network, or WhatsApp session required:

```bash
# Install test dependencies
uv sync --group test

# Run all tests
uv run pytest

# Run a specific test module
uv run pytest tests/test_realtime.py
```

---

## Migration History

This project was fully migrated from a Selenium + XPath-based architecture to the CamouChat SDK. For detailed engineering insights, architectural comparisons, and phase-by-phase breakdown, see [MIGRATION.md](MIGRATION.md).

---

## Credits & Acknowledgments

* **[CamouChat-WhatsApp](https://github.com/CamouChat-Team/CamouChat-WhatsApp)** — The SDK powering the browser automation, WA-JS bridge, session management, and anti-detection layer.
* **[Camoufox](https://github.com/daijro/camoufox)** — Hardened Firefox fork providing advanced fingerprint masking and canvas/WebGL spoofing.
* **[WA-JS (WPPConnect)](https://github.com/wppconnect-team/wa-js)** — JavaScript API hooks for accessing WhatsApp Web's internal Webpack stores.
* **[CallMeBot](https://github.com/gabrielrih/callmebot)** — Fallback notification delivery via WhatsApp messages.