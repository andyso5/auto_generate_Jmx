from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


current_path = os.path.abspath(__file__)
current_path = os.path.dirname(current_path)
config_path = os.path.join(current_path,'config.txt')

#读取配置
with open(config_path,encoding='utf-8') as file:
    chrome_setting_path = file.readline()
    chromedriver_path = file.readline()

class Cookie_login():
    
    def __init__(self,driver=None,noImage=False,ant_crl=False):
        chrome_options = Options()
        chrome_options.add_argument(r"user-data-dir=%s" % chrome_setting_path)

        prefs = {'profile.default_content_setting_values' :{'notifications' : 2}}#关闭chrome系统弹窗，不过貌似不怎么有效
        if noImage:
            prefs['profile.managed_default_content_settings.images'] = 2
        else:
            prefs['profile.managed_default_content_settings.images'] = 1
        chrome_options.add_experimental_option('prefs',prefs)
        if ant_crl:
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])#反知乎反爬虫
        #chrome_options.add_argument("window-size=1024,768")
        if not driver:
            self.driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)
        else:
            self.driver = driver
        #设置访问超时
        self.driver.set_page_load_timeout(12)

    def get_cookies(self):
        return self.driver.get_cookies()



