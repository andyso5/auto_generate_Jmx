import requests
import json,os

json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'json')
json_dict = {}

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
    }

for i in os.listdir(json_path):
    name = i[0:-5]
    path = os.path.join(json_path,i)
    json_dict[name] = json.loads(open(path).read())

def Crawl():
    def __init__(self,url,headers=headers,cookies=json_dict)
        self.url = url 
        self.domin  = self.get_domain(url)
        
        

    def get_domain(self,url):
        return re.search(r'http(s)?://(www.)?(?P<domain>[^\.]+)',url).group('domain')



