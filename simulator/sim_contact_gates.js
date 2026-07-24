// sim-contact-gates: acceptance gates for the simulator's DRAWING layer.
// Verifies drawn finger<->tooth contact at every strike and Geneva pin-slot
// tracking across a full 400-year Gregorian cycle. The engine has its own
// gates; this holds the picture to the same standard.
const fs=require('fs');
const html=fs.readFileSync(process.argv[2]||'oechslin-v151-simulator.html','utf8');
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
 'get OFF_M(){return OFF_M},get OFF_F(){return OFF_F},get OFF_L(){return OFF_L},'+
 'get K(){return {DDR,DBODY,DTIP,SUNORB,LTIP,RTIP,STN_M,STN_F,STN_L,PITCH}}};');
const S_=globalThis.__sim,K=S_.K,d2r=Math.PI/180;

function fingerTip(offDeg){const a=(180-offDeg-(S_.st.h/24)*360)*d2r;
 return [K.DDR+K.DTIP*Math.cos(a),K.DTIP*Math.sin(a)];}
function toothGap(offDeg,stn,OFF,ks){
 const phi=S_.phiDeg(),spin=(19/12)*phi,ft=fingerTip(offDeg);
 const aM=(stn+phi)*d2r,mc=[K.SUNORB*Math.cos(aM),K.SUNORB*Math.sin(aM)];
 let best=1e9;
 for(const k of ks){const ta=(spin+OFF+3.817+k*30)*d2r; // drawn flank offset (fwd)
  const tt=[mc[0]+K.LTIP*Math.cos(ta),mc[1]+K.LTIP*Math.sin(ta)];
  best=Math.min(best,Math.hypot(tt[0]-ft[0],tt[1]-ft[1]));}
 return best;}
function boardValley(){ // 24h finger enters a board VALLEY and drives the flank
 const phi=S_.phiDeg(),ft=fingerTip(0);
 const fAz=Math.atan2(ft[1],ft[0])/d2r;
 let miss=1e9;
 for(let k=0;k<31;k++){let dd=((fAz-(phi+k*K.PITCH))%360+360)%360;
  miss=Math.min(miss,Math.min(dd,360-dd));}
 const pen=K.RTIP-Math.hypot(ft[0],ft[1]);
 return {miss,pen};}
function genevaMiss(){ // pin azimuth vs nearest receiver slot axis (deg)
 const st=S_.st,yf=(st.mon+(st.pos-1)/31)/12,armA=58.8-(yf-0.4543)*360;
 const phi=103.75-armA;if(phi<-44.5||phi>44.5)return null;
 const fr=phi*d2r,adv=45+Math.atan2(30.8*Math.sin(fr),43.55-30.8*Math.cos(fr))/d2r;
 const P=(st.face!==(((st.yr-2027)%4)+4)%4)?1:0,ang=(st.face-P)*90+adv;
 const armR=armA*d2r,px=10.35+30.8*Math.cos(armR),py=-42.3+30.8*Math.sin(armR);
 const pz=Math.atan2(py,px)/d2r;let best=1e9;
 for(let k=0;k<4;k++){let dd=((pz-(ang-31.25+k*90))%360+360)%360;
  best=Math.min(best,Math.min(dd,360-dd));}
 return best;}

const TOL=[1.0,1.7];  // tip-to-tip at the hour, flank-riding at frac 0.366 -> ~1.33 nominal
const acc={mon:[0,1e9,-1e9],feb:[0,1e9,-1e9],leap:[0,1e9,-1e9],day:[0,1e9,-1e9]};
let leapPass=0,genevaWorst=0,camFail=0,fails=[];
function tally(a,g,tag){a[0]++;a[1]=Math.min(a[1],g);a[2]=Math.max(a[2],g);
 if(g<TOL[0]||g>TOL[1])fails.push(`${tag} ${S_.st.yr}-${S_.st.mon+1}-${S_.st.pos}: ${g.toFixed(2)}mm`);}
const t0=Date.now(),yrEnd=S_.st.yr+400;
let daySample=0;
while(S_.st.yr<yrEnd){
 S_.advanceHours(20-S_.st.h);          // to 20:00
 for(let i=0;i<4;i++){S_.advanceHours(1);
  const e=S_.st.evt;
  if(Math.abs(S_.st.h-21)<1e-9&&/LEAP satellite tooth/.test(e))
   tally(acc.leap,toothGap(45,K.STN_L,S_.OFF_L,[0]),'leap');
  else if(Math.abs(S_.st.h-21)<1e-9&&/retracted/.test(e))leapPass++;
  if(Math.abs(S_.st.h-22)<1e-9&&/feb fixed tooth/.test(e))
   tally(acc.feb,toothGap(30,K.STN_F,S_.OFF_F,[0]),'feb');
  if(Math.abs(S_.st.h-23)<1e-9&&/month long tooth/.test(e))
   tally(acc.mon,toothGap(15,K.STN_M,S_.OFF_M,[0,8,9,10,11]),'mon');
  if(Math.abs(S_.st.h-24)<1e-9||S_.st.h===0){
   if(daySample%97===0){const b=boardValley();
    acc.day[0]++;acc.day[1]=Math.min(acc.day[1],b.pen);acc.day[2]=Math.max(acc.day[2],b.pen);
    if(Math.abs(b.miss-1.533)>0.25)fails.push(`day flank ${S_.st.yr}-${S_.st.mon+1}-${S_.st.pos}: valley-ctr ${b.miss.toFixed(2)}deg (want 1.53)`);
    if(b.pen<0.9||b.pen>1.4)fails.push(`day pen ${S_.st.yr}-${S_.st.mon+1}-${S_.st.pos}: ${b.pen.toFixed(2)}mm`);}
   daySample++;}}
 const gm=genevaMiss();if(gm!==null)genevaWorst=Math.max(genevaWorst,gm);
 // cam face at read: parked (outside engagement) the drawn face at 0deg must be st.face
 const st=S_.st,yf=(st.mon+(st.pos-1)/31)/12,phi2=103.75-(58.8-(yf-0.4543)*360);
 if(phi2<-46||phi2>46){
  const P=(st.face!==(((st.yr-2027)%4)+4)%4)?1:0,ang=((st.face-P)*90+(phi2>46?90:0));
  const q=((Math.round(ang/90))%4+4)%4; // face q at read solves ang - q*90 === 0
  if(q!==st.face)camFail++;}
}
console.log(`400-year cycle scanned in ${((Date.now()-t0)/1000).toFixed(0)}s`);
const row=(n,a)=>console.log(`  ${n}: ${a[0]} strikes, gap ${a[1].toFixed(2)}..${a[2].toFixed(2)} mm`);
row('month (23h)',acc.mon);row('feb (22h)',acc.feb);row('leap (21h, armed)',acc.leap);
console.log(`  leap passes (retracted): ${leapPass}`);
console.log(`  daily (24h, sampled): ${acc.day[0]} strikes, valley penetration ${acc.day[1].toFixed(2)}..${acc.day[2].toFixed(2)} mm`);
console.log(`  geneva pin-slot worst miss: ${genevaWorst.toFixed(3)} deg`);
console.log(`  cam-face-at-read mismatches: ${camFail}`);
const ok=fails.length===0&&genevaWorst<0.5&&camFail===0;
if(fails.length)console.log('  contact failures:',fails.slice(0,8).join(' | '),fails.length>8?`(+${fails.length-8})`:'');
console.log(ok?'ALL DRAWN-CONTACT GATES PASS':'*** GATE FAILURES ***');
process.exit(ok?0:1);
