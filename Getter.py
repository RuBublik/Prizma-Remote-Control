from BasicConnectorComponent import CBasicConnector
from io import BytesIO
import time
import threading
#import Sender
#import Getter
#import Grabber
import socket
import struct
#from Grabber import CFileSaver
import MyCustomEvents
import wx


class CGetter(CBasicConnector):
    def __init__(self, compid, C_component_out, D_component_out, ConnectionAddr):
        CBasicConnector.__init__(self, compid, C_component_out, D_component_out, ConnectionAddr)
        self.header_len = 36
        self.read_len = 1000

    def prologue(self):
        self.getterSocket = self.make_connection()
        #self.banned_time = 0
        self.bool_discard = False

    def process_data(self, data):
        try:        
            ImgBuffer = BytesIO()
            remaining = 1036
            total_size = 0
            while remaining > 0:
                try:
                    recv_len = min(self.read_len, remaining) + self.header_len
                    packet = self.getterSocket.recv(recv_len)
                    if packet != None:
                        unpacked_packet = struct.unpack('4s 26s 6s ' + str( len(packet)-self.header_len ) + 's', packet)
                        sequenceNumber = int(unpacked_packet[0])
                        timeStamp = str(unpacked_packet[1])
                        remaining = int(unpacked_packet[2])
                        data_chunk = unpacked_packet[3]
                        total_size += len(data_chunk)
                        #if self.banned_time != timeStamp:
                        ImgBuffer.write(data_chunk)
                    else:
                        return 'continue'
                except:
                    # continue getting all packets for this imagge, but in the end do not pass it 
                    self.bool_discard = True    
                    #return 'continue'  
            if not self.bool_discard:
                #print 'received frame: ' + timeStamp + ' in ' + str(sequenceNumber) + ' packets, ' + str(total_size) + ' | ' + str(len(ImgBuffer.getvalue()))
                print 'received full frame'
                ImgBuffer.seek(0)
                self.D_component_out.send_data(ImgBuffer)
            else:
                print '\n\n\n\nframe discrded\n\n\n\n'
                self.bool_discard = False
            return 'continue'

        except socket.timeout:  
            return 'continue'
        except socket.error as e:
            if e.errno == 10054:
                print self.compid + '   socket disconnected'
                return 'exit'
          
    def epilogue(self):
        self.getterSocket.close()
        print 'epilogue:' + self.compid + ' is off...'


# ends
#--------------------------------------------------------