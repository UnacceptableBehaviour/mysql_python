

const rcpImages = document.querySelectorAll('.image-container img');

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

const removeBtns = document.querySelectorAll('button.close');
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