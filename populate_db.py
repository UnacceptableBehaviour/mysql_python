#! /usr/bin/env python

import sys

opt_dict = {
    'verbose_mode':     False,
}

if '-v' in sys.argv:
    opt_dict['verbose_mode'] = True


help_string = f'''\n\n\n
HELP:\n
Look up food info details. . . 

- - - options - - - 
-v          Verbose mode turn on more diagnostics

-h          This help
'''

if ('-h' in sys.argv) or ('--h' in sys.argv) or ('-help' in sys.argv) or ('--help' in sys.argv):
    print(help_string)
    sys.exit(0)


# add profiling - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
# for globbing filter - include / exclude sections of call graph to focus
from pycallgraph import Config
from pycallgraph import GlobbingFilter

config = Config(max_depth=4)
config.trace_filter = GlobbingFilter(
exclude=[
     'urllib.*',
#     'pprint.*',
#     'http.*',
#     #'pycallgraph.*',
#     #'*.secret_function',
],
include=[
#    '*',
    'helpers.*',
    'populate_db.*',
])

# profiling output into PNG format image - not searchable
graphviz = GraphvizOutput(output_file='filter_A.png')
# add profiling - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from pathlib import Path

# loads csv file from server and loads into database LIVE

# refresh the asset server with any new data
import subprocess

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# sessions
# https://docs.sqlalchemy.org/en/latest/orm/session_basics.html


# giza a look
from pprint import pprint
# If there are many levels of recursion, and you don't want to see them all
# you can use the depth parameter to limit how many levels it goes down
#pprint(engine, depth=2)


# for regex
import re

import urllib.parse          # used to parse passwords into url format
url_encoded_pwd = urllib.parse.quote_plus("kx%jj5/g")

from helpers import create_list_of_recipes_and_components_from_recipe_id, get_csv_from_server_as_disctionary, create_exploded_recipe
from helpers_db import get_search_settings_dict

# Relative '.' import only works if it's inside a package being imported
# so
# from .load_csv import get_csv_from_server_as_disctionary
# doesn't work
# remove '.' for it to work
# more here
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3/28154841

# when is an empty  __init__.py file in the directory required?
# when using packages
# https://stackoverflow.com/questions/448271/what-is-init-py-for


# default
#engine = db.create_engine('dialect+driver://user:pass@host:port/db')
#engine = create_engine('mysql://scott:tiger@localhost/foo')

#engine = create_engine('mysql://root:@localhost/nutridb_sr25_sanitized')
#engine = create_engine('mysql://root:meepmeep@localhost/nutridb_sr25_sanitized')

# to fine user and port at msql prompt
# mysql> select user();
# mysql> show variables;

# mysql connection
#engine = create_engine('mysql://root:meepmeep@localhost:3306/recipe_cs50')

#postgresql connection
#engine = create_engine('postgresql://root:meepmeep@localhost:3306/recipe_cs50')

# https://docs.sqlalchemy.org/en/latest/core/engines.html#postgresql
#engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different
#engine = create_engine('postgresql://simon:@localhost:5432/simon')  # database name different
# docker container DB
engine = create_engine('postgresql://simon:loop@localhost:5432/cs50_recipes')  # database name different
db = scoped_session(sessionmaker(bind=engine))
pprint(engine)

print("----- populate_asset_server.rb ----------------------------------------- ASSET SERVER POPULATION FEEDBACK - S")

# force_complete_rebuild = False
force_complete_rebuild = True

if ( force_complete_rebuild == True ):
    # .rb find txt recipes and jpgs of those recipes
    # resizes images and copies both to asset server
    # also creates a CSV file with synopsis, and nutrition info for creating DB (done by this script)
    population_data = subprocess.check_output(['populate_asset_server.rb'])
    if opt_dict['verbose_mode']: print(population_data)
else:
    print('NOT EXECUTING populate_asset_server.rb  * * * * * WARNING <<  force_complete_rebuild = False')


print("----- populate_asset_server.rb ----------------------------------------- ASSET SERVER POPULATION FEEDBACK - E")


