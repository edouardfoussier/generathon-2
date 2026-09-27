#!/usr/bin/env python3
"""Local queue, restart, idempotency and HTTP boundary tests; no provider calls."""
import base64
import concurrent.futures
import http.client
import json
from pathlib import Path
import struct
import tempfile
import threading
import unittest
import uuid
import zlib

import server


def png():
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+
            chunk(b'IDAT',zlib.compress(b'\x00\xff\x00\x00'))+chunk(b'IEND',b''))


def payload(**changes):
    return {'sceneId':'C02','type':'image','prompt':'A natural hopscotch step.',
            'modification':'Keep the original shoes.','references':[],
            'blocking':{'location':'attic','characters':[{'id':'luna','label':'Luna','position':[0,0,0]}],
                        'camera':{'position':[1,1,3],'target':[0,1,0],'fov':42},
                        'lighting':{'warmth':.6,'intensity':1}},**changes}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.creative=self.root/'creative'
        self.creative.mkdir()
        self.assets=self.creative/'assets'; self.assets.mkdir()
        self.image=self.assets/'real.png'; self.image.write_bytes(png())
        self.state=self.root/'state'
        self.store=server.JobStore(self.state,self.creative)

    def tearDown(self):
        self.temp.cleanup()


class ValidationTests(Fixture):
    def test_preserves_duration_and_reference_roles_for_frontend_contract(self):
        job,_=self.store.submit(payload(duration=6.25,references=[{
            'id':'primary-1958','label':'Départ','url':'/creative/assets/real.png','role':'start_frame'}]))
        request=self.store.request(job['id'])
        self.assertEqual(job['duration'],6.25)
        self.assertEqual(request['duration'],6.25)
        self.assertEqual(request['references'][0]['id'],'primary-1958')
        self.assertEqual(request['references'][0]['role'],'start_frame')
        for duration in (True,0,30.1,'6',float('nan')):
            with self.subTest(duration=duration),self.assertRaises(ValueError):
                server.validate_payload(payload(duration=duration),self.creative)

    def test_accepts_local_provider_reference_and_png_without_fetch(self):
        data=payload(references=[{'url':'/creative/assets/real.png','label':'Hero'},
                {'url':'https://d8j0ntlcm91z4.cloudfront.net/generated.png','label':'Generated'}],
                cameraImage='data:image/png;base64,'+base64.b64encode(png()).decode())
        request,camera,key=server.validate_payload(data,self.creative)
        self.assertEqual(camera,png())
        self.assertEqual(request['cameraImage']['width'],1)
        self.assertEqual(request['references'][0]['source'],'local')
        self.assertIsNone(key)

    def test_rejects_ssrf_hosts_traversal_symlinks_and_hidden_paths(self):
        outside=self.root/'outside.png'; outside.write_bytes(png())
        (self.assets/'link.png').symlink_to(outside)
        for url in ['http://127.0.0.1:8789/a.png','https://127.0.0.1/a.png',
                    'file:///etc/passwd','https://d8j0ntlcm91z4.cloudfront.net.evil.test/a.png',
                    'https://user:pass@d8j0ntlcm91z4.cloudfront.net/a.png',
                    'https://d8j0ntlcm91z4.cloudfront.net:444/a.png',
                    '//d8j0ntlcm91z4.cloudfront.net/a.png','/creative/assets/link.png',
                    '/creative/../outside.png','/creative/%252e%252e/outside.png',
                    '/creative/.state/secrets.json','/creative/assets/real.png?x=1',
                    '/creative/assets/missing.png']:
            with self.subTest(url=url),self.assertRaises(ValueError):
                server.validate_payload(payload(references=[{'url':url}]),self.creative)

    def test_rejects_invalid_types_and_png(self):
        bad=[{'sceneId':'../C02'},{'type':[]},{'type':'unknown'},{'prompt':'','modification':''},
             {'references':'no'},{'references':[{}]*17},{'blocking':[]},
             {'blocking':{'__proto__':{}}},{'idempotencyKey':'repeat-me'},
             {'cameraImage':'data:image/jpeg;base64,'+base64.b64encode(png()).decode()},
             {'cameraImage':'data:image/png;base64,AAAA'},
             {'cameraImage':'data:image/png;base64,'+base64.b64encode(png()[:-1]).decode()},
             {'cameraImage':'data:image/png;base64,***'}]
        for changes in bad:
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                server.validate_payload(payload(**changes),self.creative)
        with self.assertRaises(ValueError):
            server.strict_json('{"bad":NaN}')


