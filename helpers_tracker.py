#! /usr/bin/env python

# tracker helpers - this should dissapear - for the most part when DB is implemented

from pprint import pprint

from pathlib import Path
import subprocess   # exec CLI commands
import json

from datetime import datetime
from timestamping import roll_over_from_nix_time, nix_time_ms, hr_readable_from_nix
from timestamping import hr_readable_date_from_nix, time24h_from_nix_time

from helpers_db import get_daily_tracker, store_daily_tracker
from magic_numbers import ATOMIC_INDEX, QTY_IN_G_INDEX, SERVING_INDEX, INGREDIENT_INDEX, TRACK_NIX_TIME, IMAGE_INDEX, HTML_ID
from food_sets import IGD_TYPE_NO_INFO

from helper_nutrinfo import i_db
from config_files import get_config_or_data_file_path
from helpers_HR_dtk import create_human_readable_DTK_spec

# TODO
# tracker class should inherit from Recipe & extend with simple biometrics
# [(ri_name:            )(servings)][ dtk_weight,  dtk_pc_fat,    dtk_pc_h2o   ]
# 2019 calories month 09 day 15 (1) - 105.7kg,	fat_pc - 38.3,	H2O_pc - 44.8


def get_daily_tracker_from_DB(userUUID = '014752da-b49d-4fb0-9f50-23bc90e44298'):
    return get_daily_tracker(userUUID)

# dtk contains a uuid = '014752da-b49d-4fb0-9f50-23bc90e44298'
def store_daily_tracker_to_DB(dtk = {}):
    return store_daily_tracker(dtk)




# get_qty_in_nanograms_from_string_as_float
def get_qty_in_grams_from_string_as_float(qty_str):
    # TODO convert_all_qty_to_nano_g - for vitamins and minerals
    # look fo unit of measure and return float
    return float(qty_str.split('g')[0])

# def empty_nutridict():
#     return  {'igdt_type': 'dtk',
#             'n_Al': 0.0,
#             'n_Ca': 0.0,
#             'n_En': 0.0,
#             'n_Fa': 0.0,
#             'n_Fb': 0.0,
#             'n_Fm': 0.0,
#             'n_Fo3':0.0,
#             'n_Fp': 0.0,
#             'n_Fs': 0.0,
#             'n_Pr': 0.0,
#             'n_Sa': 0.0,
#             'n_St': 0.0,
#             'n_Su': 0.0,
#             'name': '',
#             'ots_ingredients': '__igdts__',
#             'serving_size': 0.0,
#             'servings': 1.0,
#             'yield': 0.0}

