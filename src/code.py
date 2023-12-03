from audiocore import WaveFile
from audiopwmio import PWMAudioOut as AudioOut
import board
import json
import os
import time
import digitalio

# __VARS_AND_DEFINITIONS__
buttons = {
  'metronome': 'metronome',
  'trigger': 'trigger',
  'command': 'command',
  'plus_minus': 'plus_minus'
}

modes = {
  'live': 'live',
  'command': 'command',
  'config': 'config',
  'time_signature': 'time_signature',
  'manual_bpm': 'manual_bpm'
}

# __CONFIGURATION__
app_config = {
  'program_tick_speed': 0,
  'audio_dir': 'audio',
  'downbeat_file_path': 'audio/downbeat.wav',
  'offbeat_file_path': 'audio/offbeat.wav',
  'user_config_path': 'user.config.json',
  'gpio': {
    'board_led': board.LED,
    'audio_out': board.GP14,
    'metronome_button': board.GP1,
    'trigger_button': board.GP2,
    'command_button': board.GP3,
    'plus_minus_button': board.GP4
  }
}

# __UTILITY_FUNCTIONS__
def noop():
  pass

# __CLASSES__
class UserConfig: 
  config = {}
  default_config = {
    'CMD Mode Timeout': 0.5,
    'BTN Debounce': 0.2,
    'TRG RCD Default': 'Beat',
    'TRG P/S Default': 'Beat',
    'Time SIG Default': (4, 4)
  }
  
  def __init__(self):
    print('Initializing User Config')
    if not os.path.exists(app_config['user_config_path']):
      self.config = self.create_new_config()
    else:
      should_write_new_file = False
      delete_keys = []
      self.config = self.read_config()

      # Delete Existing Keys
      for key in self.config:
        if key not in self.default_config:
          if not should_write_new_file:
            should_write_new_file = True
          delete_keys.append(key)

      for key in delete_keys:
        del self.config[key]

      # Create New Keys
      for key in self.default_config:
        if key not in self.config:
          if not should_write_new_file:
            should_write_new_file = True
          self.config[key] = self.default_config[key]

      if should_write_new_file:
        self.write_config()

  def update(self, key, value):
    self.config[key] = value
    self.write_config()

  def reset_default(self, key):
    self.config[key] = self.default_config[key]
    self.write_config()

  def create_new_config(self):
    with open(app_config['user_config_path'], 'w') as file:
      json.dump(self.default_config, file)
      return self.default_config
    
  def write_config(self):
    with open(app_config['user_config_path'], 'w') as file:
      json.dump(self.config, file)
      return self.config

  def read_config(self):
    with open(app_config['user_config_path'], 'r') as file:
      return json.load(file)

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

