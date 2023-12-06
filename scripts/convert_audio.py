import wave
import numpy as np
from scipy.signal import resample

incoming_file_dir = 'audio/'
incoming_downbeat_file_name = 'downbeat'
incoming_offbeat_file_name = 'offbeat'
outgoing_file_dir = 'src/audio/'
outgoing_downbeat_file_name = 'downbeat'
outgoing_offbeat_file_name = 'offbeat'

def convert_wav(input, output):
  with wave.open(input, 'rb') as input_wav:
    channels = input_wav.getnchannels()
    sample_width = input_wav.getsampwidth()
    frame_rate = input_wav.getframerate()
    frames = input_wav.getnframes()
    audio_data = input_wav.readframes(frames)

  # Make Mono
  if channels > 1:
    audio_data = audio_data = np.frombuffer(audio_data, dtype=np.int16)
    audio_data = audio_data[::channels].tobytes()

  # Resample To 22 kHz
  if frame_rate != 22000:
    audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.int16)
    num_samples = int(len(audio_data) * 22000 / frame_rate)
    audio_data = resample(audio_data, num_samples)
    audio_data = audio_data.astype(np.int16).tobytes()

  # Convert to 16 Bit
  if sample_width != 2:
    audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.int32)
    audio_data = (audio_data * (2 ** 15 - 1) / np.max(np.abs(audio_data))).astype(np.int16)
    audio_data = audio_data.tobytes()

  # Trim
  audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.int16)
  audio_max = np.max(np.abs(audio_data))
  trim_below = 0.1 * audio_max
  non_silent_indices = np.where(audio_data > trim_below)[0]
  start_index = non_silent_indices[0]
  end_index = non_silent_indices[-1]
  audio_data = audio_data[start_index:end_index + 1]

  with wave.open(output, 'wb') as output_wav:
    output_wav.setnchannels(1)
    output_wav.setsampwidth(2)
    output_wav.setframerate(22000)
    output_wav.writeframes(audio_data)

convert_wav('audio/downbeat.wav', 'src/audio/downbeat.wav')
convert_wav('audio/offbeat.wav', 'src/audio/offbeat.wav')
