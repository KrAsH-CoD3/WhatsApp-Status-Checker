<div align="center">

# WhatsApp Status Checker

[![PyPI](https://img.shields.io/pypi/v/WhatsApp-Status-Checker?style=for-the-badge&color=25D366&logo=pypi&logoColor=white)](https://pypi.org/project/WhatsApp-Status-Checker/)
[![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white&style=for-the-badge)](https://python.org)
[![License](https://img.shields.io/github/license/KrAsH-CoD3/WhatsApp-Status-Checker?style=for-the-badge&color=888888)](https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/blob/main/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/KrAsH-CoD3/WhatsApp-Status-Checker?style=for-the-badge)](https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker)

*A stealth-first, high-performance automated monitor to track, view, and receive notifications for WhatsApp status updates in real-time.*

</div>

---

## Overview

**WhatsApp Status Checker (WSC)** automatically tracks your contacts' WhatsApp status updates the moment they're posted. It can either mark them as viewed for you (Auto-View Mode) or silently notify you without revealing you've seen them (Notification Mode)—all while staying completely undetected.

---

## Key Features

- **Real-Time Monitoring** — Catches status updates instantly via WhatsApp's native event system
- **Stealth Operation** — Advanced fingerprint masking and humanized delays keep you invisible
- **Dual Running Modes** — Auto-view with confirmation, or silent notification-only monitoring
- **Self Notifications** — Get alerts directly in your own WhatsApp chat
- **Media Downloads** — Automatically saves status photos and videos
- **Auto-Healing** — Recovers automatically from connection issues
- **Fallback Notifications** — CallMeBot API backup if direct messaging fails

---

## Running Modes

Toggle via `AUTO_VIEW` in your `.env` file:

### ⚡ Auto-View Mode (`AUTO_VIEW = True`)
Automatically views new statuses as they're posted.
- Randomized 2–5 second delays mimic human behavior
- Statuses marked as viewed on target's WhatsApp
- You receive a summary: *"ContactName: 2 new status updates viewed automatically!"*

### 🔔 Notification Mode (`AUTO_VIEW = False`)
Monitors silently without ever marking statuses as read.
- Your name stays hidden from the viewer list
- Configurable reminder intervals (30m, 1h, 3h, 6h)
- Perfect for staying informed while staying invisible

---

## Configuration

Create a `.env` file in the project root:

| Variable | Description | Required / Default |
|----------|-------------|--------------------|
| `MY_NUMBER` | Your WhatsApp number with country code (e.g. `234XXXXXXXXXX`, no `+`) | **Required** |
| `STATUS_UPLOADER_NAME` | Contact name to monitor (exactly as saved on your phone) | **Required** |
| `CALLMEBOT_APIKEY` | Fallback notification API key | Optional |
| `AUTO_VIEW` | `True` = auto-view, `False` = notify only | Optional (Default: `True`) |
| `REMINDER_TIME` | Reminder interval: `1`=30m, `2`=1h, `3`=3h, `4`=6h | Optional (Default: `1`) |
| `HEADLESS` | Run browser headless (`True` / `False`) | Optional (Default: `True`) |
| `SCREEN_WIDTH` | Spoofed viewport width (min 800) | Optional (Default: `800`) |
| `SCREEN_HEIGHT` | Spoofed viewport height (min 800) | Optional (Default: `800`) |

> **Note:** The contact in `STATUS_UPLOADER_NAME` must have an existing chat thread on your WhatsApp for the lookup to work.

---

## Installation & Setup

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### 1. Install Dependencies

<details open>
<summary><strong>Using UV (Recommended)</strong></summary>

```bash
pip install uv
uv init . && uv venv
uv add whatsapp-status-checker
```
</details>

<details>
<summary><strong>Using PIP</strong></summary>

```bash
py -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install whatsapp-status-checker
```
</details>

### 2. Fetch Anti-Detect Browser (One-Time)
```bash
uv run python -m camoufox fetch
```

### 3. Run the Application
```bash
uv run wsc
```

On first run, scan the QR code in your terminal with WhatsApp on your phone. Subsequent runs reuse the saved session.

---

## Testing

```bash
# Install test dependencies
uv sync --group test

# Run all tests
uv run pytest

# Run specific test suite
uv run pytest tests/test_realtime.py
```

---

## Technical Documentation

For architecture details, runtime patches, project structure, and migration history, see [TECHNICAL.md](TECHNICAL.md).

---

## Credits & Acknowledgments

* **[CamouChat-WhatsApp](https://github.com/CamouChat-Team/CamouChat-WhatsApp)** — Core SDK for browser orchestration and WhatsApp Web bindings
* **[Camoufox](https://github.com/daijro/camoufox)** — Hardened Firefox fork for fingerprint protection
* **[WA-JS (WPPConnect)](https://github.com/wppconnect-team/wa-js)** — Direct API hooks to WhatsApp Web internals
* **[CallMeBot](https://github.com/gabrielrih/callmebot)** — Fallback notification provider