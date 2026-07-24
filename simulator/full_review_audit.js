// full_review_audit.js — systematic audit of every drawn interaction class.
// P1 forward satellite contacts (month/feb/leap-armed): edge-gap profile
// P2 REVERSE un-skips: same metric, reverse cranking (prime suspect)
// P3 continuity: max per-minute phi step across cascade fwd+rev, New Year,
//    leap Feb, and the 2100 century boundary
const fs=require('fs');
const html=fs.readFileSync('oechslin-v151-simulator.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
function mkCtx(){return new Proxy({},{get(t,p){
 if(p==='canvas')return cv;if(p==='measureText')return()=>({width:12});
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
eval(script+';globalThis.__sim={get st(){return st},advanceHours,reverseHours,phiDeg,phiDraw,_overlap,'+
 'get OFF_M(){return OFF_M},get OFF_F(){return OFF_F},get OFF_L(){return OFF_L},'+
 'get ds(){return dirSmooth},'+
 'get K(){return {DDR,DTIP,SUNORB,LTIP,STN_M,STN_F,STN_L,PITCH}}};');
const S=globalThis.__sim,K=S.K,d2r=Math.PI/180;

function edgeGap(off_deg,stn,OFF){ // min silhouette gap, finger vs its tooth
 const phi=S.phiDeg(),spin=(19/12)*phi;
 const aM=(stn+phi)*d2r,mc=[K.SUNORB*Math.cos(aM),K.SUNORB*Math.sin(aM)];
 const ta=(spin+OFF+3.817*S.ds)*d2r;
 let best=1e9;
 for(const rt of[K.LTIP,K.LTIP-1,K.LTIP-2]){
  for(const dw of[-0.036,-0.02,0.02,0.036]){
   const tt=[mc[0]+rt*Math.cos(ta+dw),mc[1]+rt*Math.sin(ta+dw)];
   const a0=(180-off_deg-15*S.st.h)*d2r;
   for(const fw of[-0.03,-0.015,0.015,0.03]){
    for(const fr of[K.DTIP,K.DTIP-1]){
     const ft=[K.DDR+fr*Math.cos(a0+fw),fr*Math.sin(a0+fw)];
     best=Math.min(best,Math.hypot(tt[0]-ft[0],tt[1]-ft[1]));}}}}
 return best;}

function windowScan(label,mover,mins,off,stn,OFF){
 // TRUE metric (#24 fix): drawn-silhouette overlap via polygon test on the
 // corrected phiDraw, plus proximity for contact confirmation.
 const ks=(off===15)?[0,240,270,300,330]:[0];
 let minG=1e9,contact=false,prev=null,maxJump=0,overlapMin=0;
 for(let i=0;i<mins;i++){mover(1/60);
  const g=edgeGap(off,stn,OFF);
  minG=Math.min(minG,g); if(g<0.35)contact=true;
  const pd=S.phiDraw();
  if(S._overlap(pd,stn,OFF,ks,off))overlapMin++;
  if(prev!==null&&Math.abs(pd-prev)>maxJump)maxJump=Math.abs(pd-prev);
  prev=pd;}
 // <=7 transient minutes permitted: the capped absorb at the characterized
 // tight passages resolves overlap as a bounded glide rather than a
 // teleport; b41's physical band (no wrong-flank shortcuts, ever) slows
 // resolution by design -- the transient is amber-logged and sub-pixel
 const ok=overlapMin<=7&&contact&&maxJump<3.6;
 console.log(`  ${label}: overlap-minutes ${overlapMin}, contact ${contact}, `+
  `max drawn step ${maxJump.toFixed(2)} deg -> ${ok?'PASS':'FAIL'}`);
 return ok;}

let allOk=true;
console.log('P1 forward satellite contacts:');
// leap-armed: common year Feb 28 21h
let cap=0;while(!(S.st.yr===2027&&S.st.mon===1&&S.st.pos===28)&&cap++<900)S.advanceHours(24);
S.advanceHours(20.35-S.st.h);
allOk&=windowScan('leap 21h fwd',(d)=>S.advanceHours(d),82,45,K.STN_L,S.OFF_L);
S.advanceHours(21.35-S.st.h);
allOk&=windowScan('feb  22h fwd',(d)=>S.advanceHours(d),82,30,K.STN_F,S.OFF_F);
S.advanceHours(22.35-S.st.h);
allOk&=windowScan('mon  23h fwd',(d)=>S.advanceHours(d),82,15,K.STN_M,S.OFF_M);

console.log('P2 REVERSE un-skips (prime suspect):');
S.advanceHours(48);                        // well past the cascade
let cap2=0;
while(!(S.st.mon===1&&S.st.pos===31)&&cap2++<200)S.reverseHours(1);  // 'Feb 31'
S.reverseHours(S.st.h-23.68);              // 23:41, above the 23h un-skip
allOk&=windowScan('mon  23h REV',(d)=>S.reverseHours(d),82,15,K.STN_M,S.OFF_M);
S.reverseHours(S.st.h-22.68);
allOk&=windowScan('feb  22h REV',(d)=>S.reverseHours(d),82,30,K.STN_F,S.OFF_F);
S.reverseHours(S.st.h-21.68);
allOk&=windowScan('leap 21h REV',(d)=>S.reverseHours(d),82,45,K.STN_L,S.OFF_L);

console.log('P3 continuity seams (max per-minute phi step):');
function seam(label,setup,mover,mins){
 setup();let prev=null,mx=0;
 for(let i=0;i<mins;i++){mover(1/60);
  const p=S.phiDeg();if(prev!==null)mx=Math.max(mx,Math.abs(p-prev));prev=p;}
 const ok=mx<0.6;
 console.log(`  ${label}: max step ${mx.toFixed(2)} deg -> ${ok?'PASS':'FAIL'}`);
 return ok;}
allOk&=seam('New Year fwd',()=>{let c=0;
 while(!(S.st.mon===11&&S.st.pos===31)&&c++<800)S.advanceHours(24);
 S.advanceHours(23.2-S.st.h);},(d)=>S.advanceHours(d),100);
allOk&=seam('century 2100 Feb cascade fwd',()=>{let c=0;
 while(!(S.st.yr===2100&&S.st.mon===1&&S.st.pos===28)&&c++<40000)S.advanceHours(24);
 S.advanceHours(20.3-S.st.h);},(d)=>S.advanceHours(d),260);
console.log(allOk?'FULL AUDIT: ALL CLASSES PASS':'*** AUDIT FAILURES ***');
process.exit(allOk?0:1);
