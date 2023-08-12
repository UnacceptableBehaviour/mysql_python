

console.log('settings.js - START');

// go through user_info
//for (tagCatergoryId in userInfo['default_filters']) {  
//  console.log(`> - - - - ${tagCatergoryId} \\ `);   
//  for (tag of userInfo['default_filters'][tagCatergoryId]){
//    console.log(tag);
//  }  
//}


function toggleTagTypeInCategory(button) {

  //var tag = button.id.replace('tag_btn_id_', '');
  var value = button.value;
  
  var tagTypeCat = button.parentNode.id.replace('did_','');
  
  //console.log(`${tagTypeCat} - ${value} - ${userInfo['default_filters'][tagTypeCat]}`);
  
  if ( userInfo['default_filters'][tagTypeCat].includes(value) ){
    //console.log(`${value} - FROM ON to OFF`);
    button.classList.add("ftb_none");
    button.classList.remove("ftb_set");

    // remove value from category - userInfo['default_filters'][tagTypeCat].delete(value)    
    var default_filters = userInfo['default_filters'][tagTypeCat];
    // remove value
    default_filters = default_filters.filter( function(tagsToKeep) { return tagsToKeep !== value; } );
    
    userInfo['default_filters'][tagTypeCat] = default_filters;

  } else {
    //console.log(`${value} - FROM OFF to ON`);
    button.classList.add("ftb_set");
    button.classList.remove("ftb_none");

    // add value back to category
    userInfo['default_filters'][tagTypeCat].push(value);
  }
  
  // typing help for touch screen - add button name to input for no type removal
  if (button.parentNode.id.includes('did_ingredient_exc')) { document.getElementById('add_igd_form').value = value; };
  
  
  //console.log(`${tagTypeCat} - ${value} - ${userInfo['default_filters'][tagTypeCat]}`);
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
  
  if (e.target.id.includes('tag_btn_id_') || e.target.id.includes('type_btn_id_')) { // its a tag - toggle it
    toggleTagTypeInCategory(e.target);
    
  } else if (e.target.id.includes('_igd_btn_id')) {  // and an ingredients to exclude button
    input = document.getElementById('add_igd_form');
    
    console.log(`IGD EXC = ${input.value}`); console.log(input);
    
    if ( input.value === '' ) return; // dont add blanks
    
    if (e.target.id === 'add_igd_btn_id') {      
      ts = userInfo['tag_sets']['ingredient_exc'];           // add ingredient to tag sets to creat button
      ts.indexOf(input.value) === -1 ? ts.push(input.value) : console.log(`ADD - ALREADY PRESENT: ${input.value} <`);
        
      df = userInfo['default_filters']['ingredient_exc'];   // seeing as we're creating the button user probably want it set!
      df.indexOf(input.value) === -1 ? df.push(input.value) : console.log(`ADD - ALREADY PRESENT: ${input.value} <`);    
      
    } else if (e.target.id === 'remove_igd_btn_id') {      
      ts = userInfo['tag_sets']['ingredient_exc'];            // remove ingredient fomr tag_sets 
      var index = ts.indexOf(input.value);
      index === -1 ? console.log(`REMOVE - ALREADY PRESENT: ${input.value} <`) : ts.splice(index, 1);
      
      df = userInfo['default_filters']['ingredient_exc'];     // seeing as we're removing the button remove from user defaults
      index = df.indexOf(input.value);
      index === -1 ? console.log(`REMOVE - ALREADY PRESENT: ${input.value} <`) : df.splice(index, 1);      
    }
    
    postUpdateSettingsToServer();
    
    // TODO - chain promises?
    console.log(`IGD EXC = RELOAD /settings`);
    window.location.replace('/settings');
    
  } else if (e.target.id === 'btn_id_toggle_tags') {     
    // toggle is all element in tag_sets not in default_filters
    let toggle = userInfo['tag_sets']['tags'].filter(item => !userInfo['default_filters']['tags_exc'].includes(item));
    
    // switch
    userInfo['default_filters']['tags_inc'] = userInfo['default_filters']['tags_exc'];
    userInfo['default_filters']['tags_exc'] = toggle;

    fillInTagButtons();
    postUpdateSettingsToServer();

  } else if (e.target.id === 'btn_id_toggle_types') { 
    
    // toggle is all element in tag_sets not in default_filters
    let toggle = userInfo['tag_sets']['types'].filter(item => !userInfo['default_filters']['type_exc'].includes(item));

    // switch
    userInfo['default_filters']['type_inc'] = userInfo['default_filters']['type_exc'];
    userInfo['default_filters']['type_exc'] = toggle;

    fillInTagButtons();
    postUpdateSettingsToServer();
  } else if (e.target.id === 'btn_id_clear_type') { 
    // clear
    userInfo['default_filters']['type_inc'] = userInfo['tag_sets']['types'];
    userInfo['default_filters']['type_exc'] = [];
    fillInTagButtons();
    postUpdateSettingsToServer();

  } else if (e.target.id === 'btn_id_clear_tags') { 
    // clear
    userInfo['default_filters']['tags_inc'] = userInfo['tag_sets']['tags'];
    userInfo['default_filters']['tags_exc'] = [];
    fillInTagButtons();
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
      tagTypeCat = buttons[i].parentNode.id.replace('did_','');
    
    } else if (buttons[i].id.includes('type_btn_id_')) { // found one set it / or not!    
      tagTypeCat = buttons[i].parentNode.id.replace('did_','');

    } else {
      continue; // its a nav bat button or other
    }

    value = buttons[i].value;
    //console.log(`cat:${tagTypeCat} - val:${value}`);
    //console.log(`- user_i:${userInfo['default_filters'][tagTypeCat]}`);

    if ( userInfo['default_filters'][tagTypeCat].includes(value) ){
      //console.log('ON');
      buttons[i].classList.add("ftb_set");
      buttons[i].classList.remove("ftb_none");
      
    } else {
      //console.log('OFF');
      buttons[i].classList.add("ftb_none");
      buttons[i].classList.remove("ftb_set");
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
//  //    tagTypeCat = buttons[i].parentNode.id.replace('did_','');
//  //    
//  //    console.log(`${tagTypeCat} - ${tag} - ${userInfo['default_filters'][tagTypeCat]}`);
//  //    
//  //    if ( userInfo['default_filters'][tagTypeCat].includes(tag) ){
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
//  //    tagTypeCat = button.parentNode.id.replace('did_','');
//  //    
//  //    console.log(`${tagTypeCat} - ${tag} - ${userInfo['default_filters'][tagTypeCat]}`);
//  //    
//  //    if ( userInfo['default_filters'][tagTypeCat].includes(tag) ){
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
//  //    tagTypeCat = button.parentNode.id.replace('did_','');
//  //    
//  //    console.log(`${tagTypeCat} - ${tag} - ${userInfo['default_filters'][tagTypeCat]}`);
//  //    
//  //    if ( userInfo['default_filters'][tagTypeCat].includes(tag) ){
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
//  //    tagTypeCat = button.parentNode.id.replace('did_','');
//  //    
//  //    console.log(`${tagTypeCat} - ${tag} - ${userInfo['default_filters'][tagTypeCat]}`);
//  //    
//  //    if ( userInfo['default_filters'][tagTypeCat].includes(tag) ){
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
