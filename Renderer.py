import wx
from BasicComponent import CBasicComponent
import MyCustomEvents


class CRenderer(CBasicComponent):
    def __init__(self, compid, C_component_out, notify_window, eventid, screen_resolution):
        CBasicComponent.__init__(self, compid, C_component_out)
        self.update_event_id = eventid
        self.notify_window = notify_window
        self.screen_width, self.screen_height = screen_resolution[0], screen_resolution[1]

    def prologue(self):
        print 'in prologue'
        '''
        self.screen_width = self.res[0]
        self.screen_height = self.res[1]
        '''

    def process_data(self, data):
        if data != None:
            image = wx.ImageFromStream(data)
            scaled_image = image.Scale(self.screen_width, self.screen_height)
            for_set = wx.BitmapFromImage(scaled_image)
            print 'image of len: ' + str(len(data.getvalue())) + '  rendered'
            try:    # could raise an exception if window was closed but conponent will receive 'exit' command only after this function ends
                wx.PostEvent(self.notify_window, MyCustomEvents.UpdateEvent(self.update_event_id, for_set))
            except Exception as e:
                print self.compid + str(e.args)
        return 'continue'

    def epilogue(self):
        print 'epilogue:' + self.compid + ' is off...'


# ends
#--------------------------------------------------------