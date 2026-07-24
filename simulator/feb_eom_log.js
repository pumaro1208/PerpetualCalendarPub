// feb_eom_log.js — full forensic log: Feb end-of-month cascade, slow-mo
// granularity (3 sim-seconds per step), forward then backward. Logs per step:
// h, base phi, drawFix, per-pair overlap at the drawn position, jam state.
const fs=require('fs');
const html=fs.readFileSync('oechslin-v151-simulator.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
function mkCtx(){return new Proxy({},{get(t,p){
 if(p==='canvas')return cv;if(p==='measureText')return()=>({width:12});
 if(p==='createLinearGradient'||p==='createRadialGradient')return()=>({addColorStop(){}});
 return()=>undefined},set(){return true}})}
const cv={width:1360,height:1170,style:{},getContext:()=>ctx,addEventListener(){},
 setPointerCapture(){},getBoundingClientRect:()=>({left:0,top:0,width:1360,height:1170})};
const ctx=mkCtx();const els={};
const mkEl=id=>els[id]??={id,style:{},textContent:'',innerHTML:'',value:'50',checked:false,
 addEventListener(){},appendChild(){},click(){},getContext:()=>ctx};
global.document={getElementById:id=>id==='cv'?cv:mkEl(id),addEventListener(){},
 createElement:()=>mkEl('t'+Math.random()),querySelector:()=>mkEl('q'),body:mkEl('b')};
global.window=global;global.performance={now:()=>Date.now()};
global.requestAnimationFrame=()=>0;global.devicePixelRatio=1;
eval(script+';globalThis.__s={get st(){return st},advanceHours,reverseHours,phiDeg,phiDraw,_overlap,'+
 'get jam(){return jamInfo},get fix(){return drawFix},'+
 'get O(){return {OFF_M,OFF_F,OFF_L,STN_M,STN_F,STN_L}}};');
const S=globalThis.__s,O=S.O;
const P=[['L21',O.STN_L,O.OFF_L,[0],45],['F22',O.STN_F,O.OFF_F,[0],30],
         ['M23',O.STN_M,O.OFF_M,[0,240,270,300,330],15]];
const STEP=3/3600;                       // 3 sim-seconds: slow-mo granularity
const lines=[];
let prevDraw=null, events=0;
function logStep(dirName){
 const base=S.phiDeg(), draw=S.phiDraw(), fix=S.fix;
 const ov=P.filter(([n,a,b,c,d])=>S._overlap(draw,a,b,c,d)).map(([n])=>n).join(',');
 const jump=prevDraw===null?0:Math.abs(draw-prevDraw); prevDraw=draw;
 const jam=S.jam?('JAM['+S.jam.pair+']'):'';
 if(ov||jam||jump>0.35||events<3){
  lines.push(`${dirName} h=${S.st.h.toFixed(4)} pos=${S.st.pos} base=${base.toFixed(3)} `+
   `fix=${fix.toFixed(3)} jump=${jump.toFixed(3)} ovl=[${ov}] ${jam}`);}
 return {jam:!!S.jam, jump};
}
let cap=0;while(!(S.st.yr===2027&&S.st.mon===1&&S.st.pos===28)&&cap++<900)S.advanceHours(24);
S.advanceHours(20.5-S.st.h);
lines.push('=== FORWARD Feb-28 cascade, 3 s steps, 20:30 -> 00:40 ===');
let maxJumpF=0,jamF=null,frozen=false;
for(let i=0;i<Math.round(4.17/STEP)&&!frozen;i++){
 const h0=S.st.h; S.advanceHours(STEP);
 if(Math.abs(S.st.h-h0)<1e-12){frozen=true;lines.push('TIME REFUSED (jam gate) at h='+h0.toFixed(4));break;}
 const r=logStep('FWD');
 maxJumpF=Math.max(maxJumpF,r.jump);
 if(r.jam&&!jamF)jamF=S.st.h.toFixed(4);
}
lines.push(`FWD summary: first jam=${jamF||'none'}  max draw jump=${maxJumpF.toFixed(3)} deg/step  frozen=${frozen}`);
// back out if frozen, then reverse pass
if(frozen){for(let i=0;i<400;i++)S.reverseHours(STEP);}
let c2=0;while(!(S.st.mon===2&&S.st.pos===1)&&c2++<3000)S.advanceHours(1);
S.advanceHours(0.6-S.st.h+0);            // Mar 1, 00:36
prevDraw=null;
lines.push('=== REVERSE Feb-28 cascade, 3 s steps, Mar-1 00:36 -> 20:30 ===');
let maxJumpR=0,jamR=null,frozenR=false;
for(let i=0;i<Math.round(4.17/STEP)&&!frozenR;i++){
 const h0=S.st.h, d0=S.st.day; S.reverseHours(STEP);
 if(Math.abs(S.st.h-h0)<1e-12&&S.st.day===d0){frozenR=true;lines.push('TIME REFUSED (jam gate) at h='+h0.toFixed(4));break;}
 const r=logStep('REV');
 maxJumpR=Math.max(maxJumpR,r.jump);
 if(r.jam&&!jamR)jamR=S.st.h.toFixed(4);
}
lines.push(`REV summary: first jam=${jamR||'none'}  max draw jump=${maxJumpR.toFixed(3)} deg/step  frozen=${frozenR}`);
fs.writeFileSync('feb-eom-forensic.log',lines.join('\n'));
console.log(lines.filter(l=>/summary|JAM|REFUSED|===/.test(l)).join('\n'));
console.log('full log: '+lines.length+' lines -> feb-eom-forensic.log');
