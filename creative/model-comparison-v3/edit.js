import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';

// Native Higgsedit recipe. CONVERSE_MODEL selects seedance25, kling3 or veo31.
// CONVERSE_WORK is an input directory containing timeline.json and media/.
export default async ({project,media,text,rect}) => {
  const model=process.env.CONVERSE_MODEL;
  const root=process.env.CONVERSE_WORK;
  if(!model||!root) throw new Error('Set CONVERSE_MODEL and CONVERSE_WORK');
  const timeline=JSON.parse(fs.readFileSync(path.join(root,model,'timeline.json'),'utf8'));
  const out=path.join(root,model,'renders');fs.mkdirSync(out,{recursive:true});
  const projectDir=path.join(root,model,'native-project');
  const p=await project({dir:projectDir,size:'1920x1080',fps:24,background:'#000000'});
  execFileSync('higgsedit',['fonts','add',projectDir,'Inter:400','Inter:600','Inter:900'],{stdio:'inherit'});
  const cache=new Map();
  const add=async(file)=>{if(!cache.has(file))cache.set(file,await p.add(path.join(root,file)));return cache.get(file);};
  const label=(s,x,y,w,h,size=40,weight=400,color='#252821')=>text(s,{x,y,width:w,height:h,fontFamily:'Inter',fontSize:size,fontWeight:weight,color,lineHeight:1.15,align:'left'});
  for(const shot of timeline.shots){
    const h=await add(shot.file);
    const nodes=[media({file:h,x:0,y:0,width:1920,height:1080,fit:'cover',trimStart:shot.source_in_seconds,muted:true})];
    if(shot.id==='B15') nodes.push(
      rect({x:0,y:0,width:1920,height:1080,fill:{kind:'linear',angle:90,stops:[{offset:0,color:'#10110e',opacity:.8},{offset:.38,color:'#10110e',opacity:.62},{offset:.69,color:'#10110e',opacity:0},{offset:1,color:'#10110e',opacity:0}]}}),
      label('CONVERSE.',110,390,930,115,88,900,'#f5f1e8'),
      label('CONSERVE\nWHAT MATTERS.',110,540,930,230,64,600,'#f5f1e8')
    );
    // Every picture uses a composition lane: no spine/overlay overlap ambiguity.
    p.compose(nodes,{at:shot.start,dur:shot.duration,name:shot.id+' '+model});
  }
  // Common editorial phone insert: exact readable text is authored, not generated.
  const photo=await add('shared/phone-photo.png');
  const phone=[
    rect({x:0,y:0,width:1920,height:1080,fill:'#1c1915'}),
    rect({x:597,y:20,width:726,height:1040,fill:'#070807',radius:60}),
    rect({x:615,y:38,width:690,height:1004,fill:'#eeece6',radius:45}),
    rect({x:855,y:53,width:210,height:28,fill:'#090a09',radius:14}),
    label('Conversation',660,110,575,55,37,600),
    rect({x:650,y:185,width:620,height:404,fill:'#dddcd3',radius:24}),
    media({file:photo,x:678,y:207,width:315,height:198,fit:'cover',radius:8,muted:true}),
    label('Rafa · 1970',1017,248,200,100,29,600),
    label('What was my\ngrandfather like?',678,441,535,115,40,600),
    label('Message',682,934,530,54,31,400,'#85867e'),
    rect({x:858,y:1011,width:204,height:6,fill:'#5e6258',radius:3})
  ];
  p.compose(phone,{at:15,dur:7,name:'Shared phone insert'});
  p.compose(label('Thinking…',680,644,530,55,33,400,'#85867e'),{at:15,dur:1.6,name:'Brief loading beat'});
  p.compose([
    label('AI',681,629,500,42,26,600,'#777b70'),
    text("I don't have enough\ninformation about him.",{x:681,y:684,width:558,height:158,fontFamily:'Inter',fontSize:38,fontWeight:400,color:'#262922',lineHeight:1.23,animate:[{property:'opacity',from:0,to:1,at:0,duration:.22,easing:'linear'}]})
  ],{at:16.6,dur:5.4,name:'Exact assistant answer'});
  if(Math.abs(p.duration()-76)>1/48)throw new Error('Expected76seconds');
  await p.frame(19,path.join(out,'phone-proof.png'));
  await p.frame(74,path.join(out,'cover.png'));
  const report=await p.render(path.join(out,'picture-only.mp4'),{depth:8,bitrate:6000000,concurrency:2,shards:4});
  fs.writeFileSync(path.join(out,'native-render-report.json'),JSON.stringify(report,null,2));
};
