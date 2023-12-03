from configuration import modes, buttons

class EventHandler:
  def __init__(self, midinome):
    self.midinome = midinome

  # Program Functions
  

  # Events
  def on_bpm_change(self, new_bpm):
    print(f'New BPM: {new_bpm}')
    pass

  def on_beat(self):
    pass

  def on_downbeat(self):
    pass

  def on_offbeat(self):
    pass

  def on_metronome_button(self):
    mode = self.midinome.mode
    
    if mode == modes['live']:
      if self.midinome.metronome.is_on:
        self.midinome.ToggleMetronomeAudio()
      else:
        self.midinome.RecordMetronomeBeat()
    elif mode == modes['command']:
      self.midinome.current_button_combo.append(buttons['metronome'])
    elif mode == modes['config']:
      # If Currently Editing Config Item
        # Confirm Config Item Changes
      # Else
        # Start Editing Config Item
        pass
    elif mode == modes['time_signature']:
      self.midinome.ConfirmTimeSignature()
    elif mode == modes['manual_bpm']:
      self.midinome.sConfirmNewBPM()

  def on_trigger_button(self):
    mode = self.midinome.mode

    if mode == modes['live']:
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
      self.midinome.sToggleSelectedTimeSignatureEditPart()
      pass
    elif mode == modes['manual_bpm']:
      self.midinome.sCancelEditBPM()
      pass

  def on_command_button(self):
    mode = self.midinome.mode
    
    if mode == modes['live']:
      # Enter Command Mode
      pass
    elif mode == modes['command']:
      # Cancel Command
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
    mode = self.midinome.mode
    
    if mode == modes['live']:
      # Go to config mode
      pass
    elif mode == modes['command']:
      self.midinome.scurrent_button_combo.append(buttons['plus_minus'])
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
