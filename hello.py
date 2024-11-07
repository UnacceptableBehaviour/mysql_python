#! /usr/bin/env python

from flask import Flask, render_template, request, send_from_directory, redirect
from werkzeug import serving
import ssl

app = Flask(__name__, template_folder='templates')

# Add additional template directories
# for non source controlled templates - CSA support
app.jinja_loader.searchpath.append('scratch/_csa')

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
#from helpers_db import get_ri_ids_with_subcompnents_from_rcp_dict_as_list
from helpers_db import convert_tree_to_list_of_dict_components
from helpers_db import get_recipes_with_subcomponents_for_display_as_list_of_dicts
from helpers_db import get_daily_tracker, commit_DTK_DB, bootstrap_daily_tracker_create
from helpers_db import get_user_devices, store_user_devices, commit_User_Devices_DB
from helpers_db import process_search
from helpers_db import get_user_info_dict, remove_favs_from_DB, get_user_info_dict_from_DB, update_user_info_dict

from helpers_db import set_DB_connection, db_to_use_string

db_container = os.getenv('DB_CONTAINER', 'localhost')
app_title = 'DTK-U'
print(f"POSTGRES CONTAINER: {db_container}")
if db_container == 'postgres-container':    
    set_DB_connection(db_to_use_string[2])
    app_title = 'DTK-DOC'    
elif db_container == 'postgres-container-n':
    set_DB_connection(db_to_use_string[5])
    app_title = 'DTK-NAS'
elif db_container == 'creativemateriel.synology.me':
    set_DB_connection(db_to_use_string[4])
else:
    set_DB_connection(db_to_use_string[1])
    app_title = 'DTK-HEALTH'

from helpers_db import helper_db_class_db # THE DATABASE  < - - - \
# / - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /
# to UPDATE ASSET SERVER and postgreSQL DB with current assets
# run 'populate_db.py'
# \ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - < 

from helpers_tracker import get_daily_tracker_from_DB, store_daily_tracker_to_DB
from helpers_tracker import process_new_dtk_from_user, archive_dtk, dtk_timestamp_rolled_over


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# giza a look - debug
from pprint import pprint
import random
# debug - delete

import urllib.parse
url_encoded_pwd = urllib.parse.quote_plus("kx%jj5/g")

import re                   # regex
import json                 # JSON tools
from pathlib import Path    # Path tools

# each app.route is an endpoint
@app.route('/')
def home():
    # return redirect('synch_n_route')
    #return redirect(url_for('home_list_of_favourites')) same as > return redirect('/favs')
    return redirect('/favs')


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

    return render_template('weigh_in_t.html', app_title=app_title, daily_tracker=dtk)


@app.route('/favs', methods=["GET", "POST"])
def home_list_of_favourites():
    # from user device
    passed_in_uuid = '014752da-b49d-4fb0-9f50-23bc90e44298'
    user_info = get_user_info_dict_from_DB(passed_in_uuid)

    if request.method =='POST':
        pprint(request)
        favs_dict = request.get_json() # parse JSON into DICT
        print('favs_dict')
        pprint(favs_dict)
        if 'ri_id' in favs_dict:
            ri_id = favs_dict['ri_id']
            print(f"REMOVING: {ri_id} from DB")
            remove_favs_from_DB(helper_db_class_db, passed_in_uuid, [ri_id])

            return json.dumps(ri_id), 200
        
        if ('ri_names' in favs_dict) and ('save_label' in favs_dict):
            type_label = favs_dict['save_label']
            print('ri_names - - - S')
            print(f"SAVING TYPES to JSON: {type_label} - ")
            save_remove_targets = {}

            save_remove_targets[type_label] = favs_dict['ri_names']            
            pprint(save_remove_targets)

            save_remove_targets_json = json.dumps(save_remove_targets)

            with open(MISSLABELED_FILE_JSON, 'w') as f:
                f.write(save_remove_targets_json)

            print('ri_names - - - E')                        

            return json.dumps(type_label), 200



    #recipes = get_gallery_info_for_display_as_list_of_dicts(user_info['fav_rcp_ids'])
    recipes = get_recipes_for_display_as_list_of_dicts(user_info['fav_rcp_ids'])

    pprint(user_info)
    
    for r in recipes:
        cals_p_srv = int(float(r['nutrinfo']['serving_size']) / 100 *  float(r['nutrinfo']['n_En']))
        print(f"ri_id:{r['ri_id']}, \t{r['nutrinfo']['serving_size']}{r['nutrinfo']['units']} @ {r['nutrinfo']['n_En']}kcals per 100g, \tcals_p_srv:{cals_p_srv}\t{r['ri_name']}") #, 
        r['nutrinfo']['cals_p_srv'] = cals_p_srv

    print(f"\n\nFavs format - rendering {len(recipes)} recipes. . \n\n")    

    return render_template('show_fav_rcp_cards.html', app_title=app_title, recipes=recipes)


