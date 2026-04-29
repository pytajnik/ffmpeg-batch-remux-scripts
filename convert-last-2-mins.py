import os
import subprocess

directory = './i'
output_dir = 'R:/output'
tmp_dir = 'R:/Temp'
extensions = ('.mkv', '.avi', '.mp4', '.mov', '.mpg')
cut_from_start=0
cut_from_end = 120
#cv = ['copy',   'copy',    'copy']
cv = ['copy',   'copy',    'libx264 -b:v 500k -maxrate 1000k -bufsize 4000k -preset slow -profile:v high -level:v 4.0 -x264-params ref=4:cabac=1']

os.makedirs(output_dir, exist_ok=True)
os.makedirs(tmp_dir, exist_ok=True)

for f in os.listdir(directory):
    if f.lower().endswith(extensions):
        filepath = os.path.join(directory, f)
        filename_wo_ext = os.path.splitext(f)[0]
        # command to check duration
        cmd_check_duration = f'ffprobe -v quiet -show_entries format=duration -of csv=p=0 "{filepath}"'
       
        # read video file duration
        result = subprocess.run(cmd_check_duration, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        duration = float(result.stdout.strip())
        
        #cut&convert
        tmp_p1 = os.path.join(tmp_dir, 'p1.mkv')
        tmp_p2 = os.path.join(tmp_dir, 'p2.mkv')
        tmp_p3 = os.path.join(tmp_dir, 'p3.mkv')

        cmd_p1 = f'ffmpeg -ss                         0    -t {cut_from_start}          -i "{filepath}" -map 0 -c:a copy -c:s copy -c:v {cv[0]}   -y -hide_banner -v warning -stats -fflags +bitexact -max_interleave_delta 0 "{tmp_p1}"'
        cmd_p2 = f'ffmpeg -ss          {cut_from_start}    -t {duration - cut_from_end} -i "{filepath}" -map 0 -c:a copy -c:s copy -c:v {cv[1]}   -y -hide_banner -v warning -stats -fflags +bitexact -max_interleave_delta 0 "{tmp_p2}"'
        cmd_p3 = f'ffmpeg -ss {duration - cut_from_end}                                 -i "{filepath}" -map 0 -c:a copy -c:s copy -c:v {cv[2]}   -y -hide_banner -v warning -stats -fflags +bitexact -max_interleave_delta 0 "{tmp_p3}"' 
      
        print ('-'*40)
        print (f'processing {f}')
        print (f'splitted at {cut_from_start} and {duration - cut_from_end} to 3 parts')
        if cut_from_start>0: subprocess.run(cmd_p1, shell=True)
        subprocess.run(cmd_p2, shell=True)
        if cut_from_end>0:   subprocess.run(cmd_p3, shell=True)
        
        # Create input list for merging
        input_list_path = os.path.join(tmp_dir, 'input_list.txt')
        with open(input_list_path, "w") as f_list:
             if os.path.isfile(tmp_p1): f_list.write(f"file '{tmp_p1}'\n")
             if os.path.isfile(tmp_p2): f_list.write(f"file '{tmp_p2}'\n")
             if os.path.isfile(tmp_p3): f_list.write(f"file '{tmp_p3}'\n")

        # Merge command
        cmd_final = f'ffmpeg -f concat -safe 0 -i input_list.txt -map 0 -c copy -y -hide_banner -v warning -stats -fflags +bitexact -max_interleave_delta 0 {f}'
       
        # Merge final file
        output_path = os.path.join(output_dir, f)
        cmd_final = f'ffmpeg -f concat -safe 0 -i "{input_list_path}" -map 0 -c copy -y "{output_path}"'
        subprocess.run(cmd_final, shell=True)
        print(f"finished processing {f}")

print('=' * 40);print ('THE END');print('=' * 40)
input("Press Enter to exit...")