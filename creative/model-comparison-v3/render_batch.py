"""Remote Higgsfield renderer. Input manifests and upload credentials stay outside repo."""
import concurrent.futures,json,os,pathlib,subprocess,time,urllib.request,zipfile
ROOT=pathlib.Path('/home/user/converse-v3')
deadline=time.time()+780
def wait_for(p):
    while not p.exists():
        if time.time()>deadline:raise TimeoutError(str(p))
        time.sleep(2)
def run(cmd,**kw):return subprocess.run(cmd,check=True,**kw)
def download(item):
    dst=ROOT/item['file'];dst.parent.mkdir(parents=True,exist_ok=True)
    run(['curl','-fsSL','--retry','2',item['url'],'-o',str(dst)])
def upload(file,record):
    result=subprocess.check_output(['curl','-f','-sS','-X','PUT','-H','Content-Type: '+record['content_type'],'--upload-file',str(file),record['upload_url'],'-w','%{http_code}'],text=True)
    print('UPLOAD',file.name,result,flush=True)
    if not result.endswith('200'):raise RuntimeError('Upload failed: '+file.name)
def load_parts(prefix):
    files=sorted(ROOT.glob(prefix+'-*.json'))
    return [item for p in files for item in json.load(open(p))]
wait_for(ROOT/'shared-ready')
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(download,load_parts('shared-input')))
exports=json.load(open(ROOT/'exports-private.json'))
proof=None
for model in ['kling3','veo31','seedance25']:
    wait_for(ROOT/(model+'-ready'))
    items=load_parts(model+'-input')
    # Manifests must use each selected shot-map file, including correction suffixes.
    if len(items)!=17:raise ValueError('Expected17 sources for '+model)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(download,items))
    env=dict(os.environ,CONVERSE_MODEL=model,CONVERSE_WORK=str(ROOT))
    print('RENDER START',model,flush=True)
    run(['higgsedit','build',str(ROOT/'edit.js')],env=env)
    out=ROOT/model/'renders'
    run(['sh',str(ROOT/'mix_audio.sh'),str(out/'picture-only.mp4'),str(ROOT/'shared/audio'),str(out/('converse-v3-'+model+'.mp4'))])
    metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(out/('converse-v3-'+model+'.mp4'))]))
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2))
    upload(out/('converse-v3-'+model+'.mp4'),exports[model])
    if proof is None:
        proof=out/'phone-proof.png';upload(proof,exports['phone-proof'])
    print('RENDER COMPLETE',model,flush=True)
archive=ROOT/'converse-v3-proofs-and-recipes.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in ['edit.js','mix_audio.sh','render_batch.py']:z.write(ROOT/file,file)
    for model in ['kling3','veo31','seedance25']:
        z.write(ROOT/model/'timeline.json',model+'/timeline.json')
        for name in ['phone-proof.png','cover.png','metadata.json','native-render-report.json']:
            z.write(ROOT/model/'renders'/name,model+'/'+name)
upload(archive,exports['archive'])
print('ALL COMPLETE',flush=True)
