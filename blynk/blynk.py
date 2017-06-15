import blynklib
import time

import blynkhash as hash
blynk = blynklib.Blynk(hash.key,ssl=False)

def v0_read_handler():
  # we must call virtual write in order to send the value to the widget
  blynk.virtual_write(0, time.ticks_ms() // 1000)
  print('v0')

# register the virtual pin
blynk.add_virtual_pin(0, read=v0_read_handler)

# define a virtual pin write handler
def v1_write_handler(value):
  print(value)

# register the virtual pin
blynk.add_virtual_pin(1, write=v1_write_handler)

IDX = 0
def V2R():
  global IDX
  blynk.virtual_write(2, IDX)
  IDX+=64
  if IDX > 1024: IDX = 0  

blynk.add_virtual_pin(2, read=V2R)

# register the task running every 3 sec (period must be a multiple of 50 ms)
def my_user_task():
  # do any non-blocking operations
  print('@@ Action')

blynk.set_user_task(my_user_task, 3000)

def oncon():
  print('Yes I am connected.')
  
blynk._on_connect = oncon

# start Blynk (this call should never return)
blynk.run()
