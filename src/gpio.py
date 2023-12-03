import digitalio, time
from utils import noop

class Button:
  def __init__(self, pin, btn_debounce, on_press=noop):
    self.last_on_state = False
    self.last_on_state_time = 0
    self.last_event_time = 0
    self.input = digitalio.DigitalInOut(pin)
    self.input.direction = digitalio.Direction.INPUT
    self.input.pull = digitalio.Pull.UP
    self.on_press = on_press
    self.btn_debounce = btn_debounce

  def is_pressed(self):
    return not self.input.value

  def check_state(self):
    if self.last_on_state == False and self.is_pressed() == True:
      now = time.monotonic()
      if now - self.last_event_time > self.btn_debounce:
        self.last_on_state = True
        self.last_event_time = now
        self.on_press()
        
    elif self.last_on_state == True and self.is_pressed() == False:
      self.last_on_state = False