# let IGD_TYPE_ATOMIC    = 0;
# let IGD_TYPE_DERIVED   = 1;
# let IGD_TYPE_OTS       = 2;   // Off The Shelf
# let IGD_TYPE_DTK       = 3;   // Daily TracKer 
# insert array of arrays
def create_sql_insert_ingredients_array_text(ingredients):
    # '{    {"0", "250", "(0)", "cheese"},          # 0 - atomic
    #       {"0", "110", "(0)", "rice"},
    #       {"1", "110", "(0)", "turkey mix"},      # 1 - sc - subcomponent- derived
    #       {"0", "20", "(0)", "pepper"},
    #       {"0", "20", "(0)", "salt"},
    #       {"0", "55", "(1)", "eggs"}
    #   }'

    sql_insert = "'{"

    for line in ingredients:
        sql_insert = sql_insert + "{"
        for i in line:
            sql_insert = sql_insert + f'"{i}", '

        sql_insert = sql_insert.rstrip(', ')             # remove trailing comma
        sql_insert = sql_insert + "}, "

    sql_insert = sql_insert.rstrip(', ')                 # remove trailing comma
    sql_insert = sql_insert + "}', "

    return sql_insert

def create_sql_insert_exploded_ingredients_array_text(ingredients):
    # from
    # ['steak and chips run 2', 'chips run 2', 'potatoes', 'ribeye steak', 'veg oil']
    # to
    # {"steak and chips run 2", "chips run 2", "potatoes", "ribeye steak", "veg oil"}

    sql_insert = "'{"

    for i in ingredients:
        sql_insert = sql_insert + f'"{i}", '

    sql_insert = sql_insert.rstrip(', ')                 # remove trailing comma
    sql_insert = sql_insert + "}', "

    return sql_insert


# insert array of strings
def create_sql_insert_tags_array_text(tags):
    # '{"veggie", "beef", "shellfish", "fish"}'

    sql_insert = "'{"

    for tag in tags:
        sql_insert = sql_insert + f'"{tag}", '

    sql_insert = sql_insert.rstrip(', ')             # remove trainling comma
    sql_insert = sql_insert + "}', "                 # close SQL array parenthesis

    return sql_insert

# TODO - check this get fleshes out from DB contents at some point
def get_default_tag_sets_dictionary():
    # defaults
    tag_sets = { 'allergens':['dairy','eggs','peanuts','nuts','seeds_lupin','seeds_sesame','seeds_mustard','fish','molluscs','crustaceans','alcohol','celery','gluten','soya','sulphur_dioxide'],
                'ingredient_exc': [],
                'tags': ['vegan','veggie','cbs','chicken','pork','beef','seafood','shellfish','gluten_free','ns_pregnant'],                
                'types': ['component','amuse','side','starter','fish','lightcourse','main','crepe','dessert','p4','cheese','comfort','low_cal','serve_cold','serve_rt','serve_warm','serve_hot']
               }

    return tag_sets

