import {copy,uid,duration,seconds,insertScene,moveScene,snapshot,applyDirection,validateProject,safeMedia,generationPrompt,mergeBlocking,replaceReference,referencePrompt} from './model.js';
import {preferredView,MAX_BATCH_SIZE} from './batch-model.js';
import {createBatchUI} from './batch-ui.js';
import {createGallery} from './gallery-ui.js';
import {resizeVideoTake} from './gallery-model.js';
import {createSequencePlayer} from './timeline.js';
const $ = id => document.getElementById(id);
const escape = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY='converse-scene-studio-v1';
let project, seed, selectedId, viewer, activeView='media', loadingScene=false, playing=false, jobs=[], toastTimer, saveTimer, backend=false, clipBounds=null, sequencePlayer, activeReferenceId, sequenceInfo;
let viewerPromise,tools3d=false;
try{tools3d=localStorage.getItem('converse-scene-studio-show-3d')==='true';}catch{}
const batchSelection=new Set();
const scene = () => project.scenes.find(s=>s.id===selectedId);
const batchUI=createBatchUI({getScenes:()=>project?.scenes||[],isBackend:()=>backend,onJobs:newJobs=>{const ids=new Set(newJobs.map(j=>j.id));jobs=[...newJobs,...jobs.filter(j=>!ids.has(j.id))];renderJobs();},onHandoff:batchHandoff,toast});
const gallery=createGallery({getScenes:()=>project?.scenes||[],getSelectedId:()=>selectedId,toast,
  onUse:({asset,sceneId,take})=>{const chosen=project.scenes.find(s=>s.id===sceneId);chosen.selectedTakes||={};chosen.takeBaseDurations||={};chosen.takeBaseDurations.video??=chosen.duration;chosen.selectedTakes.video=take;chosen.duration=(take.outFrame-take.inFrame)/take.fps;selectScene(sceneId);switchView('video');save();toast(`« ${asset.name} » : passage retenu pour ce plan. L’original reste disponible.`);},
  onInsert:({asset,sceneId,take})=>{const created=insertScene(project,sceneId,{title:asset.name.slice(0,100),description:`Passage sélectionné dans ${asset.name} : ${(take.inFrame/take.fps).toFixed(2)}–${(take.outFrame/take.fps).toFixed(2)} secondes.`});created.duration=(take.outFrame-take.inFrame)/take.fps;created.selectedTakes={video:take};if(safeMedia(asset.posterUrl||''))created.poster=asset.posterUrl;selectScene(created.id);switchView('video');save();toast('Passage inséré comme nouveau plan. Le montage précédent reste intact.');}
});
function openGallery(sceneId=null){$('scene-video').pause();sequencePlayer?.pause();viewer?.pause();playing=false;$('play-scene').textContent='▷ Animer';return gallery.open(sceneId);}
$('open-gallery').addEventListener('click',()=>openGallery());$('compare-takes').addEventListener('click',()=>openGallery(selectedId));
function directionHelp(){return tools3d?'La note sera ajoutée au prompt. Les indications simples de caméra, lumière et placement ajustent aussi la maquette.':'La note sera ajoutée au prompt. Le rendu retenu reste disponible jusqu’à ce que tu choisisses une autre version.';}
function render3dTools(){document.querySelectorAll('[data-3d-tool]').forEach(el=>el.hidden=!tools3d);$('toggle-3d').textContent=tools3d?'Masquer les outils 3D':'Afficher les outils 3D';$('toggle-3d').setAttribute('aria-pressed',String(tools3d));if(!tools3d){$('use-camera').checked=false;viewer?.pause();playing=false;$('play-scene').textContent='▷ Animer';}if(project)$('direction-result').textContent=directionHelp();}
async function ensureViewer(){if(viewer)return viewer;if(viewerPromise)return viewerPromise;viewerPromise=(async()=>{const {createSceneViewer}=await import('./scene3d.js');viewer=createSceneViewer($('viewer-3d'),{onChange:event=>{if(!loadingScene&&project&&event.blocking){scene().blocking=copy(event.blocking);save();}},onError:showViewerError});loadingScene=true;try{viewer.load(scene());}finally{loadingScene=false;}return viewer;})();try{return await viewerPromise;}catch(e){viewerPromise=null;showViewerError(e);}}
function renderBatchSelection(){for(const id of batchSelection)if(!project.scenes.some(s=>s.id===id))batchSelection.delete(id);const count=batchSelection.size;$('batch-count').textContent=count?`${count} / ${MAX_BATCH_SIZE} plans cochés`:'Coche les plans à régénérer';$('open-batch').disabled=!count;$('clear-selection').disabled=!count;document.querySelectorAll('[data-batch-scene]').forEach(input=>{input.checked=batchSelection.has(input.dataset.batchScene);input.disabled=count>=MAX_BATCH_SIZE&&!input.checked;});}

