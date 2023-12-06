import time
from configuration import modes, buttons, trigger_on

HelixEvent = {
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
    self.is_counting_beats_in_phrase = False
    self.current_beat_in_phrase = 0
    self.beats_in_phrase = 0
    self.next_helix_event = None
    self.helix_trigger_loop_running = False
    self.helix_is_recording = False
    self.ready_to_trigger_relooop = False
    # FOR TESTING
    self.log_at = time.monotonic()

  def __get_helix_event_from_snap(self, record_or_play, start_or_stop):
    # TODO Optimize this state, this is a lot of logic for simple state update
    trigger_rcd_on = self.midinome.user_config.config['TRG RCD On']
    trigger_ps_on = self.midinome.user_config.config['TRG P/S On']
    if record_or_play == 'record':
      if start_or_stop == 'start':
        if trigger_rcd_on == trigger_on['Downbeat']:
          return HelixEvent['rcd_start_next_downbeat']
        else:
          return HelixEvent['rcd_start_next_beat']
      else:
        if trigger_rcd_on == trigger_on['Downbeat']:
          return HelixEvent['rcd_stop_next_downbeat']
        else:
          return HelixEvent['rcd_stop_next_beat']
    else:
      if start_or_stop == 'start':
        if trigger_ps_on == trigger_on['Phrase']:
          return HelixEvent['play_next_phrase']
        elif trigger_ps_on == trigger_on['Downbeat']:
          return HelixEvent['play_next_downbeat']
        else:
          return HelixEvent['play_next_beat']
      else:
        if trigger_ps_on == trigger_on['Phrase']:
          return HelixEvent['stop_next_phrase']
        elif trigger_ps_on == trigger_on['Downbeat']:
          return HelixEvent['stop_next_downbeat']
        else:
          return HelixEvent['stop_next_beat']

  
  def tick(self):
    # Fire Reloop
    if self.ready_to_trigger_relooop:
      self.ready_to_trigger_relooop = None
      self.midinome.helix.stop()
      self.midinome.helix.play()

    # Set Reloop Ready State
    if self.midinome.metronome.bpm > 0 and self.helix_trigger_loop_running:
      now = time.monotonic()
      seconds_per_beat = 60 / self.midinome.metronome.bpm
      last_beat_at = self.midinome.metronome.last_beat_at
      remaining_time_in_beat = (last_beat_at + seconds_per_beat) - now
      remaining_time_in_phrase = ((seconds_per_beat * self.beats_in_phrase) - (seconds_per_beat * self.current_beat_in_phrase)) + remaining_time_in_beat

      offset = self.midinome.user_config.config['Helix LAT Offset MS'] / 1000 if self.midinome.user_config.config['Helix LAT Offset MS'] > 0 else 0
      next_trigger_in = remaining_time_in_phrase - offset

      if next_trigger_in <= 0 and self.ready_to_trigger_relooop == False:
        self.ready_to_trigger_relooop = True
  
  def on_beat(self, is_downbeat):
    # Prevent duplicate reloop state changes
    if self.ready_to_trigger_relooop == None:
      self.ready_to_trigger_relooop = False
    
    if not self.helix_is_recording:
      if (self.next_helix_event == HelixEvent['rcd_start_next_downbeat'] and is_downbeat) or self.next_helix_event == HelixEvent['rcd_start_next_beat']:
        # Trigger Record and start counting beats in phrases
        self.helix_is_recording = True
        self.helix_trigger_loop_running = False
        self.is_counting_beats_in_phrase = True
        self.midinome.helix.start_record()
        pass
    elif self.helix_is_recording:
      if (self.next_helix_event == HelixEvent['rcd_stop_next_downbeat'] and is_downbeat) or self.next_helix_event == HelixEvent['rcd_stop_next_beat']:
        self.helix_is_recording = False
        self.helix_trigger_loop_running = True
        self.beats_in_phrase = self.current_beat_in_phrase
        self.is_counting_beats_in_phrase = False
        self.midinome.helix.stop_record()

    # Count Beats In Phrase During Recording
    if self.is_counting_beats_in_phrase:
      self.current_beat_in_phrase += 1
    elif self.beats_in_phrase > 0:
      if self.current_beat_in_phrase >= self.beats_in_phrase:
        self.current_beat_in_phrase = 1
      else:
        self.current_beat_in_phrase += 1
    
    print(f'{self.current_beat_in_phrase} / {self.beats_in_phrase}')

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
    print('Recording Beat')
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
    print('Test Button Pressed')
    self.midinome.helix.play()

  def on_metronome_button(self):
    print('Metronome Pressed')
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
    print('Trigger Press')
    mode = self.midinome.mode
    metronome_is_on = self.midinome.metronome.is_on

    if mode == modes['live']:
      # If no trigger loop and metronome is on
      if not self.helix_trigger_loop_running and metronome_is_on:
        # If not recording loop
        if not self.helix_is_recording:
          # Record Start on next x
          self.next_helix_event = self.__get_helix_event_from_snap('record', 'start')
        else:
          # Record Stop on next x
          self.next_helix_event = self.__get_helix_event_from_snap('record', 'stop')
      # Else if trigger loop and metronome is on
      elif self.helix_trigger_loop_running and metronome_is_on:
        # If not playing loop
        if not self.midinome.helix.is_playing_loop:
          # Start on next x
          self.next_helix_event = self.__get_helix_event_from_snap('play', 'start')
        else:
          # Stop on next x
          self.next_helix_event = self.__get_helix_event_from_snap('play', 'stop')
      pass
    elif mode == modes['command']:
      self.midinome.scurrent_button_combo.append(buttons['trigger'])
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
