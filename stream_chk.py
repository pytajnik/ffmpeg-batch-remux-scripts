#made with python 3.10.11
import os, subprocess,re,time

#This script check videos/audio streams checksums
#ffmpeg and ffprobe must be installed (on Windows added to system path variable)
FFMPEG='ffmpeg'; FFPROBE='ffprobe'


extensions=('.mkv', '.avi', '.mp4','.mov','.mpg',  '.ac3', '.aac','.eac3','.mp3','.mka',  '.srt',  '.sub')

#set current dir to script dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('Current directory:      ', os.getcwd())

files = [f for f in os.listdir('.') if f.lower().endswith(extensions)]


def create_checksum(video, checksum, file):
        cmd='ffmpeg -i "'+ video +'" -map 0 -c copy -f streamhash -hash '+checksum+'  -hide_banner -loglevel error -y "'+file+'" '
        # unspecified file = load to memory
        if file =='-':
            checksums=[]
            output=subprocess.check_output(cmd, shell=True).decode('utf-8')
            for line in output.splitlines():
                checksums.append(re.split('[,=]', line.strip()) )
            return checksums
        else: #save to file & load it
            subprocess.call(cmd, shell=True)
            return load_checksum_file(file)
        
def load_checksum_file(file_name):
    checksums = []
    with open(file_name, 'r') as file:
        for line in file:
            checksums.append(re.split('[,=]', line.strip()) )
        file.close()
    return checksums


def compare_checksums(ch1,ch2): #ch1 - loaded from file, ch2 in memory
    print("{: >48}{: >36}".format('SAVED CHECKSUM', 'IN MEMORY'));print('-' * 96)
    for ch in ch1:
        i=ch1.index(ch)
        error='[ OK]'
        if ch[3]!=ch2[i][3]: error='[ X ]'
        format_str='{: >2}{: >2}{: >8}{: >36}{: >36}{: >8}'
        print(format_str.format(*ch, ch2[i][3], error))


def print_checksum(ch1):
      print("{: >48}".format('CHECKSUM SAVED'));print('-' * 96)
      for ch in ch1: print('{: >2}{: >2}{: >8}{: >36}'.format(*ch))
        

for v in files:
    print('=' * 40); print (v); print('=' * 40)

    checksum='md5'
    file=v+'.stream'+checksum

    #if checksum file found - load & compare
    if os.path.isfile(file):
        ch1=load_checksum_file(file)
        ch2=create_checksum (v,checksum,'-')
        compare_checksums(ch1,ch2)
    else: #create checksum file
        ch1=create_checksum (v,checksum,file)
        print_checksum(ch1)   

    print(' ' * 40)
print('=' * 40);print ('THE END');print('=' * 40)
input("Press Enter to exit...")

