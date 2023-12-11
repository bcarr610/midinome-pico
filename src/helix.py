import time
from busio import UART
from configuration import app_config, trigger_on
from utils import send_midi_signal

class HelixQueueEventNames:
  rcd_start = 0
  rcd_stop = 1
  start_reloop = 2
  stop_reloop = 3
  destroy_reloop = 4
  __play_once = 5
  __play_stop = 6

class HelixQueueEvent:
  event_name = None
  at_time = None
  was_executed = False

  def __init__(self, event_name, at_time):
    self.event_name = event_name
    self.at_time = at_time

class Helix:
  def __init__(self, midinome):
    self.__uart = UART(
      app_config['helix']['uart']['tx'],
      app_config['helix']['uart']['rx'],
      baudrate=31250
    )
    self.midinome = midinome
    self.__midi_signals = app_config['helix']['midi_signals']

    # Config
    #! MIDI LAT OFFSET SHOULD NEVER BE A NEGATIVE VALUE
    self.midi_signal_lat_offset = self.midinome.user_config.config['Helix LAT Offset MS'] * 1000

    # State
    self.is_recording = False
    self.is_looping = False
    self.is_playing = False
    self.rcd_start = 0.0
    self.rcd_duration = 0.0
    self.rcd_beats = 0
    self.current_beat_at = 0.0
    self.next_beat_at = 0.0
    self.next_downbeat_at = 0.0
    self.next_phrase_at = 0.0
    self.event_queue = []

  def on_beat(self, beat_at, is_downbeat):
    self.current_beat_at = beat_at
    self.next_beat_at = beat_at + self.midinome.metronome.time_per_beat
    self.next_downbeat_at = self.next_beat_at + ((self.midinome.metronome.time_signature[0] - self.midinome.metronome.current_beat_in_measure) * self.midinome.metronome.time_per_beat)
    self.next_phrase_at = self.current_beat_at + self.rcd_beats * self.midinome.metronome.time_per_beat
    

  def tick(self):
    now = time.monotonic()
    
    for index, queue_event in enumerate(self.event_queue):
        # Update Instance State
        if now >= queue_event.at_time:
          self.event_queue[index].was_executed = True
          self.__handle_next_event(queue_event, now)

    # Delete Completed Events
    new_events = []
    for queue_event in self.event_queue:
      if not queue_event.was_executed:
        new_events.append(queue_event)

      self.event_queue = new_events
    
  def __handle_next_event(self, helix_queue_event, current_time):
    event_name = helix_queue_event.event_name

    # RCD Start
    if event_name == HelixQueueEventNames.rcd_start:
      self.__send_record_signal()
      self.is_recording = True
      self.rcd_start = current_time

    # RCD Stop
    elif event_name == HelixQueueEventNames.rcd_stop:
      self.__send_record_signal()
      self.__send_stop_signal()
      self.is_recording = False
      self.rcd_duration = current_time - self.rcd_start
      self.rcd_beats = round(self.rcd_duration)
      
      if self.midinome.user_config.config['Loop After RCD']:
        self.is_looping = True
        # TODO Queue Events to start reloop

    # Play Once or Start Reloop
    elif event_name == HelixQueueEventNames.start_reloop or event_name == HelixQueueEventNames.__play_once:
      self.__send_play_once_signal()
      if event_name == HelixQueueEventNames.start_reloop:
        self.is_looping = True

      if self.is_looping:
        stop_at = current_time + min(
          self.rcd_duration,
          self.rcd_beats * self.midinome.metronome.time_per_beat
        ) - self.midi_signal_lat_offset
        start_at = self.current_beat_at + (self.rcd_beats * self.midinome.metronome.time_per_beat)
        self.event_queue.append(HelixQueueEvent(HelixQueueEventNames.__play_stop, stop_at))
        self.event_queue.append(HelixQueueEvent(HelixQueueEventNames.__play_once, start_at))

    # Play Stop or Stop Reloop
    elif event_name == HelixQueueEventNames.stop_reloop or event_name == HelixQueueEventNames.__play_stop:
      self.__send_stop_signal()

      if event_name == HelixQueueEventNames.stop_reloop:
        self.is_looping = False
        self.event_queue = []

  def __queue_event(self, event_name, snap):
    now = time.monotonic()
    at_time = None

    if snap == trigger_on['Instant']:
      at_time = now
    elif snap == trigger_on['Beat']:
      at_time = self.next_beat_at - self.midi_signal_lat_offset
    elif snap == trigger_on['Downbeat']:
      at_time = self.next_downbeat_at - self.midi_signal_lat_offset
    elif snap == trigger_on['Phrase']:
      at_time = self.next_phrase_at - self.midi_signal_lat_offset
    
    if at_time is not None:
      print('Added to queue')
      self.event_queue.append(HelixQueueEvent(event_name, at_time))

  def start_recording(self, snap):
    if not self.is_recording and not self.is_looping and self.rcd_duration == 0.0:
      event_name = HelixQueueEventNames.rcd_start
      self.__queue_event(event_name, snap)

  def stop_recording(self, snap):
    if self.is_recording and not self.is_looping and self.rcd_duration == 0.0:
      event_name = HelixQueueEventNames.rcd_stop
      self.__queue_event(event_name, snap)

  def start(self, snap):
    if not self.is_recording and not self.is_looping and self.rcd_duration > 0.0:
      event_name = HelixQueueEventNames.start_reloop
      self.__queue_event(event_name, snap)

  def stop(self, snap):
    if not self.is_recording and self.is_looping and self.rcd_duration > 0.0:
      event_name = HelixQueueEventNames.stop_reloop
      self.__queue_event(event_name, snap)

  # MIDI Send Signal Functions
  def __send_signal(self, cc_value_tuple):
    send_midi_signal(self.__uart, cc_value_tuple[0], cc_value_tuple[1])
  
  def __send_record_signal(self):
    print('RCD Sent')
    self.__send_signal(self.__midi_signals['record'])

  def __send_stop_signal(self):
    print('Stop Sent')
    self.__send_signal(self.__midi_signals['stop'])

  def __send_play_once_signal(self):
    print('Play Sent')
    self.__send_signal(self.__midi_signals['play_once'])

  def __send_tap_tempo_signal(self):
    self.__send_signal(self.__midi_signals['tap_tempo'])
