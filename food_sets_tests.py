#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import re
import sys
import unittest

from collections import Counter
from pathlib import Path
from pprint import pprint

from food_sets import atomic_LUT
from food_sets import brackets_balance, replace_base_bracket_items

from food_sets import get_allergens_for, get_containsTAGS_for

from food_sets import process_OTS_i_string_into_allergens_and_base_ingredients
from food_sets import get_ingredients_as_text_list_R 
from food_sets import nutridoc_scan_to_exploded_i_list_and_allergens


# 'chicken','pork','beef','shellfish' ('molluscs','crustacean'),'lamb','fish','game','gluten_free','vegan','veggie','other' = 'insect, ausie game'

class Food_sets_test(unittest.TestCase):
    # https://www.tesco.com/groceries/en-GB/products/288610223 - Tesco Garlic Flatbread 255G
    tsc_00 = 'INGREDIENTS: Wheat Flour [Wheat Flour, Calcium Carbonate, Iron, Niacin, Thiamin], Water, Rapeseed Oil, Butter (Milk) (1.5%), Durum Wheat Semolina, Salt, Sugar, Wheat Fibre, Garlic (0.8%), Yeast, Parsley, Buttermilk Powder (Milk), Concentrated Lemon Juice.'
    tsc_00_i_list = ['wheat flour','wheat flour','calcium carbonate','iron','niacin',' thiamin','water','rapeseed oil','butter','durum wheat semolina','salt, sugar','wheat fibre','garlic','yeast','parsley','buttermilk powder','concentrated lemon juice']
    tsc_00_alg = ['gluten','dairy']
    tsc_00_tag = ['veggie']

    # https://www.tesco.com/groceries/en-GB/products/252354673 - Sharwoods Real Oyster Sauce 150Ml
    tsc_01 = 'Water, Sugar, Oyster Extract (9%) (Water, Oyster (Molluscs), Salt), Modified Tapioca Starch, Salt, Wheat Flour, Acid (Lactic Acid), Colour (Ammonia Caramel)'
    tsc_01f = 'Water, Sugar, Oyster Extract (9%) (Water, Oyster (Molluscs], Salt), Modified Tapioca Starch, Salt, Wheat Flour, Acid (Lactic Acid), Colour (Ammonia Caramel)'
    tsc_01_i_list = ['water','sugar','oyster extract','oyster','salt','modified tapioca starch','wheat flour','lactic acid','ammonia caramel']
    tsc_01_alg = set(['molluscs','gluten'])
    tsc_01_tag = set(['shellfish'])

    # https://www.tesco.com/groceries/en-GB/products/289204714 - Mcvities Gold Chocolate Biscuit 8 Pack 176G
    # 'dairy, 'soya', gluten' FROM 'Milk', 'Soya', 'Wheat', 'Barley'
    tsc_02 = 'Caramel Flavour Coating (70%) [Sugar, Vegetable Oil (Palm), Dried Whole Milk, Dried Skimmed Milk, Lactose (Milk), Emulsifier (Soya Lecithin), Colours (Mixed Carotenes, Paprika Extract), Natural Flavouring], Flour (Wheat Flour, Calcium, Iron, Niacin, Thiamin), Sugar, Crisped Rice [Rice Flour, Wheat Flour, Sugar, Barley Malt Flour, Salt, Vegetable Oil (Rapeseed), Emulsifier (Soya Lecithin)], Vegetable Oil (Palm), Partially Inverted Sugar Syrup, Raising Agents (Sodium Bicarbonate, Ammonium Bicarbonate, Tartaric Acid), Salt'
    tsc_02f = 'Caramel Flavour Coating (70%) [[Sugar, Vegetable Oil (Palm), Dried Whole Milk, Dried Skimmed Milk, Lactose (Milk), Emulsifier (Soya Lecithin), Colours (Mixed Carotenes, Paprika Extract), Natural Flavouring], Flour (Wheat Flour, Calcium, Iron, Niacin, Thiamin), Sugar, Crisped Rice [Rice Flour, Wheat Flour, Sugar, Barley Malt Flour, Salt, Vegetable Oil (Rapeseed), Emulsifier (Soya Lecithin)], Vegetable Oil (Palm), Partially Inverted Sugar Syrup, Raising Agents (Sodium Bicarbonate, Ammonium Bicarbonate, Tartaric Acid), Salt'

    # https://www.tesco.com/groceries/en-GB/products/274663688
    # 'crustacean','gluten' FROM 'Crustacean','Wheat Flour','Wheat Starch','Wheat Gluten' # 
    tsc_03 = 'Scampi (Crustacean) (37%), Wheat Flour [Wheat Flour, Calcium Carbonate, Iron, Niacin (B3), Thiamin (B1)], Rapeseed Oil, Water, Potato Starch, Wheat Starch, Rice Flour, Wheat Gluten, Modified Maize Starch, Yeast, Salt, Oat Fibre, Raising Agents: Diphosphates, Sodium Bicarbonate, Stabilisers: Sodium Carbonate, Sodium Bicarbonate, Citric Acid, Dextrose, Cornflour, White Pepper'
    tsc_03_i_list = ['Scampi (Crustacean) (37%)','Wheat Flour [Wheat Flour','Calcium Carbonate','Iron','Niacin (B3)','Thiamin (B1)]','Rapeseed Oil','Water','Potato Starch','Wheat Starch','Rice Flour','Wheat Gluten','Modified Maize Starch','Yeast','Salt','Oat Fibre','Raising Agents: Diphosphates','Sodium Bicarbonate','Stabilisers: Sodium Carbonate','Sodium Bicarbonate','Citric Acid','Dextrose','Cornflour','White Pepper']
    tsc_03_alg = ['crustaceans', 'gluten']
    tsc_03_tag = ['shellfish']
    # # 'chicken','pork','beef','shellfish' ('molluscs','crustacean'),'lamb','fish','game','gluten_free','vegan','veggie','other' = 'insect, ausie game'


    # https://www.tesco.com/groceries/en-GB/products/263807542
    # 'eggs','dairy' FROM 'Reconstituted Dried Egg','Cheese Powder (Milk)','','','','','','',
    tsc_04 = 'INGREDIENTS: Rapeseed Oil, Water, White Wine Vinegar, Reconstituted Dried Egg, Lemon Juice from Concentrate, Italian Style Cheese Paste (4%), Sugar, Garlic Purée (2.5%), Worcester Sauce (Water, Sugar, Spirit Vinegar, Molasses, Onion Purée, Salt, Tamarind Paste, Clove, Ginger Purée, Garlic Purée), Salt, Acidity Regulator (Citric Acid), Thickener (Xanthan Gum), Black Pepper, Preservative (Potassium Sorbate). Italian Style Cheese Paste (4%)(Cheese Powder (Milk), Glucose Syrup, Water, Yeast Extract, Salt, Flavouring, Sunflower Oil)'

    # # 
    # # '','','','','','','','','','',
    # tsc_0 = ''
    # tsc_0_i_list = []
    # tsc_0_alg = ['dairy', 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'molluscs', 'crustaceans', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide']
    # tsc_0_tag = ['chicken','pork','beef','shellfish','lamb','fish','game','gluten_free','vegan','veggie','other']
    # # 'chicken','pork','beef','shellfish' ('molluscs','crustacean'),'lamb','fish','game','gluten_free','vegan','veggie','other' = 'insect, ausie game'
    
    def test_bracket_checker_00(self):
        """
        Brackets
        """
        expected_value = True
        
        actual_value = brackets_balance('()([[{}]])(())((({[[]]})))')        

        self.assertEqual(expected_value, actual_value)

    def test_bracket_checker_00f(self):
        """
        Brackets
        """
        expected_value = False
        
        actual_value = brackets_balance('()([[{}]])(())((({[[[[]]]})))')

        self.assertEqual(expected_value, actual_value)

    def test_bracket_checker_01(self):
        """
        Brackets 
        """
        expected_value = True
        
        actual_value = brackets_balance(Food_sets_test.tsc_00)        

        self.assertEqual(expected_value, actual_value)

    def test_bracket_checker_01f(self):
        """
        Brackets 
        """
        expected_value = False
        
        actual_value = brackets_balance(Food_sets_test.tsc_01f)        

        self.assertEqual(expected_value, actual_value)

    def test_bracket_checker_02(self):
        """
        Brackets 
        """
        expected_value = True
        
        actual_value = brackets_balance(Food_sets_test.tsc_02)        

        self.assertEqual(expected_value, actual_value)

    def test_bracket_checker_02f(self):
        """
        Brackets 
        """
        expected_value = False
        
        actual_value = brackets_balance(Food_sets_test.tsc_02f)        

        self.assertEqual(expected_value, actual_value)

    def test_bracket_checker_02f(self):
        """
        Brackets 
        """
        expected_value = False
        
        actual_value = brackets_balance(Food_sets_test.tsc_02f)        

        self.assertEqual(expected_value, actual_value)

    def test_base_brackets_00(self):        
        """
        Remove most nested sets of brackets
        """
        data = 'jibber ( more of the same (funny) (ingredients)  )'
        expected_value = 'jibber ( more of the same, funny , ingredients  )'
        
        actual_value = replace_base_bracket_items(data)
        
        self.assertEqual(expected_value, actual_value)

    def test_base_brackets_01 (self):        
        """
        Remove most nested sets of brackets
        """
        data = 'jibber ( more of the same (funny) [ingredients]  )'
        expected_value = 'jibber ( more of the same, funny , ingredients  )'
        
        actual_value = replace_base_bracket_items(data)
        
        self.assertEqual(expected_value, actual_value)

    def test_base_brackets_02 (self):        
        """
        Remove most nested sets of brackets
        """
        tsc_02_r1 = ' caramel flavour coating, 70% [sugar, vegetable oil, palm, dried whole milk, dried skimmed milk, lactose, milk, emulsifier, soya lecithin, colours, mixed carotenes, paprika extract, natural flavouring], flour, wheat flour, calcium, iron, niacin, thiamin, sugar, crisped rice [rice flour, wheat flour, sugar, barley malt flour, salt, vegetable oil, rapeseed, emulsifier, soya lecithin], vegetable oil, palm, partially inverted sugar syrup, raising agents, sodium bicarbonate, ammonium bicarbonate, tartaric acid, salt'        
        self.assertEqual(tsc_02_r1, replace_base_bracket_items(Food_sets_test.tsc_02))

    def test_base_brackets_03 (self):        
        """
        Remove most nested sets of brackets
        """
        tsc_02_r1 = replace_base_bracket_items(Food_sets_test.tsc_02)
        tsc_02_r2 = ' caramel flavour coating, 70% , sugar, vegetable oil, palm, dried whole milk, dried skimmed milk, lactose, milk, emulsifier, soya lecithin, colours, mixed carotenes, paprika extract, natural flavouring, flour, wheat flour, calcium, iron, niacin, thiamin, sugar, crisped rice, rice flour, wheat flour, sugar, barley malt flour, salt, vegetable oil, rapeseed, emulsifier, soya lecithin, vegetable oil, palm, partially inverted sugar syrup, raising agents, sodium bicarbonate, ammonium bicarbonate, tartaric acid, salt'
        self.assertEqual(tsc_02_r2, replace_base_bracket_items(tsc_02_r1))    

    # - - - - -

