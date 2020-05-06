# ‐*‐ coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,TimeoutException,\
    StaleElementReferenceException,NoSuchWindowException,WebDriverException,UnexpectedAlertPresentException

import os
import json
import re
import time


current_path = os.path.abspath(__file__)
current_path = os.path.dirname(current_path)
config_path = os.path.join(current_path,'config.txt')

#读取配置
with open(config_path) as file:#gbk编码
    chrome_setting_path = file.readline().strip()#注意行末的\n
    chromedriver_path = file.readline().strip()


class Cookie_login():
    
    def __init__(self,driver=None,ant_crl=False):
        chrome_options = Options()
        chrome_options.add_argument(r"user-data-dir=%s" % chrome_setting_path)

        # capa = DesiredCapabilities.CHROME
        # capa["pageLoadStrategy"] = "eager"#none,eager,normal

        chrome_options.add_argument("start-maximized")
        if ant_crl:
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])#反知乎反爬虫
        # chrome_options.add_argument("window-size=1024,768")
        if not driver:
            self.driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)#desired_capabilities=capa
        else:
            self.driver = driver
        #设置访问超时
        self.driver.set_page_load_timeout(1)

    def _get_url(self,url,times=4):
        self.driver.set_page_load_timeout(2)
        if not url:
            return
        
        count = 0
        while True:
            if count<times:
                count+=1
            else:
                print('网址:%s \n第%d次加载失败。\n' %(url,count))
                self.driver.set_page_load_timeout(10)
                return False
            try:
                if count!=1:
                    print('网址:%s \n正在执行第%d次加载。\n' %(url,count))
                current_url = self.driver.current_url
                if current_url==url:
                    self.driver.refresh()
                    self.driver.set_page_load_timeout(10)
                    return True
                else:
                    self.driver.get(url)
                    self.driver.set_page_load_timeout(10)
                    return True
            except TimeoutException:
                
                time.sleep(10)
                continue
    
    def get_domain(self,url):
        return re.search(r'http(s)?://(www.)?(?P<domain>[^\.]+)',url).group('domain')

    def get_cookies(self):

        json_name = self.get_domain(self.driver.current_url)
        save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'json',json_name+'.json')
        with open(save_path,'w') as file:
            file.write(json.dumps(self.driver.get_cookies()))

    def switch_to_home_page(self):
        self.driver.switch_to.window(self.driver.window_handles[0])

    def get(self,url):
        self._get_url(url)
        # try:
        #     self.driver.get(url)
        # except TimeoutException:
        #     self.driver.set_page_load_timeout(1)
        #     self.driver.get(url)

    def click(self,element,button=True,reaction=0):
        if button:
            element.click()
        else:
            self.driver.execute_script("arguments[0].click()",element)
        time.sleep(reaction)

    def find(self,locator,method=By.XPATH):
        return self.driver.find_element(method,locator)

    def finds(self,locator,method=By.XPATH):
        return self.driver.find_elements(method,locator)

    def _wait_for(self,time,express,method=By.XPATH):
        locator = (method,express)
        return WebDriverWait(self.driver,time,0.2).until(EC.presence_of_element_located(locator))

    def _wait_for_all(self,time,express,method=By.XPATH):
        locator = (method,express)
        return WebDriverWait(self.driver,time,0.2).until(EC.presence_of_all_elements_located(locator))
    

