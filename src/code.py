import time
import digitalio
from metronome import Metronome
from gpio import Button
from configuration import modes, UserConfig, app_config
from utils import TimeTracker
from event_handler import EventHandler

class Midinome:
  def __init__(self, mode=modes['live']):
    midinome_initialization_tracker = TimeTracker('Midinome Initialization')
    self.user_config = UserConfig()
    self.mode = mode
    self.current_button_combo = []
    self.event_handler = EventHandler(self)

    # Initialize Metronome
    self.metronome = Metronome(app_config['gpio']['audio_out'])
    self.metronome.on_beat = self.event_handler.on_beat
    self.metronome.on_bpm_change = self.event_handler.on_bpm_change
    self.metronome.on_downbeat = self.event_handler.on_downbeat
    self.metronome.on_offbeat = self.event_handler.on_offbeat

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

    self.gpio = {
      'led': led,
      'metronome_button': metronome_button,
      'trigger_button': trigger_button,
      'command_button': command_button,
      'plus_minus_button': plus_minus_button,
    }

    midinome_initialization_tracker.stop()

  def run_event_loop_iteration(self):
    self.gpio['metronome_button'].check_state()
    self.gpio['trigger_button'].check_state()
    self.gpio['command_button'].check_state()
    self.gpio['plus_minus_button'].check_state()
    self.gpio['metronome'].tick()
  
midinome = Midinome()

while True:
  event_loop_iteration_tracker = TimeTracker('Event Loop Iteration')
  midinome.run_event_loop_iteration()
  event_loop_iteration_tracker.stop()
  time.sleep(app_config['program_tick_speed_ms'] / 1000 if app_config['program_tick_speed_ms'] > 0 else 0)
