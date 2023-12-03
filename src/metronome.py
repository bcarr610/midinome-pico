import time
from audiopwmio import PWMAudioOut as AudioOut
from audiocore import WaveFile
from configuration import app_config
from utils import noop

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

  # State
  last_beat_at = 0

  def __init__(self, audio_out_pin, on_downbeat = noop, on_offbeat = noop, on_beat = noop, on_bpm_change = noop):
    self.on_downbeat = on_downbeat
    self.on_offbeat = on_offbeat
    self.on_beat = on_beat
    self.on_bpm_change = on_bpm_change
    self.audio = AudioOut(audio_out_pin)

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