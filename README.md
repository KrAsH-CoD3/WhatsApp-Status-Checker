# WhatsApp Status Checker

![WhatsApp Status Checker](static/images/WhatsApp%20Status%20Checker.png)

The WhatsApp Status Viewer view a specific WhatsApp contact status as soon as it is uploaded, send a WhatsApp message about the status type(Image, Video, Text, or  Audio) and the time at which it was viewed OR alternatively always check and notify you if a status is uploaded. You get notified every 30minutes, 1hour, 3hours or 6 hours depending on your choice.

> _**NOTE:** WhatsApp does not allow bots or unofficial clients on their platform, so this shouldn't be considered totally safe._

# Requirements

See [requirements.txt]


# Installation
  - Download or clone this project.
  - Open CMD from the project folder.
  - Create a Virtual Environment using the following command `py -m venv your_env_name`.
  - Activate your virtual environment and run the below command to install dependencies.

```python
pip install -r requirements.txt
```

## WhatsApp Messenger

[Python-WhatsApp-Bot] was used for WhatsApp message, **PLEASE READ!**

## WhatsApp Business Cloud API Dashboard
  - Go to [WhatsApp Business Cloud API].
  - Login and choose your created App.
  - On the left side bar, click "WhatsApp".
  - From the dropdown, select "Getting started".
  - Here is a [video demonstration](https://youtu.be/yQZsrGnJfcg)

You should see a screen like this 

![WhatsApp Business Cloud API Dashboard Image](static/images/WhatsApp%20Business%20Cloud%20API%20Dashboard.png)

> Pay attention to the version. `v15.0` was the version at the time of making this package. Use the correct version.

# How to use

It is recommended you create/use another instance of your Chrome browser with a specific profile for just this package. To create new profile, please check YouTube. 
    
> **NOTE:** *Remember your **profile-directory** and **user-data-dir** after you've created the new chrome browser profile/instance*

> To check for `profile-directory` and `user-data-dir` on your new instance, goto `chrome://version/`

  - Login into [WhatsApp Web] and make sure it is completely synced with your phone (Loading messages).
  - Download [ChromeDriver] that is of the same version as your Chrome browser. Navigate to `chrome://version/` to check your Chrome Version.
  - Extract chromedriver from the zip into this folder `assest/driver`
  - Afterwards, ensure all required in the `config.py` are provided (PHONE_ID, CONTACTS and TOKEN). See [WhatsApp Business Cloud API Dashboard] for your infomations. 
  > **REMEMBER** THE GENERATED TOKEN EXPIRES EVERY 24HOURS.
  
  > If you need a permenent token, let me know.
  - Then navigate to this project folder, open `main.py`.
  - Edit `driverpath` variable to your driver path.
  - Edit `timezone` variable to your location time zone.
  - Edit `options.add_argument(r'user-data-dir=YOUR-USER-DATA-DIR')`.
  - Edit `options.add_argument(r'--profile-directory=YOUR-PROFILE-DIR')`.
  - Edit `statusUploaderName` to your desired ContactName (make sure it is exactly how it is saved on your phone(Case Sensitive)).
  - Open command prompt in the same folder assuming your env('your_env_name') is activated.
  - Run `py main.py`.

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
- **Not Receiving WhatsApp Message:** Send a message to your Test Number.
  > If a message isn't sent to your test number within 24hours, you would not recieve message.

## Support and Contribute
- [Fork], do your thing and create a PR.
- Please star 🌟 to encourage developer(s).

## TODO
- [ ] Create a package and publish to PyPi.
- [ ] Automatically
  - [ ] Handle Chromedriver
    - [x] Download chromedriver (based on the Google Chrome version installed).
    - [x] Extract and move to `assest/driver` folder.
  - [ ] Handle dedicated Chrome profile (if not previously done)
    - [ ] Create a new chrome profile.
    - [ ] Use the new chrome profile.

[requirements.txt]: <requirements.txt>
[WhatsApp Web]: <https://web.whatsapp.com>
[Fork]: <https://github.com/KrAsH-CoD3/WhatsApp-Status-Checker/fork>
[Python-WhatsApp-Bot]: <https://github.com/Radi-dev/python-whatsapp-bot>
[ChromeDriver]: <https://googlechromelabs.github.io/chrome-for-testing/>
[WhatsApp Business Cloud API]: <https://developers.facebook.com/products/whatsapp/>
[WhatsApp Business Cloud API Dashboard]: <README.md#WhatsApp-Business-Cloud-API-Dashboard>
