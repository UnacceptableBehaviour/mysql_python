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

    return render_template('data_return.html', lines=db_lines)

    #return f"Processed Query:<br>{formatted_text} <br>END"
    
@app.route('/buton_1', methods=["GET", "POST"])
def button_1():
    return render_template('data_return.html', lines=[f"BUTTON 1"])
    #return f"<h1>BUTTON 1</h1>"

@app.route('/buton_2', methods=["GET", "POST"])
def button_2():
    return render_template('data_return.html', lines=[f"BUTTON 2"])


@app.route('/buton_3', methods=["GET", "POST"])
def button_3():    
    return render_template('data_return.html', lines=[f"BUTTON 3"])

@app.route('/buton_4', methods=["GET", "POST"])
def button_4():    
    return render_template('data_return.html', lines=[f"BUTTON 4"])

@app.route('/buton_5', methods=["GET", "POST"])
def button_5():    
    return render_template('data_return.html', lines=[f"BUTTON 5"])

@app.route('/buton_6', methods=["GET", "POST"])
def button_6():    
    return render_template('data_return.html', lines=[f"BUTTON 6"])

@app.route('/buton_7', methods=["GET", "POST"])
def button_7():    
    return render_template('data_return.html', lines=[f"BUTTON 7"])




if __name__ == '__main__':
    main()
