

console.log('settings.js - START');

// go through user_info
//for (tagCatergoryId in userInfo['default_filters']) {  
//  console.log(`> - - - - ${tagCatergoryId} \\ `);   
//  for (tag of userInfo['default_filters'][tagCatergoryId]){
//    console.log(tag);
//  }  
//}

function toggleTagInCategory(button) {

  var tag = button.id.replace('tag_btn_id_', '');            
  
  var tagCat = button.parentNode.id.replace('did_','');
  
  //console.log(`${tagCat} - ${tag} - ${userInfo['default_filters'][tagCat]}`);
  
  if ( userInfo['default_filters'][tagCat].includes(tag) ){
    //console.log(`${tag} - FROM ON to OFF`);
    button.classList.add("ftb_none");
    button.classList.remove("ftb_set");

    // remove tag from category - userInfo['default_filters'][tagCat].delete(tag)
    userInfo['default_filters'][tagCat] = userInfo['default_filters'][tagCat].filter( function(tagsToKeep) { return tagsToKeep !== tag; } )

  } else {
    //console.log(`${tag} - FROM OFF to ON`);
    button.classList.add("ftb_set");
    button.classList.remove("ftb_none");

    // add tag back to category
    userInfo['default_filters'][tagCat].push(tag)
  }
  //console.log(`${tagCat} - ${tag} - ${userInfo['default_filters'][tagCat]}`);
  console.log(userInfo);
  postUpdateSettingsToServer();
}


document.addEventListener('click', clickHandler);

function clickHandler(e) {
  //console.log("\n-\n-\n");
  //console.log(e);
  //console.log(e.target);
  //console.log(e.target.parentNode.id);
  //console.log(e.target.parentNode.classList);  
  
  if (e.target.id.includes('tag_btn_id_')) { // its a tag - toggle it
    toggleTagInCategory(e.target);
    
  } else if (e.target.id === 'igd_btn_id') {
    input = document.getElementById('add_igd_form');
    
    console.log(`IGD EXC = ${input.value}`); console.log(input);
    
    if ( input.value === '' ) return; // dont add blanks

    // TODO - add viewport update
    //df = userInfo['default_filters']['ingredient_exc'];
    //df.indexOf(input.value) === -1 ? df.push(input.value) : console.log(`ALREADY PRESENT: ${input.value} <`);    
    ts = userInfo['tag_sets']['ingredient_exc'];
    ts.indexOf(input.value) === -1 ? ts.push(input.value) : console.log(`ALREADY PRESENT: ${input.value} <`);

    //userInfo['default_filters']['ingredient_exc'] = [];
    //userInfo['tag_sets']['ingredient_exc'] = [];
    postUpdateSettingsToServer();    
  }
  
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

  // most compatible of the 4 loop/iter solutions - all at bottom!
  
  for (var i=0; i < buttons.length; i++) {
    
    if (buttons[i].id.includes('tag_btn_id_')) { // found one set it / or not!
      
      tag = buttons[i].id.replace('tag_btn_id_', '');            
      
      tagCat = buttons[i].parentNode.id.replace('did_','');
      
      // console.log(`${tagCat} - ${tag} - ${userInfo['default_filters'][tagCat]}`);
      
      if ( userInfo['default_filters'][tagCat].includes(tag) ){
        //console.log('ON');
        buttons[i].classList.add("ftb_set");
        buttons[i].classList.remove("ftb_none");
        
      } else {
        //console.log('OFF');
        buttons[i].classList.add("ftb_none");
        buttons[i].classList.remove("ftb_set");
      }
      
    } else {
      continue; // its a nav bat button or other
    }
    
  }  
}




function postUpdateSettingsToServer(){

  // TODO - store setting locally - register with dtk_storage

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


//function fillInTagButtons(e){
//    
//  buttons = document.getElementsByTagName('button');
//
//  // most compatible of teh 4 solutions
//  //
//  //for (var i=0; i < buttons.length; i++) {
//  //  
//  //  if (buttons[i].id.includes('tag_btn_id_')) { // found one set it / or not!
//  //    
//  //    tag = buttons[i].id.replace('tag_btn_id_', '');            
//  //    
//  //    tagCat = buttons[i].parentNode.id.replace('did_','');
//  //    
//  //    console.log(`${tagCat} - ${tag} - ${userInfo['default_filters'][tagCat]}`);
//  //    
//  //    if ( userInfo['default_filters'][tagCat].includes(tag) ){
//  //      console.log('ON');
//  //      buttons[i].classList.add("ftb_set");
//  //      buttons[i].classList.remove("ftb_none");
//  //      
//  //    } else {
//  //      console.log('OFF');
//  //      buttons[i].classList.add("ftb_none");
//  //      buttons[i].classList.remove("ftb_set");
//  //    }
//  //    
//  //  } else {
//  //    continue; // its a nav bat button or other
//  //  }
//  //  
//  //}
//
//  // Converting Collection to Array - not a lot of difference
//  //
//  //Array.from(buttons).forEach( button => {
//  //  if (button.id.includes('tag_btn_id_')) { // found one set it / or not!
//  //    
//  //    tag = button.id.replace('tag_btn_id_', '');            
//  //    
//  //    tagCat = button.parentNode.id.replace('did_','');
//  //    
//  //    console.log(`${tagCat} - ${tag} - ${userInfo['default_filters'][tagCat]}`);
//  //    
//  //    if ( userInfo['default_filters'][tagCat].includes(tag) ){
//  //      console.log('ON');
//  //      button.classList.add("ftb_set");
//  //      button.classList.remove("ftb_none");
//  //      
//  //    } else {
//  //      console.log('OFF');
//  //      button.classList.add("ftb_none");
//  //      button.classList.remove("ftb_set");
//  //    }
//  //    
//  //  } else {
//  //    return; // its a nav bat button or other
//  //  }
//  //});
//    
//  // Converting Collection to Array - and using filter
//  //    
//  //Array.from(buttons).filter( function(button) {    
//  //  return button.id.includes('tag_btn_id_'); // collect if true  
//  //})
//  //.forEach(function(button){
//  //    tag = button.id.replace('tag_btn_id_', '');            
//  //    
//  //    tagCat = button.parentNode.id.replace('did_','');
//  //    
//  //    console.log(`${tagCat} - ${tag} - ${userInfo['default_filters'][tagCat]}`);
//  //    
//  //    if ( userInfo['default_filters'][tagCat].includes(tag) ){
//  //      console.log('ON');
//  //      button.classList.add("ftb_set");
//  //      button.classList.remove("ftb_none");
//  //      
//  //    } else {
//  //      console.log('OFF');
//  //      button.classList.add("ftb_none");
//  //      button.classList.remove("ftb_set");
//  //    }    
//  //});
//  
//  //for (var button of buttons) {
//  //  if (button.id.includes('tag_btn_id_')) { // found one set it / or not!
//  //    
//  //    tag = button.id.replace('tag_btn_id_', '');            
//  //    
//  //    tagCat = button.parentNode.id.replace('did_','');
//  //    
//  //    console.log(`${tagCat} - ${tag} - ${userInfo['default_filters'][tagCat]}`);
//  //    
//  //    if ( userInfo['default_filters'][tagCat].includes(tag) ){
//  //      console.log('ON');
//  //      button.classList.add("ftb_set");
//  //      button.classList.remove("ftb_none");
//  //      
//  //    } else {
//  //      console.log('OFF');
//  //      button.classList.add("ftb_none");
//  //      button.classList.remove("ftb_set");
//  //    }
//  //    
//  //  } else {
//  //    continue; // its a nav bat button or other
//  //  }    
//  }
