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
import os

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
#engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different
engine = create_engine(os.environ['DATABASE_URL'])      # pick up from environment - work local/heroku
helper_db_class_db = scoped_session(sessionmaker(bind=engine))
print("----- helpers_db: attaching to DB ------------------------------------E")

# stub files for data
from config_files import get_file_for_data_set 

import uuid

class DBHelperError(Exception):
    '''TODO Move this and other error classes to separate file: exceptions.py'''
    pass

class ArgsOutOfBounds(DBHelperError):
    '''Time argument are invalid'''
    pass

class DBAccessKeyError(DBHelperError):
    '''Key not in DB'''
    pass

# time helper function for time since epoch, day, 24hr clock
# https://www.techatbloomberg.com/blog/work-dates-time-python/ < overview timezones
#def nix_time_ms(dt=datetime.now()):  < this assign the time the def statement is execute as the default! # https://effbot.org/zone/default-values.htm
def nix_time_ms(dt=None):
    if dt == None: dt = datetime.now()        
    epoch = datetime.utcfromtimestamp(0)                    #                ms 1572029735987
    print(f"nix_time_ms: {int( (dt - epoch).total_seconds() * 1000.0 )}")
    return int( (dt - epoch).total_seconds() * 1000.0 )     # total_seconds() > 1572029735.987234