# - - - - - - - - - - - - - 
    # # https://www.tesco.com/groceries/en-GB/products/252354673 - Sharwoods Real Oyster Sauce 150Ml
    # tsc_01 = 'Water, Sugar, Oyster Extract (9%) (Water, Oyster (Molluscs), Salt), Modified Tapioca Starch, Salt, Wheat Flour, Acid (Lactic Acid), Colour (Ammonia Caramel)'
    # tsc_01f = 'Water, Sugar, Oyster Extract (9%) (Water, Oyster (Molluscs], Salt), Modified Tapioca Starch, Salt, Wheat Flour, Acid (Lactic Acid), Colour (Ammonia Caramel)'
    # tsc_01_i_list = ['water','sugar','oyster extract','oyster','salt','modified tapioca starch','wheat flour','lactic acid','ammonia caramel']
    # tsc_01_alg = ['molluscs','gluten']
    # tsc_01_tag = ['shellfish']


    #scan_for_seafood_and_fish

    def test_i_list_from_ots_i_string_01(self):
        """
        OTS info processing - i_list
        """
        expected_value = sorted(Food_sets_test.tsc_01_i_list)
        
        ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(Food_sets_test.tsc_01)
        
        actual_value = sorted(ots_info['i_list'])

        self.assertEqual(expected_value, actual_value)

    def test_allergens_from_ots_i_string_01(self):
        """
        OTS info processing - allergens
        """
        expected_value = Food_sets_test.tsc_01_alg
        
        ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(Food_sets_test.tsc_01)
        
        actual_value = ots_info['allergens']

        self.assertEqual(expected_value, actual_value)

    def test_allergens_01(self):
        """
        Get list of allergens from ingredients list
        """
        
        expected_value = set(['molluscs','gluten'])
        
        actual_value = get_allergens_for(Food_sets_test.tsc_01_i_list)
        
        self.assertEqual(expected_value, actual_value)        


    def test_contains_TAGS_01(self):
        """
        Get list of tags from ingredients list
        """
        
        expected_value = set(['shellfish'])
        
        actual_value = set(get_containsTAGS_for(Food_sets_test.tsc_01_i_list))
        
        self.assertEqual(expected_value, actual_value)   


    def test_allergens_processed_food(self):
        """
        Get list of allergens from ingredients list
        """
        i_list = ['cured trout', 'salted duck egg', 'smoked cheese', 'fried bread', 'dried prawn', 'boiled edamame']
        
        expected_value = set(['fish','eggs','dairy','gluten','crustaceans','soya'])
        
        actual_value = get_allergens_for(i_list)
        
        self.assertEqual(expected_value, actual_value)    

    def test_TAGS_processed_food(self):
        """
        Get list of allergens from ingredients list
        """
        i_list = ['cured ham', 'salted cod', 'smoked egg yolk', 'fried bread', 'dried beef', 'boiled milk']
        
        expected_value = set(['pork','fish','beef'])
        
        actual_value = set(get_containsTAGS_for(i_list))
        
        self.assertEqual(expected_value, actual_value)   

    # TODO can wee loop through a set of test with arrays of data?

    def test_get_derived_i_list_allergies(self):
        """
        Get list of allegens from list of ingredients of any type
        """
        
        expected_value = Food_sets_test.tsc_01_alg
        
        composite = nutridoc_scan_to_exploded_i_list_and_allergens(Food_sets_test.tsc_01_i_list,'')

        actual_value = get_allergens_for(composite['allergens'])
        
        self.assertEqual(expected_value, actual_value)   

