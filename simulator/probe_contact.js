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
eval(script+';globalThis.__sim={get st(){return st},advanceHours,phiDeg,'+
 'get OFF_M(){return OFF_M},get OFF_F(){return OFF_F},get OFF_L(){return OFF_L},get consts(){return {DDR,DBODY,DTIP,SUNORB,LTIP,STN_M,STN_F,STN_L,PITCH}}};');
const S_=globalThis.__sim, K=S_.consts;
const d2r=Math.PI/180;
function gapFor(offDeg,stn,OFF,ks){
 const st=S_.st, phi=S_.phiDeg(), hh=st.h;
 const spin=(19/12)*phi, driveRot=-(hh/24)*360;
 const aF=(180-offDeg+driveRot)*d2r;
 const ftip=[K.DDR+K.DTIP*Math.cos(aF), K.DTIP*Math.sin(aF)];
 const aM=(stn+phi)*d2r;
 const mc=[K.SUNORB*Math.cos(aM), K.SUNORB*Math.sin(aM)];
 let best=1e9,bk=null;
 for(const k of ks){
  const ta=(spin+OFF+k*30)*d2r;
  const tt=[mc[0]+K.LTIP*Math.cos(ta), mc[1]+K.LTIP*Math.sin(ta)];
  const d=Math.hypot(tt[0]-ftip[0],tt[1]-ftip[1]);
  if(d<best){best=d;bk=k}}
 return {gap:best,k:bk};}
function contactGap(){const r=gapFor(15,K.STN_M,S_.OFF_M,[0,8,9,10,11]);
 return {...r,satAz:((K.STN_M+S_.phiDeg())%360+360)%360};}
// sample the next 6 month strikes: at each 23h strike hour (short months + Feb path)
let found=0;
while(found<6){
 S_.advanceHours(1);
 if(Math.abs(S_.st.h-23)<1e-9 && /month long tooth/.test(S_.st.evt)){
  const c=contactGap();
  console.log(`strike ${S_.st.yr}-${String(S_.st.mon+1).padStart(2,'0')} pos${S_.st.pos}: `+
   `finger->tooth tip gap ${c.gap.toFixed(2)} mm (tooth k=${c.k}, sat azimuth ${c.satAz.toFixed(1)} deg)`);
  found++;}}
// feb (22h) and leap (21h) fingers at their strikes
let fFound=0,lFound=0,cap=0;
while((fFound<2||lFound<2)&&cap++<40000){
 S_.advanceHours(1);
 if(Math.abs(S_.st.h-22)<1e-9&&/feb fixed tooth/.test(S_.st.evt)&&fFound<2){
  const g=gapFor(30,K.STN_F,S_.OFF_F,[0]);
  console.log(`feb strike ${S_.st.yr}: gap ${g.gap.toFixed(2)} mm`);fFound++}
 if(Math.abs(S_.st.h-21)<1e-9&&/LEAP satellite tooth/.test(S_.st.evt)&&lFound<2){
  const g=gapFor(45,K.STN_L,S_.OFF_L,[0]);
  console.log(`leap strike ${S_.st.yr}: gap ${g.gap.toFixed(2)} mm`);lFound++}}
