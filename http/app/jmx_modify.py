import subprocess
from string import Template
import re
import os

current_path = os.path.abspath(__file__)
current_path = os.path.dirname(current_path)
template_path = os.path.join(current_path,r'jmeterScript\template.jmx')
default_temp = os.path.join(current_path,r'jmeterScript\default_template.jmx')
# template_path = r'E:\xiaoao\http_api_test\http\jmeterScript\template.jmx'
# default_temp = r'E:\xiaoao\http_api_test\http\jmeterScript\default_template.jmx'
class ModifyJmx():
    
    def __init__(self,template_path=template_path,default_temp = default_temp):
        #获取模板
        # self.default_temp = open(default_temp,encoding='utf-8').read()
        self.temp = Template(open(template_path,encoding='utf-8').read())
        #匹配所有含变量的标签
        self.all_var_obj = re.compile(r'<[^>]+>\$[^<]+<[^>]+>')

        self.vars = self.all_var_obj.findall(self.temp.template)

        self.jmx_str = ''

        self.jmx_path = ''

        self.report_dir = ''

    def gain_default_data(self):
        pass

    def _gain_head_space_num(self,text):
        #返回头部空格个数
        return re.search(r'\s+',text).span()[-1] - 1

    def _add_header_info(self,tmp,headers):
        "添加请求头信息"
        "tmp为string.Template对象"
        "返回一个string.Template对象"
        "headers为字典"


        #定位template.jmx中的请求头区域
        #\s会匹配到\n
        target = r'\s+<collectionProp name="HeaderManager.headers"/>'

        #默认为模板中没有设置这一项
        target_pattern = re.compile(target)
        headstr = target_pattern.search(tmp.template).group()
        space_num = self._gain_head_space_num(headstr)

        #用来加载headers
        sub_temp = Template(
            '\n' + ' '*space_num \
            + '<collectionProp name="HeaderManager.headers">\n' \
            + ' '*(space_num+2) \
            + '<elementProp name="Content-Type" elementType="Header">\n$headStr' \
            + ' '*(space_num+2) \
            + '</elementProp>\n' \
            + ' '*space_num + '</collectionProp>'
            )#最有一个不需要加\n，因为正则没有匹配到

        #设置变量headStr的模板
        core = ''
        k_v_temp = Template(
            ' '*(space_num+4) \
            + '<stringProp name="Header.name">$key</stringProp>\n' \
            + ' '*(space_num+4) \
            + '<stringProp name="Header.value">$value</stringProp>\n'
            )

        #加载headers
        for i in headers:
            core += k_v_temp.substitute(key=i,value=headers[i])

        #置换模板中的变量
        tmp = Template(target_pattern.sub(sub_temp.substitute(headStr=core),tmp.template))

        return tmp
        
    #添加请求头
    def add_header_info(self,headers):
        "headers为dict"
        "添请求正文"
        if self.jmx_str:
            tmp = Template(self.jmx_str)
            tmp = self._add_header_info(tmp,headers)
            self.jmx_str = tmp.template
        else:

            self.temp = self._add_header_info(self.temp,headers)

    
    def _add_body_data(self,tmp,data):
        "data为str"
        "tmp为string.Template对象"
        "添请求正文"
        "返回一个string.Template对象"


        #定位template.jmx中的请求正文区域
        target_temp = r'\s+<collectionProp name="Arguments.arguments"/>'
        target_pattern = re.compile(target_temp)
        headstr = target_pattern.search(tmp.template).group()
        space_num = self._gain_head_space_num(headstr)

        #设置变量bodyStr的模板
        sub_tmp = Template(
            '\n' \
        
            + ' '*space_num \
            + '<collectionProp name="Arguments.arguments">' \
            + ' '*(space_num + 2*1) \
            + '<elementProp name="" elementType="HTTPArgument">' \
            + ' '*(space_num + 2*2) \
            + '<boolProp name="HTTPArgument.always_encode">false</boolProp>\n'
            + ' '*(space_num + 2*2) \
            + '<stringProp name="Argument.value">$value</stringProp>\n' \
            + ' '*(space_num + 2*2) \
            + '<stringProp name="Argument.metadata">=</stringProp>\n' \
            + ' '*(space_num + 2*1) \
            + '</elementProp>\n' \
            + ' '*space_num \
            + '</collectionProp>' 


        )

        #使data符合jmx规范
        data = re.sub('\n','',data)
        data = re.sub('"','&quot;',data)

        #置换模板中的变量
        core = sub_tmp.substitute(value=data)
        tmp = Template(target_pattern.sub(core,tmp.template))
        return tmp
        
    #添加请求正文
    def add_body_data(self,data):
        "data为str"
        "添请求正文"
        if self.jmx_str:
            tmp = Template(self.jmx_str)
            tmp = self._add_body_data(tmp,data)
            self.jmx_str = tmp.template
        else:
            self.temp = self._add_body_data(self.temp,data)


    def load_data(self,data):
        "可以连续加载"
        if 'headers' in data:
            self.add_header_info(data['headers'])
            del data['headers']
        
        if 'data' in data:
            self.add_header_info(data['data'])
            del data['data']

        if not self.jmx_str:
            self.warning(data,self.temp.template)
            self.jmx_str = self.temp.safe_substitute(**data)
        else:
            self.warning(data,self.jmx_str)
            new = Template(self.jmx_str).safe_substitute(**data)
            self.jmx_str = new

    def warning(self,data,text):
        #host为空发出警告
        ready_vars = self.all_var_obj.findall(text)
        undefined = [] 
        
        data_keys = data.keys()
        unused_keys = list(data_keys)
        for i in ready_vars:
            key = re.search(r'\$([^<]+)',i).group(1)
            if key in data_keys:
                unused_keys.remove(key)
            else:
                undefined.append(i)

        if unused_keys:
            print('存在没有使用的数据:')
            for i in unused_keys:
                print(i)

        if undefined:
            print('存在没有赋值的变量:')
            for i in undefined:
                print(i)

    def generate_jmx(self,jmx_path=None):
        if not jmx_path:
            if self.jmx_path:
                jmx_path = self.jmx_path
            else:
                print('脚本地址为空，无法运行脚本文件\n')
                return
        else:
            self.jmx_path = jmx_path

        with open(jmx_path,'w') as file:
            file.write(self.jmx_str)

    def run_jmx(self,report_dir=None,jmx_path=None,):
        if not jmx_path:
            if self.jmx_path:
                jmx_path = self.jmx_path
            else:
                print('脚本地址为空，无法运行脚本文件\n')
                return

        if not report_dir:
            if self.report_dir:
                report_dir = self.report_dir
            else:
                print('报告路径为空，无法运行脚本文件\n')
                return


        cmd = r'jmeter -n -t %s -l log.jtl -e -o %s' % (jmx_path,report_dir)
        file = os.popen(cmd)
        print(file.read())
        file.close()

        # with os.popen(cmd) as file:
        #     print(file.read())

