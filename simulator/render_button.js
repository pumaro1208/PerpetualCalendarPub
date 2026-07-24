// reproduce Ron's frame: 2027 reverse cascade, 22h un-skip in progress
const fs=require('fs');
const html=fs.readFileSync('oechslin-v151-simulator.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const ops=[];
function recCtx(record){return new Proxy({},{get(t,p){
 if(p==='canvas')return cv;
 if(p==='measureText')return()=>({width:12});
 if(p==='createLinearGradient'||p==='createRadialGradient')return()=>({addColorStop(){}});
 return(...a)=>{if(record)ops.push([p,a])}},
 set(t,p,v){if(record)ops.push(['SET_'+p,[v]]);return true}})}
const cv={width:1360,height:1170,style:{},getContext:()=>ctxMain,addEventListener(){},
 setPointerCapture(){},getBoundingClientRect:()=>({left:0,top:0,width:1360,height:1170})};
const ctxMain=recCtx(true);
const ctxSection=recCtx(false);          // discard section ops for this render
const els={};
const mkEl=id=>els[id]??={id,style:{},textContent:'',innerHTML:'',value:'50',checked:false,
 addEventListener(){},appendChild(){},click(){},
 getContext:()=>id==='cv2'?ctxSection:ctxMain,width:1360,height:440};
global.document={getElementById:id=>id==='cv'?cv:mkEl(id),addEventListener(){},
 createElement:()=>mkEl('t'+Math.random()),querySelector:()=>mkEl('q'),body:mkEl('b')};
global.window=global;global.performance={now:()=>Date.now()};
global.requestAnimationFrame=()=>0;global.devicePixelRatio=1;
eval(script+';globalThis.__sim={get st(){return st},advanceHours,reverseHours,draw};');
const S=globalThis.__sim;
let cap=0;while(!(S.st.yr===2027&&S.st.mon===2&&S.st.pos===1)&&cap++<900)S.advanceHours(24);
S.advanceHours(0.7-S.st.h>0?0.7-S.st.h:24.7-S.st.h);
const dh=(1/60)*3;                       // EXACT reverse-button path, speed 3
const frames=[];
for(let i=0;i<600;i++){
 S.reverseHours(dh);
 const h=S.st.h;
 if(h>21.55&&h<22.45&&S.st.pos>=29){     // the cascade window only
  ops.length=0;S.draw();
  frames.push({h:+h.toFixed(3),pos:S.st.pos,ops:ops.slice()});}}
fs.writeFileSync('frames_button.json',JSON.stringify(frames));
console.log('captured '+frames.length+' cascade-window frames');
