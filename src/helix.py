from busio import UART
from configuration import app_config
from utils import send_midi_signal

class Helix:
  def __init__(self):
    self.__uart = UART(
      app_config['helix']['uart']['tx'],
      app_config['helix']['uart']['rx'],
      baudrate=31250
    )
    self.__midi_signals = app_config['helix']['midi_signals']

  def __send_signal(self, cc_value_tuple):
    send_midi_signal(self.__uart, cc_value_tuple[0], cc_value_tuple[1])

  def start_record(self):
    print('Starting Recording')
    self.__send_signal(self.__midi_signals['record'])

  def stop_record(self, start_playing=True):
    print('Stopping Recording')
    self.play()
    if not start_playing:
      self.stop()

  def play(self):
    print('Playing')
    self.__send_signal(self.__midi_signals['play'])

  def stop(self):
    print('Stopping')
    self.__send_signal(self.__midi_signals['stop'])

  def looper_block_on(self):
    self.__send_signal(self.__midi_signals['looper_block_on'])

  def looper_block_off(self):
    self.__send_signal(self.__midi_signals['looper_block_off'])

  def tap_tempo(self):
    self.__send_signal(self.__midi_signals['tap_tempo'])
