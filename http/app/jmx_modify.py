import re
import os
from copy import deepcopy

current_path = os.path.abspath(__file__)
current_path = os.path.dirname(os.path.dirname(current_path))
template_path = os.path.join(current_path,r'jmeterScript\template.jmx')
default_temp = os.path.join(current_path,r'jmeterScript\default_template.jmx')
# template_path = r'E:\xiaoao\http_api_test\http\jmeterScript\template.jmx'
# default_temp = r'E:\xiaoao\http_api_test\http\jmeterScript\default_template.jmx'


class ModifyJmx():
    
    def __init__(self,template_path=template_path,default_temp = default_temp,cloud=False):

        self.cloud = cloud#是否准备到阿里云之类云端平台上去测试，这会决定csv文件路径值是否为相对路径
        self.all_var_obj = re.compile(r'<[^>]+>\$[^<]+<[^>]+>')

        # self.vars = self.all_var_obj.findall(self.temp.template)

        self.template_path = template_path
        

        self.jmx_path = ''

        self.report_dir = ''

        self.target_temp = r'<(?P<front>.*?){key}(?P<rear>.*?)>{value}<'

        self.repel_temp = r'<\g<front>{key}\g<rear>>{value}<'

    def uniform_jmx_var(self,string):
        if isinstance(string,str):
            string = re.sub(r'\\',r'\\\\',string)
            string = re.sub(r'\n','',string)
            string = re.sub(r'":\s+(?P<var>("|\d+))',r'":\g<var>',string)#虑去特定情况下:后的空格
            string = re.sub(r'"','&quot;',string)
            
            return string
        else:
            return str(string)
     
    def uniform_jmx_name(self,string):
        if isinstance(string,str):
            if string[0].isupper():
                return re.sub('_','.',string,count=1)
            else:
                return string
        else:
            return str(string)

    def adapt_cloud(self,data):
        if 'filename' in data and self.cloud:
            data['filename'] = os.path.split(data['filename'])[-1]

    def add_else_data(self,data):
        for i in data:
            # print(data[i])
            name  = self.uniform_jmx_name(i)
            target = self.target_temp.format(key=name, value='.*?')
            #需要将"转换成&quot;
            repel  = self.repel_temp.format(key=name, value=self.uniform_jmx_var(data[i]))
            res = re.subn(target, repel, self.jmx_str)
            num = res[-1]
            if num == 0:
                raise Exception("不存在变量%s" % i, 0)
            elif num > 1:

                raise Exception("存在多个同名变量", 2)
            else:
                self.jmx_str = res[0]

    def load_data(self,data):
        "data为dict，参照模版的name属性设置键"
        #事先加入assertion并在data中删除
        self.jmx_str = open(self.template_path,encoding='utf-8').read()
        
        copy_data = deepcopy(data)

        self.adapt_cloud(copy_data)

        self.add_assertion(copy_data)
        self.add_headers(copy_data)
        self.add_else_data(copy_data)

        self.last_tail(copy_data)

    def add_addtion_assertion(self,string):
        target_temp = \
            '</stringProp>\n' + \
            '{assertion}' + \
            '{space}' * 12 + '</collectionProp>\n' + \
            '{space}' * 12 + '<stringProp name="Assertion.custom_message"></stringProp>'
        assertion_temp = ' ' * 14 + '<stringProp name="{name}">{string}</stringProp>' 

        target = target_temp.format(assertion='', space='\s')
        name = self.hash_code(string)
        ass = target_temp.format(

            assertion=assertion_temp.format(name=name, string=string),
            space=' '

            )


        # self.jmx_str = re.sub(target, ass, self.jmx_str)
        res = re.subn(target, ass, self.jmx_str)
        # print('替代结果为%d' % res[-1])
        self.jmx_str = res[0]

    def add_first_assertion(self,string):
        pattern = re.compile(r'<stringProp name="\d+"></stringProp>')
        name = self.hash_code(string)
        target = r'<stringProp name="%s">%s</stringProp>' % (name,string)
        self.jmx_str = re.sub(pattern, target, self.jmx_str)

    def add_assertion(self,data):
        keys = data.keys()
        first = True

        # if '0' in keys or 0 in keys:
        #     raise Exception('不可以将字典的键设置为0或者"0"\n')
        if 'assert' in keys:
            assert_strs = data['assert']
            if isinstance(assert_strs,str):
                assert_strs = [assert_strs]
            for assert_str in assert_strs:
                assert_str = self.uniform_jmx_var(assert_str)
                # print(assert_str)
                if first:
                    self.add_first_assertion(assert_str)
                    first = False
                else:
                    self.add_addtion_assertion(assert_str)
            del data['assert']

    def hash_code(self,string):

        def convert_n_bytes(n, b):
            bits = b * 8
            return (n + 2 ** (bits - 1)) % 2 ** bits - 2 ** (bits - 1)   

        def convert_4_bytes(n):
            return convert_n_bytes(n, 4)

        def getHashCode(s):
            h = 0
            n = len(s)
            for i, c in enumerate(s):
                h = h + ord(c) * 31 ** (n - 1 - i)
            return convert_4_bytes(h)

        return getHashCode(string)
    

    def add_headers(self,data):
        
        try:
            headers = data['headers']
        except KeyError:
            return 

        if not data:
            return 
        first = True
        for i in headers:
            if first:
                try:
                    first_header = {
                        'Header_name':i,
                        'Header_value':headers[i]
                    }
                    self.add_else_data(first_header)
                except Exception as e:
                    if e.args[-1]==2:
                        self._add_a_pair_header(i,headers[i])
                    else:
                        raise Exception(*e.args)
                first = False
            else:
                self._add_a_pair_header(i,headers[i])
            
        del data['headers']

    def _add_a_pair_header(self,key,value):
        #第二及以上次插入点
        #</elementProp>\n{headers}\t\*6</collectionProp>

        temp = '  '*7 + '<elementProp name="" elementType="Header">\n' \
          + '  '*8 + '<stringProp name="Header.name">{key}</stringProp>\n' \
          + '  '*8 + '<stringProp name="Header.value">{value}</stringProp>\n' \
          + '  '*7 + '</elementProp>\n'
        
        tg_temp = '</elementProp>\n'\
             + '{header}' + '{space}' * 12 + '</collectionProp>\n'\
             + '{space}' * 10 + '</HeaderManager>'

        target = tg_temp.format(header='',space='\s')
        repel = tg_temp.format(header = temp.format(key=key,value=value), space=' ')
        res = re.subn(target, repel, self.jmx_str)
        if res[-1]==0:
            raise Exception('插入%s：%s请求头信息失败' % (key,value))
        elif res[-1] > 1:
            raise Exception('存在多个请求头信息插入点')
        else:
            self.jmx_str = res[0]

    def last_tail(self,data):
        if 'filename' not in data:
            pattern = re.compile('\s+<CSVDataSet.+?<hashTree/>', re.DOTALL)#跨行匹配
            res  = pattern.subn('',self.jmx_str)
            # print('裁剪结果:%d' % res[-1])
            self.jmx_str = res[0]

            temp = '</objProp>\n{value}</ResultCollector>'
            plus = '  ' * 5 + '<stringProp name="filename"></stringProp>\n' + '  ' * 4
            pattern = re.compile(temp.format(value='\s+'), re.DOTALL)
            res  = pattern.subn(temp.format(value=plus), self.jmx_str)
            self.jmx_str = res[0]


    def generate_jmx(self,jmx_path=None):
        if not jmx_path:
            if self.jmx_path:
                jmx_path = self.jmx_path
            else:
                print('脚本地址为空，无法运行脚本文件\n')
                return
        else:
            self.jmx_path = jmx_path

        with open(jmx_path,'w',encoding='utf-8') as file:
            file.write(self.jmx_str)

    def run_jmx(self,jmx_path=None,report_dir=None):
        if not jmx_path:
            if self.jmx_path:
                jmx_path = self.jmx_path
            else:
                print('脚本地址为空，无法运行脚本文件\n')
                return

        if not report_dir:
            if self.report_dir:
                report_dir = self.report_dir
                cmd = r'jmeter -n -t %s -l log.jtl -e -o %s' % (jmx_path,report_dir)
            else:
                # print('报告路径为空，无法运行脚本文件\n')
                cmd = r'jmeter -n -t %s' % jmx_path
        else:
            cmd = r'jmeter -n -t %s -l log.jtl -e -o %s' % (jmx_path,report_dir)
        

        file = os.popen(cmd)
        res = file.read()
        print(res)
        file.close()
        return res
        

        # with os.popen(cmd) as file:
        #     print(file.read())



