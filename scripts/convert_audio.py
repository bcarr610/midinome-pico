import os
import wave
import numpy as np

incoming_file_dir = 'audio/'
incoming_downbeat_file_name = 'downbeat'
incoming_offbeat_file_name = 'offbeat'
outgoing_file_dir = 'src/audio/'
outgoing_downbeat_file_name = 'downbeat'
outgoing_offbeat_file_name = 'offbeat'
output_pcm_config = {
  'channels': 1,
  'bit_depth': 16,
  'sample_rate': 22000,
  'trim_null_ratio': 0.1
}

def get_dtype(sample_width):
  if sample_width == 1:
    return np.int8
  elif sample_width == 2:
    return np.int16
  elif sample_width == 4:
    return np.int32

def generate_wav_file(from_path, to_path):
  output_audio = None
  output_channels = None
  output_sample_width = None
  output_frame_rate = None
  output_frames = None
  
  with wave.open(from_path) as wav_in:
    # Set Output Default Data
    output_channels = wav_in.getnchannels()
    output_sample_width = wav_in.getsampwidth()
    output_frame_rate = wav_in.getframerate()
    output_frames = wav_in.readframes(-1)
    output_audio = np.frombuffer(output_frames, dtype=get_dtype(output_sample_width))

    # Convert Channels
    if output_channels != output_pcm_config['channels']:
      # Stereo -> Mono
      if output_channels == 2 and output_pcm_config['channels'] == 1:
        output_audio = output_audio.reshape(-1, 2)
        output_audio = np.mean(output_audio, axis=1, dtype=output_audio.dtype)
        output_channels = 1

      # Mono -> Stereo
      elif output_channels == 1 and output_pcm_config['channels'] == 2:
        output_audio = np.column_stack((output_audio, output_audio))
        output_channels = 2

    # Convert Bit Depth
    if output_sample_width * 8 != output_pcm_config['bit_depth']:
      # 8 bit -> 16 bit
      if output_sample_width == 1 and output_pcm_config['bit_depth'] == 16:
        output_audio = (output_audio.astype(np.int16) - 128) * 256
        output_sample_width = 2

      # 16 bit -> 8 bit
      elif output_sample_width == 2 and output_pcm_config['bit_depth'] == 8:
        output_audio = (output_audio.astype(np.float32) / 256).astype(np.int8) + 128
        output_sample_width = 1

    # Sample Rate
    if output_frame_rate != output_pcm_config['sample_rate']:
      ratio = output_pcm_config['sample_rate'] / output_frame_rate
      if output_pcm_config['sample_rate'] > output_frame_rate:
        output_audio = np.interp(
          np.arange(0, len(output_audio) * ratio, ratio),
          np.arange(0, len(output_audio)),
          output_audio
        ).astype(get_dtype(output_pcm_config['sample_rate']))
      else:
        output_audio = np.interp(
          np.arange(0, len(output_audio), ratio),
          np.arange(0, len(output_audio)),
          output_audio
        ).astype(get_dtype(output_pcm_config['sample_rate']))
      output_frame_rate = output_pcm_config['sample_rate']
  
  # Trim Audio
  audio_max = np.max(np.abs(output_audio))
  trim_below = output_pcm_config['trim_null_ratio'] * audio_max
  non_silent_indices = np.where(output_audio > trim_below)[0]
  start_index = non_silent_indices[0]
  end_index = non_silent_indices[-1]
  output_audio = output_audio[start_index:end_index + 1]

  with wave.open(to_path, 'wb') as wav_out:
    wav_out.setnchannels(output_channels)
    wav_out.setsampwidth(output_sample_width)
    wav_out.setframerate(output_frame_rate)
    wav_out.writeframes(output_audio.tobytes())

# __PROGRAM__
# Create outgoing path if not exists
if not os.path.exists(outgoing_file_dir):
  os.makedirs(outgoing_file_dir)

# Convert WAV Files To Match Spec Configuration
print('Converting and trimming incoming wav files for performance optimization...')
generate_wav_file(
  incoming_file_dir + incoming_downbeat_file_name + '.wav',
  outgoing_file_dir + outgoing_downbeat_file_name + '.wav'
)
generate_wav_file(
  incoming_file_dir + incoming_offbeat_file_name + '.wav',
  outgoing_file_dir + outgoing_offbeat_file_name + '.wav'
)
