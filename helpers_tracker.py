#! /usr/bin/env python

# tracker helpers - this should dissapear - for the most part when DB is implemented

from pprint import pprint

from pathlib import Path
import subprocess   # exec CLI commands
import json

from datetime import datetime
import helpers_db       # explicitly use helpers_db.func_name()     << highlight where function is from 
# change to from helpers_db import - isolate  iface:
    #from helpers_db import get_daily_tracker, store_daily_tracker, time24h_from_nix_time, commit_DTK_DB
    #from helpers_db import TRACK_NIX_TIME, QTY_IN_G_INDEX, nix_time_ms
from helper_nutrinfo import i_db
from config_files import get_file_for_data_set


# TODO
# tracker class should inherit from Recipe & extend with simple biometrics
# [(ri_name:            )(servings)][ dtk_weight,  dtk_pc_fat,    dtk_pc_h2o   ]
# 2019 calories month 09 day 15 (1) - 105.7kg,	fat_pc - 38.3,	H2O_pc - 44.8


def get_daily_tracker_from_DB(userUUID = '014752da-b49d-4fb0-9f50-23bc90e44298'):
    return helpers_db.get_daily_tracker(userUUID)

# dtk contains a uuid = '014752da-b49d-4fb0-9f50-23bc90e44298'
def store_daily_tracker_to_DB(dtk = {}):
    return helpers_db.store_daily_tracker(dtk)


def post_interface_file():
    return get_file_for_data_set('dtk_recipe_txt')

def get_interface_file():
    return get_file_for_data_set('dtk_nutrients_txt')


# take dtk object and convert to daily tracker human readable record
def create_DTK_textcomponent(dtk, dtk_mode=True):
    dtk_text = ''
    recipe = dtk['dtk_rcp']
        
    print("------------------+------------------+------------------+------------------+------------------")
    print(f"mode: {dtk_mode} - {recipe['nutrinfo']['servings']} <")
    pprint(recipe['nutrinfo'])
    print("------------------+------------------+------------------+------------------+------------------")
    
    # ------------------ for the 2019 calories month 10 day 01 (1) - 103.6kg,	fat_pc - 36.9,	H2O_pc - 45.9
    # 180m	coffee												# 0815 
    # 250m	water								# swim @ 1055 - 1km 75m 668cal - included the rides on each end
    # 180m	coffee												# 1734
    # 70g		smoked mackerel
    # 38g	(2)	tomato cracker                                  # 2200
    # 30g		mixed nuts
    # 													Total (0g)
    if dtk_mode:
        headline = f"------------------ for the {recipe['ri_name']} (1) - {dtk['dtk_weight']}kg,	fat_pc - {dtk['dtk_pc_fat']},	H2O_pc - {dtk['dtk_pc_h2o']}"
    else:
        headline = f"------------------ for the {recipe['ri_name']} ({recipe['nutrinfo']['servings']})"
    
    dtk_text += headline + "\n"
    
    for line in recipe['ingredients']:
        time = helpers_db.time24h_from_nix_time(line[helpers_db.TRACK_NIX_TIME])
        qty  = line[helpers_db.QTY_IN_G_INDEX]
        ingredient = line[helpers_db.INGREDIENT_INDEX]
        if dtk_mode:
            human_line = f"{qty}\t{ingredient}\t# {time}\n"
        else:
            human_line = f"{qty}\t{ingredient}\n"
        dtk_text += human_line
        
    dtk_text += f"													Total ({recipe['nutrinfo']['yield']})\n\n"    
        
    return dtk_text


# ATOMIC_INDEX = 0                    # default value is 1 - TRUE
# QTY_IN_G_INDEX = 1
# SERVING_INDEX = 2
# INGREDIENT_INDEX = 3
# TRACK_NIX_TIME = 4

# take recipe / component convert 
def create_text_component(recipe):
    # ------------------ for the double tomato cracker (1)
    # 6g		rosemary cracker
    # 20g		tomatoes
    # 3g		mayo
    # 													Total (19g)
    create_DTK_textcomponent(recipe, False)


