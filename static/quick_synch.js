// probe script

//# load most recent dtk post for user (dtk - daily tracker)
//# render blank html, with simple JS to POST status (THIS javascript)
//# post user, device, dt_date from dtk in local storage on device
//# compare to data for user on server
//# if dt_date on device is before 5AM today (set by user) arechive the dtk

// fingerprinting code - - - - - < 

// no lib for initial simple id - but give this a go: fingerprintjs2
// navigator.appName
// navigator.platform
// navigator.userAgent
var fingerprint = {}; 

var storeFingerprint = function () {
  var d1 = new Date();  
  var fingerprint = {};
  
  Fingerprint2.get( function(components) {
    fingerprint['fp'] = Fingerprint2.x64hash128(components.map(function (pair) { return pair.value }).join(), 31);
    fingerprint['appName'] = navigator.appName;
    fingerprint['platform'] = navigator.platform;
    fingerprint['userAgent'] = navigator.userAgent;
  
    var d2 = new Date();
    var time = d2 - d1;
    fingerprint['timeTaken'] = time;
    console.log(`==> FP: ${fingerprint}`);
    console.log(fingerprint);

    if (typeof(Storage) !== "undefined") {
      window.localStorage.setItem( 'fingerprint', JSON.stringify(fingerprint) );
      console.log(`FINGERPRINT stored on device <<`);
    } else {
      console.log(`NO LOCAL STORAGE SUPPORT <<`);
    }    
    
  })
}

fingerprint = localStorage.getItem("fingerprint");
if ( fingerprint === null) {

  // shiming https://developers.google.com/web/updates/2015/08/using-requestidlecallback#why_should_i_use_requestidlecallback
  // https://www.npmjs.com/package/fingerprintjs2
  //
  if (window.requestIdleCallback) {          // check to see if requestIdleCallback available
    requestIdleCallback(storeFingerprint);  // run storeFingerprint() when browser idle
  } else {
    setTimeout(storeFingerprint, 500)       // use timeout if requestIdleCallback NOT available
  }
} 


// from server
// var ts = dtk['dtk_rcp']['dt_date'];   // dtk timestamp on server
// retrieve userUUID from local storage
// TODO implement users / login / sessions 
var userUUID = '014752da-b49d-4fb0-9f50-23bc90e44298';

// on device
var dbgOut = document.getElementById('debug_op');

// JSON.parse(string, function)
    // create object from JSON string, func can be used for further conversion
  
// JSON.stringify(obj, replacer, space)  // space - tab spaces, replacer filter function
    // var obj = { "name":"John", "age":30, "city":"New York"};
    // var myJSON = JSON.stringify(obj);


var dtkLocal;
// TODO -break out into local storage utils - also in track_items.js
// load dtk from local storage - if present
if (typeof(Storage) !== "undefined") {
  // load dtk object to ssm / 'disc' / nvm                      // key = 'lastSavedFile'
  lastSavedFile = window.localStorage.getItem('lastSavedFile'); // load name of last saved file
  dtkLocal = JSON.parse( window.localStorage.getItem(lastSavedFile) );  // key = content of lastSavedFile
  
  console.log(`LASTSAVED FILENAME = ${lastSavedFile} <<`);
} else {
  console.log(`NO LOCAL STORAGE SUPPORT <<`);
}

console.log("Loaded DTK:");
console.log(dtkLocal);
console.log("<<\n<<\n<<\n<<");


// REMOVE - TODO - debug
var dbgTxt = `Date timestamp:${dtkLocal['dtk_rcp']['dt_date']}`;
var blank = "";
dbgTxt += `<br>HRD UUID: ${userUUID}`;
dbgTxt += `<br>DTK UUID: ${dtkLocal['dtk_user_info']['UUID']}`;
dbgTxt += `<br>${lastSavedFile}`;
dbgTxt += `<br>: ${fingerprint}`;
dbgTxt += `<br>: ${blank}`;

dbgOut.innerHTML = dbgTxt;


console.log("POSTING DTK");

fetch( '/synch_n_route', {
  method: 'POST',                                             // method (default is GET)
  headers: {'Content-Type': 'application/json' },             // JSON
  body: JSON.stringify( { 'user':userUUID, 'dtk':dtkLocal, 'fp': fingerprint } )      // Payload        

}).then( function(response) {
  
  console.log("  - - - -|- - - - response");
  console.log(response);
  console.log("  - - - -|- - - -");
  console.log(typeof(response));
  console.log("  - - - -|- - - -");
  
  //return response.text();
  return response.json();

}).then( function(dtk_w_route) {
  console.log("  - - - - - - - - data S");
  console.log(dtk_w_route);
  console.log(dtk_w_route['route']);
  console.log("  - - - - - - - - data E");
  //window.location.replace(dtk_w_route['route']);
});