const download=(blob,name)=>{const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);};
function toast(text){$('toast').textContent=text;$('toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').hidden=true,5200);}
function save(){clearTimeout(saveTimer);$('save-state').textContent='Enregistrement…';saveTimer=setTimeout(()=>{try{localStorage.setItem(KEY,JSON.stringify({project,selectedId}));$('save-state').textContent='Brouillon enregistré';}catch{$('save-state').textContent='Exporter pour sauvegarder';}},180);}
function renderList(){
  sequencePlayer?.setProject(project,selectedId);
  const total=duration(project);$('project-count').textContent=`${project.scenes.length} plans`;$('scene-count').textContent=project.scenes.length;$('project-duration').textContent=`${total.toFixed(total%1?1:0)} s`;
  let at=0;
  $('scene-list').innerHTML=project.scenes.map((s,i)=>{const start=at;at+=s.duration;return `<div class="scene-entry"><label class="scene-select" title="Inclure dans le lot"><input type="checkbox" data-batch-scene="${escape(s.id)}" aria-label="Régénérer ${escape(s.title)}"></label><button class="scene-card ${s.id===selectedId?'active':''}" data-scene="${escape(s.id)}" aria-current="${s.id===selectedId?'true':'false'}">${s.poster&&safeMedia(s.poster)?`<img src="${escape(s.poster)}" alt="" loading="lazy">`:'<span class="scene-placeholder">＋</span>'}<span class="scene-text"><strong>${escape(s.title)}</strong><small>${String(i+1).padStart(2,'0')} · ${seconds(start)} · ${s.duration}s</small></span></button></div><button class="insert-between" data-insert="${escape(s.id)}" aria-label="Insérer un plan après ${escape(s.title)}">＋</button>`;}).join('');renderBatchSelection();
}
function renderHistory(){const s=scene();$('history-count').textContent=(s.versions||[]).length;$('history-list').innerHTML=(s.versions||[]).map(v=>`<div class="history-item"><p>${escape(v.reason)}<br>${new Date(v.at).toLocaleString('fr-FR',{dateStyle:'short',timeStyle:'short'})}</p><button data-restore="${escape(v.id)}">Restaurer cette version</button></div>`).join('')||'<p class="empty-note">Aucune modification pour ce plan.</p>';}
function renderReferences(){const refs=scene().references||[];$('reference-count').textContent=refs.length;$('reference-list').innerHTML=refs.map((r,i)=>`<button class="ref-card" data-ref="${i}" title="${escape(r.label)}">${safeMedia(r.url)?`<img src="${escape(r.url)}" alt="${escape(r.label)}" loading="lazy">`:''}<span>${escape(r.label)}</span><small>${escape(r.id)} · ${escape(r.role||'référence')}</small></button>`).join('')||'<p class="empty-note">Ce plan hérite de la direction du récit.</p>';}
function renderCharacters(){const chars=scene().blocking.characters||[];$('character-controls').innerHTML=chars.map((c,i)=>`<div class="character-control"><strong>${escape(c.label||c.id)}</strong><label for="character-x-${i}">Placement gauche / droite</label><input id="character-x-${i}" data-character="${i}" data-axis="0" type="range" min="-3" max="3" step="0.1" value="${Number(c.position?.[0]||0)}"><label for="character-z-${i}">Profondeur</label><input id="character-z-${i}" data-character="${i}" data-axis="2" type="range" min="-3" max="3" step="0.1" value="${Number(c.position?.[2]||0)}"></div>`).join('');}
function selectScene(id){
  if(!project.scenes.some(s=>s.id===id))return;
  selectedId=id;const s=scene();loadingScene=true;playing=false;$('play-scene').textContent='▷ Animer';viewer?.pause?.();
  const index=project.scenes.findIndex(x=>x.id===id);
  $('scene-number').textContent=`PLAN ${String(index+1).padStart(2,'0')} / ${project.scenes.length}`;$('scene-title').textContent=s.title;$('title-input').value=s.title;$('duration-input').value=s.duration;$('location-input').value=s.blocking.location||'attic';$('prompt-input').value=s.prompt;$('prompt-status').textContent=s.modified?'Direction modifiée':'Source conservée';$('scene-description').textContent=s.description||'Nouveau plan à mettre en scène.';
  $('modification').value=s.pendingDirection||'';$('direction-result').textContent=directionHelp();
  $('warmth').value=s.blocking.lighting?.warmth??.6;$('intensity').value=s.blocking.lighting?.intensity??1;
  const sourceDuration=s.source?(s.source.outFrame-s.source.inFrame)/s.source.fps:0;
  $('source-label').textContent=s.source?`${s.provenance?.cropFilter?'INSERT RECADRÉ':'PRISE SOURCE'} · ${sourceDuration}s`:'NOUVEAU PLAN · NON GÉNÉRÉ';
  $('provenance-note').textContent=(s.provenance?.note||s.provenance?.kind||'Références et prompt du dernier montage V4.')+' Le prompt source peut couvrir plusieurs plans. La demande de génération le restreint automatiquement au plan sélectionné.';
  $('move-up').disabled=index===0;$('move-down').disabled=index===project.scenes.length-1;
  renderList();renderReferences();renderCharacters();renderHistory();renderJobs();
  try{viewer?.load(s);$('viewport-error').hidden=true;}catch(e){showViewerError(e);}
  loadingScene=false;switchView(activeView==='media'||activeView==='sequence'||(!tools3d&&activeView==='3d')||(activeView==='video'&&preferredView(s)==='image')?preferredView(s):activeView);save();
}
function showSequenceHeading(){if(!sequenceInfo)return;$('scene-title').textContent=sequenceInfo.title;$('scene-number').textContent=`LECTURE DU MONTAGE · ${sequenceInfo.index} / ${sequenceInfo.total}`;$('scene-description').textContent='Lecture des versions vidéo retenues dans l’ordre du récit.';$('source-label').textContent='APERÇU DU MONTAGE';$('view-label').textContent='Lecture du montage';}
function showViewerError(e){$('viewport-error').hidden=activeView!=='3d';$('viewport-error').textContent=`La vue 3D n’a pas pu démarrer : ${e.message||e}. Les références et vidéos restent disponibles.`;}
function switchView(view){
  if(view==='3d'&&!tools3d){tools3d=true;render3dTools();}
  if(view==='3d')void ensureViewer();else{viewer?.pause();playing=false;$('play-scene').textContent='▷ Animer';}
  $('viewport-error').hidden=true;
  activeView=view;$('restore-take').hidden=!scene().selectedTakes?.[view];$('scene-video').pause();clipBounds=null;
  if(view==='sequence')showSequenceHeading();else{const s=scene();$('scene-title').textContent=s.title;$('scene-number').textContent=`PLAN ${String(project.scenes.indexOf(s)+1).padStart(2,'0')} / ${project.scenes.length}`;$('scene-description').textContent=s.description||'Nouveau plan à mettre en scène.';$('source-label').textContent=s.source?`PRISE SOURCE · ${(s.source.outFrame-s.source.inFrame)/s.source.fps}s`:'NOUVEAU PLAN · NON GÉNÉRÉ';}
  document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.view===view)));
  const isSequence=view==='sequence';
  if(!isSequence)sequencePlayer?.pause();
  $('viewer-sequence').hidden=!isSequence;
  const is3d=view==='3d';$('viewer-3d').hidden=!is3d;$('viewer-media').hidden=is3d||isSequence;$('viewport-top').hidden=!is3d;$('viewport-bottom').hidden=!is3d;$('camera-bar').hidden=!is3d;$('scene-image').hidden=true;$('scene-video').hidden=true;$('media-empty').hidden=true;
  $('view-label').textContent=is3d?'Maquette de mise en scène':view==='image'?'Image du plan':'Vidéo du plan';
  if(isSequence){$('view-label').textContent='Lecture du montage';return;}
  if(!is3d){const s=scene(), selectedTake=s.selectedTakes?.[view];let url=selectedTake?.url || (view==='image'?(s.image||s.poster):(s.previewVideo||s.source)?.url);if(!url||!safeMedia(url)){$('media-empty').hidden=false;return;}
    if(view==='image'){$('scene-image').src=url;$('scene-image').hidden=false;}
    else{const v=$('scene-video');v.src=url;v.hidden=false;const preview=selectedTake||s.previewVideo||s.source;if(Number.isFinite(preview?.inFrame)&&Number.isFinite(preview?.outFrame)){clipBounds={start:preview.inFrame/(preview.fps||24),end:preview.outFrame/(preview.fps||24)};v.addEventListener('loadedmetadata',()=>{if(clipBounds)v.currentTime=clipBounds.start;},{once:true});}v.load();}
  }
}
$('restore-take').addEventListener('click',()=>{if(!['image','video'].includes(activeView))return;delete scene().selectedTakes?.[activeView];if(Number.isFinite(scene().takeBaseDurations?.[activeView])){scene().duration=scene().takeBaseDurations[activeView];delete scene().takeBaseDurations[activeView];$('duration-input').value=scene().duration;renderList();}switchView(activeView);sequencePlayer?.setProject(project,selectedId);save();toast('Version originale restaurée. La variante reste disponible.');});
$('scene-video').addEventListener('timeupdate',()=>{const v=$('scene-video');if(clipBounds&&v.currentTime>=clipBounds.end){v.pause();v.currentTime=clipBounds.start;}});
$('scene-video').addEventListener('seeking',()=>{const v=$('scene-video');if(clipBounds&&(v.currentTime<clipBounds.start-.1||v.currentTime>clipBounds.end+.1))v.currentTime=clipBounds.start;});
function updateBlocking(patch){const s=scene();s.blocking={...s.blocking,...patch,lighting:{...s.blocking.lighting,...patch.lighting},camera:{...s.blocking.camera,...patch.camera}};viewer?.update(patch);s.modified=true;save();}
const JOB_LABELS={awaiting_mcp:'À lancer via MCP',queued:'En file',submitting:'Envoi au modèle',running:'Génération en cours',completed:'Version disponible',failed:'Génération interrompue',submission_unknown:'Envoi à vérifier · pas de relance automatique',cancelled:'Demande annulée'};
function renderJobs(){
  const current=jobs.filter(j=>j.sceneId===selectedId);$('take-count').textContent=current.length;
  const labels=JOB_LABELS;
  renderGlobalJobs();gallery.jobsUpdated(jobs);
  $('job-list').innerHTML=current.map(j=>`<div class="job-card"><span class="job-type">${j.type==='video'?'▷':j.type==='image'?'▧':'✎'}</span><div><strong>${j.target?.kind==='reference'?'Asset · '+escape(j.target.label||j.target.id):j.type==='video'?'Vidéo':j.type==='image'?'Image':j.type==='scene3d'?'Maquette 3D':'Direction'} · ${escape(labels[j.status]||j.status)}</strong><p>${escape(j.error||new Date(j.createdAt||Date.now()).toLocaleString('fr-FR',{dateStyle:'short',timeStyle:'short'}))}</p></div>${j.status==='completed'&&(safeMedia(j.result?.url||j.artifactUrl||'')||j.result?.blocking||j.result?.text)?`<button data-use-job="${escape(j.id)}">${j.target?.kind==='reference'?'Utiliser cette référence':'Utiliser cette version'}</button>`:j.status==='awaiting_mcp'?`<button data-job="${escape(j.id)}">Continuer ↗</button>`:''}</div>`).join('')||'<p class="empty-note">L’original est conservé. Chaque génération viendra s’ajouter ici.</p>';
}
async function checkBackend(){try{const r=await fetch('/api/studio/status');if(!r.ok)throw Error();const status=await r.json();backend=Boolean(status.available);const config=await batchUI.configure();$('connection-state').textContent=config.configured?`● FAL · ${config.concurrency||2} générations simultanées`:'● Demandes via MCP';$('generation-note').textContent=config.configured?'Lance une nouvelle prise ou coche jusqu’à 6 plans pour une direction commune. Les rendus progressent en arrière-plan.':'Prépare un lot ici, puis exécute-le dans notre conversation. Aucun crédit débité à la mise en file MCP.';await refreshJobs();}catch{backend=false;$('connection-state').textContent='○ Mode préparation locale';$('generation-note').textContent='Ouvre l’atelier avec son serveur local (port 8789) pour enregistrer les demandes.';}}
async function refreshJobs(){if(!backend)return;try{const r=await fetch('/api/studio/jobs');if(!r.ok)throw Error();const data=await r.json();jobs=data.jobs||[];renderJobs();}catch{toast('Impossible de lire la file de générations.');}}
function handoff(job){$('job-handoff').value=`Traite la demande ${job.id} de l’Atelier Luna/Rafa via Higgsfield MCP. Lis creative/scene-studio/.state/jobs/${job.id}/request.json (ou la demande correspondante dans la file du serveur), ${job.target?.kind==='reference'?`modifie uniquement la référence image ${job.target.id} pour le plan ${job.sceneId}`:`génère uniquement la version ${job.type} de la scène ${job.sceneId}`} avec le prompt, les références et le cadrage fournis. Importe le résultat dans l’atelier avec sa provenance en utilisant le CLI de creative/scene-studio/server.py. Conserve les originaux.`;$('job-dialog').showModal();}
async function generate(type){
  if(type!=='scene3d'&&!$('use-camera').checked){await batchUI.open([selectedId],{type,instruction:scene().pendingDirection||''});return;}
  if(!backend){toast('Démarre le serveur : python3 creative/scene-studio/server.py puis ouvre http://127.0.0.1:8789/studio');return;}
  const s=scene();if(!s.prompt.trim()){toast('Écris la direction de ce plan avant de générer.');return;}
  const button=$(type==='image'?'generate-image':type==='video'?'generate-video':'advanced-3d');button.disabled=true;
  try{let cameraImage;if(type!=='scene3d'&&$('use-camera').checked){viewer?.pause?.();cameraImage=viewer?.capture();if(!cameraImage)throw Error('Le cadrage 3D est indisponible. Décoche « Joindre le cadrage 3D » ou rétablis la vue.');}
    const payload={sceneId:s.id,type,prompt:type==='scene3d'?`Réviser la maquette 3D de la scène ${s.title}. Action: ${s.description}. Produire un JSON blocking compatible avec creative/scene-studio/scene3d.js, en gardant les personnages et références. ${s.pendingDirection||''}\nDirection complète:\n${s.prompt}`:generationPrompt(s,type,$('use-camera').checked),modification:s.pendingDirection||'',references:s.references,blocking:s.blocking,duration:s.duration,idempotencyKey:uid(),...(cameraImage?{cameraImage}:{})};
    const r=await fetch('/api/studio/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const job=await r.json();if(!r.ok)throw Error(job.error||'Demande impossible.');jobs.unshift(job);renderJobs();handoff(job);toast('Demande sauvegardée avec ses références.');
  }catch(e){toast(e.message);}finally{button.disabled=false;}
}
function renderGlobalJobs(){
  const active=new Set(['queued','submitting','running','submission_unknown']);
  const recent=[...jobs].sort((a,b)=>Number(active.has(b.status))-Number(active.has(a.status)));
  const pending=recent.filter(j=>active.has(j.status)).length;
  $('queue-count').textContent=pending?`${pending} en cours · ${recent.length} au total`:recent.length;
  $('all-job-list').innerHTML=recent.slice(0,30).map(j=>{const s=project.scenes.find(s=>s.id===j.sceneId);return `<div class="job-card ${active.has(j.status)?'job-pending':''}"><span class="job-type">${j.type==='video'?'▷':'▧'}</span><div><strong>${escape(s?.title||j.sceneId)} · ${escape(JOB_LABELS[j.status]||j.status)}</strong><p>${escape(j.error||`${j.type==='video'?'Vidéo':'Image'}${j.model?' · '+j.model:''}`)}</p></div>${j.status==='awaiting_mcp'&&j.batchId?`<button data-batch-handoff="${escape(j.batchId)}">Copier le lot</button>`:''}<button data-open-job-scene="${escape(j.sceneId)}">${j.status==='completed'?'Voir les versions':'Ouvrir le plan'}</button></div>`;}).join('')||'<p class="empty-note">Les nouvelles versions apparaîtront ici, sans remplacer les originaux.</p>';
}
function batchHandoff(batch){
  const list=(batch.jobs||[]).map(j=>`- ${j.id} : ${j.type}, scène ${j.sceneId}`).join('\n');
  $('job-handoff').value=`Exécute ce lot ${batch.id} de l’Atelier Luna/Rafa via les MCP disponibles. Les demandes sont seulement préparées, pas encore exécutées.\n${list}\nLis chaque creative/scene-studio/.state/jobs/<id>/request.json. Génère chaque scène indépendamment, en parallèle selon les limites du service, avec son prompt et ses références. Importe chaque résultat via le CLI de creative/scene-studio/server.py, avec sa provenance. Préserve les originaux et laisse l’utilisateur choisir les versions retenues.`;
  $('job-dialog').showModal();
}
$('all-job-list').addEventListener('click',e=>{const handoff=e.target.closest('[data-batch-handoff]'),open=e.target.closest('[data-open-job-scene]');if(handoff){const id=handoff.dataset.batchHandoff;batchHandoff({id,jobs:jobs.filter(j=>j.batchId===id&&j.status==='awaiting_mcp')});}if(open){selectScene(open.dataset.openJobScene);$('job-list').scrollIntoView({block:'center',behavior:'smooth'});}});
$('refresh-all-jobs').addEventListener('click',refreshJobs);
$('toggle-3d').addEventListener('click',()=>{tools3d=!tools3d;try{localStorage.setItem('converse-scene-studio-show-3d',String(tools3d));}catch{}render3dTools();if(!tools3d&&activeView==='3d')switchView(preferredView(scene()));});
$('open-batch').addEventListener('click',()=>batchUI.open([...batchSelection]));
$('clear-selection').addEventListener('click',()=>{batchSelection.clear();renderBatchSelection();});
$('scene-list').addEventListener('change',e=>{const input=e.target.closest('[data-batch-scene]');if(!input)return;if(input.checked&&batchSelection.size<MAX_BATCH_SIZE)batchSelection.add(input.dataset.batchScene);else batchSelection.delete(input.dataset.batchScene);renderBatchSelection();});
function openInsert(id=selectedId){selectedId=id;$('new-title').value='Un nouveau souvenir';$('new-description').value='';$('insert-dialog').showModal();}
$('scene-list').addEventListener('click',e=>{const card=e.target.closest('[data-scene]'),insert=e.target.closest('[data-insert]');if(card)selectScene(card.dataset.scene);if(insert){selectScene(insert.dataset.insert);openInsert();}});
$('add-scene').addEventListener('click',()=>openInsert());
$('insert-dialog').addEventListener('close',()=>{if($('insert-dialog').returnValue!=='insert')return;const s=insertScene(project,selectedId,{title:$('new-title').value.trim()||'Nouveau souvenir',description:$('new-description').value.trim()});selectScene(s.id);toast('Plan inséré. Ajuste le décor, la direction et les références héritées.');});
$('duplicate').addEventListener('click',()=>{const s=copy(scene());s.id=uid();s.title+=' · variante';s.versions=[];s.modified=true;project.scenes.splice(project.scenes.findIndex(x=>x.id===selectedId)+1,0,s);selectScene(s.id);toast('Variante ajoutée après l’original.');});
$('move-up').addEventListener('click',()=>{if(moveScene(project,selectedId,-1))selectScene(selectedId);});$('move-down').addEventListener('click',()=>{if(moveScene(project,selectedId,1))selectScene(selectedId);});
$('title-input').addEventListener('change',()=>{scene().title=$('title-input').value.trim()||'Plan sans titre';$('scene-title').textContent=scene().title;renderList();save();});
$('duration-input').addEventListener('change',()=>{const s=scene(),desired=Math.min(30,Math.max(.25,Number($('duration-input').value)||4)),take=s.selectedTakes?.video;try{if(Number.isFinite(take?.inFrame)&&Number.isFinite(take?.outFrame)){const resized=resizeVideoTake(take,desired);s.selectedTakes.video=resized;s.duration=(resized.outFrame-resized.inFrame)/(resized.fps||24);sequencePlayer?.pause();if(activeView==='video')switchView('video');if(s.duration<desired-1/24)toast('Durée limitée à la fin du fichier source.');}else s.duration=desired;$('duration-input').value=s.duration;renderList();save();}catch(e){$('duration-input').value=s.duration;toast(e.message);}});
$('prompt-input').addEventListener('change',()=>{if(scene().prompt!==$('prompt-input').value){snapshot(scene(),'Édition manuelle du prompt');scene().prompt=$('prompt-input').value;scene().modified=true;$('prompt-status').textContent='Direction modifiée';renderHistory();save();}});
$('modification').addEventListener('input',()=>{scene().pendingDirection=$('modification').value;save();});
$('apply-direction').addEventListener('click',()=>{try{const s=scene(), applied=applyDirection(s,$('modification').value);$('prompt-input').value=s.prompt;viewer?.load(s);$('direction-result').textContent=tools3d&&applied.length?`Maquette ajustée : ${applied.join(', ')}. Toute la note est conservée pour le rendu IA.`:'Note ajoutée au prompt. Lance une nouvelle prise pour voir le résultat.';s.pendingDirection='';$('modification').value='';$('warmth').value=s.blocking.lighting.warmth;$('intensity').value=s.blocking.lighting.intensity;$('location-input').value=s.blocking.location;$('prompt-status').textContent='Direction modifiée';renderCharacters();renderHistory();save();toast('Direction ajoutée ; version précédente conservée.');}catch(e){toast(e.message);}});
$('location-input').addEventListener('change',()=>{snapshot(scene(),'Changement de décor 3D');updateBlocking({location:$('location-input').value});renderHistory();});
for(const key of ['warmth','intensity'])$(key).addEventListener('input',()=>updateBlocking({lighting:{[key]:Number($(key).value)}}));
$('character-controls').addEventListener('input',e=>{if(e.target.dataset.character===undefined)return;const chars=copy(scene().blocking.characters);chars[Number(e.target.dataset.character)].position[Number(e.target.dataset.axis)]=Number(e.target.value);updateBlocking({characters:chars});});
$('history-list').addEventListener('click',e=>{const b=e.target.closest('[data-restore]');if(!b)return;const s=scene(), version=s.versions.find(v=>v.id===b.dataset.restore);if(!version)return;const chosen=copy(version);snapshot(s,'Avant restauration');s.prompt=chosen.prompt;s.blocking=chosen.blocking;selectScene(s.id);toast('Version restaurée.');});
$('reference-list').addEventListener('click',e=>{const b=e.target.closest('[data-ref]');if(!b)return;const r=scene().references[Number(b.dataset.ref)];if(!safeMedia(r.url))return;activeReferenceId=r.id;$('asset-note').value='';$('reference-full').src=r.url;$('reference-caption').textContent=`${r.id} — ${r.label}`;$('restore-reference').hidden=!(scene().referenceVersions?.[r.id]?.length);$('image-dialog').showModal();});
for(const b of document.querySelectorAll('[data-view]'))b.addEventListener('click',()=>switchView(b.dataset.view));
for(const b of document.querySelectorAll('[data-camera]'))b.addEventListener('click',()=>{viewer?.setCamera(b.dataset.camera);document.querySelectorAll('[data-camera]').forEach(x=>x.classList.toggle('selected',x===b));save();});
$('play-scene').addEventListener('click',()=>{playing=!playing;playing?viewer?.play():viewer?.pause();$('play-scene').textContent=playing?'Ⅱ Pause':'▷ Animer';});
$('capture').addEventListener('click',async()=>{try{const url=viewer.capture();const blob=await(await fetch(url)).blob();download(blob,`${scene().id}-cadrage-3d.png`);}catch(e){toast(e.message);}});
$('export-glb').addEventListener('click',async()=>{try{download(await viewer.exportGLB(),`${scene().id}-scene.glb`);toast('Maquette 3D exportée.');}catch(e){toast(`Export 3D impossible : ${e.message}`);}});
$('advanced-3d').addEventListener('click',()=>generate('scene3d'));
$('generate-image').addEventListener('click',()=>generate('image'));$('generate-video').addEventListener('click',()=>generate('video'));$('refresh-jobs').addEventListener('click',refreshJobs);
$('job-list').addEventListener('click',e=>{const b=e.target.closest('[data-job],[data-use-job]');if(!b)return;const j=jobs.find(x=>x.id===(b.dataset.job||b.dataset.useJob));if(!j)return;if(b.dataset.job){handoff(j);return;}if(j.target?.kind==='reference'&&safeMedia(j.result?.url)){try{replaceReference(scene(),j.target.id,{url:j.result.url},'Avant variante d’asset');renderReferences();save();toast('Référence remplacée pour ce plan. Son original reste restaurable.');}catch(e){toast(e.message);}return;}if(j.type==='scene3d'&&j.result?.blocking){snapshot(scene(),'Avant nouvelle maquette MCP');try{scene().blocking=mergeBlocking(scene().blocking,j.result.blocking);}catch(e){toast(e.message);return;}selectScene(selectedId);switchView('3d');toast('Nouvelle maquette appliquée.');return;}if(j.type==='revise'&&j.result?.text){snapshot(scene(),'Avant révision MCP');scene().prompt=j.result.text;selectScene(selectedId);toast('Prompt révisé appliqué.');return;}const url=j.result?.url||j.artifactUrl;if(safeMedia(url)){scene().selectedTakes||={};scene().selectedTakes[j.type]={url,jobId:j.id};switchView(j.type);sequencePlayer?.setProject(project,selectedId);save();}});
$('copy-handoff').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('job-handoff').value);toast('Demande copiée. Colle-la dans notre conversation.');}catch{$('job-handoff').select();toast('Sélectionne et copie la demande.');}});
for(const b of document.querySelectorAll('.close-dialog'))b.addEventListener('click',()=>b.closest('dialog').close());
$('export-btn').addEventListener('click',()=>download(new Blob([JSON.stringify(project,null,2)],{type:'application/json'}),'luna-rafa-studio.json'));
$('import-btn').addEventListener('click',()=>$('import-file').click());
$('import-file').addEventListener('change',async e=>{const f=e.target.files[0];if(!f)return;try{if(f.size>5*1024*1024)throw Error('Projet trop volumineux.');const imported=validateProject(JSON.parse(await f.text()));project=imported;selectScene(project.scenes[0].id);toast('Projet importé.');}catch(e){toast(e.message);}finally{$('import-file').value='';}});
$('reset-project').addEventListener('click',()=>{download(new Blob([JSON.stringify(project,null,2)],{type:'application/json'}),'luna-rafa-avant-reinitialisation.json');project=copy(seed);selectScene(project.scenes[0].id);toast('Montage source restauré ; ton brouillon a été exporté.');});
async function init(){
  if(location.protocol==='file:'){location.replace('http://127.0.0.1:8789/studio');return;}
  try{const r=await fetch('./project.json');if(!r.ok)throw Error('Données du projet indisponibles.');seed=validateProject(await r.json());project=copy(seed);try{const saved=JSON.parse(localStorage.getItem(KEY)||'null');if(saved){project=validateProject(saved.project);selectedId=saved.selectedId;}}catch{toast('Le brouillon local était incompatible. Les scènes sources sont chargées.');}
    for(const s of project.scenes){const original=seed.scenes.find(x=>x.id===s.id);if(original?.previewVideo&&!s.previewVideo)s.previewVideo=copy(original.previewVideo);if(original?.image&&!s.image)s.image=original.image;}
    selectedId=project.scenes.some(s=>s.id===selectedId)?selectedId:project.scenes[0].id;
    loadingScene=true;
    render3dTools();
    sequencePlayer=createSequencePlayer({dock:$('sequence-dock'),viewport:$('viewer-sequence'),onOpen:()=>{switchView('sequence');const rect=$('viewport').getBoundingClientRect();if(rect.top<0||rect.bottom>innerHeight-170)$('viewport').scrollIntoView({block:'center',behavior:'smooth'});},onClip:info=>{sequenceInfo=info;if(activeView==='sequence')showSequenceHeading();}});
    selectScene(selectedId);await checkBackend();setInterval(()=>{if(backend&&!document.hidden)refreshJobs();},6000);
  }catch(e){$('scene-title').textContent='Atelier indisponible';$('scene-description').textContent=e.message;toast(e.message);}
}
init();

