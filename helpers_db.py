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

import psycopg2
def create_database_if_not_exists(user, password, host, port, database):
    conn = psycopg2.connect(user=user, password=password, host=host, port=port, database='postgres')
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{database}';")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {database};")
    cursor.close()
    conn.close()


db_to_use_string = [
'POSTGRES_DB_LOCAL',                            # 0 - OSX postgres server
'POSTGRES_DB_DOCKER_OSX',                       # 1 - OSX Dockerfile solo container
'POSTGRES_DB_DOCKER_INTERNAL_OSX',              # 2 - OSX docker-compose container OSX
'POSTGRES_DB_DOCKER_NAS',                       # 3 - NAS Dockerfile solo container
'POSTGRES_DB_DOCKER_INTERNAL_NAS_FROM_OSX',     # 4 - NAS docker-compose container location from OSX
'POSTGRES_DB_DOCKER_INTERNAL_NAS'               # 5 - NAS docker-compose container OSX
]

engine = None
helper_db_class_db = None

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def set_DB_connection(db_to_use):
    global helper_db_class_db
    global engine
    print(f"----- helpers_db: attaching to DB [{db_to_use}]------------------------------------S")

    if db_to_use == 'POSTGRES_DB_LOCAL':
        #engine = create_engine(os.environ['DATABASE_URL'])      # pick up from environment - work local/heroku
        engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different    

    elif db_to_use == 'POSTGRES_DB_DOCKER_OSX':
        create_database_if_not_exists('simon', 'pool', 'localhost', '5432', 'cs50_recipes')
        engine = create_engine('postgresql://simon:pool@localhost:5432/cs50_recipes')

    elif db_to_use == 'POSTGRES_DB_DOCKER_INTERNAL_OSX':
        engine = create_engine('postgresql://simon:pool@postgres-container:5432/cs50_recipes')
        #                                   container name ^

    elif db_to_use == 'POSTGRES_DB_DOCKER_NAS':
        engine = create_engine('postgresql://postgres:meepmeep@synologynas.local:6432/cs50_recipes')

    elif db_to_use == 'POSTGRES_DB_DOCKER_INTERNAL_NAS_FROM_OSX':
        create_database_if_not_exists('postgres', 'snacktime', 'creativemateriel.synology.me', '7432', 'cs50_recipes')    
        engine = create_engine('postgresql://postgres:snacktime@creativemateriel.synology.me:7432/cs50_recipes')

    elif db_to_use == 'POSTGRES_DB_DOCKER_INTERNAL_NAS':
        create_database_if_not_exists('postgres', 'snacktime', 'postgres-container-n', '5432', 'cs50_recipes')
        engine = create_engine('postgresql://postgres:snacktime@postgres-container-n:5432/cs50_recipes')    
        #                                           container name ^
    print(f"engine: {engine}")
    helper_db_class_db = scoped_session(sessionmaker(bind=engine))
    print(f"helper_db_class_db: {helper_db_class_db}")
    print(f"----- helpers_db: attaching to DB [{db_to_use}]------------------------------------E")

