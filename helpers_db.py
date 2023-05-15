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

from timestamping import nix_time_ms, day_from_nix_time, time24h_from_nix_time, hr_readable_from_nix
from timestamping import hr_readable_date_from_nix, roll_over_from_nix_time

# for gallery stars before actual data
from random import random

import json                 # converting to json string from dict
                            # converting to dict to json string

from pprint import pprint # giza a look

print("----- helpers_db: attaching to DB ------------------------------------S")
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
#engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different
#engine = create_engine(os.environ['DATABASE_URL'])      # pick up from environment - work local/heroku
engine = create_engine('postgresql://simon:loop@localhost:5432/cs50_recipes')
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

class DBWriteError(DBHelperError):
    '''Key not in DB'''
    pass

from food_sets import IGD_TYPE_DERIVED

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
def add_ingredient_w_timestamp(recipe, igdt_type, qty, ingredient, servings=0):

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

    if igdt_type < 0:
        # look ingredient up in DB and see if we have a recipe (0)
        # or if it's off the shelf (1)
        # TODO ATOMIC
        igdt_type = -1 # not checked

    if len(ingredient) == 0:
        ingredient = "ingredient was blank!"

    ingredient_list = [str(igdt_type), qty, f"({servings})", ingredient, timestamp]

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
#{'ingredients': [[0, '250g', '(0)', 'cauliflower', nix_time_in_ms],    # sublist
#                 [0, '125g', '(0)', 'grapes', nix_time_in_ms],
#                 [0, '200g', '(4)', 'tangerines', nix_time_in_ms],
#                 [0, '55g', '(0)', 'dates', nix_time_in_ms],
#   atomic >-------0, '8g', '(0)', 'coriander', nix_time_in_ms],
#                 [0, '8g', '(0)', 'mint', nix_time_in_ms],
#                 [0, '4g', '(0)', 'chillies', nix_time_in_ms],
#   sub_comp >-----1, '45g', '(0)', 'pear and vanilla reduction lite', nix_time_in_ms],
#                 [0, '2g', '(0)', 'salt', nix_time_in_ms],
#                 [0, '2g', '(0)', 'black pepper', nix_time_in_ms],
#                 [0, '30g', '(0)', 'flaked almonds', nix_time_in_ms]],
#  'ri_name': 'cauliflower california',
#  'atomic' : 0     ** deprecated BOOL use igdt_type INT8 instead
#  'igdt_type' : -1 to 3  see below
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# //  IGDT_TYPE: UNCHECKED / ATOMIC / DERIVED / OTS / DTK
# //                 -1         0        1       2     3
# let IGD_TYPE_UNCHECKED = -1;
# let IGD_TYPE_ATOMIC    = 0;
# let IGD_TYPE_DERIVED   = 1;
# let IGD_TYPE_OTS       = 2;   // Off The Shelf
# let IGD_TYPE_DTK       = 3;   // Daily TracKer 
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
#  ingredients  | character varying(150)[] |           |          |
#  allergens    | character varying(150)[] |           |          |
#  tags         | character varying(150)[] |           |          |
#  user_tags    | character varying(150)[] |           |          |
#  lead_image   | character varying(100)   |           |          | NULL::character varying
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
# ['id','ri_id','ri_name','yield','units','servings','density','serving_size','igdt_type','ingredients','allergens','tags',
# 'user_tags','lead_image','text_file','n_en','n_fa','n_fs','n_fm','n_fp','n_fo3','n_ca','n_su','n_fb','n_st','n_pr','n_sa','n_al',]
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
        'lead_image':'none_listed',
        'text_file':'none_listed',
        'description': 'add a description . . .',
        'igdt_type': -1,
        'user_rating': 1,
        'dt_date': nix_time_in_ms,
        'dt_date_readable': hr_readable_date_from_nix(nix_time_in_ms),
        'dt_day': day_from_nix_time(nix_time_in_ms),
        'dt_time': time24h_from_nix_time(nix_time_in_ms),
        'dt_rollover': roll_over_from_nix_time(nix_time_in_ms),
        'dt_last_update': 0,
        'username':'carter',

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
        fields = ['id','ri_id','ri_name','description','method','notes','yield','units','servings','density','serving_size',
                  'igdt_type','ingredients','allergens','type','tags','user_tags','lead_image','text_file',
                  'n_En','n_Fa','n_Fs','n_Fm','n_Fp','n_Fo3','n_Ca','n_Su','n_Fb','n_St','n_Pr','n_Sa','n_Al']

    qry_string = ', '.join(fields)

    if type(ri_id_or_name).__name__ == 'str':
        print(f"ri_id_or_name is a string [{ri_id_or_name}] - {type(ri_id_or_name).__name__} - {type(ri_id_or_name)}")
        sql_query = f"SELECT {qry_string} FROM recipes WHERE ri_name ='{ri_id_or_name}';"

    elif type(ri_id_or_name).__name__ == 'int':
        print(f"ri_id_or_name is an int [{ri_id_or_name}] - {type(ri_id_or_name).__name__} - {type(ri_id_or_name)}")
        sql_query = f"SELECT {qry_string} FROM recipes WHERE ri_id = {ri_id_or_name};"
        print(sql_query)

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

        if int(ingredient[ATOMIC_INDEX]) == IGD_TYPE_DERIVED:

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

    fields = ['ri_id', 'ri_name', 'lead_image', 'description', 'user_rating']    

    for ri_id in list_of_recipe_ids:
        print(f"getting: {ri_id}")
        recipe = get_single_recipe_from_db_for_display_as_dict(ri_id, fields)
        print(f"got: {recipe['ri_name']}")
        recipe_list.append( recipe )

    return recipe_list


