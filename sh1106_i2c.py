## framebuffer inheritance, compatible with writer.py
# converted from sh1106_i2c.py

import framebuf

class SH1106(framebuf.FrameBuffer):

  _byte = bytearray(1)
  _word = bytearray(2)
    
  def __init__(self,width, height, i2c, address=0x3c ):
    self._address = address
    self.width = width
    self.height = height
    self._i2c = i2c

    buffer = bytearray(1024)
    self._buffer = memoryview(buffer)
    super().__init__(self._buffer,self.width,self.height,False)
    self.init_display()

  def init_display(self):
    self._command = bytearray(b'\xb0\x02\x10')
    if self.width > 128: self._command[1] = 0x00
    self._i2c.writeto_mem(self._address, 0x00, b'\xae\xd5\x80\xa8\x3f\xd3'
                          b'\x00\x40\x80\x14\x20\x00\xc0\xa0\xda\x12'
                          b'\x81\xcf\xd9\xf1\xdb\x40\xa4\xa6\xaf')    

  def active(self, val):
    self._i2c.writeto_mem(self._address, 0x00, b'\xaf' if val else b'\xae')

  def inverse(self, val):
    self._i2c.writeto_mem(self._address, 0x00, b'\xa7' if val else b'\xa6')

  def vscroll(self, dy):
    self._byte[0] = 0x40 | dy & 0x3f
    self._i2c.writeto_mem(self._address, 0x00, self._byte)

  def flip(self, val):
    self._i2c.writeto_mem(self._address, 0x00, b'\xc0' if val else b'\xc8')

  def mirror(self, val):
    self._i2c.writeto_mem(self._address, 0x00, b'\xa0' if val else b'\xa1')

  def contrast(self, val):
    self._word[0] = 0x81
    self._word[1] = val & 0xff
    self._i2c.writeto_mem(self._address, 0x00, self._word)

  def show(self):
    index = 0
    for page in range(self.height // 8):
      self._command[0] = 0xb0 | page
      self._i2c.writeto_mem(self._address, 0x00, self._command)
      self._i2c.writeto_mem(self._address, 0x40, self._buffer[index:index + self.width])
      index += self.width

'''
import gpio, sh1106_i2c as sh
ssd = sh.SH1106(128,64,gpio.i2c)
from writer import Writer
from fonts import freesans20 as fs20
from fonts import fapac24 as fa24
from fonts import font10 as f10
fm = Writer(ssd, f10, verbose=False)
fm.printstring('XXX')
ssd.show()
'''