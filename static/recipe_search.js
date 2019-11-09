

recordButton = document.getElementById('but-recipe-search-record');
recordButton.addEventListener('click', searchFroRecipe);

formS1 = document.getElementById('recipe-search-1-inrow');
formS2 = document.getElementById('recipe-search-2-inrow');
formS3 = document.getElementById('recipe-search-3-inrow');




function searchFroRecipe (){
  
  if ( (formWeight.value === "")|| (formPCFat.value === "")|| (formPCWater.value === "") ) {
    // user pressed SEARCH w/o entering values - see if place holder values valid        
    console.log("INVALID SEARCH VALUES");
    
    // TODO flash the form(s) missing data in red then fade to normal
    
    return;
  }

  // get details from forms
  // =  formWeight.value;
  // =  formPCFat.value;
  // =  formPCWater.value;
  
  
  // post info to DB
  fetch( '/tracker', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json' },             // JSON
    body: JSON.stringify( { 'user':userUUID, 'dtk':dtk } )      // Payload        
  
  }).then( function(response) {    
    return response.json();
  
  }).then( function(dtk) {
    window.location.replace('/search_ingredient');    
  });
}