class AssetTests(Fixture):
    def test_single_reference_scope_and_persistence(self):
        ref={'id':'shoe','label':'Shoes','role':'product','url':'/creative/assets/real.png'}
        target={'kind':'reference','id':'shoe','scope':'scene','label':'Shoes'}
        job,_=self.store.submit(payload(references=[ref],target=target))
        self.assertEqual(job['target'],target)
        self.assertEqual(server.JobStore(self.state,self.creative).request(job['id'])['target'],target)
        for changes in ({'type':'video'}, {'target':{**target,'scope':'all'}},
                        {'target':{**target,'id':'unknown'}}, {'references':[ref,ref]}):
            data=payload(references=[ref],target=target);data.update(changes)
            with self.subTest(changes=changes),self.assertRaises(ValueError):
                self.store.submit(data)

    def test_completed_asset_can_be_reused_but_pending_or_missing_cannot(self):
        original,_=self.store.submit(payload())
        url=f"/api/studio/jobs/{original['id']}/artifact"
        request=payload(references=[{'id':'shoe','url':url}])
        with self.assertRaises(ValueError): self.store.submit(request)
        self.store.complete(original['id'],self.image)
        next_job,_=self.store.submit(request)
        self.assertEqual(next_job['references'][0]['source'],'generated')
        with self.assertRaises(ValueError):
            self.store.submit(payload(references=[{'url':'/api/studio/jobs/'+('f'*32)+'/artifact'}]))
        (self.state/'jobs'/original['id']/'result.png').unlink()
        with self.assertRaises(ValueError): self.store.submit(request)