class ShowDoc(Cookie_login):
    def __init__(self):
        Cookie_login.__init__(self)
        self.login = 'https://showdoc.dev.yitong.com/web/#/user/login'
        self.index = 'https://showdoc.dev.yitong.com/web/#/item/index'
        print('*****使用前请先确保showDoc帐号已登录*****\n')
        self.switch_to_home_page()
        # self.get(self.index)

    def get_all_block(self):

        self.get(self.index)

        block_elements = self._wait_for_all(10,'.//ul[@id="item-list"]/li[@drag_group]/a')
        block_urls = []
        for i in block_elements:
            block_urls.append(i.get_attribute('href'))
        
        return tuple(block_urls)

    def get_complete_tree_context(self,url='',time=0.5):
        if url:
            self.get(url)
        res = {}
        first_class = self.get_first_context()
        first_doc = self.get_docObj()
        res = self.get_docObj_dict(first_doc)

        for first in first_class:
            first_name = self.get_branch_name(first)
            print(first_name)
            self.click(first,reaction=time)
            first_dict = {}


            second_class = self.get_second_context(first)
            second_doc  = self.get_docObj(first)
            first_dict = self.get_docObj_dict(second_doc)

            for second in second_class:
                second_name = self.get_branch_name(second)
                print(' '*2 + second_name)
                self.click(second,reaction=time)
                
                third_class = self.get_docObj(second)
                second_dict = self.get_docObj_dict(third_class)
                # for third in  third_class:
                #     second_dict[third.text]=third


                first_dict[second_name] = second_dict

            res[first_name] = first_dict
        return res

    def get_first_context(self):
        return self._wait_for_all(10,'.//ul[@role="menubar"]/li[@role="menuitem"]/div/..')

    def get_docObj(self,element=None):
        if element==None:
            return self.finds('.//ul[@role="menubar"]/li[@role="menuitem"]/i[@class="el-icon-document"]/..')
        else:
            return element.find_elements_by_xpath('./ul[@role="menu"]/li/i[@class="el-icon-document"]/..')
    
    def get_docObj_dict(self,elements):
        res = {}
        for i in elements:
            res[self.get_doc_name(i)] = i
        
        return res



    def get_second_context(self,element):
        return element.find_elements_by_xpath('./ul[@role="menu"]/li/div/..')


    # def get_third_context(self,element):
    #     return element.find_elements_by_xpath('./ul[@role="menu"]/li')

    def get_branch_name(self,element):
        # try:
        #     res = element.find_element_by_xpath('./div').text
        # except NoSuchElementException:
        #     return element.text
        return element.find_element_by_xpath('./div').text

    def get_doc_name(self,element):
        return element.text
    
    def parse_page(self):
        pass
    # def get_doc(self,element):
    #     return element.find_elements_by_xpath('./i[@class="el-icon-document"]')

class ZenTao(Cookie_login):
    def __init__(self):
        Cookie_login.__init__(self)

        print('*****使用前请先确保禅道帐号已登录*****\n')
        

    def normalize_headers(self,string):
        temp = string.split('\n')
        res = {}
        for i in temp:
            if i and '"' not in i:
                temp = i.split(':')
                if len(temp)==2:
                    res[temp[0]] = temp[-1]
        return res

    def normal_header_and_body(self,text):

        headers = self.normalize_headers(text)

        body = ''
        pattern = re.compile('{.*}',re.DOTALL)
        try:
            body = pattern.search(text).group()
        except AttributeError:
            body = ''
        return (headers,body)
        
    def parse_page(self,url):
        res = {}
        self.get(url)
        try:
            self._wait_for(5,'.//div[@class="cell"]')
        except TimeoutException:
            print('访问链接:\n%s\n超时' % url)
            return None

        url_text = self.find('.//div[@class="cell"]//div[@class="detail-content article-content"]').text

        pattern = re.compile(r'http(s)?://[^\s]+')
        try:
            res['url'] = pattern.search(url_text).group()
        except AttributeError:
            print('链接:\n%s\n中没有找到url')
            return None

        pattern = re.compile(r'请求方式(.*?)(?P<t>[A-Za-z]+)',re.DOTALL)

        try:
            res['method'] = pattern.search(url_text).group('t')
        except AttributeError:
            print('链接:\n%s\n中没有找到请求方法，默认为POST')
            res['method'] = 'POST'


        branch = []

        branch_ele = self.finds('.//table[@id="steps"]//tbody/tr')

        for i in branch_ele:
            headers, body = self.normal_header_and_body(i.find_element_by_xpath('./td[1]').text)
            branch.append({
                'id': i.find_element_by_xpath('./*[@class="step-id"]').text,
                'headers': headers,
                'body': body,
                'assert': i.find_element_by_xpath('./td[2]').text
                })

        res['branch'] = branch
        return res

    # def    
if __name__ == '__main__':
    Z = ZenTao()
    from pprint import pprint
    pprint(Z.parse_page(url='https://zentao.dev.yitong.com/testcase-view-1470-1-testcase-0.html'))


        





    
# if __name__ == '__main__':
#     S = ShowDoc()
#     d = S.driver
#     from pprint import pprint



