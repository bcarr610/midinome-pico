import board, digitalio
import time
from metronome import Metronome
from gpio import Button
import config
from _types import ProgramMode

# __STATE__
mode: ProgramMode = 'live'

# __PINS__
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# __FUNCTIONS__
def test1():
  print('Pressed 1')

def test2():
  print('Pressed 2')

# __EVENTS__
def on_bpm_change(new_bpm):
  print(f'New BPM: {new_bpm}')

def on_beat():
  led.value = True
  time.sleep(0.2)
  led.value = False
  
# __PROGRAM__
metronome = Metronome(
  board.GP14,
  on_bpm_change=on_bpm_change,
  on_beat=on_beat
)

button_1 = Button(board.GP1, on_press=metronome.record_beat)
button_2 = Button(board.GP2, on_press=test1)
button_3 = Button(board.GP3, on_press=test2)

while True:
  button_1.check_state()
  button_2.check_state()
  button_3.check_state()
  metronome.tick()
  time.sleep(config.program_tick_speed_ms / 1000 if config.program_tick_speed_ms > 0 else 0)