if __name__ == '__main__':
    import json
    report = os.path.join(os.path.dirname(os.path.abspath(__file__)),'report')
    m = ModifyJmx()
    m.report_dir = report
    m.jmx_path = os.path.join(os.path.dirname(report),'test.jmx')
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'X-YT-AppKey': 'ce2419551b8b455ebd9fcfa3101e3444',
        'Authorization': 'Bearer eyJhbGciOiJFUzI1NiJ9.eyJpc3MiOiJ5aXRvbmcuY29tIiwic3ViIjoiMTAxNzMzIiwiYXVkIjoiOTg0ZjI3MGYwMzA5NDBlYTgxNDMyNTg5NmFiMGU4NDUiLCJpYXQiOjE1NDM0ODI0MzYsImV4cCI6MTYzODA5MDQzNn0.75zp_SE5lfCsLMzoqBUCfSKwZ2yNBYUiuYYNByvFN20_XUlBA6utytCZSHM9fFyH0Qhl3HIQmOXBaOGnhRlnjA'
    }
    data = json.dumps({
        'code': 'ZHw657Qk2ree9EL595v2sh2FgZBnJzYZYkSA3SBDCVE='
    })
    m.add_header_info(headers)
    m.add_body_data(data)
    m.load_data({
        'domain':'api.dev.yitong.com',
        'protocol':'http',
        'path':'/yswx/gw/util/decode',
        'method':'POST',
        'loops':1,
        'num_threads':10,
        'ramp_time':10,

        })

    m.generate_jmx()
    m.run_jmx()