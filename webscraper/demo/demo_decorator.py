# coding=UTF-8

import time

# 类装饰器：Timer
class Timer:
    def __init__(self, func):
        self.func = func
        self.alltime = 0

    def __call__(self, *args, **kwargs):
        start = time.clock()
        result = self.func(*args, **kwargs)
        elapsed = time.clock() - start
        self.alltime += elapsed
        print('%s: %.5f, %.5f' % (self.func.__name__, elapsed, self.alltime))
        return result

@Timer
def fsum(n):
    return sum(range(n))

fsum(10000)
fsum(100000)
fsum(1000000)
fsum(10000000)
























