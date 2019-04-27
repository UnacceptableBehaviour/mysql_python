#! /usr/bin/env python

from flask import Flask, render_template, request
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# giza a look
from pprint import pprint

import urllib.parse
url_encoded_pwd = urllib.parse.quote_plus("kx%jj5/g")

import re

# default
#engine = db.create_engine('dialect+driver://user:pass@host:port/db')
#engine = create_engine('mysql://root:meepmeep@localhost:3306/nutridb_sr25_sanitized')
engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different
db = scoped_session(sessionmaker(bind=engine))


# to update asset server and postgreSQL db with current assets
# run 'populate_db.py'
# each app.route is an endpoint
@app.route('/')
def hello_world():
    # execute this query
    # SELECT yield, servings, ri_name, image_file FROM exploded WHERE image_file <> '';
    db_lines = db.execute("SELECT yield, servings, ri_name, image_file FROM exploded WHERE image_file <> '';").fetchall()
    
    formatted_text = "<br>"
    
    for line in db_lines:
        pprint(line)
        #print(f" | {round(line.yield, 0)} | {round(line.servings, 0)} | {line.ri_name} | {line.image_file} | <br>")
        #formatted_text = formatted_text + f" | {int(line.yield)} | {int(line.servings)} | {line.ri_name} | {line.image_file} | <br>"
    
    print(f"\n\nProcess Query\n{formatted_text}\n")
    
    #return render_template('data_return.html', lines=db_lines)
    return render_template('show_all_recipe_images.html', recipes=db_lines)
    
    
    #return f"Processed Query:<br>{formatted_text} <br>END"


@app.route('/gallery')
def gallery():
    # execute this query
    # SELECT yield, servings, ri_name, image_file FROM exploded WHERE image_file <> '';
    
    fields = ['ri_id', 'ri_name', 'image_file']
    
    db_lines = db.execute("SELECT ri_id, ri_name, image_file FROM exploded WHERE image_file <> '';").fetchall()
    #db_lines = db.execute("SELECT * FROM exploded WHERE image_file <> '';").fetchall()
        
    recipes = []
    
    for line in db_lines:
        rcp = {}        
        for index, content in enumerate(line):        
            rcp[fields[index]] = content            

        print( f"\nQRY Line{line}" )            
        pprint(rcp)
        print("----------------------^^")

        recipes.append(rcp)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \\")
    pprint(recipes)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")
          
    #return render_template('data_return.html', lines=db_lines)
    return render_template('gallery.html', recipes=recipes)

    
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
def nutrients():    
    headline_py = 'Nutrients from PostgreSQL'
    info = {}   # test undefined
    #  // struct / JSON
    nutrients = {
      'ri_id': 6,
      'ri_name': 'Light Apricot Cous Cous',
      'n_En': 154.0,
      'n_Fa': 3.12,
      'n_Fs': 1.33,
      'n_Su': 2.93,
      'n_Sa': 0.58,
      'serving_size': 190.0
    };
    
    #info = get_nutrients_per_serving()
    fields = ['ri_id','ri_name','n_En','n_Fa','n_Fs','n_Su','n_Sa','serving_size']
    qry_string = ', '.join(fields)

    #db_lines = db.execute("SELECT ri_id, ri_name, image_file FROM exploded WHERE image_file <> '';").fetchall()
    db_lines = db.execute(f"SELECT {qry_string} FROM exploded WHERE image_file <> '';").fetchall()
        
    recipes = []
    
    
    for line in db_lines:
        rcp = {}        
        for index, content in enumerate(line):
            print( f"\nQRY Line{line} {type(line)}\nC:{content} - {type(content)}<" )
            
            type_string = str(type(content))

            if type_string == "<class 'decimal.Decimal'>":
                
                rcp[fields[index]] = round(float(content),2)

                # print("--WTF-------------")
                # bl = (type_string == "<class 'decimal.Decimal'>")
                # pprint(bl)
                # print("^-bool-^")
                # pprint(type_string)
                # pprint("<class 'decimal.Decimal'>")
                # pprint(str(type(content)))
                # pprint(type(content))
                # pprint(content)
                # pprint(str(content))
                # pprint(int(content))
                # pprint(round(float(content),2))
                # print("--WTF-------------")

            else:
                rcp[fields[index]] = content

                #print(f"GP-X{content} - {str(type(content))} - TS:{type_string}")




        print( f"\nQRY Line{line}" )                    
        nutrients = rcp
        pprint(nutrients)
        print("----------------------^^")

        recipes.append(rcp)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \\")
    pprint(recipes)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")
    

    
    #return render_template("nutrient_traffic_lights_page.html", headline=headline_py, info=info)
    return render_template("nutrient_traffic_lights_page.html", headline=headline_py, info=nutrients)
    #return render_template('data_return.html', lines=[f"BUTTON 7"])

@app.route('/buton_7', methods=["GET", "POST"])
def button_7():    
    return render_template('data_return.html', lines=[f"BUTTON 7"])




if __name__ == '__main__':
    # https://pythonprogramminglanguage.com/flask-hello-world/
    # reserved port numbers
    # https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
    app.run(host='0.0.0.0', port=50001)
    
    # Note for deployment:
    # http://flask.pocoo.org/docs/1.0/deploying/#deployment