class Metronome:
  downbeat_sound = app_config['downbeat_file_path']
  offbeat_sound = app_config['downbeat_file_path']
  bpm = 0
  # CONVERT SOME OF THESE INTO USER/APPCONFIG
  detect_bpm_from_last = 4
  stop_recording_after = 2
  last_x_recording_timestamps = []
  time_signature = [4, 4]
  current_beat = 1
  ready_to_emit = False
  is_on = None
  should_emit_events = None
  should_emit_sound = None
  audio = None

  # State
  last_beat_at = 0

  def __init__(self, audio_pin, on_downbeat = noop, on_offbeat = noop, on_beat = noop, on_bpm_change = noop):
    self.on_downbeat = on_downbeat
    self.on_offbeat = on_offbeat
    self.on_beat = on_beat
    self.on_bpm_change = on_bpm_change
    self.audio = AudioOut(audio_pin)

  def start(self):
    self.is_on = True

  def stop(self):
    self.is_on = False

  def start_emitting_events(self):
    self.should_emit_events = True
  
  def stop_emitting_events(self):
    self.should_emit_events = False

  def start_emitting_sound(self):
    self.should_emit_sound = True

  def stop_emitting_sound(self):
    self.should_emit_sound = False

  def change_time_signature(self, beats_per_measure, beat_value):
    self.time_signature = [beats_per_measure, beat_value]
    if self.current_beat > beats_per_measure:
      self.current_beat = 1

  def play_sound(self, filename):
    with open(filename, "rb") as wave_file:
      wave = WaveFile(wave_file)
      self.audio.play(wave)
      while self.audio.playing:
        pass

  def tick(self):
    # Manage Beat State
    if self.bpm > 0 and self.is_on:
      now = time.monotonic()
      if now - self.last_beat_at >= (60 / self.bpm):
        self.last_beat_at = now
        self.current_beat = self.current_beat + 1 if self.current_beat < self.time_signature[0] else 1
        if self.ready_to_emit == False:
          self.ready_to_emit = True

    # Stop Recording BPM
    if len(self.last_x_recording_timestamps):
      if (time.monotonic() - self.last_x_recording_timestamps[-1] > self.stop_recording_after):
        print("Recording Stopped")
        self.last_x_recording_timestamps = []

    # Emit Sound and events
    if self.ready_to_emit:
      self.ready_to_emit = False
      print('Beat')
      
      # Emit Sound
      if self.should_emit_sound:
        print('Emitting Sound')
        sound = self.downbeat_sound if self.current_beat == self.time_signature[0] else self.offbeat_sound
        self.play_sound(sound)  

      # Emit Events
      if self.should_emit_events:
        print('Emitting Event')
        self.on_beat()
        if self.current_beat == self.time_signature[0]:
          self.on_downbeat()
        else:
          self.on_offbeat()

  def record_beat(self):
    print('Received')
    if len(self.last_x_recording_timestamps) + 1 < self.detect_bpm_from_last:
      # Record beat
      self.last_x_recording_timestamps.append(time.monotonic())
      print(len(self.last_x_recording_timestamps))
      print(self.detect_bpm_from_last)
    else:
      # Set BPM
      differences = [self.last_x_recording_timestamps[i + 1] - self.last_x_recording_timestamps[i] for i in range(len(self.last_x_recording_timestamps) - 1)]
      average_diff = sum(differences) / len(differences) if differences else 0
      self.bpm = round(60 / average_diff) if average_diff != 0 else 0
      self.last_x_recording_timestamps = []
      self.trigger_bpm_change(self.bpm)

      # Start Emitting if first time recording
      if self.is_on == None:
        self.is_on = True

      if self.should_emit_sound == None:
        self.should_emit_sound = True

  def trigger_bpm_change(self, value):
    self.on_bpm_change(value)

class Midinome:
  current_button_combo = []
  
  def __init__(self):
    self.mode = modes['live']
    self.user_config = UserConfig()
    self.metronome = Metronome(
      app_config['gpio']['audio_out'],
      on_bpm_change=self.on_bpm_change,
      on_beat=self.on_beat,
      on_downbeat=self.on_downbeat,
      on_offbeat=self.on_offbeat,
    )
    self.respawn_gpio()
    self.current_button_combo = []

  def respawn_gpio(self):
    led = digitalio.DigitalInOut(app_config['gpio']['board_led'])
    led.direction = digitalio.Direction.OUTPUT
    metronome_button = Button(app_config['gpio']['metronome_button'], self.user_config.config['BTN Debounce'], on_press=self.on_metronome_button)
    trigger_button = Button(app_config['gpio']['trigger_button'], self.user_config.config['BTN Debounce'], on_press=self.on_trigger_button)
    command_button = Button(app_config['gpio']['command_button'], self.user_config.config['BTN Debounce'], on_press=self.on_command_button)
    plus_minus_button = Button(app_config['gpio']['plus_minus_button'], self.user_config.config['BTN Debounce'], on_press=self.on_plus_minus_button)

    self.gpio = {
      'led': led,
      'metronome_button': metronome_button,
      'trigger_button': trigger_button,
      'command_button': command_button,
      'plus_minus_button': plus_minus_button,
    }

  def run_event_loop_iteration(self):
    self.gpio['metronome_button'].check_state()
    self.gpio['trigger_button'].check_state()
    self.gpio['command_button'].check_state()
    self.gpio['plus_minus_button'].check_state()
    self.gpio['metronome'].tick()

  # MIDINOME FUNCTIONS
  def ToggleMetronomeAudio(self):
    if (self.metronome.should_emit_sound):
      self.metronome.stop_emitting_sound()
      # Change lights and LCD Display
    else:
      self.metronome.start_emitting_sound()
      # Change Lights and LCD Display

  def RecordMetronomeBeat(self):
    self.metronome.record_beat()

  def ConfirmTimeSignature(self):
    pass

  def ConfirmNewBPM(self):
    pass

  def ToggleSelectedTimeSignatureEditPart(self):
    pass

  def CancelEditBPM(self):
    pass

  # INPUT EVENT LOGIC
  def on_metronome_button(self):
    if self.mode == modes['live']:
      if self.metronome.is_on:
        self.ToggleMetronomeAudio()
      else:
        self.RecordMetronomeBeat()
    elif self.mode == modes['command']:
      self.current_button_combo.append(buttons['metronome'])
    elif self.mode == modes['config']:
      # If Currently Editing Config Item
        # Confirm Config Item Changes
      # Else
        # Start Editing Config Item
        pass
    elif self.mode == modes['time_signature']:
      self.ConfirmTimeSignature()
    elif self.mode == modes['manual_bpm']:
      self.ConfirmNewBPM()

  def on_trigger_button(self):
    if self.mode == modes['live']:
      # If no trigger loop
        # If not recording loop
          # Record Start on next x
        # Else
          # Record Stop on next x
      # Else
        # If not playing loop
          # Start on next x
        # Else
          # Stop on next x
      pass
    elif self.mode == modes['command']:
      self.current_button_combo.append(buttons['trigger'])
      pass
    elif self.mode == modes['config']:
      # If Currently Editing Config Item
        # Cancel
      # Else
        # Back to Live Mode
      pass
    elif self.mode == modes['time_signature']:
      self.ToggleSelectedTimeSignatureEditPart()
      pass
    elif self.mode == modes['manual_bpm']:
      self.CancelEditBPM()
      pass

  def on_command_button(self):
    if self.mode == modes['live']:
      # Enter Command Mode
      pass
    elif self.mode == modes['command']:
      # Cancel Command
      pass
    elif self.mode == modes['config']:
      # If Editing Config Item
        # Increment Config Item Value
      # Else
        # Highlight Next Config Item
      pass
    elif self.mode == modes['time_signature']:
      # Increment Edit Time Signature Value
      pass
    elif self.mode == modes['manual_bpm']:
      # Increment Manual BPM Value
      pass

  def on_plus_minus_button(self):
    if self.mode == modes['live']:
      # Go to config mode
      pass
    elif self.mode == modes['command']:
      self.current_button_combo.append(buttons['plus_minus'])
      pass
    elif self.mode == modes['config']:
      # If Editing Config Item
        # Decrement Config Item Value
      # Else
        # Highlight Previous Config Item
      pass
    elif self.mode == modes['time_signature']:
      # Decrement Edit Time Signature Value
      pass
    elif self.mode == modes['manual_bpm']:
      # Decrement Manual BPM Value
      pass

  # STATE CHANGE EVENTS
  def on_beat(self):
    print('Beat')
    self.gpio['led'].value = True
    time.sleep(2)
    # Does this stop event loop?????
    self.gpio['led'].value = False

  def on_downbeat(self):
    pass

  def on_offbeat(self):
    pass

  def on_bpm_change(self, new_bpm):
    print(f'New BPM: {new_bpm}')
  
    
