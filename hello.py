#! /usr/bin/env python

from flask import Flask, render_template, request, send_from_directory
from werkzeug import serving
import ssl

app = Flask(__name__)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# for file upload
import os
from flask import Flask, redirect, url_for #, flash # request,
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = app.instance_path.replace('instance', 'static/uploads')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# dev remove
from helpers import get_csv_from_server_as_disctionary #, create_recipe_info_dictionary

from timestamping import hr_readable_from_nix, roll_over_from_nix_time

from helpers_db import get_all_recipe_ids, get_gallery_info_for_display_as_list_of_dicts, get_single_recipe_from_db_for_display_as_dict
from helpers_db import get_recipes_for_display_as_list_of_dicts, toggle_filter, return_recipe_dictionary
from helpers_db import get_single_recipe_with_subcomponents_from_db_for_display_as_dict, add_ingredient_w_timestamp
from helpers_db import get_daily_tracker, commit_DTK_DB, bootstrap_daily_tracker_create
from helpers_db import get_user_devices, store_user_devices, commit_User_Devices_DB
from helpers_db import process_search
from helpers_db import get_user_info_dict_from_DB, update_user_info_dict, get_search_settings_dict
from helpers_db import helper_db_class_db # THE DATABASE  < - - - \
# / - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /
# to UPDATE ASSET SERVER and postgreSQL DB with current assets
# run 'populate_db.py'
# \ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - < 

from helpers_tracker import get_daily_tracker_from_DB, store_daily_tracker_to_DB, post_DTK_info_for_processing, post_interface_file
from helpers_tracker import get_DTK_info_from_processing, process_new_dtk_from_user, archive_dtk, dtk_timestamp_rolled_over

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# giza a look - debug
from pprint import pprint
import random
# debug - delete

import urllib.parse
url_encoded_pwd = urllib.parse.quote_plus("kx%jj5/g")

import re           # regex
import json         # JSON tools


# each app.route is an endpoint
@app.route('/')
def db_hello_world():

    all_recipes = helper_db_class_db.execute("SELECT yield, servings, ri_name, lead_image FROM recipes WHERE lead_image <> '';").fetchall()

    formatted_text = "<br>"

    # debug - delete
    firstN = 20
    db_lines = []
    for i in range(firstN):
        q_index = random.randint(0,len(all_recipes)-1)
        db_lines.append(all_recipes.pop(q_index))

    for line in db_lines:
        pprint(line)
        #print(f" | {round(line.yield, 0)} | {round(line.servings, 0)} | {line.ri_name} | {line.lead_image} | <br>")
        #formatted_text = formatted_text + f" | {int(line.yield)} | {int(line.servings)} | {line.ri_name} | {line.lead_image} | <br>"

    print(f"\n\nProcess Query - rendering {len(db_lines)} recipes. . \n{formatted_text}\n")

    #return render_template('data_return.html', lines=db_lines)
    return render_template('show_all_recipe_images.html', recipes=db_lines)
    #return f"Processed Query:<br>{formatted_text} <br>END"

