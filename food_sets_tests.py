#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import re
import sys
from collections import Counter
from pathlib import Path
from pprint import pprint

from food_sets import atomic_LUT, filter_noise, allergenLUT

# returns True if they balance
def brackets_balance(i_string, dbg=False): 
    pair_lut = {
        ')': '(',
        ']': '[',
        '}': '{',
    }
    c_pos = 0
    brackets = []   # stack
    while (c_pos < len(i_string)):
        char = i_string[c_pos]

        if re.match(rgx_any_bracket, char):
            if char in pair_lut and brackets[-1] == pair_lut[char]:
                brackets.pop()
            else:
                brackets.append(char)
            if dbg:
                print(f"<{'-'.join(brackets).strip()}> {char}")
        c_pos += 1

    return(len(brackets) == 0)


# regex [\([{})\]]                      any bracket []{}()
# regex ([\([{]([^\([{})\]]+)[})\]])    find items surrounded witha pair of brackets
# like: 
#    group 1 - preceding text
#    |             group 2 - content w/ brackets - use to replce
#    |             |          group 3 - content w/o brackets
#    |             |          |
#   ([\s\w]+)   (  [\([{]  (  [^\([{})\]]+  )  [})\]]  )                        < < - - - - #
                                                                                            #
rgx_bracket_pair_with_title = re.compile('([\s\w:]+)([\([{]([^\([{})\]]+)[})\]])', re.I) # /

rgx_any_bracket = re.compile('[\([{})\]]')

# latin optional with brackets captured - need them becaus optional
#   makes finding & replacing it trickier without them
rgx_pullout_seafood = re.compile("([\w\s\.]+)(\([\w\s\.]+\)\s*)?\((fish|crustacean(?:s)?|mollusc(?:s)?)\)", re.I)   
# latin optional WITHOUT brackets captured 
# rgx_pullout_seafood = re.compile("([\w\s\.]+)\(?([\w\s\.]+)?\)?\s*\((fish|crustaceans|mollusc)\)", re.I)  
                                                                             #
# "([\w\s\.]+)(\([\w\s\.]+\))?\s*\((fish|crustaceans|mollusc)\)"gmi   > - - /
# 
#     G1                G2      /-optional                  G3  
# ([\w\s\.]+)   (\([\w\s\.]+\))?             \s*  \((fish|crustaceans|mollusc)\)
#       G1                   G2 (optional)        G3
# Alaska Pollock        (Theragra chalcogramma) (Fish), 
# Hake                  (Merluccius merluccius) (Fish)
# Wood Smoked Mussels                           (Mollusc)
# Mussels               (Mytilus Spp.)          (Mollusc) 
# SQUID                 (Todarodes Pacificus)   (MOLLUSC)


# latin_names = {} # seafood
# record all detected subgroup for inspection
global_subgroup_id = 0
all_sub_groups = {}

def get_allergens_for(exploded_list_of_ingredients, show_provenance=False):
    allergens_detected = []
    print(f"get_allergens_for : {exploded_list_of_ingredients}")

    for i in exploded_list_of_ingredients:
        for allergen in allergenLUT:
            if i in allergenLUT[allergen]:
                allergens_detected.append((allergen, i))

    if show_provenance:
        print("ALLERGEN show_provenance:")
        pprint(allergens_detected) 
    
    allergens_detected = set([ a for a,i in allergens_detected])

    return allergens_detected


# scan for base brackets - expand to list of ingredients 
def replace_base_bracket_items(i_string, sub_group_id=0, i_tree={}):
    global global_subgroup_id

    i_string = i_string.lower()     

    matches = re.findall(rgx_bracket_pair_with_title, i_string)
    pprint(matches)
    if matches:
        for m in matches:
            title, content_w_brk, content = m[0], m[1], m[2]
            replace_txt = title + content_w_brk
            with_this = f" {title.strip()}, {content}"

            sub_group_id_str = f"##{global_subgroup_id:03}"
            global_subgroup_id += 1
            all_sub_groups[sub_group_id_str] = { title: replace_txt }
            
            i_string = i_string.replace(replace_txt, with_this)

        #print(f"\ni_string: {i_string}\n")

    return i_string


def scan_for_seafood_and_fish(i_string):

    allergens = set()

    i_string = i_string.lower()

    #print(f"\ni_string-i: {i_string}\n")

    matches = re.findall(rgx_pullout_seafood, i_string)
    pprint(matches) # TODO remove / log

    if matches:
        for m in matches:
            title, latin, allergen = m[0], m[1], m[2]
            
            allergens.add(allergen)
            
            if not latin: latin = ''                                     # latin not present
            else: latin = latin.replace('(', '\\(').replace(')', '\\)')  # (mytilus spp.) < with brackets
            replace_rgx = f"{title}\\s*{latin}\\s*\\({allergen}\\)"
            
            i_string = re.sub(replace_rgx, f'{title}', i_string)
    
    #print(f"\ni_string-r: {i_string}\n")
    return {'i_string':i_string, 'allergens': allergens} 




# - - - ALLERGENS ARE THE REAL TARGETS HERE - - - 
# replace (x%)
# replace ; with ,
# scan for fish/seafood w/ latin names allergens in () (mollusc) remove - record allergens
# scan for allergens in () (milk) remove - record
# while (there are still base brackets)
#   title will be classifier or ingredient
# scan for ':'

