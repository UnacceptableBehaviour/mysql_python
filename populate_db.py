#! /usr/bin/env python



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

print("----- list.py ------------------------------------------------------------ importing")

# from helpers import get_csv_from_server_as_disctionary, inc_recipe_counter, log_exception, create_list_of_recipes_and_components_from_recipe_id

from helpers import create_list_of_recipes_and_components_from_recipe_id, get_csv_from_server_as_disctionary, create_exploded_recipe


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


print("----- list.py ------------------------------------------------------------ DONE importing")

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
engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different
#engine = create_engine('postgresql://simon:@localhost:5432/simon')  # database name different 
db = scoped_session(sessionmaker(bind=engine))
pprint(engine)

print("----- populate_asset_server.rb ----------------------------------------- ASSET SERVER POPLATION FEEDBACK - S")

force_complete_rebuild = False
force_complete_rebuild = True

if ( force_complete_rebuild == True ):
    population_data = subprocess.check_output(['populate_asset_server.rb'])
    print(population_data)
else:
    print('NOT EXECUTING populate_asset_server.rb  * * * * * WARNING <<  force_complete_rebuild = False')


print("----- populate_asset_server.rb ----------------------------------------- ASSET SERVER POPLATION FEEDBACK - E")

# insert array of arrays
def create_sql_insert_ingredients_array_text(ingredients):
    # '{    {"0", "250", "(0)", "cheese"},          # 0 - atomic
    #       {"0", "110", "(0)", "rice"},
    #       {"1", "110", "(0)", "turkey mix"},      # 1 - sc - subcomponent
    #       {"0", "20", "(0)", "pepper"},
    #       {"0", "20", "(0)", "salt"},
    #       {"0", "55", "(1)", "eggs"}
    #   }'
    
    sql_insert = "'{"
    
    for line in ingredients:
        sql_insert = sql_insert + "{"
        for i in line:
            sql_insert = sql_insert + f'"{i}", '
        
        sql_insert = sql_insert.rstrip(', ')             # remove trainling comma
        sql_insert = sql_insert + "}, "
    
    sql_insert = sql_insert.rstrip(', ')                 # remove trainling comma
    sql_insert = sql_insert + "}', "
    
    return sql_insert


# insert array of strings
def create_sql_insert_tags_array_text(tags):
    # '{"veggie", "beef", "s&c", "fish"}'
    
    sql_insert = "'{"
    
    for tag in tags:
        sql_insert = sql_insert + f'"{tag}", '
            
    sql_insert = sql_insert.rstrip(', ')             # remove trainling comma
    sql_insert = sql_insert + "}', "                 # close SQL array parenthesis    
    
    return sql_insert


def create_entry_in_db(db, table, entry):

    print(f"----- list.py: create_entry_in_db ------------------------------------------------------------ ")
    print(f"----- table:{table} <> recipe: {entry['ri_name']} -------------------------------------------- ")
    print(f"----- ingredients:{entry['ingredients']} \n-------------------------------------------- ")
    print(f"----- description:{entry['description']} \n-------------------------------------------- ")
    print(f"----- stars:{entry['user_rating']} \n-------------------------------------------- ")
    print(f"----- allergens:{entry['allergens']} \n-------------------------------------------- ")
    print(f"----- tags:{entry['tags']} \n-------------------------------------------- ")
    
    sql_string = f"INSERT INTO {table}"
    fields = "("
    data =  "("
    for header in entry:
        print(f"{header} = {entry[header]} - class:{entry[header].__class__.__name__}")
        fields = fields + f"{header}, "
        
        if header == 'ri_id' or header == 'serving_size':
            print(f"{header} is an INT NUMBER")
            data = data + f"{entry[header]}, "        
                
        elif re.match(r'n_\w+', header ):
            print(f"{header} is a NUMBER")
            data = data + f"{entry[header]}, "
                
        elif header == 'ingredients':
            print(f"{header} is a LIST of ingredients")
            ingredients_insert_text = create_sql_insert_ingredients_array_text(entry[header])
            data = data + ingredients_insert_text
            pprint(entry[header])
            print(f"\n - - - - i - - - - \n{ingredients_insert_text}\n - - - - i - - - - ")
        
        elif header == 'yield':
            print(f"{header} is a NUMBER in g")            
            data = data + f"{entry[header].rstrip('g')}, "
        
        elif header == 'allergens' or header == 'tags':
            print(f"{header} is a LIST of tags / strings")
            tag_to_insert = create_sql_insert_tags_array_text(entry[header])
            data = data + tag_to_insert
            
        else:
            print(f"{header} is a STRING")
            data = data + f"'{entry[header]}', "
    
    
    data = data.rstrip(', ') + ")"
    
    fields = fields.rstrip(', ') + ")"
    
    sql_string = f"{sql_string} {fields} VALUES {data};"
    
    print(sql_string)
    db.execute(sql_string)
    db.commit()
    
    #INSERT INTO recipes (rcp_id, image_filename, recipe_title, txt_ingredient_file, n_En, n_Fa, n_Fs, n_Fm, n_Fp, n_Fo3, n_Ca, n_Su, n_Fb, n_St, n_Pr, n_Sa, n_Al, serving_size) VALUES ('0', '20181226_174632_crispy prawn and vegetable risotto.jpg', 'crispy prawn and vegetable risotto', '20181226_174632_crispy prawn and vegetable risotto.txt', '137', '6.97', '2.74', '3.05', '0.51', '0.0', '11.83', '2.03', '1.02', '0.18', '6.96', '1.01', '0.0', '466');
    #INSERT INTO recipes (rcp_id, image_filename, recipe_title, serving_size) VALUES ('0', '20181226_174632_crispy prawn and vegetable risotto.jpg', 'crispy prawn and vegetable risotto', '20181226_174632_crispy prawn and vegetable risotto.txt', '137', '6.97', '2.74', '3.05', '0.51', '0.0', '11.83', '2.03', '1.02', '0.18', '6.96', '1.01', '0.0', '466');
    #INSERT INTO recipes (rcp_id, image, title, text_file, n_En, n_Fa, serving_size) VALUES (0, '20181226_174632_crispy prawn and vegetable risotto.jpg', 'crispy prawn and vegetable risotto', '20181226_174632_crispy prawn and vegetable risotto.txt', 137, 6.97, 466)
    #INSERT INTO recipes (rcp_id, image, title, text_file) VALUES (0, '20181226_174632_crispy prawn and vegetable risotto.jpg', 'crispy prawn and vegetable risotto', '20181226_174632_crispy prawn and vegetable risotto.txt');