def create_entry_in_db(db, table, entry):

    if opt_dict['verbose_mode']: 
        print(f"----- populate_db.py: create_entry_in_db: {table} -------------------------------------------- ")
        if 'ri_id' in entry:
            print(f"----- ri_id:{entry['ri_id']} -------------------------------------------- ")
        if 'ri_name' in entry:
            print(f"----- ri_name:{entry['ri_name']} -------------------------------------------- ")
        if 'igdt_type' in entry:
            print(f"----- igdt_type:{entry['igdt_type']} \n-------------------------------------------- ")
        if 'ingredients' in entry:
            print(f"----- ingredients:{entry['ingredients']} \n-------------------------------------------- ")
        if 'description' in entry:
            print(f"----- description:{entry['description']} \n-------------------------------------------- ")
        if 'user_rating' in entry:
            print(f"----- stars:{entry['user_rating']} \n-------------------------------------------- ")
        if 'allergens' in entry:
            print(f"----- allergens:{entry['allergens']} \n-------------------------------------------- ")
        if 'tags' in entry:
            print(f"----- tags:{entry['tags']} \n-------------------------------------------- ")
        if 'types' in entry:
            print(f"----- types:{entry['types']} \n-------------------------------------------- ")


    sql_string = f"INSERT INTO {table}"
    fields = "("
    data =  "("
    for header in entry:
        if opt_dict['verbose_mode']: print(f"{header} = {entry[header]} - class:{entry[header].__class__.__name__}")
        fields = fields + f"{header}, "

        if header == 'ri_id' or header == 'serving_size':
            if opt_dict['verbose_mode']: print(f"{header} is an INT NUMBER")
            data = data + f"{entry[header]}, "

        elif header == 'igdt_type':
            if opt_dict['verbose_mode']: print(f"{header} is an SMALL INT NUMBER")
            data = data + f"{entry[header]}, "

        elif re.match(r'n_\w+', header ):
            if opt_dict['verbose_mode']: print(f"{header} is a NUMBER")
            data = data + f"{entry[header]}, "

        elif header == 'ingredients':
            if opt_dict['verbose_mode']: print(f"{header} is a LIST of ingredients")
            if table == 'exploded':
                ingredients_insert_text = create_sql_insert_exploded_ingredients_array_text(entry[header])
            else:
                ingredients_insert_text = create_sql_insert_ingredients_array_text(entry[header])
            
            data = data + ingredients_insert_text
            pprint(entry[header])
            if opt_dict['verbose_mode']: print(f"\n - - - - i - - - - \n{ingredients_insert_text}\n - - - - i - - - - ")

        elif header == 'yield':
            if opt_dict['verbose_mode']: print(f"{header} is a NUMBER in g")
            data = data + f"{entry[header].rstrip('g')}, "

        elif header == 'allergens' or header == 'tags' or header =='types':
            if opt_dict['verbose_mode']: print(f"{header} is a LIST of tags / strings")
            tag_to_insert = create_sql_insert_tags_array_text(entry[header])
            data = data + tag_to_insert

        else:
            if opt_dict['verbose_mode']: print(f"{header} is a STRING")
            data = data + f"'{entry[header]}', "


    data = data.rstrip(', ') + ")"

    fields = fields.rstrip(', ') + ")"

    sql_string = f"{sql_string} {fields} VALUES {data};"

    print('|')
    print(sql_string)
    db.execute(sql_string)
    db.commit()
    print('/ - -')
    print('.\n.\n.')

    #INSERT INTO recipes (rcp_id, image_filename, recipe_title, txt_ingredient_file, n_En, n_Fa, n_Fs, n_Fm, n_Fp, n_Fo3, n_Ca, n_Su, n_Fb, n_St, n_Pr, n_Sa, n_Al, serving_size) VALUES ('0', '20181226_174632_crispy prawn and vegetable risotto.jpg', 'crispy prawn and vegetable risotto', '20181226_174632_crispy prawn and vegetable risotto.txt', '137', '6.97', '2.74', '3.05', '0.51', '0.0', '11.83', '2.03', '1.02', '0.18', '6.96', '1.01', '0.0', '466');
    #INSERT INTO recipes (rcp_id, image_filename, recipe_title, serving_size) VALUES ('0', '20181226_174632_crispy prawn and vegetable risotto.jpg', 'crispy prawn and vegetable risotto', '20181226_174632_crispy prawn and vegetable risotto.txt', '137', '6.97', '2.74', '3.05', '0.51', '0.0', '11.83', '2.03', '1.02', '0.18', '6.96', '1.01', '0.0', '466');
    #INSERT INTO recipes (rcp_id, image, title, text_file, n_En, n_Fa, serving_size) VALUES (0, '20181226_174632_crispy prawn and vegetable risotto.jpg', 'crispy prawn and vegetable risotto', '20181226_174632_crispy prawn and vegetable risotto.txt', 137, 6.97, 466)
    #INSERT INTO recipes (rcp_id, image, title, text_file) VALUES (0, '20181226_174632_crispy prawn and vegetable risotto.jpg', 'crispy prawn and vegetable risotto', '20181226_174632_crispy prawn and vegetable risotto.txt');

