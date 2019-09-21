var nutri_table = document.getElementById('nutri_taffic_table_main');
// remove servings & buttons from nutritable - makes no sense for tracker
document.getElementById('traffic_title_0').remove();
document.getElementById('b_update_0').remove();
document.getElementById('b_clear').remove();


const ATOMIC_INDEX = 0;        // default value is 1 - TRUE
const QTY_IN_G_INDEX = 1;
const SERVING_INDEX = 2;
const INGREDIENT_INDEX = 3;
const TRACK_NIX_TIME = 4;
const NO_TIME = -1;
const ATOMIC = 1;
const RCP_IN_DB = 0;

// code review - mixed style! BAD
// find out generally accepted coding style fro JS and redo JS files TODO


var addItemButton = document.getElementById('add-item-button');


var itemList = document.getElementById('items'); // depracated TODO - REMOVE
var trackerTable = document.getElementById('table-tracked-items');
var tableWithFocus = trackerTable;

var filter = document.getElementById('filter');
var undo = document.getElementById('undo-button');

// Form submit event
addItemButton.addEventListener('click', addItem);
  //addItemToList(e);
  //addItemToTable(e);

// Delete event
itemList.addEventListener('click', removeItem);
// Undelete
undo.addEventListener('click', undeleteListItem);


// Filter event
// filter.addEventListener('keyup', filterItems);
// addthis back when adding auto complete ingredients 


//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// ingredient line helpers
function isIngredientAtomic(i){
  // TODO check DB 
  return String(ATOMIC);
}

function loadServingModifierLUT(){
  // load from DB
  var lut = {
    'onion': { 'small': 100.0, 'medium': 150.0, 'large': 200.0 },
    'red onion' : { 'small': 50.0, 'medium': 100.0, 'large': 150.0 },
    'banana' : { 'small': 90.0, 'medium': 120.0, 'large': 150.0 },
    'red peppers': { 'small': 120.0, 'medium': 150.0, 'large': 180.0 },
  };
  
  return lut;
}

function getServingWeight(qty, ingredient, modifier='medium'){
  // get serving data for ingredient from LUT - TODO implement
  
  var servingModifierLUT = loadServingModifierLUT();
  var qty = parseInt(qty);
  var size = 0;
  
  // quit dirty bounds check
  if (modifier === 'xs') { modifier='small'; };
  if ( (modifier === 'xl') || (modifier === 'mahoosive') ) { modifier='large'; };
  
  
  try{
    size = servingModifierLUT[ingredient][modifier];  
  }
  catch(err){
    conssole.log(`**** WARNING: getServingWeight - DB lookup MISS: ${modifier} ${ingredient}`);
    return 99999;     // it's BIG to notice somethings wrong!
  }
  
  return qty * size;  
}


function splitLineIntoQtyAndIngredient(newItem){
  // test cases
  // qtyunit ingredient               6g wasabi
  // qty unit ingredient              7 tsp sugar
  // qty adjective ingredient         8 mediun onions
  // qty ingredient ingredient        16 pork cheeks
  // qty ingredient                   a banana
  // qty ingredient ingredient        4 large red peppers
  // qty unit ingredient              20g rosemary
  // qty unit ingredient ingredient   10 cups chicken stock
  // qtyunit ingredient ingredient    5cups gram flour
  // qty unit ingredient ingredient   a medium chicken
  
  // units: g kg kgs oz lb lbs tsp tbsp cup cups l each - I'm sure theres more but that will do for now!
  // match number with or without units at start of line
  // matches in order - put plurals 1st!
  // ^(\d+(?:gs|g|kgs|kg|oz|lbs|lb|tsp|tbsp|cups|cup|l)*)
  // /regex/i - insensitive - no need .toLowerCase()
  var qty='99999', units=null, modifier=null, ingredient=newItem, servings='(0)';
  
  newItem = newItem.trim().replace(/^a/i, '1 ' );
  
  breakDown = newItem.split(' ');
  
  console.log(`- - - - regex QTY - S\n ${breakDown}`);

  info = breakDown[0].match(/^([0-9\/\.]+)\b/img);       // Number on it's own 1, 1.2 1/2 1/4
  if (info !== null) {
    qty = parseInt(info[1]);
    breakDown.shift();
    console.log(`qty ${qty} - info:${info} len:${typeof(info)} type:${info.len}`);
    
    // see if next item is units
    info = breakDown[0].match(/\b(gs|g|kgs|kg|oz|lbs|lb|tsp|tbsp|cups|cup|l)\b/img);
    if (info !== null) {
      units = info[1];
      breakDown.shift();
      console.log(`units ${units}`);
    }
    
    // or a modifier (adjective)
    info = breakDown[0].match(/\b(xs|small|medium|large|xl|mahoosive)\b/img);
    if (info !== null) {
      modifier = info[1];
      breakDown.shift();
      console.log(`modifier ${modifier}`);
    }
    
    ingredient = breakDown.join(' ');
    console.log(`ingredient ${ingredient}`);
  }
  
  
  // may have started with 5g or 5 cups  
  console.log('- - - - regex QTY+UNIT');
  info = breakDown[0].match(/^([0-9\/\.]+)(gs|g|kgs|kg|oz|lbs|lb|tsp|tbsp|cups|cup|l)/i);
  if (info !== null) { // 1 = qty  2 = units

    qty = parseInt(info[1]);    
    console.log(`qty ${qty}`);
    
    units = info[2];  
    console.log(`units ${units}`);

    breakDown.shift();

    ingredient = breakDown.join(' ');
    console.log(`ingredient ${ingredient}`);
  }
  
  
  // have no units - look item up and calculate/guess weight
  if (units === null) { // generate weight in g from LUT
    servings = `(${qty})`
    console.log(`qty:${qty} - ingredient:${ingredient} - modifier:${modifier}`)
    qty = getServingWeight(qty, ingredient, modifier)
    units = 'g'
  }

  // have no units - look item up and calculate/guess weight
  if (units !== 'g') { // generate weight in g from volume LUT
    // TODO - implement
    //console.log(`qty:${qty} - ingredient:${ingredient} - modifier:${modifier}`)
    //qty = getServingWeight(qty, ingredient, modifier)
    //units = 'g'
  }
  
  qtyUnits = `${qty}${units}`
  
  console.log([isIngredientAtomic(newItem), qtyUnits, servings, ingredient]);
  console.log('- - - - regex QTY - E');
  
  return [isIngredientAtomic(newItem), qtyUnits, servings, ingredient];
  //return [qty, units, modifier, ingredient];
}


