import multiprocessing
import threading
import Queue
#import socket
#import time

class CBasicComponent:
    def __init__(self, compid, C_component_out, D_component_out=None):
        self.compid = compid
        self.C_component_out = C_component_out
        self.D_component_out = D_component_out
        self.D_Queue_in = multiprocessing.Queue(10)
        self.C_Queue_in = multiprocessing.Queue()
    
    # the only 3 component-specific functions:
    def prologue(self):
        pass
    def process_data(self, data):
        pass
    def epilogue(self):
        pass

    # generic functions, same in all components:
    def thread_main(self):
        print self.compid +' - in thread_main'
        self.prologue()
        while True:
            try:
                command = self.recv_command()
                if self.process_command(command) == 'exit':
                    break
                data = self.recv_data()
                if self.process_data(data) == 'exit':
                    break
            except Exception as e:
                print 'basic: thread_main: '+ self.compid + str(e.args)
        self.epilogue()

    def start(self):
        self.process = threading.Thread(target=self.thread_main)
        self.process.start()

    def exit(self):
        if not self.C_component_out == None:
            self.C_component_out.send_command(self.compid, 'exit')
        #print self.compid + ' waiting to join'   
        #self.process.join()
        print self.compid + '   dead'

    def recv_command(self, blocking=False):
        # by default non blocking
        try:    
            compid, command = self.C_Queue_in.get(blocking)
            print self.compid + ':   received command: '+ command + '  from: ' + compid
            return (compid, command)
        #except Queue.Empty:
        except:
            return None
    
    def send_command(self, compid, command, blocking=False):
        # by default non blocking
        self.C_Queue_in.put((compid, command), blocking)

    def recv_data(self, blocking=False):
        #by default non blocking
        try:    
            dat = self.D_Queue_in.get(blocking)
            return dat
        except Queue.Empty:
            return None

    def send_data(self, dat, blocking=False):
        '''puts data from previous component in self queue'''
        # by default non blocking
        try:
            self.D_Queue_in.put(dat, blocking)
        except Queue.Full:
            pass
        except IOError:
            print 'basic: send_data: '+ self.compid + str(e.args)

    def process_command(self, tup):
        if not tup == None:
            compid, command = tup
            if command == 'exit':   # for all
                #print self.compid + ' exit'
                return 'exit'
            else:
                return 'unknown'
        return 'continue'
    
# ends
#-----------------------------------------------------
