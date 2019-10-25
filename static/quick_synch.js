// probe script

//# load most recent dtk post for user (dtk - daily tracker)
//# render blank html, with simple JS to POST status (THIS javascript)
//# post user, device, dt_date from dtk in local storage on device
//# compare to data for user on server
//# if dt_date on device is before 5AM today (set by user) store the dtk



// from server
var ts = dtk['dtk_rcp']['dt_date'];   // dtk timestamp on server

var uuid = '014752da-b49d-4fb0-9f50-23bc90e44298';

// on device
var dbgOut = document.getElementById('debug_op');

var dtkLocal


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
  
// compare to dtk - select most recent

//dtk = dtkLocal; // ts compare

console.log("Loaded DTK:");
console.log(dtkLocal);
console.log("<<\n<<\n<<\n<<");
    


//console.log()
var dbgTxt = `SERVER timsamp:${ts}`;
var blank = "";
dbgTxt += `<br>UUID: ${uuid}`;
dbgTxt += `<br>${lastSavedFile}`;
dbgTxt += `<br>: ${blank}`;
dbgTxt += `<br>: ${blank}`;

dbgOut.innerHTML = dbgTxt;