# ==== random tests
    def test_TAGS_r000(self):
        """
        Apple should be gluten_free
        """
        i_list = ['apple', 'banana', 'water melon', 'coconut']
        
        expected_value = set(['gluten_free','veggie','vegan'])
        
        actual_value = set(get_containsTAGS_for(i_list))
        
        self.assertEqual(expected_value, actual_value)   

    def test_TAGS_r001(self):
        """
        Apple should be gluten_free
        """
        i_list = ['apple', 'banana', 'water melon', 'coconut', 'boiled milk']
        
        expected_value = set(['gluten_free','veggie'])
        
        actual_value = set(get_containsTAGS_for(i_list))
        
        self.assertEqual(expected_value, actual_value)   

    def test_TAGS_r002(self):
        """
        Roast lamb should should tag as lamb!
        """
        i_list = ['roast lamb shoulder']
        
        expected_value = set(['lamb'])
        
        actual_value = set(get_containsTAGS_for(i_list))
        
        self.assertEqual(expected_value, actual_value)   

    # def test_get_OTS_i_list(self):
    #     """
    #     Get list of ingredients from string
    #     """
        
    #     expected_value = set(tsc_01_i_list)
        
    #     actual_value = get_allergens_for(Food_sets_test.tsc_01)
        
    #     self.assertEqual(expected_value, actual_value)   


