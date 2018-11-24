from BasicComponent import CBasicComponent
from PIL import ImageGrab, Image
import time
from io import BytesIO
import Queue


class CGrabber(CBasicComponent):
    def __init__(self, compid, C_component_out, D_component_out):
        CBasicComponent.__init__(self, compid, C_component_out, D_component_out)
  
    def prologue(self):
        self.quality = 60 # default 60 in gui

    def process_data2(self, data):
        try:
            im = ImageGrab.grab()
            image_data = self.CompressTojpeg(im)
            self.D_component_out.send_data(image_data, True)
            print 'grabber put 1 picture'
        except Exception as e:
            print self.compid + str(e.args)
        return 'continue'



    def process_data(self, data):
        im = ImageGrab.grab()
        image_data = self.CompressTojpeg(im)
        try:
            self.D_component_out.send_data(image_data)
            print 'grabber put 1 picture'
        except Exception as e:
            print self.compid + str(e.args)
            #time.sleep(0.03)
        return 'continue'
    
    #override because grabber has to reffer to a command that is not basic known - quality
    def process_command(self, tup):
        result = CBasicComponent.process_command(self, tup)
        if result == 'unknown':
            compid, command = tup
            if command[:7] == 'quality':  # from app gui to grabber:
                self.quality = int(command.split('.')[1])
                return 'continue'
        else:
            return result

    def epilogue(self):
        print 'epilogue:' + self.compid + ' is off...'

    def CompressTojpeg(self, image):
        '''
        gets image object, compresses to jpeg and returns bytesIO buffer with the image
        '''
        file = BytesIO()
        image.save(file, 'jpeg', quality = self.quality)
        file.name = 'test.jpg'
        file.seek(0)
        return file
        

class CFileSaver(CBasicComponent):
    def prologue(self):
        self.i = 0
    def process_data(self, data):
        if data != None:
            self.i += 1
            image = Image.open(data)
            image.save('C:\\Users\\lenovo\\Desktop\\12-5-2018 gibui- success - Copy_try\\saved_pics\\dima'+str(self.i)+'.jpg', 'JPEG')
            data.seek(0)
    def epilogue(self):
        print self.i


# ends
#--------------------------------------------------------