@app.route('/db_recipe_list', methods=["GET","POST"])
def db_recipe_list():
    if request.method =='POST':
        return 

    user_info = get_user_info_dict_from_DB('014752da-b49d-4fb0-9f50-23bc90e44298')    

    #recipes = get_gallery_info_for_display_as_list_of_dicts(user_info['fav_rcp_ids'])
    #recipes = get_recipes_for_display_as_list_of_dicts(user_info['fav_rcp_ids']) 
    recipes = get_recipes_with_subcomponents_for_display_as_list_of_dicts(user_info['fav_rcp_ids']) 

    if len(user_info['fav_rcp_ids']) == 0:
        recipes = [return_recipe_dictionary()]

    return render_template("recipe_t.html", app_title=app_title, recipes=recipes)



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


    # incoming_dict = request.args.to_dict() # strange errors
    # idict = dict(incoming_dict)
    idict = dict(request.args)

    if request.method =='GET':
        print("GET                            - - - < db_recipe_page - idict")
        # pprint(incoming_dict)
        # ri_id = request.args.get('ri_id')
        pprint(idict)
        print('- - - idict')
        ri_id = idict['ri_id']
        print(f"ri_id: {ri_id}")

        # if 'text' in incoming_dict:
        #     ri_id = int(incoming_dict['text'])

    #recipe = get_single_recipe_from_db_for_display_as_dict(ri_id)
    recipe = get_single_recipe_with_subcomponents_from_db_for_display_as_dict(int(ri_id))

    recipes = [recipe]

    print(f"- - RECIPE PAGE ID:{ri_id} - - - - - - - - - - - - - - - - - - - - - - - - - - - *-* \\")
    pprint(recipes)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")

    return render_template("recipe_t.html", app_title=app_title, recipes=recipes)




# @app.route('/db_gallery/<int:year>/<int:month>/<title>')
# def db_gallery(year, month, title):
#     pass

@app.route('/db_gallery')
def db_gallery():
    user_info = get_user_info_dict_from_DB('014752da-b49d-4fb0-9f50-23bc90e44298')

    # do this in pages when larger db - use JS to reload
    ri_ids = process_search('', user_info['default_filters'])   # '' - empty search = find all

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

    return render_template('gallery.html', app_title=app_title, user_info=user_info, recipes=recipes)



@app.route('/settings', methods=["GET", "POST"])
def settings():

    # POST route
    if request.method == 'POST':
        settings = request.get_json()  # parse JSON into DICT

        if 'action' in settings and settings['action'] == 'retrieve':
            # Retrieve user_info from DB
            user_info = get_user_info_dict_from_DB(settings['user'])
            user_info.pop('devices', None)  # setting per device? - Use case multi users using one account different devices.

            sql_query = "SELECT DISTINCT unnest(types) AS all_types FROM recipes;"
            types = helper_db_class_db.execute(sql_query).fetchall()  # ret list of tuples [('serve_hot',),('serve_rt',),('lunchbox',), etc ]
            types = [t[0] for t in types if t[0].strip()]  # remove blanks
            types.sort()
            user_info['tag_sets']['types'] = types

            return json.dumps({'user_info': user_info}), 200  # OK

        elif 'user_info' in settings:
            print('/settings/POST:user_info:')
            pprint(settings['user_info'])

            # write settings to DB
            update_user_info_dict(settings['user_info'])

            # return all good
            return json.dumps({}), 201  # created

        else:
            # return - couldn't find user_info!??
            return json.dumps({}), 404  # not found


    user_info = get_user_info_dict_from_DB('014752da-b49d-4fb0-9f50-23bc90e44298')   
    user_info.pop('devices', None) # setting per device? - Use case multi users using one account different devices.

    sql_query = "SELECT DISTINCT unnest(types) AS all_types FROM recipes;"
    types = helper_db_class_db.execute(sql_query).fetchall()    # ret list of tuples [('serve_hot',),('serve_rt',),('lunchbox',), etc ]
    # print('=\ ')
    # pprint(types)
    types = [ t[0] for t in types if t[0].strip() ]   # remove blanks
    types.sort()
    for t in types: print(f"{t},",end="")
    print('=/ ')

    # source of buttons to populate with settings from default_filters
    user_info['tag_sets']['types'] = types

    return render_template('settings_t.html', app_title=app_title, user_info=user_info)


