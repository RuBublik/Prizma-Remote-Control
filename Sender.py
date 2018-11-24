import socket
import struct
import time
import multiprocessing
import datetime
#from PIL import Image
from BasicWaiterComponent import CBasicWaiter
#import sys
import Queue
#from Grabber import CFileSaver


class CSender(CBasicWaiter):
    def __init__(self, compid, C_component_out, ConnectionAddr):
        CBasicWaiter.__init__(self, compid, C_component_out, None, ConnectionAddr)
        self.read_len = 1000
        self.header_len = 36

    def prologue(self):
        self.senderSocket = self.wait_for_connection()
        self.sqnumber = 0

    def process_data(self, data):
        try:
            if data != None:
                self.sqnumber=0
                # packet build:
                header_SequenceNumber = str(self.sqnumber).zfill(4)                               
                header_TimeStamp = str(datetime.datetime.now())               
                data_chunk = data.read(self.read_len)    
                remaining_size = len(data.getvalue()) - len(data_chunk)
                total_size = len(data_chunk)
                # read/send process:
                while data_chunk:
                    header_remaingSize = str(remaining_size).zfill(6)
                    packed_packet = struct.pack('4s 26s 6s ' + str(len(data_chunk)) + 's', *(header_SequenceNumber, header_TimeStamp, header_remaingSize, data_chunk))
                    sended = self.senderSocket.send(packed_packet)
                    # prepare next packet:
                    self.sqnumber += 1
                    header_SequenceNumber = str(self.sqnumber).zfill(4)
                    data_chunk = data.read(self.read_len)
                    remaining_size -= len(data_chunk)
                    total_size += len(data_chunk)
                print 'sended frame: ' + header_TimeStamp + ' in ' + str(self.sqnumber) + ' packets, ' + str(total_size)
                return 'continue'
        except socket.timeout:
            return 'continue'
        except socket.error as e:
            if e.errno == 10054:
                print self.compid + '   socket disconnected'
                return 'exit'
            else:
                print self.compid + str(e.args)
        return 'continue' 
        
    def epilogue(self):
        self.senderSocket.close()
        print 'epilogue:' + self.compid + ' is off...'

# ends    
#-----------------------------------------------------


    
    

