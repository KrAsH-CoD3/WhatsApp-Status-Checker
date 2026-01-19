from os import path as os_path
from .config import *

driverpath: str = os_path.join(
    os_path.dirname(os_path.abspath(__file__)),
    "driver", 
    "chromedriver.exe"
)

bot_profile_name: str = "Bot Profile"
bot_profile_user_data_dir: str = os_path.join(
    os_path.dirname(os_path.abspath(__file__)),
    "driver", 
    "WSC Bot Profile"
)

# WhatsApp login instructions
login_instructions_xpath: str = '//*[contains(@aria-label, "QR code")]'

BASE_PP_XPATH: str = f'//span[@title="{STATUS_UPLOADER_NAME}"]//..//..//..//..//..//preceding-sibling::' # To identify specfied user
profile_picture_status_xpath: str = BASE_PP_XPATH + 'div//*[local-name()="svg" and @class="xe9ewy2 x1kgmq87 x10l6tqk"]' # Green circle.
profile_picture_img_xpath: str = BASE_PP_XPATH + 'div//img[contains(@class, "x1n2onr6 x1lliihq")]' # Profile picture
default_profile_picture_xpath: str = BASE_PP_XPATH + 'div//span[@data-icon="default-contact-refreshed"]' # Default Profile picture

# play_btn_xpath: str =  '//*[@data-icon="status-media-controls-play"]' # play button icon # NOT USED
pause_btn_xpath: str = '//*[@data-icon="pause"]' # pause button icon # test this

# All bars(each statuses) of the status not the container(irrespective if viewed or not)
bars_xpath: str = '//div[contains(@class, "x10l6tqk xtijo5x x1o0tod")]\
    //div[contains(@class, "x1n2onr6 x13vifvy")]'

playing_bar_xpath: str = '//div[contains(@class, "x5i6ehr velocity-animating")]' # playing status
paused_bar_xpath: str = '//div[contains(@class, "x5i6ehr")]' # paused status
scrolled_viewed_person_xpath :str = f'//span[@title="{STATUS_UPLOADER_NAME}" and \
    @class="ggj6brxn gfz4du6o r7fjleex g0rxnol2 lhj4utae le5p0ye3 _11JPr"]' # Test this
temp_status_thumbnail: str = f'//span[@title="{STATUS_UPLOADER_NAME}"]//..//..//..//preceding-sibling::div[@class="_1AHcd"]//\
    div[@class="t3g6t33p sxl192xd qnwaluaf g9p5wyxn i0tg5vk9 aoogvgrq o2zu3hjb gfz4du6o r7fjleex lniyxyh2 qssinsw9 rx2toazg"]' # Test this

img_status_xpath: str = '(//div[@class="x1n2onr6 xh8yej3 x5yr21d"]//img[1])'
video_status_xpath: str = '//video'
text_status_xpath: str = '//div[@class="x10l6tqk x13vifvy x1o0tod xh8yej3 x5yr21d xiy17q3 x1xsqp64 x18d0r48" \
    and contains(@style, "background-color: rgb")]'
audio_status_xpath: str = '//div[@class="ajgl1lbb"]' # Test this
oldMessage_status_xpath: str = '//div[contains(@class, "x88nbbm x2b8uid x1vvkbs x47corl")]'

caption_xpath: str = '//div[@class="tvsr5v2h mz6luxmp clw8hvz5 p2tfx3a3 holukk2e cw3vfol9"]//\
    span[@class="_11JPr" and @dir="auto" and @aria-label]' # Test this
read_more_caption_xpath: str = caption_xpath + '//following-sibling::strong' # Test this

loading_icon_in_status_xpath: str = '//button[@class="icon-media-disabled"]'
search_field_xpath: str = '//p[contains(@class, "copyable-text") and contains(@class, "x15bjb6t") and contains(@class, "x1n2onr6")]'
unviewed_status_xpath: str = '//div[contains(@class, "x5fxwdf")]'
status_exit_xpath: str = '//span[@data-icon="x-viewer"]'
status_list_page_xpath: str = '//span[@data-icon="status-outline"]' # Test this