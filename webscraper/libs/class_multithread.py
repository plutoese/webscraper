# coding=UTF-8

import threading
from time import ctime


class MultiThread(threading.Thread):
    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.res = None

    def get_result(self):
        return self.res

    def run(self):
        print('Starting ',self.name,' at: ',ctime())
        self.res = self.func(*self.args)
        print(self.name,' finished at: ',ctime())

if __name__ == '__main__':
    pass