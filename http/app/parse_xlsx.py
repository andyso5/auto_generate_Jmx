# 如果现实找不到win32api，应将..\AppData\Local\Programs\Python\Python37\lib\site-packages\win32
# 添加到系统路径里
try:
    from win32com.client import Dispatch, DispatchEx
except ModuleNotFoundError:
    import sys
    part = r'Python\Python37\lib\site-packages'
    for i in sys.path:
        anchor = i.find(part)
        if anchor!=-1:
            sys.path.append(i[:anchor ] + part + r'\win32')
            break
    
    from win32com.client import Dispatch,constants
import win32com.client
import os

class EasyExcel():

    def __init__(self, filename=None): 
        #需要绝对路径
        self.xlApp = win32com.client.Dispatch('Excel.Application') 
        if filename: 
            self.filename = filename 
            self.xlBook = self.xlApp.Workbooks.Open(filename) 
        else: 
            self.xlBook = self.xlApp.Workbooks.Add() 
            self.filename = ''

    def trans_absdir(self,file_name):
        #在此脚本同级目录下寻找文件名，并返回绝对路径
        if ':\\' not in file_name:
            if os.path.exists(file_name):
                return os.path.join(os.path.dirname(__file__),file_name)
            else:
                print('请输入绝对路径，或是class:EasyExcel所在目录中的文件的相对路径\n')
                return file_name
        else:
            return file_name


    def getCell(self, sheet, row, col): 
        "Get value of one cell" 
        sht = self.xlBook.Worksheets(sheet) 
        return sht.Cells(row, col).Value 

    def setCell(self, sheet, row, col, value,color = None): 
        "set value of one cell" 
        sht = self.xlBook.Worksheets(sheet) 
        sht.Cells(row, col).Value = value #用的是默认字体
        #sht.Cells (row, col).Interior.Color = color #指的是单元格背景颜色，搜索xlBackground

    def getRange(self, sheet, row1, col1, row2, col2): 
        "return a 2d array (i.e. tuple of tuples)" 
        sht = self.xlBook.Worksheets(sheet) 
        return sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Value  #返回的是一个二维数组，两个Cells的四个参数，确定了表格区域的对角
        #range除了可以用数字表示外，还可以用excel自带的大写字母加数字表示，形如 Range('A1:A4')

    def getUsedRange(self,sheet):
        sht = self.xlBook.Worksheets(sheet)
        info  = sht.UsedRange
        return (info.Rows.Count,info.Columns.Count)
        # return sht.Range('A65536').End(-4162).Row #xlUp=-4162

    def deleteRow(self,sht,cell=None):
        sht = self.xlBook.Worksheets(sht)
        if cell:
            return sht.Range(cell).Delete()
        else:
            pass

    def parse(self,dst='',sheet='Sheet1'):
        Range = self.getUsedRange(sheet)
        res = []
        data = self.getRange(sheet, row1=1, col1=1, row2=Range[0], col2 = Range[1])
        head = data[0]
        body = data[1:]
        body_list = []
        for i in body:
            row = []
            for j in i:
                if isinstance(j,float) and int(j)==j:
                    row.append(int(j))
                        
                else:
                    row.append(j)
            body_list.append(row)

        self.close()
        res = {
                'data':[dict(zip(head,x)) for x in body_list]
            }
        if dst:
            self.save_res_with_json(res,dst)
            # self.close()
        else:
            # self.close()
            return res

    def save_res_with_json(self,res,dst):
        import json
        with open(dst,'w') as file:
            file.write(json.dumps(res))

    def save(self, newfilename=None): 
        if newfilename: 
            self.filename = newfilename 
            self.xlBook.SaveAs(newfilename)#save()里面也可以带参数，作为文件名，保存同时修改文件名的意思吗？ 
        else: 
            self.xlBook.Save()

    def close(self,change=False): 
        self.xlBook.Close(SaveChanges=change)#貌似无论是True还是False，结果都是不保存的##需要与Quit()联用？
        self.xlApp.Quit()

if __name__ == '__main__':

    sheet  = 'Sheet1'
    from pprint import pprint

    # p = r'E:\xiaoao\http_api_test\http\test.xlsx'
    p = os.path.join(os.path.dirname(os.path.dirname(__file__)),'test.xlsx')

    xlxs = EasyExcel(p)

    # pprint(xlxs.parse('test.json'))
    pprint(xlxs.parse())

