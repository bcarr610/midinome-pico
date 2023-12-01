import digitalio
import config
import time
from utils import noop

class Button:
  last_on_state = False
  
  def __init__(self, pin, on_press=noop, on_double=noop, on_hold=noop):
    self.input = digitalio.DigitalInOut(pin)
    self.input.direction = digitalio.Direction.INPUT
    self.input.pull = digitalio.Pull.UP
    self.on_press = on_press
    self.on_double = on_double
    self.on_hold = on_hold
    self.last_pressed_time = 0

  def is_pressed(self):
    return not self.input.value

  def check_state(self):
    if self.last_on_state == False and self.is_pressed() == True:
      current_time = time.monotonic()
      if (current_time - self.last_pressed_time) > (config.button_debounce_time_ms / 1000):
        self.last_on_state = True
        self.last_pressed_time = current_time
        self.on_press()
        
    elif self.last_on_state == True and self.is_pressed() == False:
      self.last_on_state = False
