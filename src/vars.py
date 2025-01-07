from os import environ as env_variable, path as os_path, getcwd
from dotenv import load_dotenv

load_dotenv()

NUMBER: str = env_variable.get("MY_NUMBER")  # Your WhatsApp Number e.g: 234xxxxxxxxxx
NUM_ID: str = env_variable.get("NUM_ID")  # Your Number ID
TOKEN: str =  env_variable.get("TOKEN")  # Token
CURRENT_DIR = getcwd()

timezone: str = "Africa/Lagos"  # Your timezone #TODO: Use specified timezone else Automatically get it
pause_btn_xpath:str = '//span[@data-icon="status-media-controls-pause"]'
statusUploaderName: str = "ContactName" # As it is saved on your phone(Case Sensitive)
ppsXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]'
ppXpath: str = f'//span[@title="{statusUploaderName}"]//..//..//..//..//preceding-sibling::\
    div[@class="_1AHcd"]//*[local-name()="svg" and @class="bx0vhl82 ma4rpf0l lhggkp7q"]//parent::div'
barsXpath: str = '//div[@class="g0rxnol2 qq0sjtgm jxacihee l7jjieqr egv1zj2i ppled2lx gj5xqxfh om6y7gxh"]'
barXpath: str =  '//div[@class="lhggkp7q qq0sjtgm tkdu00h0 ln8gz9je ppled2lx ss1fofi6 o7z9b2jg"]'
driverpath: str = os_path.join(CURRENT_DIR, "driver", "chromedriver.exe")
barVA_Xpath: str =  '//div[@class="lhggkp7q qq0sjtgm tkdu00h0 ln8gz9je ppled2lx ss1fofi6 o7z9b2jg velocity-animating"]'
scrolled_viewed_person_xpath :str = f'//span[@title="{statusUploaderName}" and \
    @class="ggj6brxn gfz4du6o r7fjleex g0rxnol2 lhj4utae le5p0ye3 _11JPr"]'
tempStatusThumbnail: str = f'//span[@title="{statusUploaderName}"]//..//..//..//preceding-sibling::div[@class="_1AHcd"]//\
    div[@class="t3g6t33p sxl192xd qnwaluaf g9p5wyxn i0tg5vk9 aoogvgrq o2zu3hjb gfz4du6o r7fjleex lniyxyh2 qssinsw9 rx2toazg"]'
img_status_xpath: str = '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//img'
video_status_xpath: str = '//div[@class="g0rxnol2 ln8gz9je ppled2lx gfz4du6o r7fjleex"]//video'
text_status_xpath: str = '//div[contains(@class, "lhggkp7q l3hfgdr1 qk2y3tb3 myeiuhv9")]'
audio_status_xpath: str = '//div[@class="ajgl1lbb"]'
oldMessage_status_xpath: str = '//div[contains(@class, "qfejxiq4 b6f1x6w7 m62443ks")]'
caption_xpath: str = '//div[@class="tvsr5v2h mz6luxmp clw8hvz5 p2tfx3a3 holukk2e cw3vfol9"]//\
    span[@class="_11JPr" and @dir="auto" and @aria-label]'
read_more_caption_xpath: str = f'{caption_xpath}//following-sibling::strong'