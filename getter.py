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

size = pickle.loads(getter.recv(1024))
scrn = getter.recv(10000000)
print type(scrn), len(scrn), size
getter.close()
'''
f = open('test1.txt','w')
f.write(scrn)
f.close()
print 'f.write done'
f = open('test1.txt','w')
'''
#unpkd = pickle.loads(scrn)
#print type(unpkd)
im = Image.frombytes('RGB', size, scrn)
im.show()#im = Image.open(StringIO.StringIO(scrn))
raw_input()




    

