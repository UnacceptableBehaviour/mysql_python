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
# alcohol classification should be limited to rum, vodka, red wine, white wine, champagne, cava - that's enough for this




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
    main()
    
    
