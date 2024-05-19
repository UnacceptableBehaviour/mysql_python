var nutri_table = document.getElementById('nutri_taffic_table_main');
// remove servings & buttons from nutritable - makes no sense for tracker
// document.getElementById('traffic_title_0').remove();
// document.getElementById('b_update_0').remove();
// document.getElementById('b_clear').remove();


const ATOMIC_INDEX = 0;        // default value is 1 - TRUE
const QTY_IN_G_INDEX = 1;
const SERVING_INDEX = 2;
const INGREDIENT_INDEX = 3;
const TRACK_NIX_TIME = 4;
const IMG_ID = 5;
const HTML_ID = 6;
const NO_TIME = -1;
const ATOMIC = 1;
const RCP_IN_DB = 0;
const ONE_DAY_IN_MS = 24 * 60 * 60 * 1000;

// code review - mixed style! BAD
// find out generally accepted coding style fro JS and redo JS files TODO


var addItemButton = document.getElementById('add-item-button');
var inputForm = document.getElementById('addForm');
// Form submit event
addItemButton.addEventListener('click', addItem);
inputForm.addEventListener('keyup', function(event) {   // act on hit return key
  if (event.key === "Enter") { addItem(event) }
});

var trackerTable = document.getElementById('table-tracked-items');
var tableWithFocus = trackerTable;
var allTrackerTables = document.getElementById('all-tables-div');

var filter = document.getElementById('filter');
var undoButton = document.getElementById('undo-button');

// DEBUG/DEV BUTTONS
var saveDTKbutton = document.getElementById('but-save-dtk');
saveDTKbutton.addEventListener('click', saveDailyTrackerToLocalStorage);
//-
var loadDTKbutton = document.getElementById('but-load-dtk');
loadDTKbutton.addEventListener('click', loadDailyTrackerFromLocalStorage);
//-
var clearLocalStorageButton = document.getElementById('but-c');
clearLocalStorageButton.addEventListener('click', clearLocalStorage);
//-
var postDTKdataToServer = document.getElementById('but-p');
postDTKdataToServer.addEventListener('click', fetchUpdateDailyTrackerNutrients);
//-
var listPostAndSaveButton = document.getElementById('but-post-store');
listPostAndSaveButton.addEventListener('click', saveDTKLocallyThenPostToServer);
//-
var listLocalStorageButton = document.getElementById('but-l');
listLocalStorageButton.addEventListener('click', listLocalStorageKeys);
//-
var debugOutputDiv = document.getElementById('store-display');



// row buttons: delete, add image, build recipe
allTrackerTables.addEventListener('click', clickHandler);
// Undelete
undoButton.addEventListener('click', undeleteItemFromComponent);


// Filter event
// filter.addEventListener('keyup', filterItems);
// addthis back when adding auto complete ingredients 

//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// ingredient line helpers
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
function isIngredientAtomic(i){
  // TODO check DB 
  return String(ATOMIC);
}

function singular(ingredient){
  let singular_ingredient = '';
  
  ingredient = ingredient.toLowerCase();

  // end in s but are singular, or have no plural
  const exceptions = new Set(['beef silverside w&s','lemon grass', 'vegetable samosa indian takeaway mrs']);
  
  // if it doesn't end in s and has no plural should come out fine!
  // , 'fish', 'mutton', 'hogget'}
  
  if (exceptions.has(ingredient)) {
    return ingredient;
  }

  // exceptions with singular version
  const singular_from_plural = {
    'radishes'          : 'radish',
  };
  
  if (singular_from_plural.hasOwnProperty(ingredient) ) {
    return(singular_from_plural[ingredient]);
  }
  
  // ending with
  // cloves > clove - superseed ves > f
  if ( ingredient.match(/cloves$/) ) return( ingredient.replace(/cloves$/,'clove') );

  // cookies > cookie - superseed ies > y - all sorts of cookie flavours
  if ( ingredient.match(/cookies$/) ) return( ingredient.replace(/cookies$/,'cookie') );
  
  // cherries to cherry 
  if ( ingredient.match(/ies$/) ) return( ingredient.replace(/ies$/,'y') );
  
  // various olive - superseed ves > f
  if ( ingredient.match(/olives$/) ) return( ingredient.replace(/olives$/,'olive') );
  
  // leaves > leaf
  if ( ingredient.match(/ves$/) ) return( ingredient.replace(/ves$/,'f') );
  
  // tomatoes > tomato
  if ( ingredient.match(/oes$/) ) return( ingredient.replace(/oes$/,'o') );
  
  // octopii > opctpus
  if ( ingredient.match(/ii$/) ) return( ingredient.replace(/ii$/,'us') );
  
  return(ingredient.replace(/s\b/i,''));  
  
}

