function format_nutrition_table_column_colours(nut_qty, column, lower_threshold, upper_threshold, rda, id_qty, id_hml, id_ri, multiplier ){
                          
  var col_mapping = {
    'LOW':'#3CB938', // green
    'MED':'#FEA150',  // amber
    'HIGH':'#CB2B0B',  // red
  };            

  console.log('- - -');
  console.log(`COL:${column} - ${nut_qty} <`);
  console.log(`LIMITS ${lower_threshold} - ${upper_threshold}`);            
  
  if (nut_qty < lower_threshold) {
    heat = 'LOW';

  } else if ( (nut_qty >= lower_threshold) && (nut_qty <= upper_threshold) ){
    heat = 'MED';
    
  } else {
    heat = 'HIGH';

  }

  console.log(`HEAT: ${heat} < - COLOUR: ${col_mapping[heat]} < id: ${id_qty}`);
  
  serving_qty = (parseFloat(nut_qty) * multiplier).toFixed(1);  // returns a string
                                                                // 
  document.getElementById(id_qty).textContent = serving_qty;
  
  console.log(`HEAT: ${heat} < - COLOUR: ${col_mapping[heat]} < id: ${id_hml}`);
  document.getElementById(id_hml).textContent = heat;
  
  document.getElementById(id_ri).textContent = `${Math.round(serving_qty/parseFloat(rda) * 100)}%`;
  
  column_elements = document.getElementsByClassName(column);
  
  console.log(column_elements)
  
  for (var element = 0; element < column_elements.length; element++ ){
    console.log(element);
    console.log(column_elements[element]);
    column_elements[element].style.backgroundColor = col_mapping[heat];
  }
  
}

// 0=left col  1=right col
function fill_and_format_column(nutrinfo, side){
  // lower & upper thresholds are per 100g
  // displayed numbers are numbers per serving!
  // there should be a liquids version of this too!
  // carbs ref = 260g
  // protein ref = 50g
  var nut_cols = {
    n_En:{column_class: "t_lgt_en", lower:0, upper:5000, rda:2000, id_qty:'t_energy_qty', id_hml:'t_energy_hml', id_ri:'t_energy_ri'},
    n_Fa:{column_class: "t_lgt_fa", lower:3.0, upper:17.5, rda:70, id_qty:'t_fat_qty', id_hml:'t_fat_hml', id_ri:'t_fat_ri'},
    n_Fs:{column_class: "t_lgt_fs", lower:1.5, upper:5.0, rda:20,  id_qty:'t_saturates_qty', id_hml:'t_saturates_hml', id_ri:'t_saturates_ri'},
    n_Su:{column_class: "t_lgt_su", lower:5.0, upper:22.5, rda:90, id_qty:'t_sugars_qty', id_hml:'t_sugars_hml', id_ri:'t_sugars_ri'},
    n_Sa:{column_class: "t_lgt_sa", lower:0.3, upper:1.5, rda:6,   id_qty:'t_salt_qty', id_hml:'t_salt_hml', id_ri:'t_salt_ri'}
  };
  
  document.getElementById(`traffic_title_${side}`).textContent = `Serving: ${ Math.round(nutrinfo.serving_size) }g`;
  
  const multiplier = parseFloat(nutrinfo.serving_size)/100.0;  // EG x1.6 got a serving size of 160g

  // fill in left table
  for (var col in nut_cols) {
    // nut_qty, column, lower_threshold, upper_threshold, rda, id_hml, id_ri
    console.log(col);              
    console.log(`${col} nut_qty:${nutrinfo[col]} column_class:${nut_cols[col].column_class} lower:${nut_cols[col].lower} upper:${nut_cols[col].upper} rda:${nut_cols[col].rda} id_qty:${nut_cols[col].id_qty} id_hml:${nut_cols[col].id_hml} id_ri:${nut_cols[col].id_ri} `);
    format_nutrition_table_column_colours(nutrinfo[col],
                                          `${nut_cols[col].column_class}_${side}`,
                                          nut_cols[col].lower,
                                          nut_cols[col].upper,
                                          nut_cols[col].rda,
                                          `${nut_cols[col].id_qty}_${side}`,
                                          `${nut_cols[col].id_hml}_${side}`,
                                          `${nut_cols[col].id_ri}_${side}`,
                                          multiplier );
  }
  
}




