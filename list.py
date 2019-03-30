#! /usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# giza a look
from pprint import pprint

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


if __name__ == '__main__':
    main()
