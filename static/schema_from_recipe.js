// these are also defined in recipe_dtk_multi.js
// break out into common file DRY
const IGD_IDX_TYPE = 0;
const IGD_IDX_QTY  = 1;
const IGD_IDX_EACH = 2;
const IGD_IDX_NAME = 3;


// schema_from_recipe.js
class SchemaRecipe {
  constructor(recipe) {
    this.recipe = recipe;
  }

  generateSchema() {    
    const r  = this.recipe;
    console.log('r', r);
    console.log(' - - - * - - - ');
    console.log('this.recipe', this.recipe);
    console.log(' - - - * - - - ');
    let serving_size_text = `${r.nutrinfo.serving_size}${r.nutrinfo.units}`;

    return JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Recipe",        // https://schema.org/Recipe
      "name": r.ri_name,
      "recipeIngredient": r.ingredients.map(i => i[IGD_IDX_NAME]),
      "recipeYield": r.nutrinfo.yield,
      "recipeInstructions": r.method.replace('\n', '').replace('\t', '').split('.'),  // method
      "description": r.description,

      // stars
      "aggregateRating": 5, //r.user_rating,
    //   "aggregateRating": {  // https://schema.org/AggregateRating
    //     "@type": "AggregateRating",
    //     "ratingValue": r.user_rating,
    //     "reviewCount": 1                    //r.num_reviews
    //   },

      // allergens - in keywords
      //"allergens": r.allergens,  // https://schema.org/RestrictedDiet

      // tags   
      "recipeCuisine": r.tags,
      
      // type
      "recipeCategory": r.types,

      "image": `static/recipe/${r.lead_image}`,

      "keywords": [...r.allergens, ...r.tags, ...r.types],  // https://schema.org/RestrictedDiet

      // https://schema.org/NutritionInformation
      "nutrition":{     
        "@type":"NutritionInformation",
        "calories":r.nutrinfo.n_En,
        "fatContent": r.nutrinfo.n_Fa,        
        "saturatedFatContent": r.nutrinfo.n_Fs,
        "unsaturatedFatContent": r.nutrinfo.n_Fm + r.nutrinfo.n_Fp,
        //"transFatContent": r.nutrinfo.n_
        //"cholesterolContent": r.nutrinfo.n_
        "carbohydrateContent": r.nutrinfo.n_Ca,
        "sugarContent": r.nutrinfo.n_Su,
        "fiberContent": r.nutrinfo.n_Fb,
        "proteinContent": r.nutrinfo.n_Pr,
        "sodiumContent": r.nutrinfo.n_Sa,
        "servingSize": `${r.nutrinfo.serving_size}${r.nutrinfo.units}`, //serving_size_text,
      },
      //"recipeNotes": r.notes, // notes not defined in schema.org
      "author": r.username,
      "datePublished": r.dt_date_readable,
      "dateModified": r.dt_last_update,
    });
  }
}













// "nutrition":{
//     "@type":"NutritionInformation",
//     "calories":"170 calories",
//     "fatContent":"3 grams",
//     "fiberContent":"2 grams",
//     "proteinContent":"4 grams"
//  },

export default SchemaRecipe;





// {'UUID': '014752da-b49d-4fb0-9f50-23bc90e44298',
//     'default_filters': {'allergens': [],
//                         'ingredient_exc': [],
//                         'tags_exc': [],
//                         'tags_inc': [],
//                         'type_exc': [],
//                         'type_inc': []},
//     'fav_rcp_ids': [1094, 1095, 1593, 925, 841],
//     'name': 'carter',
//     'tag_sets': {'allergens': ['dairy',
//                                'eggs',
//                                'peanuts',
//                                'nuts',
//                                'seeds_lupin',
//                                'seeds_sesame',
//                                'seeds_mustard',
//                                'fish',
//                                'molluscs',
//                                'crustaceans',
//                                'alcohol',
//                                'celery',
//                                'gluten',
//                                'soya',
//                                'sulphur_dioxide'],
//                  'ingredient_exc': [],
//                  'tags': ['vegan',
//                           'veggie',
//                           'cbs',
//                           'chicken',
//                           'pork',
//                           'beef',
//                           'seafood',
//                           'shellfish',
//                           'gluten_free',
//                           'ns_pregnant'],
//                  'types': ['component',
//                            'amuse',
//                            'side',
//                            'starter',
//                            'fish',
//                            'lightcourse',
//                            'main',
//                            'crepe',
//                            'dessert',
//                            'p4',
//                            'cheese',
//                            'comfort',
//                            'low_cal',
//                            'serve_cold',
//                            'serve_rt',
//                            'serve_warm',
//                            'serve_hot']}}