set_i_classifiers = set(['preservative','preservatives','colour','acidity regulator','emulsifier','antioxidant','antioxidants',
                         'stabiliser','stabilisers','stabilizer','stabilizers','acidity regulators','raising agents',
                         'vegetable fats','preservatives','colours','natural flavouring','flavour enhancer','vitamins',                         
                         'spice extracts','gelling agent','sweeteners','raising agent','gelling agents','firming agent',
                         'flour treatment agent','flavour enhancers','natural flavourings','live bacterial cultures','thickener',
                         'acid','humectant','acids','flavourings','colouring','vegetable oils and fats','vegetables',
                         'emulsifiers','flavouring','herbs'])
#set_igdts = set('wheat flour','spices','fortified british wheat flour','vegetable oils','lactose','butter','whey powder','fortified wheat flour','niacin','thiamin','milk','unsalted butter','vegetable oil','yogurt','mussels','alaska pollock','hake','oyster','butterfat','calcium','lecithins','cheese','cheese powder','cream','low fat yogurt','malt vinegar','anchovies','soya extract','mackerel','greek style natural yogurt','extra mature cheddar cheese','single cream','mozzarella cheese','flour','emmental cheese','semolina','half cream','manchego cheese','whipped cream','white wine','salt','grana padano cheese','moistened sultanas','moistened raisins','moistened chilean flame raisins','curry powder','seasoning with sea salt and balsamic vinegar of modena','poultry meat','salmon','rusk','butteroil','vegetable margarine','sausage casing','salted butter','squid','herring fillets','parmigiano reggiano medium fat hard cheese','worcestershire sauce','worcester sauce','anchovy','dried cream','pork','breadcrumbs','cooked marinated lamb','malt extract','herring','wholetail scampi','butter oil','mayonnaise','hydrolysed vegetable protein','casing','halloumi cheese','wood smoked mussels','chaource cheese','prawns','king prawn','paprika','beef extract powder','anchovy extract','lemon juice powder')
def process_ots_i_list_into_allergens_and_base_ingredients(i_string):
    orig_i_string = i_string
    # replace (x%)
    i_string = filter_noise(i_string, False)  # TODO test contains vs contains: may may contain

    # replace ; with ,
    i_string = i_string.replace(';', ',')

    # scan for fish/seafood w/ latin names allergens in () (mollusc) remove - record allergens
    ots_info = scan_for_seafood_and_fish(i_string)

    i_string = ots_info['i_string']

    # loop until all bracket pairs removed  -   -   -   -   -   -   -   #
    initial_i_string = i_string                                         #
    i_string = replace_base_bracket_items(initial_i_string)             #
                                                                        #   
    while(initial_i_string != i_string):                                #
        initial_i_string = i_string                                     #
        i_string = replace_base_bracket_items(initial_i_string)         #

    # scan for ':'
    i_string = i_string.replace(':', ',').replace('.', '') # TODO SB replace \..*?$ -  Ie from Full stop to end - NO TIME TO analyse or test
    ots_info['i_string'] = i_string

    # scrub classifiers frim i_list
    i_list = [ i.strip() for i in i_string.split(',') if i.strip() not in set_i_classifiers]

    allergens = get_allergens_for(i_list)

    ots_info['allergens'].update(allergens)
    ots_info['i_list'] = sorted(list(set(i_list)))

    # TODO - fix allergenLUT? food_sets.get_allergens_headings
    if 'molluscs' in ots_info['allergens']: 
        ots_info['allergens'].add('mollusc')
        ots_info['allergens'].discard('molluscs')

    if 'crustaceans' in ots_info['allergens']: 
        ots_info['allergens'].add('crustacean')
        ots_info['allergens'].discard('crustaceans')

    ots_info['orig_i_string'] = orig_i_string

    return ots_info




if __name__ == '__main__':
    
    ots_i_list = {}

    for i in atomic_LUT:
        if atomic_LUT[i]['igdt_type'] == 'ots' and atomic_LUT[i]['ingredients'] != '__igdts__':
            ots_i_list[i] = atomic_LUT[i]['ingredients']


    # TEST FODDER
    check_list = ['preserved herring','scampi','ap','chicken stock cube','mussels in white wine','','','','','','','','','']
    # some exceptions
    # 'isolate',
    # 'including 113g of poultry meat',
    # '100 g of product made from 160 g meat',

    for ri_name in ots_i_list:
        i_string = ots_i_list[ri_name]
        print(f"\n\n\nR======= {ri_name} - brackets_balance:{brackets_balance(i_string)} =======     =======     =======\n\n{i_string}")
        ots_info = process_ots_i_list_into_allergens_and_base_ingredients(i_string)
        print(f"i_string: {ots_info['i_string']}")
        print(f"allergens: {ots_info['allergens']}")
        print('=======     =======     =======\n')
    
    print(get_allergens_for(['flour','milk','butter','eggs','sugar']))
    print(get_allergens_for(['s&p ribs w prawns & squid', 's&p coating', 'dried chillies', 's&p ribs', 'aromat', 'black pepper', 'bread flour', 'chillies', 'corn flour', 'eggs', 'garlic', 'ginger', 'octopus', 'olive oil', 'pork ribs', 'prawns', 'red onion', 'red pepper', 'salt', 'spring onions', 'szechuan pepper']))
    
    #pprint(all_sub_groups, width=160)




