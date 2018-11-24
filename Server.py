import random
import string
import socket
import threading
import time

# server can not know if one comp has more than one ip address (such as laptop that has wifi and lan adresses, 127.0.0.1, comps with more than one ethernet card... and more)
class CServer:
    def __init__(self):
        self.address_dict = {}   # id : ip
        # len(ip) = 15, len(id) = 9

        self.id_generator = socket.socket()
        #self.id_generator.settimeout(2)
        self.id_generator.bind(('',5555))
        self.id_generator.listen(1)

        self.ip_exchanger = socket.socket()
        #self.ip_exchanger.settimeout(2)
        self.ip_exchanger.bind(('',5556))
        self.ip_exchanger.listen(1)
        
        self.disconnector = socket.socket()
        #self.disconnector.settimeout(2)
        self.disconnector.bind(('',5557))
        self.disconnector.listen(1)

    def start(self):
        t1 = threading.Thread(target=self.handle_new_clients)
        t2 = threading.Thread(target=self.handle_ip_exchange)
        t3 = threading.Thread(target=self.handle_client_disconnection)
        
        t1.start()
        t2.start()
        t3.start()
        
        t1.join()
        t2.join()
        t3.join()

    def stripIP(self, recv):
        split = recv.split('.')
        split[0] = str(int(split[0]))
        join = '.'.join(split)
        return join

    def handle_new_clients(self):
        print 'new clients'
        while True:
            try:
                c, addr = self.id_generator.accept()
                recv = c.recv(15)
                ip = self.stripIP(recv)
                if self.address_dict:    # empty disctionaries are represented by False
                    if not ip in self.address_dict.values():   
                        id_value = self.generate_rand_id()
                        # ensure no same id's can be given:
                        while id_value in self.address_dict.keys():  
                            id_value = self.generate_rand_id()
                        self.address_dict[id_value] = ip
                        print 'new client: address: ' + str(addr) + '   updated ip dict:  ' + str(self.address_dict)
                    else:   # somebody already connected with this ip
                        id_value = 'EXIST'.zfill(9) # returns this instead of id
                else:
                    id_value = self.generate_rand_id()
                    self.address_dict[id_value] = ip
                    print 'new client: address: ' + str(addr) + '   updated ip dict:  ' + str(self.address_dict)
                c.send(str(id_value))
            except Exception as e:
                print 'new clients:  ' + str(e.args)
                
    def handle_ip_exchange(self):
        print 'ip exchange'
        while True:
            try:
                c, addr = self.ip_exchanger.accept()
                request_id = c.recv(9)
                print '---- exchange: ' + str(addr) + ' requested ip of: ' + request_id
                ans = self.address_dict.get(int(request_id), 'ERROR')    # id, or if does not exist - 'error'
                c.send(ans.zfill(15))
            except Exception as e:
                print 'exchange ip: ' + str(e.args)
                
    def handle_client_disconnection(self):
        print 'disconnections'
        while True:
            try:
                c, addr = self.disconnector.accept()
                traitor_id = c.recv(9)
                self.address_dict.pop(int(traitor_id))
                print 'id: ' + traitor_id + '   disconnected.   updated ip dict:  ' + str(self.address_dict)
            except Exception as e:
                print 'handle disconnect:  ' + str(e.message)
        


    def generate_rand_id(self):
        rnumber = 0
        for i in range(9):
            rnumber = rnumber*10 + random.randint(1,9)
        print rnumber
        return rnumber



def test():
    i=0
    while i<5:
        time.sleep(2)
        print 'test' + str(i)
        s = socket.socket()
        s.connect(('127.0.0.1', 5555))
        s.send( socket.gethostbyname(socket.gethostname()) )
        print s.recv(9)
        s.close()
        i += 1
        



if __name__ == '__main__':
    s = CServer()
    s.start()