import re
from tempfile import TemporaryFile

class HttpParse():

    def __init__(self,http_str=''):

        self.pattern = re.compile(r'\${([a-zA-Z0-9]+)}')
        self.variables = []
        self.http_str = http_str
        self.res = {
            'method': '',
            'url': '',
            'protocol': '',
            'headers': {},
            'data': '',
            'error': False,
        }
        self.var = self.contains_variables()

        if http_str:
            self.is_empty=False
        else:
            self.is_empty=True




    def contains_variables(self):


        self.variables = self.pattern.findall(self.http_str)
        if self.variables:
            return True
        else:
            self.variables = ''
            return False

    def parse_request_line(self):
        line_info = self.file.readline().split()
        if line_info:

            self.res['method'], self.res['url'], *_ = line_info
        else:
            print('文件:%s\n内容为空\n' % self.http_path) 
            self.is_empty = True


    def parse_request_headers(self):
        while True:
            header_line = self.file.readline()
            if header_line.split():
                if  not self.res['error']:
                    self._parse_one_header(header_line)
                else:
                    pass

            else:
                break

    def _parse_one_header(self,line):
        if self._check_header(line):
            pair = line.split(':')
            self.res['headers'][pair[0].strip()] = pair[1].strip()
        else:
            print('文件:%s\n请求头出现格式错误\n' % self.http_path)
            self.res['error'] = True
            

    def _check_header(self,line):
        res = re.findall(r'[^\d]+?:\s?.+',line)
        if len(res)==1:
            return True
        else:
            return False

    def parse_body(self):
        data = re.sub(r'\n','',self.file.read())
        self.res['data'] = data

    def close(self):
        self.file.close()

    def _parse(self):
        try:
            self.parse_request_line()
        except AttributeError:
            raise Exception("%s文件中存在变量，不予解析" % self.http_path)

        if self.is_empty:
            pass
            
        else:
            self.parse_request_headers()
            self.parse_body()

        self.close()
        return self.res
    


    def parse(self,data={}):
        if self.var:
            if (not data):
                raise Exception("%s中存在变量，解析需要加载变量数据，参数data不能为空" % self.http_path)
            else:
                return self._parse_with_data(data)

        else:
            return self._parse()
        
        

    def _load_data(self,data):
        temp_str = self.http_str
        for i in self.variables:
            temp_str = re.sub(r'\${%s}' % i, data[i], temp_str)
        return temp_str

    def _parse_with_data(self,data):
        "data是变量字典"
        temp_str = self._load_data(data)
        with TemporaryFile('w+t') as file:
            file.write(temp_str)
            file.seek(0)
            self.file = file
            res = self._parse()
        return res




if __name__ == '__main__':
    import os
    from pprint import pprint
    "无变量测试"
    # path = r'E:\xiaoao\yswx-api-gateway.git\test\page'
    # one_path = r'E:\xiaoao\yswx-api-gateway.git\test\page\getHomeData.http'
    # for i in os.listdir(path):
    #     p = os.path.join(path,i)
    #     print(p)
    #     print(HttpParse(p).parse())
    "有变量测试"
    p = r'app\test.http'
    # print(os.path.exists(p))
    pprint(HttpParse(p).parse({'id':'101689'}))





    