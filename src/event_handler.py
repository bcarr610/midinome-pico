import time
from configuration import modes, buttons, trigger_on

HelixEvent = {
  'rcd_start_instant': 'rcd_start_instant',
  'rcd_stop_instant': 'rcd_stop_instant',
  'rcd_start_next_beat': 'rcd_start_next_beat',
  'rcd_stop_next_beat': 'rcd_stop_next_beat',
  'rcd_start_next_downbeat': 'rcd_start_next_downbeat',
  'rcd_stop_next_downbeat': 'rcd_stop_next_downbeat',
  'play_next_beat': 'play_next_beat',
  'stop_next_beat': 'stop_next_beat',
  'play_next_downbeat': 'play_next_downbeat',
  'stop_next_downbeat': 'stop_next_downbeat',
  'play_next_phrase': 'play_next_phrase',
  'stop_next_phrase': 'stop_next_phrase',
}

class EventHandler:
  def __init__(self, midinome):
    self.midinome = midinome

    # Helix Loop State
    self.next_helix_event = None
    self.helix_trigger_loop_running = False

  def __get_helix_event_from_snap(self, record_or_play, start_or_stop):
    # TODO Optimize this state, this is a lot of logic for simple state update
    trigger_rcd_start_on = self.midinome.user_config.config['TRG RCD Start On']
    trigger_rcd_stop_on = self.midinome.user_config.config['TRG RCD Stop On']
    trigger_play_on = self.midinome.user_config.config['TRG Play On']
    trigger_stop_on = self.midinome.user_config.config['TRG Stop On']
    if record_or_play == 'record':
      if start_or_stop == 'start':
        if trigger_rcd_start_on == trigger_on['Instant']:
          return HelixEvent['rcd_start_instant']
        elif trigger_rcd_start_on == trigger_on['Downbeat']:
          return HelixEvent['rcd_start_next_downbeat']
        else:
          return HelixEvent['rcd_start_next_beat']
      else:
        if trigger_rcd_stop_on == trigger_on['Instant']:
          return HelixEvent['rcd_stop_instant']
        elif trigger_rcd_stop_on == trigger_on['Downbeat']:
          return HelixEvent['rcd_stop_next_downbeat']
        else:
          return HelixEvent['rcd_stop_next_beat']
    else:
      if start_or_stop == 'start':
        if trigger_play_on == trigger_on['Phrase']:
          return HelixEvent['play_next_phrase']
        elif trigger_play_on == trigger_on['Downbeat']:
          return HelixEvent['play_next_downbeat']
        else:
          return HelixEvent['play_next_beat']
      else:
        if trigger_stop_on == trigger_on['Phrase']:
          return HelixEvent['stop_next_phrase']
        elif trigger_stop_on == trigger_on['Downbeat']:
          return HelixEvent['stop_next_downbeat']
        else:
          return HelixEvent['stop_next_beat']

  def on_beat(self, beat_at, is_downbeat):
    pass

  # Program Functions
  def F_Toggle_Metronome_Audio(self):
    current_state = self.midinome.metronome.should_emit_sound
    if current_state == True:
      self.midinome.metronome.should_emit_sound = False
      print('Metronome Audio [OFF]')
    elif current_state == True:
      self.midinome.metronome.should_emit_sound = False
      print('Metronome Audio [ON]')

  def F_Record_Beat(self):
    print('Beat Recorded')
    self.midinome.metronome.record_beat()

  def F_Record_Combo_Press(self, btn):
    self.midinome.current_button_combo.append(btn)
    print(f'Current Combo: [{", ".join(self.midinome.current_button_combo)}]')

  def F_Confirm_Config_Item_Changes(self):
    pass

  def F_Start_Editing_Config_Item(self):
    pass

  def F_Confirm_Time_Signature(self):
    pass

  def F_Confirm_Manual_BPM(self):
    pass

  def F_Enter_Command_Mode(self):
    print('Entering Command Mode')
    pass

  def F_Cancel_Command_Mode(self):
    print('Cancelling Command Mode')
    pass

  # Events
  def on_bpm_change(self, new_bpm):
    print(f'New BPM: {new_bpm}')
    pass

  def on_test_button(self):
    print([ev.event_name for ev in self.midinome.helix.event_queue])

  def on_metronome_button(self):
    mode = self.midinome.mode
    
    if mode == modes['live']:
      if self.midinome.metronome.is_on:
        self.F_Toggle_Metronome_Audio()
        pass
      else:
        self.F_Record_Beat()
        pass
    elif mode == modes['command']:
      self.F_Record_Combo_Press(buttons['metronome'])
      pass
    elif mode == modes['config']:
      # If Currently Editing Config Item
        self.F_Confirm_Config_Item_Changes()
      # Else
        self.F_Start_Editing_Config_Item()
        pass
    elif mode == modes['time_signature']:
      self.F_Confirm_Time_Signature()
      pass
    elif mode == modes['manual_bpm']:
      self.F_Confirm_Manual_BPM()
      pass

  def on_trigger_button(self):
    mode = self.midinome.mode
    metronome_is_on = self.midinome.metronome.is_on
    is_playing_loop = self.midinome.helix.is_playing
    has_loop_stored = self.midinome.helix.rcd_duration > 0
    cfg = self.midinome.user_config.config

    if mode == modes['live']:
      if not has_loop_stored and metronome_is_on:
        if not self.midinome.helix.is_recording:
          self.midinome.helix.start_recording(cfg['TRG RCD Start On'])
        else:
          self.midinome.helix.stop_recording(cfg['TRG RCD Stop On'])
      elif has_loop_stored and metronome_is_on:
        if not is_playing_loop:
          self.midinome.helix.start(cfg['TRG Play On'])
        else:
          self.midinome.helix.stop(cfg['TRG Stop On'])
      pass
    elif mode == modes['command']:
      self.midinome.current_button_combo.append(buttons['trigger'])
      pass
    elif mode == modes['config']:
      # If Currently Editing Config Item
        # Cancel
      # Else
        # Back to Live Mode
      pass
    elif mode == modes['time_signature']:
      # Toggle Selected Time Signature Part
      pass
    elif mode == modes['manual_bpm']:
      # Cancel Edit BPM
      pass

  def on_command_button(self):
    print('Command Pressed')
    mode = self.midinome.mode
    
    if mode == modes['live']:
      # Enter Command Mode
      self.F_Enter_Command_Mode()
      pass
    elif mode == modes['command']:
      self.F_Cancel_Command_Mode()
      pass
    elif mode == modes['config']:
      # If Editing Config Item
        # Increment Config Item Value
      # Else
        # Highlight Next Config Item
      pass
    elif mode == modes['time_signature']:
      # Increment Edit Time Signature Value
      pass
    elif mode == modes['manual_bpm']:
      # Increment Manual BPM Value
      pass

  def on_plus_minus_button(self):
    print('+/- Pressed')
    mode = self.midinome.mode
    
    if mode == modes['live']:
      # Go to config mode
      pass
    elif mode == modes['command']:
      # self.midinome.scurrent_button_combo.append(buttons['plus_minus'])
      pass
    elif mode == modes['config']:
      # If Editing Config Item
        # Decrement Config Item Value
      # Else
        # Highlight Previous Config Item
      pass
    elif mode == modes['time_signature']:
      # Decrement Edit Time Signature Value
      pass
    elif mode == modes['manual_bpm']:
      # Decrement Manual BPM Value
      pass
