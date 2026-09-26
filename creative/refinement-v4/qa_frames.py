from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,tempfile,json
R=Path(__file__).resolve().parent
for name,duration in [('luna-prompt',5),('salsa-prompt',5),('phone-attic',8),('phone-attic-v2',8),('luna-pro',5),('salsa-pro',5)]:
 src=R/'videos'/f'{name}.mp4'
 if not src.exists():continue
 times=[.1,duration*.2,duration*.4,duration*.6,duration*.8,duration-.15]
 out=Image.new('RGB',(1440,600),'#242620');d=ImageDraw.Draw(out)
 with tempfile.TemporaryDirectory() as tmp:
  for i,t in enumerate(times):
   p=Path(tmp)/f'{i}.png';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=480:270',str(p)],check=True)
   x=i%3*480;y=i//3*300;out.paste(Image.open(p),(x,y));d.text((x+10,y+275),f'{name} {t:.2f}s',fill='white')
 out.save(R/'qa'/f'{name}-sheet.jpg',quality=92)
 subprocess.run(['ffmpeg','-v','error','-i',str(src),'-f','null','-'],check=True)
print('QA frames and full decode complete')
