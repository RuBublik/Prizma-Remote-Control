import wx

class UpdateEvent(wx.PyEvent):
    """Object for update_picture event"""
    def __init__(self, EVT_UPDATE_PICTURE_ID, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_UPDATE_PICTURE_ID)
        self.data = data

class PartnerQuitEvent(wx.PyEvent):
    """Object for disconnect event"""
    def __init__(self, EVT_PARTNER_QUIT):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PARTNER_QUIT)