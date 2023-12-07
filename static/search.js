
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
//cs50_recipes=# SELECT ri_id,ri_name, tags FROM recipes WHERE 'veggie' = ANY(tags);
// ri_id |              ri_name              |                                   tags
//-------+-----------------------------------+--------------------------------------------------------------------------
//   901 | spinach tortilla                  | {veggie,gluten_free,msg,ns_pregnant}
//  2701 | mushroom risotto                  | {veggie,cbs,gluten_free}
//  3101 | goats cheese and spinach omelette | {veggie,gluten_free}
//  3401 | simple beef and onion broth       | {vegan,veggie,cbs,chicken,pork,beef,seafood,shellfish,gluten_free,ns_pregnant}
//(4 rows)


var searchButton = document.getElementById('but-recipe-search');
searchButton.addEventListener('click', searchForRecipe);

var saveCheckedBtn = document.getElementById('but-return-checked');
saveCheckedBtn.addEventListener('click', saveCheckedRcps);

var checkAllBtn = document.getElementById('but-check-all-lbl');
checkAllBtn.addEventListener('click', checkAllRcpsLabel);

var checkAllBtn = document.getElementById('but-check-all-fav');
checkAllBtn.addEventListener('click', checkAllRcpsFavs);



var searchFrom = document.getElementById('recipe-search-2-inrow');
searchFrom.placeholder = 'search string';
searchFrom.addEventListener('keyup', function(event) {   // act on hit return key
  if (event.key === "Enter") { searchForRecipe(); }
});

var rcpsToUnlabel = [];
var rcpsShortList = [];

function checkBoxClicked(event) {
    if (event.target.checked) {
      
      if (event.target.id.includes('flexCheckFAVS_')){
        let ri_id = event.target.id.replace('flexCheckFAVS_','');
        rcpsShortList.push(ri_id);
      } else {
        rcpsToUnlabel.push(event.target.value);
      }        
    
    } else {
      if (event.target.id.includes('flexCheckFAVS_')){
        let ri_id = event.target.id.replace('flexCheckFAVS_','');
        let index = rcpsShortList.indexOf(ri_id);
        if (index > -1) {
          rcpsShortList.splice(index, 1);
        }

        rcpsShortList.push(event.target.value);
      } else {
        let index = rcpsToUnlabel.indexOf(event.target.value);
        if (index > -1) {
            rcpsToUnlabel.splice(index, 1);
        }
      }
    }
}


// for one
// document.querySelector('.form-check-input').addEventListener('click', checkBoxClicked);
// for many
function addCheckboxListeners(){
  let checkboxes = document.querySelectorAll('.form-check-input');

  checkboxes.forEach(function(checkbox) {
      checkbox.addEventListener('click', checkBoxClicked);
  });  

  // let checkboxLabels = document.querySelectorAll('.form-check-label');
  // checkboxLabels.forEach(function(checkboxLabel) {
  //   checkboxLabel.addEventListener('click', checkBoxClicked);
  // });  
}





function checkAllRcpsLabel(){
  checkAllRcps('flexCheckLBL_');  
}

function checkAllRcpsFavs(){
  checkAllRcps('flexCheckFAVS_');  
}

function checkAllRcps(checkType) {
  let checkboxes = document.querySelectorAll('.form-check-input');
  rcpsToUnlabel = [];
  rcpsShortList = [];
  checkboxes.forEach(function(checkbox) {
    if (checkbox.id.includes(checkType)){
      checkbox.checked = true;
      if (checkType === 'flexCheckLBL_'){
        rcpsToUnlabel.push(checkbox.value);
      } else {
        let ri_id = checkbox.id.replace('flexCheckFAVS_','');
        rcpsShortList.push(ri_id);
      }
      
    }
  });    
}

function saveCheckedRcps(){
  let search = searchFrom.value;

  fetch( '/search', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json' },             // JSON
    body: JSON.stringify( { 'user':userUUID,
                            'alt_label': search,
                            'rcpsToUnlabel': rcpsToUnlabel,
                            'rcpsShortList': rcpsShortList } )      // Payload

  }).then( function(response) {
    return response.json();
  }).then( function(saveChecked_response) {    
    console.log('SCR----*----S');
    console.log("AHEM:", saveChecked_response);
    console.log('SCR----*----E');
  })
}


