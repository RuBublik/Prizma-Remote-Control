import socket, pickle
from PIL import ImageGrab

s = socket.socket()
s.connect(('127.0.0.1',4444))
im = ImageGrab.grab()
im.save('scrn.jpg')
print 'saved'
d = pickle.dumps(im)#d = t.tobytes()
s.send(d)
s.close()