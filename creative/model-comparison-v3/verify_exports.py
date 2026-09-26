"""Measured export checks and contact sheets; not a substitute for full playback."""
import concurrent.futures,json,pathlib,re,subprocess,tempfile
from PIL import Image,ImageDraw
BASE=pathlib.Path(__file__).resolve().parent
TIMES=[.5,3,8,12,16,19,24,27.5,30.5,33,35,37.5,42,49,53,59,64,68,70.5,74]
def verify(model):
    file=BASE/'renders'/('converse-v3-'+model+'.mp4')
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(file)]))
    v=next(s for s in meta['streams'] if s['codec_type']=='video')
    a=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert abs(float(meta['format']['duration'])-76)<.001
    assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'24/1')
    assert int(meta['format']['size'])<95*1048576
    decode=subprocess.run(['ffmpeg','-v','warning','-i',str(file),'-f','null','-'],capture_output=True,text=True)
    assert decode.returncode==0,decode.stderr
    (BASE/'renders'/(model+'-decode.log')).write_text(decode.stderr)
    measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(file),'-vf','blackdetect=d=0.08:pix_th=0.04','-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True)
    lines=[l for l in measure.stderr.splitlines() if 'black_start' in l or 'mean_volume' in l or 'max_volume' in l]
    canvas=Image.new('RGB',(1600,1250),'#161714');draw=ImageDraw.Draw(canvas)
    with tempfile.TemporaryDirectory(prefix='converse-v3-qa-') as temp:
        for i,t in enumerate(TIMES):
            f=pathlib.Path(temp)/(str(i)+'.jpg')
            subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(file),'-frames:v','1','-update','1','-y',str(f)],check=True)
            im=Image.open(f);im.thumbnail((394,220));x=i%4*400;y=i//4*250
            canvas.paste(im,(x,y+25));draw.text((x+6,y+5),str(t)+' sec',fill='white')
        canvas.save(BASE/'renders'/(model+'-contact-sheet.jpg'),quality=88)
    subprocess.run(['ffmpeg','-v','error','-ss','74','-i',str(file),'-frames:v','1','-update','1','-y',str(BASE/'renders'/(model+'-cover.jpg'))],check=True)
    return {'model':model,'duration':float(meta['format']['duration']),'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'videoCodec':v['codec_name'],'audioCodec':a['codec_name'],'audioSampleRate':a['sample_rate'],'sizeBytes':int(meta['format']['size']),'decodeExitCode':decode.returncode,'decodeWarnings':decode.stderr,'blackAndAudioMeasurements':lines,'sampleTimes':TIMES}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(verify,['seedance25','kling3','veo31']))
    (BASE/'renders'/'qa-report.json').write_text(json.dumps({'method':'Full decode and metadata checks;20 sampled final frames/model plus unit source review. Does not claim full normal-speed perceptual playback or listening.','results':results},indent=2))
    print(json.dumps(results,indent=2))
