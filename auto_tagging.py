#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import json

from pprint import pprint
from pathlib import Path

from helper_nutrinfo import i_db



def get_allergens_from_ingredients(igds):    
    return 'dairy, eggs, peanuts, nuts, seeds_lupin, seeds_sesame, seeds_mustard, fish, molluscs, shellfish, alcohol, celery, gluten, soya, sulphur_dioxide'

def get_tags_from_ingredients(igds):
    return 'vegan, veggie, cbs, chicken, pork, beef, seafood, shellfish, gluten_free, ns_pregnant'

def get_type_from_ingredients(igds):
    return 'component, amuse, side, starter, fish, lightcourse, main, crepe, dessert, p4, cheese, comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot'

#
#
#
#
# move these functions into apprpriate helper after dev
LINE_TEST_DATA_FILE = Path('/Users/simon/a_syllabus/lang/python/repos/mysql_python/scratch/igdt_test_data.txt')
def parse_igdt_lines_into_sets(lines=[]):
    i_list = []
    
    with LINE_TEST_DATA_FILE.open('r') as f:
        lines = f.readlines()

    # remove qty & comment from each line    
    for line in lines:
        #parts = [ item.strip() for item in line.split('\t') if len(item) > 0 ] # include comment in lists
        parts = [ item.strip() for item in line.split('\t') if (len(item) > 0) & ('#' not in item) & ('(' not in item) ] # remove comments
        parts.pop(0)    # remove qty
        try: 
            i_list.append(parts.pop(0))
        except IndexError:
            pass

    # remove duplicates from list
    i_list = list(dict.fromkeys(i_list))
    # remove empty strings    
    i_list = list(filter(None, i_list))
    
    return i_list   #print(i_list)


if __name__ == '__main__':
    pprint( i_db.get('apple') )
    
    # i_list = parse_igdt_lines_into_sets()
    # 
    # for i in i_list:
    #     pprint( i_db.get(i) )
    
