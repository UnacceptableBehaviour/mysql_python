

const rcpImages = document.querySelectorAll('.image-container img');

var saveFavsAsTypeBtn = document.getElementById('but-save-favs');
saveFavsAsTypeBtn.addEventListener('click', saveFavsAsType);

var favsTypeLabelInput = document.getElementById('save-favs-label');
favsTypeLabelInput.placeholder = 'enter save as label here . .';
favsTypeLabelInput.addEventListener('keyup', function(event) {   // act on hit return key
  if (event.key === "Enter") { saveFavsAsType(); }
});

// a user could save these directly to DB using this route
// TODO - data route think through
function saveFavsAsType(){
  let label = favsTypeLabelInput.value;  
  console.log(`saveFavsAsType: ${label}`);

  // const id_name_pairs = [];
  // const ri_ids = [];
  const ri_names = [];

  for (let i = 0; i < favRecipes.length; i++) {
  
    const recipe = favRecipes[i];
    
    //const entry = [recipe["ri_id"], recipe["ri_name"]];
    
    //ri_ids.push(recipe["ri_id"]);       // TODO - comment back in for live DB insert
    ri_names.push(recipe["ri_name"]);
    //id_name_pairs.push(entry);
  
  }  

  // post info to DB
  fetch( '/favs', {
    method: 'POST',                                             // method (default is GET)
    headers: {'Content-Type': 'application/json' },             // JSON
    body: JSON.stringify( { 'user':userUUID, 'save_label':label, 
                            //'ri_ids': ri_ids,
                            'ri_names': ri_names,
                            //'id_name_pairs': id_name_pairs,
                          } )      // Payload

  }).then( function(response) {
    return response.json();

  }).then( function(saveFavsResponse) {
    console.log('----*----');
    console.log("AHEM FAVS:", saveFavsResponse);    
    console.log('----*----');
  })
  //.catch(err){
  //  console.log("WTF", err);
  //};  

}

// Add SHOW recipe (click on image) click handler
for (let i = 0; i < rcpImages.length; i++) {
  const container = rcpImages[i];

  // USING GET TO DIPLAY RECIPE
  container.addEventListener('click', () => {

    const recipeId = container.getAttribute('value');
    const url = `/db_recipe_page?ri_id=${recipeId}`;    

    fetch(url)
    .then(response => {
      // check response
      if(!response.ok) {
        throw new Error('Error submitting form');
      }      
      window.location.href = url;     // show recipe
    });
  
    console.log(`id:${recipeId} exit`);
  });
}

const removeBtns = document.querySelectorAll('button.favs-close');
for (let i = 0; i < removeBtns.length; i++) {
  const container = removeBtns[i];

  container.addEventListener('click', (el) => {
    const recipeId = container.getAttribute('value');
    console.log(el);
    console.log(`Rmv: ${recipeId}`);


    // Make POST request            - - - < REMOVE FAV RCP
    // Create a FormData object
    const body = {
      ri_id: recipeId 
    };
    
    fetch('/favs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
    .then(response => {
      if(!response.ok) {
        throw new Error('Error submitting form');
      }
      
      // Redirect?
      // window.location.href = '/db_recipe_page'; 
    })  
  

    const recipeCard = el.target.closest('.recipe-card');
    console.log(recipeCard);
    recipeCard.remove();
    //document.getElementsByClassName('close')[0].closest('.recipe-card')

  });  
}

const blogPostBtns = document.querySelectorAll('button.blog-post');
for (let i = 0; i < blogPostBtns.length; i++) {
  const container = blogPostBtns[i];

  // USING GET TO DIPLAY RECIPE
  container.addEventListener('click', () => {

    const recipeId = container.getAttribute('value');
    const url = `/email_debug?ri_id=${recipeId}`;

    fetch(url)
    .then(response => {
      // check response
      if(!response.ok) {
        throw new Error('Error submitting form');
      }      
      window.location.href = url;     // show recipe
    });
  
    console.log(`id:${recipeId} exit`);
  });
}



{/* <div class="recipe-card">

  <div class="image-container">
    <img src="https://asset.server:8080/static/recipe/20200822_151526_nectarine salsa.jpg" value="1644"> 
  </div>

  <div class="content">
    <h2 class="title">nectarine salsa</h2>

    <div class="info">
      190.0g  <p style="display: inline;">79.0kcal/100g</p> = 150kcals
      <!-- <p>sweet sharp spicy great w/ prawns</p> -->
    </div>

    <button class="close" value="1644">X</button>
  </div>

</div> */}


    // POST
    // // Create a FormData object
    // const formData = new FormData();
  
    // // Append the recipeId to it  
    // formData.append('ri_id', recipeId);
  
    // console.log(`id:${recipeId} fetch`);
    // // Make POST request
    // fetch('/db_recipe_page', {
    //   method: 'POST', 
    //   body: formData
    // })
    // .then(response => {
    //   if(!response.ok) {
    //     throw new Error('Error submitting form');
    //   }
      
    //   // Redirect to recipe page
    //   window.location.href = '/db_recipe_page'; 
    // })
    
    
    // // .then( function(response) {    
    // //   return response.json();    
    // // }).then( function() {
    // //   //window.location.replace('/db_recipe_page');
    // //   window.location.href = '/db_recipe_page';
    // // });