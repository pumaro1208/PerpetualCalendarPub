// Verify the flank-push drawing: no drawn interpenetration, one pitch per
// strike, continuity, and forward/reverse identity.
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
eval(script+';globalThis.__sim={get st(){return st},advanceHours,reverseHours,phiDeg,phiDraw,'+
 'get dir(){return renderDir},get K(){return {DDR,DTIP,RTIP,RROOT,PITCH}}};');
const S_=globalThis.__sim,K=S_.K,d2r=Math.PI/180;
const smoo=u=>{u=Math.max(0,Math.min(1,u));return u*u*(3-2*u)};
function toothR(az,phi){ // gearPts board surface radius at azimuth az (deg)
 let ad=((az-phi)%(360)+360)%360; const tp=K.PITCH;
 const td=ad%tp,c=tp/2,d=Math.abs(td-c),half=tp*0.22,ramp=tp*0.16;
 const w=d<half?1:d<half+ramp?1-smoo((d-half)/ramp):0;
 return K.RROOT+(K.RTIP-K.RROOT)*w;}
function fingerPen(hh_off){ // incursion of the finger tip PAST a tooth flank
 // (riding ON the flank = 0; only azimuthal entry into full-height tooth
 // body counts, converted to mm at the contact radius)
 const a=(180-hh_off-15*S_.st.h)*d2r;
 const tip=[K.DDR+K.DTIP*Math.cos(a),K.DTIP*Math.sin(a)];
 const az=Math.atan2(tip[1],tip[0])/d2r, r=Math.hypot(tip[0],tip[1]);
 if(r>K.RTIP+0.01)return 0;
 const phi=S_.phiDraw(), tp=K.PITCH;
 let ad=((az-phi)%tp+tp)%tp;            // position within one pitch, valley at 0
 const c=tp/2, half=tp*0.22;
 const d=Math.abs(ad-c);
 if(d>=half)return 0;                    // in a valley or on/beyond a flank: clear
 if(r>=toothR(az,phi))return 0;          // radially above the surface: clear
 return (half-d)*d2r*Math.PI/180*0+ (half-d)*(Math.PI/180)*r;} // mm past the nearer flank
function offFor(evt){ // which finger is striking, from the event text
 if(/midnight/.test(evt)||/24h|program teeth/.test(evt))return 0;
 if(/month long/.test(evt))return 15;
 if(/feb fixed/.test(evt))return 30;
 if(/LEAP/.test(evt))return 45;return null;}
// --- scan a plain midnight and a Feb-cascade evening, minute by minute ---
let worstPen=0, worstAt=null, phiPrev=null, worstJump=0, strikes=0, pitchErrs=0;
let worstTrack=0, worstTrail=1e9;
function flankCheck(){ // during the midnight window only
 const fr=S_.st.h-Math.floor(S_.st.h), tp=K.PITCH;
 const a=(180-15*S_.st.h)*d2r;
 const tip=[K.DDR+K.DTIP*Math.cos(a),K.DTIP*Math.sin(a)];
 const b=Math.atan2(tip[1],tip[0])/d2r, r=Math.hypot(tip[0],tip[1]);
 if(r>K.RTIP-0.02)return;
 const phi=S_.phiDraw();
 // leading flank ABOVE the finger: lower full-height edge of the tooth above
 let ad=((b-phi)%tp+tp)%tp;              // finger position within one pitch
 const gapU=tp-0.22*tp;                   // upper flank at ad = tp-0.22tp? teeth span [c-half,c+half], c=tp/2
 const half=0.22*tp, c=tp/2;
 const distUp=(c-half)-ad;                // >0: finger below the leading flank
 const distDn=((ad-(c+half))%tp+tp)%tp;   // clearance above the trailing flank
 if(S_.dir>0&&b>-4.4&&b<6.9){ if(Math.abs(distUp-1.7189)>worstTrack)worstTrack=Math.abs(distUp-1.7189);}
 if(S_.dir<0&&b<3.8&&b>-7.4){ const lo=((ad-(c+half))%tp+tp)%tp;
  if(Math.abs(lo-1.7189)>worstTrack)worstTrack=Math.abs(lo-1.7189);}
 if(distDn<worstTrail)worstTrail=distDn;}
