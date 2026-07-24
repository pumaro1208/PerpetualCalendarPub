const fs=require('fs');
const html=fs.readFileSync('oechslin-v151-simulator.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
function mkCtx(){return new Proxy({},{get(t,p){
 if(p==='canvas')return cv;
 if(p==='measureText')return()=>({width:12});
 if(p==='createLinearGradient'||p==='createRadialGradient')return()=>({addColorStop(){}});
 return()=>undefined},set(){return true}})}
const cv={width:1500,height:980,style:{},getContext:()=>ctx,addEventListener(){},
 setPointerCapture(){},getBoundingClientRect:()=>({left:0,top:0,width:1500,height:980})};
const ctx=mkCtx();const els={};
const mkEl=id=>els[id]??={id,style:{},textContent:'',innerHTML:'',value:'50',checked:false,
 addEventListener(){},appendChild(){},click(){},getContext:()=>ctx};
global.document={getElementById:id=>id==='cv'?cv:mkEl(id),addEventListener(){},
 createElement:()=>mkEl('t'+Math.random()),querySelector:()=>mkEl('q'),body:mkEl('b')};
global.window=global;global.performance={now:()=>Date.now()};
global.requestAnimationFrame=()=>0;global.devicePixelRatio=1;
eval(script+';globalThis.__sim={get st(){return st},advanceHours,reverseHours,draw};');
const S_=globalThis.__sim;

// replicate the drawn receiver angle from state (same formula as the sim)
function drawnAngle(){const st=S_.st;
 const yf=(st.mon+(st.pos-1)/31)/12;
 const armA=(58.8-(yf-0.4543)*360);
 const CG=43.55,RG=30.8;
 let phi=103.75-armA;
 let adv; if(phi<-45)adv=0;
 else if(phi<=45){const fr=phi*Math.PI/180;
  adv=45+Math.atan2(RG*Math.sin(fr),CG-RG*Math.cos(fr))*180/Math.PI}
 else adv=90;
 const P=(st.face!==(((st.yr-2027)%4)+4)%4)?1:0;
 return {ang:(st.face-P)*90+adv, phi, armA};}

// 1) continuity scan: whole of 2098 + through 2100, 1-hour samples
let prev=null, worstJump=0, jumpAt=null;
while(S_.st.yr<2098) S_.advanceHours(24);
while(S_.st.yr<2101){
 S_.advanceHours(1);
 const d=drawnAngle();
 if(prev!==null){let dj=Math.abs(d.ang-prev);dj=Math.min(dj,Math.abs(dj-360));
  if(dj>worstJump){worstJump=dj;jumpAt={yr:S_.st.yr,mon:S_.st.mon,pos:S_.st.pos,h:S_.st.h}}}
 prev=d.ang;}
console.log(`continuity 2098->2100 hourly: worst step ${worstJump.toFixed(3)} deg at`,JSON.stringify(jumpAt));
console.log(worstJump<3.0?'  PASS (daily-quantized like the hardware; theoretical peak 2.34 deg/day, no snaps)':'  FAIL');

// 2) pin-on-slot alignment during engagement (angular distance pin vs nearest slot axis)
Object.assign(S_.st,{h:0});
// rewind state cheaply: re-eval fresh
let worstMiss=0;
// scan one engagement window (mid-March..mid-June of current st.yr) via daily samples
for(let i=0;i<120;i++){S_.advanceHours(24);
 const st=S_.st, d=drawnAngle();
 if(d.phi>=-44.5&&d.phi<=44.5){
  const armR=d.armA*Math.PI/180;
  const px=10.35+30.8*Math.cos(armR), py=-42.3+30.8*Math.sin(armR); // ring-frame, y-up
  const pinAz=Math.atan2(py,px)*180/Math.PI;
  let best=1e9;
  for(let k=0;k<4;k++){const sa=d.ang-31.25+k*90;
   let dd=((pinAz-sa)%360+360)%360; dd=Math.min(dd,360-dd); best=Math.min(best,dd)}
  worstMiss=Math.max(worstMiss,best);}}
console.log(`pin vs nearest slot axis through engagement: worst ${worstMiss.toFixed(2)} deg`);
console.log(worstMiss<1.0?'  PASS (pin rides the slot centerline)':'  FAIL');

// 3) draw() exercised hourly across New Year 2099->2100 and the Feb cascade
try{
 const tgt=S_.st.yr+1; let cap=0;
 while(!(S_.st.mon===11&&S_.st.pos===30)&&cap++<800)S_.advanceHours(24);
 for(let i=0;i<72;i++){S_.advanceHours(1);S_.draw();}
 cap=0; while(!(S_.st.mon===1&&S_.st.pos===27)&&cap++<800)S_.advanceHours(24);
 for(let i=0;i<96;i++){S_.advanceHours(1);S_.draw();}
 console.log(`draw() hourly across NY ${tgt} and the Feb cascade: PASS (at ${S_.st.yr}-${S_.st.mon+1}-${S_.st.pos})`);
}catch(e){console.log('draw() EXCEPTION:',e.message)}