def day_from_nix_time(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%a").lower()

def time24h_from_nix_time(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%H%M")

def hr_readable_from_nix(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y %m %d %H%M")

def hr_readable_date_from_nix(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y %m %d")

# Unecessarily complicated refactor!
#
# %Y 2049 year
# %m month
# %d 05 day 0pad
# %H 09 hours 24h 0pad
# %m 05 minutes 0pad
# get rollover 5AM time as nix time
# https://docs.python.org/3.5/library/datetime.html#datetime.datetime.replace
#
# time_in_the_AM_to_rollover 24h 4 digit string 5am = '0500'
def roll_over_from_nix_time(nix_ts, time_in_the_AM_to_rollover='0500'):
    rollover_nix_time_ms = 0

    ONE_DAY_IN_MS = 24*60*60*1000
    HRS_IN_DAY = 24
    MIN_IN_HOUR = 60
    
    if len(time_in_the_AM_to_rollover) == 4:
        h = int(time_in_the_AM_to_rollover[0:2])
        herr = int(h / HRS_IN_DAY)      # check for out of range
        h = h % HRS_IN_DAY
        
        m = int(time_in_the_AM_to_rollover[2:4])
        merr = int(m / MIN_IN_HOUR)     # check for out of range
        m = m % MIN_IN_HOUR
        
        if (herr or merr):
            raise(ArgsOutOfBounds(f"roll_over_from_nix_time - arguments out of range; H{herr}-M{merr} >=1 => ERROR"))
    
    else:       # set to 5am - 0500
        h=5
        m=0

    # convert to datetime to overwrite hrs/mins then back to nixtime
    # ts1_date:0500
    nixtime_opt1 = nix_time_ms( datetime.utcfromtimestamp(nix_ts / 1000.0).replace(hour=h, minute=m) ) 

    # debug
    nix_ts_hr = hr_readable_from_nix(nix_ts)
    
    if nixtime_opt1 > nix_ts:
        rollover_nix_time_ms = nixtime_opt1
        #print(f"<{nix_ts}|{nix_ts_hr}> - {nix_ts} - <{rollover_nix_time_ms}|{hr_readable_from_nix(rollover_nix_time_ms)}> -  {time_in_the_AM_to_rollover} - {h}:{m} - ERR:{herr} or {merr} = {herr or merr}")
    else:        
        nix_ts_plus_1_day = nix_ts + ONE_DAY_IN_MS   # this takes care of rollover, last day of month / year etc        
                                                            # set hours minute to the rollover time >--------\
        dt_rollover = datetime.utcfromtimestamp(nix_ts_plus_1_day / 1000.0).replace(hour=h, minute=m)  # <---/  
    
        rollover_nix_time_ms = nix_time_ms(dt_rollover)
        #print(f"<{nix_ts}|{nix_ts_hr}> - {nix_ts_plus_1_day} - <{rollover_nix_time_ms}|{dt_rollover}> -  {time_in_the_AM_to_rollover} - {h}:{m} - ERR:{herr} or {merr} = {herr or merr}")    
    
    return rollover_nix_time_ms

# What are we trying to do with this function?
# Create a rollover timestamp (R) for a passed in timestamp
# Compare a posted timestamp to the users daily tracker timestamp.
# if the posted timestamp has gone past the roll over
# R the rollover point R is, for example 5AM
#
# ts1        *                            < initial ts
# ts2                           *         < not rolled over yet
# ts3                                 *   < rolled over
#     ----R-------------------|----R-------------------|----R-------------------| < timeline
#     |         day 1         |         day 2          |
#         |         set 1          |         set 2          |
#
# if    ts1_date:0500 > ts1     roll over = ts1_date:0500
# else                          roll over = (ts1_date +1day):0500




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
        'dt_date_readable': hr_readable_date_from_nix(nix_time_in_ms),
        'dt_day': day_from_nix_time(nix_time_in_ms),
        'dt_time': time24h_from_nix_time(nix_time_in_ms),
        'dt_rollover': roll_over_from_nix_time(nix_time_in_ms),
        'dt_last_update': 0,

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
#                     list of ID's for SEARCH - - - - \
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

# EG search
# SELECT ri_name, ri_id, tags FROM exploded WHERE 'vegan'= ANY(tags);       # recipe w/ tag 'vegan'
# inc ANY
# SELECT ri_id  FROM exploded WHERE 'gluten_free' = ANY( tags ) OR 'vegan' = ANY( tags );
# inc ALL
# SELECT ri_id  FROM exploded WHERE 'gluten_free' = ANY( tags ) AND 'vegan' = ANY( tags );

# All veggie recipes that are GF
# SELECT ri_id  FROM exploded WHERE 'gluten_free' = ANY( tags ) AND ('vegan' =  ANY( tags ) OR 'veggie' =  ANY( tags ));


# composition of a basic search

# filter out any allergens:
# SELECT ri_id,user_rating,ri_name, allergens FROM exploded WHERE NOT ('peanuts' = ANY(allergens) OR 'dairy' = ANY(allergens) OR 'gluten' = ANY(allergens) OR 'celery' = ANY(allergens));
    # 
    # SELECT ri_id,user_rating,ri_name, allergens - - - - - - - - - - - - - - - - - - - -\ 
    # FROM exploded                                                                      |
    # WHERE NOT (                                                                        |
    # 'peanuts' = ANY(allergens) OR 			# allergen settings                      |
    # 'dairy' = ANY(allergens) OR                                                        |
    # 'gluten' = ANY(allergens) OR                                                       |
    # 'celery' = ANY(allergens)                                                          |
    # );                                                                                 |
#                                                                                        |
#                                                                                    (- \/ - - )
# SELECT ri_id,ri_name,igd FROM  (SELECT ri_id,ri_name, unnest(ingredients) igd FROM exploded) x WHERE igd LIKE '%beans%';
# Look for ingredient
# 
#         bubble_columns = 'ri_id,user_rating,ri_name,tags,allergens,ingredients'
#        | - - - - - - - - |
# SELECT ri_id,ri_name,igd, tags FROM (
#     SELECT ri_id,ri_name,tags, unnest(ingredients) igd FROM (
#         SELECT ri_id,user_rating,ri_name,tags,allergens,ingredients FROM exploded WHERE NOT ('gluten' = ANY(allergens) OR 'celery' = ANY(allergens))
#     ) allergens_filtered
# ) ingredients_unnested
# WHERE igd LIKE '%beans%';
# 
# SELECT ri_id,ri_name,igd,tags FROM ( SELECT ri_id,ri_name,tags, unnest(ingredients) igd FROM ( SELECT ri_id,user_rating,ri_name,tags,allergens,ingredients FROM exploded WHERE NOT ('gluten' = ANY(allergens) OR 'celery' = ANY(allergens)) ) allergens_filtered ) ingredients_unnested WHERE igd LIKE '%beans%';
# 

filter_to_column_LUT = {'allergens': 'allergens',
                        'ingredient_exc': 'ingredients',
                        'tags_exc': 'tags',
                        'tags_inc': 'tags',
                        'type_exc': 'user_tags', # SB type
                        'type_inc': 'user_tags'}
                                                       
                                                       
# process allergens, tags_exc
# EG
#   SELECT ri_id,user_rating,ri_name,tags,allergens,ingredients FROM exploded WHERE NOT ('gluten' = ANY(allergens) OR 'celery' = ANY(allergens))
def construct_sql_query_to_exclude_tags(tag_list, bubble_columns, db_name_or_subquery, table_name_from_filter):
    
    column = filter_to_column_LUT[table_name_from_filter]
    
    sql_query = f"( SELECT {bubble_columns} FROM {db_name_or_subquery} WHERE NOT (-*insert*-) ) {table_name_from_filter}"
                                                                 # REFACTOR   ^  INTO ONE FUNCTION # TODO
    insert = ""                                                                                  #
    for tag in tag_list:                                                                         #
        print(tag)                                                                               #
        if insert != "": insert += " OR "                                                        #
        insert += f"'{tag}' = ANY({column})"                                                     #
                                                                                                 #
    sql_query = sql_query.replace('-*insert*-', insert)                                          #
                                                                                                 #
    return sql_query                                                                             #
                                                                                                 #
                                                                                                 #
#                                                                                                #
def construct_sql_query_to_include_tags(tag_list, bubble_columns, db_name_or_subquery, table_name_from_filter):
    
    column = filter_to_column_LUT[table_name_from_filter]
    
    sql_query = f"( SELECT {bubble_columns} FROM {db_name_or_subquery} WHERE (-*insert*-) ) {table_name_from_filter}"
    
    insert = ""
    for tag in tag_list:
        print(tag)
        if insert != "": insert += " OR "
        insert += f"'{tag}' = ANY({column})"
    
    sql_query = sql_query.replace('-*insert*-', insert)
    
    return sql_query


# default_filters:
# {'allergens': [],
#  'ingredient_exc': [],
#  'tags_exc': [],
#  'tags_inc': [],
#  'type_exc': [],
#  'type_inc': []}
# SELECT ri_id,ri_name,igd, tags FROM (              
#     SELECT ri_id,ri_name,tags, unnest(ingredients) igd FROM (
#         SELECT ri_id,user_rating,ri_name,tags,allergens,ingredients FROM exploded WHERE NOT ('gluten' = ANY(allergens) OR 'celery' = ANY(allergens))
#     ) allergens_filtered
# ) ingredients_unnested
# WHERE igd LIKE '%beans%';
def build_search_query(search, default_filters):
    
    search_words = [ word.strip() for word in search.split(',') ]
    
    bubble_columns = 'ri_id,user_rating,ri_name,tags,allergens,ingredients'
    
    filter_sub_queries = 'exploded'
    
    if len(default_filters['allergens']) > 0:    
        filter_sub_queries = construct_sql_query_to_exclude_tags(default_filters['allergens'], bubble_columns, filter_sub_queries, 'allergens')
        print("filter_sub_queries:", filter_sub_queries)
    
    if len(default_filters['tags_exc']) > 0:
        filter_sub_queries = construct_sql_query_to_exclude_tags(default_filters['tags_exc'], bubble_columns, filter_sub_queries, 'tags_exc')
        print("filter_sub_queries:", filter_sub_queries)
    
    if len(default_filters['tags_inc']) > 0:      #\\//#
        filter_sub_queries = construct_sql_query_to_include_tags(default_filters['tags_inc'], bubble_columns, filter_sub_queries, 'tags_inc')
                                                  #//\\#
        print("filter_sub_queries:", filter_sub_queries)
        
    #search_query = f"SELECT ri_id FROM ( SELECT ri_id,ri_name,tags, unnest(ingredients) igd FROM {filter_sub_queries} ) all_filters WHERE -*insert*-;"
    # returns duplicates! ^^
    search_query = f"SELECT DISTINCT ri_id FROM ( SELECT ri_id, igd FROM ( SELECT ri_id,ri_name,tags, unnest(ingredients) igd FROM {filter_sub_queries} ) all_filters ) distict_ids WHERE -*insert*-;"
    # added DISTINCT to remove duplicates    
    # SELECT DISTINCT ri_id FROM ( SELECT ri_id, igd FROM ( SELECT ri_id,ri_name,tags, unnest(ingredients) igd FROM ( SELECT ri_id,user_rating,ri_name,tags,allergens,ingredients FROM exploded WHERE ('vegan' = ANY(tags)) ) tags_inc ) all_filters) distict_ids WHERE (igd LIKE '%');

    insert = ""
    for ingredient in search_words:
        if insert != "": insert += " OR "
        insert += f"(igd LIKE '%{ingredient}%')"
        
    search_query = search_query.replace('-*insert*-', insert)
    
    print("\n\n- - - - - Constructing Query - - - - S")
    pprint(default_filters)
    pprint(search_words)
    print(insert)
    print(search_query)
    print("\n\n- - - - - Constructing Query - - E")        
    
    return search_query
    
  
    

# {'UUID': '014752da-b49d-4fb0-9f50-23bc90e44298',
#  'default_filters': {'allergens': [],
#                      'ingredient_exc': [],
#                      'tags_exc': [],
#                      'tags_inc': ['chicken', 'pork']},
def process_search(search, default_filters):
    # # SELECT ri_id,ri_name, igd FROM  (SELECT ri_id,ri_name, unnest(ingredients) igd FROM exploded) x WHERE igd LIKE '%red onion%';
    #  ri_id |                   ri_name                    |    igd     
    # -------+----------------------------------------------+------------
    #      1 | mixed vegetable risotto                      | red onion
    #      3 | crispy prawn and vegetable risotto           | red onion
    #    503 | beetroot and chicken broth                   | red onion
    #    504 | chicken beetroot w broccoli and greens       | red onion
    #    801 | chicken and shredded lettuce soup w cardamom | red onion
    #   1001 | fillet steak and vegetables in gravy         | red onion
    #   1302 | beef & jalapeno burger                       | red onion
    #   1304 | jalapeno burger w cauliflower california     | red onion
    #   1601 | winner winner chicken dinner                 | red onion
    #   1901 | chicken and aubergine stew                   | red onions
    #   2301 | savoury pear grape and squash salad          | red onion
    #   2401 | mango salsa                                  | red onion
    #   2402 | savoury pear grape and squash salad          | red onion
    #   2403 | prawns w crab cakes mango salsa and salad    | red onion
    #   3101 | goats cheese and spinach omelette            | red onion
    #   3201 | light apricot cous cous                      | red onion
    #   3202 | ham green beans and cous cous w egg          | red onion
    #   3301 | light apricot cous cous                      | red onion
    # (18 rows)
    
    # split search by commas
    # build basic query from search
    # add the default filters
    #    handle empty filter arrays
    query = build_search_query(search, default_filters)
    
    db_lines = helper_db_class_db.execute(query).fetchall()                    
    
    pprint(db_lines)
    
    # results are string change to ints    
    #ids = [ int(number) for number in ids ] # TypeError: int() argument must be a string, a bytes-like object or a number, not 'RowProxy'
    ids = [ int( str(line).lstrip('(').rstrip(',)') )  for line in db_lines ]
    
    return ids





def toggle_filter(filter_list, filter_name):
    
    if filter_name in filter_list:
        filter_list.remove(filter_name)
        return
    else:
        filter_list.append(filter_name)
    

# TODO - Implement - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class RecipeTracker:    
    def __init__(self, recipe={}):
        self.recipe = return_recipe_dictionary().update(recipe)




# TODO - implement DB DTK LOAD/STORE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# for now - load data from JSON files - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 



def create_daily_tracker_name_from_nix_time(nix_time_ms = nix_time_ms()):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y calories month %m %a %d").lower()

def bootstrap_daily_tracker_create(uuid):
    dtk = { 'dtk_user_info': get_user_info_name_uuid_dict(uuid),
            'dtk_rcp':    return_recipe_dictionary(),
            'dtk_weight': 0.0,
            'dtk_pc_fat': 0.0,
            'dtk_pc_h2o': 0.0  }
    
    dtk['dtk_rcp']['ri_name'] = create_daily_tracker_name_from_nix_time()
    
    return dtk


def commit_dict_to_DB(db, data_set):
    '''
    commit data for key data_set - if no file - create it
    -
    set of user data
    set of dtk data for each use
    data_set key must be in .json config_file (config.py) 
    '''
    database_file = get_file_for_data_set(data_set)
    
    with open(database_file, 'w') as f:
        #pprint(db)
        db_as_json = json.dumps(db)
        f.write(db_as_json)
    
    # if database_file.exists():
    #     with open(database_file, 'w') as f:
    #         f.write(db)
    # else:
    #     with open(database_file, 'w') as f:
    #         f.write(db)
        
    

def load_dict_data_from_DB(data_set):
    '''
    load data for key: data_set - if no file - create it
    -
    set of user data
    set of dtk data for each use
    data_set key must be in .json config_file (config.py) 
    '''    
    database_file = get_file_for_data_set(data_set)
            
    if database_file.exists():
        with open(database_file, 'r') as f:
            json_db = f.read()
            db = json.loads(json_db)
            print(f"DTK database LOADED [{data_set}] ({db.__len__()})")
    else:
        db = {}  # create a blank file          
        commit_dict_to_DB(db, data_set)
            
    return db


# private
users_devices_db = load_dict_data_from_DB('user_device_database')
# private
daily_tracker_db = load_dict_data_from_DB('dtk_database')
# private
user_db = load_dict_data_from_DB('user_database')
# user_db = { '014752da-b49d-4fb0-9f50-23bc90e44298': {'UUID': '014752da-b49d-4fb0-9f50-23bc90e44298',
#                                                      'name': 'Simon'},
#             '8e4475a5-218d-4153-8103-000764cf5ef6': {'UUID': '8e4475a5-218d-4153-8103-000764cf5ef6',
#                                                      'name': 'Susan'} }            
# commit_dict_to_DB(user_db, 'user_database')


def commit_DTK_DB():
    commit_dict_to_DB(daily_tracker_db, 'dtk_database')

def commit_User_DB():
    commit_dict_to_DB(user_db, 'user_database')

def commit_User_Devices_DB():
    commit_dict_to_DB(users_devices_db, 'user_device_database')



def get_daily_tracker(userUUID):
    try:
        return daily_tracker_db[userUUID]
    except KeyError:        
        return None
    
    
def store_daily_tracker(dtk):
    try:
        dtk['dtk_rcp']['dt_last_update'] = nix_time_ms()
        daily_tracker_db[str(dtk['dtk_user_info']['UUID'])] = dtk
        commit_DTK_DB()
        #pprint(dtk)
        return True
    except KeyError:
        print("** W A R N I N G ** Failed to Store DTK data:")
        pprint(dtk)
        raise("Failed to Store DTK data:")


def get_user_devices(userUUID):
    try:
        return users_devices_db[userUUID]
    except KeyError:        
        return None
    
    
def store_user_devices(userUUID, devFP):
    if userUUID not in users_devices_db:
        print(f"store_user_devices===---> Adding: {devFP['fp']}")
        users_devices_db[userUUID] = {devFP['fp']: devFP}
        pprint(users_devices_db[userUUID])
        
        
    elif devFP['fp'] not in users_devices_db[userUUID]:
        print(f"store_user_devices===---> Appending: {devFP['fp']}")
        pprint(users_devices_db[userUUID])
        users_devices_db[userUUID][devFP['fp']] = devFP
        

def get_search_settings_dict(empty=False):
    # default_filters = {'allergens': [],   # exclude ALL
    #              'tags_inc': [],          # include at least ONE - think about OR vs AND
    #              'tags_exc': [],          # exclude ALL
    #              'type_inc': [],          # include at least ONE - think about OR vs AND
    #              'type_exc': [],          # exclude ALL
    #              'ingredient_exc': [] }   # exclude ALL

    default_filters = {
        'allergens': ['dairy', 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'molluscs', 'shellfish', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide'],
        'tags_inc': ['vegan', 'veggie', 'cbs', 'chicken', 'pork', 'beef', 'seafood', 'shellfish', 'gluten_free', 'ns_pregnant'],
        'tags_exc': ['vegan', 'veggie', 'cbs', 'chicken', 'pork', 'beef', 'seafood', 'shellfish', 'gluten_free', 'ns_pregnant'],
        'type_inc': ['component', 'amuse', 'side', 'starter', 'fish', 'lightcourse', 'main', 'crepe', 'dessert', 'p4', 'cheese', 'comfort', 'low_cal', 'serve_cold', 'serve_rt', 'serve_warm', 'serve_hot'],
        'type_exc': [],
        'ingredient_exc': [] }
    
    if empty == True:
        for filter_list in default_filters:
            default_filters[filter_list] = []

    # example user settings
    # default_filters = {'allergens': ['eggs', 'seeds_mustard', 'gluten'],     # exclude ALL
    #              'tags_inc': ['vegan', 'veggie', 'cbs'],                    # include at least ONE
    #              'tags_exc': ['ns_pregnant'],                               # exclude ALL
    #              'ingredient_exc': ['celery']                               # exclude ALL
    #              }
    
    return default_filters


def create_user(uuid='014752da-b49d-4fb0-9f50-23bc90e44298', user_settings={}):
    # Tables for get_user: user_devices, devices, default_filters, tag_sets, usernames, dtk
    # https://docs.python.org/3/library/uuid.html
    # maybe use domain version, have a think
    default_user_settings = {
        'UUID': '014752da-b49d-4fb0-9f50-23bc90e44298',  #uuid #str(uuid.uuid4()), # TODO comment back in and look up from unique name
        'name': 'Simon',
        'devices': ['dev1_fp_hash', 'dev2_fp_hash', 'dev3_fp_hash'],
        'default_filters': get_search_settings_dict(True),
        'tag_sets': get_search_settings_dict(True),
        }
    
    default_user_settings.update(user_settings)
    
    # TODO - update devices DB
        
    user_db[uuid] = default_user_settings

    #pprint(user_db[uuid])
    
    try:
        commit_User_DB()
        return user_db[uuid]
    
    except e:
        raise('What could possibly go wrong!?', e)

# DATABASE_URL
def get_user_info_dict_from_DB(uuid):
    request_tables = ['default_filters','tag_sets']#,'usernames']
    # get_filter_colums(from_central_source)
    filter_cols = ['allergens','ingredient_exc','tags_exc','tags_inc','type_exc','type_inc']
    
    username = helper_db_class_db.execute("SELECT username FROM usernames WHERE uuid_user='{uuid}';").fetchone()
    if username == None: username = 'Aardvark' # Place holder until logins implemented
    
    
    return_user_info = {'UUID':uuid, 'name':username}
    
    print(f"RETRIEVING FROM DB - {uuid} ( -o- )")
    

    tag_sets_and_filters = {}
    
    for table in request_tables:
        tag_sets_and_filters[table] = {}
        # SELECT * FROM default_filters WHERE uuid_user='014752da-b49d-4fb0-9f50-23bc90e44298';    
        sql_query = f"SELECT * FROM {table} WHERE uuid_user='{uuid}';"
        print(f"\nTABLE {table} - SQL: {sql_query} < - - - - - < <")
        
        #db_lines = helper_db_class_db.execute(sql_query).fetchall()  - returns list of RowProxy
        #pprint(db_lines[0]['allergens'])
        
        tagdata_for_table = helper_db_class_db.execute(sql_query).fetchone() # - returns RowProxy
        
        for col in filter_cols:
            tag_sets_and_filters[table][col] = tagdata_for_table[col]                
        
    return_user_info.update(tag_sets_and_filters)
    
    #pprint(return_user_info)
    
    print(f"RETRIEVING FROM DB - {uuid} ( -o- )")    
    return return_user_info


def get_user_info_dict(uuid):
    try:
        return user_db[uuid]
    except KeyError as e:
        raise(DBAccessKeyError("get_user_info_dict ERROR", e))
        return None


def get_user_info_name_uuid_dict(uuid):
    u_info = get_user_info_dict_from_DB(uuid)

    try:
        return { 'UUID': u_info['UUID'],'name':u_info['name'] }
    
    except KeyError as e:
        raise(DBAccessKeyError("get_user_info_name_uuid_dict ERROR", e))
        return None

  
# Go through list of tables to update
# pick each out of settings passed in (if present)
# create SQL update command
#       UPDATE tag_sets SET ingredient_exc = '{"turkey", "caramelised apple", "knockwurst"}', tags_inc = '{"1","2"}' WHERE uuid_user = '014752da-b49d-4fb0-9f50-23bc90e44298';
# Update relevant table
#
# Typical entry (one of table list):
#
# 'default_filters': { 'allergens': [],
#         ^            'ingredient_exc': ['coriander', 'bad sausage'],
#         ^            'tags_exc': ['ns_pregnant'],
#         ^            'tags_inc': [] },    ^
#         ^              ^                  ^
#         ^              ^                  ^
#         ^           column_name       rows_data
#      table_key > dict of arrays
#
# DATABASE_URL
def update_settings_tables_for_uuid(db, user_settings):
    pprint(user_settings)
    
    uuid = user_settings['UUID']
    
    #table_list = ['allergens','ingredient_exc','tags_exc','tags_inc','type_exc','type_inc']
    table_list = ['default_filters','tag_sets']
    
    for table_key in iter(user_settings):
        #print(f"- - - - - - - - - - - - - - - - - - - - - - - - table_key:{table_key}")
        if table_key not in table_list: continue
            
        settings = user_settings[table_key]
    
        column_update = ""
        for column_name in settings:
            if column_update != "": column_update += ','            # comma between sets                                                        
                                                            # create list of array entries
            row = ','.join([ f'"{entry}"' for entry in settings[column_name] ])                                                           
                                                            # col     array1              col          array2
            column_update += f"{column_name} = '{{{row}}}'"     # tags = '{"item1","item2"}', allergens = '{"item1","item2"}'             
        
        # assemble into sql command
        # UPDATE tag_sets SET
        #                   ingredient_exc = '{"turkey", "caramelised apple", "knockwurst"}',
        #                   tags_inc = '{"vegan","veggie"}'
        #                 WHERE uuid_user = '014752da-b49d-4fb0-9f50-23bc90e44298';    
        sql_command = f"UPDATE {table_key} SET {column_update} WHERE uuid_user = '{uuid}';"
        
        #print(f"TK:{table_key}\nROW:{column_update}\nSQL:{sql_command}")        
        db.execute(sql_command)
        print(f"***** SQL WRITE:\n{sql_command}\n\nRESULT: {db.commit()} <\n\n") # < < COMMIT 
        # TODO - commit return None on success?
        # how is failure report?
        


    

# EG DB write
# UPDATE tag_sets SET ingredient_exc = '{"turkey", "caramelised apple", "knockwurst"}' WHERE uuid_user = '014752da-b49d-4fb0-9f50-23bc90e44298';
# UPDATE default_filters
# UPDATE tag_sets
def update_user_info_dict(user_settings):
    uuid = user_settings['UUID']
    
    try:
        # local filesystem
        user_db[uuid].update(user_settings)
        commit_User_DB()
        
        # db defined in DATABASE_URL
        update_settings_tables_for_uuid(helper_db_class_db, user_settings)
        return True
    
    except KeyError as e:
        raise(DBAccessKeyError("get_user_info_name_uuid_dict ERROR", e))
        return None
    

    

# TODO - implement DB DTK LOAD/STORE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# for now - load data from JSON files - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 













    
if __name__ == '__main__':
    
    # "402, 'tuna with vegetable and tangerine salad'",
    # "1304, 'jalapeno burger w cauliflower california'",
    # "2403, 'prawns w crab cakes mango salsa and salad'",
    test_ids = [1304,2403,402]
    test_id = [1304]
    pprint(user_db)
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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #--
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior    #
    day = datetime.now().strftime("%d") # day number                                    #
    day = datetime.now().strftime("%a").lower() # day 3 letter                          #
    time = datetime.now().strftime("%H%M").lower() # 4 digit 24hr clock                 #
    #time_since_epoch = nix_time_ms(datetime.now())                                     #
    time_since_epoch = nix_time_ms()                                                    #
    day_from_nx = day_from_nix_time(time_since_epoch)                                   #
    time24_from_nx = time24h_from_nix_time(time_since_epoch)                            #
                                                                                        #
    print(day, time, time_since_epoch, day_from_nx)                                     #
    print(type(datetime.now()))                                                         #
    print(create_daily_tracker_name_from_nix_time(nix_time_ms()))                       #
    
    # rollover time 5AM tomorrow
    print(datetime.strptime('0500',"%H%M"))
    nix_ts = nix_time_ms()
    # %Y 2049 year
    # %m month
    # %d 05 day 0pad
    # %H 09 hours 24h 0pad
    # %m 05 minutes 0pad
    # get rollover 5AM time as nix time
    time_in_the_AM_to_rollover='0500'
    h = int(time_in_the_AM_to_rollover[0:2])
    m = int(time_in_the_AM_to_rollover[2:4])
    ONE_DAY_IN_MS = 24*60*60*1000
    hrs=5
    mins=0
    nix_ts_plus_1_day = nix_ts + ONE_DAY_IN_MS
    rollover_time = '0500'
    print(datetime.utcfromtimestamp(nix_ts / 1000.0).strftime("%Y %m %d %H%M"))
    print(datetime.utcfromtimestamp(nix_ts_plus_1_day / 1000.0).strftime(f"%Y %m %d {rollover_time}"))    
    print(datetime.utcfromtimestamp(nix_ts_plus_1_day / 1000.0).replace(hour=5, minute=0).strftime(f"%Y %m %d %H%M"))
    print(datetime.utcfromtimestamp(nix_ts_plus_1_day / 1000.0).replace(hour=hrs, minute=mins).strftime(f"%Y %m %d %H%M"))
    print(datetime.utcfromtimestamp(nix_ts_plus_1_day / 1000.0).replace(hour=h, minute=m).strftime(f"%Y %m %d %H%M"))
    # https://docs.python.org/3.5/library/datetime.html#datetime.datetime.replace
    dt_rollover = datetime.utcfromtimestamp(nix_ts_plus_1_day / 1000.0).replace(hour=hrs, minute=mins)    
    rollover_nix_time_ms = nix_time_ms(dt_rollover)
    print(datetime.strptime('2000 0458',"%Y %H%M"))
    print( hr_readable_from_nix( roll_over_from_nix_time( nix_time_ms(datetime.strptime('2000 0458',"%Y %H%M")), '0500') ) )
    print( hr_readable_from_nix( roll_over_from_nix_time( nix_time_ms(datetime.strptime('2000 0459',"%Y %H%M")), '0500') ) )
    print( hr_readable_from_nix( roll_over_from_nix_time( nix_time_ms(datetime.strptime('2000 0500',"%Y %H%M")), '0500') ) )
    print( hr_readable_from_nix( roll_over_from_nix_time( nix_time_ms(datetime.strptime('2000 0501',"%Y %H%M")), '0500') ) )
    #print( hr_readable_from_nix( roll_over_from_nix_time( nix_time_ms(datetime.strptime('2000 0501',"%Y %H%M")), '0599') ) ) # out of bounds 
    #print( hr_readable_from_nix( roll_over_from_nix_time( nix_time_ms(datetime.strptime('2000 0501',"%Y %H%M")), '2615') ) ) # out of bounds 
    # for i in range(1,240):
    #     print(f"{i % 24}\t{i % 12}\t{i % 60}")
    # 
    # print(int(23 / 24))
    # print(int(12 / 24))
    # print(int(24 / 24))
    # print("-")
    # print(0 or 1)
    # print(0 or 0)
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #--
    
    # search  notes
    # get_daily_tracker_from_DB - hello.py
    # print("- - - USER / UUID - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    # user = 'Simon'
    # user_info = get_user_info_name_uuid_dict(user)
    # user_db[user_info['UUID']] = user_info['name']
    # user_info = get_user_info_name_uuid_dict('Susan')
    # user_db[user_info['UUID']] = user_info['name']    
    # pprint(user_db)
    # print("- - - boot DTK - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")    
    # test_dtk = bootstrap_daily_tracker_create(user)
    # test_dtk['dtk_user_info']['UUID'] = '014752da-b49d-4fb0-9f50-23bc90e44298'
    # test_dtk['dtk_user_info']['name'] = 'Simon'
    # pprint(test_dtk)
    # print("- - - WRITE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    # store_daily_tracker(test_dtk)
    # print("- - - READ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    # test_dtk_read = get_daily_tracker(test_dtk['dtk_user_info']['UUID'])    
    # pprint(test_dtk_read)
    # print("- - - COMMIT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    # commit_DTK_DB()
    # commit_User_DB()
    print("\n\n\n\n\n- - - - - - - - - - - - - - - - - - - - - - - User DB < < \n")
    pprint(user_db)
    
    pprint(bootstrap_daily_tracker_create('014752da-b49d-4fb0-9f50-23bc90e44298'))
    
    print("\n\n\n\n\nUser Device Fingerprints\n")
    pprint(users_devices_db)
    
    # allergens: dairy, eggs, peanuts, nuts, seeds_lupin, seeds_sesame, seeds_mustard, fish, molluscs, shellfish, alcohol, celery, gluten, soya, sulphur_dioxide
    # tags: vegan, veggie, cbs, chicken, pork, beef, seafood, shellfish, gluten_free, ns_pregnant, 
    default_filters = { 'allergens': [],
                        'ingredient_exc': [],
                        'tags_exc': [],
                        'tags_inc': ['chicken',
                                     'pork','s&c']}
        
    user_data_db = load_dict_data_from_DB("user_database")
    pprint(user_data_db)
    print("CREATE USER. . .")
    pprint(create_user('8e4475a5-218d-4153-8103-000764cf5555', {'name':'Candice'}))    
    print("ACCESS GRANTED?")
    pprint(get_user_info_name_uuid_dict('014752da-b49d-4fb0-9f50-23bc90e44298'))               

 #    pprint(get_user_info_name_uuid_dict('8e4475a5-218d-4153-8103-000764cf5ef6'))
 #    #pprint(get_user_info_name_uuid_dict('8e4475a5-218d-4153-8103-000764cf5555'))
 #    
 #    pprint(get_search_settings_dict())
 #    pprint(get_search_settings_dict(True))
 #    
 #    bubble_columns = 'ri_id,user_rating,ri_name,tags,allergens,ingredients'
 #    print("\n\nConstructing Query")
 #          #construct_sql_query_to_exclude_tags(tag_list,                 bubble_columns,  db_name,    table_name_from_filter):
 #    print( construct_sql_query_to_exclude_tags(['vegan','veggie','cbs'], bubble_columns, 'exploded', 'tags_exc') )
 #        
 #    print( construct_sql_query_to_include_tags(['vegan','veggie','cbs'], bubble_columns, 'exploded', 'tags_inc') )
 #    
 #    print(build_search_query(' prawn , crab , mango ', default_filters))
 #    
 #    print("\n\nSinge UPDATE Command < - - - <<")
 #    test_default_filters = { 'default_filters': {'allergens': ['greedy twats', 'fake people'],
 #                             'ingredient_exc': ['coriander'],
 #                             'tags_exc': [],
 #                             'tags_inc': ['ns_pregnant']} }
 #    
 #    update_settings_table_for_uuid('theDB', '014752da-b49d-4fb0-9f50-23bc90e44298', test_default_filters)
 #    
 #    print("\n\nMulti UPDATE Command < - - - <<")
 #    user_settings = {'UUID': '014752da-b49d-4fb0-9f50-23bc90e44297',
 # 'default_filters': {'allergens': ['dairy'],
 #                     'ingredient_exc': ['coriander'],
 #                     'tags_exc': ['ns_pregnant'],
 #                     'tags_inc': ['gluten_free']},   # difficult customer
 # 'name': 'Simon',
 # 'tag_sets': {'allergens': ['dairy',
 #                            'sulphur_dioxide'],
 #              'ingredient_exc': ['coriander'],
 #              'tags_exc': ['vegan',
 #                           'ns_pregnant'],
 #              'tags_inc': ['vegan',
 #                           'ns_pregnant'],
 #              'type_exc': [],
 #              'type_inc': ['component',
 #                           'serve_hot']}}
 #    
 #    update_settings_tables_for_uuid(helper_db_class_db, user_settings)
 #    
    pprint(get_user_info_dict('014752da-b49d-4fb0-9f50-23bc90e44298'))
        
    pprint( get_user_info_dict_from_DB('014752da-b49d-4fb0-9f50-23bc90e44298') )
    
               