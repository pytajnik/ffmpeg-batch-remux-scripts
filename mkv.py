#made with python 3.10.11
import os, subprocess, json,re
#This script loads videos from PATH amd match audio and subtitles files in prefered language order
# ffmpeg and ffprobe must be installed (on Windows added to system path variable)
FFMPEG='ffmpeg'; FFPROBE='ffprobe'

#scripts was checked that keeps audio (AC3) file checksum after unpack & pack & unpack again

#files will be loaded from
PATH="./input/"
AUDIO_PATH='./audio/'
SUB_PATH='./sub/'
DATA_PATH='./data/'
OUTPUT_PATH="./output/"

NAME_SPLIT="."


# pattern for match episode titles:  (example: audio.S01E01.DE.ac3 ,  video.S01E01.EN.720p.mkv)

PATTERN = '[sS][0-9][0-9][eE][0-9][0-9]'
#            S    0    3   e   1     2


# languages to load (from first)
#3 letter names for set the language in ffmpeg, 2 letter name to search in file names)

lang2=('pl','en')
lang3=('pol','eng')
lang4=('Polish','English')

#error if too many tracks (can be more than 1 audio by language)
audio_format=('copy','copy','copy','copy','copy','copy','copy','copy','copy','copy')

#trim evry input video from start (-ss) e.g. 00:01:25.000 or 25 (in seconds)
video_trim_from_start = '0'

#trim evry input video from end (-sseof) e.g. 00:01:25.000 or 25 (in seconds)
video_trim_from_end = '0'

#audio/sub track in each file: 1   2   3   4   5   6   7  8
audio_offset                =('0','0','0','0','0','0','0','0','0','0')
sub_offset                  =('0','0','0','0','0','0','0','0','0','0')

DEFAULT_AUDIO=0

#text to add to output file names
TEXT_AFTER_EPISODE=NAME_SPLIT.join(lang2).upper()+'.720p.WEB-DL.x264'

#files extensions to search
#subtitle files with 'FORCED' in name will be forced

audio_extensions=( '.ac3', '.aac','.eac3','.mp3','.mka')
video_extensions=('.mkv', '.avi', '.mp4','.mov','.mpg')
sub_extensions=('.srt', '.txt', '.sub')

OUTPUT_EXTENSION="mkv"

#set current dir to script dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('Current directory:      ', os.getcwd())

video_files = [f for f in os.listdir(PATH) if f.lower().endswith(video_extensions)]
audio_files = [f for f in os.listdir(AUDIO_PATH) if f.lower().endswith(audio_extensions)]
sub_files   = [f for f in os.listdir(SUB_PATH) if f.lower().endswith(sub_extensions)]
#sort files by extension
audio_files.sort(key=lambda x: audio_extensions.index(os.path.splitext(x)[1].lower()))
sub_files.sort(key=lambda x: sub_extensions.index(os.path.splitext(x)[1].lower()))

commands=[]

#FUNTION TO SPLIT FILE NAME TO SPECIAL PARTS (film_title,  episode, lang/format info, file_extension)
def Split_Title(file): 
    ext=file.split(NAME_SPLIT)[-1];ep ='';title=''
    s= re.search(PATTERN, file, flags=re.IGNORECASE)
    if s is not None:
        ep =file[s.start():s.end()];  title=file[0:s.start()]; info=file[s.end():-len(ext)]
    else:
        ep =''; title,info=file.split(NAME_SPLIT,1)[0,-len(ext)]
    return title.strip(NAME_SPLIT), ep.strip( NAME_SPLIT) ,info.strip( NAME_SPLIT),ext

def ffprobe_info(file):
    cmd = [FFPROBE, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file]
    process = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(process.stdout)


os.makedirs(OUTPUT_PATH, exist_ok=True)
#==============Start========================