function loadServingModifierLUT(){
  // TODO load from DB
  // currently created by scan_for_each_data.py

  var lut = {
'alpen breakfast': { 'small': 150.0, 'medium': 200.0, 'large': 250.0, 'density': 1.0 },
'anchovy': { 'small': 2.6, 'medium': 3.5, 'large': 4.4, 'density': 1.0 },
'apple': { 'small': 101.2, 'medium': 135.0, 'large': 168.8, 'density': 1.0 },
'aubergine': { 'small': 258.8, 'medium': 345.0, 'large': 431.2, 'density': 1.0 },
'avocado': { 'small': 127.5, 'medium': 170.0, 'large': 212.5, 'density': 1.0 },
'baby courgette': { 'small': 45.0, 'medium': 60.0, 'large': 75.0, 'density': 1.0 },
'baby pepper': { 'small': 18.8, 'medium': 25.0, 'large': 31.2, 'density': 1.0 },
'banana': { 'small': 86.2, 'medium': 115.0, 'large': 143.8, 'density': 1.0 },
'beef silverside w&s': { 'small': 19.5, 'medium': 26.0, 'large': 32.5, 'density': 1.0 },
'beetroot brioche bun': { 'small': 45.0, 'medium': 60.0, 'large': 75.0, 'density': 1.0 },
'belgian chocolate': { 'small': 9.0, 'medium': 12.0, 'large': 15.0, 'density': 1.0 },
'boquerone': { 'small': 3.1, 'medium': 4.1, 'large': 5.1, 'density': 1.0 },
'braeburn apple': { 'small': 131.2, 'medium': 175.0, 'large': 218.8, 'density': 1.0 },
'brazil nut': { 'small': 2.6, 'medium': 3.5, 'large': 4.4, 'density': 1.0 },
'butter sultana biscuit': { 'small': 14.2, 'medium': 19.0, 'large': 23.8, 'density': 1.0 },
'butternut squash': { 'small': 375.0, 'medium': 500.0, 'large': 625.0, 'density': 1.0 },
'cantuccini': { 'small': 6.8, 'medium': 9.0, 'large': 11.2, 'density': 1.0 },
'cardamom': { 'small': 0.1, 'medium': 0.2, 'large': 0.2, 'density': 1.0 },
'cauliflower': { 'small': 600.0, 'medium': 800.0, 'large': 1000.0, 'density': 1.0 },
'cherry': { 'small': 1.9, 'medium': 2.5, 'large': 3.1, 'density': 1.0 },
'cherry tart': { 'small': 83.3, 'medium': 111.0, 'large': 138.8, 'density': 1.0 },
'cherry tomato': { 'small': 8.2, 'medium': 11.0, 'large': 13.8, 'density': 1.0 },
'chicken bite': { 'small': 14.0, 'medium': 18.7, 'large': 23.4, 'density': 1.0 },
'chicken dark meat': { 'small': 67.5, 'medium': 90.0, 'large': 112.5, 'density': 1.0 },
'chicken quinoa salmon sushi': { 'small': 17.2, 'medium': 23.0, 'large': 28.8, 'density': 1.0 },
'chicken roll': { 'small': 5.1, 'medium': 6.8, 'large': 8.5, 'density': 1.0 },
'chinese leaf': { 'small': 26.5, 'medium': 35.3, 'large': 44.1, 'density': 1.0 },
'chorizo': { 'small': 3.0, 'medium': 4.0, 'large': 5.0, 'density': 1.0 },
'chorizo aubergine ball': { 'small': 22.5, 'medium': 30.0, 'large': 37.5, 'density': 1.0 },
'chrunchie choc': { 'small': 3.0, 'medium': 4.0, 'large': 5.0, 'density': 1.0 },
'cocktail beetroot': { 'small': 12.2, 'medium': 16.3, 'large': 20.4, 'density': 1.0 },
'conference pear': { 'small': 97.5, 'medium': 130.0, 'large': 162.5, 'density': 1.0 },
'confit garlic': { 'small': 1.7, 'medium': 2.2, 'large': 2.8, 'density': 1.0 },
'confit garlic clove': { 'small': 3.0, 'medium': 4.0, 'large': 5.0, 'density': 1.0 },
'coop prosciutto': { 'small': 10.0, 'medium': 13.3, 'large': 16.6, 'density': 1.0 },
'coppa': { 'small': 4.1, 'medium': 5.4, 'large': 6.8, 'density': 1.0 },
'corn on the cob': { 'small': 120.0, 'medium': 160.0, 'large': 200.0, 'density': 1.0 },
'cornfed chicken': { 'small': 1350.0, 'medium': 1800.0, 'large': 2250.0, 'density': 1.0 },
'courgette': { 'small': 315.0, 'medium': 420.0, 'large': 525.0, 'density': 1.0 },
'crab cake': { 'small': 63.8, 'medium': 85.0, 'large': 106.2, 'density': 1.0 },
'crab meat': { 'small': 100.0, 'medium': 133.3, 'large': 166.6, 'density': 1.0 },
'crunchie choc': { 'small': 3.0, 'medium': 4.0, 'large': 5.0, 'density': 1.0 },
'cumberland sausage': { 'small': 45.0, 'medium': 60.0, 'large': 75.0, 'density': 1.0 },
'date': { 'small': 7.4, 'medium': 9.9, 'large': 12.4, 'density': 1.0 },
'dried apricot': { 'small': 4.5, 'medium': 6.0, 'large': 7.5, 'density': 1.0 },
'egg': { 'small': 31.5, 'medium': 42.0, 'large': 52.5, 'density': 1.0 },
'egg yolk': { 'small': 17.2, 'medium': 23.0, 'large': 28.8, 'density': 1.0 },
'es dark chocolate 40%': { 'small': 3.8, 'medium': 5.0, 'large': 6.2, 'density': 1.0 },
'fish finger': { 'small': 21.0, 'medium': 28.0, 'large': 35.0, 'density': 1.0 },
'fish stick': { 'small': 10.0, 'medium': 13.3, 'large': 16.6, 'density': 1.0 },
'flat peach': { 'small': 64.5, 'medium': 86.0, 'large': 107.5, 'density': 1.0 },
'garlic': { 'small': 3.0, 'medium': 4.0, 'large': 5.0, 'density': 1.0 },
'garlic clove': { 'small': 3.0, 'medium': 4.0, 'large': 5.0, 'density': 1.0 },
'grape': { 'small': 4.9, 'medium': 6.5, 'large': 8.1, 'density': 1.0 },
'green olive': { 'small': 2.1, 'medium': 2.8, 'large': 3.5, 'density': 1.0 },
'guinea fowl raw': { 'small': 787.5, 'medium': 1050.0, 'large': 1312.5, 'density': 1.0 },
'head on prawn': { 'small': 18.0, 'medium': 24.0, 'large': 30.0, 'density': 1.0 },
'hs frazzle': { 'small': 0.5, 'medium': 0.7, 'large': 0.9, 'density': 1.0 },
'humous and tomato cracker': { 'small': 20.2, 'medium': 27.0, 'large': 33.8, 'density': 1.0 },
'king date': { 'small': 17.2, 'medium': 23.0, 'large': 28.8, 'density': 1.0 },
'king prawn': { 'small': 4.6, 'medium': 6.1, 'large': 7.6, 'density': 1.0 },
'kiwi fruit': { 'small': 60.0, 'medium': 80.0, 'large': 100.0, 'density': 1.0 },
'lamb and aubergine teriyaki skewer': { 'small': 51.0, 'medium': 68.0, 'large': 85.0, 'density': 1.0 },
'lamb chop wfat': { 'small': 67.5, 'medium': 90.0, 'large': 112.5, 'density': 1.0 },
'leaf gelatine': { 'small': 3.8, 'medium': 5.0, 'large': 6.2, 'density': 1.0 },
'leek': { 'small': 107.5, 'medium': 143.3, 'large': 179.1, 'density': 1.0 },
'lemon': { 'small': 64.5, 'medium': 86.0, 'large': 107.5, 'density': 1.0 },
'lemon basil leaf': { 'small': 0.1, 'medium': 0.2, 'large': 0.2, 'density': 1.0 },
'lemon grass': { 'small': 6.8, 'medium': 9.0, 'large': 11.2, 'density': 1.0 },
'lemon sole': { 'small': 81.0, 'medium': 108.0, 'large': 135.0, 'density': 1.0 },
'mackerel fillet': { 'small': 58.1, 'medium': 77.5, 'large': 96.9, 'density': 1.0 },
'medjool date': { 'small': 13.8, 'medium': 18.4, 'large': 23.0, 'density': 1.0 },
'mgt': { 'small': 37.5, 'medium': 50.0, 'large': 62.5, 'density': 1.0 },
'milano salami': { 'small': 3.0, 'medium': 4.0, 'large': 5.0, 'density': 1.0 },
'mixed sushi': { 'small': 9.2, 'medium': 12.3, 'large': 15.4, 'density': 1.0 },
'mmgb': { 'small': 22.5, 'medium': 30.0, 'large': 37.5, 'density': 1.0 },
'monkfish tail': { 'small': 127.5, 'medium': 170.0, 'large': 212.5, 'density': 1.0 },
'mrs veg samosa': { 'small': 30.0, 'medium': 40.0, 'large': 50.0, 'density': 1.0 },
'nectarine': { 'small': 82.5, 'medium': 110.0, 'large': 137.5, 'density': 1.0 },
'olive': { 'small': 2.2, 'medium': 3.0, 'large': 3.8, 'density': 1.0 },
'onion': { 'small': 112.5, 'medium': 150.0, 'large': 187.5, 'density': 1.0 },
'onion ring': { 'small': 1.0, 'medium': 1.4, 'large': 1.7, 'density': 1.0 },
'oxo cube': { 'small': 4.7, 'medium': 6.3, 'large': 7.9, 'density': 1.0 },
'parma': { 'small': 11.5, 'medium': 15.3, 'large': 19.1, 'density': 1.0 },
'peanut kitkat bite': { 'small': 3.8, 'medium': 5.0, 'large': 6.2, 'density': 1.0 },
'pear chews beta': { 'small': 3.8, 'medium': 5.0, 'large': 6.2, 'density': 1.0 },
'pickled beetroot': { 'small': 30.0, 'medium': 40.0, 'large': 50.0, 'density': 1.0 },
'pitta': { 'small': 20.0, 'medium': 26.7, 'large': 33.3, 'density': 1.0 },
'plum': { 'small': 52.5, 'medium': 70.0, 'large': 87.5, 'density': 1.0 },
'plum tomato': { 'small': 50.2, 'medium': 67.0, 'large': 83.8, 'density': 1.0 },
'pork chernoula mini kebab': { 'small': 105.0, 'medium': 140.0, 'large': 175.0, 'density': 1.0 },
'pork shoulder (seared & diced)': { 'small': 112.5, 'medium': 150.0, 'large': 187.5, 'density': 1.0 },
'pork shoulder chop': { 'small': 112.5, 'medium': 150.0, 'large': 187.5, 'density': 1.0 },
'portobello mushroom': { 'small': 78.8, 'medium': 105.0, 'large': 131.2, 'density': 1.0 },
'potato': { 'small': 75.0, 'medium': 100.0, 'large': 125.0, 'density': 1.0 },
'prawn': { 'small': 8.2, 'medium': 11.0, 'large': 13.8, 'density': 1.0 },
'prawn and mayo dragon roll': { 'small': 14.1, 'medium': 18.8, 'large': 23.5, 'density': 1.0 },
'prawns w lemon grass and chilli': { 'small': 16.5, 'medium': 22.0, 'large': 27.5, 'density': 1.0 },
'pringle': { 'small': 1.7, 'medium': 2.2, 'large': 2.8, 'density': 1.0 },
'prune': { 'small': 5.6, 'medium': 7.4, 'large': 9.3, 'density': 1.0 },
'prune yogurt': { 'small': 93.8, 'medium': 125.0, 'large': 156.2, 'density': 1.0 },
'radish': { 'small': 6.3, 'medium': 8.4, 'large': 10.5, 'density': 1.0 },
'raspberry and white choc chip cookie': { 'small': 54.0, 'medium': 72.0, 'large': 90.0, 'density': 1.0 },
'red onion': { 'small': 55.0, 'medium': 73.3, 'large': 91.6, 'density': 1.0 },
'rosemary cracker': { 'small': 4.5, 'medium': 6.0, 'large': 7.5, 'density': 1.0 },
'salmon coriander sushi lite v1': { 'small': 22.5, 'medium': 30.0, 'large': 37.5, 'density': 1.0 },
'salt and pepper aubergine croquette': { 'small': 48.0, 'medium': 64.0, 'large': 80.0, 'density': 1.0 },
'sbs bakewell tart': { 'small': 30.0, 'medium': 40.0, 'large': 50.0, 'density': 1.0 },
'sbs wholemeal tortilla wrap': { 'small': 48.0, 'medium': 64.0, 'large': 80.0, 'density': 1.0 },
'seafood croquette': { 'small': 56.2, 'medium': 75.0, 'large': 93.8, 'density': 1.0 },
'smoked mackerel fillet': { 'small': 44.8, 'medium': 59.7, 'large': 74.6, 'density': 1.0 },
'smoked rindless bacon': { 'small': 37.5, 'medium': 50.0, 'large': 62.5, 'density': 1.0 },
'spring onion': { 'small': 7.5, 'medium': 10.0, 'large': 12.5, 'density': 1.0 },
'squash socarat cake': { 'small': 10.5, 'medium': 14.0, 'large': 17.5, 'density': 1.0 },
'squid': { 'small': 54.0, 'medium': 72.0, 'large': 90.0, 'density': 1.0 },
'squid stuffed w chicken and spinach': { 'small': 86.2, 'medium': 115.0, 'large': 143.8, 'density': 1.0 },
'squid tube': { 'small': 80.0, 'medium': 106.7, 'large': 133.3, 'density': 1.0 },
'ssr chicken squid and red pepper': { 'small': 9.4, 'medium': 12.5, 'large': 15.6, 'density': 1.0 },
'ssr mushroom aubergine': { 'small': 9.4, 'medium': 12.5, 'large': 15.6, 'density': 1.0 },
'ssr prawn': { 'small': 9.4, 'medium': 12.5, 'large': 15.6, 'density': 1.0 },
'steamed chicken chunk meatball': { 'small': 28.5, 'medium': 38.0, 'large': 47.5, 'density': 1.0 },
'strawberry': { 'small': 8.1, 'medium': 10.8, 'large': 13.5, 'density': 1.0 },
'sugar snap': { 'small': 3.2, 'medium': 4.2, 'large': 5.2, 'density': 1.0 },
'sweet pickled gherkin': { 'small': 26.0, 'medium': 34.6, 'large': 43.3, 'density': 1.0 },
'tangerine': { 'small': 36.3, 'medium': 48.4, 'large': 60.5, 'density': 1.0 },
'thick smoked bacon': { 'small': 38.2, 'medium': 51.0, 'large': 63.8, 'density': 1.0 },
'tiger baguette round': { 'small': 11.2, 'medium': 15.0, 'large': 18.8, 'density': 1.0 },
'tiger prawn': { 'small': 5.2, 'medium': 6.9, 'large': 8.6, 'density': 1.0 },
'tomato': { 'small': 56.8, 'medium': 75.7, 'large': 94.6, 'density': 1.0 },
'tomato cracker': { 'small': 14.2, 'medium': 19.0, 'large': 23.8, 'density': 1.0 },
'tortilla chips ll': { 'small': 1.4, 'medium': 1.8, 'large': 2.3, 'density': 1.0 },
'tortilla wrap': { 'small': 43.5, 'medium': 58.0, 'large': 72.5, 'density': 1.0 },
'turmeric pancake': { 'small': 56.2, 'medium': 75.0, 'large': 93.8, 'density': 1.0 },
'vegetable samosa indian takeaway mrs': { 'small': 30.0, 'medium': 40.0, 'large': 50.0, 'density': 1.0 },
'walnut half': { 'small': 1.4, 'medium': 1.8, 'large': 2.3, 'density': 1.0 },
'white mushroom': { 'small': 17.2, 'medium': 23.0, 'large': 28.8, 'density': 1.0 },
'wrap': { 'small': 30.0, 'medium': 40.0, 'large': 50.0, 'density': 1.0 },
'yakult': { 'small': 48.8, 'medium': 65.0, 'large': 81.2, 'density': 1.0 }
  };
  
  return lut;
}


