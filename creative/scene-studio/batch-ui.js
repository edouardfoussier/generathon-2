import {uid} from './model.js';
import {buildBatchRequests,startingImage,modelDuration,MAX_BATCH_SIZE} from './batch-model.js';
const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function createBatchUI({getScenes,isBackend,onJobs,onHandoff,toast}){
  let config={configured:false,models:[],concurrency:2,maxBatchSize:MAX_BATCH_SIZE}, selectedIds=[], submitting=false, retryAttempt=null;
  const chosenScenes=()=>{const selected=new Set(selectedIds);return getScenes().filter(s=>selected.has(s.id));};
  const chosenModel=()=>config.models.find(m=>m.id===$('batch-model').value);
  const error=message=>{$('batch-error').textContent=message||'';$('batch-error').hidden=!message;};
  function models(){
    const previous=$('batch-model').value;
    $('batch-model').innerHTML=config.models.filter(m=>m.kind===$('batch-type').value).map(m=>`<option value="${esc(m.id)}">${esc(m.name)}</option>`).join('');
    if([...$('batch-model').options].some(o=>o.value===previous))$('batch-model').value=previous;
    durations();
  }
  function durations(){
    const previous=$('batch-duration').value;
    $('batch-duration').innerHTML='<option value="scene">Durées des plans (adaptées au modèle)</option>'+(chosenModel()?.durations||[]).map(n=>`<option value="${n}">${n} secondes pour chaque plan</option>`).join('');
    if([...$('batch-duration').options].some(o=>o.value===previous))$('batch-duration').value=previous;
    preview();
  }
  function preview(){
    const scenes=chosenScenes(),engine=$('batch-engine').value,type=$('batch-type').value,model=chosenModel(),fal=engine==='fal';
    $('batch-model-field').hidden=!fal;$('batch-duration-field').hidden=!fal||type!=='video';
    $('batch-intro').textContent=`${scenes.length} plan${scenes.length>1?'s':''} sélectionné${scenes.length>1?'s':''}. Chaque plan garde son propre prompt et reçoit la direction commune ci-dessous.`;
    $('batch-provider-note').textContent=fal?`${config.concurrency||2} générations simultanées ; les autres attendent leur tour. Tu peux continuer à travailler ou fermer l’onglet ; laisse les serveurs locaux ouverts. FAL reçoit UNE image de départ par plan (la version image retenue, sinon l’image existante). Les autres références restent dans le contexte écrit. Le lancement utilise les crédits FAL.`:'Les demandes sont enregistrées ensemble, puis copiées dans notre conversation pour être exécutées via MCP. Ce mode ne lance pas de rendu automatiquement et ne débite aucun crédit à la préparation.';
    $('batch-preview').innerHTML=scenes.map(s=>{const image=startingImage(s),n=type==='video'&&fal?($('batch-duration').value==='scene'?modelDuration(s.duration,model):Number($('batch-duration').value)):s.duration;return `<div class="batch-preview-row">${image?`<img src="${esc(image)}" alt="" loading="lazy">`:'<span class="batch-no-image">?</span>'}<div><strong>${esc(s.title)}</strong><small>${type==='image'?'1 image':`${s.duration}s prévues${fal?` → ${n}s générées`:''}`}${fal&&!image?' · Image de départ manquante':''}</small></div>${type==='video'&&fal&&n!==s.duration?'<span class="duration-adjusted">Durée adaptée</span>':''}</div>`;}).join('');
    let problem='';
    try{buildBatchRequests(scenes,{type,engine,model,duration:$('batch-duration').value,instruction:$('batch-instruction').value});if(fal&&!config.configured)problem='FAL n’est pas connecté. Utilise le mode MCP pour préparer ces demandes.';}catch(e){problem=e.message;}
    error(problem);$('batch-submit').disabled=submitting||Boolean(problem)||!isBackend();
    $('batch-submit').textContent=submitting?'Enregistrement du lot…':fal?`Lancer ${scenes.length} ${type==='video'?'vidéo':'image'}${scenes.length>1?'s':''}`:`Préparer ${scenes.length} demande${scenes.length>1?'s':''} MCP`;
  }
  function setBusy(value){submitting=value;for(const id of ['batch-engine','batch-type','batch-model','batch-duration','batch-instruction'])$(id).disabled=value;preview();}
  async function configure(){
    try{const response=await fetch('/api/studio/generation-config');if(!response.ok)throw Error();config=await response.json();config.models||=[];}catch{config={configured:false,models:[],concurrency:2,maxBatchSize:MAX_BATCH_SIZE};}
    $('batch-engine').querySelector('[value="fal"]').disabled=!config.configured;
    return config;
  }
  async function open(ids,{type='video',instruction=''}={}){
    if(submitting){$('batch-dialog').showModal();return;}
    if(!isBackend()){toast('Le serveur local de l’atelier doit être ouvert pour enregistrer les demandes.');return;}
    selectedIds=[...ids];if(!selectedIds.length||selectedIds.length>MAX_BATCH_SIZE){toast('Coche de 1 à 6 plans dans le récit.');return;}
    $('batch-status').hidden=true;$('batch-instruction').value=instruction;$('batch-type').value=type;
    $('batch-engine').value=config.configured?'fal':'mcp';models();$('batch-dialog').showModal();
  }
  $('batch-instruction').addEventListener('input',preview);
  $('batch-type').addEventListener('change',models);$('batch-model').addEventListener('change',durations);
  for(const id of ['batch-engine','batch-duration'])$(id).addEventListener('change',preview);
  $('batch-cancel').addEventListener('click',()=>$('batch-dialog').close());
  $('batch-submit').addEventListener('click',async()=>{
    if(submitting)return;
    const engine=$('batch-engine').value,model=chosenModel();let request;
    try{request={engine,...(engine==='fal'?{model:model?.id}:{}),requests:buildBatchRequests(chosenScenes(),{type:$('batch-type').value,engine,model,duration:$('batch-duration').value,instruction:$('batch-instruction').value})};}catch(e){error(e.message);return;}
    // A network retry reuses the same ID for the exact same request; it cannot submit a second paid lot.
    const signature=JSON.stringify(request);if(retryAttempt?.signature!==signature)retryAttempt={signature,key:uid()};
    request.idempotencyKey=retryAttempt.key;setBusy(true);$('batch-status').hidden=true;
    try{
      const response=await fetch('/api/studio/batch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request)});
      const data=await response.json();if(!response.ok)throw Error(data.error||'Le lot n’a pas pu être enregistré.');
      onJobs(data.jobs||[]);retryAttempt=null;$('batch-dialog').close();
      if(engine==='mcp')onHandoff(data);
      toast(engine==='fal'?`${data.jobs.length} prises en file. Suis leur progression dans « Générations en arrière-plan ».`:`${data.jobs.length} demandes MCP enregistrées.`);
    }catch(e){error(e.message);$('batch-status').textContent='La même demande peut être renvoyée sans créer un second lot. Les versions existantes restent disponibles.';$('batch-status').hidden=false;}
    finally{submitting=false;for(const id of ['batch-engine','batch-type','batch-model','batch-duration','batch-instruction'])$(id).disabled=false;$('batch-submit').disabled=false;$('batch-submit').textContent=$('batch-status').hidden?'Lancer les nouvelles prises':'Renvoyer la même demande';}
  });
  return {configure,open,get configured(){return config.configured;}};
}
