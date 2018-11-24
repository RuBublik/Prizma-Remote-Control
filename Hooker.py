from BasicConnectorComponent import CBasicConnector
from BasicComponent import CBasicComponent
import time
import socket 
import threading
import struct
import wx
import datetime


class CHooker(CBasicConnector):
    def __init__(self, compid, C_component_out, ConnectionAddr, self_res, partner_res):
        CBasicConnector.__init__(self, compid, C_component_out, None, ConnectionAddr)
        
        self.self_res = (self_res[0]*1.0, self_res[1]*1.0)
        self.partner_res = partner_res
        self.coefficient = (self.partner_res[0] / self.self_res[0], self.partner_res[1] / self.self_res[1])
        print 'coefficient:     ' + str(self.coefficient)

    def prologue(self):
        print 'in prologue'
        self.hoockerSocket = self.make_connection()
        self.sqnumber = 0

    def process_data(self, data):
        try:
            if data != None:
                print data
                #self.sqnumber+=1
                header_SequenceNumber = str(self.sqnumber).zfill(4)
                header_TimeStamp = str(datetime.datetime.now())
                header_remainingSize = ''.zfill(6)
                device = data[0]
                state = data[1]
                
                if device == 'm' and state == 'm':  #mouse move
                    xykey = str(int(round(int(data[2][:4])*self.coefficient[0]))).zfill(4) + str(int(round(int(data[2][4:])*self.coefficient[1]))).zfill(4)
                else:
                    xykey = data[2]

                ready_packet = struct.pack('4s 26s 6s 1s 1s 8s', *(header_SequenceNumber, header_TimeStamp, header_remainingSize, device, state, xykey))
                self.hoockerSocket.send(ready_packet)
        except socket.timeout:  # continue? exit? if even needed?
            return 'continue'
        except socket.error as e:
            if e.errno == 10054:
                print self.compid + '   socket disconnected'
                return 'exit'    

    def epilogue(self):
        self.hoockerSocket.close()
        print 'epilogue:' + self.compid + ' is off...'

    



