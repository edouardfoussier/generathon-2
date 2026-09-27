#!/usr/bin/env python3
"""Local scene studio with durable MCP requests and background FAL batches.

FAL uses the existing local Cut Room service; credentials never enter this app.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import contextlib
import copy
import datetime as dt
import fcntl
import hashlib
import importlib.util
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import shutil
import struct
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from urllib.parse import quote, unquote, urlsplit, urlunsplit
import uuid
import zlib

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CREATIVE = REPO / 'creative'
# The shared editor backend imports its sibling modules when loaded by path.
if str(CREATIVE/'editor') not in sys.path:
    sys.path.append(str(CREATIVE/'editor'))
spec = importlib.util.spec_from_file_location('scene_studio_editor_backend', CREATIVE/'editor/server.py')
editor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(editor)
ValidationError = editor.ValidationError

MAX_BODY = 8 * 1024 * 1024
MAX_CAMERA = 5 * 1024 * 1024
MAX_TEXT = 30000
MAX_REFERENCES = 16
MAX_PENDING = 100
ID_RE = re.compile(r'^[a-f0-9]{32}$')
SCENE_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$')
TYPES = {'image','video','revise','scene3d'}
PENDING = {'awaiting_mcp','queued','submitting','running'}
STATIC_EXTENSIONS = editor.STATIC_EXTENSIONS | {'.glb','.gltf','.bin','.mjs'}
REFERENCE_EXTENSIONS = {'.png','.jpg','.jpeg','.webp','.mp4','.webm','.glb','.gltf','.json'}
LOCATIONS = {'attic','basketball','salsa','wedding','nursery','handover','product'}
PROVIDER_HOSTS = frozenset({
    'd8j0ntlcm91z4.cloudfront.net', 'd2ol7oe51mr4n9.cloudfront.net',
    'cdn.higgsfield.ai', 'media.higgsfield.ai', 'assets.higgsfield.ai',
    'cdn.arcads.ai', 'assets.arcads.ai',
})
mimetypes.add_type('model/gltf-binary','.glb')
mimetypes.add_type('model/gltf+json','.gltf')
mimetypes.add_type('application/javascript','.mjs')


class Conflict(RuntimeError):
    pass


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='milliseconds')


def strict_json(data):
    def reject(value):
        raise ValidationError(f'Non-finite JSON number: {value}')
    return json.loads(data, parse_constant=reject)


def canonical_json(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def text_field(value, name, maximum=MAX_TEXT, required=False):
    if value is None and not required:
        return ''
    if not isinstance(value,str) or len(value)>maximum or '\x00' in value:
        raise ValidationError(f'{name} must be text of at most {maximum} characters.')
    if required and not value.strip():
        raise ValidationError(f'{name} cannot be empty.')
    return value.strip()


def safe_creative_path(value, creative=CREATIVE, extensions=None):
    if not isinstance(value,str) or '\\' in value or any(ord(c)<32 for c in value):
        raise ValidationError('Invalid local creative reference.')
    parts=urlsplit(value)
    if parts.scheme or parts.netloc or parts.query or parts.fragment:
        raise ValidationError('Local references must be plain /creative/ URLs.')
    path=parts.path
    for _ in range(4):
        decoded=unquote(path)
        if decoded==path:
            break
        path=decoded
    if not path.startswith('/creative/') or '%' in path or '\\' in path:
        raise ValidationError('Local references must stay under /creative/.')
    relative=Path(path.removeprefix('/creative/'))
    if not relative.parts or any(p.startswith('.') for p in relative.parts):
        raise ValidationError('Hidden paths and traversal are not permitted.')
    candidate=(creative/relative).resolve()
    if not candidate.is_relative_to(creative.resolve()):
        raise ValidationError('The reference escapes the creative directory.')
    if extensions and candidate.suffix.lower() not in extensions:
        raise ValidationError('Unsupported local file type.')
    if not candidate.is_file():
        raise ValidationError('The referenced local file does not exist.')
    return candidate, '/creative/'+quote(relative.as_posix(),safe='/')


def validate_reference(value, creative=CREATIVE, state=None):
    if not isinstance(value,dict) or not set(value)<= {'url','label','id','role'}:
        raise ValidationError('Each reference must contain url and optional label,id,role.')
    url=text_field(value.get('url'),'reference.url',4096,True)
    label=text_field(value.get('label'),'reference.label',200)
    metadata={field:text_field(value[field],'reference.'+field,128)
              for field in ('id','role') if field in value}
    if any(ord(c)<32 for c in url) or '\\' in url:
        raise ValidationError('Invalid reference URL.')
    artifact_match=re.fullmatch(r'/api/studio/jobs/([a-f0-9]{32})/artifact',url)
    if artifact_match:
        if state is None:
            raise ValidationError('Generated reference must belong to this local queue.')
        folder=Path(state)/'jobs'/artifact_match[1]
        try:
            job=strict_json((folder/'job.json').read_text())
            result=job.get('result') or {}
            filename=result.get('filename','')
            artifact=(folder/filename).resolve()
            valid=(job.get('status')=='completed' and job.get('type')=='image'
                   and filename in {'result.png','result.jpg','result.jpeg','result.webp'}
                   and artifact.parent==folder.resolve() and artifact.is_file())
        except (OSError,ValueError,TypeError):
            valid=False
        if not valid:
            raise ValidationError('Generated reference must be a completed image result.')
        return {'url':url,'label':label,'source':'generated',**metadata}
    parsed=urlsplit(url)
    if not parsed.scheme and not parsed.netloc:
        _,url=safe_creative_path(url,creative,REFERENCE_EXTENSIONS)
        return {'url':url,'label':label,'source':'local',**metadata}
    try:
        valid=(parsed.scheme=='https' and parsed.hostname in PROVIDER_HOSTS
               and parsed.port in (None,443) and not parsed.username and not parsed.password)
    except ValueError:
        valid=False
    if not valid:
        raise ValidationError('Remote references must use an approved provider HTTPS host.')
    # No HTTP fetch is made here: URLs are data for the explicitly operated MCP queue.
    url=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,parsed.query,''))
    return {'url':url,'label':label,'source':'provider',**metadata}


def validate_png(raw):
    if len(raw)>MAX_CAMERA or raw[:8]!=b'\x89PNG\r\n\x1a\n':
        raise ValidationError('Camera capture must be a PNG of at most5MiB.')
    position=8; dimensions=None; saw_data=False; saw_end=False
    while position+12<=len(raw):
        length=struct.unpack('>I',raw[position:position+4])[0]
        kind=raw[position+4:position+8]
        end=position+12+length
        if end>len(raw):
            raise ValidationError('Truncated PNG capture.')
        payload=raw[position+8:position+8+length]
        crc=struct.unpack('>I',raw[position+8+length:end])[0]
        if zlib.crc32(kind+payload)&0xffffffff != crc:
            raise ValidationError('Invalid PNG checksum.')
        if dimensions is None:
            if kind!=b'IHDR' or length!=13:
                raise ValidationError('PNG is missing its initial image header.')
            width,height=struct.unpack('>II',payload[:8])
            if not 1<=width<=8192 or not 1<=height<=8192 or width*height>20_000_000:
                raise ValidationError('Camera PNG dimensions are too large.')
            dimensions={'width':width,'height':height}
        if kind==b'IDAT':
            saw_data=True
        if kind==b'IEND':
            if length!=0 or end!=len(raw):
                raise ValidationError('Invalid PNG terminator.')
            saw_end=True
            break
        position=end
    if not dimensions or not saw_data or not saw_end:
        raise ValidationError('Incomplete PNG capture.')
    return dimensions


def validate_payload(payload, creative=CREATIVE, state=None):
    if not isinstance(payload,dict):
        raise ValidationError('Expected a JSON object.')
    allowed={'sceneId','type','prompt','modification','references','blocking','cameraImage','idempotencyKey','duration','target','startingImage'}
    if not set(payload)<=allowed:
        raise ValidationError('Unknown job fields: '+', '.join(sorted(set(payload)-allowed)))
    scene=text_field(payload.get('sceneId'),'sceneId',80,True)
    if not SCENE_RE.fullmatch(scene):
        raise ValidationError('sceneId must be an ordinary scene identifier.')
    kind=payload.get('type')
    if not isinstance(kind,str) or kind not in TYPES:
        raise ValidationError('type must be image,video,revise or scene3d.')
    duration=payload.get('duration')
    if duration is not None and (type(duration) not in (int,float) or
                                not math.isfinite(duration) or not .25<=duration<=30):
        raise ValidationError('duration must be a finite number between0.25and30seconds.')
    prompt=text_field(payload.get('prompt'),'prompt',MAX_TEXT)
    modification=text_field(payload.get('modification'),'modification',12000)
    if not prompt and not modification:
        raise ValidationError('Provide a prompt or modification.')
    references=payload.get('references',[])
    if not isinstance(references,list) or len(references)>MAX_REFERENCES:
        raise ValidationError('references must be a list of at most16 items.')
    refs=[validate_reference(item,creative,state) for item in references]
    starting=payload.get('startingImage')
    if starting is not None:
        starting=validate_reference({'url':starting,'role':'start_frame'},creative,state)
        if starting['source']=='provider':
            raise ValidationError('startingImage must be a local image or a completed studio image.')
        if starting['source']=='local':
            safe_creative_path(starting['url'],creative,{'.png','.jpg','.jpeg','.webp'})
        starting=starting['url']
    target=payload.get('target')
    if target is not None:
        if (kind!='image' or not isinstance(target,dict)
                or not set(target)<={'kind','id','label','scope'}
                or target.get('kind')!='reference' or target.get('scope')!='scene'):
            raise ValidationError('Asset edits must target one reference image in this scene.')
        target_id=text_field(target.get('id'),'target.id',128,True)
        if sum(ref.get('id')==target_id for ref in refs)!=1:
            raise ValidationError('The asset target must match exactly one supplied reference.')
        target={'kind':'reference','id':target_id,'scope':'scene',
                'label':text_field(target.get('label'),'target.label',200)}
    blocking=payload.get('blocking')
    if blocking is not None:
        if not isinstance(blocking,dict):
            raise ValidationError('blocking must be a JSON object.')
        encoded=canonical_json(blocking)
        if len(encoded.encode())>128*1024:
            raise ValidationError('blocking exceeds128KiB.')
        def depth(value,level=0):
            if level>12:
                raise ValidationError('blocking is nested too deeply.')
            if isinstance(value,dict):
                for key,item in value.items():
                    if key in {'__proto__','prototype','constructor'}:
                        raise ValidationError('Unsupported blocking key.')
                    depth(item,level+1)
            elif isinstance(value,list):
                if len(value)>1000:
                    raise ValidationError('blocking contains an oversized list.')
                for item in value:
                    depth(item,level+1)
        depth(blocking)
    camera=None
    if payload.get('cameraImage') is not None:
        capture=payload['cameraImage']
        prefix='data:image/png;base64,'
        if not isinstance(capture,str) or not capture.startswith(prefix):
            raise ValidationError('cameraImage must be a PNG base64 data URL.')
        try:
            camera=base64.b64decode(capture[len(prefix):],validate=True)
        except (ValueError,binascii.Error) as error:
            raise ValidationError('Invalid camera PNG base64.') from error
        dims=validate_png(camera)
        camera_meta={'mimeType':'image/png','bytes':len(camera),
                     'sha256':hashlib.sha256(camera).hexdigest(),**dims}
    else:
        camera_meta=None
    key=payload.get('idempotencyKey')
    if key is not None:
        try:
            key=str(uuid.UUID(key))
        except (ValueError,TypeError,AttributeError) as error:
            raise ValidationError('idempotencyKey must be a UUID.') from error
    request={'schemaVersion':1,'sceneId':scene,'type':kind,'duration':duration,'prompt':prompt,
             'modification':modification,'references':refs,'blocking':copy.deepcopy(blocking),
             'cameraImage':camera_meta,**({'target':target} if target else {}),
             **({'startingImage':starting} if starting else {})}
    return request,camera,key


def atomic_json(path,value):
    temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        with temporary.open('x',encoding='utf-8') as output:
            os.chmod(temporary,0o600)
            output.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
            output.flush(); os.fsync(output.fileno())
        os.replace(temporary,path)
    finally:
        temporary.unlink(missing_ok=True)


def merge_and_validate_blocking(base,patch):
    """Apply a partial AI proposal to the saved scene, then verify renderable data.

    Camera/lighting merge by field. Character/prop arrays replace as whole arrays;
    absence preserves the recorded cast rather than inventing replacement actors.
    """
    if not isinstance(patch,dict) or not isinstance(base or {},dict):
        raise ValidationError('The3D proposal and saved blocking must be JSON objects.')
    allowed={'location','characters','camera','lighting','props','animationSpeed','showGrid'}
    if not set(patch)<=allowed:
        raise ValidationError('Unsupported blocking fields: '+', '.join(sorted(set(patch)-allowed)))
    default={'location':'attic','characters':[],
             'camera':{'position':[6,4,8],'target':[0,1,0],'fov':42},
             'lighting':{'warmth':.6,'intensity':1},'props':[]}
    result=copy.deepcopy(default)
    for changes in (base or {},patch):
        for key,value in changes.items():
            if key in {'camera','lighting'}:
                if not isinstance(value,dict):
                    raise ValidationError(f'blocking.{key} must be an object.')
                result[key]={**result[key],**copy.deepcopy(value)}
            else:
                result[key]=copy.deepcopy(value)
    def finite(value,name,minimum=None,maximum=None):
        if type(value) not in (int,float) or not math.isfinite(value):
            raise ValidationError(f'{name} must be a finite number.')
        if minimum is not None and value<minimum or maximum is not None and value>maximum:
            raise ValidationError(f'{name} is outside its supported range.')
        return value
    def vector(value,name):
        if not isinstance(value,list) or len(value)!=3:
            raise ValidationError(f'{name} must contain exactly3finite coordinates.')
        for item in value: finite(item,name,-10000,10000)
    if not isinstance(result.get('location'),str) or result['location'] not in LOCATIONS:
        raise ValidationError('Unknown3D location.')
    characters=result.get('characters')
    if not isinstance(characters,list) or len(characters)>12:
        raise ValidationError('blocking.characters must contain at most12 characters.')
    ids=set()
    for index,character in enumerate(characters):
        if not isinstance(character,dict):
            raise ValidationError(f'Character{index} must be an object.')
        ident=text_field(character.get('id'),'character.id',100,True)
        text_field(character.get('label'),'character.label',120,True)
        if ident in ids: raise ValidationError('Character ids must be unique.')
        ids.add(ident)
        vector(character.get('position'),'character.position')
        if 'age' in character: finite(character['age'],'character.age',0,120)
        if 'rotation' in character: finite(character['rotation'],'character.rotation')
        if 'scale' in character: finite(character['scale'],'character.scale',.1,5)
    camera=result.get('camera')
    if not isinstance(camera,dict) or not set(camera)<= {'position','target','fov'}:
        raise ValidationError('Camera accepts only position,target,fov.')
    vector(camera.get('position'),'camera.position'); vector(camera.get('target'),'camera.target')
    finite(camera.get('fov'),'camera.fov',10,100)
    lighting=result.get('lighting')
    if not isinstance(lighting,dict) or not set(lighting)<= {'warmth','intensity','exposure'}:
        raise ValidationError('Lighting accepts only warmth,intensity,exposure.')
    finite(lighting.get('warmth'),'lighting.warmth',0,1)
    finite(lighting.get('intensity'),'lighting.intensity',.2,2)
    if 'exposure' in lighting: finite(lighting['exposure'],'lighting.exposure',.25,2.5)
    props=result.get('props',[])
    if not isinstance(props,list) or len(props)>40 or any(not isinstance(p,dict) for p in props):
        raise ValidationError('blocking.props must contain at most40 object definitions.')
    for prop in props:
        if 'position' in prop: vector(prop['position'],'prop.position')
        if 'rotation' in prop: finite(prop['rotation'],'prop.rotation')
        if 'scale' in prop:
            if isinstance(prop['scale'],list): vector(prop['scale'],'prop.scale')
            else: finite(prop['scale'],'prop.scale',.1,5)
    if 'animationSpeed' in result: finite(result['animationSpeed'],'animationSpeed',0,3)
    if 'showGrid' in result and type(result['showGrid']) is not bool:
        raise ValidationError('showGrid must be boolean.')
    return result


class JobStore:
    def __init__(self,state=None,creative=None):
        self.state=Path(state or HERE/'.state').resolve()
        self.creative=Path(creative or CREATIVE).resolve()
        self.jobs_dir=self.state/'jobs'
        self.jobs_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
        os.chmod(self.state,0o700); os.chmod(self.jobs_dir,0o700)
        self.thread_lock=threading.RLock()

    @contextlib.contextmanager
    def locked(self):
        with self.thread_lock:
            with (self.state/'queue.lock').open('a') as lock:
                os.chmod(self.state/'queue.lock',0o600)
                fcntl.flock(lock,fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock,fcntl.LOCK_UN)

    def _dir(self,job_id):
        if not isinstance(job_id,str) or not ID_RE.fullmatch(job_id):
            raise ValidationError('Invalid job identifier.')
        return self.jobs_dir/job_id

    def _read(self,job_id):
        path=self._dir(job_id)/'job.json'
        if not path.is_file():
            return None
        return strict_json(path.read_text())

    def _all(self):
        jobs=[]
        for folder in self.jobs_dir.iterdir():
            if not ID_RE.fullmatch(folder.name) or not folder.is_dir():
                continue
            try:
                item=self._read(folder.name)
            except (OSError,ValueError):
                # Surface corruption without exposing a raw filesystem path.
                item={'id':folder.name,'status':'failed','error':'Persisted job metadata is unreadable.',
                      'createdAt':'','updatedAt':'','recoverable':False}
            if item:
                jobs.append(item)
        return sorted(jobs,key=lambda x:x.get('createdAt',''),reverse=True)

    @staticmethod
    def public(job):
        if job is None:
            return None
        result=copy.deepcopy(job)
        result.pop('requestFingerprint',None)
        result.pop('idempotencyKey',None)
        return result

    def list(self):
        with self.locked():
            return [self.public(job) for job in self._all()]

    def get(self,job_id):
        with self.locked():
            return self.public(self._read(job_id))

    def request(self,job_id):
        with self.locked():
            if not self._read(job_id):
                return None
            return strict_json((self._dir(job_id)/'request.json').read_text())

    def submit(self,payload,header_key=None,execution=None):
        if header_key:
            payload=copy.deepcopy(payload)
            if not isinstance(payload,dict):
                raise ValidationError('Expected a JSON object.')
            if payload.get('idempotencyKey') not in (None,header_key):
                raise ValidationError('Header and payload idempotency keys differ.')
            payload['idempotencyKey']=header_key
        request,camera,key=validate_payload(payload,self.creative,self.state)
        fingerprint=hashlib.sha256(canonical_json(request).encode()).hexdigest()
        with self.locked():
            existing=self._all()
            if key:
                for job in existing:
                    if job.get('idempotencyKey')==key:
                        if job.get('requestFingerprint')!=fingerprint:
                            raise Conflict('This idempotency key already belongs to a different request.')
                        return self.public(job),False
            if sum(job['status'] in PENDING for job in existing)>=MAX_PENDING:
                raise Conflict('The queue has100 pending requests; finish some before adding more.')
            job_id=uuid.uuid4().hex
            timestamp=now()
            canonical={**request,'id':job_id,'createdAt':timestamp,'mode':'mcp_queue',
                       'operatorInstructions':'Use this request in the current authorized conversation; submit through available provider MCP tools, then import the actual result with the local completion CLI.'}
            if camera:
                canonical['cameraImage']={**request['cameraImage'],
                    'path':str(self._dir(job_id)/'camera.png'),
                    'url':f'/api/studio/jobs/{job_id}/camera'}
            job={'id':job_id,'sceneId':request['sceneId'],'type':request['type'],'duration':request['duration'],
                 'status':'awaiting_mcp','mode':'mcp_queue','autonomous':False,
                 'createdAt':timestamp,'updatedAt':timestamp,'progress':None,
                 'prompt':request['prompt'],'modification':request['modification'],
                 'references':request['references'],'blocking':request['blocking'],
                 **({'target':request['target']} if request.get('target') else {}),
                 'cameraImage':canonical['cameraImage'],'requestUrl':f'/api/studio/jobs/{job_id}/request',
                 'message':'Request saved. Generation awaits the MCP conversation; no provider job has been submitted.',
                 'result':None,'error':None,'idempotencyKey':key,'requestFingerprint':fingerprint}
            if execution:
                job.update(copy.deepcopy(execution))
                canonical.update({key:copy.deepcopy(value) for key,value in execution.items()
                                  if key in {'mode','engine','model','batchId','autonomous','startingImage'}})
                if execution.get('engine')=='fal':
                    canonical['operatorInstructions']='Submitted by the background local FAL bridge; never resubmit this request through MCP.'
            # Rename the whole request folder only after both files are durable.
            temporary=Path(tempfile.mkdtemp(prefix='.pending-',dir=self.jobs_dir))
            try:
                if camera:
                    (temporary/'camera.png').write_bytes(camera)
                    os.chmod(temporary/'camera.png',0o600)
                atomic_json(temporary/'request.json',canonical)
                atomic_json(temporary/'job.json',job)
                os.replace(temporary,self._dir(job_id))
            finally:
                if temporary.exists(): shutil.rmtree(temporary)
            return self.public(job),True

    def update_generation(self,job_id,expected_status=None,**changes):
        """Internal durable bridge lifecycle update; never exposed as a write endpoint."""
        with self.locked():
            job=self._read(job_id)
            if not job: raise ValidationError('Job not found.')
            if expected_status is not None and job['status']!=expected_status:
                return None
            if job['status']=='completed': return self.public(job)
            job.update(copy.deepcopy(changes),updatedAt=now())
            atomic_json(self._dir(job_id)/'job.json',job)
            return self.public(job)

    def mark_running(self,job_id,provider,provider_job_id):
        provider=text_field(provider,'provider',100,True)
        provider_job_id=text_field(provider_job_id,'providerJobId',200,True)
        with self.locked():
            job=self._read(job_id)
            if not job: raise ValidationError('Job not found.')
            if job['status']=='running' and job.get('providerJobId')==provider_job_id:
                return self.public(job)
            if job['status']!='awaiting_mcp': raise Conflict('Only waiting jobs can be marked running.')
            job.update(status='running',provider=provider,providerJobId=provider_job_id,
                       updatedAt=now(),message='A provider job was submitted by the MCP operator. Awaiting its actual output.')
            atomic_json(self._dir(job_id)/'job.json',job)
            return self.public(job)

    def fail(self,job_id,message):
        message=text_field(message,'error',2000,True)
        with self.locked():
            job=self._read(job_id)
            if not job: raise ValidationError('Job not found.')
            if job['status']=='completed': raise Conflict('A completed result cannot be replaced by an error.')
            job.update(status='failed',error=message,message=message,updatedAt=now(),progress=None)
            atomic_json(self._dir(job_id)/'job.json',job)
            return self.public(job)

    def complete(self,job_id,artifact,provider=None,provider_job_id=None):
        # Import only a real local creative artifact. No remote fetch, redirect,
        # credentials or SSRF surface is needed to complete a generation.
        artifact=Path(artifact).resolve()
        if not artifact.is_relative_to(self.creative) or not artifact.is_file():
            raise ValidationError('Completion requires an existing file inside creative/.')
        relative=artifact.relative_to(self.creative)
        if any(part.startswith('.') for part in relative.parts):
            raise ValidationError('Cannot import hidden paths as generation results.')
        size=artifact.stat().st_size
        if not 0<size<=512*1024*1024:
            raise ValidationError('Result must be a nonempty file of at most512MiB.')
        with self.locked():
            job=self._read(job_id)
            if not job: raise ValidationError('Job not found.')
            kind=job['type']; suffix=artifact.suffix.lower()
            extra={}
            with artifact.open('rb') as source:
                head=source.read(16)
            if kind=='image':
                good=(suffix=='.png' and head.startswith(b'\x89PNG\r\n\x1a\n') or
                      suffix in {'.jpg','.jpeg'} and head.startswith(b'\xff\xd8\xff') or
                      suffix=='.webp' and head[:4]==b'RIFF' and head[8:12]==b'WEBP')
                if not good: raise ValidationError('Image result must be a PNG,JPEG or WebP file with its proper signature.')
            elif kind=='video':
                good=(suffix=='.mp4' and head[4:8]==b'ftyp' or
                      suffix=='.webm' and head.startswith(b'\x1a\x45\xdf\xa3'))
                if not good: raise ValidationError('Video result must be an MP4 or WebM file with its proper signature.')
            else:
                if size>256*1024: raise ValidationError('Text and3D JSON results must be at most256KiB.')
                if kind=='scene3d':
                    if suffix!='.json': raise ValidationError('scene3d result must be JSON.')
                    data=strict_json(artifact.read_text())
                    if not isinstance(data,dict): raise ValidationError('scene3d result must be an object.')
                    proposal=data.get('blocking',data)
                    if not isinstance(proposal,dict): raise ValidationError('blocking result must be an object.')
                    validate_payload({'sceneId':job['sceneId'],'type':'scene3d','prompt':'result validation','blocking':proposal},self.creative)
                    extra['blocking']=merge_and_validate_blocking(job.get('blocking'),proposal)
                else:
                    if suffix=='.json':
                        data=strict_json(artifact.read_text())
                        if not isinstance(data,dict): raise ValidationError('Revision JSON must be an object.')
                        result_text=data.get('prompt',data.get('text'))
                    elif suffix=='.txt': result_text=artifact.read_text()
                    else: raise ValidationError('Revision result must be UTF-8 text or JSON.')
                    extra['text']=text_field(result_text,'result text',MAX_TEXT,True)
                    extra['prompt']=extra['text']
            hasher=hashlib.sha256()
            with artifact.open('rb') as source:
                for chunk in iter(lambda:source.read(1024*1024),b''):
                    hasher.update(chunk)
            digest=hasher.hexdigest()
            if job['status']=='completed':
                if job.get('result',{}).get('sha256')==digest: return self.public(job)
                raise Conflict('This job already has a different completed result.')
            target=self._dir(job_id)/('result'+suffix)
            temporary=target.with_name('.result-'+uuid.uuid4().hex+suffix)
            try:
                shutil.copyfile(artifact,temporary); os.chmod(temporary,0o600)
                os.replace(temporary,target)
            finally:
                temporary.unlink(missing_ok=True)
            result={'url':f'/api/studio/jobs/{job_id}/artifact','kind':kind,
                    'filename':target.name,'bytes':size,'sha256':digest,
                    'mimeType':mimetypes.guess_type(target.name)[0] or 'application/octet-stream',**extra}
            job.update(status='completed',result=result,updatedAt=now(),progress=100,error=None,
                       message='Actual generated result imported from a verified local file.')
            if provider: job['provider']=text_field(provider,'provider',100,True)
            if provider_job_id: job['providerJobId']=text_field(provider_job_id,'providerJobId',200,True)
            atomic_json(self._dir(job_id)/'job.json',job)
            return self.public(job)


class StudioServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,store=None,bridge=None,batch_autostart=True):
        self.store=store or JobStore()
        from batch_generation import BatchManager
        self.batches=BatchManager(self.store,validate_payload,atomic_json,canonical_json,Conflict,
                                  bridge=bridge,autostart=batch_autostart)
        from scene_library import SceneLibrary
        self.scene_library=SceneLibrary(self.store,atomic_json)
        # Retain the original project's read-only project/media routes.
        self.manager=editor.ExportManager()
        super().__init__(address,StudioHandler)


    def server_close(self):
        self.batches.close()
        super().server_close()


class StudioHandler(editor.EditorHandler):
    server_version='ConverseSceneStudio/1.0'

    def _check_request(self):
        hosts=self.headers.get_all('Host',[])
        if len(hosts)!=1 or self.headers.get('Sec-Fetch-Site')=='cross-site':
            self.close_connection=True
            self._json(403,{'error':'Only same-origin local requests are accepted.'})
            return False
        if not super()._check_request(): return False
        host=self.headers.get('Host','')
        if host not in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}',f'[::1]:{self.server.server_port}'}:
            self.close_connection=True
            self._json(403,{'error':'Invalid local Host header.'})
            return False
        return True

    def _resolve_file(self,path):
        if path in {'/studio','/studio/','/'}: return HERE/'index.html',False
        if path.startswith('/studio/'):
            path='/creative/scene-studio/'+path.removeprefix('/studio/')
        elif not path.startswith(('/creative/','/media/','/exports/')):
            path='/creative/scene-studio/'+path.lstrip('/')
        if path.startswith('/creative/'):
            try:
                file,_=safe_creative_path(path,self.server.store.creative,STATIC_EXTENSIONS)
                return file,False
            except ValidationError:
                return None,False
        return super()._resolve_file(path)

    def do_GET(self):
        path=unquote(urlsplit(self.path).path)
        if not path.startswith('/api/studio/'):
            return super().do_GET()
        if not self._check_request(): return
        try:
            store=self.server.store
            if path=='/api/studio/library':
                self._json(200,self.server.scene_library.snapshot()); return
            poster=re.fullmatch(r'/api/studio/library/(m_[a-f0-9]{20}|studio_[a-f0-9]{32})/poster',path)
            if poster:
                file=self.server.scene_library.poster(poster[1])
                if file: self._serve_file(file)
                else: self._json(404,{'error':'Poster unavailable.'})
                return
            if path=='/api/studio/generation-config':
                self._json(200,self.server.batches.config()); return
            if path=='/api/studio/status':
                jobs=store.list(); pending=[j for j in jobs if j['status'] in PENDING]
                self._json(200,{'mode':'mcp_queue','available':True,'autonomous':False,
                    'providerConfigured':False,'pendingJobs':len(pending),'pendingjobs':len(pending),
                    'pending':pending,'supportedTypes':sorted(TYPES),'maxBodyBytes':MAX_BODY,
                    'message':'Requests are saved locally. This conversation must run the MCP generation and import the real result; the website does not generate autonomously.'})
                return
            if path=='/api/studio/jobs':
                jobs=store.list()
                self._json(200,{'jobs':jobs,'pendingJobs':sum(j['status'] in PENDING for j in jobs)})
                return
            match=re.fullmatch(r'/api/studio/jobs/([a-f0-9]{32})(?:/(request|camera|artifact))?',path)
            if not match:
                self._json(404,{'error':'Unknown studio route.'}); return
            job_id,sub=match.groups(); job=store.get(job_id)
            if not job: self._json(404,{'error':'Job not found.'}); return
            if sub=='request': self._json(200,store.request(job_id)); return
            if sub in {'camera','artifact'}:
                name='camera.png' if sub=='camera' and job.get('cameraImage') else None
                if sub=='artifact' and job['status']=='completed': name=job['result']['filename']
                if not name: self._json(404,{'error':'Artifact is not available.'}); return
                if Path(name).name!=name or name.startswith('.'):
                    self._json(404,{'error':'Invalid stored artifact.'}); return
                file=(store._dir(job_id)/name).resolve()
                if not file.is_relative_to(store._dir(job_id).resolve()):
                    self._json(404,{'error':'Invalid stored artifact.'}); return
                if not file.is_file(): self._json(404,{'error':'Artifact file is missing.'}); return
                self._serve_file(file); return
            self._json(200,job)
        except (BrokenPipeError,ConnectionResetError): pass
        except (ValueError,OSError) as error: self._json(400,{'error':str(error)})

    def do_POST(self):
        if not self._check_request(): return
        route=urlsplit(self.path).path
        if route not in {'/api/studio/jobs','/api/studio/batch','/api/studio/library/refresh','/api/studio/library/assignment'}:
            self.close_connection=True; self._json(404,{'error':'Unknown studio write route.'}); return
        if self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length',[]))!=1:
            self.close_connection=True; self._json(400,{'error':'Send one explicit Content-Length; chunked bodies are unsupported.'}); return
        if self.headers.get('Content-Type','').split(';',1)[0].strip()!='application/json':
            self.close_connection=True; self._json(415,{'error':'Send application/json.'}); return
        try: length=int(self.headers.get('Content-Length','0'))
        except ValueError: length=-1
        if not 0<length<=MAX_BODY:
            self.close_connection=True; self._json(413,{'error':'JSON body must be1byte to8MiB.'}); return
        try:
            self.connection.settimeout(15)
            data=self.rfile.read(length)
            if len(data)!=length: raise ValidationError('Incomplete request body.')
            if route=='/api/studio/library/refresh':
                if strict_json(data)!={}: raise ValidationError('Send an empty JSON object.')
                self._json(200,self.server.scene_library.snapshot(refresh=True))
            elif route=='/api/studio/library/assignment':
                self._json(200,self.server.scene_library.assign(strict_json(data)))
            elif route=='/api/studio/batch':
                batch,created=self.server.batches.submit(strict_json(data),self.headers.get('Idempotency-Key'))
                self._json(202 if created else 200,batch)
            else:
                job,created=self.server.store.submit(strict_json(data),self.headers.get('Idempotency-Key'))
                self._json(202 if created else 200,job)
        except Conflict as error: self._json(409,{'error':str(error)})
        except (ValueError,UnicodeError,RecursionError) as error: self._json(400,{'error':str(error)[:1000]})
        except OSError: self._json(503,{'error':'The local data could not be saved. No generation was submitted.'})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir',type=Path,default=HERE/'.state')
    sub=parser.add_subparsers(dest='command')
    serve=sub.add_parser('serve'); serve.add_argument('--port',type=int,default=8789)
    sub.add_parser('list')
    req=sub.add_parser('request'); req.add_argument('id')
    running=sub.add_parser('mark-running'); running.add_argument('id')
    running.add_argument('--provider',required=True); running.add_argument('--provider-job-id',required=True)
    complete=sub.add_parser('complete'); complete.add_argument('id')
    complete.add_argument('--artifact',type=Path,required=True)
    complete.add_argument('--provider'); complete.add_argument('--provider-job-id')
    failure=sub.add_parser('fail'); failure.add_argument('id'); failure.add_argument('--error',required=True)
    args=parser.parse_args()
    store=JobStore(args.state_dir)
    try:
        if args.command in (None,'serve'):
            port=getattr(args,'port',8789)
            if not 1<=port<=65535: parser.error('Port must be1–65535.')
            http=StudioServer(('127.0.0.1',port),store)
            print(f'Scene studio: http://127.0.0.1:{port}/studio',flush=True)
            print('Persistent MCP requests + background FAL batches through local Cut Room on port8787.',flush=True)
            try: http.serve_forever()
            except KeyboardInterrupt: pass
            finally: http.server_close()
            return
        if args.command=='list': result=store.list()
        elif args.command=='request': result=store.request(args.id)
        elif args.command=='mark-running': result=store.mark_running(args.id,args.provider,args.provider_job_id)
        elif args.command=='complete': result=store.complete(args.id,args.artifact,args.provider,args.provider_job_id)
        else: result=store.fail(args.id,args.error)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValidationError,Conflict,OSError) as error:
        parser.exit(2,str(error)+'\n')


if __name__=='__main__': main()
