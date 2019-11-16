
console.log(dtk);
  
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