if __name__ == '__main__':
    import json
    report = os.path.join(os.path.dirname(os.path.abspath(__file__)),'report')
    m = ModifyJmx(cloud=False)
    m.report_dir = report
    m.jmx_path = os.path.join(os.path.dirname(report),'test.jmx')

    """约定像name="Argument.value"这样的变量将"."用"_"代替"""
    data  = {
        #线程设置
        'num_threads':3,
        'ramp_time':1,
        'loops':1,

        #请求参数
        'Argument_value':'{"id":"${id}"}',#请求正文
        'HTTPSampler_domain':'api.dev.yitong.com',
        'HTTPSampler_path':'/ytxy/gw/statistics/getUserStatistics',
        'HTTPSampler_method':'POST',

        #请求头
        'headers':{
            'Content-Type':'application/json;charset=utf-8',
            'xiaoao':'agwgwqwfew'
            },
        
        #断言
        "assert":['"code": 1','"message": "操作成功"'],

        #csv配置
        #上传到阿里云，只需要写test.csv
        #在本地测试需要填写完整路径
        "filename":r"C:\Users\Administrator\Desktop\python\project\auto_generate_jmx\http\app\test.csv",
        # "filename":'test.csv',
        #如果csv第一行没有变量名需要设置，变量名之间用","隔开
        "variableNames":'',



    }
    m.load_data(data)
    m.generate_jmx()
    # m.run_jmx()