def create_human_readable_DTK_spec(dtk):
    # insert constituent components of the daily tracker above it so makes sense reading
    # lik a recipe
    test_text_1 = '''
========== COSTING
968 nutritest - 20190830-12

'''
    test_text_2 = '''
------------------ for the double tomato cracker (1)
6g		rosemary cracker
20g		tomatoes
3g		mayo
													Total (19g)

'''

    test_text_3 = '''
------------------ for the 2019 calories month 10 day 02 (1) - 103.6kg,	fat_pc - 36.9,	H2O_pc - 45.9
180m	coffee												# 0815 
20g		spinach and cheddar cheese tortilla
250m	water								# swim @ 1055 - 1km 75m 668cal - included the rides on each end
80m		coffee												# 1210
330g	post swim breakfast 20190901
180m	coffee												# 1230 
384g	lamb teriyaki skewers and lambs lettuce
40g		lamb and aubergine teriyaki skewers					# helped mum with lamb on one of hers - aubergine went down well
180m	coffee												# 1630
10g		plain chocolate 
180m	coffee												# 1734
200m	vodka												# 2136
500m 	omega cider											# 2200
50g		chorizo crisps
70g		smoked mackerel
38g	(2)	tomato cracker
30g		mixed nuts
16g		st agur
6g		spanish goats cheese
													Total (2744g)

'''

    test_text_4 = '''
====================================================================================
'''
    # TODO
    # reverse iterate components creating multiple test_text_2 sections
    # using create_text_component(component)    # list ? dict of components in dtk['components']
    # TODO - recursive into components - CHECK
    #      - reverse order? lowest level component first
    #
    # test_text_2 = ''
    # for recipe in dtk['dtk_rcp']['components']:
    #     test_text_2 += create_text_component(recipe)

    test_text_3 = create_DTK_textcomponent(dtk)

    return test_text_1 + test_text_2 + test_text_3 + test_text_4

# awaiting implementation
# 
def post_DTK_info_for_processing(dtk):
    # create DTK
    dtk_spec = create_human_readable_DTK_spec(dtk)    
    
    # file it - post_interface_file() get the name of filee from
    # a shared config file - a json file
    with open(post_interface_file(), 'w') as i_face_out:
        i_face_out.write(dtk_spec)
        i_face_out.close()

        
def get_DTK_info_from_processing(dtk):
    # just loaf info for dtk
    search_name = dtk['dtk_rcp']['ri_name']
    
    dtk_nut_dict = {}
    
    # load nutrinfo
    i_db.loadNutrientsFromTextFile(get_file_for_data_set('dtk_nutrients_txt'), dtk_nut_dict)
    
    return dtk_nut_dict[search_name]
                
    # return {'density': 1,
    #         'n_Al': 0,
    #         'n_Ca': 0,
    #         'n_En': 100,
    #         'n_Fa': 15.0,
    #         'n_Fb': 0,
    #         'n_Fm': 0,
    #         'n_Fo3': 10.0,
    #         'n_Fp': 0,
    #         'n_Fs': 5,
    #         'n_Pr': 0,
    #         'n_Sa': 2,
    #         'n_St': 2,
    #         'n_Su': 12,
    #         'serving_size': 200,
    #         'servings': 2,
    #         'units': 'g',
    #         'yield': '400g'}


# updated dtk package arrived from user
# process into nutrient info:
#
#   h_tracker  -   -   >     config     <   -  legacy
#                              .
#   createHRversion            .
#   |                          .
#   create_human_readable_DTK_spec
#   create_DTK_textcomponent   .
#   |                          .
#   save it to file - - -> iface_file - - -> process into nutrients
#                                                   |
#   load file <- - - - - - iface_file <- - - write it back
#   |
#
#
#

def process_new_dtk_from_user(dtk_data):
    uuid = dtk_data['dtk_user_info']['UUID']
    
    # update DB
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - R")
    
    # export DTK for PROCESSING
    # as nutridoc entry
    post_DTK_info_for_processing(dtk_data)
    
    # fire up ccm_nutridoc_web.rb PROCESS DTK data
    arg1 = f"{dtk_data['dtk_weight']}"
    arg2 = f"file={post_interface_file()}"
    data_from_nutriprocess = subprocess.check_call(["ccm_nutridoc_web.rb", arg1, arg2])
    
    # import RESULT: just get nutrinfo for daily tracker for now.
    # will expect a fully processed DTK including subcomponents
    # TODO
    nutridata = get_DTK_info_from_processing(dtk_data)
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")
    
    # TODO - 1st
    # Make robust - if a single item is NO NUTIRIENT DATA
    # nothing is returned because DTK in for day FAILS
    # Highlight missing items, but total the known ones
    
    
    # merge nutrinfo into DTK and send it back!        
    dtk_data['dtk_rcp']['nutrinfo'].update( nutridata ) # <<
    dtk_data['dtk_user_info'] = {'UUID': '014752da-b49d-4fb0-9f50-23bc90e44298', 'name': 'Simon'}
    #pprint(dtk_data)
    store_daily_tracker_to_DB(dtk_data)   # ram & disc
    #helpers_db.commit_DTK_DB()            # disc
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /")  

    return(dtk_data)