# synch / login route
# load js that send devices uuid, user uuid, and most recent dtk (daily tracker)
# load most users most recent dtk from DB
# use the version w/ most recent last update (highest value)
#
# check dtk to see if we've passed the rollover point
#
# if passed the rollover
#   archive old one and create a fresh dtk
#   return for rendering with weigh_in route
#
# if not rollover dtk
#   process the new addition and return the data
#   return for rendering with tracker route
#
@app.route('/synch_n_route', methods=["GET", "POST"])
def query_status_w_js():

    if request.method == 'POST':
        tracker_post = request.get_json() # parse JSON into DICT
        uuid =  tracker_post['user']

        if ('fp' in tracker_post):
            fingerprint = tracker_post['fp']
            print(">FINGERPRINT- -- -- -- -- -- -- -- -- -- -- -- -- -- -\ ")
            pprint(fingerprint)
            print(">FINGERPRINT- -- -- -- -- -- -- -- -- -- -- -- -- -- -/ ")

            store_user_devices(uuid,fingerprint)
            commit_User_Devices_DB()

            print(">DEVICES- -- -- -- -- -- -- -- -- -- -- -- -- -- -\ ")
            pprint(get_user_devices(uuid))
            print(">DEVICES- -- -- -- -- -- -- -- -- -- -- -- -- -- -/ ")

        #pprint(dtk)

        if ( ('dtk' in tracker_post) and (tracker_post['dtk'] != None) ):
            dtk = tracker_post['dtk']

            # check for roll over key, if present archive dtk
            if ('dtk_rcp' in dtk) and ('dt_rollover' in dtk['dtk_rcp']):
                archive_dtk(dtk)

            # if it's rolled over issue a fresh dtk for the day
            if dtk_timestamp_rolled_over(dtk):
                dro = hr_readable_from_nix(dtk['dtk_rcp']['dt_rollover'])     # roll_over
                dts = hr_readable_from_nix(dtk['dtk_rcp']['dt_date'])         # creation date
                dlu = hr_readable_from_nix(dtk['dtk_rcp']['dt_last_update'])  # last update
                print(f"ROLLED OVER: {dro} <   TS: {dts} <    LUP: {dlu} <")

                new_day_dtk = bootstrap_daily_tracker_create(uuid)
                store_daily_tracker_to_DB(new_day_dtk)
                
                dtk_w_reroute = { 'route': '/weigh_in', 'dtk': new_day_dtk }

                return json.dumps(dtk_w_reroute), 200

            else:
                dro = hr_readable_from_nix(dtk['dtk_rcp']['dt_rollover'])     # roll_over
                dts = hr_readable_from_nix(dtk['dtk_rcp']['dt_date'])         # creation date
                dlu = hr_readable_from_nix(dtk['dtk_rcp']['dt_last_update'])  # last update
                print(f"SYNCH A: {dro} <   TS: {dts} <    LUP: {dlu} <")

                # TODO REMOVE - BOOTPATCH
                if dtk['dtk_rcp']['dt_rollover'] == 0:  #1572411612346
                    dtk['dtk_rcp']['dt_rollover'] = roll_over_from_nix_time(dtk['dtk_rcp']['dt_date'])

                dro = hr_readable_from_nix(dtk['dtk_rcp']['dt_rollover'])     # roll_over
                dts = hr_readable_from_nix(dtk['dtk_rcp']['dt_date'])         # creation date
                dlu = hr_readable_from_nix(dtk['dtk_rcp']['dt_last_update'])  # last update
                print(f"SYNCH B: {dro} <   TS: {dts} <    LUP: {dlu} <")


                updated_dtk_data = process_new_dtk_from_user(dtk)
                # TODO - should verfify this is valid data and not a null
                store_daily_tracker_to_DB(updated_dtk_data)

                dro = hr_readable_from_nix(updated_dtk_data['dtk_rcp']['dt_rollover'])     # roll_over
                dts = hr_readable_from_nix(updated_dtk_data['dtk_rcp']['dt_date'])         # creation date
                dlu = hr_readable_from_nix(updated_dtk_data['dtk_rcp']['dt_last_update'])  # last update
                print(f"SYNCH C: {dro} <   TS: {dts} <    LUP: {dlu} <")

                pprint(updated_dtk_data)

                print(f"UUID: {dtk['dtk_user_info']['UUID']}")

                dtk_w_reroute = { 'route': '/tracker', 'dtk': updated_dtk_data }

                return json.dumps(dtk_w_reroute), 200
        else:
            raise(Exception("POST to route: /synch_n_route - INVALID DATA"))
            return 404

    else:
        # render blank html, with simple JS to POST status
        return render_template('quick_synch.html')



@app.route('/weigh_in')
def weigh_in():
    dtk = get_daily_tracker_from_DB() # TODO uuid/session
    uuid = dtk['dtk_user_info']['UUID']

    # if it's rolled over archive and create a new dtk
    print(f"WEIGH IN Rollover:")
    if dtk_timestamp_rolled_over(dtk):
        archive_dtk(dtk)
        dtk = bootstrap_daily_tracker_create(uuid)
        store_daily_tracker_to_DB(dtk)

    # draw chart - in .js

    return render_template('weigh_in_t.html', daily_tracker=dtk)