def create_table_in_database_from_sql_template(data_base, template_file):
    create_table_sql_command = ''
    print(f"\n> - create_table_in_database_from_sql_template - S\n{template_file}")
    
    with open(template_file) as sql_template:
        create_table_sql_command = sql_template.read()

    db_lines = data_base.execute(create_table_sql_command)    
    data_base.commit()

    if opt_dict['verbose_mode']: print(f"\n{db_lines}\n> - create_table_in_database_from_sql_template - E\n")
    return(db_lines)


def drop_tables_for_fresh_start(data_base, tables):

    for table in tables:
        sql_command = f"DROP TABLE IF EXISTS {table};"

        print(f"\nSQL cmd: {sql_command} <")

        if opt_dict['verbose_mode']: print(f"> - drop_tables_for_fresh_start - S\n{sql_command}\n> - drop_tables_for_fresh_start - E\n")
        data_base.execute(sql_command)
        data_base.commit()

    return

def insert_empty_default_filters_for_user(db, uuid):
    empty_default_filters = get_search_settings_dict()
    insert_tags_for_table_for_user(db, uuid, 'default_filters', empty_default_filters)


def insert_default_tag_sets_for_user(db, uuid):
    tag_sets = get_default_tag_sets_dictionary()
    insert_tags_for_table_for_user(db, uuid, 'tag_sets', tag_sets)


def insert_tags_for_table_for_user(db, uuid, table, tag_sets):
    # create DB INSERT command
    # INSERT INTO tag_sets ('uuid_user', 'allergens', 'ingredient_exc', . . ) VALUES (uuid, {tags}, {tags});
    #create_sql_insert_tags_array_text(tags)

    column_names = ','.join([ f"{tag_set}" for tag_set in tag_sets ])

    rows_data = ""
    for tag_set in tag_sets:
        if rows_data != "": rows_data += ','                              # comma between sets

        row = ','.join([ f'"{entry}"' for entry in tag_sets[tag_set] ])   # create list of array entries
                                      #  array1              array2
        rows_data += f"'{{{row}}}'"   # '{"item1","item2"}', '{"item1","item2"}' correct format for sql

    # assemble into sql command
    sql_command = f"INSERT INTO {table} (uuid_user, {column_names} ) VALUES ('{uuid}', {rows_data});"

    print(f"> - insert_tags_for_table_for_user - S\n{sql_command}\n> - insert_tags_for_table_for_user - E\n")
    db.execute(sql_command)
    db.commit()

def insert_dev_user_into_usernames_table(db, uuid, user_name, table):
    # create DB INSERT command
    # INSERT INTO usernames (uuid_user, username)  VALUES ('uuid', 'user_name');

    sql_command = f"INSERT INTO {table} (uuid_user, username)  VALUES ('{uuid}', '{user_name}');"

    print(f"> - insert_dev_user_into_usernames_table - S\n{sql_command}\n> - insert_dev_user_into_usernames_table - E\n")
    db.execute(sql_command)
    db.commit()


