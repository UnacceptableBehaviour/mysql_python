#! /usr/bin/env python

from flask import Flask, render_template, request
app = Flask(__name__)

# dev remove
from helpers import get_csv_from_server_as_disctionary, get_nutirents_for_redipe_id #, create_recipe_info_dictionary


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# giza a look
from pprint import pprint

import urllib.parse
url_encoded_pwd = urllib.parse.quote_plus("kx%jj5/g")

import re

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# to UPDATE ASSET SERVER and postgreSQL DB with current assets
# run 'populate_db.py'
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# default
#engine = db.create_engine('dialect+driver://user:pass@host:port/db')
#engine = create_engine('mysql://root:meepmeep@localhost:3306/nutridb_sr25_sanitized')
engine = create_engine('postgresql://simon:@localhost:5432/cs50_recipes')  # database name different
db = scoped_session(sessionmaker(bind=engine))



# each app.route is an endpoint
@app.route('/')
def db_hello_world():
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


@app.route('/db_gallery')
def db_gallery():
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

@app.route('/db_nutrients', methods=["GET", "POST"])
def db_nutrients():    
    headline_py = 'Nutrients from PostgreSQL'
    info = {}   # test undefined
    #  // struct / JSON
    # nutrients = {
    #   'ri_id': 6,
    #   'ri_name': 'Light Apricot Cous Cous',
    #   'n_En': 154.0,
    #   'n_Fa': 3.12,
    #   'n_Fs': 1.33,
    #   'n_Su': 2.93,
    #   'n_Sa': 0.58,
    #   'serving_size': 190.0
    # };
    
    #info = get_nutrients_per_serving()
    fields = ['ri_id','ri_name','n_En','n_Fa','n_Fs','n_Su','n_Sa','serving_size']
    qry_string = ', '.join(fields)

    db_lines = db.execute(f"SELECT {qry_string} FROM exploded WHERE image_file <> '';").fetchall()
        
    recipes = []
        
    for line in db_lines:
        rcp = {}        
        for index, content in enumerate(line):
            #print( f"\nQRY Line{line} {type(line)}\nC:{content} - {type(content)}<" )            
            type_string = str(type(content))

            if type_string == "<class 'decimal.Decimal'>":                
                rcp[fields[index]] = round(float(content),2)

            else:
                rcp[fields[index]] = content

        nutrients = rcp
        recipes.append(rcp)
        
        #print( f"\nQRY Line{line}" )                    
        #pprint(nutrients)
        #print("----------------------^^")

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \\")
    pprint(recipes[4])
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")
    

    
    #return render_template("nutrient_traffic_lights_page.html", headline=headline_py, info=info)
    return render_template("nutrient_traffic_lights_page.html", headline=headline_py, info=nutrients)
    #return render_template('data_return.html', lines=[f"BUTTON 7"])


@app.route('/db_nutrients_compare')
def db_nutrients_compare():
    BEEF_BRISKET_BROTH = 3402
    LEMON_GRASS_CHICKEN = 2001
    
    nutrients_0 = get_nutirents_for_redipe_id(db, BEEF_BRISKET_BROTH)
    nutrients_1 = get_nutirents_for_redipe_id(db, LEMON_GRASS_CHICKEN)

    # nutrients_0 = {
    #   'ri_id': 6,
    #   'ri_name': 'Light Apricot Cous Cous',
    #   'n_En': 154.0,
    #   'n_Fa': 3.12,
    #   'n_Fs': 1.33,
    #   'n_Su': 2.93,
    #   'n_Sa': 0.58,
    #   'serving_size': 190.0
    # };
        
    headline_py = "Compare Nutrients"
    return render_template("nutrient_compare_page.html", headline=headline_py, info_0=nutrients_0, info_1=nutrients_1)




@app.route('/db_recipe_page', methods=["GET", "POST"])
def db_recipe_page():
    
    ri_id = 2403 # loaded by GET below
    
    incoming_dict = request.args.to_dict()
    
    if request.method =='GET':
        print("GET                            - - - < db_recipe_page")        
        pprint(incoming_dict)
        if 'text' in incoming_dict:
            ri_id = int(incoming_dict['text'])
        
    if request.method =='POST':
        print("POST                            - - - < db_recipe_page")
        pprint(request.args.to_dict())


    sql_dict = get_csv_from_server_as_disctionary()    
    # ri_id = 23
    # updated_info = create_recipe_info_dictionary(sql_dict, 23)
    # 
    headline_py = f"Recipe Page"

    updated_info = {}   # test undefined
    #  // struct / JSON
    # updated_info = {
    #   'ri_id': 6,
    #   'ri_name': 'Light Apricot Cous Cous',
    #   'n_En': 154.0,
    #   'n_Fa': 3.12,
    #   'n_Fs': 1.33,
    #   'n_Su': 2.93,
    #   'n_Sa': 0.58,
    #   'serving_size': 190.0
    #   'ingredients' : ['10g', 'chicken stock cube'], ['20g', '(2)', 'cherry tomatoes'], ['10g', 'spring onion'], ['1g', 'coriander'], ['274g', 'water']]
    # };
    
    #info = get_nutrients_per_serving()
    fields = ['ri_id','ri_name','n_En','n_Fa','n_Fs','n_Su','n_Sa','serving_size', 'ingredients', 'image_file']    
    qry_string = ', '.join(fields)
    #ri_id = 2403 # loaded by GET
    
    #sql_query = f"SELECT {qry_string} FROM exploded WHERE image_file <> '' AND ri_id = {ri_id};"
    sql_query = f"SELECT {qry_string} FROM recipes WHERE image_file <> '' AND ri_id = {ri_id};"
    #sql_query = f"SELECT {qry_string} FROM exploded WHERE image_file <> '' AND ri_name LIKE '%crab cakes mango salsa%';"
    
    #db_lines = db.execute(f"SELECT {qry_string} FROM exploded WHERE image_file <> '';").fetchall()
    db_lines = db.execute(sql_query).fetchall()
    
    for line in db_lines:
        rcp = {}        
        for index, content in enumerate(line):
            #print( f"\n--->? QRY Line{line}\nT: {type(line)}" )
            #print( f"\nC:{content} - {type(content)}<" )            
            type_string = str(type(content))
    
            if type_string == "<class 'decimal.Decimal'>":                
                rcp[fields[index]] = round(float(content),2)
    
            else:
                rcp[fields[index]] = content
    
        updated_info = rcp
    
    pprint(db_lines)
        
    recipes = []
        
    #return render_template("recipe_page.html", headline=headline_py, info=updated_info, image_dict=sql_dict)
    #return render_template("recipe_page.html", headline=headline_py, info=updated_info, image_dict=sql_dict)
    return render_template("recipe_page.html", headline=headline_py, info=updated_info)


@app.route('/buton_7', methods=["GET", "POST"])
def button_7():    
    return render_template('data_return.html', lines=[f"BUTTON 7"])




if __name__ == '__main__':
    # https://pythonprogramminglanguage.com/flask-hello-world/
    # reserved port numbers
    # https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
    app.run(host='0.0.0.0', port=50015)
    
    # Note for deployment:
    # http://flask.pocoo.org/docs/1.0/deploying/#deployment
