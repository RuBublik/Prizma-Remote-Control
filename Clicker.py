import socket
import time
from BasicWaiterComponent import CBasicWaiter
import struct
import datetime
import wx



class CClicker(CBasicWaiter):
    def __init__(self, compid, C_component_out, ConnectionAddr):
        CBasicWaiter.__init__(self, compid, C_component_out, None, ConnectionAddr)
        self.User_Simulator = wx.UIActionSimulator()

        self.header_len = 36
        self.event_len = 10
        

    def prologue(self):
        self.clickerSocket = self.wait_for_connection()

    def process_data(self, data):
        try:
            packet = self.clickerSocket.recv(self.header_len + self.event_len)
            if packet != None:
                unpacked_packet = struct.unpack('4s 26s 6s 1s 1s 8s', packet)
                print 'clicker: ' + str(unpacked_packet)
                
                # packet's parsing to components:
                sequenceNumber = int(unpacked_packet[0])
                timeStamp = str(unpacked_packet[1])
                #if self.validate_time(timeStamp): 
                remaining = int(unpacked_packet[2])
                device = unpacked_packet[3] # m - mouse, k - keyboard
                state = unpacked_packet[4]  # u -up, d - down, m - move, f - forward(scroll), b - backward(scroll)
                xykey = unpacked_packet[5]  # xy or key

                if device == 'k':
    
                    if state == 'u':    #up
                        keyCode = int(xykey)
                        self.User_Simulator.KeyUp(keyCode)

                    elif state == 'd':  #down
                        keyCode = int(xykey)
                        self.User_Simulator.KeyDown(keyCode)
                
                elif device == 'm':

                    if state == 'm':    # move
                        x = int(xykey[:4])
                        y = int(xykey[4:])
                        self.User_Simulator.MouseMove(x,y)
                    
                    elif state == 'd':
                        button = int(xykey)
                        self.User_Simulator.MouseDown(button)
                    
                    elif state == 'u':
                        button = int(xykey)
                        self.User_Simulator.MouseUp(button)
        
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
        self.clickerSocket.close()
        print 'epilogue:' + self.compid + ' is off...'



    def validate_time(self, timestr):
        cmd_timestamp = datetime.datetime(year=int(timestr[0:4]), month=int(timestr[5:7]), day=int(timestr[8:10]), hour=int(timestr[11:13]), minute=int(timestr[14:16]), second=int(timestr[17:19]), microsecond=int(timestr[20:]))
        print cmd_timestamp
        delta = datetime.datetime.now() - cmd_timestamp
        print delta
        if delta.seconds > 1:
            print 'false'
            return False
        print 'True'
        return True                        

# ends
#-----------------------------------------------------                    
