#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
from pprint import pprint
from pathlib import Path


# simple allergen detection - this could explode into a massively time consuming exersize to keep it simple!
# Breif: should work with the ingredient in the current data set ~1400 ingredients
#
# a call to get_allergens_from_ingredients(['cod','flour','egg','water','soda water','salt','veg oil','corn flour'])
# should return ['dairy', 'eggs', 'fish', 'gluten']
#
# alcohol classification should be limited to rum, vodka, red wine, white wine, champagne, cava, scrumpy
# - that's enough for scope of this exersize


fish_basic = {'anchovies','barracuda','basa','bass','black cod','blowfish','bluefish','bombay duck','bream','brill','butter fish','catfish','cod','dogfish','dorade','eel','flounder','grouper','haddock','hake','halibut','herring','ilish','john dory','lamprey','lingcod','mackerel','mahi mahi','monkfish','mullet','orange roughy','parrotfish','patagonian toothfish','perch','pike','pilchard','pollock','pomfret','pompano','sablefish','salmon','sanddab','sardine','sea bass','shad','shark','skate','smelt','snakehead','snapper','sole','sprat','sturgeon','surimi','swordfish','tilapia','tilefish','trout','tuna','turbot','wahoo','whitefish','whiting','witch','whitebait'}
# exceptions, sub sets & alternate names
# different name same fish
fish_alt = [
    {'black cod','sablefish'},
    {'patagonian toothfish', 'chilean sea bass'},
    {'dab', 'sanddab'},
    {'red snapper','northern red snapper'},
    {'witch','righteye flounder'}
]

# subsets
fish_subsets = {
    'cod' : { 'pacific cod', 'atlantic cod' },
    'bass' : {'bass','striped bass'},
    'sanddab' : {'pacific sanddab'},   # there are a lot of these
    'shad' : {'alewife','american shad'},
    'eel' : {'eel','conger eel'},
    'trout' : {'trout','rainbow trout'},
    'snapper' : {'rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
    'tuna' : {'albacore tuna','yellowfin tuna','bigeye tuna','bluefin tuna','dogtooth tuna'}    
}

def git ():
    fish = {'fish'}
    
    for key, val in fish_subsets.items():
        union = val | {key}     # include the categegory generalisation
        fish = fish | union
        
    for val in fish_alt:
        fish = fish | val       # include different names for each fish
    
    fish = fish | fish_basic
    
    return fish


conv_list ='''
plain text list here
'''

# def get_allergens_from_ingredients(igds):    
#     return 'dairy, eggs, peanuts, nuts, seeds_lupin, seeds_sesame, seeds_mustard, fish, molluscs, shellfish, alcohol, celery, gluten, soya, sulphur_dioxide'
# 
# def get_tags_from_ingredients(igds):
#     return 'vegan, veggie, cbs, chicken, pork, beef, seafood, shellfish, gluten_free, ns_pregnant'
# 
# def get_type_from_ingredients(igds):
#     return 'component, amuse, side, starter, fish, lightcourse, main, crepe, dessert, p4, cheese, comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot'




def main():
    pass

if __name__ == '__main__':
    
    # fish = ''
    # for m in re.finditer(r'^(.*?)$', conv_list, re.MULTILINE | re.DOTALL):
    #     fish += f"'{m.group(1).lower()}',"         
    #     print(f"'{m.group(1).lower()}'")
    #     
    # print(fish)
    # sys.exit()

    # fish_basic, fish_alt (list of sets), fish_subsets (dict of sets)
    # fish = {'fish'}
    # print(len(fish), fish)
    # 
    # for key, val in fish_subsets.items():
    #     print(key, val)
    #     union = val | {key}     # include the categegory generalisation
    #     fish = fish | union
    #     print(union)
    #     print()
    #     
    # print(len(fish), fish)    
    # 
    # for val in fish_alt:
    #     print(val)
    #     fish = fish | val       # include different names for each fish
    #     print()
    #     
    # print(len(fish), fish)
    # 
    # fish = fish | fish_basic
    # 
    # print(len(fish), fish)
    
    print(build_fish_set())