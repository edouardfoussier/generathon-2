#!/bin/sh
set -eu
# Args: input picture, shared audio directory, output. Identical soundtrack for all models.
picture=$1
audio=$2
output=$3
ffmpeg -y -v warning -i "$picture" -i "$audio/score.wav" -i "$audio/mom-opening.wav" -i "$audio/luna-annoyed.wav" -i "$audio/mom-return.wav" -i "$audio/luna-ending.wav" \
 -filter_complex "[1:a]atrim=0:76,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=2,afade=t=out:st=74.6:d=1.4,volume='if(lt(t,10),0.19,if(lt(t,22),0.4,if(lt(t,62),0.72,if(lt(t,71),0.19,0.6))))':eval=frame[m];[2:a]atempo=0.70,highpass=f=130,lowpass=f=6600,aecho=0.8:0.8:45:0.1,volume=1.45,adelay=250|250[v1];[3:a]atempo=0.72,volume=1.35,adelay=6120|6120[v2];[4:a]atempo=0.72,highpass=f=130,lowpass=f=6600,aecho=0.8:0.8:45:0.1,volume=1.45,adelay=62900|62900[v3];[5:a]atempo=0.78,volume=1.35,adelay=67100|67100[v4];[m][v1][v2][v3][v4]amix=inputs=5:duration=first:normalize=0,loudnorm=I=-18:TP=-1.5:LRA=11,aresample=48000[out]" \
 -map 0:v:0 -map '[out]' -c:v copy -c:a aac -b:a 192k -t 76 -movflags +faststart "$output"
