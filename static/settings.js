

console.log('settings.js - START');

// go through user_info
for (tagCatergoryId in userInfo['default_filters']) {
  
  console.log(`> - - - - ${tagCatergoryId} \\ `);
  //console.log(userInfo['default_filters'][tagCatergoryId]);
  
  for (tag of userInfo['default_filters'][tagCatergoryId]){
    console.log(tag);
  }
  
}

document.addEventListener('click', clickHandler);

function clickHandler(e) {
  
  console.log("\n-\n-\n");
  console.log(e);
  console.log(e.target);
  console.log(e.target.parentNode.id);
  console.log(e.target.parentNode.classList);  
  
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// div    id="did_tags_inc" `did_${tagCatergoryId}`     // contains is category of tags
// button id='tag_btn_id_nuts' value='nuts'             // contains a tag
//
// class ftb_set  - present in list highlighted             // css - control the background col
// class ftb_none - NOT present in list, not highlighted
//
// document.getElementById("div1").classList.add("ftb_set / ftb_none");
// document.getElementById("div1").classList.remove("ftb_none / ftb_set");
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
document.addEventListener('DOMContentLoaded', fillInTagButtons);
function fillInTagButtons(e){
    
  buttons = document.getElementsByTagName('button');

  for (var i=0; i < buttons.length; i++) {
    
    if (buttons[i].id.includes('tag_btn_id_')) { // found one set it / or not!
      
      tag = buttons[i].id.replace('tag_btn_id_', '');            
      
      tagCat = buttons[i].parentNode.id.replace('did_','');
      
      console.log(`${tagCat} - ${tag} - ${userInfo['default_filters'][tagCat]}`);
      
      if ( userInfo['default_filters'][tagCat].includes(tag) ){
        console.log('ON');
        buttons[i].classList.add("ftb_set");
        buttons[i].classList.remove("ftb_none");
        
      } else {
        console.log('OFF');
        buttons[i].classList.add("ftb_none");
        buttons[i].classList.remove("ftb_set");
      }
      
    } else {
      continue; // its a nav bat button or other
    }
    
  }

    
  //Array.from(buttons).forEach( button => {
  // console.log(button.id);
  // // no next / break / loop! :/
  //});
    
  //buttons.filter(function(element) {
  //  return element.shouldBeProcessed;
  //})
  //.forEach(function(element){
  //  doSomeLengthyOperation();
  //});
  
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