$('generate-asset').addEventListener('click',async()=>{
  if(!backend){toast('La file MCP nécessite le serveur local de l’atelier.');return;}
  const s=scene(),reference=s.references.find(r=>r.id===activeReferenceId);
  if(!reference)return;
  const button=$('generate-asset');button.disabled=true;
  try{
    const note=$('asset-note').value;
    const payload={sceneId:s.id,type:'image',prompt:referencePrompt(s,reference,note),modification:note,references:[{id:reference.id,label:reference.label,url:reference.url,role:reference.role||'reference'}],target:{kind:'reference',id:reference.id,label:reference.label,scope:'scene'},idempotencyKey:uid()};
    const response=await fetch('/api/studio/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const job=await response.json();if(!response.ok)throw Error(job.error||'Demande impossible.');
    jobs.unshift(job);renderJobs();$('image-dialog').close();handoff(job);toast('Demande préparée pour cet asset uniquement.');
  }catch(e){toast(e.message);}finally{button.disabled=false;}
});
$('restore-reference').addEventListener('click',()=>{
  const s=scene(),history=s.referenceVersions?.[activeReferenceId];
  if(!history?.length)return;
  const original=copy(history.at(-1));replaceReference(s,activeReferenceId,original,'Avant restauration de l’asset');
  $('reference-full').src=original.url;renderReferences();save();toast('Référence originale restaurée pour ce plan.');
});