def process_new_dtk_from_user(dtk_data):
    uuid = dtk_data['dtk_user_info']['UUID']

    # update DB
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - P_submitted_DTK S")
    # TODO do this for all nutrient not just traffic lights
    # break out into f()
    tot_cals = 0
    tot_weight = 0
    tot_fat = 0
    tot_saturates = 0
    tot_sugars = 0
    tot_salt = 0
    multiplier = 0.0
    for index, i in enumerate(dtk_data['dtk_rcp']['ingredients']):
        nutri_info = i_db.get(i[INGREDIENT_INDEX])  # pull nutrient info from DB
        print(f"nutri_info - - - d {i[INGREDIENT_INDEX]}")
        pprint(nutri_info)
        print("nutri_info - - - E")
        if nutri_info == None:
            # set i[ATOMIC_INDEX] = IGD_TYPE_NO_INFO
            dtk_data['dtk_rcp']['ingredients'][index][ATOMIC_INDEX] = str(IGD_TYPE_NO_INFO)
            print(f"WARNING - NO NUTRIENT INFO FOR {i[INGREDIENT_INDEX]}")
            continue
        else:
            multiplier = get_qty_in_grams_from_string_as_float(i[QTY_IN_G_INDEX]) / 100
            if 'n_En' in nutri_info:
                i_cals = nutri_info['n_En'] * multiplier
                tot_cals += i_cals
            
            i_weight = get_qty_in_grams_from_string_as_float(i[QTY_IN_G_INDEX])
            tot_weight += i_weight
            
            if 'n_Fa' in nutri_info:
                i_fat = nutri_info['n_Fa'] * multiplier
                tot_fat += i_fat
            
            if 'n_Sa' in nutri_info:
                i_saturates = nutri_info['n_Sa'] * multiplier
                tot_saturates += i_saturates

            if 'n_Su' in nutri_info:
                i_sugars = nutri_info['n_Su'] * multiplier
                tot_sugars += i_sugars

            if 'n_St' in nutri_info:
                i_salt = nutri_info['n_St'] * multiplier
                tot_salt += i_salt
    
    nutridata = {}
    nutridata['n_En'] = int(tot_cals)
    nutridata['n_Fa'] = round(tot_fat, 1)
    nutridata['n_Sa'] = round(tot_saturates, 1)
    nutridata['n_Su'] = round(tot_sugars, 1)
    nutridata['n_St'] = round(tot_salt, 1)
    nutridata['yield'] = round(tot_weight, 1)
    nutridata['serving_size'] = 100 # use by traffic light to scale nutrients - set to 100 for DTK
    nutridata['servings'] = 1
    

    # merge nutrinfo into DTK and send it back!
    dtk_data['dtk_rcp']['nutrinfo'].update( nutridata ) # <<
    # TODO REMOVE - user uuid etc shoul come in with the data
    dtk_data['dtk_user_info'] = {'UUID': '014752da-b49d-4fb0-9f50-23bc90e44298', 'name': 'Simon'}
    pprint(dtk_data)
    store_daily_tracker_to_DB(dtk_data)   # ram & disc
    #commit_DTK_DB()            # disc

    # # fire up ccm_nutridoc_web.rb PROCESS DTK data - DEPRACATED
    # # potentially use this to create JSON for nutridoc w/ costing & nutrients
    # arg1 = f"{dtk_data['dtk_weight']}"
    # arg2 = f"file={post_interface_file()}"
    # # inline slow
    # #data_from_nutriprocess = subprocess.check_call(["./scratch/_ruby_scripts/ccm_nutridoc_web.rb", arg1, arg2])
    # # BACK GROUND Fire off a separate process to create some info file for access later
    # subprocess.Popen(["ruby", "./scratch/_ruby_scripts/ccm_nutridoc_web.rb", arg1, arg2])

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - P_submitted_DTK E")
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

    archfile_name = f"{archive_dtk['dtk_user_info']['UUID']}_{archive_dtk['dtk_user_info']['name']}_{serv_dtk['dtk_rcp']['dt_rollover']}_{hr_readable_date_from_nix(serv_dtk['dtk_rcp']['dt_date'])}.json"

    arch_target = Path(get_config_or_data_file_path("archive_path")).joinpath(archfile_name)

    with open(arch_target, 'w') as f:
        f.write(json.dumps(archive_dtk))
        #f.close()

    store_daily_tracker_to_DB(archive_dtk)

    print(f"SRV:{serv_dtk['dtk_user_info']['name']} - {serv_dtk['dtk_user_info']['UUID']} - {serv_dtk['dtk_rcp']['dt_last_update']}")
    print(f"DEV:{dtk['dtk_user_info']['name']} - {dtk['dtk_user_info']['UUID']} - {dtk['dtk_rcp']['dt_last_update']}")
    print(f"ARC:{archive_dtk['dtk_user_info']['name']} - {archive_dtk['dtk_user_info']['UUID']} - {archive_dtk['dtk_rcp']['dt_last_update']}")
    pprint(archive_dtk)

    # to allow inspection and cpoying to nutridocs for processing / analysis
    dtk_spec = create_human_readable_DTK_spec(dtk)
    with open(str(arch_target).replace('.json','_last_post.txt'), 'w') as dtk_arc_file:
        dtk_arc_file.write(dtk_spec)
    print("------------------+------------------+ a r c h i v i n g +------------------+------------------ E")




def dtk_timestamp_rolled_over(dtk):
    print("dtk_timestamp_rolled_over?")

    # this is only necessary for earlier version - TODO REMOVE
    if 'dt_rollover' not in dtk['dtk_rcp']:
        dtk['dtk_rcp']['dt_rollover'] = roll_over_from_nix_time(dtk['dtk_rcp']['dt_date'])
        print("WARNING 'dt_rollover' not in dtk['dtk_rcp'] . . creating . .  ")
        return True         # start a fresh dtk

    dro = hr_readable_from_nix(dtk['dtk_rcp']['dt_rollover'])     # roll_over
    dts = hr_readable_from_nix(dtk['dtk_rcp']['dt_date'])         # creation date
    dlu = hr_readable_from_nix(dtk['dtk_rcp']['dt_last_update'])  # last update
    nix_now = nix_time_ms()                                       # time now
    hr_now = hr_readable_from_nix(nix_now)
    # human readable
    print(f"RollOver check: RO: {dro} < NOW: {hr_now}  -  CREATED: {dts}  -  Last Update: {dlu} <")
    # nix time
    print(f"RollOver check: RO: {dtk['dtk_rcp']['dt_rollover']} < NOW: {nix_now}  -  CREATED: {dtk['dtk_rcp']['dt_date']}  -  Last Update: {dtk['dtk_rcp']['dt_last_update']} <")

    if nix_now > dtk['dtk_rcp']['dt_rollover']:
        print("dtk_timestamp_rolled_over? True")
        return True

    print("dtk_timestamp_rolled_over? False")
    return(False)





# testing
if __name__ == '__main__':
    pprint(get_daily_tracker_from_DB())





