import {safeMedia} from './model.js';
export function safePoster(url){return safeMedia(url||'')||/^\/api\/studio\/library\/(?:m_[a-f0-9]{20}|studio_[a-f0-9]{32})\/poster$/.test(url||'');}
export function filterVideos(assets,{search='',model='',collection='',scope='all'}={}){
  const needle=search.trim().toLocaleLowerCase();
  return assets.filter(a=>a.kind==='video'&&safeMedia(a.url)&&(!model||a.model===model)&&(!collection||a.collection===collection)&&(!needle||[a.name,a.relativePath,a.model,a.collection,a.classificationNote,...(a.sceneIds||[])].join(' ').toLocaleLowerCase().includes(needle))&&(scope==='all'||scope.startsWith('group:')?scope==='all'||a.group===scope.slice(6):(a.sceneIds||[]).includes(scope)||(a.ranges||[]).some(r=>r.sceneId===scope)));
}
export function groupVideos(assets,scenes,scope='all'){
  const groups=[];const grouped=new Set();
  for(const scene of scenes){if(scope!=='all'&&scope!==scene.id)continue;const items=assets.filter(a=>a.group==='scenes'&&(a.sceneIds||[]).includes(scene.id));if(items.length){groups.push({id:scene.id,name:scene.title,sceneId:scene.id,items});items.forEach(a=>grouped.add(a.id));}}
  for(const [id,name] of [['films','Films & séquences complètes'],['other','Autres explorations'],['unassigned','À classer']]){const items=assets.filter(a=>!grouped.has(a.id)&&(a.group===id||(id==='unassigned'&&a.group==='scenes'&&!scenes.some(s=>(a.sceneIds||[]).includes(s.id)))));if(items.length){groups.push({id,name,items});items.forEach(a=>grouped.add(a.id));}}
  const remainder=assets.filter(a=>!grouped.has(a.id));if(remainder.length)groups.push({id:'unassigned-other',name:'À classer',items:remainder});return groups;
}
export function suggestedRange(asset,scene,actualDuration=asset.durationSeconds){
  const total=Number(actualDuration);if(!Number.isFinite(total)||total<=0)return null;
  const match=(asset.ranges||[]).find(r=>r.sceneId===scene?.id&&Number.isFinite(r.inSeconds)&&Number.isFinite(r.outSeconds)&&r.inSeconds>=0&&r.outSeconds>r.inSeconds&&r.outSeconds<=total+.001);
  if(match)return {inSeconds:match.inSeconds,outSeconds:Math.min(match.outSeconds,total),mapped:true};
  return {inSeconds:0,outSeconds:Math.min(total,Number(scene?.duration)||4),mapped:false};
}
export function selectedVideoTake(asset,start,end,durationSeconds=asset.durationSeconds){
  const total=Number(durationSeconds),a=Number(start),b=Number(end);
  if(!safeMedia(asset.url)||!Number.isFinite(total)||total<=0||!Number.isFinite(a)||!Number.isFinite(b)||a<0||b<=a||b>total+.001)throw Error('Choisis un début et une fin valides dans cette vidéo.');
  const fps=24,inFrame=Math.round(a*fps),outFrame=Math.min(Math.round(b*fps),Math.floor(total*fps+1e-6));
  if(outFrame-inFrame<6||outFrame-inFrame>30*fps)throw Error('Choisis un passage de 0,25 à 30 secondes pour ce plan.');
  return {url:asset.url,libraryId:asset.id,inFrame,outFrame,fps,durationSeconds:total};
}
export function resizeVideoTake(take,requestedSeconds){
  const fps=take?.fps||24,start=take?.inFrame,sourceDuration=take?.durationSeconds;
  if(!Number.isFinite(fps)||fps<=0||!Number.isFinite(start)||start<0||!Number.isFinite(sourceDuration)||sourceDuration<=0||!Number.isFinite(requestedSeconds))throw Error('Les bornes de cette prise sont indisponibles.');
  const desiredFrames=Math.round(Math.min(30,Math.max(.25,requestedSeconds))*fps);
  const end=Math.min(start+desiredFrames,Math.floor(sourceDuration*fps+1e-6));
  if(end-start<Math.ceil(.25*fps))throw Error('Il reste moins de 0,25 seconde dans cette prise.');
  return {...take,outFrame:end};
}
