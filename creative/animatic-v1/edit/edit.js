import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';

// Run from repository root: higgsedit build creative/animatic-v1/edit/edit.js
// Rebuilds this new animatic project; do not use on a manually edited canonical project.
export default async ({project, media, text, rect}) => {
  const root = process.env.CONVERSE_ROOT || process.cwd();
  const timeline = JSON.parse(fs.readFileSync(path.join(root, 'creative/animatic-v1/edit/timeline.json'), 'utf8'));
  const p = await project({dir:path.join(root, 'creative/animatic-v1/native-project'),size:'1920x1080',fps:24,background:'#141611'});
  execFileSync('higgsedit',['fonts','add',path.join(root,'creative/animatic-v1/native-project'),'Caveat:700','Inter:900','Inter:600'],{stdio:'inherit'});
  const handles = new Map();
  for (const shot of timeline.shots) {
    if (!handles.has(shot.file)) handles.set(shot.file, await p.add(path.join(root,shot.file)));
    const h = handles.get(shot.file);
    const at = shot.start_seconds, dur = shot.duration_seconds;
    if (shot.media_type === 'image') {
      // A restrained editorial push is explicitly distinguished from generated motion.
      p.compose(media({file:h,x:0,y:0,width:1920,height:1080,fit:'cover',
        animate:shot.shot_id==='S24' ? [] : [{property:'scale',from:1,to:1.03,at:0,duration:dur,easing:'linear'}]
      }),{at,dur,name:shot.shot_id+' still insert'});
    } else if (shot.shot_id === 'S26') {
      // Keep this picture and its endline on native composition lanes.
      // Mixing a spine cut with a new overlay here collides in this hosted CLI.
      p.compose(media({file:h,x:0,y:0,width:1920,height:1080,fit:'cover',trimStart:shot.source_in_seconds}),{at,dur,name:'S26 closing picture'});
    } else if (shot.required_crop_pixels) {
      const c=shot.required_crop_pixels, scale=1920/c.width;
      p.compose(media({file:h,x:-c.x*scale,y:-c.y*scale,width:h.width*scale,height:h.height*scale,fit:'fill',trimStart:shot.source_in_seconds}),{at,dur,name:shot.shot_id+' editorial crop'});
    } else {
      p.cut(h,{from:shot.source_in_seconds,dur,at,fit:'cover'});
    }
  }
  // Flat tongue insert: old initials already present, new initials appear in the edit.
  p.compose(text('R.M.',{x:765,y:323,width:380,height:115,fontFamily:'Caveat',fontSize:102,fontWeight:700,color:'#c7bea5',align:'center'}),{at:66,dur:3,name:'Rafa initials'});
  p.compose(text('L.M.',{x:790,y:450,width:370,height:115,fontFamily:'Caveat',fontSize:102,fontWeight:700,color:'#e8e2cb',align:'center',animate:[{property:'opacity',from:0,to:1,at:0,duration:.25,easing:'linear'}]}),{at:66.9,dur:2.1,name:'Luna initials editorial reveal'});
  p.compose([
    rect({x:0,y:0,width:1920,height:1080,fill:{kind:'linear',angle:90,stops:[{offset:0,color:'#11120e',opacity:.78},{offset:.42,color:'#11120e',opacity:.42},{offset:.72,color:'#11120e',opacity:0},{offset:1,color:'#11120e',opacity:0}]}}),
    text('CONVERSE.',{x:120,y:375,width:850,height:100,fontFamily:'Inter',fontSize:78,fontWeight:900,color:'#f4f0e6',align:'left'}),
    text('CONSERVE\nWHAT MATTERS.',{x:120,y:510,width:880,height:210,fontFamily:'Inter',fontSize:63,fontWeight:600,lineHeight:1.15,color:'#f4f0e6',align:'left'})
  ],{at:72,dur:4,name:'Four-second endline'});
  if(Math.abs(p.duration()-76)>1/48) throw new Error('Timeline must be exactly 76 seconds');
  const outputs=path.join(root,'creative/animatic-v1/renders');
  fs.mkdirSync(outputs,{recursive:true});
  await p.frame(73.5,path.join(outputs,'cover.png'));
  await p.frame(67.75,path.join(outputs,'initials-proof.png'));
  const report=await p.render(path.join(outputs,'picture-only.mp4'),{depth:8,bitrate:6000000,concurrency:2,shards:4});
  fs.writeFileSync(path.join(outputs,'native-render-report.json'),JSON.stringify(report,null,2));
};
