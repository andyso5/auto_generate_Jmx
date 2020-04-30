import csv

class ParseCSV():

    def __init__(self,path):
        self.file = open(path,'r')
        self.lines = csv.reader(self.file)

    def parse(self):
        res = {
            'data':[]
        }

        headers = self.lines.__next__()
        body = []
        for i in self.lines:
            body.append(i)
        res['data'] = [dict(zip(headers,x)) for x in body]
        self.file.close()
        return res
if __name__ == '__main__':
    import os
    p = os.path.join(os.path.dirname(__file__),'test.csv')
    from pprint import pprint
    pprint(ParseCSV(p).parse())



