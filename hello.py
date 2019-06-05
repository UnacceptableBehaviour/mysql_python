#! /usr/bin/env python

from flask import Flask, render_template, request
app = Flask(__name__)

# dev remove
from helpers import get_csv_from_server_as_disctionary, get_nutirents_for_redipe_id #, create_recipe_info_dictionary
from helpers_db import get_all_recipe_ids, get_gallery_info_for_display_as_list_of_dicts, get_single_recipe_from_db_for_display_as_dict, get_recipes_for_display_as_list_of_dicts, toggle_filter


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

# add persistence until sessions implemented
data = {}
data['tags'] = ['vegan', 'veggie', 'cbs', 'chicken', 'pork', 'beef', 'seafood', 's&c', 'gluten_free', 'ns_pregnant']
data['chosen_tag_filters'] = ['vegan', 'veggie', 'cbs']
data['chosen_tag_filters_string'] = ', '.join(data['chosen_tag_filters'])

data['allergens'] = ['dairy', 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'molluscs', 's&c', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide']

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
    
    # do this in pages when larger db - use JS to reload
    ri_ids = get_all_recipe_ids() # get_next_page_recipe_ids()
    
    recipes = get_gallery_info_for_display_as_list_of_dicts(ri_ids)

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \\")
    pprint(recipes)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")
          
    #return render_template('data_return.html', lines=db_lines)
    return render_template('gallery.html', recipes=recipes)


@app.route('/twonky_donuts', methods=["GET", "POST"])
def buttons_inputs():
    headline_py = "Sending data back . . ."
    recipes = []
    rx = '*'
    rxD = '*'
    arr_get = ['A','B','C','D']
    arr_post = ['L','M','N','O']
        
    incoming_dict = request.args.to_dict()          # for method=GET - contents of query string which is part of URL after question mark 
    print(f">-----> requesting: {type(request)}")
    pprint(incoming_dict)
    
    if request.method =='GET':
        #rx = request.form["var_in_url_g"]
        rx = request.form.get("var_in_url_g") # NO WORK - USE dictionary for GET - this for POST only?
        
        if 'var_in_url_g' in incoming_dict:
            rxD = incoming_dict['var_in_url_g']
        
        bt_val = request.form.get("button_p")

        for key, val in incoming_dict.items():
            print(f"GET k: {key} - v: {val} <")
            if re.match(r'btn_arr_', key):
                print("MATCH")
                data['button_keypad_GET'] = arr_get[int(val)]     # you can only press one button at a time!
        
        print(f"GET request.form.get: {rx}")
        print(f"GET rxD = incoming_dict['var_in_url_p']: {rxD}")
        print(f"GET request.form.get( button_g ): {bt_val}")
        pprint(incoming_dict)


    if request.method =='POST':
        rx = request.form.items()
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - *-* \\")
        pprint(request.form)
        print(f"rx['tag_btn_create']{type(rx)}")
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")         
        
        for key, val in request.form.items():
            print(f"POST k: {key} - v: {val} <")
            
            if key == 'create_tag_button' and val != '':
                print(f"MATCH - ADDING: {val} to TAGS")
                new_tag = val.lower().replace(" ", "_")
                data['tags'].append(new_tag)
                data['chosen_tag_filters'].append(new_tag)
                
            
            # process button array POST
            if re.match(r'btn_arr_', key):
                print("MATCH - but ARR")
                data['button_keypad_POST'] = arr_post[int(val)]     # you can only press one button at a time!
            
            # process TAG buttond
            if re.match(r'tag_btn_', key):                
                tag_filter = key.replace('tag_btn_', '')
                toggle_filter(data['chosen_tag_filters'], tag_filter)
                data['chosen_tag_filters_string'] = ', '.join(data['chosen_tag_filters'])
                print(f"MATCH - but TAG: {data['chosen_tag_filters_string']}")

            
            


        #if 'var_in_url_p' in incoming_dict:         # use for GET
        #    rxD = incoming_dict['var_in_url_p']
        
        bt_val = request.form.get("button_p")
        
        print(f"POST request.form: {type(rx)}")
        print(f"POST request.form: {rx}")
        print(f"POST rxD = incoming_dict['var_in_url_p']: {rxD}")
        print(f"POST request.form.get( button_p ): {bt_val}")
        pprint(incoming_dict)
        
    data['data'] = f"POST: {rx} - dict:{rxD}"
    
    print(f">-----> rendering: {data}")
    
    return render_template('buttons_and_inputs.html', headline=headline_py, data=data, recipes=recipes)

    
@app.route('/buton_1', methods=["GET", "POST"])
def button_1():
    return render_template('data_return.html', lines=[f"BUTTON 1"])
    #return f"<h1>BUTTON 1</h1>"

@app.route('/buton_2', methods=["GET", "POST"])
def button_2():
    return render_template('data_return.html', lines=[f"BUTTON 2"])

@app.route('/buton_3', methods=["GET", "POST"])
def button_3():
    headline_py = 'Page title . .'
    recipes = []    
    return render_template("data_return.html", headline=headline_py, recipes=recipes, lines=[f"BUTTON 3"])

@app.route('/buton_4', methods=["GET", "POST"])
def button_4():    
    return render_template('data_return.html', lines=[f"BUTTON 4"])

@app.route('/buton_5', methods=["GET", "POST"])
def button_5():    
    return render_template('data_return.html', lines=[f"BUTTON 5"])

@app.route('/db_nutrients', methods=["GET", "POST"])
def db_nutrients():    
    headline_py = 'Nutrients from PostgreSQL'
    
    ri_id = 3301

    recipe = get_single_recipe_from_db_for_display_as_dict(ri_id)

    recipes = [recipe]

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - *-* \\")
    pprint(recipes)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")    
    
    return render_template("nutrient_traffic_lights_page.html", headline=headline_py, recipes=recipes)


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

    recipes = get_recipes_for_display_as_list_of_dicts( [BEEF_BRISKET_BROTH, LEMON_GRASS_CHICKEN] )
    
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - *-* \\")
    pprint(recipes)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")
    
    headline_py = "Compare Nutrients fetch from DB"
    
    return render_template("nutrient_compare_page.html", headline=headline_py, recipes=recipes)



@app.route('/db_recipe_page', methods=["GET", "POST"])
def db_recipe_page():
    
    if request.method =='POST':    
        for key, val in request.form.items():
            print(f"POST k: {key} - v: {val} <")
            if re.match(r'gallery_button_', key):
                ri_id = int(val)
    
    else:
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

    headline_py = "single recipe page"
    
    recipe = get_single_recipe_from_db_for_display_as_dict(ri_id)
    
    recipes = [recipe]
    
    return render_template("recipe_page.html", headline=headline_py, recipes=recipes)


@app.route('/buton_7', methods=["GET", "POST"])
def button_7():    
    return render_template('data_return.html', lines=[f"BUTTON 7"])


@app.route('/diary_w_image', methods=["GET", "POST"])
def diary_w_image_snap():
    
    headline_py = 'Record diary entry w/ image . .'
    recipes = []
    
    return render_template("image_capture.html", headline=headline_py, recipes=recipes)


if __name__ == '__main__':
    # https://pythonprogramminglanguage.com/flask-hello-world/
    # reserved port numbers
    # https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
    #app.run(host='0.0.0.0', port=50015)
    
    # setting up SSL for image capture:
    # https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
    # pip install pyOpenSSL
    app.run(host='192.168.0.8', port=50015, ssl_context='adhoc')
    
    # Note for deployment:
    # http://flask.pocoo.org/docs/1.0/deploying/#deployment
