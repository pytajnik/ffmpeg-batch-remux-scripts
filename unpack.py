import os, subprocess, json,re

#script to extract audio and subtitle tracks from video
# it create file names like audio.S01E01.EN.6ch.128kb.ac3

#python 3.10.11
# ffmpeg and ffprobe must be installed (on Windows added to system path variable)
FFMPEG='ffmpeg'; FFPROBE='ffprobe'

#input output folders (attention! use '/' not '\')
PATH="./input/"
AUDIO_PATH='./audio/'
SUB_PATH='./sub/'
DATA_PATH='./data/'
NAME_SPLIT="."

# episode pattern S*E* will matched
#example:  video.S01E01.EN.720p.mkv -> audio.S01E01.EN.6ch.128kb.ac3
PATTERN = '[sS][0-9][0-9][eE][0-9][0-9]'
#           S    0    3   e   1     2

#will be unpacked only slected languages:
#3 letter names for ffprobe 2 letter names for file names
#(small characters)
# und = undefined
lang2=('pl' ,'en','und')
lang3=('pol','eng','und')



#audio_extensions=( '.ac3', '.aac','.eac3',  '.ogg', '.mp3','.mka')
video_extensions=('.mkv', '.avi', '.mp4','.mov','.mpg')
#sub_extensions=('.srt' ,  '.vtt' ,'.ass', '.txt')

#file extensions and their codecs (small letters)

Always_save_audio_as_MKA=False
extensions={
#audio (or mka for unknown)
    'ac3':      'ac3',
    'aac':      'aac',
    'eac3':     'eac3',
    'vorbis':   'ogg',
    'mp3':      'mp3',
    'pcm':      'pcm',
#subtitles
    'subrip':   'srt',
    'srt':      'srt',
    'webvtt':   'vtt',
    'ass':      'ass',
    'text':     'txt'
}

unpack_audio=True #False
unpack_sub=True #False
unpack_metadata=True #False

#subtitle files with 'FORCED' in name will have forced in names

#set current dir to script dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('Current directory:      ', os.getcwd())

os.makedirs(AUDIO_PATH, exist_ok=True)
os.makedirs(SUB_PATH, exist_ok=True)
os.makedirs(DATA_PATH, exist_ok=True)

#audio_files = [f for f in os.listdir(AUDIO_PATH) if f.lower().endswith(audio_extensions)]
video_files = [f for f in os.listdir(PATH) if f.lower().endswith(video_extensions)]
#sub_files   = [f for f in os.listdir(SUB_PATH) if f.lower().endswith(sub_extensions)]

commands=[]

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

def ffmpeg_metadata(in_file,out_file):
        cmd2=FFMPEG+'  -i "'+in_file +'"  -f ffmetadata "'+out_file+'" -y -hide_banner -loglevel warning -stats'
        subprocess.call(cmd2,shell=True)
        f= open(out_file, mode='r',encoding='utf-8'); lines = f.read().splitlines(); f.close()
        return lines