class QueueTests(Fixture):
    def test_persistence_canonical_request_and_no_fake_generation(self):
        capture='data:image/png;base64,'+base64.b64encode(png()).decode()
        job,created=self.store.submit(payload(cameraImage=capture))
        self.assertTrue(created)
        self.assertEqual(job['status'],'awaiting_mcp')
        self.assertFalse(job['autonomous'])
        self.assertIsNone(job['result'])
        self.assertIsNone(job['progress'])
        restart=server.JobStore(self.state,self.creative)
        self.assertEqual(restart.get(job['id']),job)
        request=restart.request(job['id'])
        self.assertEqual(Path(request['cameraImage']['path']).read_bytes(),png())
        self.assertNotIn('base64',json.dumps(request))
        self.assertTrue((self.state/'jobs'/job['id']/'request.json').is_file())

    def test_uuid_idempotency_survives_restart_and_detects_different_request(self):
        data=payload(idempotencyKey=str(uuid.uuid4()))
        first,created=self.store.submit(data)
        second,created=server.JobStore(self.state,self.creative).submit(data)
        self.assertFalse(created); self.assertEqual(first['id'],second['id'])
        with self.assertRaises(server.Conflict):
            self.store.submit({**data,'prompt':'Different'})
        self.assertEqual(len(self.store.list()),1)

    def test_concurrent_retries_create_one_job(self):
        key=str(uuid.uuid4())
        second=server.JobStore(self.state,self.creative)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(lambda i:(self.store if i%2 else second).submit(payload(idempotencyKey=key)),range(16)))
        self.assertEqual(len({x[0]['id'] for x in results}),1)
        self.assertEqual(sum(x[1] for x in results),1)

    def test_real_import_and_running_state_survive_restart(self):
        job,_=self.store.submit(payload())
        running=self.store.mark_running(job['id'],'higgsfield','actual-provider-job-id')
        self.assertEqual(running['status'],'running')
        self.assertEqual(server.JobStore(self.state,self.creative).get(job['id'])['status'],'running')
        done=self.store.complete(job['id'],self.image)
        self.assertEqual(done['status'],'completed')
        self.assertEqual(done['result']['bytes'],len(png()))
        self.assertEqual((self.state/'jobs'/job['id']/'result.png').read_bytes(),png())
        self.assertEqual(self.store.complete(job['id'],self.image),done)
        with self.assertRaises(server.Conflict): self.store.fail(job['id'],'Cannot overwrite completed.')

    def test_completion_rejects_missing_remote_wrong_type_and_hidden_files(self):
        job,_=self.store.submit(payload())
        invalid=self.assets/'bad.png'; invalid.write_text('This is not a generated image.')
        hidden=self.creative/'.hidden.png'; hidden.write_bytes(png())
        for path in [self.assets/'missing.png',invalid,hidden,Path('https://example.com/image.png')]:
            with self.subTest(path=path),self.assertRaises(ValueError):
                self.store.complete(job['id'],path)
        self.assertEqual(self.store.get(job['id'])['status'],'awaiting_mcp')

    def test_revision_and_3d_results_are_actual_local_json(self):
        revision=self.assets/'revision.json'; revision.write_text(json.dumps({'prompt':'A revised natural step.'}))
        job,_=self.store.submit(payload(type='revise'))
        result=self.store.complete(job['id'],revision)['result']
        self.assertEqual(result['prompt'],'A revised natural step.')
        blocking=self.assets/'blocking.json'; blocking.write_text(json.dumps({'camera':{'position':[2,1,3]}}))
        job,_=self.store.submit(payload(type='scene3d'))
        result=self.store.complete(job['id'],blocking)['result']
        self.assertEqual(result['blocking']['camera']['position'],[2,1,3])
        self.assertEqual(result['blocking']['characters'][0]['id'],'luna')
        self.assertEqual(result['blocking']['lighting']['intensity'],1)

    def test_scene3d_completion_rejects_malformed_render_data_without_marking_done(self):
        job,_=self.store.submit(payload(type='scene3d'))
        result_file=self.assets/'invalid-blocking.json'
        invalid=[{'characters':[None]}, {'characters':[{'id':'luna','label':'Luna','position':'bad'}]},
                 {'characters':[{'id':str(i),'label':'X','position':[0,0,0]} for i in range(13)]},
                 {'camera':{'position':[0,1]}},{'camera':{'fov':101}},{'camera':{'x':2}},
                 {'lighting':{'intensity':.1}},{'lighting':{'warmth':1.2}},
                 {'location':'unknown'},{'props':[None]}]
        for proposal in invalid:
            result_file.write_text(json.dumps(proposal))
            with self.subTest(proposal=proposal),self.assertRaises(ValueError):
                self.store.complete(job['id'],result_file)
            self.assertEqual(self.store.get(job['id'])['status'],'awaiting_mcp')

    def test_failure_is_explicit_and_queue_recovery_does_not_reenqueue(self):
        job,_=self.store.submit(payload(idempotencyKey=str(uuid.uuid4())))
        failed=self.store.fail(job['id'],'Provider rejected the request before output.')
        self.assertEqual(failed['status'],'failed')
        self.assertIsNone(failed['result'])
        self.assertEqual(server.JobStore(self.state,self.creative).get(job['id'])['error'],failed['error'])


class QuietHandler(server.StudioHandler):
    def log_message(self,*args): pass


