// high level functionality
// https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API
// https://developer.mozilla.org/en-US/docs/Web/API/Document/visibilitychange_event
//
// detect when app goes in/out of visibility

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
dtkLocalState = 'waitingToLoad';

// TODO - implement DTK event handling
// loadFromServer, invalidateYield (dtkLocal has additions, recalculate & store), storeToServer (cache & write through), 
// states: waitingToLoad, loadedValid (synched w/ server), yieldInvalid (dtkLocal has additions, recalculate & store), 


// If if hiding store DTK state
// if showing, load DTK state
function handleVisibilityChange() {
  
  if (document[hidden]) {
    // going into hiding - on the lamb store DTK to cache (and server if available)
    console.log(`GONE DARK - storing dtkLocal to cache & server ${dtkLocalState}`);
    dtkLocalState = 'yieldInvalid'; // updates may occur serverside
    console.log(dtkLocal);
    // store dtkLocal
    console.log(`dtkLocalState: ${dtkLocalState} <`);
    
  } else {
    // coming out to play - load latest DTK from cache (and server if available)
    console.log(`HELOOO THERE I'm BACK - no action needed: ${dtkLocalState}`);
    
    // store dtkLocal
    console.log(`dtkLocalState: ${dtkLocalState} <`);
  
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