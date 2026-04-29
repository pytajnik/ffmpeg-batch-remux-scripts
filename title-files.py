import os, subprocess,re

# This file Load episode titles from txt file and add titles to file names

PATH="./output/"
TITLES_FILE='./titles.txt'

PATTERN = '[0-9][0-9]'
#           S    0    3   e   1     2

video_extensions=('.mkv', '.avi', '.mp4','.mov','.mpg')
NAME_SPLIT="."

#set current dir to script dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('Current directory:      ', os.getcwd())

video_files = [f for f in os.listdir(PATH) if f.lower().endswith(video_extensions)]




#FUNTION TO SPLIT FILE NAME TO SPECIAL PARTS (#film_title,  episode, lang/format info, file_extension)
def Split_Title(file): 
    ext=file.split(NAME_SPLIT)[-1];ep ='';title=''
    s= re.search(PATTERN, file, flags=re.IGNORECASE)
    if s is not None:
        ep =file[s.start():s.end()];  title=file[0:s.start()]; info=file[s.end():-len(ext)]
    else:
        ep =''; title,info=file.split(NAME_SPLIT,1)[0,-len(ext)]
    return title.strip(NAME_SPLIT), ep.strip( NAME_SPLIT) ,info.strip( NAME_SPLIT),ext

CHARACTERS_TO_REPLACE = '/\:?!'
REPLACE_WITH='.'
def replace_characters(input_str,characters,char):
    for ch in characters:
        input_str = input_str.replace(ch, char).replace(char*2,char)
    return input_str

#get list of titles from txt (order by pattern - example: S01E01 New Film Title)
episode_titles = {}
with open(TITLES_FILE, mode='r',encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
       if re.match(PATTERN, line.lower()):
            episode_num, title = line.split(NAME_SPLIT, 1);episode_num.strip(NAME_SPLIT).strip() 
            episode_titles[episode_num] = title.strip(NAME_SPLIT).strip()
            #print(episode_titles[episode_num])
            
new_title=[]
print ('Writing titles from "titles.txt" to "'+PATH +'" file names')
for v in video_files:
    print('=' * 40); print (v); print('=' * 40)
    film_title, episode, film_info, extension = Split_Title(v)
    episode_title=episode_titles.get(episode,"")
    print (' title=',film_title, ' ep=',episode, ' ep title=',episode_title, ' right=',film_info, ' ext=',extension)
    t=( '.'.join([film_title, episode, episode_title,film_info,extension]).strip(NAME_SPLIT).replace(NAME_SPLIT*2,NAME_SPLIT) )    
    t=replace_characters (t, CHARACTERS_TO_REPLACE,REPLACE_WITH)
    print ('new title=',t)
    new_title.append(t)

i = input('Continue?[y/n]:')
if i=='y':
    for i,v in enumerate(video_files):
        os.rename(PATH+v, PATH+new_title[i])

print('=' * 40);print ('THE END');print('=' * 40)
input("Press Enter to exit...")
