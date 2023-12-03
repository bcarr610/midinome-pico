import time

def noop():
  pass

class Emitter:
  def __init__(self, program):
    self.program = program

  def on_beat(self):
    if self.program.metronome.current_beat < 5:
      self.program.metronome.current_beat += 1
    else:
      self.program.is_metronome_running = False

class Metronome:
  def __init__(self, on_beat=noop):
    self.current_beat = 0
    self.on_beat = on_beat

  def trigger_beat(self):
    self.on_beat()

class Program:
  def __init__(self):
    self.is_metronome_running = True
    self.emitter = Emitter(self)
    self.metronome = Metronome()
    self.metronome.on_beat = self.emitter.on_beat

program = Program()

while(program.is_metronome_running):
  program.metronome.trigger_beat()
  print(program.metronome.current_beat)
  time.sleep(2)
