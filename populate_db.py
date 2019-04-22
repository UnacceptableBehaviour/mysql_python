#! /usr/bin/env python

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

print("----- populate_asset_server.rb ----------------------------------------- ASSET SERVER POPLATION FEEDBACK - S")

#population_data = subprocess.check_output(['populate_asset_server.rb'])
print('COMMENTED OUT - NOT EXECUTING populate_asset_server.rb  * * * * * WARNING <')

#pprint(population_data)
pprint(engine)

print("----- populate_asset_server.rb ----------------------------------------- ASSET SERVER POPLATION FEEDBACK - E")


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


def create_entry_in_db(db, table, entry):

    print(f"----- list.py: create_entry_in_db ------------------------------------------------------------ ")
    print(f"----- table:{table} <> recipe: {entry['ri_name']} -------------------------------------------- ")
    print(f"----- ingredients:{entry['ingredients']} \n-------------------------------------------- ")
    
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



def main():
    # execute this query
    # SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;
    #db_lines = db.execute("SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;").fetchall()    
    #db_lines = db.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES").fetchall()
    #db_lines = db.execute("SHOW TABLES").fetchall() #msyql    
    #db_lines = db.execute('SELECT * FROM sal_emp').fetchall()  # work fine 
    
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

    formatted_text = "\n"
    
    # for line in db_lines:
    #     #print(f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | ")
    #     #formatted_text = formatted_text + f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | \n"
    #     print(line)
    # 
    # print(f"\n\nProcess Query {formatted_text}")
    #     
    # print(f"\n\nHello World > {engine} <")

    # http-server -p 8000 --cors
    url_file = 'http://192.168.0.8:8000/static/sql_recipe_data.csv'
    
    sql_dict = get_csv_from_server_as_disctionary(url_file)

    print(sql_dict.__class__.__name__)

    # for entry in sql_dict:
    #     print(f"> > > > ENTRY:{entry} {type(entry)}* * * * * * * * * * * * * * * * ")
    #     print(f"> > > > RECIPE: * * * * * * * * * * * * * * * * S")
    #     
    #     pprint(sql_dict[entry])
    #     print(f"> > > > RECIPE: {type(sql_dict[entry]['ri_id'])} * * * * * * * * * * * * * * * * M1")
    #     
    #     sql_row = sql_dict[entry]
    #     
    #     #ri_id = int(sql_row['ri_id'])
    #     
    #     print(f"> > > > SQL_ROW: C:{type(sql_row)} {sql_row['text_file']} - {sql_row['ri_name']} * * * * * * * * * * * * * * * * M - - -")
    #     pprint(sql_row)
    #     # create list of recipes (headline & sub components) to add into database
    #     
    #     recipes_from_id = create_list_of_recipes_and_components_from_recipe_id(sql_row)
    #     
    #     headline_recipe = ''
        
        # for recipe in recipes_from_id:
        #     if 'ri_id' in recipe:                                  # create an empty dictionary - make more robust
        #         if int(recipe['ri_id']) == ri_id:
        #             headline_recipe = recipe
        #             break
            
        #print(f"> > > > RECIPE: {type(sql_dict[entry]['ri_id'])} * * * * * * * * * * * * * * * * M2")
        #pprint(headline_recipe)
        #print(f"> > > > RECIPE: * * * * * * * * * * * * * * * * E")
        
        # should put some exception handling around this    
        #for recipe in recipes_from_id:
        #    create_entry_in_db(db, 'recipes', recipe)
    
    print(f"> > > > E X P L O D E - E X P L O D E - E X P L O D E - E X P L O D E - <    <    <    <    <    <    <    <    <")
    
    for entry in sql_dict:
        if int(entry) != 13:
            continue

        sql_row = sql_dict[entry]    
                
        exploded = create_exploded_recipe(sql_row)
        
        if int(entry) == 13:
            break
        
        #print(f"> > > > E X P L O D  E D: {exploded['ri_name']} {type(exploded)} <    <    <    <    <    <    <    <    <     *")        
        #pprint(exploded)
        #for recipe in recipes_from_id:
        #    create_entry_in_db(db, 'recipes', recipe)


if __name__ == '__main__':
    main()
