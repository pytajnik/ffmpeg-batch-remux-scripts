import os, subprocess,re

# This file Load episode titles from txt file and generate FFMETADATA files with titles

PATH="./input/"
DATA_PATH='./data/'
TITLES_FILE='./titles.txt'
NAME_SPLIT="."

PATTERN = '[sS][0-9][0-9][eE][0-9][0-9]'
#           S    0    3   e   1     2

video_extensions=('.mkv', '.avi', '.mp4','.mov','.mpg')

#set current dir to script dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('Current directory:      ', os.getcwd())

video_files = [f for f in os.listdir(PATH) if f.lower().endswith(video_extensions)]

os.makedirs(DATA_PATH, exist_ok=True)

#FUNTION TO SPLIT FILE NAME TO SPECIAL PARTS (#film_title,  episode, lang/format info, file_extension)
def Split_Title(file): 
    ext=file.split(NAME_SPLIT)[-1];ep ='';title=''
    s= re.search(PATTERN, file, flags=re.IGNORECASE)
    if s is not None:
        ep =file[s.start():s.end()].upper();  title=file[0:s.start()]; info=file[s.end():-len(ext)]
    else:
        ep =''; title,info=file.split(NAME_SPLIT,1)[0,-len(ext)]
    return title.strip(NAME_SPLIT), ep.strip( NAME_SPLIT) ,info.strip( NAME_SPLIT),ext


episode_titles = {}
with open(TITLES_FILE, mode='r',encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
       if re.match(PATTERN, line,flags=re.IGNORECASE):
            episode_num, title = line.split(NAME_SPLIT, 1);episode_num.strip(NAME_SPLIT).strip() 
            episode_titles[episode_num] = title.strip(NAME_SPLIT).strip()
          #  print(episode_titles[episode_num])
            
lines=[]

print ('Writing titles from "titles.txt" to "'+DATA_PATH +'" metadata txt files')
for v in video_files:
    data_file=DATA_PATH+v+'.txt'
    print('=' * 40); print (v); print('=' * 40)
    film_title, episode, right, extension = Split_Title(v)

    episode_title=episode_titles.get(episode,"")
    print (' title=',film_title, ' ep=',episode, ' right=',right, ' ext=',extension)

    ffmpeg_title = 'title='+' '.join([film_title.replace(NAME_SPLIT," "),episode+".", episode_title])
            
    if os.path.isfile(data_file):
        f= open(data_file, mode='r',encoding='utf-8'); lines = f.read().splitlines(); f.close()
        f= open(data_file, mode='w',encoding='utf-8'); 

        print (lines, len(lines))
        if len(lines)>1:
            if 'title' in lines[1].lower():
                lines[1]=ffmpeg_title
            else: lines.insert(1,ffmpeg_title)
        else: lines.insert(1,ffmpeg_title)
        f.write("\n".join(lines))
        f.close()
    else:
        f= open(data_file, mode='w+',encoding='utf-8')
        f.write(';FFMETADATA1' + '\n')
        f.write(ffmpeg_title + '\n')
        f.close()

    print (lines)
print('=' * 40);print ('THE END');print('=' * 40)
input("Press Enter to exit...")
