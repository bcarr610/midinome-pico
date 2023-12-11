import board, json
from utils import path_exists

# __CONSTANTS__
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

trigger_on = {
  'Instant': 'Instant',
  'Beat': 'Beat',
  'Downbeat': 'Downbeat',
  'Phrase': 'Phrase'
}

# __CONFIGURATION__
app_config = {
  'program_tick_speed': 0,
  'audio_dir': 'audio',
  'downbeat_file_path': 'audio/downbeat.wav',
  'offbeat_file_path': 'audio/offbeat.wav',
  'user_config_path': 'user_config.env',
  'helix': {
    'uart': {
      'tx': board.GP0,
      'rx': board.GP1
    },
    'midi_signals': {
      'record': (60, 80),
      'overdub': (60, 40),
      'play': (61, 80),
      'stop': (61, 40),
      'play_once': (62, 80),
      'looper_block_on': (67, 80),
      'looper_block_off': (67, 40),
      'tap_tempo': (64, 80)
    }
  },
  'gpio': {
    'board_led': board.LED,
    'audio_out': board.GP14,
    'metronome_button': board.GP2,
    'trigger_button': board.GP3,
    'command_button': board.GP4,
    'plus_minus_button': board.GP5,
    'test_button': board.GP6,
  }
}

class UserConfig: 
  config = {}
  default_config = {
    'CMD Mode Timeout': 0.5,
    'BTN Debounce': 0.2,
    'TRG RCD Start On': trigger_on['Beat'],
    'TRG RCD Stop On': trigger_on['Beat'],
    'TRG Play On': trigger_on['Beat'],
    'TRG Stop On': trigger_on['Beat'],
    'Loop After RCD': True,
    'Time Signature': (4, 4),
    'Helix LAT Offset MS': 0
  }
  
  def __init__(self):
    if not path_exists(app_config['user_config_path']):
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