function loadUnitsToVolume() {
  unitsToVolume = { // 1 cm3 of water density = 1.0
    'gs': 1.0,
    'g': 1.0,
    'mls': 1.0,
    'ml': 1.0,
    'm': 1.0,
    'kgs': 1000.0,
    'kg': 1000.0,
    'oz': 28.35, 
    'lbs': 453.59,
    'lb': 453.59,
    'tsp': 5.0,
    'tbsp': 15.0,
    'cups': 236.6,  // us cups - bonkers
    'cup': 236.6,
    'ls': 1000.0,
    'l': 1000.0,    
  };
  
  return unitsToVolume;
}

// 1 cup of veg oil
// vol of unit * ingredient[density] 
function convertToGrams(qty, units, ingredient){
  
  // load ingredient density info from DB
  var servingModifierLUT = loadServingModifierLUT();

  // load volume of units info from DB
  var unitsToVolume = loadUnitsToVolume();
  
  singular_igdt = singular(ingredient);
  
  try {
    if ( servingModifierLUT[singular_igdt] === undefined) {
      return qty * unitsToVolume[units] * 1.0;      
    } else {
      return qty * unitsToVolume[units] * servingModifierLUT[singular_igdt]['density'];  
    }
    
  } catch(err) {
    console.log(`**** WARNING: convertToGrams - DB lookup MISS: qty:${qty} units:${units} ingredient:${ingredient}(${singular_igdt}) vol:${unitsToVolume[units]}`);
    return 99999;     // it's BIG to notice somethings wrong!
  }
  
}