if __name__ == '__main__':
    
    ots_i_list = {}

    for i in atomic_LUT:
        if atomic_LUT[i]['igdt_type'] == 'ots' and atomic_LUT[i]['ingredients'] != '__igdts__':
            ots_i_list[i] = atomic_LUT[i]['ingredients']


    # TEST FODDER
    ots_check_list = [
        'chicken frankfurter',
        'preserved herring',
        'scampi',                       # 'Wholetail Scampi (Nephrops Norvegicus) (Crustacean) - remove 'wholetail scampi', 'scampi' from crustaceans_alt 
                                        # the fish section should catch the crustacean allergy even if its not explicitly in the set!
        #'scampi & sushi w garlic bread', # vegan? contains 's&p prawn arancini' . . in fact the tree for this is monster 
        # 's&p prawn arancini',           # {'dairy', 'eggs', 'celery', 'gluten', 'crustaceans'}
        # 'ap',
        # 'chicken stock cube',
        # 'nik naks',                     # Natural Flavourings (contains Barley Malt Vinegar, Barley Malt Extract, Soya Sauce, Wheat Flour)
        # 'asda sweet pickled gherkin',   # Flavouring (contains Celery)
        # 'mussels in white wine',
        # 'grana padano',
        # 'mrs hazelnut spread',
        # 'aldi lrg beef yorkie',
        # 'sbs greek yogurt',
        # 'white chocolate cookies',
        #'haricot beans',               # recursion test self referencing ingredient 
        'sbs bakewell tarts',
        'cumberland sausage',
        'veg stock'         # weird symbols in i_list # https://www.sainsburys.co.uk/gol-ui/product/knorr-stock-cubes--vegetable-x8-80g
        'actimel veg',      # weird symbols in i_list # https://www.sainsburys.co.uk/gol-ui/product/actimel-strawberry-yogurt-12x100g
        'lambs lettuce',    # has INGREDIENT: in i_list NO S
        'wasabi paste',
        'chocolate',
        '',
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
        ots_info = process_OTS_i_string_into_allergens_and_base_ingredients(i_string)        
        print(f"i_list--: {ots_info['i_list']}")
        print(f"allergens--: {ots_info['allergens']}")
        print('=======     =======     =======\n')

    print(f"= = = = = = {'scampi & sushi w garlic bread'} = = = = = = =")
    e_list = get_ingredients_as_text_list_R('scampi & sushi w garlic bread')
    print(e_list)
    print(f"= = = = = = ALLERGENS {'scampi & sushi w garlic bread'} = = = = = = =")
    print(get_allergens_for(e_list))



    # Tests
    # functions
    [
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',        
    ]
    balancing = brackets_balance('()([[{}]])(())((({[[]]})))', True)
    print(f'brackets_balance: {balancing}')
    
    print("\n\n- - - - unittest - - S")
    unittest.main()
    print("\n\n- - - - unittest - - E")


    # get_allergens_for(exploded_list_of_ingredients, show_provenance=False)
    # replace_base_bracket_items(i_string, sub_group_id=0, i_tree={})
    # scan_for_seafood_and_fish(i_string)

    # process_OTS_i_string_into_allergens_and_base_ingredients(i_string, ri_name='')
    
    # get_exploded_ingredients_as_list_from_list
    
    # get_ingredients_as_text_list_R(recipe_component_or_ingredient, d=0):

    # get_exploded_ingredients_and_components_for_DB_from_name(comps_and_rcoi, d=0):

    # get_containsTAGS_for(list_of_ingredients, show_provenance=False)

    # does_component_contain_allergen(component, allergen)    # where is this used?
    
    # OTS - TODO comment  #'wholetail scampi', 'scampi'}, back in food_sets once done
    # 10 i_string from Tesco
    # 10 i_string from Sainsburys
    # 10 i_string from Waitrose
    # 10 i_string from Morrison
    # 10 i_string from Aldi
    # ots_info = process_OTS_i_string_into_allergens_and_base_ingredients




    # i_tree 