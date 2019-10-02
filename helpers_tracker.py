#! /usr/bin/env python

# tracker helpers

from datetime import datetime
import helpers_db


# tracker class should inherit from Recipe & extend with simple biometrics
# [(ri_name:            )(servings)][ dtk_weight,  dtk_pc_fat,    dtk_pc_h2o   ]
# 2019 calories month 09 day 15 (1) - 105.7kg,	fat_pc - 38.3,	H2O_pc - 44.8

def create_daily_tracker_name_from_nix_time(nix_time_ms = helpers_db.nix_time_ms()):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y calories month %m %a %d").lower()


def return_daily_tracker():
    dtk = { 'dtk_rcp':    helpers_db.return_recipe_dictionary(),
            'dtk_weight': 102.7,
            'dtk_pc_fat': 36.2,
            'dtk_pc_h2o': 46.4  }
    
    dtk['dtk_rcp']['ri_name'] = create_daily_tracker_name_from_nix_time()
    
    return dtk

def post_interface_file():
    return './scratch/___LAB_RECIPE_SMALLEST_DTK_TEST.txt'

def get_interface_file():
    return './scratch/z_product_nutrition_info_autogen_day_cal.txt'


# take dtk object and convert to daily tracker human readable record
def create_DTK_textcomponent(dtk, dtk_mode=True):
    dtk_text = ''
    recipe = dtk['dtk_rcp']
    # ------------------ for the 2019 calories month 10 day 01 (1) - 103.6kg,	fat_pc - 36.9,	H2O_pc - 45.9
    # 180m	coffee												# 0815 
    # 250m	water								# swim @ 1055 - 1km 75m 668cal - included the rides on each end
    # 180m	coffee												# 1734
    # 70g		smoked mackerel
    # 38g	(2)	tomato cracker                                  # 2200
    # 30g		mixed nuts
    # 													Total (0g)        
    return dtk_text



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
    test_text = '''
========== COSTING
968 nutritest - 20190830-12


------------------ for the double tomato cracker (1)
6g		rosemary cracker
20g		tomatoes
3g		mayo
													Total (19g)


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

====================================================================================
'''
    return test_text


def post_DTK_info_for_processing(dtk):
    # create DTK
    dtk_spec = create_human_readable_DTK_spec(dtk)    
    
    # file it
    with open(post_interface_file(), 'w') as i_face_out:
        i_face_out.write(dtk_spec)
        i_face_out.close()
        
def get_DTK_info_from_processing():
    # load nutrinfo
    with open(get_interface_file(), 'r') as i_face_in:
        # process incoming DTK nutrinfo into DTK JSON
        i_face_in.close()
        
        
    return {'density': 1,
            'n_Al': 0,
            'n_Ca': 0,
            'n_En': 100,
            'n_Fa': 15.0,
            'n_Fb': 0,
            'n_Fm': 0,
            'n_Fo3': 10.0,
            'n_Fp': 0,
            'n_Fs': 5,
            'n_Pr': 0,
            'n_Sa': 2,
            'n_St': 2,
            'n_Su': 12,
            'serving_size': 200,
            'servings': 2,
            'units': 'g',
            'yield': '400g'}


# testing         
if __name__ == '__main__':
    
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    day = datetime.now().strftime("%d") # day number
    day = datetime.now().strftime("%a").lower() # day 3 letter
    time = datetime.now().strftime("%H%M").lower() # 4 digit 24hr clock
    #time_since_epoch = nix_time_ms(datetime.now())
    time_since_epoch = nix_time_ms()
    day_from_nx = day_from_nix_time(time_since_epoch)
    time24_from_nx = time24h_from_nix_time(time_since_epoch)
    
    print(day, time, time_since_epoch, day_from_nx)
    print(type(datetime.now()))
    print(create_daily_tracker_name_from_nix_time(nix_time_ms()))

    
    
    