import socket, pickle
from PIL import ImageGrab

s = socket.socket()
s.connect(('127.0.0.1',4444))

im = ImageGrab.grab()
#im.save('scrn.jpg')
#print 'saved'
w, h = im.size
print (w,h)

s.send(pickle.dumps((w,h)))
s.send(im.tobytes())
s.close()