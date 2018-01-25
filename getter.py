import socket, pickle
from PIL import Image

import StringIO
import time

s = socket.socket()
s.bind(('127.0.0.1',4444))
s.listen(1)
print 'waiting for connection to be established'
getter, addr = s.accept()
print 'connection established successfully'

data = getter.recv(1000000)
print type(data), len(data)
getter.close()
'''
f = open('test1.txt','w')
f.write(data)
f.close()
print 'f.write done'
f = open('test1.txt','w')
'''
unpkd = pickle.loads(data)
print type(unpkd)
im = Image.open(unpkd)#im = Image.open(StringIO.StringIO(data))
raw_input()




    

