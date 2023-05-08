#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import re
import sys
from collections import Counter
from pathlib import Path
from pprint import pprint

from food_sets import atomic_LUT
from food_sets_refactor import brackets_balance

# compare
from food_sets          import process_ots_ingredient_string
from food_sets_refactor import process_ots_i_string_into_allergens_and_base_ingredients

from food_sets          import get_allergens_for_refactor                        # calls get_ingredients_as_text_list_R
from food_sets_refactor import get_allergens_for_refactor as get_allergens_for_R

# from food_sets          import 
# from food_sets_refactor import 

# from food_sets          import 
# from food_sets_refactor import 

# from food_sets          import 
# from food_sets_refactor import 



from food_sets import parse_igdt_lines_into_igdt_list   # ', '.join(get_allergens_for(parse_igdt_lines_into_igdt_list(ingredients))),
#from food_sets import errors
#from food_sets import scan_for_error_items
from food_sets import get_exploded_ingredients_as_list_from_list    # calls get_ingredients_as_text_list_R


if __name__ == '__main__':
    
    ots_i_list = {}

    for i in atomic_LUT:
        if atomic_LUT[i]['igdt_type'] == 'ots' and atomic_LUT[i]['ingredients'] != '__igdts__':
            ots_i_list[i] = atomic_LUT[i]['ingredients']


    # TEST FODDER
    ots_check_list = [
        'preserved herring',
        'scampi',
        'ap',
        'chicken stock cube',
        'mussels in white wine',
        'grana padano',
        'mrs hazelnut spread',
        'aldi lrg beef yorkie',
        'sbs greek yogurt',
        'white chocolate cookies',
        #'haricot beans',               # recursion test self referencing ingredient    
    ]
    derived_check = [
        '',
        '',
        '',
        '',
        '',
    ]
    # some exceptions
    # 'isolate',
    # 'including 113g of poultry meat',
    # '100 g of product made from 160 g meat',

    for ri_name in ots_check_list:
        i_string = ots_i_list[ri_name]
        print(f"\n\n\nR======= {ri_name} - brackets_balance:{brackets_balance(i_string)} =======     =======     =======\n\n{i_string}")        
        ots_info = process_ots_ingredient_string(i_string)        
        ots_info_R = process_ots_i_string_into_allergens_and_base_ingredients(i_string)        
        print(f"i_list--: {ots_info['i_list']}")
        print(f"i_list-R: {ots_info_R['i_list']}")
        print(f"allergens--: {ots_info['allergens']}")
        print(f"allergens-R: {ots_info_R['allergens']}")
        print('=======     =======     =======\n')


    # for ri_name in ots_i_list:
    #     i_string = ots_i_list[ri_name]
    #     print(f"\n\n\nR======= {ri_name} - brackets_balance:{brackets_balance(i_string)} =======     =======     =======\n\n{i_string}")
    #     if ri_name == 'white chocolate cookies':
    #         print("break")
    #     ots_info = process_ots_i_list_into_allergens_and_base_ingredients(i_string)
    #     print(f"i_string: {ots_info['i_string']}")
    #     print(f"i_list (classifiers removed): {ots_info['i_list']}")
    #     print(f"allergens: {ots_info['allergens']}")
    #     print('=======     =======     =======\n')
    
    # print(get_allergens_for(['flour','milk','butter','eggs','sugar']))
    # print(get_allergens_for(['s&p ribs w prawns & squid', 's&p coating', 'dried chillies', 's&p ribs', 'aromat', 'black pepper', 'bread flour', 'chillies', 'corn flour', 'eggs', 'garlic', 'ginger', 'octopus', 'olive oil', 'pork ribs', 'prawns', 'red onion', 'red pepper', 'salt', 'spring onions', 'szechuan pepper']))
    # print(get_allergens_for(['s&p ribs w prawns & squid']))
    # print()
    # pprint(ots_info)
    # #pprint(all_sub_groups, width=160)




