// probe script

//# load most recent dtk post for user (dtk - daily tracker)
//# render blank html, with simple JS to POST status (THIS javascript)
//# post user, device, dt_date from dtk in local storage on device
//# compare to data for user on server
//# if dt_date on device is before 5AM today (set by user) store the dtk



// from server
// var ts = dtk['dtk_rcp']['dt_date'];   // dtk timestamp on server

// retrieve userUUID from local storage
// TODO implement users / login / sessions 
var userUUID = '014752da-b49d-4fb0-9f50-23bc90e44298';

// on device
var dbgOut = document.getElementById('debug_op');

var dtkLocal;


// TODO -break out into local storage utils - also in track_items.js
// load dtk from local storage - if present
if (typeof(Storage) !== "undefined") {
  lastSavedFile = window.localStorage.getItem('lastSavedFile'); // key = 'lastSavedFile'
  console.log(`LASTSAVED FILENAME = ${lastSavedFile} <<`);
} else {
  console.log(`NO LOCAL STORAGE SUPPORT <<`);
}

// JSON.parse(string, function)
    // create object from JSON string, func can be used for further conversion
  
// JSON.stringify(obj, replacer, space)  // space - tab spaces, replacer filter function
    // var obj = { "name":"John", "age":30, "city":"New York"};
    // var myJSON = JSON.stringify(obj);

// load dtk object to ssm / 'disc' / nvm 
lastSavedFile = window.localStorage.getItem('lastSavedFile');         // load name of last saved file
dtkLocal = JSON.parse( window.localStorage.getItem(lastSavedFile) );  // key = content of lastSavedFile
  

console.log("Loaded DTK:");
console.log(dtkLocal);
console.log("<<\n<<\n<<\n<<");


//console.log()
var dbgTxt = `Date timestamp:${dtkLocal['dtk_rcp']['dt_date']}`;
var blank = "";
dbgTxt += `<br>HRD UUID: ${userUUID}`;
dbgTxt += `<br>DTK UUID: ${dtkLocal['dtk_user_info']['UUID']}`;
dbgTxt += `<br>${lastSavedFile}`;
dbgTxt += `<br>: ${blank}`;
dbgTxt += `<br>: ${blank}`;

dbgOut.innerHTML = dbgTxt;

// no lib for initial simple id - but give theis a go fingerprintjs2
// navigator.appName
// navigator.appVersion
// navigator.platform
// navigator.userAgent
fingerprint = {}


console.log("POSTING DTK");

fetch( '/synch_n_route', {
  method: 'POST',                                             // method (default is GET)
  headers: {'Content-Type': 'application/json' },             // JSON
  body: JSON.stringify( { 'user':userUUID, 'dtk':dtkLocal } )      // Payload        

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





// fingerprinting code

var fingerprintReport = function () {
  var d1 = new Date()
  Fingerprint2.get( function(components) {
    var murmur = Fingerprint2.x64hash128(components.map(function (pair) { return pair.value }).join(), 31);
    var d2 = new Date();
    var time = d2 - d1;

    console.log(`==> FP: ${murmur}`);
    console.log(`==> appName: ${navigator.appName}`);
    console.log(`==> appVersion: ${navigator.appVersion}`);
    console.log(`==> platform: ${navigator.platform}`);
    console.log(`==> userAgent: ${navigator.userAgent}`);
    console.log("==> time:", time);

    //document.querySelector("#time").textContent = time
    //document.querySelector("#fp").textContent = murmur
    //var details = ""
    //if(hasConsole) {
      //console.log("time", time);
      //console.log("fingerprint hash", murmur);
    //}
    //for (var index in components) {
    //  var obj = components[index]
    //  var line = obj.key + " = " + String(obj.value).substr(0, 100)
    //  if (hasConsole) {
    //    console.log(line)
    //  }
    //  details += line + "\n"
    //}
    //document.querySelector("#details").textContent = details
  })
}

var cancelId;
var cancelFunction;

// see usage note in the README
// 
if (window.requestIdleCallback) {                     // check to see if requestIdleCallback available
  cancelId = requestIdleCallback(fingerprintReport);  // run fingerprintReport() when browser idle
  cancelFunction = cancelIdleCallback
} else {
  cancelId = setTimeout(fingerprintReport, 500)       // use timeout if requestIdleCallback NOT available
  cancelFunction = clearTimeout
}

//document.querySelector("#btn").addEventListener("click", function () {
//  if (cancelId) {
//    cancelFunction(cancelId)
//    cancelId = undefined
//  }
//  fingerprintReport()
//})