#@app.route('<ri_id>', methods=["GET", "POST"]) 
#def email_debug(ri_id):
@app.route('/email_debug', methods=["GET", "POST"])
def email_debug():
    ri_id = 1712    # prawns in garlic - default

    # if request.method =='POST':
    #     print("POST                            - - - < email_debug - S = = = =*=*")
    #     pprint(request.json)
    #     print("POST                            - - - < email_debug - M = = = =*=*")
    #     pprint(request)
    #     print("POST                            - - - < email_debug - E = = = =*=*")
    #     if ('ri_id' in request.json):
    #         ri_id = int(request.json['ri_id'])
    #         print(f"POST ri_id: {ri_id} <")
    #     else:
    #         print(f"POST ri_id: NO PAYLOAD > email_debug <")
    #         ri_id = 1175    #'egg prawn & chorizo wontan dumpling broth'

    if request.method =='GET':
        idict = dict(request.args)
        print("GET                            - - - < email_debug - idict")
        if 'ri_id' in idict:
            ri_id = idict['ri_id']
            print(f"ri_id: {ri_id}")
        else:
            print(f"ri_id: DEFAULT: {ri_id}")


    # get all the sub components in the recipe
    rcp_tree = get_single_recipe_with_subcomponents_from_db_for_display_as_dict(int(ri_id))
    #pprint(rcp_tree)

    recipes = convert_tree_to_list_of_dict_components(rcp_tree)
    # remove DB misses & duplicates
    seen = set()
    def duplictate(name , seen):
        if name in seen:
            return True
        seen.add(name)
        return False
    
    recipes = [r for r in recipes if (r['ri_name'] != 'none_listed') and (not duplictate(r['ri_name'], seen))]
    print(f"seen: {seen}")

    # set blog_post flag to change rendering
    recipes = [{**r, 'blog_post': True} for r in recipes]

    print('> > > > - - - - - - > > > > - - - - - - > > > > - - - - - - > > > > - - - - - - S')
    pprint(recipes)
    print('> > > > - - - - - - > > > > - - - - - - > > > > - - - - - - > > > > - - - - - - E')
    
    return render_template('email_debug_t.html', app_title=app_title, recipes=recipes)


last_search_result_recipes = {}
MISSLABELED_FILE_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_incorrectly_labeled_WEBIF.json')
FAV_TYPE_GROUPING_DIR = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_incorrectly_labeled_WEBIF_LABELS')

