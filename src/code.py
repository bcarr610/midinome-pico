import time, digitalio
from metronome import Metronome
from gpio import Button
from configuration import modes, UserConfig, app_config
from utils import TimeTracker
from event_handler import EventHandler
from helix import Helix
class Midinome:
  def __init__(self, mode=modes['live']):
    midinome_initialization_tracker = TimeTracker('Midinome Initialization')
    self.user_config = UserConfig()

    # State
    self.mode = mode
    self.current_button_combo = []

    # Event Handler
    self.event_handler = EventHandler(self)

    # Initialize Metronome
    self.metronome = Metronome(
      app_config['gpio']['audio_out'],
      on_beat=self.on_beat,
      on_bpm_change=self.on_bpm_change
    )

    # Initialize Helix
    self.helix = Helix(self)

    # Initialize GPIO
    led = digitalio.DigitalInOut(app_config['gpio']['board_led'])
    led.direction = digitalio.Direction.OUTPUT
    metronome_button = Button(
      app_config['gpio']['metronome_button'],
      self.user_config.config['BTN Debounce'],
      on_press=self.event_handler.on_metronome_button
    )
    trigger_button = Button(
      app_config['gpio']['trigger_button'],
      self.user_config.config['BTN Debounce'],
      on_press=self.event_handler.on_trigger_button
    )
    command_button = Button(
      app_config['gpio']['command_button'],
      self.user_config.config['BTN Debounce'],
      on_press=self.event_handler.on_command_button
    )
    plus_minus_button = Button(
      app_config['gpio']['plus_minus_button'],
      self.user_config.config['BTN Debounce'],
      on_press=self.event_handler.on_plus_minus_button
    )
    test_button = Button(
      app_config['gpio']['test_button'],
      self.user_config.config['BTN Debounce'],
      on_press=self.event_handler.on_test_button,
    )

    self.gpio_input = {
      'metronome_button': metronome_button,
      'trigger_button': trigger_button,
      'command_button': command_button,
      'plus_minus_button': plus_minus_button,
      'test_button': test_button
    }

    midinome_initialization_tracker.stop()

  def on_beat(self, beat_at, is_downbeat):
    self.helix.on_beat(beat_at, is_downbeat)
    self.event_handler.on_beat(beat_at, is_downbeat)
    pass

  def on_bpm_change(self, value):
    print(f'BPM Changed to {value}')
    pass

  def run_event_loop_iteration(self):
    self.gpio_input['metronome_button'].check_state()
    self.gpio_input['trigger_button'].check_state()
    self.gpio_input['command_button'].check_state()
    self.gpio_input['plus_minus_button'].check_state()
    self.gpio_input['test_button'].check_state()
    self.metronome.tick()
    self.helix.tick()
  
midinome = Midinome()
midinome.metronome.__start_metronome(60)
print('Program Running')

while True:
  midinome.run_event_loop_iteration()
  if app_config['program_tick_speed'] > 0:
    time.sleep(app_config['program_tick_speed'])
