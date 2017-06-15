# MicroPython SH1106 OLED driver, I2C and SPI interfaces
# Sample code sections
# ------------ SPI ------------------
# Pin Map SPI
#   - 3v - xxxxxx   - Vcc
#   - G  - xxxxxx   - Gnd
#   - D7 - GPIO 13  - Din / MOSI fixed
#   - D5 - GPIO 14  - Clk / Sck fixed
#   - D8 - GPIO 4   - CS (optional, if the only connected device)
#   - D2 - GPIO 5   - D/C
#   - D1 - GPIO 2   - Res
# 
# for CS, D/C and Res other ports may be chosen.
# 
# from machine import Pin, SPI
# import sh1106

# spi = SPI(1, baudrate=1000000)
# display = sh1106.SH1106_SPI(128, 64, spi, Pin(5), Pin(2), Pin(4))
# display.sleep(False)
# display.fill(0)
# display.text('Testing 1', 0, 0, 1)
# display.show()
#
# --------------- I2C ------------------
# 
# Pin Map I2C
#   - 3v - xxxxxx   - Vcc
#   - G  - xxxxxx   - Gnd
#   - D2 - GPIO 5   - SCK / SCL
#   - D1 - GPIO 4   - DIN / SDA
#   - D0 - GPIO 16  - Res
#   - G  - xxxxxx     CS
#   - G  - xxxxxx     D/C
#
# Pin's for I2C can be set almost arbitrary
# 
# from machine import Pin, I2C
# import sh1106
#
# i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
# display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)
# display.sleep(False)
# display.fill(0)
# display.text('Testing 1', 0, 0, 1)
# display.vpage()

from micropython import const
import time
import framebuf

# a few register definitions
SET_CONTRAST        = const(0x81)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
LOW_COLUMN_ADDRESS  = const(0x00)
HIGH_COLUMN_ADDRESS = const(0x10)
SET_PAGE_ADDRESS    = const(0xB0)
SET_START_LINE      = const(0x40)

