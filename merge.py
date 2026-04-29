import os
import re

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

# Directory containing video files
video_dir = "./"

# Output file for the list of video files
output_file = "output.mp4"

# Get list of video files in directory
video_files = [f for f in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, f)) and f.endswith(".mkv")]
video_files=natural_sort(video_files)

# Write list of video files to text file
with open('concat.txt', "w",encoding='utf-8') as file:
    for video_file in video_files:
        file.write(f"file '{os.path.join(video_dir, video_file)}'\n")

# Run ffmpeg concat command
os.system(f"ffmpeg -f concat -safe 0 -i concat.txt -c:v copy -c:s copy -an output.mp4")