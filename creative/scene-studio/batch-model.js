import {copy,generationPrompt,safeMedia} from './model.js';

export const MAX_BATCH_SIZE=6;
export function preferredView(scene){return safeMedia(scene.selectedTakes?.video?.url||scene.previewVideo?.url||scene.source?.url||'')?'video':'image';}
export function startingImage(scene){return [scene.selectedTakes?.image?.url,scene.image,scene.poster].find(url=>safeMedia(url||'')&&(url.startsWith('/creative/')||url.startsWith('/api/studio/'))&&(/^\/api\/studio\/jobs\/[a-f0-9]{32}\/artifact$/.test(url)||/\.(png|jpe?g|webp)(?:$|\?)/i.test(url)))||null;}
export function modelDuration(value,model){const options=(model?.durations||[]).filter(n=>Number.isFinite(n)).sort((a,b)=>a-b);return options.find(n=>n>=value)??options.at(-1)??value;}
export function buildBatchRequests(scenes,{type,model,engine='fal',instruction='',duration='scene'}={}){
  if(!scenes.length||scenes.length>MAX_BATCH_SIZE)throw Error('Sélectionne de 1 à 6 plans.');
  if(!['video','image'].includes(type))throw Error('Choisis une image ou une vidéo.');
  if(engine==='fal'&&(!model||model.kind!==type))throw Error('Choisis un modèle compatible.');
  return scenes.map(scene=>{
    if(!scene.prompt?.trim())throw Error(`Le prompt de « ${scene.title} » est vide.`);
    const frame=startingImage(scene);
    if(engine==='fal'&&!frame)throw Error(`« ${scene.title} » nécessite une image de départ.`);
    const outputDuration=type==='video'&&engine==='fal'?(duration==='scene'?modelDuration(scene.duration,model):Number(duration)):scene.duration;
    if(type==='video'&&engine==='fal'&&!model.durations.includes(outputDuration))throw Error('Durée non prise en charge par ce modèle.');
    const adapted={...scene,duration:outputDuration};
    let prompt=generationPrompt(adapted,type,false);
    if(engine==='fal')prompt+=`\n\nREFERENCE DELIVERY: Only ONE starting image is attached to this request. Treat any image numbers or extra references mentioned above as historical creative context, not additional supplied files. Preserve the identity, costume, product design, composition and painted texture visible in this single starting image.`;
    if(instruction.trim())prompt+=`\n\nSHARED DIRECTOR NOTE FOR THIS NEW TAKE (takes precedence where conflicting):\n${instruction.trim()}`;
    if(engine==='fal'&&prompt.length>12000)throw Error(`Le prompt complet de « ${scene.title} » dépasse 12 000 caractères. Raccourcis le prompt du plan ou la direction commune.`);
    return {sceneId:scene.id,type,prompt,modification:instruction.trim(),references:copy(scene.references||[]),blocking:copy(scene.blocking),duration:outputDuration,...(frame?{startingImage:frame}:{})};
  });
}