def main():
    # execute this query
    # SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;
    #db_lines = db.execute("SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;").fetchall()
    #db_lines = db.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES").fetchall()
    #db_lines = db.execute("SHOW TABLES").fetchall() #msyql
    #db_lines = db.execute('SELECT * FROM sal_emp').fetchall()  # work fine

    force_drop_tables = True 

    # insert default_filters
    # create setings tables
    user_settings_tables_templates = ['db_table_default_filters.sql','db_table_devices.sql','db_table_tag_sets.sql','db_table_user_devices.sql','db_table_usernames.sql','db_table_fav_rcp_ids.sql']
    # create recipes table
    # create exploded recipes table
    # create ingredients table
    recipe_table_templates = ['db_table_recipe_table_def.sql','db_table_recipe_exploded_table_def.sql','db_table_atomic_ingredients_table_def.sql']

    settings_tables = ['default_filters','devices','tag_sets','user_devices','usernames','fav_rcp_ids']
    recipe_tables = ['recipes','exploded','atomic_ingredients']    

    template_folder = Path('/Users/simon/a_syllabus/lang/python/mysql_python/static/')

    if (force_drop_tables == True or force_complete_rebuild == True):
        # DROP TABLES
        drop_tables_for_fresh_start(db, settings_tables + recipe_tables)

    table_templates_to_initialize = recipe_table_templates + user_settings_tables_templates

    for table in table_templates_to_initialize:
        sql_template = template_folder.joinpath(table)
        db_lines = create_table_in_database_from_sql_template(db, sql_template)
        print(db_lines)

    # insert default values into tag_sets
    uuid = '014752da-b49d-4fb0-9f50-23bc90e44298'
    dev_user = 'carter'
    insert_default_tag_sets_for_user(db, uuid)
    insert_empty_default_filters_for_user(db, uuid)
    insert_dev_user_into_usernames_table(db, uuid, dev_user, 'usernames')
    

    # *** SEE TOP OF HELPERS FILE - FOR SERVER SETTING INFO ***
    # http-server -p 8000 --cors
    #url_file = 'http://192.168.1.13:8000/static/sql_recipe_data.csv'
    url_file = 'http://127.0.0.1:8000/static/sql_recipe_data.csv'
    
    
    # http-server  --cors -S -C ./scratch/asCerts/server.crt -K ./scratch/asCerts/server.key
    #url_file = 'https://asset.server:8080/static/sql_recipe_data.csv' # problem with cert 10.Jun.22
    

    sql_dict = get_csv_from_server_as_disctionary(url_file)

    print(sql_dict.__class__.__name__)
    print(f"Size of sql_dict {len(sql_dict)}")
    #sys.exit(0)

    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    # go through the CSV file of rows of recipes - parse and load data
    max_entries = 20
    rcount = 0
    for entry in sql_dict:
        print(f"> > > > ENTRY:{entry} {type(entry)}* * * * * * * * * * * * * * * * ")

        sql_row = sql_dict[entry]
        ri_id = int(sql_row['ri_id'])   # TOP level / master recipe ID - the ID in the CSV row!

        if opt_dict['verbose_mode']: print(f"> > > > SQL_ROW: C:{type(sql_row)} {sql_row['text_file']} - {sql_row['ri_name']} * * * * * * * * * * * * * * * * M - - -")
        if opt_dict['verbose_mode']: pprint(sql_row)
        # create list of recipes (headline & sub components) to add into database

        recipes_from_id = create_list_of_recipes_and_components_from_recipe_id(sql_row, opt_dict['verbose_mode'])

        if opt_dict['verbose_mode']: print("\n|\n|\n|\n= = = = = =")
        if opt_dict['verbose_mode']: pprint(recipes_from_id)
        if opt_dict['verbose_mode']: print("\n= = = = = =\n|\n|\n|")

        #should put some exception handling around this
        for recipe in recipes_from_id:
           create_entry_in_db(db, 'recipes', recipe)

        # rcount += 1
        # if rcount > max_entries: break

    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    print(f"> > > > E X P L O D E - E X P L O D E - E X P L O D E - E X P L O D E - <    <    <    <    <    <    <    <    <")
    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    
    max_entries = 20
    rcount = 0
    for entry in sql_dict:

        sql_row = sql_dict[entry]

        exploded_recipe_dict = create_exploded_recipe(sql_row)
        
        print(f"> > > > E X P L O D E D: {exploded_recipe_dict['ri_name']} {type(exploded_recipe_dict)} <    <    <    <    <    <    <    <    <     *")
        if opt_dict['verbose_mode']: pprint(exploded_recipe_dict)

        create_entry_in_db(db, 'exploded', exploded_recipe_dict )

        # rcount += 1
        # if rcount > max_entries: sys.exit(0)

if __name__ == '__main__':
    main()
    # with PyCallGraph(output=graphviz, config=config):
    #     main()

    # tests