@app.route('/twonky_donuts', methods=["GET", "POST"])
def buttons_inputs():
    headline_py = "Sending data back . . ."
    recipes = []
    rx = '*'
    rxD = '*'
    arr_get = ['A','B','C','D']
    arr_post = ['L','M','N','O']
    data = {}

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


# @app.route('/db_gallery/<int:year>/<int:month>/<title>')
# def db_gallery(year, month, title):
#     pass

@app.route('/db_gallery')
def db_gallery():

    # do this in pages when larger db - use JS to reload
    ri_ids = get_all_recipe_ids() # get_next_page_recipe_ids()

    # debug - delete
    firstN = 20
    rcp_ids_20_off = []
    for i in range(firstN):
        q_index = random.randint(0,len(ri_ids)-1)
        rcp_ids_20_off.append(ri_ids.pop(q_index))

    #recipes = get_gallery_info_for_display_as_list_of_dicts(ri_ids)  # show WHOLE DB!!! :/
    recipes = get_gallery_info_for_display_as_list_of_dicts(rcp_ids_20_off)  # show 20 random! :)
    # print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \\")
    # pprint(recipes)
    # pprint(rcp_ids_20_off)
    # print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")

    return render_template('gallery.html', recipes=recipes)



@app.route('/settings', methods=["GET", "POST"])
def settings():

    # POST route
    if request.method =='POST':
        settings = request.get_json() # parse JSON into DICT

        if 'user_info' in settings:
            print('/settings/POST:user_info:')
            pprint(settings['user_info'])

            # write settings to DB
            update_user_info_dict(settings['user_info'])

            # return all good
            return json.dumps({}), 201 # created

        else:
            # return - couldnt find user_info!??
            return json.dumps({}), 404


    # default_filters = { # ADDITIONS LIKELY - USER DEFINED ESPECIALLY
    #     'allergens': ['dairy', 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'molluscs', 'shellfish', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide'],
    #     'tags_inc': ['vegan', 'veggie', 'cbs', 'gluten_free'],
    #     'tags_exc': ['vegan', 'veggie', 'cbs', 'chicken', 'pork', 'beef', 'seafood', 'shellfish', 'gluten_free', 'ns_pregnant'],
    #     'type_inc': ['component', 'amuse', 'side', 'starter', 'fish', 'lightcourse', 'main', 'crepe', 'dessert', 'p4', 'cheese', 'comfort', 'low_cal', 'serve_cold', 'serve_rt', 'serve_warm', 'serve_hot'],
    #     'type_exc': [],
    #     'ingredient_exc': [] }

    user_info = get_user_info_dict_from_DB('014752da-b49d-4fb0-9f50-23bc90e44298')    
    user_info.pop('devices', None) # setting per device? - Use case multi users using one account different devices.

    sql_query = "SELECT DISTINCT unnest(type) AS all_types FROM recipes;"
    types = helper_db_class_db.execute(sql_query).fetchall()    # ret list of tuples [('serve_hot',),('serve_rt',),('lunchbox',), etc ]
    # print('=\ ')
    # pprint(types)
    types = [ t[0] for t in types if t[0].strip() ]   # remove blanks
    types.sort()
    for t in types: print(f"{t},",end="")
    print('=/ ')

    # source of buttons to populate with settings from default_filters
    user_info['tag_sets']['type_exc'] = types
    # TODO H - remove ['tag_sets']['type_inc'] and ['tag_sets']['tags_inc']
    # replace ['tag_sets']['type_exc'] with ['tag_sets']['type_all']
    # replace ['tag_sets']['tags_exc'] with ['tag_sets']['tags_all']
    user_info['tag_sets']['type_inc'] = types
    if (len(user_info['default_filters']['type_inc']) == 0) and (len(user_info['default_filters']['type_exc']) == 0):
        user_info['default_filters']['type_exc'] = types

    return render_template('settings_t.html', user_info=user_info)


last_search_result_recipes = {}

