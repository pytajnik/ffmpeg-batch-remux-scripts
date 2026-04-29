#made with python 3.10.11
import os, subprocess, json,re
#This  convert all audio files in selected folder to AC3

FFMPEG='ffmpeg'; FFPROBE='ffprobe'

#files will be loaded from
AUDIO_PATH='./audio/'
OUTPUT_PATH="./output/"

NAME_SPLIT="."

#files extensions to search
#subtitle files with 'FORCED' in name will be forced

audio_extensions=( '.ac3', '.aac','.eac3','.mp3','.mka')

#set current dir to script dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('Current directory:      ', os.getcwd())





commands=[]
Always_save_audio_as_MKA=False
IN_NAME=''
OUTPUT_CODEC='ac3'
OUTPUT_CHANNELS='6'
EXTENSION=OUTPUT_CODEC
BITRATE='448k'

audio_files = [f for f in os.listdir(AUDIO_PATH) if f.lower().endswith(audio_extensions) and IN_NAME.lower() in f.lower()]

#Load stream info through ffprobe
def ffprobe_info(file):   #this runs FFPROBE to get stream info in json format and then load it using json library
    cmd=  FFPROBE+' -hide_banner -loglevel fatal -show_error -show_format -show_streams -show_programs -show_chapters -show_private_data -print_format json "'+ file +'"'
    file=file +'.json'; subprocess.call(cmd+'>"'+file+'"', shell=True); f=open(file); info = json.load(f); f.close()
    return info

os.makedirs(OUTPUT_PATH, exist_ok=True)
#==============Start========================
for file in audio_files:
    print('=' * 40); print (file); print('=' * 40)
    name, ext=file.rsplit(NAME_SPLIT,1)
    #change channels and bitrate info in file name
    name = re.sub('[2-6]ch', OUTPUT_CHANNELS+'ch', name, flags=re.IGNORECASE)
    name = re.sub('[1-9][1-9][1-9]k', BITRATE, name, flags=re.IGNORECASE)
    

    #print info about input file
    ffinfo=ffprobe_info(AUDIO_PATH+file).get('streams')[0]
    codec=ffinfo.get('codec_name');    ch=ffinfo.get('channels');duration=ffinfo.get('duration')
    first_audio=codec;bit_rate=int(int(ffinfo.get('bit_rate')+'')/1000);
    print ('ffprobe: (codec=',codec,' ch=', ch,' b=',bit_rate,' duration=',duration, ') ')
                    
    name = re.sub(codec, OUTPUT_CODEC.upper(), name, flags=re.IGNORECASE)
    
    input_option=' -i "'+AUDIO_PATH+file+ '" -c:a ' + OUTPUT_CODEC + ' -ac '+OUTPUT_CHANNELS+' -b:a '+BITRATE
    
    if Always_save_audio_as_MKA==True: EXTENSION ='mka'

    out_file= ' "'+OUTPUT_PATH + name + '.' + EXTENSION +'" '
    cmd = FFMPEG + input_option + out_file + '-y -hide_banner -loglevel warning -stats'
    commands.append(cmd)
   
    print('-' * 40);print (cmd);print('=' * 40)
    
i = input('Continue?[y/n]:')
    
#run all FFMPEG commands after 'y' answer
if i=='y':
    for cmd in commands:
        print('');print (cmd);print('')
        subprocess.call(cmd,shell=True)

print('=' * 40);print ('THE END');print('=' * 40)
input("Press Enter to exit...")
