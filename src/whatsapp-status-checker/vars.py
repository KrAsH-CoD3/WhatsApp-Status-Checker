from os import path as os_path
from config import *

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

pause_btn_xpath:str = '//span[@data-icon="status-media-controls-pause"]'
pps_xpath: str = f'//span[@title="{status_uploader_name}"]//..//..//..//..//preceding-sibling::\
    div//*[local-name()="svg" and @class="x8182xy x1kgmq87 x10l6tqk"]' # Green circle
profile_picture_img_xpath: str = f'//span[@title="{status_uploader_name}"]//..//..//..//..//preceding-sibling::\
    div//img[contains(@class, "x1hc1fzr _ao3e")]' # Profile picture
default_profile_picture_xpath: str = f'//span[@title="{status_uploader_name}"]//..//..//..//..//preceding-sibling::\
    div//span[@data-icon="default-user"]' # Default Profile picture
bars_xpath: str = '//div[contains(@class, "x12mruv9 xfs2ol5")]' # All bars in the status(irrespective if viewed or not)
paused_video_bar_xpath: str =  '//div[contains(@class, "x5i6ehr")]' # paused video
playing_video_bar_xpath: str = '//div[contains(@class, "x5i6ehr velocity-animating")]' # playing video
scrolled_viewed_person_xpath :str = f'//span[@title="{status_uploader_name}" and \
    @class="ggj6brxn gfz4du6o r7fjleex g0rxnol2 lhj4utae le5p0ye3 _11JPr"]'
temp_status_thumbnail: str = f'//span[@title="{status_uploader_name}"]//..//..//..//preceding-sibling::div[@class="_1AHcd"]//\
    div[@class="t3g6t33p sxl192xd qnwaluaf g9p5wyxn i0tg5vk9 aoogvgrq o2zu3hjb gfz4du6o r7fjleex lniyxyh2 qssinsw9 rx2toazg"]'
img_status_xpath: str = '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//img'
video_status_xpath: str = '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//video'
text_status_xpath: str = '//div[contains(@class, "lhggkp7q l3hfgdr1 qk2y3tb3 myeiuhv9")]'
audio_status_xpath: str = '//div[@class="ajgl1lbb"]'
oldMessage_status_xpath: str = '//div[contains(@class, "qfejxiq4 b6f1x6w7 m62443ks")]'
caption_xpath: str = '//div[@class="tvsr5v2h mz6luxmp clw8hvz5 p2tfx3a3 holukk2e cw3vfol9"]//\
    span[@class="_11JPr" and @dir="auto" and @aria-label]'
read_more_caption_xpath: str = f'{caption_xpath}//following-sibling::strong'
search_bar_loading_xpath: str = '//*[local-name()="svg" and @class="x1e112to x1c74tu6 x1esw782 xa4qsjk xhtitgo"]'
loading_icon_in_status_xpath: str = '//button[@class="icon-media-disabled"]'
search_field_xpath: str = '//p[@class="selectable-text copyable-text x15bjb6t x1n2onr6"]'
unviewed_status_xpath: str = '//div[contains(@class, "x5fxwdf")]'
status_exit_xpath: str = '//span[@data-icon="x-viewer"]'
status_list_page_xpath: str = '//span[@data-icon="status-outline"]'