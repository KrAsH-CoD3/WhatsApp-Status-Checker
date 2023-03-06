# WhatsApp Status Viewer

![WhatsApp Status Checker](static/images/WhatsApp%20Status%20Checker.png)

The WhatsApp Status Viewer is a Python project which enables you to view a specific WhatsApp contact status as soon as it is uploaded and send a WhatsApp message about what status type was uploaded(Image, Video, Text, or  Audio) and the time of which it is viewed.

# Requirements

Check [requirements.txt]

# Installation

Download or clone this project, open command prompt from the folder and run the below command

`pip install -r requirements.txt`

[WhatsAppCloud] was used for WhatsApp message, PLEASE READ!

## Bug with WhatsAppCloud config

After installation, navigate to your config, it should be in this path: `C:\Users\YOUR-PC-NAME\AppData\Local\Programs\Python\Python311\Lib\site-packages\whatsappcloud\whatsappcloud_config.py`

When this README was made, [WhatsAppCloud] comes with a config file of which the variable ```ENDPOINT``` had `f"https://graph.facebook.com/v13.0/{PHONE_ID}/messages"`. You need to update the `V13.0` to the Updated Version. To know the latest version; 

### WhatsApp Business Cloud API Dashboard
  - Go to [WhatsApp Business Cloud API].
  - Login and choose your created App.
  - On the left side bar, click "WhatsApp".
  - From the dropdown, select "Getting started".

You should see a screen like this 

![WhatsApp Business Cloud API Dashboard Image](static/images/WhatsApp%20Business%20Cloud%20API%20Dashboard.png)

# How to use

It is recommended you create/use another instance of your Chrome browser with a specific profile for just this software. To create new profile, please check YouTube. 
    
**NOTE:** *Remember your profile-directory and user-data-dir after you've created the new chrome browser instance*

To check for `profile-directory` and `user-data-dir` in your new instance, goto `chrome://version/`

  - Login into [WhatsApp Web] and make sure it is completely synced with your phone (Loading messages).
  - Download [ChromeDriver] that is of the same version as your Chrome browser. goto `chrome://version/` to check your Chrome Version.
  - After this, ensure all required in the `config.py` are provided (PHONE_ID, CONTACTS and TOKEN). See your [WhatsApp Business Cloud API Dashboard]. Remember the given token expires after 24hrs.
  - Then navigate to this project folder, open `main.py`.
  - Edit `driverpath` variable to your driver path.
  - Edit `timezone` variable to your location time zone.
  - Edit `options.add_argument(r'user-data-dir=YOUR-USER-DATA-DIR')`.
  - Edit `options.add_argument(r'--profile-directory=YOUR-PROFILE-DIR')`.
  - Edit `ContactName` to your desired ContactName (make sure it is exactly how it is saved on your phone(Case Sensitive).
  - Open command prompt and run `py main.py`

## Errors

**Timeout When Logging in:** Increase the timeout value `60` at `wait = WebDriverWait(bot, 60)`.
**Not Receiving WhatsApp Message:** Send a message to your Test Number. If a message isn't sent to your test Number within 24hours, you would not also recieve. 

[requirements.txt]: <requirements.txt>
[WhatsApp Web]: <https://web.whatsapp.com>
[WhatsAppCloud]: <https://github.com/PFython/WhatsAppCloud>
[ChromeDriver]: <https://chromedriver.chromium.org/downloads>
[WhatsApp Business Cloud API]:<https://developers.facebook.com/products/whatsapp/>
[WhatsApp Business Cloud API Dashboard]: <README.md#WhatsApp-Business-Cloud-API-Dashboard>
