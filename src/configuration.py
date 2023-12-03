import board, os, json

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

