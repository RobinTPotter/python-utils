import subprocess
import re
import sys
import argparse

# chatgpt helped with this, i'm not saying i couldn't, but it bothers with comments
# i would prefer double quotes if i'm honest

# Set up argument parser
parser = argparse.ArgumentParser(description="Split audio files based on silence detection with minimum duration.")

# Positional arguments
parser.add_argument('input_filename', type=str, help='Input audio file path')
parser.add_argument('min_duration', type=int, help='Minimum duration for each split in seconds')

# Optional arguments
parser.add_argument('--low_volume', type=float, default=-80, help='Volume threshold in dB to detect silence (default: -80dB)')
parser.add_argument('--low_volume_length', type=float, default=4, help='Duration in seconds for silence detection (default: 4s)')

# Parse arguments
args = parser.parse_args()

# Access the parsed arguments
input_file = args.input_filename
min_duration = args.min_duration
low_volume = args.low_volume
low_volume_length = args.low_volume_length

# Print parsed arguments for verification
print(f'Input file: {input_file}')
print(f'Minimum duration: {min_duration} seconds')
print(f'Low volume threshold: {low_volume} dB')
print(f'Low volume length: {low_volume_length} seconds')



# File paths
silence_log = '.silence_log.txt'

# FFmpeg command to detect silence and output to a log file
def detect_silence(input_file, silence_log):
    command = [
        'ffmpeg', '-i', input_file, '-af', f'silencedetect=n={low_volume}dB:d={low_volume_length}', '-f', 'null', '-'
    ]
    with open(silence_log, 'w') as log_file:
        subprocess.run(command, stderr=log_file)

# Parse the silence log to extract silence_end times
def parse_silence_log(silence_log):
    silence_end_times = []
    with open(silence_log, 'r') as log:
        for line in log:
            match = re.search(r'silence_end: (\d+\.?\d*)', line)
            if match:
                silence_end_times.append(float(match.group(1)))
    return silence_end_times

# Split audio at the valid silence points ensuring minimum 10 minutes per chunk
def split_audio(input_file, silence_end_times, min_duration=600):
    last_split = 0
    segment_num = 1
    
    for silence_end in silence_end_times:
        if silence_end - last_split >= min_duration:
            # Split the audio between last_split and silence_end
            output_file = f'{segment_num:03d}-{input_file}'
            command = [
                'ffmpeg', '-i', input_file, '-ss', str(last_split), '-to', str(silence_end),
                '-c', 'copy', output_file
            ]
            subprocess.run(command)
            print(f'Segment {segment_num} created: {output_file}')
            segment_num += 1
            last_split = silence_end
    
    # Split the remaining part after the last silence point
    if last_split < get_audio_duration(input_file):
        output_file = f'output_{segment_num:03d}.opus'
        command = [
            'ffmpeg', '-i', input_file, '-ss', str(last_split), '-c', 'copy', output_file
        ]
        subprocess.run(command)
        print(f'Segment {segment_num} created: {output_file}')

# Helper function to get the total duration of the audio file
def get_audio_duration(input_file):
    command = ['ffmpeg', '-i', input_file]
    result = subprocess.run(command, stderr=subprocess.PIPE, universal_newlines=True)
    duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stderr)
    if duration_match:
        hours, minutes, seconds = map(float, duration_match.groups())
        return hours * 3600 + minutes * 60 + seconds
    return 0

# Main process
detect_silence(input_file, silence_log)                  # Step 1: Detect silence
silence_end_times = parse_silence_log(silence_log)       # Step 2: Parse silence points
split_audio(input_file, silence_end_times, min_duration)          # Step 3: Split audio at valid points