// pass a nutrints object in to function and let the helpers to the rest!
function fill_in_nutrients_table() {
  
  display_template_params();
  
  // struct / JSON
  //nutrients = {
  //  ri_id: 6,
  //  n_En: 154.0,
  //  n_Fa: 3.12,
  //  n_Fs: 1.33,
  //  n_Su: 2.93,
  //  n_Sa: 0.58,
  //  serving_size: 190.0
  //};
  
  // was 
  // recipes[0]['nutrinfo']['ri_name'] = recipes[0]['ri_name'];
  if (recipes) {
   
    side = 0; // LEFT
    
    recipes.forEach( function(recipe){        
        console.log(`recipes.forEach side:${side} <`);
        
        fill_and_format_column(recipe.nutrinfo, side);

        side += 1;
      }
 
    );
    
  }
  else {
    console.log("recipes not valid");
  }
  
  
  //recipes[0].nutrinfo.ri_name = recipes[0].ri_name;  
  //recipes[1].nutrinfo.ri_name = recipes[1].ri_name;
  //
  //// fill left hand side (or solo table)
  //fill_and_format_column(recipes[0]['nutrinfo'], 0);
  //
  //// fill right hand side
  //fill_and_format_column(recipes[1]['nutrinfo'], 1);
  
  console.log('PAGE_LOADED:' + create_timestamp());    
  
  display_template_params();
}

function create_timestamp(){
  var today = new Date();
  var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
  var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
  var date_time = date+' '+time;
  
  return date_time;
}

function display_template_params(){

  console.log("COMPARE: display_template_params S: ");  

  if (recipes) {
   
    recipes.forEach( function(recipe){        

        var str = JSON.stringify(recipe, null, 2);      

        console.log(str);

      }
 
    );
    
  }
  else {
    console.log("recipes not valid");
  }

  console.log("display_template_params E: ");
    
}

// attach an event listener to nutrient table
// comparison table
try {
  document.querySelector('#nutri_taffic_table_main_compare').addEventListener('load', fill_in_nutrients_table);
}
catch(error) {
  // console.error(error);
}


// solo table
try {
  document.querySelector('#nutri_taffic_table_main').addEventListener('load', fill_in_nutrients_table);
}
catch(error) {
  // console.error(error);
}


// attach an event listener to the left button
document.querySelector('#b_update_0').addEventListener('mousedown', display_template_params);


// attach an event listener to the button
document.querySelector('#b_update_0').addEventListener('click', fill_in_nutrients_table);

// create a button element (not yet inserted into DOM)
var clear_button = document.createElement('button');

// give button and id - so we can attach function easily
clear_button.id = 'b_clear';

// create a text node and add it to the button
clear_button.appendChild(document.createTextNode('CLEAR TABLE'));

//<div class="btn-group">
//  <button id='b_update'>UPDATE</button>
//</div>
// select tag div class .btn-group     add node to DOM
// document.querySelector('div.btn-group').appendChild(clear_button);
document.querySelector('#nutri_table_btns').appendChild(clear_button);


// to put NEW button first
//document.getElementById('b_update').insertBefore(clear_button);               // NO
// syntax
// var insertedNode = parentNode.insertBefore(newNode, referenceNode);
//document.querySelector('div.btn-group').insertBefore(clear_button, b_update); // YES!!

clear_button.addEventListener('click', clear_table_contents);

clear_button.addEventListener('mousedown', clear_table_colours);

function clear_table_contents(){
  
  console.log('FIRE: clear_table_contens')
  
  nut_table = document.querySelector('.nutri_taffic_table');

  // reset text to QTY - <tr class='row_qty'>
  // reset text to XX - <tr class='row_hml'>  
  // reset text to YY% - <tr class='row_ri'> 
  var row_reset_values = {
    'row_qty':'QTY',
    'row_hml':'XX',
    'row_ri':'YY%'
  };

  for (var row in row_reset_values){
    console.log(`.$(row) td`);
    
    cells = document.getElementsByClassName(`.${row}`);   // give row only!
    cells = document.querySelectorAll(`.${row} td`);      // use ALL . dot class space tag_name(s)
    
    console.log(cells);
  
    for (c=0; c < cells.length; c++) {

      cells[c].textContent = row_reset_values[row];

    }
    
  }
  
  document.getElementById('traffic_title').textContent = 'title text to fill in . . ';
 
}

// reset to ALL cells to white background
function clear_table_colours(){
  
  const WHITE = "#FFFFFF";
  
  all_table_cells = document.querySelectorAll('.nutri_taffic_table *')

  for ( cell=0; cell < all_table_cells.length; cell++){
    all_table_cells[cell].style.backgroundColor = WHITE;
  }
  
}


// ways to load table

///////// 1
// see if we have valid data and fire from here!
//if (info_t0['ri_id'] != undefined) {
//  fill_in_nutrients_table();
//}

///////// 2
// add an onload attribute to the body and call it from there - in html file:
// <body onload="fill_in_nutrients_table()">

///////// 3
document.addEventListener('DOMContentLoaded', fill_in_nutrients_table());



























          