import time
from audiopwmio import PWMAudioOut as AudioOut
from audiocore import WaveFile
from configuration import app_config

class Metronome:
  # TODO CONVERT SOME OF THESE INTO USER/APPCONFIG
  # TODO Instead of setting last_beat at when a beat emits, set times each measure for each beat to keep clock in sync
  detect_bpm_from_last = 4
  stop_recording_after = 2
  time_signature = [4, 4]

  # Sound Latency Control
  metronome_audio_offset = 0

  # State
  bpm = 0
  time_per_beat = 0.0
  is_on = None
  last_beat_at = 0.0
  next_beat_at = 0.0
  next_measure_at = 0.0
  last_x_recording_timestamps = []
  current_beat_in_measure = 1
  ready_to_emit_beat = False
  should_emit_events = None
  should_emit_sound = None

  def __init__(
      self,
      audio_out_pin,
      on_beat=None,
      on_bpm_change=None,
    ):
    self.emit_on_beat = on_beat
    self.emit_on_bpm_change = on_bpm_change
    self.audio = AudioOut(audio_out_pin)

    self.downbeat_file = open(app_config['downbeat_file_path'], 'rb')
    self.offbeat_file = open(app_config['offbeat_file_path'], 'rb')

  # Calculations
  # def get_time_since_last_beat(self, now=time.monotonic()):
  #   return now - self.last_beat_at
  
  # def get_time_until_next_beat(self, now=time.monotonic()):
  #   return self.time_per_beat - (now - self.last_beat_at)
  
  # def get_time_until_next_downbeat(self):
  #   return self.get_time_until_next_beat() + ((self.time_signature[0] - self.current_beat_in_measure) * self.time_per_beat)
    
  # def get_next_beat_number(self):
  #   return self.current_beat_in_measure if self.current_beat_in_measure < self.time_signature[0] else 1

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

  # State Updates
  def change_time_signature(self, beats_per_measure, beat_value):
    self.time_signature = [beats_per_measure, beat_value]
    if self.current_beat_in_measure > beats_per_measure:
      self.current_beat_in_measure = 1

  # Functions
  def play_sound(self, wav):
    self.audio.play(wav)

  # Events
  def on_beat(self):
    print(f'{self.current_beat_in_measure}/{self.time_signature[1]}')
    is_downbeat = self.current_beat_in_measure == self.time_signature[0]

    if self.emit_on_beat is not None:
      self.emit_on_beat(self.last_beat_at, is_downbeat)

  def tick(self):
    if self.bpm > 0 and self.is_on:
      now = time.monotonic()

      # Manage Beat State
      if now - self.last_beat_at >= self.time_per_beat:
        self.last_beat_at = now
        self.next_beat_at = now + self.time_per_beat
        self.next_measure_at = (self.time_signature[0] - self.current_beat_in_measure + 1) * self.time_per_beat
        self.current_beat_in_measure = self.current_beat_in_measure + 1 if self.current_beat_in_measure < self.time_signature[0] else 1
        if self.ready_to_emit_beat == False:
          self.ready_to_emit_beat = True

    # Stop Recording BPM
    if len(self.last_x_recording_timestamps):
      if (time.monotonic() - self.last_x_recording_timestamps[-1] > self.stop_recording_after):
        self.last_x_recording_timestamps = []

    # Emit Sound and events
    if self.ready_to_emit_beat:
      now = time.monotonic()
      self.ready_to_emit_beat = False
      
      # Emit Sound
      if self.should_emit_sound:
        wave_file = self.offbeat_file if self.current_beat_in_measure == self.time_signature[0] else self.downbeat_file
        wav = WaveFile(wave_file)
        self.play_sound(wav)

      # Emit Events
      if self.should_emit_events:
        self.on_beat()

  def __start_metronome(self, bpm):
    self.bpm = bpm
    self.last_x_recording_timestamps = []
    self.last_beat_at = time.monotonic()
    self.time_per_beat = 60 / self.bpm

    if self.is_on == None:
        self.is_on = True

    if self.should_emit_sound == None:
      self.should_emit_sound = True

    if self.should_emit_events == None:
      self.should_emit_events = True

    self.trigger_bpm_change(self.bpm)
    self.on_beat()

  def record_beat(self):
    if len(self.last_x_recording_timestamps) + 1 < self.detect_bpm_from_last:
      self.last_x_recording_timestamps.append(time.monotonic())
    else:
      # Set BPM
      # TODO This function needs to wait before triggering beat 1
      # TODO(cont) It's currently firing immediately on press
      differences = [self.last_x_recording_timestamps[i + 1] - self.last_x_recording_timestamps[i] for i in range(len(self.last_x_recording_timestamps) - 1)]
      average_diff = sum(differences) / len(differences) if differences else 0
      bpm = round(60 / average_diff) if average_diff != 0 else 0
      self.__start_metronome(bpm)

  def trigger_bpm_change(self, value):
    if self.emit_on_bpm_change is not None:
      self.emit_on_bpm_change(value)