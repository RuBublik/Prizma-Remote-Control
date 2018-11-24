from BasicComponent import CBasicComponent
import socket


class CBasicWaiter(CBasicComponent):
    def __init__(self, compid, C_component_out, D_component_out, ConnectionAddr):
        CBasicComponent.__init__(self, compid, C_component_out, D_component_out)
        self.ConnectionAddr = ConnectionAddr
        
    def wait_for_connection(self):
        # socket initialization
        s = socket.socket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        #s.settimeout(10)
        s.bind(self.ConnectionAddr)
        s.listen(1)
        print self.compid + ' - waiting for connection to be established'
        c, addr = s.accept()
        print self.compid + ' - connection established successfully'
        return c

#--------------------------------------------------