## Order Of Items To Complete

- [ ] Define Program Logic
- [ ] Define Button Input Logic
- [ ] Connect TRS Female
- [ ] Connect MIDI Module
- [ ] Connect LCD
- [ ] Build Metronome Class
- [ ] Build MIDI Trigger Class
- [ ] Build LCD Display Class
- [ ] Map Primary Loop To Handle Metronome, MIDI and LCD classes
- [ ] Map Buttons to Button Input Logic
- [ ] Test On Helix
- _Provided No Items Added After Testing..._
  - [ ] Building Wiring Diagram
  - [ ] Build PCB Diagram
  - [ ] Build Case Diagram
  - [ ] Design Case Parts
  - [ ] Print Case Parts
  - [ ] Avengers..... ASSEMBLE!!!

## Desired Controls

**Metronome**

- Record Beat
- Stop Metronome
- Mute/Unmute Metronome While retaining saved bpm

**Trigger**

- Start/Stop Looper On Next Downbeat
- Start/Stop Looper on next phrase start
- Only Play While Holding

**Control**

- Change Time Signature
- Quick Shutdown (Kill the board in case of error)
- Disable Outgoing MIDI
- Disable Incomming MIDI
- Metronome Double Time / Half Time
- Change Double Press Delay
- Change Hold Duration
- Latency

### Future Ideas

- Pull Audio from the looper and store in memory to enable time stretching?
- Bluetooth/Serial Connection to sync multiple Midinomes

### Button Logic

Button actions
5 Buttons: METRONOME, TRIGGER, CONTROL, PLUS, MINUS

Button Press Variations: single_press, double_press, hold

```python
  mode: 'settings' | 'live'
  is_editing_setting: True | False
  metronome_running: True | False
  metronome_speed: 'half_time' | 'standard' | 'double_time'
  triggering_looper: True | False

  def METRONOME_SINGLE_PRESS():
    if mode == 'settings':
      if is_editing_setting:
        change_setting()
      else:
        start_editing_setting()
      return

    if metronome_running:
      toggle_metronome_audio()
    else:
      record_beat()

    return

  def METRONOME_DOUBLE_PRESS():
    if mode == 'settings':
      if is_editing_setting:
        cancel_edit_setting()
      else:
        back_to_live_mode()
      return
    return

  # TODO On Metronome Hold, Stop Metronome and stop triggering MIDI events (release control to the HELIX)
  # TODO What happens if helix has loop running and we start a new metronome?

  def PLUS_PRESS():
    if mode === 'settings':
      if is_editing_setting:
        val_up()
      else:
        select_next_setting()
      pass
    else:
      if metronome_running:
        if metronome_speed == 'half-time':
          standard_time()
        elif metronome_speed == 'standard':
          double_time()

  def PLUS_MINUS():
    if mode === 'settings':
      if is_editing_setting:
        val_down()
      else:
        select_prev_setting()
      pass
    else:
      if metronome_running:
        if metronome_speed == 'standard':
          half_time()
        elif metronome_speed == 'double_time':
          standard_time()


```

```python
# # MIDI Control Numbers
CC_RECORD_OVERDUB = 60
CC_PLAY_STOP = 61
CC_PLAY_ONCE = 62

# # MIDI Control Volues
MIDI_RECORD = 80
MIDI_OVERDUB = 40
MIDI_PLAY = 80
MIDI_STOP = 40
MIDI_PLAY_ONCE = 80

# # MIDI Data
# # Helix Documentation: https://helixhelp.com/tips-and-guides/universal/midi
# # Record: CC_60, 0-63 (overdub), 64-127 Record
# # Play Stop: CC_61, Stop(0-63), Play (64-127)
# #  Play Once: CC_62, 64-127

# __MIDI__
uart = UART(0, baudrate=31250)
def send_control_change(control_number, value):
  midi_data = bytes([0xB0, control_number, value])
```
