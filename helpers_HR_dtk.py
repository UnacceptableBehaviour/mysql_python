#! /usr/bin/env python

# tracker helpers - this should dissapear - for the most part when DB is implemented

from pprint import pprint
from timestamping import  time24h_from_nix_time
# indexes for ingredients row
from magic_numbers import ATOMIC_INDEX, QTY_IN_G_INDEX, SERVING_INDEX, INGREDIENT_INDEX, TRACK_NIX_TIME, IMAGE_INDEX, HTML_ID

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
        time = time24h_from_nix_time(line[TRACK_NIX_TIME])
        qty  = line[QTY_IN_G_INDEX]
        ingredient = line[INGREDIENT_INDEX]
        if dtk_mode:
            human_line = f"{qty}\t{ingredient}\t# {time}\n"
        else:
            human_line = f"{qty}\t{ingredient}\n"
        dtk_text += human_line

    dtk_text += f"							Total ({recipe['nutrinfo']['yield']})\n\n"

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

    test_text_3 = create_DTK_textcomponent(dtk)

    return test_text_1 + test_text_3 + test_text_4


