from flask import Flask, render_template
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# giza a look
from pprint import pprint

import urllib.parse
url_encoded_pwd = urllib.parse.quote_plus("kx%jj5/g")


# default
#engine = db.create_engine('dialect+driver://user:pass@host:port/db')
engine = create_engine('mysql://root:meepmeep@localhost:3306/nutridb_sr25_sanitized')
db = scoped_session(sessionmaker(bind=engine))


# each app.route is an endpoint
@app.route('/')
def hello_world():
    # execute this query
    # SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;
    db_lines = db.execute("SELECT ndb_no, nutr_no, nutr_val, deriv_cd FROM nutrientdata ORDER BY nutr_val LIMIT 10;").fetchall()
 
    formatted_text = "<br>"
    
    for line in db_lines:
        #print(f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | ")
        formatted_text = formatted_text + f" | {line.ndb_no} | {line.nutr_no} | {line.nutr_val} | {line.deriv_cd} | <br>"
    
    print(f"\n\nProcess Query {formatted_text}")
    
    return f"Processed Query:<br>{formatted_text} <br>END"
    
    



if __name__ == '__main__':
    main()
