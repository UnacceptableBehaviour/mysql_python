
//broad brush lets get a feel for it
//anatomy
//
//search {
//  field:      value:       logic:
//    name,       str          matches, contains
//    ingdt,      str/id       matches, contains, exclude     [allegens]
//    cuisine,    str          inc, exc, all, any             [type of tag]
//    tags,       str          inc, exc, all, any
//    stars,      int          >=, <=, ==
//    nutri,      str          limit >=, <=,
//}

// SQL queries

// recipes including a tag: name
//
//cs50_recipes=# SELECT ri_id,ri_name, tags FROM exploded WHERE 'veggie' = ANY(tags);
// ri_id |              ri_name              |                                   tags                                   
//-------+-----------------------------------+--------------------------------------------------------------------------
//   901 | spinach tortilla                  | {veggie,gluten_free,msg,ns_pregnant}
//  2701 | mushroom risotto                  | {veggie,cbs,gluten_free}
//  3101 | goats cheese and spinach omelette | {veggie,gluten_free}
//  3401 | simple beef and onion broth       | {vegan,veggie,cbs,chicken,pork,beef,seafood,s&c,gluten_free,ns_pregnant}
//(4 rows)




searchButton = document.getElementById('but-recipe-search');
searchButton.addEventListener('click', searchForRecipe);

formField = document.getElementById('recipe-search-1-inrow');
formValue = document.getElementById('recipe-search-2-inrow');
formLogic = document.getElementById('recipe-search-3-inrow');

formField.placeholder = 'tags';
formValue.placeholder = 'search string';
formLogic.placeholder = 'contains';



function searchForRecipe (){
  formField.value = 'tags';
  formValue.value = 'vegan';
  formLogic.value = 'contains';
  
  if ( (formField.value === "")|| (formValue.value === "")|| (formLogic.value === "") ) {
    // user pressed SEARCH w/o entering values - see if place holder values valid        
    console.log("INVALID SEARCH VALUES");
    
    // TODO flash the form(s) missing data in red then fade to normal
    
    return;
  }

  var query = {
    field: formField.value,
    value: formValue.value,
    logic: formLogic.value,
  }
  
  var search = [query];

  //query =  = {
  //  field: [formField.value],
  //  value: [formValue.value],
  //  logic: [formLogic.value],
  //}
  
  
  // post info to DB
  fetch( '/search_ingredient', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json' },             // JSON
    body: JSON.stringify( { 'user':userUUID, 'search':search } )      // Payload        
  
  }).then( function(response) {    
    return response.json();
  
  }).then( function(search_response) {
    console.log("AHEM:", search_response);
    // how to something like . .
    // window.location.replace('/db_gallery', recipes=search_response);
    window.location.replace('/db_gallery')
  })
  //.catch(err){
  //  console.log("WTF", err);
  //};
}