from machine import UART, Pin, PWM
import uasyncio as asyncio
import time
import array
import ujson

# Load Assets
pwm_audio = None

with open('pwm_data.json', 'r') as pwm_data_file:
  pwm_audio = ujson.load(pwm_data_file)

# # __CONFIG__
# # Pins
gpio_led = Pin("LED", Pin.OUT)
gpio_test_button = Pin(6, Pin.IN, Pin.PULL_DOWN)
gpio_speaker = PWM(Pin(15))

# # Pin Config
gpio_speaker.freq(44100)
gpio_speaker.duty_u16(32768)

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

# __Functions__
async def stream_audio(filename):
  with open(filename, 'rb') as audio_file:
    chunk_size = 512 # Adjust for memory allocation
    sample_delay = 0 # Adjust for performance usage
    print('Playing Audio')

    while True:
      chunk = audio_file.read(chunk_size)
      if not chunk:
        break

      for sample in chunk:
        gpio_speaker.duty_u16(sample)
        await asyncio.sleep_ms(sample_delay)

  gpio_speaker.deinit()
  print('Playing complete')

# __Handlers__
def on_test_button_press():
  print('Test Btn Pressed')

# __Program__
gpio_test_button.irq(trigger=Pin.IRQ_RISING, handler=on_test_button_press)


async def main():
  audio_task = None
  
  while True:
    if audio_task and not audio_task.done():
      audio_task.cancel()
      try:
        await audio_task
      except asyncio.CancelledError:
        pass
    
    asyncio.create_task(stream_audio(pwm_audio['downbeat']['file_path']))
    gpio_led.toggle()
    await asyncio.sleep_ms(1000)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
