from app import ModifyJmx
from app import EasyExcel
import re,os

def parse_url(url):
    pattern = re.compile('(?P<protocol>https?)://(?P<domain>[^/]+)(?P<path>(.*)?)')
    mat_obj = pattern.search(url)

    pattern = re.compile('(?P<domain>[^:]+):?(?P<port>(.*)?)')

    mat_obj_min = pattern.search(mat_obj.group('domain'))
    return {
        'HTTPSampler_protocol': mat_obj.group('protocol'),
        'HTTPSampler_domain': mat_obj_min.group('domain'),
        'HTTPSampler_port': mat_obj_min.group('port'),
        'HTTPSampler_path': mat_obj.group('path')

    }

def recall_value(xlsx,sht,row,col):
    res = xlsx.getCell(sht, row, col)
    while row>0:
        if res==None:
            row -= 1
            res = xlsx.getCell(sht, row, col)
        else:
            return res


def normalize_assert(string):
    temp = string.split(',')
    res = []
    for i in temp:
        if i:
            if ':' in i:
                res.append(i.strip())
    
    return res
    
def parse_temp_xlsx(xlsx,sht,xlsx_path):

    Range = xlsx.getUsedRange(sht)#(rows,columns)
    #跳过前两行
    rows_num = Range[0]
    for i in range(4,rows_num+1):
        data = {}
        index = int(xlsx.getCell(sht, i, 1))
        url = recall_value(xlsx, sht, i, 4)

        data = parse_url(url)

        data['HTTPSampler_method'] = recall_value(xlsx, sht, i, 5).upper()

        header_str = xlsx.getCell(sht, i, 7)
        if header_str:
            data['headers'] = {x.split(':')[0]:x.split(':')[-1] for x in header_str.split(',')}
        
        body = xlsx.getCell(sht, i, 8)
        if body:
            data['Argument_value'] = body

        assertion = xlsx.getCell(sht, i, 10)
        if assertion:
            data['assert'] = normalize_assert(assertion)

        filename = xlsx.getCell(sht, i, 9)
        if filename:
            data['filename'] = os.path.join(xlsx_path,filename)

        num_threads = xlsx.getCell(sht, i, 11)
        if isinstance(num_threads,float):
            data['num_threads'] = int(num_threads)

        loops = xlsx.getCell(sht, i, 12)
        if isinstance(loops,float):
            data['loops'] =  int(loops)

        ramp_time = xlsx.getCell(sht, i, 13)
        if isinstance(ramp_time,float):
            data['ramp_time'] = int(ramp_time)
        

        if data['HTTPSampler_protocol'] == 'http':
            del data['HTTPSampler_protocol']
        
        if not data['HTTPSampler_port']:
            del data['HTTPSampler_port']


        yield (index, data)


def generate_jmx_and_report_repository(xlsx_path):
    dir_path = os.path.dirname(xlsx_path)
    jmx_rep = os.path.join(dir_path,'jmx_repository')
    if not os.path.exists(jmx_rep):
        os.mkdir(jmx_rep)
    report_rep = os.path.join(dir_path,'report')
    if not os.path.exists(report_rep):
        os.mkdir(report_rep)
    return (jmx_rep,report_rep)



if __name__ == '__main__':

    api_xlsx = 'api_test_temp.xlsx'

    xlsx_path = os.path.join(os.path.dirname(__file__),api_xlsx)
    sheet = 'pc端'

    xlsx = EasyExcel(xlsx_path)

    #cloud：是否准备到阿里云之类云端平台上去测试，这会决定csv文件路径值是否为相对路径
    #如果为True，将修改为相对路径test.csv，如果是False(默认)，将保留绝对路径
    #在本地测试需要绝对路径，但是在xlsx模版中不需要，但前提是与模版文件放在同一个目录下
    m = ModifyJmx(cloud=True)
    
    data = parse_temp_xlsx(xlsx,sheet,xlsx_path)
    jmx_path, report_path = generate_jmx_and_report_repository(xlsx_path)
    m.report_dir = report_path

    from pprint import pprint
    for i in range(4):
        m_data = data.__next__()
        pprint(m_data[-1])
        m.load_data(m_data[-1])
        m.jmx_path = os.path.join(jmx_path,'test_%d.jmx' % m_data[0])
        m.generate_jmx()
    del data
    xlsx.close()



