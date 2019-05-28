#! /usr/bin/env python

# Quick note on generating a call graph - darwin / osx
	# $ pip install pycallgraph
	# $ brew install graphviz
	# $ pycallgraph --include "helpers.*" graphviz -- ./populate_db.py
	# # http://pycallgraph.slowchop.com/en/master/guide/command_line_usage.html

# helper functions

#import csv
import itertools
import re
import copy                 # copy.deepcopy()
#from pathlib import Path

from pprint import pprint # giza a look


# indexes for ingredients row
ATOMIC_INDEX = 0                    # default value is 1 - TRUE
QTY_IN_G_INDEX = 1
SERVING_INDEX = 2
INGREDIENT_INDEX = 3


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


    

  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# def ingredient_in_recipe_list(ingredient, recipies_and_subcomponents):
#     found = None
#     
#     for recipe in recipies_and_subcomponents:
#         if recipe['ri_name'] == ingredient[INGREDIENT_INDEX]:
#             found = recipe
#     
#     return found
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# typical recipe
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # recipe_info = {
    #     'ri_name':"Initialised as NO MATCH",
    #     'ingredients':"Pure green",
    #     'allergens': [ 'none_listed' ],
    #     'tags': [ 'none_listed' ],
    #     'servings': 0,
    #     'yield': '0g'
    # }
#{'ingredients': [[1, '250g', '(0)', 'cauliflower'],    # sublist
#                 [1, '125g', '(0)', 'grapes'],
#                 [1, '200g', '(4)', 'tangerines'],
#                 [1, '55g', '(0)', 'dates'],
#   atomic >-------1, '8g', '(0)', 'coriander'],
#                 [1, '8g', '(0)', 'mint'],
#                 [1, '4g', '(0)', 'chillies'],
#   sub_comp >-----0, '45g', '(0)', 'pear and vanilla reduction lite'],
#                 [1, '2g', '(0)', 'salt'],
#                 [1, '2g', '(0)', 'black pepper'],
#                 [1, '30g', '(0)', 'flaked almonds']],
#  'ri_name': 'cauliflower california',
#  'atomic' : 0
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
def get_single_recipe_in_display_dicts(ri_id):
    recipe_info = {
        'ri_id': ri_id,
        'ri_name':"Initialised as NO MATCH",
        'image_file':'bouncy.jpg',
        'desc': "Tasty veggie dish . . . ",
        'nutrinfo': {
            'servings': 0,
            'yield': '0g'            
        },
        'components': {},                       # ingredients or each component
        'allergens': [ 'none_listed' ],
        'tags': [ 'none_listed' ],
    }
    
    #for idx, ingredient in enumerate(recipe_dict['ingredients']):
        
    return recipe_info



def get_recipes_in_display_dicts(list_of_recipe_ids):
    recipe_list = []
    
    for ri_id in list_of_recipe_ids:
        get_single_recipe_in_display_dicts(ri_id)

    recipe_list


    
if __name__ == '__main__':
    print("-----  attaching to DB ------------------------------------S")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different
    db = scoped_session(sessionmaker(bind=engine))
    db_lines = db.execute("SELECT ri_id, ri_name FROM recipes;").fetchall()
    
    # for line in db_lines:
    #     for index, content in enumerate(line):
    #         print(f"{index}\t{line}")
            
    # for line in db_lines:
    #     print(type(line))
    #     print( str(line).lstrip('(').rstrip(',)') )
    
    all_ri_id = [ str(line).lstrip('(').rstrip(',)') for line in db_lines ]
    
    pprint(all_ri_id)
    ['1304','2403','402']
    
    print("-----  attaching to DB ------------------------------------E")

    print("-----  get recipes in display format ------------------------------------S")
    get_recipes_in_display_dicts( all_ri_id )
    print("-----  get recipes in display format ------------------------------------E")