# stub files for data
from config_files import get_config_or_data_file_path

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
        'types': [ 'none_listed' ],

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
    #               type
    # -
    nutrinfo_dict_keys = [ k for k, v in updated_info['nutrinfo'].items() ]

    # query db - the index from fields is used to retrive and alocate data to correct dictionary entry - -
    if fields == None:
        fields = ['id','ri_id','ri_name','description','method','notes','yield','units','servings','density','serving_size',
                  'igdt_type','ingredients','allergens','types','tags','user_tags','lead_image','text_file',
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

    print(sql_query)
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
    # print(f"----- updated_info: S")
    # print(updated_info)
    # print(updated_info.keys())
    # print(f"----- updated_info: F")
    # print(fields)
    print(f"----- updated_info: M")
    print(updated_info['tags'])
    print(updated_info['types'])     
    print(updated_info['allergens'])
    print(f"----- updated_info: E")
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

# def flatten(lst):
#     result = []
#     for i in lst:
#         if isinstance(i, list):
#             result.extend(flatten(i))
#         else:
#             result.append(i)
#     return result

# # scan ingredients for subcomponents - recurse until ALL ATOMIC!
# # return a list of components id's

# TODO would it be better to add an unroll flag to the recipe dictionary and do this on the device?
# as in in JS land?

def convert_tree_to_list_of_dict_components(tree):
    leaf_list = []

    def prl(tag, leaf_list):
        leaf_list_ids = [n['ri_id'] for n in leaf_list]
        print(f"{tag}: {leaf_list_ids}")


    def dfs(node, parent=None, key=None, sub_list=[]):

        print(f"DFS: {node['ri_id']} - {node['ri_name']}")
        if 'components' in node and node['components']:  # If the node has components
            ssl = []    # sub sub list
            for child_key, child in list(node['components'].items()):  # For each child
                print(f"child: {child['ri_id']} - {child['ri_name']}")
                ssl = dfs(child, node, child_key, ssl)
                prl('ssl',ssl)

            sub_list = sub_list + [node] + ssl
            prl('sub_list',sub_list)

            if parent is not None:
                parent['components'].pop(key)  # Remove the node from its parent's components

            return sub_list

        else:
            sub_list.append(node)
            print(f"append: {node['ri_id']} - {node['ri_name']}")
            prl('sub_list',sub_list)

            if parent is not None:
                parent['components'].pop(key)
            return sub_list

    leaf_list = dfs(tree)

    print(f">> ri_name: {tree['ri_name']}")
    pprint(tree)
    print(' - o - ')

    return leaf_list


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

def get_recipes_with_subcomponents_for_display_as_list_of_dicts(list_of_recipe_ids):
    recipe_list = []

    for ri_id in list_of_recipe_ids:
        print(f"getting: {ri_id}")

        recipe = get_single_recipe_with_subcomponents_from_db_for_display_as_dict(int(ri_id))

        print(f"got: {recipe['ri_name']}")

        recipe_list.append( recipe )

    return recipe_list

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                     list of ID's for SEARCH - - - - \
def get_gallery_info_for_display_as_list_of_dicts(list_of_recipe_ids=[]):
    recipe_list = []

    fields = ['ri_id', 'ri_name', 'lead_image', 'description', 'user_rating', 'types']    

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



# return recipe with all the ingredients listed
# olive oil, garlic, eggs
# filter out ingredients that contain allergies in the user profile
# def build_search_query_v4
def build_search_query(search, default_filters):

    search_words = [ word.strip() for word in search.split(',') ]

    if len(search_words) == 0:
        return ''
    
    def add_one_more_igdt(i):
        return f"AND (ri_id IN (SELECT ri_id FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered WHERE (igd LIKE '%{i}%'))) "

    if (len(search_words) == 1) and (search_words[0] == '*'):
        search_query = f"SELECT DISTINCT ri_id FROM ( SELECT ri_id, igd FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered ) distinct_ids WHERE (igd IS NOT NULL) " 
    else:
        search_query = f"SELECT DISTINCT ri_id FROM ( SELECT ri_id, igd FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered ) distinct_ids WHERE (igd LIKE '%{search_words.pop(0)}%') "

        for w in search_words:
            search_query = search_query + add_one_more_igdt(w)

    # SELECT DISTINCT ri_id
    # FROM (
    #     SELECT ri_id, igd FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered
    # ) distinct_ids
    # WHERE (igd LIKE '%olive oil%')
    # AND (ri_id IN (SELECT ri_id FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered WHERE (igd LIKE '%garlic%'))) 
    # AND (ri_id IN (SELECT ri_id FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered WHERE (igd LIKE '%eggs%'  )))
    # ;

    # add check for filter
    def wrap_allergy_qry(item, filter_col):
        return f"'{item}' = ANY({filter_col})"

    # type_inc, tags_exc
    if (len(default_filters['allergens']) > 0) or (len(default_filters['type_inc']) > 0):
        search_query = f"SELECT ri_id FROM recipes WHERE ri_id IN ( {search_query} ) "


    filter = 'allergens'
    if (len(default_filters[filter]) > 0):
        exclude_qry_list = [ wrap_allergy_qry(a, filter) for a in default_filters[filter] ]
        # ["'dairy' = ANY(allergens)", "'eggs' = ANY(allergens)", "'peanuts' = ANY(allergens)"]

        exclude_qry = ' OR '.join(exclude_qry_list)
        # "'dairy' = ANY(allergens) OR 'eggs' = ANY(allergens) OR 'peanuts' = ANY(allergens)"

        search_query = search_query + f"AND NOT ( {exclude_qry} ) "

    filter = 'types'
    if (len(default_filters['type_inc']) > 0):
        exclude_qry_list = [ wrap_allergy_qry(a, filter) for a in default_filters['type_inc'] ]
        # ["'dairy' = ANY(allergens)", "'eggs' = ANY(allergens)", "'peanuts' = ANY(allergens)"]

        exclude_qry = ' OR '.join(exclude_qry_list)
        # "'dairy' = ANY(allergens) OR 'eggs' = ANY(allergens) OR 'peanuts' = ANY(allergens)"

        #search_query = search_query + f"AND NOT ( {exclude_qry} ) "
        search_query = search_query + f"AND ( {exclude_qry} ) "

    # SELECT ri_id FROM recipes
    # WHERE ri_id IN (
    #     SELECT DISTINCT ri_id
    #     FROM (
    #         SELECT ri_id, igd FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered
    #     ) distinct_ids
    #     WHERE (igd LIKE '%olive oil%')
    #     AND (ri_id IN (SELECT ri_id FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered WHERE (igd LIKE '%garlic%'))) 
    #     AND (ri_id IN (SELECT ri_id FROM ( SELECT ri_id, unnest(ingredients) igd FROM exploded ) unfiltered WHERE (igd LIKE '%eggs%'  )))
    # )
    # AND NOT ('dairy' = ANY(allergens) OR 'eggs' = ANY(allergens) OR 'peanuts' = ANY(allergens));

    #search_query += ';'
    # Add ordering by the number of ingredients
    search_query = f"""
    SELECT filtered_results.ri_id
    FROM (
        {search_query}
    ) AS filtered_results
    JOIN exploded ON filtered_results.ri_id = exploded.ri_id
    ORDER BY (
        SELECT COUNT(*)
        FROM unnest(exploded.ingredients) AS igd
    );
    """

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
    print(f"No of hits: {len(db_lines)} <")

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
    database_file = get_config_or_data_file_path(data_set)

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
    database_file = get_config_or_data_file_path(data_set)

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


def get_search_settings_dict():
    default_filters = {
        'allergens': [],          # exclude ALL
        'tags_inc':  [],          # include at least ONE - think about OR vs AND
        'tags_exc':  [],          # exclude ALL
        'type_exc':  [],          # include at least ONE - think about OR vs AND
        'type_inc':  [],          # exclude ALL
        'ingredient_exc': [] }    # exclude ALL

    return default_filters


def create_user(uuid='014752da-b49d-4fb0-9f50-23bc90e44298', user_settings={}):
    # Tables for get_user: user_devices, devices, default_filters, tag_sets, usernames, dtk
    # https://docs.python.org/3/library/uuid.html
    # maybe use domain version, have a think
    default_user_settings = {
        'UUID': '014752da-b49d-4fb0-9f50-23bc90e44298',  #uuid #str(uuid.uuid4()), # TODO comment back in and look up from unique name
        'name': 'Simon',
        'devices': ['dev1_fp_hash', 'dev2_fp_hash', 'dev3_fp_hash'],
        'default_filters': get_search_settings_dict(),
        'tag_sets': get_search_settings_dict(),
        'fav_rcp_ids':[],
        'update_time_stamp': nix_time_ms()
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

    request_table_w_cols = {
        'default_filters':['allergens','ingredient_exc','tags_exc','tags_inc','type_inc','type_exc'],
        'tag_sets':['allergens','ingredient_exc','tags','types']
    }

    usernameRowProxy = helper_db_class_db.execute(f"SELECT username, update_time_stamp FROM usernames WHERE uuid_user='{uuid}';").fetchone()

    try:
        username = usernameRowProxy[0]
        update_time_stamp = usernameRowProxy[1]
    except:
        return create_user(uuid, {'name': 'carter'})
        
    return_user_info = {'UUID':uuid, 'name':username, 'update_time_stamp':update_time_stamp}

    print(f"- - RETRIEVING FROM DB - {uuid} ( -o- ) - S")

    pprint(return_user_info)

    tag_sets_and_filters = {}

    for table, filter_cols in request_table_w_cols.items():
        tag_sets_and_filters[table] = {}

        # SELECT * FROM default_filters WHERE uuid_user='014752da-b49d-4fb0-9f50-23bc90e44298';
        sql_query = f"SELECT * FROM {table} WHERE uuid_user='{uuid}';"
        print(f"\nTABLE {table} - SQL: {sql_query} < - - - - - < <")        
        
        tagdata_for_table = helper_db_class_db.execute(sql_query).fetchone() # - returns RowProxy        

        # print(f"table:{table}, filter_cols:")
        # pprint(filter_cols)
        # print('- - - / ')
        for col in filter_cols:
            #print(f"table:{table}, col:{col}")
            tag_sets_and_filters[table][col] = tagdata_for_table[col]            
    
    return_user_info.update(tag_sets_and_filters)

    return_user_info['fav_rcp_ids'] = get_favs_from_DB(helper_db_class_db, uuid)

    #pprint(return_user_info)

    print(f"- - RETRIEVING FROM DB - {uuid} ( -o- ) - E")
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
# 'tag_sets': { 'allergens': [],
#     ^         'ingredient_exc': ['coriander', 'bad sausage'],
#     ^         'tags_exc': ['ns_pregnant'],
#     ^         'tags_inc': [] },    ^
#     ^           ^                  ^
#     ^           ^                  ^
#     ^        column_name       rows_data
#      table_key > dict of arrays
#
#
def get_favs_from_DB(db, uuid):
    fav_recipes = []

    sql_query = f"SELECT fav_rcp_id FROM fav_rcp_ids WHERE uuid_user='{uuid}';"
    print(f"\nSQL: {sql_query} < - - - - - < <")        
    
    favs_db = db.execute(sql_query).fetchall() # - returns RowProxy   
    pprint(favs_db)
    if len(favs_db) > 0: pprint(favs_db[0][0])
    pprint(len(favs_db))
    if favs_db and len(favs_db) > 0:
        fav_recipes = [ ri_id_tup[0] for ri_id_tup in favs_db ]

    return fav_recipes


def append_merge_favs_to_DB(db, user_settings):
    # Save favourites
    # INSERT INTO fav_rcp_ids 
    # VALUES 
    # ('014752da-b49d-4fb0-9f50-23bc90e44298', 112),
    # ('014752da-b49d-4fb0-9f50-23bc90e44298', 999),
    # ('014752da-b49d-4fb0-9f50-23bc90e44298', 331)
    # ON CONFLICT (uuid_user, fav_rcp_id) DO NOTHING;
    if len(user_settings['fav_rcp_ids']) > 0:
        uuid = user_settings['UUID']
        value_pairs = ','.join([ f"('{uuid}', {fav})" for fav in user_settings['fav_rcp_ids'] ])
        sql_command = f"INSERT INTO fav_rcp_ids VALUES {value_pairs} ON CONFLICT (uuid_user, fav_rcp_id) DO NOTHING;"

        print(f"***** SQL WRITE:\n{sql_command}\n\n")
        db.execute(sql_command)    
        print(f"RESULT: {db.commit()} <\n\n") # < < COMMIT
    else:
        print(f"RESULT: No of fav_rcp_ids = {len(user_settings['fav_rcp_ids'])} <\n\n") # < < COMMIT


def add_timestamp_to_user_DB(db, user_settings):
    uuid = user_settings['UUID']
    user_name = user_settings['name']
    timestamp = user_settings['update_time_stamp']

    sql_command = f"""
    INSERT INTO usernames (uuid_user, username, update_time_stamp)
    VALUES ('{uuid}', '{user_name}', {timestamp})
    ON CONFLICT (uuid_user)
    DO UPDATE SET username = EXCLUDED.username, update_time_stamp = EXCLUDED.update_time_stamp;
    """

    print(f"***** SQL WRITE:\n{sql_command}\n\n")
    db.execute(sql_command)    
    print(f"RESULT: {db.commit()} <\n\n") # < < COMMIT


def remove_favs_from_DB(db, uuid, recipe_ids):
    # Remove favourites
    # DELETE FROM fav_rcp_ids
    # WHERE uuid_user = '014752da-b49d-4fb0-9f50-23bc90e44298'
    # AND fav_rcp_id IN (613, 1566, 969);   

    recipe_id_string = ','.join(recipe_ids)
    sql_command = f"DELETE FROM fav_rcp_ids WHERE uuid_user = '{uuid}' AND fav_rcp_id IN ({recipe_id_string});"
    
    print(f"***** SQL WRITE:\n{sql_command}\n\n")
    db.execute(sql_command)
    result = db.commit()
    print(f"RESULT: {result} <\n\n") # < < COMMIT
    return result


def update_settings_tables_for_uuid(db, user_settings):
    pprint(user_settings)

    uuid = user_settings['UUID']

    #table_list = ['allergens','ingredient_exc','tags_exc','tags_inc','type_inc','type_exc']
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
        #                   tags = '{"vegan","veggie"}'
        #                 WHERE uuid_user = '014752da-b49d-4fb0-9f50-23bc90e44298';
        sql_command = f"UPDATE {table_key} SET {column_update} WHERE uuid_user = '{uuid}';"

        #print(f"TK:{table_key}\nROW:{column_update}\nSQL:{sql_command}")
        print(f"***** SQL WRITE:\n{sql_command}\n\n")
        db.execute(sql_command)    
        print(f"RESULT: {db.commit()} <\n\n") # < < COMMIT
        # TODO - commit return None on success?
        # how is failure reported?

    append_merge_favs_to_DB(db, user_settings)

    add_timestamp_to_user_DB(db, user_settings)


# EG DB write
# UPDATE tag_sets SET ingredient_exc = '{"turkey", "caramelised apple", "knockwurst"}' WHERE uuid_user = '014752da-b49d-4fb0-9f50-23bc90e44298';
# UPDATE default_filters
# UPDATE tag_sets
def update_user_info_dict(user_settings):
    uuid = user_settings['UUID']
    user_settings['update_time_stamp'] = nix_time_ms()
    
    try:
        # local filesystem
        user_db[uuid].update(user_settings)
        commit_User_DB()

        # db defined in DATABASE_URL
        update_settings_tables_for_uuid(helper_db_class_db, user_settings)
        return True

    except KeyError as e:
        raise(DBAccessKeyError("update_settings_tables_for_uuid ERROR", e))
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