//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// table building and helpers
function pad(n) {
  n = parseInt(n);             // parseInt(n, 10) base 10
  return n<10 ? '0'+n : n;
}

function time4d_24h(timestamp){
  ts = new Date(timestamp);
  return `${pad(ts.getHours())}${pad(ts.getMinutes())}`;
}

function timeNixTimeInms(){
  return (new Date()).getTime();
}

//JS Regex
//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
//Flags
//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions#Advanced_searching_with_flags_2
// my hot dog recipe => my-hot-dog-recipe
String.prototype.ingtToClass = function(ingredient){
  // remove punctuation
  ingredient = ingredient.split(/[^a-zA-Z0-9\s]/).join('')

  // replace sapce w/ hyphen
  return ingredient.split(/\s+/).join('-')

}



//<tr>  <!--ingredient row items-->        
//  <td class="col-but-all text-center"><button class="btn btn-danger btn-sm delete">X</button></td><!--<button class="btn btn-danger btn-sm float-left delete">X</button>-->          
//  <td class="col-but-time">2400</td>
//  <td class="col-but-qty text-center">180g</td>			<!-- qty -->
//      <!-- servings -->
//      <td class="col-but-serv text-center"></td>                              
//  <td class="col-but-ingdt">coffee</td>			<!-- ingredient -->
//  <td class="col-but-all"><button class="btn btn-secondary btn-sm snapshot float-right"><svg class="svg-inline--fa fa-camera fa-w-16" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="camera" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" data-fa-i2svg=""><path fill="currentColor" d="M512 144v288c0 26.5-21.5 48-48 48H48c-26.5 0-48-21.5-48-48V144c0-26.5 21.5-48 48-48h88l12.3-32.9c7-18.7 24.9-31.1 44.9-31.1h125.5c20 0 37.9 12.4 44.9 31.1L376 96h88c26.5 0 48 21.5 48 48zM376 288c0-66.2-53.8-120-120-120s-120 53.8-120 120 53.8 120 120 120 120-53.8 120-120zm-32 0c0 48.5-39.5 88-88 88s-88-39.5-88-88 39.5-88 88-88 88 39.5 88 88z"></path></svg><!-- <i class="fas fa-camera"></i> --></button></td>
//      <!-- not an atomic engredient - expandable button -->										  
//    <td class="col-but-all"><a class="btn btn-sm btn-outline-success float-right" href="#" role="button">e</a></td>
//    
//  <!--extra small button - relies on additional styling recipe.css-->
//  <!--<td>coffee<a class="btn btn-xs btn-outline-secondary float-right" href="#" role="button">expand</a></td>-->							  
//</tr>  
//
//atomic, qty,  sevings, item, timestamp
// ['1', '180g', '(0)', 'steak', 1568927767066]
function createTablelineHTML(ingredient_line_array){
  var but_delete = '<td class="col-but-all text-center"><button class="btn btn-danger btn-sm delete">X</button></td>'; 
    
  var time=''
  if (ingredient_line_array[TRACK_NIX_TIME] < 0) {
    time = '<td class="col-but-time"></td>'
  } else {
    time = `<td class="col-but-time">${time4d_24h(ingredient_line_array[TRACK_NIX_TIME])}</td>`
  }
  
  var qty = `<td class="col-but-qty text-center">${ingredient_line_array[QTY_IN_G_INDEX]}</td>`
      
  var servings = '';
  if (ingredient_line_array[SERVING_INDEX] === '(0)'){
    servings = '<td class="col-but-serv text-center"></td>';
  } else {
    servings = `<td class="col-but-serv text-center">${ingredient_line_array[SERVING_INDEX]}</td>`;
  }
  
  var item = `<td class="col-but-ingdt">${ingredient_line_array[INGREDIENT_INDEX]}</td>`
  
  var but_photo = '<td class="col-but-all"><button class="btn btn-secondary btn-sm snapshot float-right"><i class="fas fa-camera"></i></button></td>';

  var but_explode = '<td class="col-but-all"><a class="btn btn-sm btn-outline-success float-right" href="#" role="button">e</a></td>';
  var but_recipe = '<td class="col-but-all"><a class="btn btn-sm btn-outline-secondary float-right" href="#" role="button">R</a></td>';
  var but_more = '';  
  if (ingredient_line_array[ATOMIC_INDEX] === '1') { // atomic - allow add recipe
    
    but_more = but_recipe;
    
  } else { // not atomic - show expandable button
  
    but_more = but_explode;
    
  }
    
  return `<tr>${but_delete} ${time} ${qty} ${servings} ${item} ${but_photo} ${but_more}</tr>`
}