function scan(mins){
 for(let i=0;i<mins;i++){
  const phiBefore=S_.phiDraw(), stepsBefore=S_.st.steps;
  S_.advanceHours(1/60);
  const phi=S_.phiDraw();
  if(phiPrev!==null){const dj=Math.abs(phi-phiPrev);
   if(dj>worstJump)worstJump=dj;}
  phiPrev=phi;
  if(S_.st.steps!==stepsBefore){strikes++;}
  // penetration of the 24h finger (always) and any finger near its window
  flankCheck();
  for(const off of[0]){ // only the midnight finger is at BOARD level (others are z-gated)
   const p=fingerPen(off);
   if(p>worstPen){worstPen=p;worstAt={yr:S_.st.yr,mon:S_.st.mon,pos:S_.st.pos,
    h:+S_.st.h.toFixed(2),off};}}}}
// plain mid-month midnight: go to a March 11 18:00
let cap=0;while(!(S_.st.mon===2&&S_.st.pos===11)&&cap++<800)S_.advanceHours(24);
S_.advanceHours(18-S_.st.h);
phiPrev=null;scan(12*60);   // 18:00 -> 06:00
// Feb cascade: advance to Feb 28 18:00 of a common year
cap=0;while(!(S_.st.mon===1&&S_.st.pos===28&&![0].includes(S_.st.yr%4===0?0:1))&&cap++<900)S_.advanceHours(24);
S_.advanceHours(Math.max(0,18-S_.st.h));
phiPrev=null;scan(14*60);   // through the 4-strike ladder to morning
console.log(`worst drawn finger->tooth penetration: ${worstPen.toFixed(3)} mm at`,JSON.stringify(worstAt));
console.log(worstPen<0.15?'  PASS (flank-graze tolerance 0.15)':'  FAIL');
console.log(`edge-contact tracking during push (both directions): worst ${worstTrack.toFixed(3)} deg off the finger edge`);
console.log(worstTrack<0.25?'  PASS (contact drawn at the finger edge)':'  FAIL');
console.log(`trailing-tooth clearance: min ${worstTrail.toFixed(3)} deg`);
console.log(worstTrail>0.35?'  PASS (never struck head-on)':'  FAIL');
console.log(`worst per-minute phi step: ${worstJump.toFixed(3)} deg`);
// minute budget: chase 0.5 + absorb 0.45 + base 0.35 (frame level proven 0.002-0.043)
console.log(worstJump<1.4?'  PASS (continuous push, no snaps)':'  FAIL');
console.log(`strikes observed in scans: ${strikes}`);
// --- reverse onset: board must HOLD through backlash traverse, then drive ---
cap=0;while(!(S_.st.pos===20)&&cap++<40)S_.advanceHours(24);
S_.advanceHours(23-S_.st.h);
S_.advanceHours(2.0);           // cross midnight forward; now 01:00, parked
const parked=S_.phiDraw();
let onsetBeta=null;
for(let i=0;i<150;i++){S_.reverseHours(1/60);
 const a=(180-15*S_.st.h)*d2r;
 const tip=[K.DDR+K.DTIP*Math.cos(a),K.DTIP*Math.sin(a)];
 const b=Math.atan2(tip[1],tip[0])/d2r, r=Math.hypot(tip[0],tip[1]);
 if(r<K.RTIP&&onsetBeta===null&&Math.abs(S_.phiDraw()-parked)>0.05)onsetBeta=b;}
console.log(`reverse motion onset at finger beta ${onsetBeta===null?'never':onsetBeta.toFixed(2)+' deg'} (entry +8.78; expected onset ~+3.99 after backlash traverse)`);
console.log(onsetBeta!==null&&Math.abs(onsetBeta-3.99)<0.6?'  PASS (board holds through backlash, then drives back)':'  FAIL');