def archive_dtk(dtk):
    print("------------------+------------------+ a r c h i v i n g +------------------+------------------ S")
    # scenarios
    # submitted dtk most up to date - archive it
    # server side dtk more up to date (updated by another device) merge them - lossless
    serv_dtk = get_daily_tracker_from_DB(dtk['dtk_user_info']['UUID'])

    # compare server / device versions
    # make sure they're in the same 24hr period
    dtk_timestamp_rolled_over(serv_dtk) # insert 'dt_rollover' if not present - TODO REMOVE
    dtk_timestamp_rolled_over(dtk)
    

    # if 'dt_last_update' not in dtk['dtk_rcp']: dtk['dtk_rcp']['dt_last_update'] = 0
    # if 'dt_last_update' not in serv_dtk['dtk_rcp']: serv_dtk['dtk_rcp']['dt_last_update'] = 0
    
    # check we're in the same day - otherwise not relevant
    if serv_dtk['dtk_rcp']['dt_rollover'] == dtk['dtk_rcp']['dt_rollover']:
        archive_dtk = dtk if (dtk['dtk_rcp']['dt_last_update'] > serv_dtk['dtk_rcp']['dt_last_update']) else serv_dtk
        # TODO if server is more upto date MERGE
        print(f"Comparing DEV_TS:{dtk['dtk_rcp']['dt_last_update']} SRV_TS:{serv_dtk['dtk_rcp']['dt_last_update']}")
    else:
        archive_dtk = dtk
        print("Archiving DEV directly")

    archfile_name = f"{archive_dtk['dtk_user_info']['UUID']}_{archive_dtk['dtk_user_info']['name']}_{serv_dtk['dtk_rcp']['dt_rollover']}.json"
    
    arch_target = Path(get_file_for_data_set("archive_path")).joinpath(archfile_name)
    
    with open(arch_target, 'w') as f:
        f.write(json.dumps(archive_dtk))
        #f.close()        
    
    store_daily_tracker_to_DB(archive_dtk)
    
    print(f"SRV:{serv_dtk['dtk_user_info']['name']} - {serv_dtk['dtk_user_info']['UUID']} - {serv_dtk['dtk_rcp']['dt_last_update']}")
    print(f"DEV:{dtk['dtk_user_info']['name']} - {dtk['dtk_user_info']['UUID']} - {dtk['dtk_rcp']['dt_last_update']}")
    print(f"ARC:{archive_dtk['dtk_user_info']['name']} - {archive_dtk['dtk_user_info']['UUID']} - {archive_dtk['dtk_rcp']['dt_last_update']}")
    pprint(archive_dtk)
    print("------------------+------------------+ a r c h i v i n g +------------------+------------------ E")    
                



def dtk_timestamp_rolled_over(dtk):    
    print("dtk_timestamp_rolled_over?")
    
    # this is only necessary for earlier version - TODO REMOVE
    if 'dt_rollover' not in dtk['dtk_rcp']:
        dtk['dtk_rcp']['dt_rollover'] = roll_over_from_nix_time(dtk['dtk_rcp']['dt_date'])
        print("WARNING 'dt_rollover' not in dtk['dtk_rcp'] . . creating . .  ")        
        return True         # start a fresh dtk
    
    dro = helpers_db.hr_readable_from_nix(dtk['dtk_rcp']['dt_rollover'])     # roll_over
    dts = helpers_db.hr_readable_from_nix(dtk['dtk_rcp']['dt_date'])         # creation date
    dlu = helpers_db.hr_readable_from_nix(dtk['dtk_rcp']['dt_last_update'])  # last update
    nix_now = helpers_db.nix_time_ms()                                       # time now
    hr_now = helpers_db.hr_readable_from_nix(nix_now)
    # human readable
    print(f"RollOver check: RO: {dro} < NOW: {hr_now}  -  CREATED: {dts}  -  Last Update: {dlu} <")
    # nix time
    print(f"RollOver check: RO: {dtk['dtk_rcp']['dt_rollover']} < NOW: {nix_now}  -  CREATED: {dtk['dtk_rcp']['dt_date']}  -  Last Update: {dtk['dtk_rcp']['dt_last_update']} <")
        
    #if helpers_db.nix_time_ms() > dtk['dtk_rcp']['dt_rollover']:
    if nix_now > dtk['dtk_rcp']['dt_rollover']:
        print("dtk_timestamp_rolled_over? True")
        return True

    print("dtk_timestamp_rolled_over? False")
    return(False)





# testing         
if __name__ == '__main__':
    pprint(get_daily_tracker_from_DB())


    
    
    