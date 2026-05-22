<div align="center">

# WhatsApp Status Checker

*A high-performance, automated tool to continuously monitor and interact with WhatsApp statuses.*

<!-- [![Test PyPI](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ftest.pypi.org%2Fpypi%2Fwhatsapp-status-checker%2Fjson&query=%24.info.version&label=Test%20PyPI&color=blue&logo=pypi)](https://test.pypi.org/project/whatsapp-status-checker/) -->
[![PyPI](https://img.shields.io/pypi/v/WhatsApp-Status-Checker)](https://pypi.org/project/WhatsApp-Status-Checker/)
[![Python Version](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/github/license/KrAsH-CoD3/WhatsApp-Status-Checker?color=blue)](https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/blob/main/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/KrAsH-CoD3/WhatsApp-Status-Checker)](https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker)

<br/>

![WhatsApp Status Checker](https://raw.githubusercontent.com/KrAsH-CoD3/WhatsApp-Status-Checker/main/static/images/WhatsApp%20Status%20Checker.png)

</div>

WhatsApp Status Checker is a high-performance tool designed to continuously monitor and interact with WhatsApp statuses. It can automatically view a specific contact's status (Images, Videos, Text, or Audio) as soon as they are uploaded, ensuring every update is registered as "viewed" even on slow internet connections. Alternatively, it can function in a notification-only mode, alerting you via WhatsApp at your preferred intervals (30m, 1h, 3h, 6h).

> _**NOTE:** WhatsApp does not allow bots or unofficial clients on their platform, so this shouldn't be considered totally safe._

## Demo Video

![WhatsApp Status Checker Demo](https://raw.githubusercontent.com/KrAsH-CoD3/WhatsApp-Status-Checker/main/static/images/Demo.webp)

View HD Demo Video [here](https://raw.githubusercontent.com/KrAsH-CoD3/WhatsApp-Status-Checker/main/static/videos/Demo.mp4)

<details>
<summary><b><font size="4">AI Auto-Healing (Deprecation)</font></b></summary>

While we explored implementing an AI-powered "Auto-Healing" mechanism to dynamically resolve broken XPaths, it has been intentionally deprecated. WhatsApp Web is a "heavy" application with highly dynamic DOM structures, making automated path resolution unreliable and performance-heavy. 

To ensure the bot remains stable and reliable, we manually maintain and update the XPaths using an **accessibility-first** approach (targeting ARIA labels and attributes). This makes the locators significantly more resilient to UI updates and provides the consistency required for heavy applications like WhatsApp.
</details>

## WhatsApp Messenger

[CallMeBot] was used for WhatsApp message, **PLEASE READ!**

# How to use

Make sure your installed Google Chrome Browser is the latest.

  - Create a `.env` file.
    - Set `MY_NUMBER` to your phone number. (Your WhatsApp Number e.g: 234xxxxxxxxxx)
    - Set `CALLMEBOT_APIKEY` to your API Key. (API Key provided by CallMeBot)
      > See [CallMeBot] for detailed information.
    - Set `STATUS_UPLOADER_NAME` contact you want to view their status. 
      > NOTE: As it is saved on your phone(Case Sensitive).
    - **Optionally**, set `TIMEZONE` to your preferred timezone. Time will be displayed in this timezone.
      > If not set, it resolves to IP timezone.
  
  ## Installation
  - <details>
      <summary>Using UV</summary>
      
      - Install UV if you haven't already using `pip install uv`
      - Initialize and create virtual environment using `uv init . && uv venv`
      - Install package using `uv add whatsapp-status-checker`
    </details>
    
  - <details>
      <summary>Using PIP</summary>
      
      - Create a Virtual Environment using `py -m venv .venv`
      - Activate your virtual environment using `.venv\Scripts\activate`
      - Install dependencies using `pip install whatsapp-status-checker`
    </details>
  
  ## Usage

  ### CLI (Recommended)
  
  You can run the application directly from the terminal using the `wsc` alias:

  - <details>
      <summary>Using UV</summary>
      
      ```bash
      uv run wsc
      ```
    </details>
    
  - <details>
      <summary>Using Python</summary>
      
      ```bash
      python -m whatsapp_status_checker
      ```
      *Or if the package is already installed in your path:*
      ```bash
      wsc
      ```
    </details>

  ### Python Script
  
  Alternatively, you can import and run it in your own Python script:
  
  ```python
  from whatsapp_status_checker import WhatsAppStatusChecker

  def main():
      # Create and run application
      app = WhatsAppStatusChecker()
      app.run()

  if __name__ == "__main__":
      main()
  ```
  </details>


## Screenshots

### Terminal | First Time Logging In
![WhatsApp first time log in](https://raw.githubusercontent.com/KrAsH-CoD3/WhatsApp-Status-Checker/main/static/images/WhatsApp%20first%20time%20log%20in.png)
#
### Terminal | Viewed Contact Status 
![WhatsApp subsequent log in view status 2](https://raw.githubusercontent.com/KrAsH-CoD3/WhatsApp-Status-Checker/main/static/images/WhatsApp%20subsequent%20log%20in%20view%20status%202.png)
#
### WhatsApp Message | Status Notification
![WhatsApp first time log in](https://raw.githubusercontent.com/KrAsH-CoD3/WhatsApp-Status-Checker/main/static/images/WhatsApp%20Notification%20Status%20Message.png)
### See other Screenshots, [Click here](https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/tree/main/static/images)

## Errors and Fixes

- **Timeout When Logging in:** The application now uses an efficient 3-minute (180s) polling loop that handles QR code scanning and transient loading screens automatically.
  > If you consistently timeout, ensure your internet connection is stable.
- **Not Receiving WhatsApp Message:** Make sure you follow [CallMeBot] instructions carefully.
  > Also confirm your `.env` values are correct.

## Support and Contribute
- Please [![⭐ Star Project](https://img.shields.io/badge/Star-Project-blue?logo=github)]() to encourage developer(s).
- [Fork], do your thing and create a PR.

## Issues and Bug Reports

Found a bug or have a feature request? Please:

1. **Check existing issues**: [Browse issues] to see if it’s already reported.
2. **Open a new issue**: [Create one here] with:
   - A clear title
   - Description (and steps to reproduce, if a bug)
   - Expected vs actual behavior
   - Screenshots or error logs, if relevant
   - Environment (OS, Python, Chrome version)
3. **Use the template**: Please use the provided bug report template.
4. **Feature requests**: Explain what you want, why it’s useful, and any suggestions.


## Discussion

Have feedback or suggestions? Open an [issue] or join [dicussions] on new features, improvements, and use cases. Your input helps shape the project!

## TODO
- [x] PyPi Package.
    - [x] Convert to a package.
    - [x] pip install package.
    - [x] publish to PyPi.
- [ ] Automatically
  - [x] Use specified timezone othwerwise automatically get it.
  - [ ] Check first time activity.
    - [ ] Make sure it is completely synced with phone (Loading messages).
  - [x] Handle Chromedriver
    - [x] Check if Chrome browser is updated (same version as latest chromedriver release)
    - [x] Download latest chromedriver.
    - [x] Extract and move to `driver` directory.
  - [x] Handle dedicated Chrome profile 
    - [x] Create a new chrome profile(if not previously done).
    - [x] Use the newly chrome profile(if just created for the first time).
    - [x] Use existing chrome profile(if already created).

[WhatsApp Web]: <https://web.whatsapp.com/>
[Fork]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/fork/>
[CallMeBot]: <https://www.callmebot.com/blog/free-api-whatsapp-messages/>
[ChromeDriver]: <https://googlechromelabs.github.io/chrome-for-testing/>
[WhatsApp Business Cloud API]: <https://developers.facebook.com/products/whatsapp/>
[WhatsApp Business Cloud API Dashboard]: <README.md#WhatsApp-Business-Cloud-API-Dashboard>
[Create one here]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/issues/new>
[Browse issues]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/issues>
[issue]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/issues>
[REPO]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker>
[Dicussions]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/discussions>

[Todo]: <README.md#TODO>