def create_table_in_database_from_sql_template(data_base, template_file):
    create_table_sql_command = ''
    
    with open(template_file) as sql_template:
        create_table_sql_command = sql_template.read()
        
    db_lines = data_base.execute(create_table_sql_command)    
    data_base.commit()
    
    return(db_lines)


def drop_tables_for_fresh_start(data_base, tables):
        
    for table in tables:
        sql_command = f"DROP TABLE IF EXISTS {table};"
        
        print(f"SQL cmd: {sql_command} <")

        data_base.execute(sql_command)    
        data_base.commit()
    
    return


def main():
    # execute this query
    # SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;
    #db_lines = db.execute("SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;").fetchall()    
    #db_lines = db.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES").fetchall()
    #db_lines = db.execute("SHOW TABLES").fetchall() #msyql    
    #db_lines = db.execute('SELECT * FROM sal_emp').fetchall()  # work fine
    
    force_drop_tables = True # False
    
    if (force_drop_tables == True or force_complete_rebuild == True):
        # DROP TABLES
        drop_tables_for_fresh_start(db, ['recipes','exploded','atomic_ingredients'])
    
    
    # create recipes table
    sql_template = '/Users/simon/a_syllabus/lang/python/repos/mysql_python/static/recipe_table_def.sql'    
    db_lines = create_table_in_database_from_sql_template(db, sql_template)        
    print(db_lines)

    # create exploded recipes table
    sql_template = '/Users/simon/a_syllabus/lang/python/repos/mysql_python/static/recipe_exploded_table_def.sql'
    db_lines = create_table_in_database_from_sql_template(db, sql_template)        
    print(db_lines)
    
    # create ingredients table
    sql_template = '/Users/simon/a_syllabus/lang/python/repos/mysql_python/static/atomic_ingredients_table_def.sql'
    db_lines = create_table_in_database_from_sql_template(db, sql_template)        
    print(db_lines)


    # http-server -p 8000 --cors
    # url_file = 'http://192.168.0.8:8000/static/sql_recipe_data.csv'
    url_file = 'http://127.0.0.1:8000/static/sql_recipe_data.csv'
    
    sql_dict = get_csv_from_server_as_disctionary(url_file)

    print(sql_dict.__class__.__name__)



    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    # go through the CSV file of rows of recipes - parse and load data 
    for entry in sql_dict:
        print(f"> > > > ENTRY:{entry} {type(entry)}* * * * * * * * * * * * * * * * ")
        print(f"> > > > RECIPE: * * * * * * * * * * * * * * * * S")        
        pprint(sql_dict[entry])
        print(f"> > > > RECIPE: {type(sql_dict[entry]['ri_id'])} * * * * * * * * * * * * * * * * M1")
        
        sql_row = sql_dict[entry]
        
        ri_id = int(sql_row['ri_id'])   # TOP level / master recipe ID - the ID in the CSV row!
        
        print(f"> > > > SQL_ROW: C:{type(sql_row)} {sql_row['text_file']} - {sql_row['ri_name']} * * * * * * * * * * * * * * * * M - - -")
        pprint(sql_row)
        # create list of recipes (headline & sub components) to add into database
        
        recipes_from_id = create_list_of_recipes_and_components_from_recipe_id(sql_row)
        
        headline_recipe = ''
        
        for recipe in recipes_from_id:
            if 'ri_id' in recipe:                            # create an empty dictionary - make more robust
                if int(recipe['ri_id']) == ri_id:
                    headline_recipe = recipe
                    break
            
        print(f"> > > > RECIPE: {type(sql_dict[entry]['ri_id'])} * * * * * * * * * * * * * * * * M2")
        pprint(headline_recipe)
        print(f"> > > > RECIPE: * * * * * * * * * * * * * * * * E")
        
        #should put some exception handling around this    
        for recipe in recipes_from_id:
           create_entry_in_db(db, 'recipes', recipe)

    
    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==
    print(f"> > > > E X P L O D E - E X P L O D E - E X P L O D E - E X P L O D E - <    <    <    <    <    <    <    <    <")
    #     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -     -==

    for entry in sql_dict:

        sql_row = sql_dict[entry]    
                
        exploded = create_exploded_recipe(sql_row)
                
        #print(f"> > > > E X P L O D  E D: {exploded['ri_name']} {type(exploded)} <    <    <    <    <    <    <    <    <     *")        
        pprint(exploded)
        
        for ex_rcp in exploded:
            create_entry_in_db(db, 'exploded', ex_rcp )


if __name__ == '__main__':
    main()
    # with PyCallGraph(output=graphviz, config=config):
    #     main()