function addRowToTable(table, ingredient_array){
  
  // get table body
  var tbody = table.getElementsByTagName("tbody")[0];
  
  console.log('- - - -');
  console.log(tbody);
  console.log(ingredient_array);
  console.log('- - - -');

  var row = document.createElement('tr');
  
  createdHTML = createTablelineHTML(ingredient_array)
  
  console.log(`\n- - - - createdHTML\n${createdHTML}`);
  
  row.innerHTML = createdHTML;
    
  // add the row to the end of the table body
  tbody.appendChild(row);
  
}

// https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Traversing_an_HTML_table_with_JavaScript_and_DOM_Interfaces
function buildTableFromDailyTracker(){
  // load loacally stored dailyTracker
  
  // compare to version from server
  
  // render selected version
  
  // get handle to table
  table = document.getElementById('table-tracked-items');
  
  console.log('> >  building table < < - - - - S');
  console.log(dtk);
  console.log(dtk['dtk_rcp']['ingredients']);
  
  for (i_arr in dtk['dtk_rcp']['ingredients']){
    console.log(i_arr);    
    addRowToTable(table, dtk['dtk_rcp']['ingredients'][i_arr]);
  }
  
  console.log('> >  building table < < - - - - E');
}

// a component is a sub recipe, a recipe for an item in an ingredients list
function buildTableFromComponent(name, component){
  // needs work for recipe page too - TODO CHECK & ingtegrate
  
  // create table
  table = document.createElement('table');
  table.className = 'tbl-ingredients'
  table.setAttribute('id', name.ingtToClass)
  
  console.log(`> >  building table [${table.getAttribute('id')}] < < - - - - S`);
  //console.log(dtk);
  //console.log(dtk['dtk_rcp']['ingredients']);
  //
  //for (i_arr in dtk['dtk_rcp']['ingredients']){
  //  console.log(i_arr);    
  //  addRowToTable(table, dtk['dtk_rcp']['ingredients'][i_arr]);
  //}
  
  console.log('> >  building table < < - - - - E');
}

//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// buttons

function addItem(e){
  e.preventDefault();
  addItemToList(e);
  addItemToTable(e);
}

//- - - - - - - - - - - - - - - - - - - - - - - - - - - -
// Add item to table
function addItemToTable(e){
  e.preventDefault();

  console.log('e.target.id - table');
  console.log(e.target.id);
  console.log('>>');
  
  // Get input value
  var newItem = document.getElementById('addForm').value;
  console.log(`>newItem ${newItem} - ${newItem.trim().length} [${newItem.trim()}]`);
  
  // break it into constituents  
  ingredientLineArray = splitLineIntoQtyAndIngredient(newItem);  // return [qty, units, modifier, ingredient];
  
  // timestamp it if it's a tracker item
  var time = NO_TIME;
  if (tableWithFocus === trackerTable) {
    time = timeNixTimeInms();
    console.log(`* * * timeNixTimeInms(): ${time}  24H-${time4d_24h(time)}`)
  }
  
  ingredientLineArray.push(time);
  
  //atomic, qty,  sevings, item, timestamp
  // ['1', '180g', '(0)', 'steak', 1568927767066]
  
  dtk['dtk_rcp']['ingredients'].push(ingredientLineArray);
  
  // COMPONENT

  // all print exaclty the same thing
  console.log( `dtk['dtk_rcp'] ingredientLineArray - ${ingredientLineArray}` );      // => [[ingredient_arr]]
  //console.log( `dtk['dtk_rcp']['ingredients'][lastIngredient] - ${dtk['dtk_rcp']['ingredients'][lastIngredient]}` );// => [ingredient_arr]
  
  //addRowToTable( tableWithFocus, dtk['dtk_rcp']['ingredients'][lastIngredient]);
  addRowToTable( tableWithFocus, ingredientLineArray);

}