# get_next_page_recipe_ids()
def get_all_recipe_ids():

    db_lines = helper_db_class_db.execute("SELECT ri_id FROM recipes WHERE lead_image <> '';").fetchall()

    ids = [ int( str(line).lstrip('(').rstrip(',)') )  for line in db_lines ]

    return ids


filter_to_column_LUT = {'allergens': 'allergens',
                        'ingredient_exc': 'ingredients',
                        'tags_exc': 'tags',
                        'tags_inc': 'tags',
                        'type_exc': 'user_tags', # SB type
                        'type_inc': 'user_tags'}


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
def build_search_query_v1(search, default_filters):

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

# olive oil, garlic, eggs
def build_search_query(search, default_filters):

    search_words = [ word.strip() for word in search.split(',') ]

    if len(search_words) == 0:
        return ''

    def add_one_more_igdt(i):
        return f"AND (ri_id IN (SELECT ri_id FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) all_filters WHERE (igd LIKE '%{i}%'))) "

    # SELECT DISTINCT ri_id
    # FROM (
    #     SELECT ri_id, igd FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) all_filters
    # ) distinct_ids
    # WHERE (igd LIKE '%olive oil%')
    # AND (ri_id IN (SELECT ri_id FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) all_filters WHERE (igd LIKE '%garlic%'))) 
    # AND (ri_id IN (SELECT ri_id FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) all_filters WHERE (igd LIKE '%eggs%'  )))
    # ;

    search_query = f"SELECT DISTINCT ri_id FROM ( SELECT ri_id, igd FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) all_filters ) distinct_ids WHERE (igd LIKE '%{search_words.pop(0)}%') "

    for w in search_words:
        search_query = search_query + add_one_more_igdt(w)

    search_query += ';'

    # print("\n\n- - - - - Constructing Query - - - - S")
    # pprint(default_filters)
    # pprint(search_words)
    # print(insert)
    # print(search_query)
    # print("\n\n- - - - - Constructing Query - - E")

    return search_query


# {'UUID': '014752da-b49d-4fb0-9f50-23bc90e44298',
#  'default_filters': {'allergens': [],
#                      'ingredient_exc': [],
#                      'tags_exc': [],
#                      'tags_inc': ['chicken', 'pork']},
def process_search(search, default_filters):

    # split search by commas
    # build basic query from search
    # add the default filters
    #    handle empty filter arrays
    query = build_search_query(search, default_filters)

    print(f"SEARCH QUERY:\n{query}")

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



def create_daily_tracker_name_from_nix_time(nix_time_ms):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y calories month %m %a %d").lower()


def bootstrap_daily_tracker_create(uuid):
    dtk = { 'dtk_user_info': get_user_info_name_uuid_dict(uuid),
            'dtk_rcp':    return_recipe_dictionary(),
            'dtk_weight': 0.0,
            'dtk_pc_fat': 0.0,
            'dtk_pc_h2o': 0.0  }

    dtk['dtk_rcp']['ri_name'] = create_daily_tracker_name_from_nix_time(dtk['dtk_rcp']['dt_date'])

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

    except DBWriteError as e:
        raise('What could possibly go wrong!?', e)

# DATABASE_URL
def get_user_info_dict_from_DB(uuid):
    request_tables = ['default_filters','tag_sets']#,'usernames']
    # get_filter_colums(from_central_source)
    filter_cols = ['allergens','ingredient_exc','tags_exc','tags_inc','type_exc','type_inc']

    username = helper_db_class_db.execute("SELECT username FROM usernames WHERE uuid_user='{uuid}';").fetchone()
    if username == None: username = 'carter' # Place holder until logins implemented


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

    user_uuid = '014752da-b49d-4fb0-9f50-23bc90e44298'
    print(f"Getting user: {user_uuid}")
    user_info = get_user_info_dict_from_DB(user_uuid)
    print(f"Name: {user_info['name']}")

    search_text = 'olive oil, garlic, eggs'
    
    search_words = [ word.strip() for word in search_text.split(',') ]

    sql_query = build_search_query(search_text, user_info['default_filters'])

    print(f"SQL Query:\n{sql_query}\n\n")


