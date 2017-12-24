# coding = UTF-8

from collections import deque

n = [1,2,3,4,5,6,7,8,9]
step = 10
dn = deque(n)

while (len(dn) > 0):
    if len(dn) >= step:
        print([dn.popleft() for i in range(step)])
    else:
        print([dn.popleft() for i in range(len(dn))])