import board, digitalio
import time
from metronome import Metronome

# __CONFIG__
program_tick_speed_ms = 0
button_debounce_time_ms = 200

# __INSTANCES__
metronome = None
test_btn = None

class Button:
  last_on_state = False
  
  def __init__(self, pin, on_press):
    self.input = digitalio.DigitalInOut(pin)
    self.input.direction = digitalio.Direction.INPUT
    self.input.pull = digitalio.Pull.UP
    self.on_press = on_press
    self.last_pressed_time = 0

  def is_pressed(self):
    return not self.input.value

  def check_state(self):
    if self.last_on_state == False and self.is_pressed() == True:
      current_time = time.monotonic()
      if (current_time - self.last_pressed_time) > (button_debounce_time_ms / 1000):
        self.last_on_state = True
        self.last_pressed_time = current_time
        self.on_press()
        
    elif self.last_on_state == True and self.is_pressed() == False:
      self.last_on_state = False

# __PINS__
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# __FUNCTIONS__
def test():
  led.value = True if led.value == False else False
  print('Pressed')

# __EVENTS__
def on_bpm_change(new_bpm):
  print(f'New BPM: {new_bpm}')
  
# __PROGRAM__
led.value = False
metronome = Metronome(board.GP14, on_bpm_change=on_bpm_change)
test_btn = Button(board.GP3, metronome.record_beat)

while True:
  test_btn.check_state()
  metronome.tick()
  time.sleep(program_tick_speed_ms / 1000 if program_tick_speed_ms > 0 else 0)
