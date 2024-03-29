
import * as dtkChart from './dtk_chart.js';


const recordButton = document.getElementById('but-weigh-in-record');
recordButton.addEventListener('click', recordWeighInDetails);

const formWeight = document.getElementById('weigh-in-weight-inrow');
const formPCFat = document.getElementById('weigh-in-pc-fat-inrow');
const formPCWater = document.getElementById('weigh-in-pc-water-inrow');

var userUUID = dtk['dtk_user_info']['UUID'];

// TODO use an iterator for this
// set initial values if they're already present (retrurn to page)
console.log(`formWeight.value ${formWeight.value}`);
if ((formWeight.value === "") && (dtk['dtk_weight'] !== 0)) {  
  formWeight.value = dtk['dtk_weight'];
}

console.log(`formPCFat.value ${formPCFat.value}`);
if ((formPCFat.value === "") && (dtk['dtk_pc_fat'] !== 0)) {
  formPCFat.value = dtk['dtk_pc_fat'];
}

console.log(`formPCWater.value ${formPCWater.value}`);
if ((formPCWater.value === "") && (dtk['dtk_pc_h2o'] !== 0)) {
  formPCWater.value = dtk['dtk_pc_h2o'];
}


function recordWeighInDetails (){
  
  if ( (formWeight.value === "")|| (formPCFat.value === "")|| (formPCWater.value === "") ) {
    // user pressed RECORD w/o entering values - see if place holder values valid        
    console.log("INVALID WEIGH IN VALUES");
    
    // TODO flash the form(s) missing data in red then fade to normal
    
    return;
  }
  
  
  // get details from forms
  dtk['dtk_weight'] =  formWeight.value;
  dtk['dtk_pc_fat'] =  formPCFat.value;
  dtk['dtk_pc_h2o'] =  formPCWater.value;
  
  // save to local
  // TODO - creating a JS library
  
  console.log(dtk);
  
  // post info to DB
  fetch( '/tracker', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json' },             // JSON
    body: JSON.stringify( { 'user':userUUID, 'dtk':dtk } )      // Payload        
  
  }).then( function(response) {    
    return response.json();
  
  }).then( function(dtk) {
    window.location.replace('/tracker');
    //window.location.replace('/weigh_in');
  });
}


const dtkCwgt = new dtkChart.DtkChartWithControls( "wic-wgt", "dtkChart_js", {selectedDataSources: ['dtk_weight', 'dtk_weight_av7']} );    
const dtkClip = new dtkChart.DtkChartWithControls( "wic-lip", "dtkChart_js", {selectedDataSources: ['dtk_kg_fat','dtk_kg_fat_av7']} );
const dtkCh20 = new dtkChart.DtkChartWithControls( "wic-h2o", "dtkChart_js", {selectedDataSources: ['dtk_kg_h2o', 'dtk_kg_h2o_av7']} );