@app.route('/search', methods=["GET", "POST"])
def search_ingredient():
    global last_search_result_recipes # what the point of a global if it isn't implicitly global? TODO
    search = ''
    
    # fallback data - TODO - CHECK if needed once search working
    user_info = get_user_info_dict_from_DB('014752da-b49d-4fb0-9f50-23bc90e44298')

    # process search post - query database
    # get all recipes with search criterea
    if request.method == 'POST':
        search_request = request.get_json() # parse JSON into DICT

        if ('user' in search_request):
            uuid =  search_request['user']
            print(f"UUID: {uuid} <")

        if ('search' in search_request):
            search = search_request['search']            
            print("search_ingredient - - - - - > >")
            pprint(search)        
            user_info = get_user_info_dict_from_DB(uuid)
            
            ri_ids = process_search(search, user_info['default_filters'])
            
            print("search_result - - - - - > >")
            last_search_result_recipes = get_gallery_info_for_display_as_list_of_dicts(ri_ids)
            #pprint(last_search_result_recipes)
            print(f"SEARCH FOUND: {len(last_search_result_recipes)} results")

            return json.dumps(last_search_result_recipes), 200

        elif ('rcpsToUnlabel' in search_request) or ('rcpsShortList' in search_request):
            removal_targets = {}
            filter_target = 'None'
            rcpsToUnlabel = []
            if ('rcpsToUnlabel' in search_request):
                rcpsToUnlabel = search_request['rcpsToUnlabel']
            
            if len(rcpsToUnlabel) > 0:
                if len(user_info['default_filters']['type_inc']) > 1:
                    filter_target = 'multiple_type_labels'

                if len(user_info['default_filters']['type_inc']) == 1:
                    filter_target = user_info['default_filters']['type_inc'][0]

                if len(user_info['default_filters']['type_inc']) == 0:
                    filter_target = search_request['alt_label']

                print('removal_targets - - - S')
                removal_targets[filter_target] = rcpsToUnlabel
                pprint(removal_targets)
                removal_targets_json = json.dumps(removal_targets)
                with open(MISSLABELED_FILE_JSON, 'w') as f:
                    f.write(removal_targets_json)
                print('removal_targets - - - E')

        
            # save favourite recipes to user settings
            print('favourite_targets - - - S')            
            favourite_targets = []
            if len(search_request['rcpsShortList']) > 0:
                user_info = get_user_info_dict_from_DB(uuid)
                if 'fav_rcp_ids' in user_info:
                    pprint("search_request['rcpsShortList']")
                    pprint(search_request['rcpsShortList'])
                    pprint("user_info['fav_rcp_ids']")
                    pprint(user_info['fav_rcp_ids'])
                    if 'toggle_favs' in search_request:
                        if search_request['toggle_favs']: # true toggle them
                            for item in search_request['rcpsShortList']:
                                if item in user_info['fav_rcp_ids']:
                                    # If item is in both lists, remove it from user_info['fav_rcp_ids']
                                    user_info['fav_rcp_ids'].remove(item)
                                else:
                                    # If item is in search_request['rcpsShortList'] but not in user_info['fav_rcp_ids'], add it
                                    user_info['fav_rcp_ids'].append(item)
                    else:
                        add_to_existing = search_request['rcpsShortList'] + user_info['fav_rcp_ids']
                        favourite_targets = list(set(add_to_existing))

                else:
                    favourite_targets = list(set(search_request['rcpsShortList']))
                pprint(user_info)
                print('favourite_targets - - - M')
                user_info.update({'UUID':uuid, 'fav_rcp_ids':favourite_targets})
                pprint(user_info)
                print('favourite_targets - - - M1')
                # write settings to DB
                update_user_info_dict(user_info)
                print('favourite_targets - - - E')
            
            ret_object = {'filter_target':filter_target,
                          'favourite_targets':len(favourite_targets) }
            
            return json.dumps(ret_object), 200
        else:
            raise('Come on!!')                

    else:
        # landed on search
        print(f"search_ingredient: {request.method}")
        pprint(request)
        print("- - - - s_i:" )

        #ri_ids = [301,1101,1202,1701,2301,2501,2902,3301,3401]
        #recipes = get_gallery_info_for_display_as_list_of_dicts(ri_ids)
        dbg_user_info = dict(user_info) # duplicate so as not to interfere with 'db' (dev only)
        dbg_user_info.pop('tag_sets')
        pprint(dbg_user_info)

    # GET route                                     # TODO implement --\
    return render_template('search_t.html', app_title=app_title, recipes=last_search_result_recipes)



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
        


    return render_template('track_items.html', app_title=app_title, daily_tracker=dtk)


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


    return render_template("image_capture.html", app_title=app_title, headline=headline_py, recipes=recipes, mobi=def_im)


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

    return render_template('upload_file.html', app_title=app_title, files=files)




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
