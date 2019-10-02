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
from datetime import datetime
#datetime.now()

# for gallery stars before actual data
from random import random

import json                 # converting to json string from dict
                            # converting to dict to json string

from pprint import pprint # giza a look

print("----- helpers_db: attaching to DB ------------------------------------S")
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different
helper_db_class_db = scoped_session(sessionmaker(bind=engine))
print("----- helpers_db: attaching to DB ------------------------------------E")


# time helper function for time since epoch, day, 24hr clock

def nix_time_ms(dt=datetime.now()):
    epoch = datetime.utcfromtimestamp(0)
    return int( (dt - epoch).total_seconds() * 1000.0 )

def day_from_nix_time(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%a").lower()

def time24h_from_nix_time(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%H%M")



# indexes for ingredients row
ATOMIC_INDEX = 0                    # default value is 1 - TRUE
QTY_IN_G_INDEX = 1
SERVING_INDEX = 2
INGREDIENT_INDEX = 3
TRACK_NIX_TIME = 4
IMAGE_INDEX = 5
HTML_ID = 6

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# using decorators to implement static vars
# https://stackoverflow.com/questions/279561/what-is-the-python-equivalent-of-static-variables-inside-a-function
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def add_ingredient_w_timestamp(recipe, atomic, qty, ingredient, servings=0):

    # for dev - adding a bunch of ingredients needs to have non identical timestamp
    timestamp = nix_time_ms()                                               #
    static_ts = add_ingredient_w_timestamp.last_time_stamp # readabiliy     #
                                                                            #
    if (static_ts >= timestamp):                                            #
        static_ts += 1                                                      #
        timestamp = static_ts                                               #
                                                                            #
        add_ingredient_w_timestamp.last_time_stamp = static_ts              #
                                                                            #
    # stop duplicate timestamps - - - - - - - - - - - - - - - - - - - - - - # 

    if atomic < 0:
        # look ingredient up in DB and see if we have a recipe (0)
        # or if it's off the shelf (1)
        atomic = -1 # not checked        

    if len(ingredient) == 0:
        ingredient = "ingredient was blank!"

    ingredient_list = [str(atomic), qty, f"({servings})", ingredient, timestamp]
    
    pprint(ingredient_list)
    
    recipe['ingredients'].append(ingredient_list)

# stops duplicate stamps - - - - dev only!
# add attribute that holds last timestamp
add_ingredient_w_timestamp.last_time_stamp = nix_time_ms()
  
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
#{'ingredients': [[1, '250g', '(0)', 'cauliflower', nix_time_in_ms],    # sublist
#                 [1, '125g', '(0)', 'grapes', nix_time_in_ms],
#                 [1, '200g', '(4)', 'tangerines', nix_time_in_ms],
#                 [1, '55g', '(0)', 'dates', nix_time_in_ms],
#   atomic >-------1, '8g', '(0)', 'coriander', nix_time_in_ms],
#                 [1, '8g', '(0)', 'mint', nix_time_in_ms],
#                 [1, '4g', '(0)', 'chillies', nix_time_in_ms],
#   sub_comp >-----0, '45g', '(0)', 'pear and vanilla reduction lite', nix_time_in_ms],
#                 [1, '2g', '(0)', 'salt', nix_time_in_ms],
#                 [1, '2g', '(0)', 'black pepper', nix_time_in_ms],
#                 [1, '30g', '(0)', 'flaked almonds', nix_time_in_ms]],
#  'ri_name': 'cauliflower california',
#  'atomic' : 0
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# cs50_recipes=# \d recipes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                                         Table "public.recipes"
#     Column    |           Type           | Collation | Nullable |               Default               
# --------------+--------------------------+-----------+----------+-------------------------------------
#  id           | bigint                   |           | not null | nextval('recipes_id_seq'::regclass)
#  ri_id        | bigint                   |           | not null | 
#  ri_name      | character varying(100)   |           | not null | 
#  yield        | numeric(9,2)             |           |          | NULL::numeric
#  units        | character varying(10)    |           |          | NULL::character varying
#  servings     | numeric(9,2)             |           |          | NULL::numeric
#  density      | numeric(9,2)             |           |          | NULL::numeric
#  serving_size | numeric(9,2)             |           |          | NULL::numeric
#  atomic       | boolean                  |           |          | false
#  ingredients  | character varying(150)[] |           |          | 
#  allergens    | character varying(150)[] |           |          | 
#  tags         | character varying(150)[] |           |          | 
#  user_tags    | character varying(150)[] |           |          | 
#  image_file   | character varying(100)   |           |          | NULL::character varying
#  text_file    | character varying(100)   |           |          | NULL::character varying
#  n_en         | numeric(9,2)             |           |          | NULL::numeric
#  n_fa         | numeric(9,2)             |           |          | NULL::numeric
#  n_fs         | numeric(9,2)             |           |          | NULL::numeric
#  n_fm         | numeric(9,2)             |           |          | NULL::numeric
#  n_fp         | numeric(9,2)             |           |          | NULL::numeric
#  n_fo3        | numeric(9,2)             |           |          | NULL::numeric
#  n_ca         | numeric(9,2)             |           |          | NULL::numeric
#  n_su         | numeric(9,2)             |           |          | NULL::numeric
#  n_fb         | numeric(9,2)             |           |          | NULL::numeric
#  n_st         | numeric(9,2)             |           |          | NULL::numeric
#  n_pr         | numeric(9,2)             |           |          | NULL::numeric
#  n_sa         | numeric(9,2)             |           |          | NULL::numeric
#  n_al         | numeric(9,2)             |           |          | NULL::numeric
# Indexes:
#     "recipes_pkey" PRIMARY KEY, btree (id)
#     "recipes_ri_id_key" UNIQUE CONSTRAINT, btree (ri_id)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# all fields
# ['id','ri_id','ri_name','yield','units','servings','density','serving_size','atomic','ingredients','allergens','tags',
# 'user_tags','image_file','text_file','n_en','n_fa','n_fs','n_fm','n_fp','n_fo3','n_ca','n_su','n_fb','n_st','n_pr','n_sa','n_al',]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def return_recipe_dictionary():
    nix_time_in_ms = nix_time_ms()
    
    return {
        # fields super sections
        # header:       name image desc             EG gallery          
        'ri_id': 0,
        'ri_name':'none_listed',
        'image_file':'none_listed',
        'text_file':'none_listed',
        'description': 'this fabulously tasty little number is suitable for both carnivores and vegans alike, packed with flavour and protein! Drawbacks . . none_listed',
        'atomic': 1,        # 0 if component / further recipe info available
        'user_rating': 1,
        'dt_date': nix_time_in_ms,
        'dt_day': day_from_nix_time(nix_time_in_ms),
        'dt_time': time24h_from_nix_time(nix_time_in_ms),

        # info:         nurients, servings, etc     Traffic Lights & Nutrition
        'nutrinfo': {
            'servings': 0,
            'serving_size': 0,
            'yield': '0g',
            'units': 'g',
            'density': 1,            
            'n_En':0, 'n_Fa':0, 'n_Fs':0, 'n_Fm':0, 'n_Fp':0, 'n_Fo3':0, 'n_Ca':0,
            'n_Su':0, 'n_Fb':0, 'n_St':0, 'n_Pr':0, 'n_Sa':0, 'n_Al':0
        },
                
        # top level ingredients - look for sub component flags to dig deeper
        'ingredients': [],
        'method': {},

        # tags:         tags, allergens, user_tags  Simplify classification
        'allergens': [ 'none_listed' ],
        'tags': [ 'none_listed' ],
        'user_tags': [ 'none_listed' ],
        
        # SUB COMPONENT RECIPES
        # components:  { 'component name': recipe dictionary, . . . }
        'components': {},
        
    }

#
# re-design schema to get rid of arrays - this will do to learn HTML/CSS/JS for now
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# interface to DB
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_single_recipe_from_db_for_display_as_dict(ri_id_or_name, fields=None):
    
    print(f"----- QUERY: helper_db_class_db: get_single_recipe_from_db_for_display_as_dict ---------S:{ri_id_or_name}")
    updated_info = return_recipe_dictionary()
    #pprint(updated_info)
    
    # fields super sections - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # header:       name image desc             EG gallery
    # nutrinfo:     nurients, servings, etc     Traffic Lights & Nutrition    
    # components:   name, ingredients           Subcomponents & ingredients
    # tags:         tags, allergens, user_tags  Simplify classification
    # -
    nutrinfo_dict_keys = [ k for k, v in updated_info['nutrinfo'].items() ]
    
    # query db - the index from fields is used to retrive and alocate data to correct dictionary entry - -
    if fields == None:
        fields = ['id','ri_id','ri_name','yield','units','servings','density','serving_size',
                  'atomic','ingredients','allergens','tags','user_tags','image_file','text_file',
                  'n_En','n_Fa','n_Fs','n_Fm','n_Fp','n_Fo3','n_Ca','n_Su','n_Fb','n_St','n_Pr','n_Sa','n_Al']

    qry_string = ', '.join(fields)
    
    if type(ri_id_or_name).__name__ == 'str':
        print(f"ri_id_or_name is a string [{ri_id_or_name}] - {type(ri_id_or_name).__name__} - {type(ri_id_or_name)}")
        sql_query = f"SELECT {qry_string} FROM recipes WHERE ri_name ='{ri_id_or_name}';"
        
    elif type(ri_id_or_name).__name__ == 'int':
        print(f"ri_id_or_name is an int [{ri_id_or_name}] - {type(ri_id_or_name).__name__} - {type(ri_id_or_name)}")
        sql_query = f"SELECT {qry_string} FROM recipes WHERE ri_id = {ri_id_or_name};"
    
    else:
        raise(TypeError, f"recipe ID should be a ri_name (str) or ri_id(int) - {ri_id_or_name}")
    
    db_lines = helper_db_class_db.execute(sql_query).fetchall()
    
    # pprint(db_lines) # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
        
    for line in db_lines:
        rcp = {}        
        for index, content in enumerate(line):
            #print( f"\n--->? QRY Line{line}\nT: {type(line)}" )
            #print( f"\nC:{content} - {type(content)}<" )
            
            if content == None: continue            # leave defaults in place
            
            type_string = str(type(content))            
            
            if type_string == "<class 'decimal.Decimal'>":
                # if has a nutrinfo key insert the index into the nutrinfo dict
                if fields[index] in nutrinfo_dict_keys:
                    updated_info['nutrinfo'][fields[index]] = round(float(content),2)
                else:
                    updated_info[fields[index]] = round(float(content),2)
    
            else:
                # if has a nutrinfo key insert the index into the nutrinfo dict
                if fields[index] in nutrinfo_dict_keys:
                    updated_info['nutrinfo'][fields[index]] = content
                else:
                    updated_info[fields[index]] = content
    
    #user_R = int(random() * 5 ) + 1
    #updated_info['user_rating'] = user_R
    
    print(f"----- QUERY: helper_db_class_db: get_single_recipe_from_db_for_display_as_dict ---------E: {updated_info['ri_name']}")
    return updated_info

# scan ingredients for subcomponents - recurse until ALL ATOMIC!
# maybe 2 or 3 deep for all but most in depth recipes
def get_single_recipe_with_subcomponents_from_db_for_display_as_dict(ri_id_or_name, fields=None):
    
    return_recipe = return_recipe_dictionary()
    
    # get base recipe
    return_recipe.update( get_single_recipe_from_db_for_display_as_dict(ri_id_or_name, fields) )
    
    # go through ingredients and load non-atomic (IE subcomponents) into components
    for ingredient in return_recipe['ingredients']:
        
        if int(ingredient[ATOMIC_INDEX]) == 0:
            
            # NON atomic - fetch subcomponent
            sub_component_name = ingredient[INGREDIENT_INDEX]
        
            #return_recipe['components'][sub_component_name] = get_single_recipe_from_db_for_display_as_dict(sub_component_name, fields)
            return_recipe['components'][sub_component_name] = get_single_recipe_with_subcomponents_from_db_for_display_as_dict(sub_component_name, fields)            
     
    return return_recipe    
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# get more than one recipe, for comparison for example
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_recipes_for_display_as_list_of_dicts(list_of_recipe_ids):
    recipe_list = []
    
    for ri_id in list_of_recipe_ids:
        print(f"getting: {ri_id}")
        
        recipe = get_single_recipe_from_db_for_display_as_dict(ri_id)
        
        print(f"got: {recipe['ri_name']}")
        
        recipe_list.append( recipe )

    return recipe_list

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_gallery_info_for_display_as_list_of_dicts(list_of_recipe_ids=[]):
    recipe_list = []
    
    fields = ['ri_id', 'ri_name', 'image_file', 'description', 'user_rating']
    
    for ri_id in list_of_recipe_ids:
        print(f"getting: {ri_id}")
        recipe = get_single_recipe_from_db_for_display_as_dict(ri_id, fields)
        print(f"got: {recipe['ri_name']}")
        recipe_list.append( recipe )

    return recipe_list


def get_ingredients_as_text_list(ri_id):
    
    ingredients = []
    
    return ingredients
    
# get_next_page_recipe_ids()    
def get_all_recipe_ids():
    
    db_lines = helper_db_class_db.execute("SELECT ri_id FROM exploded WHERE image_file <> '';").fetchall()                
    
    ids = [ int( str(line).lstrip('(').rstrip(',)') )  for line in db_lines ]
    
    return ids



def toggle_filter(filter_list, filter_name):
    
    if filter_name in filter_list:
        filter_list.remove(filter_name)
        return
    else:
        filter_list.append(filter_name)
    


class RecipeTracker:    
    def __init__(self, recipe={}):
        self.recipe = return_recipe_dictionary().update(recipe)

    
    



    
if __name__ == '__main__':
    
    # "402, 'tuna with vegetable and tangerine salad'",
    # "1304, 'jalapeno burger w cauliflower california'",
    # "2403, 'prawns w crab cakes mango salsa and salad'",
    test_ids = [1304,2403,402]
    test_id = [1304]
    
    print("-----  attaching to DB ------------------------------------E")

    print("-----  get recipes in display format ------------------------------------S")
    
    #recipes = get_recipes_for_display_as_list_of_dicts( test_ids )
        
    # print("-----  get recipes in display format ------------------------------------E1")
    # 
    # for r in recipes:
    #    print(f"-----  recipe: {r['ri_name']} ------------------------------------S")
    #    pprint(r)
    # 
    # print("-----  get recipes in display format ------------------------------------E2")

    #pprint(get_single_recipe_from_db_for_display_as_dict(test_id[0]))
    #pprint(get_single_recipe_from_db_for_display_as_dict('beef & jalapeno burger'))

    # display recipe dict
    #json_string_from_dict = json.dumps(return_recipe_dictionary(), indent=2, sort_keys=True )
    #print( json_string_from_dict )
    print("-----  get subcomponents in display format ------------------------------------S")
    
    pprint( get_single_recipe_with_subcomponents_from_db_for_display_as_dict(test_id[0]) )
    
    print("\n\n << RECIPE DICT >>\n\n")
    pprint(return_recipe_dictionary())
    
    pprint(RecipeTracker())
    
    