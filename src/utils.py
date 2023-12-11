import time

def noop():
  pass

def path_exists(path):
  try:
    f = open(path, 'r')
    return True
  except:
    return False
  
def send_midi_signal(uart, cc, value, midi_channel=0):
  status_byte = 0xB0 + midi_channel
  uart.write(bytes([status_byte, cc, value]))

def time_until_next_beat(last_beat_at, bpm):
  pass

def time_until_new_phrase(beats_in_phrase, current_beat, last_beat_at, bpm):
  pass

class TimeTracker:
  def __init__(self, label='Process'):
    print(f'Tracking completion for [{label}]')
    self.__start_time = time.monotonic()
    self.__label = label

  def stop(self):
    print(f'[{self.__label}] Took {(time.monotonic() - self.__start_time) * 1000}ms')
