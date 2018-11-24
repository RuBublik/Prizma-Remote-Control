import wx
from BasicComponent import CBasicComponent
import time
import threading
import multiprocessing
import socket
import string
import random
import sys
import os

import Hooker
import Getter
import Sender
import Grabber
import MyCustomEvents
import Renderer
import Clicker

#import ClientGui
#import Getter1
#import Hooker1
#import MyCustomEvents
#import Clicker1
#import Clicker2


# Define event for updating the screen viewer
EVT_UPDATE_PICTURE_ID = wx.NewId()
# Define event for quiting the GUI
EVT_PARTNER_QUIT = wx.NewId()

def connectEvent(window, function, evt):
    """defines given event """
    window.Connect(-1, -1, evt, function)

def determine_ip():
    ''' returns this comp's. ip '''
    return (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close())for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]



class ApplicationGUI(wx.Frame):
    def __init__(self):
        if len(sys.argv) > 1:
            try:
                print 'args from command'
                self.meetingPointIP = sys.argv[1]
                self.listenPort = int(sys.argv[2])
            except:
                print 'wrong arguments, can not launch :/'
        else:
            print 'default args'
            f = open('config.txt', 'r')
            read = f.read()
            args = read.split(' ')
            self.meetingPointIP = args[0]
            self.listenPort = int(args[1])
            f.close()
        print self.meetingPointIP
        print 'set'

        # thread listens to incoming calls
        self.restart_wait_for_call()

        # get information needed to present on client window
        myip = determine_ip()
        print 'my ip: ' + myip
        sock = socket.socket()
        sock.connect((self.meetingPointIP, 5555))
        time.sleep(0.1)
        print sock.send( myip.zfill(15) ) # works fine in lan, questionable with wan
        self.id = sock.recv(9)
        sock.close()
        if self.id != 'EXIST'.zfill(9):
            self.own_password = self.generate_rand_password()
            wx.Frame.__init__( self, None, -1, 'Client' )
            self.show_client_window()
            self.make_control_window()
            #self.Show(True)
        elif self.id == 'EXIST'.zfill(9):
            wx.Frame.__init__( self, None, -1, 'Client' )
            secclientdlg = wx.MessageDialog(self, message='Sorry, your IP is currently being used by another client.', caption='Something Fucked Up...', style=wx.OK | wx.ICON_WARNING)
            secclientdlg.ShowModal()

    def stripIP(self, recv):
        split = recv.split('.')
        split[0] = str(int(split[0]))
        join = '.'.join(split)
        return join
    
    def restart_wait_for_call(self):
        self.listener = socket.socket()
        try:
            self.listener.bind(('', self.listenPort))
            self.listener.listen(1)
            self.flag_quit = False
            self.listener_thread = threading.Thread(target=self.wait_for_call)
            self.listener_thread.start()
        except Exception as e:
            print 'restart:' + str(e.args)
        

    def abort_wait_for_call(self):
        # trick the waiting thread to stop waiting on accept and finish the thread
        self.flag_quit = True
        s = socket.socket()
        try:
            s.connect(('127.0.0.1', self.listenPort))
        except:
            print 'aux abort,   could not connect'
        s.close()


    def abort_wait_for_call2(self):
        # trick the waiting thread to stop waiting on accept and finish the thread
        self.flag_quit = True
        '''
        t = threading.Thread(target=self.aux_abort) # must connect from another thread
        t.start()
        t.join()
        '''
        self.aux_abort()
        self.listener.close()

    def wait_for_call(self):
        while True:
            try:
                c, addr = self.listener.accept()
                if self.flag_quit:
                    c.close()
                    self.listener.close() 
                    break
                recv_password = c.recv(6)
                print 'received password: ' + recv_password
                if recv_password == self.own_password:
                    c.send('1')  # ok
                    self.partner_ip = addr[0]
                    self.functionality = 's'
                    print 'accepted call, starting as sender'
                    #---- create application window and start application as sender:
                    self.app_process = ApplicationProcess(self.control_frame, self.functionality, self.partner_ip, None)
                    global EVT_PARTNER_QUIT
                    connectEvent(self.control_frame, self.Harakiri, EVT_PARTNER_QUIT)
                    self.control_frame.Show()
                    self.app_process.start()
                    # disable future incoming calls:
                    #self.abort_wait_for_call()
                    self.listener.close()
                    break
                else:
                    c.send('0')  # don't mess with me
                    '''
                    self.listener = socket.socket()
                    self.listener.bind()
                    self.listener.listen()
                    '''
            except socket.timeout:
                print 'timeout'
                
        print 'not waiting for calls anymore'

    def OnConnect(self, e):
        # quit listener thread to make incoming connections un-available while this side is conneting
        self.abort_wait_for_call()
        self.listener_thread.join()
        print 'listener thread join'

        partnerID = self.the_entry.GetValue()
        print 'requested id: ' + partnerID
        waitdialog = wx.Dialog(self, title='wait')
        waitdialog.Show()
        try:
            # exchanges partner's id with his ip:
            sock = socket.socket()
            sock.connect((self.meetingPointIP, 5556))
            sock.send(partnerID)
            recv = sock.recv(15)
            print 'recv - : ' + recv
            sock.close()
        except Exception as e:
            print 'exchange: ' + str(e.args) + '\n\n starting listen to incoming again'
            self.restart_wait_for_call()  
            return        

        # uses partner's ip to check password:
        if recv == 'ERROR'.zfill(15): # means server did no recognize id
            waitdialog.Show(False)
            wrongiddlg = wx.MessageDialog(self, message='Sorry, no client with such id is connected.', caption='Something Fucked Up...', style=wx.OK | wx.ICON_INFORMATION)
            wrongiddlg.ShowModal()
            print '\n\n starting listen to incoming again'
            self.restart_wait_for_call()    
            return
        reply_ip = self.stripIP(recv)

        try:
            sock = socket.socket()
            sock.connect((reply_ip, 7777))
        except socket.error: # means connection can not be established
            sock.close()
            print 'connect: socket.error'
            waitdialog.Show(False)
            notavailabledlg = wx.MessageDialog(self, message='Sorry, client with such id is not available.', caption='Something Fucked Up...', style=wx.OK | wx.ICON_INFORMATION)
            notavailabledlg.ShowModal()
            print '\n\n starting listen to incoming again'
            self.restart_wait_for_call()    
            return

        # if connected successfully:
        waitdialog.Show(False)
        passdlg = wx.PasswordEntryDialog(self, 'Enter Partner\'s password below:', 'Password Entry Dialog')
        btn = passdlg.ShowModal()
        if btn == wx.ID_OK:
            # do not print password without checking for only english alpha numeic input.
            password_input = passdlg.GetValue()
            passdlg.Destroy()
            try:
                sock.send(password_input)   # sends password to second client
            except UnicodeEncodeError:
                sock.close()
                wrongpassdlg = wx.MessageDialog(self, message='Bad input.\r\nThe password consists of English alpha-numeric symbols only.', caption='Something Fucked Up...', style=wx.OK | wx.ICON_ERROR)
                wrongpassdlg.ShowModal()
                print '\n\n starting listen to incoming again'
                self.restart_wait_for_call()    
                return
            reply = sock.recv(1)  
            print 'reply: ' + reply 
            sock.close()
            if reply == '1':
                self.partner_ip = reply_ip
                self.partner_id = partnerID
                self.functionality = 'r'
                #---- create application window and start application as controller:
                try:
                    self.show_monitor_window()
                    self.app_process = ApplicationProcess(self.monitor_frame, self.functionality, self.partner_ip, self.projected_image)
                    self.app_process.start()
                    # quit listener thread so nobody can connect until session ends
                    self.abort_wait_for_call()
                except Exception as e:
                    print 'open window: ' + str(e.args) + '\n\n starting listen to incoming again'
                    self.restart_wait_for_call()   
            elif reply == '0':
                wrongpassdlg = wx.MessageDialog(self, message='Wrong password, go hack another guy\'s comp.', caption='Something Fucked Up...', style=wx.OK | wx.ICON_ERROR)
                wrongpassdlg.ShowModal()
                print '\n\n starting listen to incoming again'
                self.restart_wait_for_call()   

    def Harakiri(self, evt=None):
        print '\n\n\n\nharakiri\n\n\n\n'
        try:    # if no application_process data member was built yet, exception will be raised
            self.app_process.send_command('ApplicationGUI', 'exit')
            print 'Harakiri:    send exit to app_process'
        except Exception as e:
            print 'harakiri:    '+str(e.args)
            
        try:    # if functuanality is not defined yet exception will be raised (or if this is the side who quit first, the way to get here was closing this frame)
            if self.functionality == 's':
                self.control_frame.Destroy()
                print 'Harakiri:    control frame destroyed'
            elif self.functionality == 'r':
                self.monitor_frame.Destroy()
                print 'Harakiri:    monitor frame destroyed'
        except Exception as e: 
            print 'harakiri:    '+str(e.args)

        # if call was not for complete quit, make client be ready for incoming calls again:
        if evt != 'client':
            # prepare for returning to client normal operation:
            # init frame and prepare all windows again,
            self.make_control_window()
            print '\n\n starting listen to incoming again\n\n'
            self.restart_wait_for_call()
        else:
            print '\n\n\n\n no restart \n\n\n\n'

    def onEndSession(self, e):
        if e.CanVeto():
            if wx.MessageBox(message='Do you really want to quit?', caption='Double Check', style=wx.ICON_QUESTION|wx.YES_NO) != wx.YES:
                e.Veto()    #cancel quit
                return
        # if not veto, and user really wants to quit:
        self.Harakiri()
        
    def onClientClose(self, e):
        # kill listen to incoming calls thread
        self.abort_wait_for_call()
        self.listener_thread.join()
        print 'listener thread join'
        self.listener.close()
        print 'listen socket was closed'
        # acknowledge server about disconnection
        sock = socket.socket()
        sock.connect((self.meetingPointIP, 5557))
        sock.send(self.id)
        sock.close()
        # quit ongoing session if there is one
        self.Harakiri('client')
        # after all of child threads are dead,
        self.Destroy()
    
    def onDisconnectButton(self, e):
        #wx.PostEvent(self.control_frame, wx.CloseEvent())
        self.control_frame.Close()  # generates a wx.CloseEvent event, however does not close the window - Harakiri will do it.

    def onEntryKeypress(self, e):
        # accepts int (numbers) only and limits len to 9
        keycode = e.GetKeyCode()
        print keycode
        if (ord('0') <= keycode <= ord('9') and len(self.the_entry.GetValue()) < 9 ) or keycode == wx.WXK_BACK or keycode == wx.WXK_DELETE or keycode == wx.WXK_LEFT or keycode == wx.WXK_RIGHT:
            e.Skip()
    
    def onFocus(self, e):
        print 'focus gained event'
        self.monitor_frame.SetFocus()
    '''
    def onEnterWin(self, e):
        print 'enter win'
        try:
            self.app_process.send_data('hover.enter')
        except Exception as e:
            print e.args
    
    def onLeaveWin(self, e):
        print 'enter win'
        try:
            self.app_process.send_data('hover.leave')
        except Exception as e:
            print e.args
    '''
    def OnSliderScroll(self, e):
        val = self.qualitySL.GetValue()
        print val
        self.app_process.send_data('quality.'+str(val))

    def show_monitor_window(self):
        #disp = wx.Display() # return rect obejct, using default screen
        #size = disp.GetClientArea()[2:] # RECT's fields [:2] not used
        #gangamStyle = (wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE) & ~ wx.MAXIMIZE_BOX

        self.monitor_frame = wx.Frame( None, -1, title='monitor')#, style=gangamStyle, size = size)#self, -1, title='monitor')
        self.monitor_frame.Bind(wx.EVT_CLOSE, self.onEndSession)

        self.monitor_panel = wx.Panel( self.monitor_frame)
        
        self.monitor_panel.Bind(wx.EVT_SET_FOCUS, self.onFocus)
        '''
        self.monitor_panel.Bind(wx.EVT_KILL_FOCUS, self.onLoseFocus)
        '''
        self.projected_image = wx.StaticBitmap(self.monitor_panel, -1, bitmap=wx.EmptyBitmap(1000,1000))
        '''
        self.projected_image.Bind(wx.EVT_ENTER_WINDOW, self.onEnterWin)
        self.projected_image.Bind(wx.EVT_LEAVE_WINDOW, self.onLeaveWin)
        '''
        global EVT_UPDATE_PICTURE_ID
        connectEvent(self.monitor_frame, self.onUpdate, EVT_UPDATE_PICTURE_ID)
        global EVT_PARTNER_QUIT
        connectEvent(self.monitor_frame, self.Harakiri, EVT_PARTNER_QUIT)

        self.monitor_frame.Show()
        self.monitor_frame.Maximize()

    def make_control_window(self):
        # disable pictures  -?
        # disable input     -?
        
        self.control_frame = wx.Frame( self, -1, title='controls' )
        self.control_frame.SetMinSize((200,200))
        self.control_frame.SetMaxSize((300,300))
        self.control_frame.Bind(wx.EVT_CLOSE, self.onEndSession)

        self.control_panel = wx.Panel( self.control_frame )
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        disconnectBTN = wx.Button(self.control_panel, -1, label='End Session')
        disconnectBTN.Bind(wx.EVT_BUTTON, self.onDisconnectButton)
        main_sizer.Add(disconnectBTN, proportion=1, flag=wx.ALL|wx.EXPAND)
        main_sizer.AddStretchSpacer(10)

        self.qualitySL = wx.Slider(self.control_panel, -1, 60, 1, 100, style=wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.qualitySL.SetTickFreq(10)
        self.qualitySL.Bind(wx.EVT_SLIDER, self.OnSliderScroll) 
        main_sizer.Add(self.qualitySL, proportion=1, flag=wx.ALL|wx.EXPAND)

        self.control_panel.SetSizer(main_sizer)
        self.control_panel.Fit()

    def show_client_window(self):
        self.SetMinSize((500,200))
        self.SetMaxSize((650,300))
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap("prizmaIcon.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.Bind(wx.EVT_CLOSE, self.onClientClose)

        # left side: (waiter)
        panel = wx.Panel(self) 
        main_h_box = wx.BoxSizer(wx.HORIZONTAL)

        sbox1 = wx.StaticBox(panel, -1, 'ALLOW REMOTE CONTROL:')
        r_static_sizer = wx.StaticBoxSizer(sbox1, wx.VERTICAL) 

        h_waiterbox = wx.BoxSizer(wx.HORIZONTAL)

        v_labelbox = wx.BoxSizer(wx.VERTICAL)
        self.id_label = wx.StaticText(panel, -1, 'YOUR ID:')
        self.pass_label = wx.StaticText(panel, -1, 'PASSWORD: ')
        v_labelbox.Add(self.id_label, proportion=1, flag=wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, border=10)
        v_labelbox.Add(0,10,0)
        v_labelbox.Add(self.pass_label, proportion=1, flag=wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, border=10)
        
        v_textctrlbox = wx.BoxSizer(wx.VERTICAL)
        splitid = self.id[:3]+' '+self.id[3:6]+' '+self.id[6:]  # for easier reading
        self.id_textctrl = wx.TextCtrl(panel, -1, splitid, size=(100, 25), style=wx.TE_READONLY)
        self.pass_textctrl = wx.TextCtrl(panel, -1, self.own_password, size=(100, 25), style=wx.TE_READONLY) 
        v_textctrlbox.Add(self.id_textctrl, proportion=1, flag=wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, border=10)
        v_textctrlbox.Add(self.pass_textctrl, proportion=1, flag=wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, border=10)

        h_waiterbox.Add(v_labelbox)
        h_waiterbox.Add(v_textctrlbox)

        r_static_sizer.Add(h_waiterbox, 0, wx.ALL|wx.CENTER, 10)
        
        # right side: (connector)
        sbox2 = wx.StaticBox(panel, -1, 'CONTROL REMOTE COMPUTER:') 
        l_static_sizer = wx.StaticBoxSizer(sbox2, wx.VERTICAL)

        v_connectorbox = wx.BoxSizer(wx.VERTICAL)

        h_enteridbox = wx.BoxSizer(wx.HORIZONTAL)
        self.entry_label = wx.StaticText(panel, -1, 'PARTNER\'S ID: ')
        self.the_entry = wx.TextCtrl(panel, size=(100, 25))
        self.the_entry.Bind(wx.EVT_CHAR, self.onEntryKeypress)
        h_enteridbox.Add(self.entry_label, proportion=1, flag=wx.ALL|wx.ALIGN_LEFT|wx.EXPAND|wx.FIXED_MINSIZE, border=10)
        h_enteridbox.Add(self.the_entry, proportion=1, flag=wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND|wx.FIXED_MINSIZE, border=10)

        self.connectBtn = wx.Button(panel, -1, label='connect')
        self.connectBtn.Bind(wx.EVT_BUTTON, self.OnConnect)

        v_connectorbox.Add(h_enteridbox)
        v_connectorbox.Add(0,18,0)        
        v_connectorbox.Add(self.connectBtn, proportion=1, flag=wx.EXPAND, border=10) 

        l_static_sizer.Add(v_connectorbox, 0, wx.ALL|wx.CENTER, 10)
        

        main_h_box.Add(r_static_sizer,0, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5) 
        main_h_box.AddStretchSpacer(10)
        main_h_box.Add(l_static_sizer,0, wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, 5) 
        panel.SetSizer(main_h_box) 
        self.Centre() 
            
        panel.Fit() 
        self.Show() 
    

    def generate_rand_password(self):
        rpass = ''
        allchars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        for i in range(6):
            rpass += "".join(random.choice(allchars))
        return rpass

    def onUpdate(self, event):
        #self.projected_image.SetBitmap(wx.BitmapFromImage(wx.ImageFromStream(event.data)))
        self.projected_image.SetBitmap(event.data)



class ApplicationProcess(CBasicComponent):
    def __init__(self, notify_window, functionality, partner_ip, projected_image):
        """Init AppProcess class."""
        self.notify_window = notify_window
        CBasicComponent.__init__(self, 'app_process', self.notify_window, self.notify_window)
        
        self.functionality = functionality
        self.projected_image = projected_image
        self.partner_ip = partner_ip
        print partner_ip

        self.partner_res = None # control thread should receive and set this value
        self.control_socket = socket.socket()
        self.control_thread = threading.Thread(target=self.control_thread_func)
        self.control_thread.start()    

        if self.functionality == 'r':
            global EVT_UPDATE_PICTURE_ID
            dispRect = wx.Display() # return rect obejct, using default screen
            temp = dispRect.GetClientArea()[2:] # RECT's fields [:2] not used
            #mods = ( wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_Y)/2 , wx.SystemSettings.GetMetric(wx.SYS_CAPTION_Y) + wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_Y)/2 )
            mods = ( wx.SystemSettings.GetMetric(wx.SYS_BORDER_X) , wx.SystemSettings.GetMetric(wx.SYS_BORDER_Y) + wx.SystemSettings.GetMetric(wx.SYS_CAPTION_Y))
            client_area = ( temp[0] - mods[0], temp[1] - mods[1] )
            print client_area
            
            while self.partner_res == None: # wait for control thread to receive this value, make sure it is set before passing it to components
                time.sleep(0.2)
                print 'waiting for partner_res'

            self.rendererObj = Renderer.CRenderer('renderer', self, self.notify_window, EVT_UPDATE_PICTURE_ID, client_area)
            self.getterObj = Getter.CGetter('getter', self, self.rendererObj, (self.partner_ip,6789))
            #self.hookerObj = Hooker.CHooker('hooker', self, (self.partner_ip,4321), client_area, self.partner_res, mods)  
            self.hookerObj = Hooker.CHooker('hooker', self, (self.partner_ip,4321), client_area, self.partner_res)
            self.componentsArray = [self.rendererObj, self.getterObj, self.hookerObj]
            #self.componentsArray = [self.rendererObj, self.getterObj]
            #self.componentsArray = [self.hookerObj]
            
            self.notify_window.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
            self.notify_window.Bind(wx.EVT_KEY_UP, self.onKeyUp)
            self.projected_image.Bind(wx.EVT_RIGHT_UP, self.onRightMouseUp)
            self.projected_image.Bind(wx.EVT_LEFT_UP, self.onLeftMouseUp)
            self.projected_image.Bind(wx.EVT_RIGHT_DOWN, self.onRightMouseDown)
            self.projected_image.Bind(wx.EVT_LEFT_DOWN, self.onLeftMouseDown)
            self.projected_image.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
            self.projected_image.Bind(wx.EVT_MOTION, self.onMouseMotion)
            
        elif self.functionality == 's':
            self.senderObj = Sender.CSender('sender', self, ('', 6789))
            self.grabberObj = Grabber.CGrabber('grabber', self, self.senderObj)
            #self.clickerObj = Clicker.CClicker('clicker', self, ('',4321))
            #self.clickerObj = Clicker1.CClicker('clicker', self, ('',4321))
            self.clickerObj = Clicker.CClicker('clicker', self, ('',4321))
            self.componentsArray = [self.grabberObj, self.senderObj, self.clickerObj]
            #self.componentsArray = [self.senderObj, self.grabberObj]
            #self.componentsArray = [self.clickerObj]

    def control_thread_func(self):
        global EVT_DISCONNECT
        if self.functionality == 'r':
            self.control_socket.connect((self.partner_ip, 7778))
            while True:
                news = self.control_socket.recv(8)
                if news != None:
                    print 'control thread recv: ' + news
                    if news == 'quit'.zfill(8):
                        #self.control_socket.send('quit')    # for the other side to end this thread
                        try:
                            wx.PostEvent(self.notify_window, MyCustomEvents.PartnerQuitEvent(EVT_PARTNER_QUIT))
                        except:
                            pass    # if this is the side who quit, notify window was terminated and does not exist by now.
                        break
                    # if news is not quit, then it must be sender's screen resolution
                    else:
                        print 'control:     resolution is ' + news
                        #self.hookerObj.send_command(self.compid, 'res.'+news)
                        self.partner_res = (int(news[:4]), int(news[4:]))   # width, height
                        print 'partner_res set'
        
        elif self.functionality == 's':
            self.control_socket.bind(('', 7778))
            self.control_socket.listen(1)
            self.control_socket, addr = self.control_socket.accept()
            print 'accept'

            my_res = wx.GetDisplaySize()  
            send_res = str(my_res[0]).zfill(4)+str(my_res[1]).zfill(4)
            print send_res
            self.control_socket.send(send_res)
            
            while True:
                news = self.control_socket.recv(8)
                if news != None:
                    print 'control thread recv: ' + news
                    if news == 'quit'.zfill(8):
                        #self.control_socket.send('quit')    # for the other side to end this thread
                        try:
                            wx.PostEvent(self.notify_window, MyCustomEvents.PartnerQuitEvent(EVT_PARTNER_QUIT))
                        except:
                            pass    # if this is the side who quit, notify window was terminated and does not exist by now.
                        break
        
        print 'control thread ended'

    def prologue(self):
        #time.sleep(5)
        for i in self.componentsArray:
            i.start()
            time.sleep(0.1)

    def process_data(self, data):
        if data != None:
            # in order to know whom to forward the message
            split = data.split('.')
            op = split[0]   
            details = split[1]
            if op == 'quality':
                self.grabberObj.send_command(self.compid, data)

    def epilogue(self):
        # kill all child components:
        for i in self.componentsArray:
            i.send_command(self.compid, 'exit')
            
        # kill control thread:
        try:
            self.control_socket.send('quit'.zfill(8))
            print 'epilogue:    quit sended to partner, waiting on control thread for reply to shut down'
            self.control_thread.join()  # control thread is still listening for partner to send quit on his epilogue.
            print 'control thread joined app process'
            self.control_socket.close()
            print 'control socket was closed'
        except Exception as e:
            print e.args
        '''
        for i in self.componentsArray:
            i.exit()
        '''
        
    def onKeyUp(self, event):
        print 'on key up'
        device = 'k'
        state = 'u'
        hexcode = str(event.GetKeyCode()).zfill(8)
        data = (device, state, hexcode)
        print data
        self.hookerObj.send_data(data)
        #event.Skip()

    def onKeyDown(self, event):
        print 'on key down'
        device = 'k'
        state = 'd'
        hexcode = str(event.GetKeyCode()).zfill(8)
        data = (device, state, hexcode)
        print data
        self.hookerObj.send_data(data)
        #event.Skip()

    def onRightMouseUp(self, event):
        device = 'm'
        state = 'u'
        key = str(wx.MOUSE_BTN_RIGHT).zfill(8)
        data = (device, state, key)
        print data
        self.hookerObj.send_data(data)
        #event.Skip()

    def onLeftMouseUp(self, event):
        device = 'm'
        state = 'u'
        key = str(wx.MOUSE_BTN_LEFT).zfill(8)
        data = (device, state, key)
        #print data
        self.hookerObj.send_data(data)
        #event.Skip()

    def onRightMouseDown(self, event):
        device = 'm'
        state = 'd'
        key = str(wx.MOUSE_BTN_RIGHT).zfill(8)
        data = (device, state, key)
        print data
        self.hookerObj.send_data(data)
        #event.Skip()

    def onLeftMouseDown(self, event):
        device = 'm'
        state = 'd'
        key = str(wx.MOUSE_BTN_LEFT).zfill(8)
        data = (device, state, key)
        #print data
        self.hookerObj.send_data(data)
        #event.Skip()

    def onMouseMotion(self, event):
        device = 'm'
        state = 'm'
        dc = wx.WindowDC(self.projected_image)
        point = event.GetLogicalPosition(dc)  #i.e. translated according to the translation set for the DC, which usually indicates that the window has been scrolled ????
        x = point.x
        y = point.y
        xy = str(x).zfill(4) + str(y).zfill(4)
        data = (device, state, xy)
        print data
        self.hookerObj.send_data(data)
        #event.Skip()

    def onMouseWheel(self, event):
        device = 'm'
        #if event.MouseWheelAxis() == wxMOUSE_WHEEL_VERTICAL
        if event.GetWheelRotation() < 0:
            state = 'b'
        elif event.GetWheelRotation() > 0:
            state = 'f'
        dxy = str(event.GetWheelDelta()).zfill(8)
        #print dxy
        data = (device, state, dxy)
        print data
        self.hookerObj.send_data(data)
        #event.Skip()


#-------------------------

class MainApp(wx.App):
    def OnInit(self):
        """init MainApp class."""
        self.appgui = ApplicationGUI()
        #self.appgui.Show(True)
        #self.SetTopWindow(self.appgui)
        return True




if __name__ == '__main__':
    app = MainApp(0)
    app.MainLoop()
    print 'bye bye'
    os._exit(0)

