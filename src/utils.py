import time

def noop():
  pass

class TimeTracker:
  def __init__(self, label='Process'):
    print(f'Tracking completion for [{label}]')
    self.__start_time = time.monotonic()
    self.__label = label

  def stop(self):
    print(f'[{self.__label}] Took {(time.monotonic() - self.__start_time) * 1000}ms')
