#!/usr/bin/env python3
"""Reproducible 76-second alternative edit; preserves FG01 as an untouched baseline.

Edits use actual video source trims. Extra close shots are explicitly reframings,
not claimed to be newly generated camera angles. No footage is flipped.
"""
from pathlib import Path
import argparse, json, subprocess, hashlib, tempfile
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
C=R.parent
OLD=C/'gpt-full-film-v1'
OPEN=C/'continuity-video-v1/renders/converse-continuity-g-seedance25-30s.mp4'
SHARED=C/'model-comparison-v3/shared/audio'
def run(cmd,**kw):
 return subprocess.run([str(x) for x in cmd],check=True,**kw)
def probe(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def shot(source,start,duration,label,crop=None):
 return dict(source=str(source),start=start,duration=duration,label=label,crop=crop)
def schedule(luna,salsa,phone='phone-attic.mp4'):
 # Three added product/face inserts are crop-based editorial coverage.
 return [
 shot(OPEN,0,10,'Original opening and two dialogue lines'),
 shot(OPEN,10,2.5,'Shoebox discovery'),
 shot(OPEN,12.5,1.5,'Closer photograph insert','crop=iw*0.82:ih*0.82:iw*0.09:ih*0.09'),
 shot(R/'videos'/phone,0,8,'Luna photographs the physical print and asks AI'),
 shot(OPEN,22,2.5,'Luna puts on the inherited pair'),
 shot(OPEN,24.5,1.5,'Lace and canvas detail','crop=iw*0.82:ih*0.82:iw*0.09:ih*0.09'),
 shot(OPEN,26,4,'Shoe-to-court match cut'),
 shot(OLD/'videos/basketball.mp4',0,7,'Rafa shoots; net; smile; landing'),
 shot(OLD/'videos/salsa.mp4',0,1.5,'Black and red shoes meet'),
 shot(R/'videos'/salsa,0,5,'Salsa encounter — selected source'),
 shot(OLD/'videos/salsa.mp4',6.5,1.5,'Footstep out of dance'),
 shot(OLD/'videos/wedding.mp4',0,4,'Wedding doorway'),
 shot(OLD/'videos/newborn.mp4',0,4,'Baby and hand insert'),
 shot(OLD/'videos/handover.mp4',0,5.5,'Gift and lace gesture'),
 shot(OLD/'videos/handover.mp4',5.5,1.25,'Father and daughter smile'),
 shot(OLD/'videos/handover.mp4',6.75,1.25,'Closer daughter reaction','crop=iw*0.84:ih*0.84:iw*0.15:ih*0.06'),
 shot(R/'videos'/luna,0,4,'Luna returns; Mom call bridges the cut'),
 shot(OLD/'videos/return.mp4',4,2,'Luna returns photo to box'),
 shot(OLD/'videos/return.mp4',6,5,'Luna asks Mom; Mom smiles'),
 shot(OLD/'renders/converse-gpt-seedance25-full-76s.mp4',72,4,'Conserve what matters endline')]
def render_picture(shots,output):
 at=0
 with tempfile.TemporaryDirectory(prefix='converse-v4-edit-') as tmp:
  temp=Path(tmp); parts=[]
  for i,s in enumerate(shots):
   path=Path(s['source'])
   if not path.is_file(): raise RuntimeError(f'Missing real source: {path}')
   m=probe(path); duration=float(m['format']['duration'])
   if s['start']+s['duration']>duration+.05: raise RuntimeError(f'Source too short: {path}')
   filters=[]
   if s['crop']:filters.append(s['crop'])
   filters+=['scale=1280:720:flags=lanczos','setsar=1','fps=24']
   dest=temp/f'{i:02}.mp4'
   run(['ffmpeg','-y','-v','error','-ss',s['start'],'-i',path,'-t',s['duration'],'-vf',','.join(filters),'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','12288',dest])
   s['timelineStart']=at; at+=s['duration'];s['timelineEnd']=at;parts.append(dest)
  if at!=76:raise RuntimeError(f'Bad duration {at}')
  f=temp/'concat.txt';f.write_text(''.join("file '"+str(p)+"'\n" for p in parts))
  run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',f,'-c','copy','-movflags','+faststart',output])
 return shots

def mix(music,output,ask=None,reply=None):
 # Deliberate silence around spoken lines; call begins before return to attic.
 inputs=[music,SHARED/'mom-opening.wav',SHARED/'luna-annoyed.wav',SHARED/'mom-return.wav',SHARED/'luna-ending.wav']
 filters=["[0:a]atrim=duration=76,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1,afade=t=out:st=74.6:d=1.4,volume='if(lt(t,9.7),0.20,if(lt(t,10),0.20+0.53*(t-9.7)/0.3,if(lt(t,14.5),0.73,if(lt(t,14.7),0.73-0.57*(t-14.5)/0.2,if(lt(t,21.6),0.16,if(lt(t,21.9),0.16+0.57*(t-21.6)/0.3,if(lt(t,59.9),0.73,if(lt(t,60.2),0.73-0.55*(t-59.9)/0.3,if(lt(t,71.5),0.18,if(lt(t,71.8),0.18+0.55*(t-71.5)/0.3,0.73))))))))))':eval=frame[m]",
 '[1:a]atempo=0.70,highpass=f=130,lowpass=f=6600,aecho=0.8:0.8:45:0.1,volume=1.35,adelay=250|250[v1]',
 '[2:a]atempo=0.72,volume=1.30,adelay=6120|6120[v2]',
 '[3:a]atempo=0.72,highpass=f=130,lowpass=f=6600,aecho=0.8:0.8:45:0.1,volume=1.45,adelay=60200|60200[v3]',
 '[4:a]atempo=0.78,volume=1.35,adelay=67100|67100[v4]']
 labels=['m','v1','v2','v3','v4']
 for p,name,at in [(ask,'ask',14700),(reply,'reply',18700)]:
  if p:
   inputs.append(p);n=len(inputs)-1
   filters.append(f'[{n}:a]aresample=48000,volume=1.25,adelay={at}|{at}[{name}]');labels.append(name)
 filters.append(''.join('['+l+']' for l in labels)+f'amix=inputs={len(labels)}:duration=first:normalize=0,loudnorm=I=-17:TP=-1.5:LRA=9,aresample=48000[out]')
 cmd=['ffmpeg','-y','-v','error']
 for p in inputs:cmd+=['-i',p]
 run(cmd+['-filter_complex',';'.join(filters),'-map','[out]','-t','76','-ac','2','-c:a','pcm_s16le',output])

def sheet(video,out):
 times=[6,11,14.5,16.2,19,21,24.5,29.5,33,36,38,40,43,47,51,54,57,60,63,65.5,68,71,73,75]
 im=Image.new('RGB',(1600,1040),'#23241f');d=ImageDraw.Draw(im)
 with tempfile.TemporaryDirectory() as tmp:
  for i,t in enumerate(times):
   f=Path(tmp)/f'{i}.jpg';run(['ffmpeg','-y','-v','error','-ss',t,'-i',video,'-frames:v','1','-vf','scale=320:180',f])
   x=i%5*320;y=i//5*208;im.paste(Image.open(f),(x,y));d.text((x+5,y+184),f'{t}s',fill='white')
 im.save(out,quality=91)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--luna',default='luna-original.mp4');ap.add_argument('--salsa',default='salsa-original.mp4');ap.add_argument('--phone',default='phone-attic.mp4');ap.add_argument('--music-a',type=Path,required=True);ap.add_argument('--music-b',type=Path,required=True);ap.add_argument('--ask',type=Path);ap.add_argument('--reply',type=Path);a=ap.parse_args()
 for d in ['renders','audio','qa']:(R/d).mkdir(exist_ok=True)
 picture=R/'renders/picture-76s.mp4';shots=render_picture(schedule(a.luna,a.salsa,a.phone),picture)
 report={'status':'experimental-review','baselineUntouched':'../gpt-full-film-v1/renders/converse-gpt-seedance25-full-76s.mp4','durationSeconds':76,'notes':['Three extra inserts are editorial reframings, not newly generated angles.','Face treatments remain in the separate comparison; these soundtrack edits preserve FG01 faces except the new phone take.','Mom call begins 60.2s: sound bridge 0.8s before attic return.','Two score editions share identical encoded picture.'],'shots':shots,'exports':[]}
 for name,music in [('a',a.music_a),('b',a.music_b)]:
  audio=R/'audio'/f'mix-{name}.wav';mix(music,audio,a.ask,a.reply)
  out=R/'renders'/f'converse-refinement-v4-music-{name}-76s.mp4'
  run(['ffmpeg','-y','-v','error','-i',picture,'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','76','-movflags','+faststart',out])
  run(['ffmpeg','-v','error','-i',out,'-f','null','-'])
  m=probe(out);v=next(s for s in m['streams'] if s['codec_type']=='video')
  assert int(v['nb_frames'])==1824 and abs(float(v['duration'])-76)<.01
  volume=subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-af','volumedetect','-vn','-f','null','-'],capture_output=True,text=True,check=True).stderr
  report['exports'].append({'file':str(out.relative_to(R)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'metadata':m,'decodePassed':True,'volume':[l for l in volume.splitlines() if 'mean_volume:' in l or 'max_volume:' in l]})
 sheet(R/'renders/converse-refinement-v4-music-a-76s.mp4',R/'qa/contact-sheet.jpg')
 run(['ffmpeg','-y','-v','error','-ss','19','-i',picture,'-frames:v','1',R/'renders/poster.jpg'])
 (R/'qa/render-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'rendered':[e['file'] for e in report['exports']],'duration':76,'decodePassed':True}))
if __name__=='__main__':main()