class SH1106:
  def __init__(self, width, height, external_vcc):
    self.width = width
    self.height = height
    self.external_vcc = external_vcc
    self.pages = self.height // 8
    self.buffer = bytearray(self.pages * self.width)
    self.framebuf = framebuf.FrameBuffer1(self.buffer, self.width, self.height)
    self.init_display()

  def init_display(self):
    self.reset()
    self.fill(0)
    self.poweron()
    self.show()

  def poweroff(self):
    self.write_cmd(SET_DISP | 0x00)

  def poweron(self):
    self.write_cmd(SET_DISP | 0x01)

  def sleep(self, value):
    self.write_cmd(SET_DISP | (not value))

  def contrast(self, contrast):
    self.write_cmd(SET_CONTRAST)
    self.write_cmd(contrast)

  def invert(self, invert):
    self.write_cmd(SET_NORM_INV | (invert & 1))

  def show(self):
    for page in range(self.height // 8):
      self.write_cmd(SET_PAGE_ADDRESS | page)
      self.write_cmd(LOW_COLUMN_ADDRESS | 2)
      self.write_cmd(HIGH_COLUMN_ADDRESS | 0)
      self.write_data(self.buffer[
        self.width * page:self.width * page + self.width
      ])

  def fill(self, val):
    self.framebuf.fill(val)

  def fill_rect(self, x, y, width, height, val):
    self.framebuf.fill_rect(x, y, width, height, val)

  def line(self, x1, y1, x2, y2, val):
    self.framebuf.line(x1, y1, x2, y2, val)

  def pixel(self, x, y, col):
    self.framebuf.pixel(x, y, col)

  def clear(self):
    self.fill(0)
    self.show()

  def scroll(self, dx, dy):
    self.framebuf.scroll(dx, dy)

  def vpage(self,delay=10):
    show = False
    self.write_cmd(SET_START_LINE | 0)
    for x in range(self.height-1):
      self.write_cmd(SET_START_LINE | x)
      if not show:
        self.show()
        show = True
      time.sleep_ms(delay)
    self.fill(0)

  def text(self, string, x, y, col=1):
    self.framebuf.text(string, x, y, col)

  def reset(self, res):
    res.value(1)
    time.sleep_ms(1)
    res.value(0)
    time.sleep_ms(20)
    res.value(1)
    time.sleep_ms(20)

class SH1106_I2C(SH1106):
  def __init__(self, width, height, i2c, res=None, addr=0x3c, external_vcc=False):
    self.i2c = i2c
    self.addr = addr
    self.res = res
    self.temp = bytearray(2)
    if hasattr(self.i2c, "start"):
      self.write_data = self.sw_write_data
    else:
      self.write_data = self.hw_write_data  
    if res is not None:
      res.init(res.OUT, value=1)
    super().__init__(width, height, external_vcc)

  def write_cmd(self, cmd):
    self.temp[0] = 0x80 # Co=1, D/C#=0
    self.temp[1] = cmd
    self.i2c.writeto(self.addr, self.temp)

  def hw_write_data(self, buf):
    self.i2c.writeto(self.addr, b'\x40'+buf)

  def sw_write_data(self, buf):
    self.temp[0] = self.addr << 1
    self.temp[1] = 0x40 # Co=0, D/C#=1
    self.i2c.start()
    self.i2c.write(self.temp)
    self.i2c.write(buf)
    self.i2c.stop()
  
  def reset(self):
    super().reset(self.res)

class SH1106_SPI(SH1106):
  def __init__(self, width, height, spi, dc, res, cs):
    self.rate = 10 * 1000 * 1000
    dc.init(dc.OUT, value=0)
    res.init(res.OUT, value=0)
    if cs is not None:
      cs.init(cs.OUT, value=1)
    self.spi = spi
    self.dc = dc
    self.res = res
    self.cs = cs
    super().__init__(width, height, external_vcc)

  def write_cmd(self, cmd):
    self.spi.init(baudrate=self.rate, polarity=0, phase=0)
    if self.cs is not None:
      self.cs.value(1)
      self.dc.value(0)
      self.cs.value(0)
      self.spi.write(bytearray([cmd]))
      self.cs.value(1)
    else:
      self.dc.value(0)
      self.spi.write(bytearray([cmd]))

  def write_data(self, buf):
    self.spi.init(baudrate=self.rate, polarity=0, phase=0)
    if self.cs is not None:
      self.cs.value(1)
      self.dc.value(1)
      self.cs.value(0)
      self.spi.write(buf)
      self.cs.value(1)
    else:
      self.dc.value(1)
      self.spi.write(buf)
      
  def reset(self):
    super().reset(self.res)


"""

"""

"""
# Hardware Scroll
SET_HWSCROLL_OFF    = const(0x2e)
SET_HWSCROLL_ON     = const(0x2f)
SET_HWSCROLL_RIGHT  = const(0x26)
SET_HWSCROLL_LEFT   = const(0x27)
#SET_HWSCROLL_VR     = const(0x29)
#SET_HWSCROLL_VL     = const(0x2a)
"""

"""
def right(self,start=0,stop=7):
  self.write_cmd(SET_HWSCROLL_RIGHT)
  self.write_cmd(0X00)
  self.write_cmd(start)
  self.write_cmd(0X00)
  self.write_cmd(stop)
  
  self.write_cmd(0X00)
  self.write_cmd(0XFF)
  self.write_cmd(SET_HWSCROLL_ON);

def hw_scroll_h(self, direction=True):   # default to scroll right
  self.write_cmd(SET_HWSCROLL_OFF)  # turn off hardware scroll per SSD1306 datasheet
  if not direction:
    self.write_cmd(SET_HWSCROLL_LEFT)
    self.write_cmd(0x00) # dummy byte
    self.write_cmd(0x07) # start page = page 7
    self.write_cmd(0x00) # frequency = 5 frames
    self.write_cmd(0x00) # end page = page 0
  else:
    self.write_cmd(SET_HWSCROLL_RIGHT)
    self.write_cmd(0x00) # dummy byte
    self.write_cmd(0x00) # start page = page 0
    self.write_cmd(0x00) # frequency = 5 frames
    self.write_cmd(0x07) # end page = page 7
      
  self.write_cmd(0x00)
  self.write_cmd(0xff)
  self.write_cmd(SET_HWSCROLL_ON) # activate scroll
"""