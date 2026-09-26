#!/bin/sh
set -eu
# Run from repository root after edit.js. The voice is intentionally off screen.
base=creative/animatic-v1
ffmpeg -y -v warning -i "$base/renders/picture-only.mp4" -i "$base/audio/score-original.wav" -i "$base/audio/mom-voice-original.wav" \
  -filter_complex "[1:a]atrim=0:76,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.4,afade=t=out:st=74.5:d=1.5,volume='if(lt(t,4.5),0.8,if(lt(t,5),0.8-1.1*(t-4.5),if(lt(t,9),0.25,if(lt(t,10),0.25+0.55*(t-9),0.8))))':eval=frame[m];[2:a]asplit=2[v1][v2];[v1]atrim=0:0.7,asetpts=PTS-STARTPTS,atempo=0.8,afade=t=in:st=0:d=0.008,volume=1.8,adelay=5000|5000[a];[v2]atrim=0.7:1.699025,asetpts=PTS-STARTPTS,atempo=0.8,afade=t=in:st=0:d=0.008,apad=pad_dur=0.15,volume=1.8,adelay=7500|7500[b];[m][a][b]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-18:TP=-1.5:LRA=11,aresample=48000[out]" \
  -map 0:v:0 -map '[out]' -c:v copy -c:a aac -b:a 192k -t 76 -movflags +faststart "$base/renders/converse-animatic-v1.mp4"
