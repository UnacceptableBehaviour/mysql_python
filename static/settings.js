

console.log('settings.js - START');

// go through user_info
for (tagCatergoryId in userInfo['default_filters']) {
  
  console.log(`> - - - - ${tagCatergoryId} \\ `);
  //console.log(userInfo['default_filters'][tagCatergoryId]);
  
  for (tag of userInfo['default_filters'][tagCatergoryId]){
    console.log(tag);
  }
  
}
// div    id="did_tags_inc" `did_${tagCatergoryId}`
// button id='tag_btn_id_nuts' value='nuts'
// class ftb_set  - present in list highlighted
// class ftb_none - NOT present in list, not highlighted
//
// document.getElementById("div1").classList.add("classToBeAdded");
// document.getElementById("div1").classList.remove("classToBeRemoved");


document.addEventListener('click', clickHandler);

function clickHandler(e) {
  
  console.log("\n-\n-\n");
  console.log(e);
  console.log(e.target);
  console.log(e.target.parentNode.id);
  console.log(e.target.parentNode.classList);  
  
}

document.addEventListener('DOMContentLoaded', fillInTagButtons);

const TAGCAT = 0;
const TAG = 1;

//function isTagSet(){}

function fillInTagButtons(e){
  console.log('>- - - - - - - - fillInTagButtons <1');
  
  buttons = document.getElementsByTagName('button');
  
  //console.log(buttons);
  
  console.log(typeof buttons);
  
  console.log(buttons.length);
  
  
  //buttons.forEach( e => { console.log(e.target); });  NOPE
  Array.from(buttons).forEach(function(item) {
   console.log(item.id);
  });

  console.log('>- - - - - - - - fillInTagButtons <2');
  
  for (let button of buttons){
    console.log(button.id);
  }
  
  console.log('>- - - - - - - - fillInTagButtons <3');
    
  for (let i=0; i < buttons.length; i++) {
    console.log(buttons[i].id);
    //console.log(i);
  }
  
}



























  
//// post info to DB
//fetch( '/tracker', {
//  method: 'POST',                                             // method (default is GET)
//  headers: {'Content-Type': 'application/json' },             // JSON
//  body: JSON.stringify( { 'user':userUUID, 'dtk':dtk } )      // Payload        
//
//}).then( function(response) {    
//  return response.json();
//
//}).then( function(dtk) {
//  window.location.replace('/tracker');
//  //window.location.replace('/weigh_in');
//});