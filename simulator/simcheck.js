// Extract the sim's Gregorian logic and re-verify the acceptance points
const leapG = y => (y%4===0 && y%100!==0) || y%400===0;
// progTouch logic from the sim: armed = (face != shortq) || lobe, gov = yr+1
function febLen(y){ // what the mechanism produces for February of year y
  const lobe = (y%100===0 && y%400!==0);
  const mechLeap = leapG(y) && !lobe ? true : (y%400===0 ? true : (leapG(y) && !lobe));
  // mechanism: leap tooth retracted (29 days) iff face==shortq && !lobe
  // face==shortq occurs exactly when y is div by 4 (programmer phased to leap cycle)
  const faceMatch = (y%4===0);
  const retracted = faceMatch && !lobe;
  return retracted ? 29 : 28;
}
const tests = [[2100,28],[2104,29],[2400,29],[2000,29],[2028,29],[2027,28],[2200,28],[2300,28],[1900,28],[2096,29]];
let ok=true;
for(const [y,exp] of tests){
  const got = febLen(y);
  if(got!==exp){ok=false;console.log(`FAIL ${y}: got ${got} expected ${exp}`)}
  else console.log(`ok   Feb ${y} = ${got}d`);
}
console.log(ok ? "\nGregorian logic: all acceptance points PASS" : "\nFAILURES");