@app.route('/search', methods=["GET", "POST"])
def search_ingredient():
    global last_search_result_recipes # what the point of a global if it isn't implicitly global? TODO
    search = ''
    
    user_info = get_user_info_dict_from_DB('014752da-b49d-4fb0-9f50-23bc90e44298')

    # process search post - query database
    # get all recipes with search criterea
    if request.method == 'POST':
        search_request = request.get_json() # parse JSON into DICT

        if ('user' in search_request):
            uuid =  search_request['user']

        if ('search' in search_request):
            search = search_request['search']
            print("search_ingredient >>")
            pprint(search)
        else:
            raise('Come on!!')
        
        user_info = get_user_info_dict_from_DB(uuid)

        ri_ids = process_search(search, user_info['default_filters'])

        last_search_result_recipes = get_gallery_info_for_display_as_list_of_dicts(ri_ids)

        return json.dumps(last_search_result_recipes), 200

    else:
        print(f"search_ingredient: {request.method}")
        pprint(request)
        print("- - - - s_i:" )

        #ri_ids = [301,1101,1202,1701,2301,2501,2902,3301,3401]
        #recipes = get_gallery_info_for_display_as_list_of_dicts(ri_ids)
        dbg_user_info = dict(user_info) # duplicate so as not to interfere with 'db' (dev only)
        dbg_user_info.pop('tag_sets')
        pprint(dbg_user_info)

    # GET route                                     # TODO implement --\
    return render_template('search_t.html', recipes=last_search_result_recipes)


@app.route('/buton_2', methods=["GET", "POST"])
def button_2():
    return render_template('data_return.html', lines=[f"BUTTON 2"])

@app.route('/buton_3', methods=["GET", "POST"])
def button_3():
    headline_py = 'Page title . .'
    recipes = []
    return render_template("data_return.html", headline=headline_py, recipes=recipes, lines=[f"BUTTON 3"])



        # TRACK ITEMS
@app.route('/tracker', methods=["GET", "POST"])
def track_items():
    headline_py = 'track items..'

    if request.method == 'POST':
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - *-* \\")
        print("* * * TRACKER: data POSTED:")
        # check payload
        tracker_post = request.get_json() # parse JSON into DICT
        if ('dtk' in tracker_post):
            dtk = tracker_post['dtk']
            uuid =  tracker_post['user']

            dro = hr_readable_from_nix(dtk['dtk_rcp']['dt_rollover'])     # roll_over
            dts = hr_readable_from_nix(dtk['dtk_rcp']['dt_date'])         # creation date
            dlu = hr_readable_from_nix(dtk['dtk_rcp']['dt_last_update'])  # last update
            print(f"TRACKING POST ROv: {dro} <   TS: {dts} <    LUP: {dlu} <")

            updated_dtk_data = process_new_dtk_from_user(dtk)  # , uuid) contained in dtk
            # TODO - store runs twice on post!???? - ENABLE print dtk in store_daily_tracker_to_DB
            store_daily_tracker_to_DB(updated_dtk_data)
            pprint(updated_dtk_data)

            print(f"UUID: {uuid}")
        else:
            raise(Exception("POST to route: /tracker - INVALID DATA"))

        return json.dumps(updated_dtk_data), 200

    else:
        # TODO UUID awaresnes - username login etc
        dtk = get_daily_tracker_from_DB('014752da-b49d-4fb0-9f50-23bc90e44298') # < UUID
        dro = hr_readable_from_nix(dtk['dtk_rcp']['dt_rollover'])     # roll_over
        dts = hr_readable_from_nix(dtk['dtk_rcp']['dt_date'])         # creation date
        dlu = hr_readable_from_nix(dtk['dtk_rcp']['dt_last_update'])  # last update
        


    return render_template('track_items.html', daily_tracker=dtk)


@app.route('/diary_w_image', methods=["GET", "POST"])
def diary_w_image_snap():

    def_im = 'static/uploads/light_lunch.JPG'
    headline_py = 'Record diary entry w/ image . .'
    recipes = []
    files = []

    if request.method == 'POST':
        pprint(request)
        #files = request.files['file']

    print("> > > - - \ ")
    print(type(files))
    pprint(files)
    #print(f"IMAGE FROM CAPTURE = {file[0]}")
    print("> > > - - / ")


    return render_template("image_capture.html", headline=headline_py, recipes=recipes, mobi=def_im)


