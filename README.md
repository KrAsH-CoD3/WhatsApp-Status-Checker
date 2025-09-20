# WhatsApp Status Checker

![WhatsApp Status Checker](static/images/WhatsApp%20Status%20Checker.png)

The WhatsApp Status Viewer view a specific WhatsApp contact status as soon as it is uploaded, send a WhatsApp message about the status type(Image, Video, Text, or  Audio) and the time at which it was viewed OR alternatively always check and notify you if a status is uploaded. You get notified every 30minutes, 1hour, 3hours or 6 hours depending on your choice.

> _**NOTE:** WhatsApp does not allow bots or unofficial clients on their platform, so this shouldn't be considered totally safe._

# Requirements

See [requirements.txt]


# Installation

  - Download or clone this project.
  - Open CMD from the project directory.
  
  - <details>
      <summary>Using UV</summary>
      
      - Install UV if you haven't already using `pip install uv`.
      - Create a Virtual Environment using `uv venv`.
      - Activate your virtual environment using `.venv\Scripts\activate`.
      - Install dependencies using `uv add -r requirements.txt && uv sync`.
    </details>
    
  - <details>
      <summary>Using Python</summary>
      
      - Create a Virtual Environment using `py -m venv .venv`.
      - Activate your virtual environment using `.venv\Scripts\activate`.
      - Install dependencies using `pip install -r requirements.txt`.
    </details>

## WhatsApp Messenger

[CallMeBot] was used for WhatsApp message, **PLEASE READ!**

# How to use

Make sure your installed Google Chrome Browser is the latest.
  
  - Create a `.env` file.
    - Set `NUMBER` to your phone number. (Your WhatsApp Number e.g: 234xxxxxxxxxx)
    - Set `CALLMEBOT_APIKEY` to your API Key. (API Key provided by CallMeBot)
      > See [CallMeBot] for detailed information.

  - Then navigate to `src/whatsapp-status-checker` directory, open `config.py`.
    - Set `status_uploader_name` (The contact name you want to view his/her status. Make sure it is exactly how it is saved on your phone(Case Sensitive)).
    - Set `timezone` to your location time zone. (See [TODO] for more information).
  
  - <details>
      <summary>Run Program</summary>
      
      <details>
        <summary>Using UV</summary>
        
        uv run main.py
      </details>

      <details>
        <summary>Using Python</summary>

        py main.py
      </details>
    </details>


## Screenshots

### Terminal | First Time Logging In
![WhatsApp first time log in](static/images/WhatsApp%20first%20time%20log%20in.png)
#
### Terminal | Viewed Contact Status 
![WhatsApp subsequent log in view status 2](static/images/WhatsApp%20subsequent%20log%20in%20view%20status%202.png)
#
### WhatsApp Message | Status Notification
![WhatsApp first time log in](static/images/WhatsApp%20Notification%20Status%20Message.png)
### See other Screenshots, [Click here](static/images)

## Errors and Fixes

- **Timeout When Logging in:** Increase the timeout value `60` at `wait = WebDriverWait(bot, 60)`.
  > Preferrably, use a more stable internet.
- **Not Receiving WhatsApp Message:** Make sure you follow [CallMeBot] instructions carefully.
  > Also confirm your `.env` values are correct.

## Support and Contribute
- Please [![⭐ Star Project](https://img.shields.io/badge/Star-Project-blue?logo=github)]() to encourage developer(s).
- [Fork], do your thing and create a PR.

## TODO
- [ ] PyPi Package.
    - [x] Convert to a package.
    - [ ] publish to PyPi.
- [ ] Automatically
  - [ ] Use specified timezone othwerwise automatically get it.
  - [ ] Check first time activity.
    - [ ] Make sure it is completely synced with phone (Loading messages).
  - [x] Handle Chromedriver
    - [ ] Check if Chrome browser version is same as chromedriver else download lastest
    - [x] Download latest chromedriver.
    - [x] Extract and move to `driver` directory.
  - [x] Handle dedicated Chrome profile 
    - [x] Create a new chrome profile(if not previously done).
    - [x] Use the newly chrome profile(if just created for the first time).
    - [x] Use existing chrome profile(if already created).

[requirements.txt]: <requirements.txt>
[WhatsApp Web]: <https://web.whatsapp.com/>
[Fork]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/fork/>
[CallMeBot]: <https://www.callmebot.com/blog/free-api-whatsapp-messages/>
[ChromeDriver]: <https://googlechromelabs.github.io/chrome-for-testing/>
[WhatsApp Business Cloud API]: <https://developers.facebook.com/products/whatsapp/>
[WhatsApp Business Cloud API Dashboard]: <README.md#WhatsApp-Business-Cloud-API-Dashboard>
[REPO]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker>
[Todo]: <README.md#TODO>

