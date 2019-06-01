function reflect_selected_tag_filters () {
  
  // lets see what we've got
  for (var key in data){
    
    console.log(`=- - - data -key: ${key} < - -<`);
    
    var str = JSON.stringify(data[key], null, 2);      
    
    console.log(str);
    console.log(' - - - - - - - - ---<');
    
  }
    
  // next step - use AJAX? to do this w/o reload
  console.log("------- tag list -------S");
  data['chosen_tag_filters'].forEach( function(tag){
    console.log(tag);
    document.getElementById(`tag_btn_id_${tag}`).style.background='#B8DB0D';
  });
  console.log("------- tag list -------E");
  
}

// attach an event listener to tag selector form
try {
  document.querySelector('#form_filter_tags').addEventListener('load', reflect_selected_tag_filters());
}
catch(error) {
  // console.error(error);
}



// document.addEventListener('DOMContentLoaded', fill_in_nutrients_table());
console.log('button_experiments.js - EXECUTED');