# upload support - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# upload support - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@app.route('/uload_img_test', methods=["GET", "POST"])
def upload_image_test():

    files = []

    # snippet lifted from
    # http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        rx_file = request.files['file']

        if 'file_from_html' in request.files:
            print('file_from_html in: request.files')
            rx_file = request.files['file_from_html']

        # if user does not select file, browser also
        # submit a empty part without filename
        if rx_file.filename == '':
            print('No selected file')
            return redirect(request.url)

        if rx_file and allowed_file(rx_file.filename):
            filename = secure_filename(rx_file.filename)

            print(f"COPYING {filename} TO:")
            full_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(full_filepath)

            rx_file.save(full_filepath)
            #os.rename("from","to")

            files.append(filename)

            for f in files:
                print(f"FILE {f} **UPLOADED**")
                print(f"# files: {len(files)}")

            #return redirect(url_for('upload_image_test', files=files))

    return render_template('upload_file.html', files=files)




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

    recipes = get_recipes_for_display_as_list_of_dicts( [BEEF_BRISKET_BROTH, LEMON_GRASS_CHICKEN] )

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - *-* \\")
    pprint(recipes)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")

    headline_py = "Compare Nutrients fetch from DB"

    return render_template("nutrient_compare_page.html", headline=headline_py, recipes=recipes)



@app.route('/db_recipe_page', methods=["GET", "POST"])
def db_recipe_page():

    ri_id = 3202

    # route from gallery or other recipe request routes
    if request.method =='POST':
        print("POST                            - - - < db_recipe_page - S = = = =*=*")
        pprint(request.args.to_dict())
        print("POST                            - - - < db_recipe_page - M = = = =*=*")
        pprint(request)
        print("POST                            - - - < db_recipe_page - E = = = =*=*")
        if ('ri_id' in request.form):
            ri_id = int(request.form['ri_id'])
            print(f"POST ri_id: {ri_id} <")
        else:
            for key, val in request.form.items():
                print(f"POST k: {key} - v: {val} <")
                if re.match(r'gallery_button_', key):
                    ri_id = int(val)


    incoming_dict = request.args.to_dict()

    if request.method =='GET':
        print("GET                            - - - < db_recipe_page")
        pprint(incoming_dict)
        pprint(request.value)
        pprint(request.value)
        if 'text' in incoming_dict:
            ri_id = int(incoming_dict['text'])

    #recipe = get_single_recipe_from_db_for_display_as_dict(ri_id)
    recipe = get_single_recipe_with_subcomponents_from_db_for_display_as_dict(ri_id)

    recipes = [recipe]

    print(f"- - RECIPE PAGE ID:{ri_id} - - - - - - - - - - - - - - - - - - - - - - - - - - - *-* \\")
    pprint(recipes)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")

    return render_template("recipe_t.html", recipes=recipes)


@app.route('/buton_7', methods=["GET", "POST"])
def button_7():
    return render_template('data_return.html', lines=[f"BUTTON 7"])

# https://flask.palletsprojects.com/en/0.12.x/patterns/favicon/
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')



if __name__ == '__main__':
    # https://pythonprogramminglanguage.com/flask-hello-world/
    # reserved port numbers
    # https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers
    #app.run(host='0.0.0.0', port=50015)
    #app.run(host='192.168.1.13', port=50015 )

    #app.run(host='192.168.1.13', port=50015, ssl_context='adhoc' )
    #app.run(host='192.168.1.13', port=50015, ssl_context=('server.crt', 'server.key') )
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain("./scratch/server.crt", "./scratch/server.key")
    
    serving.run_simple("0.0.0.0", 50015, app, ssl_context=context)      # list on all IP addresses
    print("Running on 0.0.0.0 - https://localhost:50015/ - https://dtk.health:50015/")
    
    #serving.run_simple("192.168.1.13", 50015, app, ssl_context=context)
    #serving.run_simple("192.168.1.13", 443, app, ssl_context=context) # self.socket.bind(self.server_address)
                                                                      # PermissionError: [Errno 13] Permission denied?
    #print("Running on https://dtk.health:50015/")


    # setting up SSL for image capture:
    # https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
    # pip install pyOpenSSL
    #app.run(host='192.168.1.13', port=50015, ssl_context='adhoc')

    # Note for deployment:
    # http://flask.pocoo.org/docs/1.0/deploying/#deployment