for v in video_files:
  
    print('=' * 40); print (v); print('=' * 40)

    film_title, episode, right, extension = Split_Title(v)
    print (' title=',film_title, ' ep=',episode, ' right=',right, ' ext=',extension)

    #FFMETADATA
    if unpack_metadata == True:
        ffmpeg_metadata (PATH+v,DATA_PATH+v+'.txt')
        #cmd2=FFMPEG+'  -i "'+PATH+v +'"  -f ffmetadata "'+DATA_PATH+v+'.txt" -y -hide_banner -loglevel warning -stats'
       # subprocess.call(cmd2,shell=True)

 
    #cmd = FFPROBE+' -v error -print_format json -show_format -show_streams "'+ PATH+v +'"'

   # cmd=  FFPROBE+' -hide_banner -loglevel fatal -show_error -show_format -show_streams -show_programs -show_chapters -show_private_data -print_format json "'+ PATH+v +'"'

    #file=PATH+v +'.json'
  #  subprocess.call(cmd+'>"'+file+'"', shell=True)
   # f=open(file); info = json.load(f); f.close()
    info=ffprobe_info(PATH+v)
        # file.write(output)
 

    #generate FFMPEG command to unpack audio & sub
    cmd2=FFMPEG+' -y -hide_banner -loglevel warning -stats -i "'+PATH+v +'"  '
    
    for d in info.get('streams'):
        index=       d.get('index','0')
        codec_name = d.get('codec_name','ERROR').lower()
        codec_type = d.get('codec_type','ERROR')
        
        out_file='';lang='';forced='';channels='';bitrate=''
        if codec_type=='audio' and unpack_audio==True:
            lang=d.get('tags').get('language').lower()
            
            if not lang in lang3: continue #if language not found continue to next iteration
            i=lang3.index(lang)
          
            channels  = str(d.get('channels','0'))+'ch'
            bitrate  =  str(int(int(d.get('bit_rate','0'))/1000))+'k'
            if bitrate=='0k': bitrate='VBR'  #if bitrate not detected - probably VBR - add text to name
            
            extension=extensions.get(codec_name,'mka')
            if Always_save_audio_as_MKA==True: extension =NAME_SPLIT+codec_name.upper()+'.mka'
            
            out_file= NAME_SPLIT.join([film_title.title(),episode.upper(),lang2[i].upper(),channels,bitrate,extension]).replace(NAME_SPLIT*2, NAME_SPLIT)
            #example name                  Title          .S01E01 .      EN               . 2ch    .    128kb . ac3

            #add number to filename if exists in final cmd (when more than 1 track/language)
            i=1;replace_this= '.'
            while out_file in cmd2:
              if i>1: replace_this=with_this
              i=i+1; with_this=('.'+str(i)+'.'); out_file= with_this.join(out_file.rsplit(replace_this, 1))
              
            cmd2+=' -map 0:'+str(index) + ' -c copy "'+AUDIO_PATH + out_file+'"'
            
        elif codec_type=='subtitle' and unpack_sub==True:
            lang=d.get('tags').get('language')
            
            if not lang in lang3: continue #if language not found continue to next iteration
            i=lang3.index(lang)

            #is subtitle track FORCED?
            forced=''
            if d.get('disposition').get('forced'): forced = 'forced'
            if 'forced'.lower() in str(d.get('tags').get('title')).lower(): forced = 'forced'
          
            extension=extensions.get(codec_name,'srt')
            
            out_file=NAME_SPLIT.join([film_title,episode,lang2[i].upper(),forced, extension]).replace(NAME_SPLIT*2, NAME_SPLIT)

            #example name           Title       .S01E01 .   EN          . forced  .     ac3
            
            #add number to filename if exists in final cmd (when more than 1 track/language)
            i=1;replace_this= '.'
            while out_file in cmd2:
              if i>1: replace_this=with_this
              i=i+1; with_this=('.'+str(i)+'.'); out_file= with_this.join(out_file.rsplit(replace_this, 1))
              
            cmd2+=' -map 0:'+str(index) + ' -c copy "'+SUB_PATH + out_file +'"'
            
        print (extension,episode, index, codec_name, codec_type, lang, channels, bitrate, forced)
    print('-' * 40);print (cmd2);print('-' * 40);print('')
    commands.append(cmd2)

i = input('Continue?[y/n]:')
    
#run all FFMPEG commands after 'y' answer
if i.lower()=='y':
    for cmd in commands:
        print('');print (cmd2);print('')
        subprocess.call(cmd,shell=True)
        
print('=' * 40);print ('THE END');print('=' * 40)

input("Press Enter to exit...")

#ffprobe -show_entries stream=index,codec_type:stream_tags=language -of compact $video1 2>&1 | { while read line; do if $(echo "$line" | grep -q -i "stream #"); then echo "$line"; fi; done; while read -d $'\x0D' line; do if $(echo "$line" | grep -q "time="); then echo "$line" | awk '{ printf "%s\r", $8 }'; fi; done; }

#The Scene release name:
#Title.Of.The.Movie.YEAR.Source.Codec-GROUP
#The Scene release name for TV series
#Title.of.Film.S01E01.1080p.WEB-DL.DD5.1.H.264-GROUP.Spanish.English.Subs
