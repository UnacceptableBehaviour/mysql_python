
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
//  3401 | simple beef and onion broth       | {vegan,veggie,cbs,chicken,pork,beef,seafood,shellfish,gluten_free,ns_pregnant}
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
  //formValue.value = 'vegan';            << USE ACTUAL FORM VALUE!
  formLogic.value = 'contains';
  
  if ( (formField.value === "")|| (formValue.value === "")|| (formLogic.value === "") ) {
    // user pressed SEARCH w/o entering values - see if place holder values valid        
    console.log("INVALID SEARCH VALUES");
    
    // TODO flash the form(s) missing data in red then fade to normal
    
    return;
  }

  //var query = {
  //  field: formField.value,
  //  value: formValue.value,
  //  logic: formLogic.value,
  //}
  //
  //var search = [query];
  
  search = formValue.value;

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
    console.log('----*----');
    //gallery_html = renderRecipeCard(search_response[0]);
    gallery_html = renderGalleryFromResult(search_response);
    console.log(gallery_html);
    console.log('----*----');
    gallery = document.getElementById('rcp-gallery');
    gallery.innerHTML = gallery_html;
    // how to something like . .
    // window.location.replace('/db_gallery', recipes=search_response);
    // window.location.replace('/db_gallery')
    // window.location.href="district.php?dist="+dist;
  })
  //.catch(err){
  //  console.log("WTF", err);
  //};
}

function renderRecipeCard(rcpInfo){
  //<div class="card">
  //    <img class="card-img-top" src="http://192.168.0.8:8000/static/recipe/{{recipe_info['image_file']}}"></img>
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
  
  assets_url = 'http://192.168.0.8:8000/static/recipe/';

  var html_stars = '';
  for ( var i = 0; i < 5; i++ ) {
    if ( i+1 <= parseInt(rcpInfo['user_rating']) ) {                          // gold star
      html_stars += '<i class="fa fa-star recip-star-up-rating"></i>';
    } else {                                                              // black star
      html_stars += '<i class="fa fa-star recip-star-down-rating"></i>';
    }
  }
  
  html_card = `<div class="card">
      <img class="card-img-top" src="${assets_url}${rcpInfo['image_file']}"></img>
      <div class="card-body">
          <h5 class="card-title">${rcpInfo['ri_name']}</h5>
          <p class="card-text">${rcpInfo['description']}</p>
          ${html_stars}        
          <button type='submit' name="gallery_button_${ rcpInfo['ri_id'] }" value="${ rcpInfo['ri_id'] }" class="btn btn-outline-secondary float-right">Show!</button>
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