// get serving data for ingredient from LUT
function getServingWeight(qty, ingredient, modifier='medium'){
  
  var servingModifierLUT = loadServingModifierLUT(); // TODO implement DB table
  var qty = parseInt(qty);
  var size = 0;
  var validModifers = ['xs', 'small', 'medium', 'large', 'xl', 'mahoosive'];
  if ( !validModifers.includes(modifier) ){
    modifier='medium';
  };
  
  // quick dirty bounds check
  if (modifier === 'xs')
    { modifier = 'small'; };
    
  if ( (modifier === 'xl') || (modifier === 'mahoosive') )
    { modifier = 'large'; };
  
  singular_igdt = singular(ingredient);
  
  try {    
    size = servingModifierLUT[singular_igdt][modifier];
    console.log(`*> servingModifierLUT: ${modifier} ${ingredient}(${singular_igdt}) = ${size} <`);
  
  } catch(err) { 
    console.log(`**** WARNING: getServingWeight - DB lookup MISS: ${modifier} ${ingredient}(${singular_igdt})`);
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
  // ^(\d+(?:gs|g|kgs|kg|oz|lbs|lb|tsp|tbsp|cups|cup|ls|l)*)      // generate using loadUnitsToVolume().keys - DRY
  // /regex/i - insensitive - no need .toLowerCase()
  var qty='99999', units=null, modifier='', ingredient=newItem, servings='(0)', new_timestamp = null;


  // Check if @1845 time over ride in ingredient EG 120g apple @1330
  console.log(`ingredient CHECK @time? ${newItem} <<`);
  info = newItem.match(/(@\s*?(\d\d)(\d\d)\b)/);
  console.log(info);
  console.log('^^ info ^^');
  if (info !== null) { // 1 = @1330  2 = hrs  3 = mins
    newItem = newItem.replace( info[1], '');
    const new_hr = info[2];
    const new_min = info[3];
    new_timestamp = timeNixTimeInmsFromHrsMins(new_hr, new_min);
    console.log(`ingredient @time? ${newItem} changing to time: ${new_hr}${new_min}`);
  } else {
    console.log(`ingredient @time? ${newItem} no change.`);
  }  
  
  // replace line starting a with one - a chicken - 1 (unlucky) chicken
  newItem = newItem.trim().replace(/^(an\b|a\b)/i, '1 ' );
  
  // split entry into separate items, and discard blanks
  breakDown = newItem.split(' ').filter(function (i) { return ((i != "") && (i != null)); }); // remove empty, null and undefined;
  
  // what we got
  console.log(`- - - - regex QTY - S\n ${breakDown}`);

  // case: non adjacent qty units - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  info = breakDown[0].match(/^([0-9\/\.]+)\b/i);       // Number on it's own 1, 1.2 1/2 1/4
  if (info !== null) {
    qty = parseInt(info[1]);  
    breakDown.shift();
    console.log(`breakDown[0] ${breakDown[0]} - qty ${qty} - info:${info} type:${typeof(info)} len:${info.length}`);
        
    // see if next item is units
    info = breakDown[0].match(/\b(gs|g|mls|ml|m|kgs|kg|oz|lbs|lb|tsp|tbsp|cups|cup|ls|l)\b/i);  // generate using loadUnitsToVolume().keys - DRY
    if (info !== null) {      
      units = info[1];
      console.log(`breakDown[0] ${breakDown[0]} - units ${units} - info:${info} type:${typeof(info)} len:${info.length}`);
      breakDown.shift();
    }
    
    // or a modifier (adjective)
    info = breakDown[0].match(/\b(xs|small|medium|large|xl|mahoosive)\b/i);
    if (info !== null) {
      modifier = info[1];
      console.log(`breakDown[0] ${breakDown[0]} - modifier ${modifier} - info:${info} type:${typeof(info)} len:${info.length}`);
      breakDown.shift();
    }
    
    ingredient = breakDown.join(' ');
    console.log(`ingredient ${ingredient}`);
  }
  
  // case: adjacent qty units - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  // may have started with 5g or 5 cups  
  console.log('- - - - regex QTY+UNIT');
  info = breakDown[0].match(/^([0-9\/\.]+)(gs|g|mls|ml|m|kgs|kg|oz|lbs|lb|tsp|tbsp|cups|cup|ls|l)/i); // generate using loadUnitsToVolume().keys - DRY
  if (info !== null) { // 1 = qty  2 = units

    qty = parseInt(info[1]);    
    console.log(`qty ${qty}`);
    
    units = info[2];  
    console.log(`units ${units}`);

    breakDown.shift();

    ingredient = breakDown.join(' ');
    console.log(`ingredient > ${ingredient} <`);
  }
  
  // case: no units no qty - apple, prune yogurt - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  if (qty==='99999') qty='1';
    
  
  // have no units - look item up and calculate/guess weight
  if (units === null) { // generate weight in g from LUT
    servings = `(${qty})`;
    console.log(`qty:${qty} - units:${units} - ingredient:${ingredient} - modifier:${modifier}`);
    qty = getServingWeight(qty, ingredient, modifier);
    units = 'g';
  }
    

  // units not in grams - convert unit
  if (units !== 'g') { // generate weight in g from volume LUT    
    qty = convertToGrams(qty, units, ingredient);
    units = 'g'
  }
  
  qtyUnits = `${qty}${units}`
  
  console.log([isIngredientAtomic(newItem), qtyUnits, servings, ingredient]);   // << BUG - surely this is ingredient
  console.log([isIngredientAtomic(ingredient), qtyUnits, servings, ingredient]);
  console.log('- - - - regex QTY - E');

  // use consts to define array
//const ATOMIC_INDEX = 0;        // default value is 1 - TRUE
//const QTY_IN_G_INDEX = 1;
//const SERVING_INDEX = 2;
//const INGREDIENT_INDEX = 3;
//const TRACK_NIX_TIME = 4;
//const NO_NUTRINFO = 5;      << NEED to send from server / local storage
  
  //return [isIngredientAtomic(ingredient), qtyUnits, servings, (`${modifier} ${ingredient}`).trim()];
  return [isIngredientAtomic(newItem), qtyUnits, servings, (`${modifier} ${ingredient}`).trim(), new_timestamp];
  //return [qty, units, modifier, ingredient];
}


//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// table building and helpers
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
function pad(n) {
  n = parseInt(n);             // parseInt(n, 10) base 10
  return n<10 ? '0'+n : n;
}

// TODO - make time functions aware - include GMT offset
function time4d_24h(timestamp){
  ts = new Date(timestamp);
  return `${pad(ts.getHours())}${pad(ts.getMinutes())}`;
}

function timeNixTimeInms(){
  return (new Date()).getTime();
}

// TODO - needs to be rollover aware if after midnight & before rollover +1 day
// port the python code - using nix time dodges day/month rollover
function timeNixTimeInmsFromHrsMins(hrs, mins){
  new_time = (new Date()).setHours(hrs, mins);
  console.log(`timeNixTimeInmsFromHrsMins: ${typeof(new_time)} - ${new_time}`)
  new_time = (new Date(new_time)).setSeconds(0);
  new_time = (new Date(new_time)).setMilliseconds(0);
  
  // check it lands on correct side of dtk rollover
  if (new_time > dtk['dtk_rcp']['dt_rollover']) {
    console.log(`timeNixTimeInmsFromHrsMins ${new_time}`);
    new_time -= ONE_DAY_IN_MS;
    console.log(`                changed to ${new_time}`);
  }
  
  return new_time;
}



//
// 1569665275998ms to '2019 calories month 09 thu 26'
function createDailyTrackerNameFromNixTime( nix_time_ms = timeNixTimeInms() ){
  date = new Date(nix_time_ms);
  dayNumToDay3L = ['sun','mon','tue','wed','thu','fri','sat'];  // day of week    0-6
  dateDD    = pad(date.getDate());                              // day of month   1-31
  yearYYYY  = date.getFullYear(); 
  monthMM   = pad(date.getMonth()+1);                           // month of year  0-11
  dayDDD    = dayNumToDay3L[date.getDay()];
  return `${yearYYYY} calories month ${monthMM} ${dayDDD} ${dateDD}`;
}


//JS Regex
//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
//Flags
//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions#Advanced_searching_with_flags_2
// my hot dog recipe => my-hot-dog-recipe
String.prototype.ingtToClass = function(){
  
  // remove punctuation
  var ingredientTagId = this.split(/[^a-zA-Z0-9\s]/).join('');
  
  ingredientTagId = ingredientTagId.split(/\s+/).join('-');
  
  console.log(`ingredient to tag ID: ${ingredientTagId}`);
  
  // replace sapce w/ hyphen
  return ingredientTagId;

}

function invalidateYield(){
  dtk['dtk_rcp']['dt_last_update'] = timeNixTimeInms();
  dtk['dtk_rcp']['nutrinfo']['yield'] = 0;
  dtkState = 'yieldInvalid';
}


// create line ID, add it to line
function idFromIngredient(ingredientLineArray){
  // timestamp-ingredient_name
  var id = `ts${ ingredientLineArray[TRACK_NIX_TIME] }-${ ingredientLineArray[INGREDIENT_INDEX].ingtToClass() }`
  
  // if already defined use the original tag id
  if (ingredientLineArray[HTML_ID] !== undefined) {
    console.log(`ORIGINAL HTML_ID: ${ingredientLineArray[HTML_ID]}`);
    return ingredientLineArray[HTML_ID];
  
  } else {
    console.log(`NEW HTML_ID: ${id}`);
    return id;  
  
  }
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
    
  var time='';
  if (ingredient_line_array[TRACK_NIX_TIME] < 0) {
    time = '<td class="col-but-time"></td>';
  } else {
    time = `<td class="col-but-time">${time4d_24h(ingredient_line_array[TRACK_NIX_TIME])}</td>`;
  }
  
  var qty = `<td class="col-but-qty text-center">${ingredient_line_array[QTY_IN_G_INDEX]}</td>`;
      
  var servings = '';
  if (ingredient_line_array[SERVING_INDEX] === '(0)'){
    servings = '<td class="col-but-serv text-center"></td>';
  } else {
    servings = `<td class="col-but-serv text-center">${ingredient_line_array[SERVING_INDEX]}</td>`;
  }
  
  var item = `<td class="col-but-ingdt">${ingredient_line_array[INGREDIENT_INDEX]}</td>`;
  
  // <img src="static/png/camera.png" alt="tick" srcset="static/svg/camera.svg">
  //var but_photo = '<td class="col-but-all"><button class="btn btn-secondary btn-sm snapshot float-right"><i class="fas fa-camera"></i></button></td>';
  var but_photo = '<td class="col-but-all"><button class="btn btn-secondary btn-sm snapshot float-right"><img src="static/png/camera.png" alt="tick" srcset="static/svg/camera.svg"></button></td>';

  var but_explode = '<td class="col-but-all"><a class="btn btn-sm btn-outline-success float-right" href="#" role="button">e</a></td>';
  var but_recipe = '<td class="col-but-all"><a class="btn btn-sm btn-outline-secondary float-right" href="#" role="button">R</a></td>';
  var but_more = '';  
  if (ingredient_line_array[ATOMIC_INDEX] === '1') { // atomic - allow add recipe
    
    but_more = but_recipe;
    
  } else { // not atomic - show expandable button
  
    but_more = but_explode;
    
  }
    
  return `<tr>${but_delete} ${time} ${qty} ${servings} ${item} ${but_photo} ${but_more}</tr>`;
}


function addRowToTable(table, ingredient_array){
  
  // get table body
  var tbody = table.getElementsByTagName("tbody")[0];
  
  console.log('- - - -');
  console.log(tbody);
  console.log(ingredient_array);
  console.log('- - - -');
  
  var row = document.createElement('tr');
  row.setAttribute('id', ingredient_array[HTML_ID]);
  
  createdHTML = createTablelineHTML(ingredient_array)
  
  console.log(`\n- - - - createdHTML\n${createdHTML}`);
  
  row.innerHTML = createdHTML;
    
  // add the row to the end of the table body
  tbody.appendChild(row);
  
}

// https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Traversing_an_HTML_table_with_JavaScript_and_DOM_Interfaces
function buildTableFromDailyTracker(){
  // load loacally stored dailyTracker  < already done
  
  // compare to version from server - if newer update <<<
  
  // render selected version  <<< where is this loaded?
  
  // get handle to table
  table = document.getElementById('table-tracked-items');
  
  // check if there's a tbody element - create if not
  if (table.getElementsByTagName("tbody")[0]) {
    console.log(`<tbody> present in [${table.getAttribute('id')}]`);
  } else {
    table.appendChild(document.createElement('tbody'));
    console.log(`<tbody> ADDED [${table.getAttribute('id')}]`);
  }
  
  
  
  console.log('> >  building table < < - - - - S');
  console.log(dtk);
  console.log(dtk['dtk_rcp']['ingredients']);
  
  
  // should already be present in save tracker data
  // timestamp it - TODO remove
  var bootstrapTimestamp = timeNixTimeInms();  
      
  for (i_arr in dtk['dtk_rcp']['ingredients']){
    console.log(i_arr);
    // add sequential unique timestamp to bootstrap - TODO remove
    bootstrapTimestamp += 1;
        
    // create html ID for it
    dtk['dtk_rcp']['ingredients'][i_arr][HTML_ID] = idFromIngredient(dtk['dtk_rcp']['ingredients'][i_arr]);
    
    // add it to table
    addRowToTable(table, dtk['dtk_rcp']['ingredients'][i_arr]);
  }
  
  console.log('> >  building table < < - - - - E');
}

// a component is a sub recipe, a recipe for an item in an ingredients list
function buildTableFromComponent(name, component){
  // needs to work for recipe page too - TODO CHECK & ingtegrate
  
  // create table
  table = document.createElement('table');
  table.className = 'tbl-ingredients'
  table.setAttribute('id', name.ingtToClass)
  // <tbody>
  
  // TODO - implement 
  
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
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// buttons

function addItem(e){
  e.preventDefault();
  addItemToTableFromForm(e);
}

//- - - - - - - - - - - - - - - - - - - - - - - - - - - -
// Add item to table
function addItemToTableFromForm(e){
  e.preventDefault();

  console.log('e.target.id - table');
  console.log(e.target.id);
  console.log('>>');
  
  // Get input value
  var newItem = inputForm.value;
  inputForm.value = null;

  console.log(`>newItem ${newItem} - ${newItem.trim().length} [${newItem.trim()}]`);

  // break it into constituents  
  ingredientLineArray = splitLineIntoQtyAndIngredient(newItem);  // return [qty, units, modifier, ingredient];

  // timestamp it 
  if (ingredientLineArray[TRACK_NIX_TIME] === null) {
    ingredientLineArray[TRACK_NIX_TIME] = timeNixTimeInms();    
  }

  // create html ID for it
  ingredientLineArray[HTML_ID] = idFromIngredient(ingredientLineArray);
  
  //atomic, qty,  sevings, item, timestamp, img_id, html_id
  // ['1', '180g', '(0)', 'steak', 1568927767066, tag_id]
  
  dtk['dtk_rcp']['ingredients'].push(ingredientLineArray);  
  
  // reset yield to zero so it's recalculated
  invalidateYield();

  // all print exaclty the same thing
  console.log( `dtk['dtk_rcp'] ingredientLineArray - ${ingredientLineArray}` );      // => [[ingredient_arr]]
  //console.log( `dtk['dtk_rcp']['ingredients'][lastIngredient] - ${dtk['dtk_rcp']['ingredients'][lastIngredient]}` );// => [ingredient_arr]
  
  //addRowToTable( tableWithFocus, dtk['dtk_rcp']['ingredients'][lastIngredient]);
  addRowToTable( tableWithFocus, ingredientLineArray);

  console.log(dtk['dtk_rcp']['ingredients']);
  
  saveDailyTrackerToLocalStorage();
}

//
//function factoryLineItem(){
//  var line_item = {
//    qty: 0,
//    uints: 'g',
//    each: 0,
//    item: '',
//    time: new Date,
//    img_id: 0,
//    html_id: ''
//  }
//  
//  line_item
//}


// find parent table body from row element, get id
function scanAncestorsForTag(elementNode, tag){

  while(elementNode){

    elementNode = elementNode.parentNode;
    
    if (elementNode.tagName.toLowerCase() === tag) {
      console.log(`FOUND ancestor ${tag}`);
      console.log(elementNode);
      return elementNode;
    }    

  }
}

// var undoList = { 0: factory_line_item() }
// parse entry into factoryline
var undoList = [];

function getComponentRef(tableId){
  var componentRef = dtk['dtk_rcp'];
  
  console.log(`COMPONENT_REF from tableId<${tableId}> - - - - - < <`);
  console.log(`COMPONENT_REF ${componentRef['ri_name']} <`);
  
  return componentRef;
}

function removeItemFromComponent(dtk, tableId, elementId){
  
  // keep and incase need to undo!
  var undoItem = { 'prevSib':     null,
                   'itemElement': document.getElementById(elementId),
                   'lineArr':     null,
                   'nextSib':     null,
                   'parent':      tableId };  

  // check if 1st node => NO previous sibling
  prevNode = document.getElementById(elementId).previousSibling;  
  if (prevNode) { undoItem['prevSib'] = prevNode.getAttribute('id'); }
  
  // check if Last node => NO next sibling
  nextNode = document.getElementById(elementId).nextSibling;
  if (nextNode) { undoItem['nextSib'] = nextNode.getAttribute('id'); }
  
  //                               component   ingredient/item
  //                                    |        |
  // idendify item in component from tableId, rowId
  // tableId: table-tracked-items - daily tracker
  // tableId: other - recipe or component being edited/created
    
  // de-reference table - simplify code below  
  recipeTracker = getComponentRef(tableId);
  
  // copy it to return for undo
  //console.log(`recipeTracker: deleting ${elementId} ---- S`);
  //console.log(recipeTracker['ingredients']);
  
  // go through items find the item to remove
  for (var item = 0; item < recipeTracker['ingredients'].length; item++) {
  
    //console.log(`c: ${recipeTracker['ingredients'][item][HTML_ID]} === ${elementId}`);
  
    if (recipeTracker['ingredients'][item][HTML_ID] === elementId) { //got it
      
      // remove it from ingredients & store it in undo list
      undoItem['lineArr'] = recipeTracker['ingredients'].splice(item, 1)[0]; // 3rd optional parameter can swap in            
      
      console.log(`'lineArr': [${undoItem['lineArr'].length}] ${undoItem['lineArr']}`);
      
      break;
    }
    
  }
  //console.log(`pSib: ${undoItem['prevSib']} >-D`);
  //console.log(`elem: ${document.getElementById(elementId)} - ${elementId}`)
  //console.log(`nSib: ${undoItem['nextSib']} >-D`);
  //console.log(`deleted: ${undoItem['lineArr']} >-D`);
  console.log(`recipeTracker: deleting ${elementId} ---- E`);
    
  // return it
  return undoItem;
}


// delete item from tracker/component table
function clickHandler(e) {

  if (e.target.classList.contains('delete')) { // clicked on a delete button  
    
    // identify element to delete from buttons parent row (td.parent)
    var tableRow = scanAncestorsForTag(e.target, 'tr');   
    var elementId = tableRow.getAttribute('id');
    
    var tableBody = scanAncestorsForTag(e.target, 'tbody');
    
    // get table id from element parents - get id
    var table = scanAncestorsForTag(tableRow, 'table');
    var tableId =  table.getAttribute('id');
    
    // remove item from model - use tag id
    // undo item should contain doubley linked row refs - before & after silings
    // store item to delete in undo list
    //undoList.push( removeItemFromComponent(dtk['dtk_rcp'], tableId, elementId) );
    
    undoList.push( removeItemFromComponent(dtk['dtk_rcp'], 'table-tracked-items', elementId) );
    console.log(`UNDO < Item: ${undoList[undoList.length-1]['itemElement'].getAttribute('id')} <`);
        
    // remove item from table
    tableBody.removeChild(tableRow);
    
    invalidateYield();

    saveDailyTrackerToLocalStorage();   // make data persistent when tabs change
  }
  
}


function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

// this feels very cumbersomb! and not very DRY
// TODO - REFACTOR
// pop() from the deleted stack and re-insert into model
function undeleteItemFromComponent(e){
  var success = false;
  if (undoList.length === 0) { success = true; return success; }
      
  var undoItem = undoList.pop();
  
  invalidateYield();
  
  recipeTracker = getComponentRef(undoItem['parent']);
    
  console.log(`recipeTracker: restoring ${undoItem['lineArr'][HTML_ID]} ---- S`);
  console.log(recipeTracker['ingredients']);
  
  // go through insert after previous sibling - if it exists
  for (var item = 0; item < recipeTracker['ingredients'].length; item++) {
  
    console.log(`c: ${recipeTracker['ingredients'][item][HTML_ID]} === ${undoItem['prevSib']}`);
    
    if (recipeTracker['ingredients'][item][HTML_ID] === undoItem['prevSib']) { //got it
      
      // add it to ingredients & update table
      recipeTracker['ingredients'].splice(item+1, 0, undoItem['lineArr']);
      
      // update table - insertAfter(newNode, referenceNode)      
      refNode = document.getElementById(undoItem['prevSib']);
      insertAfter(undoItem['itemElement'], refNode);
      
      success = true; return success;
    }    
  }
  
  // didn't find it? try nextSibling - undoItem['nextSib']
  for (var item = 0; item < recipeTracker['ingredients'].length; item++) {
  
    console.log(`c: ${recipeTracker['ingredients'][item][HTML_ID]} === ${undoItem['nextSib']}`);
    
    if (recipeTracker['ingredients'][item][HTML_ID] === undoItem['nextSib']) { //got it
      
      // add it to ingredients & update table
      recipeTracker['ingredients'].splice(item, 0, undoItem['lineArr']);

      // update table - insertBefore
      // parentNode.insertBefore(newNode, referenceNode);
      refNode = document.getElementById(undoItem['nextSib']); 
      refNode.parentNode.insertBefore(undoItem['itemElement'], refNode);
            
      success = true; return success;
    }    
  }  
  
  // didn't find that? insert at begining
  if (recipeTracker['ingredients'].length === 0) {    
    recipeTracker['ingredients'][0] = undoItem['lineArr'];
    
    // update empty table with a row
    table = document.getElementById(undoItem['parent']);
    addRowToTable(table, undoItem['lineArr']);
    
    success = true; return success;
  }
  
  return success;
}

//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// LOAD STORE / Local storage
// TODO - break out into local storage utils - also in quick_synch.js
//      - use dtk_storage.js
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// local storage API
// setItem(): Add key and value to localStorage
// getItem(): Retrieve a value by the key from localStorage
// removeItem(): Remove an item by key from localStorage
// clear(): Clear all localStorage
// key(): Passed a number to retrieve nth key of a localStorage
// Pattern:
// https://stackoverflow.com/questions/2010892/storing-objects-in-html5-localstorage
// https://blog.logrocket.com/the-complete-guide-to-using-localstorage-in-javascript-apps-ba44edb53a36/
// https://mathiasbynens.be/notes/localstorage-pattern

                               // various device & display detect
function getPlatformInfo(){ // https://stackoverflow.com/questions/3514784/what-is-the-best-way-to-detect-a-mobile-device
  
  console.log('DEVICE ID:');
  console.log(navigator.userAgent);
  console.log('DEVICE ID:');
  // Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)
  // AppleWebKit/537.36 (KHTML, like Gecko)
  // Chrome/76.0.3809.100
  // Safari/537.36
  return '_genericDevice';
}

var lastSavedFile = '';
// HARD code a bootstrap UUID
var youAreWhoISayYouAre = '014752da-b49d-4fb0-9f50-23bc90e44298';
var userUUID = youAreWhoISayYouAre;
var deviceInfo = getPlatformInfo();

if (typeof(Storage) !== "undefined") {
  lastSavedFile = window.localStorage.getItem('lastSavedFile'); // key = 'lastSavedFile'
  console.log(`LASTSAVED FILENAME = ${lastSavedFile} <<`);
} else {
  console.log(`NO LOCAL STORAGE SUPPORT <<`);
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// store dtk object to ssm / 'disc' / nvm
// - - - - - - - - - - - - - - - - - - - - - - - - - - - -
function saveDailyTrackerToLocalStorage(){
  var succeeded = false;

  // dtk_[timestamp]_[userUUID].JSON  
  var fileName = `dtk_${ dtk['dtk_rcp']['dt_date'] }_${ userUUID }_${ deviceInfo }`;
  
  try {        
    window.localStorage.setItem( fileName, JSON.stringify(dtk) );
    
    lastSavedFile = fileName;   // store last save filename (which changes) in a consistent place
    
    window.localStorage.setItem( 'lastSavedFile', lastSavedFile );
    
    succeeded = true;
    
    debugOutputDiv.innerHTML = `Saving . . ${fileName}`;      

  } catch (err) {

    console.log(`**** WARNING: save to local storage FAILED ${err}`);

    console.log(err);

  }
  
  // POST to server too.
  
  return succeeded;
}

function saveDTKLocallyThenPostToServer (){
  var success = false;    
  
  // TODO need to wait for result fix this!
  if (saveDailyTrackerToLocalStorage() === true) {
    if (fetchUpdateDailyTrackerNutrients() === true) {
      success = true;
    }    
  }
  
  return success;
}


function clearLocalStorage() {
  var retVal = localStorage.clear();
  console.log(`localStorage.cleared >${retVal}<`);
}

// to list keys AND contents
// set withContents = true
function listLocalStorageKeys(withContents = false) {
  // 'iterating' though local storage
  
  console.log( `>- - - - - listLocalStorageKeys: [${localStorage.length}] (${typeof(localStorage)}) <` );
  console.log(`DEVICE: ${getPlatformInfo()}`);
  
  for (var i = 0; i < localStorage.length; i++){
  
    if (lastSavedFile === localStorage.key(i)) {
      dtk = JSON.parse( localStorage.getItem(localStorage.key(i)) );
      console.log( `GOT IT:: ${localStorage.key(i)} <` );
    }
  
    console.log(`>- - - - - - - - - - - - ls keys [${i}] \\\\ `);
    
    console.log( `lsKey: ${localStorage.key(i)} <` );
  
    if (withContents) console.log( localStorage.getItem(localStorage.key(i)) );
    
    console.log('>- - - - - - ');
  }
  
  console.log('>- - - - - - - - - - - - ls keys // ');
}


// JSON.parse(string, function)
    // create object from JSON string, func can be used for further conversion
  
// JSON.stringify(obj, replacer, space)  // space - tab spaces, replacer filter function
    // var obj = { "name":"John", "age":30, "city":"New York"};
    // var myJSON = JSON.stringify(obj);

// load dtk object to ssm / 'disc' / nvm 
function loadDailyTrackerFromLocalStorage(){

  // clear current tracker table
  tbody = trackerTable.getElementsByTagName("tbody")[0];  
  trackerTable.removeChild(tbody);

  // load last saved
  lastSavedFile = window.localStorage.getItem('lastSavedFile');  
  dtkLocal = JSON.parse( window.localStorage.getItem(lastSavedFile) ); // key = content of lastSavedFile
  
  // if server side has archived & rolled over to fresh day prefer it instead
  if (dtkLocal['dtk_rcp']['dt_rollover'] < dtk['dtk_rcp']['dt_rollover']) {
    console.log('WARNING ROLLED OVER using FRESH server dtk');
    console.log(`dtkLocal_ro: ${dtkLocal['dt_rollover']} < dtk_ro: ${dtk['dt_rollover']} = ${dtkLocal['dt_rollover'] < dtk['dt_rollover']}`);
  } else {
    console.log('loadDailyTrackerFromLocalStorage: LOADED ');
    console.log(`dtkLocal_ro: ${dtkLocal['dt_rollover']} < dtk_ro: ${dtk['dt_rollover']} = ${dtkLocal['dt_rollover'] < dtk['dt_rollover']}`);
    dtk = dtkLocal;
  }
  
  dtkState = 'yieldInvalid';

  console.log(`Loaded DTK = ${dtk} <<\n<<\n<<\n<<`);

  buildTableFromDailyTracker();
}


// post DTK for processing to...
// fetch Nutrients
function fetchUpdateDailyTrackerNutrients() {
  var success = false;
  // TODO - careful think about where/when to set this - new recipe vs daily tracker
  //dtk['dtk_rcp']['ri_name'] = createDailyTrackerNameFromNixTime();
  //console.log("--------> dtk['dtk_rcp']['ri_name']");
  //console.log(dtk['dtk_rcp']['ri_name']);
  //console.log("--------> dtk['dtk_rcp']['ri_name']");
    
  fetch( '/tracker', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json' },             // JSON
    body: JSON.stringify( { 'user':userUUID, 'dtk':dtk } )      // Payload        

  }).then( function(response) {
    
    console.log("  - - - -|- - - - response")
    console.log(response);
    console.log("  - - - -|- - - -")
    console.log(typeof(response))
    console.log("  - - - -|- - - -")
    
    //return response.text();
    return response.json();
  
  }).then( function(data) {
    
    // iterator 1
    text = 'iterator 1 style - - - - - - - - - - - - - - - - - - - - '
    console.log(`POST response: ${text} - ${typeof(data)} - ${data.length} <`);
    Object.entries(data).forEach(        
        ([key, value]) => {
          console.log('====================');
          console.log(key, value);
        }
    );
    
    // iterator 2
    text = 'iterator 2 style- - - - - - - - - - - - - - - - - - - - '
    console.log(`POST response: ${text} - ${typeof(data)} - ${data.length} <`);
    console.log(`POST response: \n ${data}`);
    
    // gor through object keys - list of outstanting file by category
    for (const [key, value] of Object.entries(data)) {
        console.log('====================');
        console.log(key, value);                
    }
    console.log('====================');
        
    dtkState = 'loadedValid';
    console.log(`DTK returned: ${dtkState}`);    // should read "POST response: OK"
  
    recipes = [ data['dtk_rcp'] ] // load recipes array
    
    fill_in_nutrients_table();
    
    success = true;
    console.log(`fetchUpdateDailyTrackerNutrients INside: \n ${success}`);
  });
  
  // TODO this comes back straight await (before console above) - use await?
  console.log(`fetchUpdateDailyTrackerNutrients OUTside: \n ${success}`);
  return success;
}



//// Filter Items
//function filterItems(e){
//  // convert text to lowercase
//  var text = e.target.value.toLowerCase();
//  
//  // Get lis
//  var items = itemList.getElementsByTagName('li');
//  
//  // Convert to an array
//  Array.from(items).forEach( function(item){
//    var itemName = item.firstChild.textContent;
//    if(itemName.toLowerCase().indexOf(text) != -1){
//      item.style.display = 'block';
//    } else {
//      item.style.display = 'none';
//    }
//  });
//}

//- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// build tracker table
loadDailyTrackerFromLocalStorage();


var array = [0, 1, null, 2, "", 3, undefined, 3,,,,,, 4,, 4,, 5,, 6,,,,];

// remove empty, null and undefined
var filtered = array.filter(function (i) { return ((i != "") && (i != null)); }); // remove empty, null and undefined

console.log(filtered);

console.log( convertToGrams(100, 'g', 'veg oil') );
console.log( convertToGrams(100, 'g', 'water') );
console.log( convertToGrams(6, 'g', 'wasabi') );
console.log( convertToGrams(7, 'tsp', 'sugar') );
console.log( convertToGrams(10, 'cups', 'chicken stock') );
//8 medium onions
//16 pork cheeks
//1/4 banana
//4 large red peppers

console.log("createDailyTrackerNameFromNixTime");
console.log(createDailyTrackerNameFromNixTime());
