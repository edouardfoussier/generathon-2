/** Native Higgsedit composition. All image panels remain editable source references. */
import fs from 'node:fs';
import path from 'node:path';
export default async ({ project, frame, text, rect, media, path: vector }) => {
 const root=process.env.MOTION_ROOT||process.cwd();
 const p=await project({dir:path.join(root,'native'),size:'1280x720',fps:24,background:'#ede3cb'});
 const assets={};
 for(const a of JSON.parse(fs.readFileSync(path.join(root,'sources.json'),'utf8'))) assets[a.code]=await p.add(path.join(root,'input',a.code+'.png'));
 const C={paper:'#f4ecdc',ink:'#253338',red:'#c75337',blue:'#163f51',olive:'#667450',gold:'#c49956',white:'#fffaf0'};
 const tw=(property,from,to,duration,at=0,easing='house')=>({property,from,to,duration,at,easing});
 const kf=(property,values)=>({property,keyframes:values.map(([at,value,easing])=>({at,value,...easing?{easing}:{}}))});
 const enter=(delay=0,angle=0)=>[tw('offsetY',80,0,.7,delay),tw('opacity',0,1,.45,delay),tw('rotation',angle-5,angle,.7,delay)];
 const label=(s,x,y,w=500,size=28,color=C.ink,opts={})=>text(s,{x,y,width:w,height:size*2.8,fontFamily:'DM Sans',fontSize:size,color,...opts});
 const hand=(s,x,y,w=800,size=75,color=C.ink,opts={})=>text(s,{x,y,width:w,height:size*2.5,fontFamily:'Caveat',fontSize:size,fontWeight:700,color,...opts});
 const big=(s,x,y,w=1200,size=125,color=C.ink,opts={})=>text(s,{x,y,width:w,height:size*2.5,fontFamily:'Anton',fontSize:size,color,...opts});
 const flat=(x,y,w,h,color,opts={})=>rect({x,y,width:w,height:h,fill:color,...opts});
 const line=(x,y,w,h,color=C.red,opts={})=>vector({d:`M 0 ${h*.65} C ${w*.22} ${h*.1},${w*.4} ${h*.95},${w*.55} ${h*.4} C ${w*.72} 0,${w*.84} ${h*.6},${w} ${h*.2}`,x,y,width:w,height:h,stroke:{color,width:5,cap:'round'},...opts});
 const panel=(code,crop,x,y,w,h,opts={})=>{
   const a=assets[code],cw=a.width*crop[2],ch=a.height*crop[3],s=(code.startsWith('CS')?Math.min:Math.max)(w/cw,h/ch);
   return frame({x,y,width:w,height:h,layout:'none',clip:true,background:C.paper,...opts},[
    media({...(code.startsWith('CS')?{mask:{shape:'path',d:[[.005,.16],[.26,.16],[.3,.34],[.33,.48],[.42,.53],[.44,.65],[.43,.85],[.005,.87]].map((v,i)=>(i?'L ':'M ')+(v[0]*a.width*s)+' '+(v[1]*a.height*s)).join(' ')+' Z'}}:{}),file:a,x:-a.width*crop[0]*s+(w-cw*s)/2,y:-a.height*crop[1]*s+(h-ch*s)/2,width:a.width*s,height:a.height*s,fit:'fill'})]);
 };
 const full=[0,0,1,1],left=[.015,.025,.315,.95],middle=[.34,.025,.31,.95],right=[.68,.025,.31,.95];
 const portrait=[.69,.08,.30,.75];
 const card=(code,crop,x,y,w,h,caption='',angle=0,delay=0,extra={})=>frame({x,y,width:w+24,height:h+65,layout:'none',background:C.white,shadow:{x:3,y:7,blur:12,color:'#00000035'},animate:enter(delay,angle),...extra, ...(extra.animate?{animate:extra.animate.filter((a,i,l)=>l.findLastIndex(b=>b.property===a.property)===i)}:{})},[
   panel(code,crop,12,12,w,h),...(caption?[hand(caption,17,h+15,w,27,C.ink)]:[]),flat(w*.35,-7,w*.25,24,'#dbcaaad9',{animate:[tw('rotation',-6,-6,.1)]})]);
 const paper=(color=C.paper)=>flat(0,0,1280,720,color);
 const specks=()=>[...Array(13)].map((_,i)=>flat((i*131+31)%1270,(i*67+80)%710,2,2,'#9c80573a'));
 const scene=(at,dur,name,nodes)=>p.compose([paper(),...specks(),...nodes],{at,dur,name});
 const circle=(x,y,r,color,opts={})=>flat(x,y,r*2,r*2,color,{radius:r,...opts});
 const year=(s,color=C.red)=>frame({x:40,y:28,width:230,height:73,layout:'none',background:C.paper,animate:enter(.2,-3)},[hand(s,18,5,200,43,C.ink)]);
 // 00—03: mother's voice enters before the illustrated world.
 p.compose([paper(C.paper), ...'LUNA!'.split('').map((ch,i)=>frame({x:160+i*190,y:180+(i%2)*17,width:170,height:240,layout:'none',background:[C.red,C.blue,C.gold,C.ink,C.olive][i],animate:enter(i*.1,(i%2?-1:1)*5)},[big(ch,0,12,170,170,C.paper,{align:'center'})])),label('A PAIR OF SHOES. A WHOLE LIFE.',95,570,1100,23,C.ink,{align:'center',animate:[tw('opacity',0,1,.6,1.2)]})],{at:0,dur:3,name:'01 • Mum calls from downstairs'});
 // Attic: sliding postcards reveal the space, with the teenager held as its own paper layer.
 scene(3,6,'02 • Why keep all this?',[
   panel('CL01N',middle,450,0,830,720,{animate:[tw('scale',1.08,1.0,6,0,'linear')]}),
   flat(0,0,470,720,C.paper),card('CC01N',left,60,160,250,440,'Luna, 2026',-4,.25),
   flat(520,38,600,222,C.paper),hand('Why keep\nall this?',545,58,555,90,C.ink,{motion:{by:'word',from:{opacity:0,y:20},duration:.4,overlap:.6,at:2.6}}),
   line(15,587,1245,100,C.red,{animate:[tw('maskWidth',0,1245,1.2,3)]})]);
 scene(9,4,'03 • One forgotten box',[
   panel('CL01N',left,0,0,1280,720,{animate:[tw('scale',1.03,1.1,4,0,'linear')]}),
   card('CS02N',[.005,.14,.435,.74],140,80,610,465,'R.M.',-7,.15),
   card('CC05N',portrait,840,150,270,340,'Rafael Morales',7,.5),
   hand('Who were you?',520,590,700,69,C.white,{animate:enter(1.2,-4)})]);
 // An editorial phone, drawn natively so every word is readable.
 scene(13,5,'04 • The answer a search cannot give',[
   card('CC05N',portrait,80,110,260,345,'Grandpa',-7,.1),
   frame({x:480,y:42,width:425,height:620,layout:'none',background:'#fafafa',radius:30,shadow:{x:8,y:12,blur:20,color:'#00000024'},animate:enter(0,3)},[
    label('Ask anything',28,30,350,20,'#737373'),flat(24,85,377,2,'#dedbd4'),
    label('Tell me about\nmy grandfather.',28,120,355,36,C.ink,{fontWeight:700}),
    label('Searching memories…',28,300,355,25,'#9d978b',{duration:2}),
    label('Not enough data.',28,335,355,38,C.red,{at:2,duration:3,animate:enter()})]),
   hand('Some things\naren’t online.',940,240,315,59,C.ink,{animate:enter(2,-6)}),
   line(30,595,420,67,C.red,{animate:[tw('maskWidth',0,420,.8,3)]})]);
 scene(18,4,'05 • Put them on',[
   paper(C.blue),hand('Walk into\na memory.',52,78,495,84,C.paper,{motion:{by:'word',from:{opacity:0,y:25},duration:.5,overlap:.5}}),
   card('CS02N',[.005,.14,.435,.74],665,85,480,435,'',5,0,{animate:[...enter(),tw('scale',.95,1.04,4,0,'linear')]}),
   line(-60,570,1380,110,C.gold,{animate:[tw('maskWidth',0,1380,1.5,1)]})]);
 // A lace becomes the story's line. Moving circle is the visual bridge to a basketball.
 scene(22,3,'06 • The thread opens',[
   paper(C.red),big('R.M.',52,30,600,205,C.paper,{animate:[tw('scale',.88,1.2,3,0,'linear')]}),
   line(-200,225,1740,350,C.paper,{animate:[tw('offsetX',-330,160,3,0,'linear')]}),
   circle(500,500,58,C.gold,{animate:[kf('offsetX',[[0,0],[1.3,370],[3,110]]),kf('offsetY',[[0,0],[1.3,-480],[3,-350]]),tw('scale',.5,1.1,3)]})]);
 scene(25,7,'07 • First dream — Bronx 1970',[
   panel('CL02N',left,0,0,1280,720,{animate:[tw('scale',1.05,1.15,7,0,'linear')]}),
   frame({x:40,y:28,width:360,height:70,layout:'none',background:C.paper},[hand('Bronx, 1970',15,4,325,43,C.ink)]),card('CC02N',left,170,125,250,445,'Rafa, 16',-5,.2,{animate:[...enter(.2,-5),kf('offsetY',[[0,100],[.7,0],[3.1,0],[3.35,-80],[3.8,0],[7,0]])]}),
   card('CS01N',[.005,.14,.435,.74],770,355,410,270,'One first step.',6,2.5),
   circle(467,580,43,C.gold,{strokeColor:C.ink,strokeWidth:3,animate:[kf('offsetX',[[0,0],[1.4,280],[2.9,540],[4.5,480],[7,470]]),kf('offsetY',[[0,0],[1.4,-415],[2.9,-430],[4.5,-120],[7,-180]])]}),
   hand('A dream.',800,120,380,83,C.paper,{animate:enter(1,-5)})]);
 scene(32,3,'08 • Footwork is a language',[
   paper(C.blue),card('CS01N',[.005,.14,.435,.74],60,120,490,350,'his',-8,0,{animate:[...enter(0,-8),tw('rotation',-8,6,3)]}),
   card('CS03N',[.005,.14,.435,.74],705,120,475,350,'hers',8,.25,{animate:[...enter(.25,8),tw('rotation',8,-6,2.7,.25)]}),
   hand('And then…',450,555,500,74,C.paper,{animate:enter(.6,-4)}),line(380,40,500,95,C.gold,{animate:[tw('maskWidth',0,500,1,.8)]})]);
 scene(35,6,'09 • Two lives find their rhythm',[
   panel('CL03N',middle,0,0,1280,720,{animate:[tw('scale',1.03,1.1,6,0,'linear')]}),year('1977',C.paper),
   card('CC03N',left,240,120,270,465,'Rafa',-8,.1,{animate:[...enter(.1,-8),kf('rotation',[[0,-8],[1,4],[2,-5],[3,4],[4,-4],[6,3]])]}),
   card('CC06N',left,640,110,270,465,'Elena',7,.3,{animate:[...enter(.3,7),kf('rotation',[[0,7],[1,-4],[2,5],[3,-4],[4,4],[6,-3]])]}),
   hand('Together.',900,65,340,68,C.paper,{animate:enter(1,-6)}),
   line(740,44,460,110,C.red,{animate:[tw('maskWidth',0,460,1,2)]})]);
 scene(41,5,'10 • A promise',[
   panel('CL04N',middle,0,0,1280,720,{animate:[tw('scale',1.06,1.13,5,0,'linear')]}),year('1978',C.paper),
   card('CC03N',middle,350,88,250,470,'',-5,.15),card('CC06N',middle,647,85,270,470,'',5,.35),
   flat(440,616,400,83,C.paper),hand('A promise.',75,621,1130,64,C.ink,{align:'center',animate:enter(.6,-2)}),
   circle(1015,110,66,'#00000000',{strokeColor:C.gold,strokeWidth:10,animate:[tw('scale',0,1,.6,1.5)]})]);
 scene(46,6,'11 • A whole new reason',[
   panel('CL05N',left,0,0,1280,720),year('1979',C.ink),
   card('CC03N',right,58,177,225,394,'Dad',-5,.1),card('CC06N',right,940,177,225,394,'Mum',5,.3),
   card('CC10N',middle,425,105,365,435,'Luna’s mum.',-3,.6,{animate:[...enter(.6,-3),tw('scale',.95,1.08,5.4,.6,'linear')]}),
   flat(300,612,760,87,C.paper),hand('A whole new reason.',75,623,1130,62,C.ink,{align:'center',animate:enter(1.4,-2)})]);
 scene(52,6,'12 • Passing it on',[
   panel('CL05N',middle,0,0,1280,720),year('1995',C.ink),
   card('CC04N',left,88,155,255,410,'Dad',-6,.1),card('CC08N',left,910,155,255,410,'His daughter, 16',6,.2),
   card('CS02N',[.005,.14,.435,.74],404,210,420,300,'Yours now.',-3,.7,{animate:[...enter(.7,-3),tw('offsetX',-80,100,4.5,.8)]}),
   flat(340,28,630,105,C.paper),hand('Love, passed on.',370,40,590,78,C.ink,{animate:enter(.2,-3)})]);
 scene(58,5,'13 • A life is more than data',[
   paper(C.blue),card('CC05N',portrait,100,70,330,420,'Rafa',-7,0),card('CC07N',portrait,485,115,305,388,'Elena',5,.15),
   card('CC09N',portrait,825,80,320,410,'Mum',-3,.3),
   hand('A life worth keeping.',45,618,1180,62,C.paper,{align:'center',animate:enter(.6,-2)}),
   ...Array.from({length:12},(_,i)=>circle((i*233+30)%1260,(i*97+32)%520,1.5,C.paper,{animate:[tw('opacity',.15,1,.8,(i%4)*.3)]}))]);
 scene(63,5,'14 • Called back to the attic',[
   panel('CL01N',middle,0,0,1280,720,{animate:[tw('scale',1.07,1.0,5,0,'linear')]}),
   card('CC01N',portrait,75,85,465,455,'Luna',-4,.2),
   hand('Luna?\nAre you coming down?',655,115,580,69,C.white,{motion:{by:'word',from:{opacity:0,y:20},at:0,duration:.4,overlap:.5}}),
   line(560,550,650,90,C.red,{animate:[tw('maskWidth',0,650,1,2)]})]);
 scene(68,4,'15 • Mom, tell me about Grandpa',[
   paper(C.paper),card('CC01N',portrait,66,75,300,390,'daughter',-5,0),
   card('CC09N',portrait,885,75,300,390,'mother',5,.15),
   card('CS02N',[.005,.14,.435,.74],416,110,420,360,'R.M. → L.M.',-2,.2),
   hand('Mom… tell me about Grandpa.',125,580,1040,64,C.ink,{animate:enter(.1,-3)})]);
 p.compose([paper(C.ink),big('CONVERSE',80,100,1120,190,C.paper,{align:'center',animate:enter(0,0)}),
   line(170,360,940,82,C.red,{animate:[tw('maskWidth',0,940,.7,.35)]}),
   label('CONSERVE WHAT MATTERS.',80,476,1120,49,C.paper,{align:'center',fontWeight:700,letterSpacing:2,animate:[tw('opacity',0,1,.6,.45)]}),
   label('ONE SNEAKER. EVERY GENERATION.',100,625,1080,20,'#bdbaa8',{align:'center',letterSpacing:3,animate:[tw('opacity',0,1,.6,1)]})],{at:72,dur:4,name:'16 • Converse — conserve what matters'});
 fs.mkdirSync(path.join(root,'renders'),{recursive:true});
 fs.writeFileSync(path.join(root,'native-timeline.json'),JSON.stringify(await p.read(),null,2));
 const proofTimes=[1.8,6.6,10.8,16.5,20,23.5,28.5,33.5,38,43.5,49.5,55.5,60.5,65,70,74];
 for (const time of proofTimes) await p.frame(time,`renders/proof-${String(time).replace('.','_')}.png`);
 if(process.env.MOTION_RENDER==='1') {
 const report=await p.render('renders/picture-only.mp4',{bitrate:5500000,shards:12,concurrency:4});
 fs.writeFileSync(path.join(root,'native-render-report.json'),JSON.stringify(report,null,2));
 }
};
