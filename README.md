# ffmpeg-batch-remux-scripts

Some useful batch remux scripts for FFmpeg.  
This tool is intended for remuxing TV series with different audio and subtitle tracks.

**Attention 1:** Requires manual code adjustments depending on your individual needs.  
**Attention 2:** My code is a mess!  
(These scripts were written in Python 3.10.11 on Windows in 2024 and have not been tested on Linux yet.  )

## scripts description
**unpack.py** - unpack video files from input dir  
**mkv.py** - mux mkv files to output dir  
**audio-to-ac3.py** - convert audio tracks from audio dir  
**title-metadata.py** - add titles from titles.txt to video metadata using 'FFMETADATA'   
**title-files.py** - add titles from titles.txt to video names  
**stream_chk.py** -  check videos/audio streams checksums using ffmpeg 'streamhash'

## Example usage

1. Make sure `ffmpeg` and `ffprobe` are available in your system PATH.  
2. Put your video files (e.g. `my.video.S01E01.EN.720p.mkv`) into the `video` subdirectory.  
3. Run `unpack.py` (edit it first to set the languages you want to extract).  
4. Make any changes you need — for example, replace video files with different resolutions, or add subtitles or audio extracted from other files.  
5. Run `mkv.py` (you may also need to edit it before running).
6. it may work out of the box or not. If not learn how to fix errors :-)

**btw.1** sometimes renaming files could help)  
**btw.2** use MediaInfo to check input/output files, their formats and parametres

