# Technical Documentation

This document contains the complete technical reference for WhatsApp Status Checker: architecture, internals, migration history, and implementation details.

---

## System Architecture

WhatsApp Status Checker connects a Python control layer to a headless instance of WhatsApp Web running in a hardened, fingerprint-spoofed browser.

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

### Execution Flow

1. **Session Initialization**: The app starts the browser and checks for authentication. If not logged in, it prints a clean terminal QR code for a one-time scan.
2. **WebSocket Subscriptions**: Once logged in, WSC injects a JavaScript event handler into the browser environment that listens directly to the native WhatsApp WebSocket connection for incoming status uploads.
3. **Event Forwarding**: When the target contact uploads a status, the WebSocket handler intercepts the event instantly and logs it to the browser console. WSC captures the console log inside Python to trigger processing.
4. **Action & Notification**: Depending on the configured **Running Mode**, the application either automatically marks the statuses as viewed (using human-like delays) or notifies you of the status count, followed by a direct WhatsApp notification sent to your own phone number.

---

## Key Technical Features

- **Real-Time WebSocket Listener**: Listens to native WhatsApp WebSocket events (`window.__statusStoreAddHandler`). No polling loops or excessive requests under normal operation.
- **Auto-Healing Health Loop**: Background async thread that periodically verifies event listener integrity, automatically re-injects lost handler bindings, and falls back to smart polling if the real-time websocket channel is disrupted.
- **Anti-Detection & Stealth Layer**: Integrates advanced user-agent, canvas, and WebGL fingerprint spoofing using Camoufox. Includes humanized delay simulation (2s–5s randomized pauses) and namespaces cleaning to purge injected handles from the `window` scope.
- **Dual-Channel Self-Notification**: Delivers notifications using a primary direct-to-self messaging mechanism through the WA-JS `InteractionController`, with an automated HTTP API fallback to **CallMeBot**.
- **Robust Patching Layer**: Monkey-patches crucial parts of the WhatsApp Web lifecycle to resolve QR code rendering, session detection state transitions, and status-fetch edge cases dynamically.
- **Media Download Support**: Fully integrates with `MediaController` within `WhatsAppOperations` to support downloading status media files directly.

---

## Runtime Monkey-Patches (`src/whatsapp_status_checker/core/patches.py`)

To guarantee seamless integration and stealth, WSC dynamically applies the following patches at runtime:

1. **Stealth Fingerprints**: Overrides Camoufox config generation to randomize Canvas, WebGL, Screen sizes, and User-Agents safely.
2. **Terminal QR Code**: Replaces the default QR code display loop with a custom terminal-formatted renderer to ensure scannability.
3. **Session Start Lifecycle**: Enhances authentication state checks to reliably detect session transitions and page initialization.
4. **Wapi Bridge Extensions**: Extends native `status_get` and `status_send_read` bindings with isolated error-handling wrappers.
5. **Log Filtering**: Employs `FriendlyFormatter` to suppress irrelevant browser messages and highlight actionable status tracker events.

---

## Project Layout

```
src/whatsapp_status_checker/
├── __init__.py
├── __main__.py                    # CLI entry point (exposes 'wsc' command)
├── config.py                      # Environment configuration manager
├── core/
│   ├── __init__.py
│   ├── app.py                     # Main WhatsAppStatusChecker event loop
│   ├── patches.py                 # Stealth, QR login, and Wapi bridge monkey-patches
│   └── whatsapp_operations.py     # Unviewed status fetching, reading, and media management
└── utils/
    ├── __init__.py
    └── helpers.py                 # Timing, scheduling, and formatting helpers
```

---

## Migration History: Selenium → CamouChat

### Architectural Shift

The legacy application relied on Selenium WebDriver to automate Google Chrome, using complex XPath selectors to navigate the WhatsApp Web DOM. This approach was highly fragile, prone to breaking on minor WhatsApp UI updates, and easily detectable by anti-bot systems.

The migrated system shifts to an **API-driven stealth model** powered by **CamouChat**:

1. **[CamouChat-WhatsApp](https://github.com/CamouChat-Team/CamouChat-WhatsApp)** does the heavy lifting: orchestrating the under-the-hood **Camoufox** browser engine, applying realistic browser fingerprints, and injecting the WA-JS library directly into the WhatsApp Webpack context.
2. Direct API interaction bypasses the DOM entirely, executing native Backbone.js actions on in-memory stores (`StatusV3Store`).
3. We introduced a **custom surgical patch layer** over CamouChat where default behaviors fell short for continuous background monitoring.

```
graph TD
    subgraph legacy [Legacy Architecture]
        A[Selenium Script] -->|XPath Scraping| B[WhatsApp Web DOM]
        B -->|Unstable UI Poll| C[Detect and Click UI Elements]
    end

    subgraph modern [CamouChat and Patch Layer]
        D[WhatsApp Status Checker] -->|Framework Control| E[CamouChat SDK]
        E -->|Fingerprint and Sandbox| F[Camoufox Browser Core]
        D -->|Custom Patches| G[Surgical Patch Layer]
        G -->|Accurate Receipt Handshake| H[WA-JS Webpack context]
    end
```

### Component-Level Comparison

| Feature | Legacy System (Selenium) | Migrated System (CamouChat & Patch Layer) |
| :--- | :--- | :--- |
| **Orchestration SDK** | Custom Selenium wrappers | **CamouChat-WhatsApp** (Direct WhatsApp API) |
| **Automation Driver** | Selenium WebDriver (Chrome) | Hardened Camoufox Firefox engine managed by CamouChat |
| **Data Extraction** | UI/DOM XPath selectors (`//div[...]`) | Native memory queries via `WapiSession` interface |
| **Mark Viewed** | Simulating physical page clicks | Backbone seen receipt stanza transmission |
| **Session Control** | Standard Chrome profile directories | Isolated, platform-bound `ProfileManager` sandbox |
| **Execution Loop** | Synchronous element polling | Non-blocking asynchronous event evaluations |

### Critical Custom Patches

While **CamouChat-WhatsApp** provided the foundational platform, background status tracking required custom engineering patches to remain resilient and silent:

#### 1. Robust Non-Blocking View Receipts

Marking a status as read in WhatsApp Web requires a strict two-way handshake with the server. In headless connections, this handshake frequently hangs or is throttled by the socket, causing standard automation integrations to block indefinitely and eventually timeout.

**Our Patch**:
* **Asynchronous Racing**: Wrapped read receipt execution in a 4-second `Promise.race` wrapper so execution loops never freeze.
* **Timestamp Restructuring**: Fixed a critical design issue where text status updates without a `mediaKeyTimestamp` were silently rejected by WhatsApp servers. The patch extracts the message creation epoch (`msgObj.t`) as a fallback:
  ```javascript
  const timestamp = msgObj.mediaKeyTimestamp || msgObj.t;
  await collection.sendReadStatus(msgObj, timestamp);
  ```
* **Instant State Sync**: Marks status viewed locally instantly, preventing repeat processing while letting the network receipt transmit asynchronously.

#### 2. Viewport & Screen Sizing Override

WhatsApp Web dynamically modifies its structural layout if screen resolutions drop below standard bounds. To ensure layout stability while spoofing realistic devices, our patch repairs browser engine sizing to support the custom `.env` dimensions securely.

### Migration Phases (Completed)

#### ✅ Phase 1: Proof of Concept
- [x] Set up CamouChat-WhatsApp plugin
- [x] Implement single status viewer using internal API
- [x] Basic notification logic

#### ✅ Phase 2: Core Features
- [x] Replace all XPath-based operations with wa-js API calls
- [x] Implement notification modes (30m, 1h, 3h, 6h intervals) via `.env`
- [x] Add ProfileManager for session persistence
- [x] Integrate CallMeBot for external notifications

#### ✅ Phase 3: Hardening & Cleanup
- [x] Refactor patches for QR Code injection and session management fixes
- [x] Remove all redundant Selenium `vars.py` and old dependencies
- [x] Modularize test suite (`test_realtime.py`, `test_status_processing.py`, `test_health.py`, `test_modes.py`)
- [x] Validate anti-ban measures (humanized delays, proper headers)

---

## Risk Mitigation

### WhatsApp ToS Compliance
- **Mitigation Active**: 
  - Humanized delays (randomized 2-5s between actions)
  - Rate limiting logic embedded in the `whatsapp_operations.py` core
  - Safe, stealth-first viewport configurations

### Technical Risks Handled
- **API changes**: Handled via centralized `patches.py` which dynamically injects fixes to `wa-js` and `camoufox` runtime behavior without waiting for upstream package updates.
- **Profile corruption**: Handled securely via `ProfileManager`.

---

## Success Metrics Achieved
- [x] Zero XPath selectors in codebase
- [x] Headless and Headful modes successfully tested
- [x] Legacy code completely purged from the repository
- [x] Test coverage ensures core polling/notification loop resilience

---

## Testing

The project contains a fully mocked test suite that simulates browser and WebSocket operations without launching a live browser or hitting WhatsApp Web:

```bash
# Install test group dependencies
uv sync --group test

# Run all test suites
uv run pytest

# Run a specific test suite
uv run pytest tests/test_realtime.py
```

---

## Credits & Acknowledgments

* **[CamouChat-WhatsApp](https://github.com/CamouChat-Team/CamouChat-WhatsApp)** — The core SDK driving browser orchestration, WA-JS bindings, and profile isolation. The heavy lifter for migration infrastructure.
* **[Camoufox](https://github.com/daijro/camoufox)** — Hardened Firefox fork providing browser fingerprint protection.
* **[WA-JS (WPPConnect)](https://github.com/wppconnect-team/wa-js)** — Direct API hooks to interact with WhatsApp Web's underlying stores.
* **[CallMeBot](https://github.com/gabrielrih/callmebot)** — Dynamic API notifications fallback provider.