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


class TimeTracker:
  def __init__(self, label='Process'):
    print(f'Tracking completion for [{label}]')
    self.__start_time = time.monotonic()
    self.__label = label

  def stop(self):
    print(f'[{self.__label}] Took {(time.monotonic() - self.__start_time) * 1000}ms')
