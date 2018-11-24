from BasicComponent import CBasicComponent
import socket


class CBasicConnector(CBasicComponent):
    def __init__(self, compid, C_component_out, D_component_out, ConnectionAddr):
        CBasicComponent.__init__(self, compid, C_component_out, D_component_out)
        self.ConnectionAddr = ConnectionAddr
        
    def make_connection(self):
        # socket initialization
        s = socket.socket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        #s.settimeout(10)
        s.connect(self.ConnectionAddr)
        return s

#------------------------------------------