for v in video_files:
    print('=' * 40); print (v); print('=' * 40)
    film_title, episode, right, extension = Split_Title(v)
    
   #check video info
    info = ffinfo=ffprobe_info(PATH+v).get('streams')[0]
    video_codec=info.get('codec_name')
    
    res=str(info.get('width'))+'x'+str(info.get('height'))
    res_txt=str(info.get('height'))+'p'

    print (' title=',film_title, ' ep=',episode, ' right=',right, ' ext=',extension)
    print ('codec=',video_codec,'res=',res,' ('+res_txt+') ')

    audio=[]; subs=[]; audio_lang=[]; sub_lang=[]; input_option=''
    # -ss crop input file from start, -sseof from end (or use -t for duration -to for end position)
    if video_trim_from_start !='0':input_option+=' -ss '+ video_trim_from_start +' '
    if video_trim_from_end !='0':input_option+=' -sseof '+ video_trim_from_end +' '
    
    #input video file
    input_option+= ' -i "' + PATH+v +'" '
    mapped_channels = " -map 0:v:0 "
    metadata=' '
    other_options= ' -fflags +bitexact '  #without mkv unique id
    # other_options=' -c copy ' + ' -fflags +bitexact '  #without mkv unique id
    other_options+=' -max_interleave_delta 0 '  #fix for error 'Starting new cluster due to timestamp'
    all_streams=1;audio_streams=0;sub_streams=0
    formats=' -c:v copy -c:s copy'
    
    for L2 in (lang2):
        L3=lang3[lang2.index(L2)].lower()
        for file in audio_files:
            title, ep, info, audio_ext = Split_Title(file)
          #  print (title, ep, info, audio_ext)
            if ep.lower()==episode.lower() and title.lower() in film_title.lower():
                #if L2 in info.lower() or L3 in info.lower():
                if NAME_SPLIT+L2 in info.lower() or NAME_SPLIT+L3 in info.lower() or L2+NAME_SPLIT in info.lower() or L3+NAME_SPLIT in info.lower() or info.lower()==L2 or info.lower()==L3:
                    #print some info about audio file
                    print ('...a:',str(audio_streams), file);       ffinfo=ffprobe_info(AUDIO_PATH+file).get('streams')[0]
                    codec=ffinfo.get('codec_name');    ch=ffinfo.get('channels');duration=ffinfo.get('duration')
                    first_audio=codec;bit_rate=int(int(ffinfo.get('bit_rate')+'')/1000);
                    print (' '*4,'lang=',L3,'ffprobe: (codec=',codec,' ch=', ch,' b=',bit_rate,' duration=',duration, ') ')
                    
                    #extend ffmpeg command to load audio file and audio offset (itsoffset must be before input)
                    #command itsoffset offset file 
                    
                    if audio_offset[audio_streams] !='0':input_option+=' -itsoffset '+audio_offset[audio_streams]+' '
                   
                    input_option += ' -i "'+ AUDIO_PATH+file+'" '  

                    mapped_channels +=  ' -map '+str(all_streams)+':a:0 '
                    metadata+= ' -metadata:s:a:'+str(audio_streams) +' language='+L3 +' '
                    metadata+= ' -metadata:s:a:'+str(audio_streams) +' title="'+info.replace(NAME_SPLIT,' ')+'" '
                    formats+= ' -c:a:'+ str(audio_streams) + ' ' + audio_format[audio_streams]
                    
                    #set default audiio
                    if audio_streams==DEFAULT_AUDIO: other_options+=' -disposition:a:'+str(DEFAULT_AUDIO)+ ' default '

                    all_streams+=1; audio_streams+=1

    for L2 in lang2:
        L3=lang3[lang2.index(L2)].lower()
        Lang_Name=lang4[lang2.index(L2)]
        for file in sub_files:
            title,  ep,  info, sub_ext = Split_Title(file)
            if ep.lower()==episode.lower() and title.lower() in film_title.lower():
               # print (file)
                #if L2 in info.lower() or L3 in info.lower():
                if NAME_SPLIT+L2 in info.lower() or NAME_SPLIT+L3 in info.lower() or L2+NAME_SPLIT in info.lower() or L3+NAME_SPLIT in info.lower() or info.lower()==L2 or info.lower()==L3:
                    iii=ffprobe_info(SUB_PATH+file)
                    #print some info about subtitle file
                    print ('...s:',str(sub_streams), file); ffinfo=ffprobe_info(SUB_PATH+file).get('streams')[0]

                    codec=ffinfo.get('codec_name'); print (' '*4,'lang=',L3,'ffprobe: (codec=',codec,') ')

                    #extend ffmpeg command to load subtitle file and delay subtitle
                    if sub_offset[sub_streams] !='0':input_option+=' -itsoffset '+sub_offset[sub_streams]
                    input_option+= ' -i "'+ SUB_PATH + file+'" '
                   
                    

                    mapped_channels +=  ' -map '+str(all_streams)+':s:0 '
                    forced=''
                    #set forced and/or default subtitles
                    if 'forced' in info.lower():
                         forced=' (FORCED)'
                         if sub_streams==0:
                             other_options+=' -disposition:s:'+str(0)+ ' default+forced '
                         else:
                            other_options+=' -disposition:s:'+str(sub_streams)+ ' forced '
                    else: 
                        if sub_streams==0: other_options+=' -disposition:s:'+str(0)+ ' default '
                        
                    metadata+= ' -metadata:s:s:'+str(sub_streams) +' language='+L3 +' '
                    metadata+= ' -metadata:s:s:'+str(sub_streams) +' title="'+Lang_Name+forced+'" '
                    
                    all_streams+=1; sub_streams+=1;forced=''

    #command to load metadata (FFMETADATA format)
    if os.path.isfile(DATA_PATH+v+'.txt'):
         input_option+= ' -i "'+DATA_PATH+v+'.txt" ' 
         metadata= ' -map_metadata '+ str(all_streams) + metadata

    #cmd+=' -i "'+DATA_PATH+v+'.txt" -map_metadata 1 '

    out_file= ' "'+ OUTPUT_PATH + NAME_SPLIT.join([film_title.title(),episode.upper(),TEXT_AFTER_EPISODE,OUTPUT_EXTENSION]).replace(NAME_SPLIT*2, NAME_SPLIT) +'" '
   # out_file= ' "'+ OUTPUT_PATH + NAME_SPLIT.join([film_title.title(),episode.upper(),res_txt,source,video_codec,first_audio,extension]).replace(NAME_SPLIT*2, NAME_SPLIT) +'" '


    cmd = FFMPEG + input_option + mapped_channels + metadata + formats + other_options + out_file + '-y -hide_banner -loglevel warning -stats'
    cmd=" ".join(cmd.split()) #remove double spaces
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

#The Scene release name:

#Title.Of.The.Movie.YEAR.Source.Codec-GROUP
#The Scene release name for TV series
#Title.of.Film.S01E01.LANG1.LANG2.1080p.WEB-DL.DD5.1.H.264-GROUP