function searchForRecipe (){

  search = searchFrom.value;

  if (search === "") search ='%'; // match anything - just use filters & tags - TODO randomise for roulette!

  // post info to DB
  fetch( '/search', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json' },             // JSON
    body: JSON.stringify( { 'user':userUUID, 'search':search } )      // Payload

  }).then( function(response) {
    return response.json();

  }).then( function(search_response) {
    console.log('----*----');
    console.log("AHEM:", search_response);    
    //gallery_html = renderRecipeCard(search_response[0]);
    gallery_html = renderGalleryFromResult(search_response);
    //console.log(gallery_html);
    console.log('----*----');
    gallery = document.getElementById('rcp-gallery');
    gallery.innerHTML = gallery_html;
    addCheckboxListeners();
  })
  //.catch(err){
  //  console.log("WTF", err);
  //};
}

function renderRecipeCard(rcpInfo){
  //<div class="card">
  //    <img class="card-img-top" src="https://asset.server:8080/static/recipe/{{recipe_info['lead_image']}}"></img>
  //    <div class="card-body">
  //        <h5 class="card-title">{{ recipe_info['ri_name'] }}</h5>
  //        <p class="card-text">{{ recipe_info['description'] }}</p>
  //        <!-- (recipe_info['user_rating']|int) user_rating is a float use a filter to covert to int -->
  //        {% for stars in range((recipe_info['user_rating']|int)) %}
  //        <i class="fa fa-star recip-star-up-rating"></i>
  //        {% endfor %}
  //        {% for stars in range(5 - (recipe_info['user_rating']|int)) %}
  //        <i class="fa fa-star recip-star-down-rating"></i>
  //        {% endfor %}
  //        <button type='submit' name="gallery_button_{{ recipe_info['ri_id'] }}" value="{{ recipe_info['ri_id'] }}" class="btn btn-outline-secondary float-right">Show!</button>
  //    </div>
  //</div>

  // TODO - serve from environment
  //ASSET_ROOT = 'http://192.168.1.13:8000/'
  ASSET_ROOT = 'https://asset.server:8080/'   // otherwise https fails - & no images
  assets_url = `${ASSET_ROOT}static/recipe/`; // local dev

  //ASSET_ROOT = ''
  //assets_url = `${ASSET_ROOT}static/images/`; // heroku

  var html_stars = '';
  for ( var i = 0; i < 5; i++ ) {
    if ( i+1 <= parseInt(rcpInfo['user_rating']) ) {                          // gold star
      html_stars += '<i class="fa fa-star recip-star-up-rating"></i>';
    } else {                                                              // black star
      html_stars += '<i class="fa fa-star recip-star-down-rating"></i>';
    }
  }

  html_card = `<div class="card">
        <img class="card-img-top" src="${assets_url}${rcpInfo['lead_image']}"></img>
        <div class="card-body">
            <h5 class="card-title">${rcpInfo['ri_name']}</h5>
            <p class="card-text">${rcpInfo['description']}</p>
            ${html_stars}
            <button type='submit' name="gallery_button_${ rcpInfo['ri_id'] }" value="${ rcpInfo['ri_id'] }" class="btn btn-outline-secondary float-right">Show!</button>
            <div class="form-check">
            <input class="form-check-input" type="checkbox" value="${rcpInfo['ri_name']}" id="flexCheckLBL_${rcpInfo['ri_id']}">
            <label class="form-check-label" for="flexCheckLBL_${rcpInfo['ri_id']}">
              Un/Label
            </label>            
            </div>
            <div class="form-check">
            <input class="form-check-input" type="checkbox" value="${rcpInfo['ri_name']}" id="flexCheckFAVS_${rcpInfo['ri_id']}">
            <label class="form-check-label" for="flexCheckFAVS_${rcpInfo['ri_id']}">
              Add to List
            </label>    
            </div>
        </div>
  </div>`

  return html_card;
}

function renderGalleryFromResult(recipeList){
  var htmlInnerGallery = ''

  if (typeof(recipeList) === 'object') {

    for (var rcpNo = 0; rcpNo < recipeList.length; rcpNo++ ) {
      htmlInnerGallery += renderRecipeCard(recipeList[rcpNo]);
    }

  }

  var html_gallery = `<div class="row padding">
      <div class="card-columns">
          <form action='/db_recipe_page' method='POST'>
            ${htmlInnerGallery}
          </form>
      </div>
  </div>`;

  return html_gallery;
}
