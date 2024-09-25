// high level functionality
// https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API
// https://developer.mozilla.org/en-US/docs/Web/API/Document/visibilitychange_event
//
// detect when app goes in/out of visibility

var userUUID = '014752da-b49d-4fb0-9f50-23bc90e44298';

// Set the name of the hidden property and the change event for visibility
var hidden, visibilityChange;                 // document[hidden] 
if (typeof document.hidden !== "undefined") { // Opera 12.10 and Firefox 18 and later support 
  hidden = "hidden";
  visibilityChange = "visibilitychange";                  // event name for version
} else if (typeof document.msHidden !== "undefined") {
  hidden = "msHidden";
  visibilityChange = "msvisibilitychange";                // event name for version
} else if (typeof document.webkitHidden !== "undefined") {
  hidden = "webkitHidden";
  visibilityChange = "webkitvisibilitychange";            // event name for version
}
 
//var videoElement = document.getElementById("videoElement");
var dtkLocal = {};
var dtkState = 'waitingToLoad';

var timeNowSinceEpoch = Date.now();
console.log(`timeNowSinceEpoch: ${timeNowSinceEpoch}`);


// bootstrap userInfo
// userInfoLocal stored on Device
// userInfo passed from Server
// use most recent update_time_stamp when loading
var userInfoLocal = {'UUID': userUUID,
  'update_time_stamp': 1727281788799,         // use old stamp so always updated
  'default_filters': {'allergens': ['dairy', 'soya'],
                      'ingredient_exc': [],
                      'tags_exc': [],
                      'tags_inc': [],
                      'type_exc': [],
                      'type_inc': ['amuse',
                                   'bao',
                                   'batter']},
  'fav_rcp_ids': [1321, 1228, 1187, 1191, 395, 2032],
  'name': 'carter'};

// Load userInfo from local storage if available server if not.
function loadUserInfo() {

  var storedUserInfo = localStorage.getItem('userInfo');
  storedUserInfo = JSON.parse(storedUserInfo);

  // compare passed in userInfo
  if (storedUserInfo) {    
    if (userInfoLocal['update_time_stamp'] < storedUserInfo['update_time_stamp']){
      userInfoLocal = storedUserInfo;         // 1
    }
  } else {
    // Load from server if not available in local storage
    fetchUserInfoFromServer();
  }
}

// Save userInfo to local storage
function saveUserInfo(callerUserInfo = null) {
  console.log(`saveUserInfo: ${callerUserInfo.default_filters.type_inc}`);

  if (callerUserInfo) {  // update userInfoLocal if newer
    if (callerUserInfo['update_time_stamp'] > userInfoLocal['update_time_stamp']){
      console.log(`callerUserInfo - more recent - SAVING`);
      userInfoLocal = callerUserInfo;
    }
  } 
  localStorage.setItem('userInfo', JSON.stringify(userInfoLocal));
}

// Fetch userInfo from server
function fetchUserInfoFromServer() {
  console.log('fetchUserInfoFromServer');

  fetch('/settings', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json'},              // JSON
    body: JSON.stringify({'action': 'retrieve', 'user': userUUID})  // Payload        
  }).then(function(response) {
    return response.json();
  }).then(function(jsonResp) {
    if (jsonResp.user_info) {
      userInfo = jsonResp.user_info;
      console.log('Retrieved userInfo:', userInfo);
      saveUserInfo(userInfo);
    } else {
      console.error('Failed to retrieve userInfo');
    }
  });
}

// Update userInfo on server
function updateUserInfoOnServer(userInfo) {
  console.log('updateUserInfoOnServer');

  userInfo['update_time_stamp'] = Date.now(); // timeNowSinceEpoch
  console.log(userInfo);

  saveUserInfo(userInfo);   // save locally first

  fetch( '/settings', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json' },             // JSON
    body: JSON.stringify( { 'user':userUUID, 'user_info':userInfo } )      // Payload        
  
  }).then( function(response) {    
    return response.json();
  
  }).then( function(jsonResp) {
    //window.location.replace('/tracker');
    //window.location.replace('/weigh_in');
    console.log(`setting UPDATED? - ${jsonResp}`);
  });  
  
}

// Load userInfo when the script is loaded
loadUserInfo();

// Example usage: Update userInfo and save it
function updateUserInfo(newInfo) {
  Object.assign(userInfo, newInfo);
  saveUserInfo();
  updateUserInfoOnServer();
}




// TODO - implement DTK event handling
// loadFromServer, invalidateYield (dtkLocal has additions, recalculate & store), storeToServer (cache & write through), 
// states: waitingToLoad, loadedValid (synched w/ server), yieldInvalid (dtkLocal has additions, recalculate & store), 


// If if hiding store DTK state
// if showing, load DTK state
function handleVisibilityChange() {
  
  if (document[hidden]) {
    // going into hiding - on the lamb store DTK to cache (and server if available)
    console.log(`GONE DARK - storing dtkLocal to cache & server ${dtkState}`);
    dtkState = 'yieldInvalid'; // updates may occur serverside
    console.log(dtkLocal);
    // store dtkLocal
    console.log(`dtkState: ${dtkState} <`);
    // store userInfo (allergy settiings) - postUpdateSettingsToServer(); - 
    
    
  } else {
    // coming out to play - load latest DTK from cache (and server if available)
    console.log(`HELOOO THERE I'm BACK - no action needed: ${dtkState}`);
    
    // store dtkLocal
    console.log(`dtkState: ${dtkState} <`);
  
  }
}

// Warn if the browser doesn't support addEventListener or the Page Visibility API
if (typeof document.addEventListener === "undefined" || hidden === undefined) {
  console.log("** W A R N I N G ** addEventListener or the Page Visibility API - NOT SUPPORTED: Rewuires browser such as Google Chrome or Firefox, that supports the Page Visibility API.");
} else {
  // Handle page visibility change   
  document.addEventListener(visibilityChange, handleVisibilityChange, false);
                                                                //      ^------- ??
  // TODO - implement DTK event handling
  // loadFromServer, invalidateYield (dtkLocal has additions, recalculate & store), storeToServer (cache & write through), 
  // states: waitingToLoad, loadedValid (synched w/ server), yieldInvalid (dtkLocal has additions, recalculate & store), 
  // https://stackoverflow.com/questions/20835768/addeventlistener-on-custom-object
  // https://github.com/component/emitter
  // https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
  //
  //dailyTracker.addEventListener("pause", function(){
  //  document.title = 'Paused';
  //}, false);
  //  
  //// When the video plays, set the title.
  //videoElement.addEventListener("play", function(){
  //  document.title = 'Playing'; 
  //}, false);

}