#! /usr/bin/env python

# loads csv file from server and loads into database LIVE


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
# sessions
# https://docs.sqlalchemy.org/en/latest/orm/session_basics.html


# giza a look
from pprint import pprint
# for regex
import re

import urllib.parse                     # sed to parse passwords into url format
url_encoded_pwd = urllib.parse.quote_plus("kx%jj5/g")

print("----- list.py ------------------------------------------------------------ importing")

from load_csv import get_csv_from_server_as_disctionary 
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
engine = create_engine('mysql://root:meepmeep@localhost:3306/recipe_cs50')

db = scoped_session(sessionmaker(bind=engine))

pprint(engine)

# If there are many levels of recursion, and you don't want to see them all
# you can use the depth parameter to limit how many levels it goes down
#pprint(engine, depth=2)

def create_entry_in_db(db, table, entry):
    print(f"----- list.py: create_entry_in_db ------------------------------------------------------------ ")
    print(f"----- table:{table} <> recpipe:{entry['title']} ------------------------------------------------------------ ")
    
    sql_string = f"INSERT INTO {table}"
    fields = "("
    data =  "("
    for header in entry:
        print(f"{header} = {entry[header]} - class:{entry[header].__class__.__name__}")
        fields = fields + f"{header}, "
        
        if header == 'rcp_id' or header == 'serving_size':
            print(f"{header} is an INT NUMBER")
            data = data + f"{entry[header]}, "        
        
        elif re.match(r'n_\w+', header ):
            print(f"{header} is a NUMBER")
            data = data + f"{entry[header]}, "
        
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

def main():
    # execute this query
    # SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;
    #db_lines = db.execute("SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;").fetchall()
    
    #db_lines = db.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES").fetchall()
    db_lines = db.execute("SHOW TABLES").fetchall()
    
    formatted_text = "\n"
    
    for line in db_lines:
        #print(f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | ")
        #formatted_text = formatted_text + f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | \n"
        print(line)
    
    print(f"\n\nProcess Query {formatted_text}")
        
    print(f"\n\nHello World > {engine} <")


    url_file = 'http://192.168.0.8:8000/static/sql_recipe_data.csv'
    
    sql_dict = get_csv_from_server_as_disctionary(url_file)

    print(sql_dict.__class__.__name__)
    
    info = {}

    for entry in sql_dict:
        print(f"> > > > ENTRY:{entry} * * * * * * * * * * * * * * * * ")
        #pprint(sql_dict[entry])
        
        for key in sql_dict[entry]:
            #print(f"{key} = {sql_dict[entry][key]}")
            info[key] = sql_dict[entry][key]
        
        # should put some exception handling around this    
        create_entry_in_db(db, 'recipes', info)
        
    
    


if __name__ == '__main__':
    main()
