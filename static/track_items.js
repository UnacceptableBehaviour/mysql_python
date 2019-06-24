var nutri_table = document.getElementById('nutri_taffic_table_main');
// remove servings & buttons from nutritable - makes no sense for tracker
document.getElementById('traffic_title_0').remove();
document.getElementById('b_update_0').remove();
document.getElementById('b_clear').remove();


var form = document.getElementById('addForm');
//var addItem = document.getElementById('add-item-button');
var itemList = document.getElementById('items');
var filter = document.getElementById('filter');
var undo = document.getElementById('undo-button');


// Form submit event
form.addEventListener('submit', addItem);
//addItem.addEventListener('submit', addItem);

// Delete event
itemList.addEventListener('click', removeItem);
// Undelete
undo.addEventListener('click', undeleteListItem);

// Filter event
// filter.addEventListener('keyup', filterItems);
// addthis back when adding auto complete ingredients 


// Add item
function addItem(e){
  //<li class="list-group-item">
  //  <button class="btn btn-danger btn-sm float-left delete">X</button>
  //  <div class="list-group-item-sub-text">${added_item_text}</div>
  //  <button class="btn btn-default btn-sm float-right add-recipe">Rcp</button>
  //  <button class="btn btn-secondary btn-sm float-right snapshot"><i class="fas fa-camera"></i></button>
  //</li>
  //`<li class="list-group-item"><button class="btn btn-danger btn-sm float-left delete">X</button><div class="list-group-item-sub-text">---- 30g smoked ham</div><button class="btn btn-default btn-sm float-right add-recipe">Rcp</button><button class="btn btn-secondary btn-sm float-right snapshot"><i class="fas fa-camera"></i></button></li>`
  e.preventDefault();

  console.log('e.target.id');
  console.log(e.target.id);
  console.log('>>');
  
  // Get input value
  var newItem = document.getElementById('item').value;
  
  // Create new li element
  var li = document.createElement('li');
  
  //// Add class
  li.className = 'list-group-item';

  var now = new Date;
  var eaten_at = `${now.getHours()}${now.getMinutes()}`;
  
  li.innerHTML = `<button class="btn btn-danger btn-sm float-left delete">X</button><div class="list-group-item-sub-text">${eaten_at} ${newItem}</div><button class="btn btn-default btn-sm float-right add-recipe">Rcp</button><button class="btn btn-secondary btn-sm float-right snapshot"><i class="fas fa-camera"></i></button>`
  
  console.log(eaten_at);
  console.log(newItem);
  console.log((new Date).getHours());
  console.log((new Date).getMinutes());
  
  
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