//- - - - - - - - - - - - - - - - - - - - - - - - - - - -
// Add item to list
function addItemToList(e){
  //<li class="list-group-item">
  //  <button class="btn btn-danger btn-sm float-left delete">X</button>
  //  <div class="list-group-item-sub-text">${added_item_text}</div>
  //  <button class="btn btn-default btn-sm float-right add-recipe">Rcp</button>
  //  <button class="btn btn-secondary btn-sm float-right snapshot"><i class="fas fa-camera"></i></button>
  //</li>
  //`<li class="list-group-item"><button class="btn btn-danger btn-sm float-left delete">X</button><div class="list-group-item-sub-text">---- 30g smoked ham</div><button class="btn btn-default btn-sm float-right add-recipe">Rcp</button><button class="btn btn-secondary btn-sm float-right snapshot"><i class="fas fa-camera"></i></button></li>`
  e.preventDefault();

  console.log('e.target.id - list');
  console.log(e.target.id);
  console.log('>>');
  
  // Get input value
  var newItem = document.getElementById('addForm').value;
  console.log(`>newItem ${newItem} - ${newItem.trim().length} [${newItem.trim()}]`);
  
  // Create new li element
  var li = document.createElement('li');
  var row = document.createElement('tr');
  
  //// Add class
  li.className = 'list-group-item';

  var now = new Date;
  var eaten_at = '2409';// time4d_24h(now);
  
  li.innerHTML = `<button class="btn btn-danger btn-sm float-left delete">X</button><div class="list-group-item-sub-text">${eaten_at} ${newItem}</div><button class="btn btn-default btn-sm float-right add-recipe">Rcp</button><button class="btn btn-secondary btn-sm float-right snapshot"><i class="fas fa-camera"></i></button>`
  
  console.log(eaten_at);
  console.log(newItem);
  console.log((new Date).getHours());         // 8
  console.log(pad((new Date).getHours()));    // 08
  console.log((new Date).getMinutes());       // 59
  console.log((new Date));                    // Fri Sep 20 2019 08:59:42 GMT+0100 (British Summer Time)
  console.log(new Date(1568927767066));       // from timestamp - Thu Sep 19 2019 22:16:07 GMT+0100 (British Summer Time)
  
  //// Add text node with input value
  //li.appendChild(document.createTextNode(newItem));
  //
  //// Create del button element
  //var deleteBtn = document.createElement('button');
  //
  //// Add classes to del button
  //deleteBtn.className = 'btn btn-danger btn-sm float-right delete';
  //
  //// Append text node
  //deleteBtn.appendChild(document.createTextNode('X'));
  //
  //// Append button to li
  //li.appendChild(deleteBtn);
  //
  //// Create new li element  
  //var li = document.createElement('li');  // list element
  //var row = document.createElement('tr'); // table row element etc

  // Append li to list
  itemList.appendChild(li);
    
}


function factoryLineItem(){
  var line_item = {
    qty: 0,
    uints: 'g',
    each: 0,
    item: '',
    time: new Date,
    img_id: 0
  }
  
  line_item
}

// var undoList = { 0: factory_line_item() }
// parse entry into factoryline
var undoList = [];

// Remove item
function removeItem(e){
  if(e.target.classList.contains('delete')){
    var li = e.target.parentElement;        // parent of button = <li>text & buttons</li>
    var preceeding = li.previousElementSibling;
    undoList.push([preceeding, li])
    itemList.removeChild(li);
    console.log(undoList);
  }
}

// this needs to understan original oder in list but for now just tack it back on the end!
function undeleteListItem(e){
  if (undoList.length === 0) { return; }
  
  console.log(undoList);
  
  //itemList.appendChild(undoList.pop()[1]);
  var undoPair = undoList.pop();
  
  undoPair[0].after(undoPair[1]);
  
  console.log(undoList);
}

// Filter Items
function filterItems(e){
  // convert text to lowercase
  var text = e.target.value.toLowerCase();
  
  // Get lis
  var items = itemList.getElementsByTagName('li');
  
  // Convert to an array
  Array.from(items).forEach(function(item){
    var itemName = item.firstChild.textContent;
    if(itemName.toLowerCase().indexOf(text) != -1){
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
    }
  });
}

//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// build tracker table
buildTableFromDailyTracker()