# mode = 'live'
# user_config = UserConfig()

# # __PINS__
# led = digitalio.DigitalInOut(app_config['gpio']['board_led'])
# led.direction = digitalio.Direction.OUTPUT

# __EVENTS__
# def on_metronome_button():
#   # Check if no metronome running, and correct mode, etc.
#   metronome.record_beat()
#   pass

# def on_trigger_button():
#   pass

# def on_command_button():
#   pass

# def on_plus_minus_button():
#   pass

# def on_beat():
#   print('Beat')
#   led.value = True
#   time.sleep(2)
#   led.value = False

# def on_downbeat():
#   pass

# def on_offbeat():
#   pass

# def on_bpm_change(new_bpm):
#   print(f'New BPM: {new_bpm}')
  
# # __PROGRAM__
# metronome = Metronome(
#   app_config['gpio']['audio_out'],
#   on_bpm_change=on_bpm_change,
#   on_beat=on_beat,
#   on_downbeat=on_downbeat,
#   on_offbeat=on_offbeat,
# )

# Buttons
# metronome_button = Button(app_config['gpio']['metronome_button'], user_config.config['BTN Debounce'], on_press=on_metronome_button)
# trigger_button = Button(app_config['gpio']['trigger_button'], user_config.config['BTN Debounce'], on_press=on_trigger_button)
# command_button = Button(app_config['gpio']['command_button'], user_config.config['BTN Debounce'], on_press=on_command_button)
# plus_minus_button = Button(app_config['gpio']['plus_minus_button'], user_config.config['BTN Debounce'], on_press=on_plus_minus_button)

midinome = Midinome()
while True:
  # metronome_button.check_state()
  # trigger_button.check_state()
  # command_button.check_state()
  # plus_minus_button.check_state()
  # metronome.tick()
  midinome.run_event_loop_iteration()
  time.sleep(app_config['program_tick_speed_ms'] / 1000 if app_config['program_tick_speed_ms'] > 0 else 0)