class HTTPTests(Fixture):
    def setUp(self):
        super().setUp()
        self.web=self.creative/'scene-studio'; self.web.mkdir()
        (self.web/'index.html').write_text('<!doctype html><title>Test studio</title>')
        self.binary=self.assets/'scene.glb'; self.binary.write_bytes(b'glTF'+bytes(range(100)))
        self.http=server.StudioServer(('127.0.0.1',0),self.store)
        self.http.RequestHandlerClass=QuietHandler
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.http.shutdown(); self.http.server_close()
        super().tearDown()

    def request(self,method,path,body=None,headers=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.http.server_port,timeout=5)
        connection.request(method,path,body=body,headers=headers or {})
        response=connection.getresponse()
        result=response.status,dict(response.headers),response.read()
        connection.close()
        return result

    def post(self,data,headers=None):
        return self.request('POST','/api/studio/jobs',json.dumps(data),{'Content-Type':'application/json',**(headers or {})})

    def test_status_jobs_request_and_retry_contract(self):
        status,_,body=self.request('GET','/api/studio/status')
        data=json.loads(body)
        self.assertEqual(status,200); self.assertEqual(data['mode'],'mcp_queue')
        self.assertTrue(data['available']); self.assertFalse(data['autonomous'])
        key=str(uuid.uuid4())
        status,_,body=self.post(payload(),{'Idempotency-Key':key})
        self.assertEqual(status,202); job=json.loads(body)
        self.assertEqual(self.post(payload(),{'Idempotency-Key':key})[0],200)
        self.assertEqual(self.post(payload(prompt='new'),{'Idempotency-Key':key})[0],409)
        status,_,body=self.request('GET',job['requestUrl'])
        self.assertEqual(status,200); self.assertEqual(json.loads(body)['sceneId'],'C02')
        self.assertNotIn('idempotencyKey',json.loads(body))
        self.assertEqual(json.loads(self.request('GET','/api/studio/jobs')[2])['pendingJobs'],1)
        self.assertEqual(json.loads(self.request('GET','/api/studio/status')[2])['pending'][0]['requestUrl'],job['requestUrl'])

    def test_glb_static_range_camera_and_completed_artifact(self):
        status,headers,body=self.request('GET','/creative/assets/scene.glb',headers={'Range':'bytes=4-9'})
        self.assertEqual(status,206); self.assertEqual(body,bytes(range(6)))
        self.assertEqual(headers['Content-Type'],'model/gltf-binary')
        self.assertEqual(self.request('HEAD','/creative/assets/scene.glb',headers={'Range':'bytes=-2'})[2],b'')
        self.assertEqual(self.request('GET','/creative/assets/scene.glb',headers={'Range':'bytes=999-'})[0],416)
        capture='data:image/png;base64,'+base64.b64encode(png()).decode()
        job=json.loads(self.post(payload(cameraImage=capture))[2])
        self.assertEqual(self.request('GET',job['cameraImage']['url'])[2],png())
        done=self.store.complete(job['id'],self.image)
        self.assertEqual(self.request('GET',done['result']['url'])[2],png())

    def test_host_origin_path_and_body_guards(self):
        for headers in [{'Host':'evil.test'},{'Origin':'https://evil.test'},
                        {'Sec-Fetch-Site':'cross-site'},
                        {'Host':f'127.0.0.1:{self.http.server_port}/evil'}]:
            self.assertEqual(self.request('GET','/api/studio/status',headers=headers)[0],403)
        for path in ['/creative/%2e%2e/outside.json','/creative/%252e%252e/outside.json',
                     '/creative/scene-studio/.state/jobs/a/request.json','/creative/editor/server.py',
                     '/api/studio/jobs/../../secrets','/api/studio/jobs/'+('0'*32)]:
            self.assertEqual(self.request('GET',path)[0],404,path)
        self.assertEqual(self.request('POST','/api/studio/jobs','{}',{'Content-Type':'text/plain'})[0],415)
        self.assertEqual(self.request('POST','/api/studio/jobs','{}',{'Content-Type':'application/json','Content-Length':str(server.MAX_BODY+1)})[0],413)
        self.assertEqual(self.request('POST','/api/studio/jobs','{',{'Content-Type':'application/json'})[0],400)
        self.assertEqual(self.post(payload(type=[]))[0],400)
        self.assertEqual(self.request('POST','/api/studio/jobs/abc/complete','{}',{'Content-Type':'application/json'})[0],404)


if __name__=='__main__': unittest.main()
