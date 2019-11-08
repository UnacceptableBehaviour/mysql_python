// probe script

var dbgOut = document.getElementById('debug_op');

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
var page_report = '';


var storeFingerprint = function () {
  var d1 = new Date();  
  var fingerprint = {};
  
  Fingerprint2.get( function(components) {
    fingerprint['fp'] = Fingerprint2.x64hash128(components.map(function (pair) { return pair.value }).join(), 31);
  
    var d2 = new Date();
    var time = d2 - d1;
    fingerprint['timeTaken'] = time;
    console.log(`==> FP: ${fingerprint}`);
    console.log(fingerprint);

    if (typeof(Storage) !== "undefined") {
      window.localStorage.setItem( 'fingerprint', JSON.stringify(fingerprint) );
      console.log(`FINGERPRINT stored on device <<`);
    } else {
      page_report += "\nFINGERPRINT NOT stored on device <<"
      console.log(`NO LOCAL STORAGE SUPPORT <<`);
    }    
    
  })
}

fingerprint = localStorage.getItem("fingerprint");
fingerprint['appName']    = navigator.appName;
fingerprint['platform']   = navigator.platform;
fingerprint['userAgent']  = navigator.userAgent;
console.log('FINGERPRINT stored on device << S');
console.log(fingerprint);
console.log(navigator.appName);
console.log(navigator.platform);
console.log(navigator.userAgent);
console.log(fingerprint['appName']  );
console.log(fingerprint['platform'] );
console.log(fingerprint['userAgent']);
console.log('FINGERPRINT stored on device << E');
if ( fingerprint === null) {

  // shiming https://developers.google.com/web/updates/2015/08/using-requestidlecallback#why_should_i_use_requestidlecallback
  // https://www.npmjs.com/package/fingerprintjs2
  //
  if (window.requestIdleCallback) {         // check to see if requestIdleCallback available
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


// JSON.parse(string, function)
    // create object from JSON string, func can be used for further conversion
  
// JSON.stringify(obj, replacer, space)  // space - tab spaces, replacer filter function
    // var obj = { "name":"John", "age":30, "city":"New York"};
    // var myJSON = JSON.stringify(obj);


// var dtkLocal; declared in dtk_storage.js
//
// TODO -break out into local storage utils (dtk_storage.js) - also in track_items.js
// load dtk from local storage - if present


if (typeof(Storage) !== "undefined") {
  //
  // it's possible nothing is currently stored locally!
  //
  // load dtk object to ssm / 'disc' / nvm                      // key = 'lastSavedFile'
  lastSavedFile = window.localStorage.getItem('lastSavedFile'); // load name of last saved file
  dtkLocal = JSON.parse( window.localStorage.getItem(lastSavedFile) );  // key = content of lastSavedFile
  
  //(compare to server before valid - currently server is required to recalculate the nutrients data)
  dtkState = 'yieldInvalid'; 
  
  console.log(`LASTSAVED FILENAME = ${lastSavedFile} <<`);
} else {
  page_report += "\nNO LOCAL STORAGE SUPPORT <<"
  console.log(page_report);
}

console.log("Loaded LOCALSTORAGE DTK to dtkLocal:");
console.log(dtkLocal);
console.log(`\ndtkState: ${dtkState} <`);
console.log("<<\n<<\n<<\n<<");


// REMOVE - TODO - debug
var dbgTxt = 'dbg blank';
var blank = "";

try {
  
  dbgTxt = `Date timestamp:${dtkLocal['dtk_rcp']['dt_date']}`;
  blank = "";
  dbgTxt += `<br>HRD UUID: ${userUUID}`;
  dbgTxt += `<br>DTK UUID: ${dtkLocal['dtk_user_info']['UUID']}`;
  dbgTxt += `<br>${lastSavedFile}`;
  dbgTxt += `<br>: ${fingerprint}`;
  dbgTxt += `<br>: ${blank}`;
  dbgTxt += `<br>page_report: ${page_report}`;
  dbgTxt += `<br>: ${blank}`;
  dbgTxt += `<br>: ${blank}`;
  
} catch (err) {

  if (dtkLocal === null) {
    console.log("*** WARNING *** NO LOCALSTORAGE DTK! dtkLocal: null");  
  } else {
    console.log("*** WARNING *** ERROR! dtkLocal:", dtkLocal);
    console.log("*** ERROR:\n", err);  
  }

}

dbgOut.innerHTML = dbgTxt;


console.log("Gettting DTK from Server (POST to /synch_n_route");

fetch( '/synch_n_route', {
  method: 'POST',                                             // method (default is GET)
  headers: {'Content-Type': 'application/json' },             // JSON
  body: JSON.stringify( { 'user':userUUID, 'dtk':dtkLocal, 'fp': fingerprint } )      // Payload        

}).then( function(response) {  
  return response.json();
}).then( function(dtk_w_route) {
  console.log("  - - - - - - - - data S");
  console.log(dtk_w_route);
  console.log(dtk_w_route['route']);
  console.log("  - - - - - - - - data E");
  // if it's a NEW day go to weigh in page    \
  // if SAME day go to tracker page            \ - - detected server side
  window.location.replace(dtk_w_route['route']);
});





