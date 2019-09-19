#! /usr/bin/env python

# tracker helpers
#from helpers_tracker import nix_time_ms, day_from_nix_time, time24h_from_nix_time

from datetime import datetime
import helpers_db



# tracker class should inherit from Recipe & extend with simple biometrics
# [(ri_name:            )(servings)][ dtk_weight,  dtk_pc_fat,    dtk_pc_h2o   ]
# 2019 calories month 09 day 15 (1) - 105.7kg,	fat_pc - 38.3,	H2O_pc - 44.8

def create_daily_tracker_name_from_nix_time(nix_time_ms = helpers_db.nix_time_ms()):
    return datetime.utcfromtimestamp(nix_time_ms / 1000.0).strftime("%Y calories month %m %a %d").lower()


def return_daily_tracker():
    dtk = { 'dtk_rcp': helpers_db.return_recipe_dictionary(),
                          'dtk_weight': 102.7,
                          'dtk_pc_fat': 36.2,
                          'dtk_pc_h2o': 46.4  }
    
    dtk['dtk_rcp']['ri_name'] = create_daily_tracker_name_from_nix_time()
    
    return dtk


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

    
    
    