#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import re
import sys
from collections import Counter
from pathlib import Path
from pprint import pprint

from food_sets import atomic_LUT, filter_noise, get_allergens_headings

#from food_sets import process_ots_ingredient_string


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

    #print(f"<{'-'.join(brackets).strip()}>")
    return(len(brackets) == 0)

# regex [\([{})\]]                      any bracket []{}()
# regex ([\([{]([^\([{})\]]+)[})\]])    find items surrounded witha pair of brackets
# like: 
#    group 1 - preceding text
#    |             group 2 - content w/ brackets - use to replce
#    |             |          group 3 - content w/o brackets
#    |             |          |
#  ,([\s\w]+)   (  [\([{]  (  [^\([{})\]]+  )  [})\]]  )                        < < - - - - #
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

set_i_classifiers = set(['preservative','preservatives','colour','acidity regulator','emulsifier','antioxidant','antioxidants','stabiliser','stabilisers','stabilizer','stabilizers','acidity regulators','raising agents','vegetable fats','preservatives','colours','natural flavouring','flavour enhancer','vitamins','emulsifiers','flavouring','herbs','roasted sliced nuts','seed mix','medium fat hard cheese','spice extracts','gelling agent','sweeteners','raising agent','gelling agents','firming agent','flour treatment agent','flavour enhancers','natural flavourings','live bacterial cultures','thickener','acid','humectant','acids','flavourings','colouring','vegetable oils and fats','vegetables','mixed seeds'])
#set_igdts = set('wheat flour','spices','fortified british wheat flour','vegetable oils','lactose','butter','whey powder','fortified wheat flour','niacin','thiamin','milk','unsalted butter','vegetable oil','yogurt','mussels','alaska pollock','hake','oyster','butterfat','calcium','lecithins','cheese','cheese powder','cream','low fat yogurt','malt vinegar','anchovies','soya extract','mackerel','greek style natural yogurt','extra mature cheddar cheese','single cream','mozzarella cheese','flour','emmental cheese','semolina','half cream','manchego cheese','whipped cream','white wine','salt','grana padano cheese','moistened sultanas','moistened raisins','moistened chilean flame raisins','curry powder','seasoning with sea salt and balsamic vinegar of modena','poultry meat','salmon','rusk','butteroil','vegetable margarine','sausage casing','salted butter','squid','herring fillets','parmigiano reggiano medium fat hard cheese','worcestershire sauce','worcester sauce','anchovy','dried cream','pork','breadcrumbs','cooked marinated lamb','malt extract','herring','wholetail scampi','butter oil','mayonnaise','hydrolysed vegetable protein','casing','halloumi cheese','wood smoked mussels','chaource cheese','prawns','king prawn','paprika','beef extract powder','anchovy extract','lemon juice powder')


global_subgroup_id = 0
all_sub_groups = {}
latin_names = {}
sub_groups = {}
allergens = set()
def print_subgroups(sg):
    print()
    for key in sg:
        print(f"\t{key} - {sg[key]}")

# scan for base brackets
# if allergen leave item remove allergen & addit ti allergens set
# if list of ingredients expand 
def replace_base_bracket_items(ots_info, sub_group_id=0, i_tree={}):
    global global_subgroup_id
    
    i_string = ots_info['i_string']
    i_string = i_string.lower()     

    matches = re.findall(rgx_bracket_pair_with_title, i_string)
    pprint(matches)
    if matches:
        for m in matches:
            title, content_w_brk, content = m[0], m[1], m[2]
            replace_txt = title + content_w_brk
            
            sub_group_id_str = f"##{sub_group_id:03}"
            sub_group_id += 1
            sub_groups[sub_group_id_str] = { title: content }

            sub_group_id_str = f"##{global_subgroup_id:03}"
            global_subgroup_id += 1
            all_sub_groups[sub_group_id_str] = { title: replace_txt }
            
            i_string = i_string.replace(replace_txt, sub_group_id_str)
            i_tree = [ i.strip() for i in i_string.split(',') ]

        print_subgroups(sub_groups)
        print(f"\ni_string: {i_string}\n")

    else:
        i_tree = [ i.strip() for i in i_string.split(',') ]
        
    return i_tree

# some exceptions
# 'isolate',
# 'including 113g of poultry meat',
# '100 g of product made from 160 g meat',

# 'antioxidant: sodium metabisulphite',
# 'preservative: lysozyme',
# 'emulsifier: lecithins',
# 'preservative:sodium metabisulphite',
# 'preservatives: sodium metabisulphite',

def scan_for_seafood_and_fish(i_string):
    #global global_subgroup_id

    allergens = set()

    i_string = i_string.lower()

    print(f"\ni_string-i: {i_string}\n")

    matches = re.findall(rgx_pullout_seafood, i_string)
    pprint(matches) # TODO remove / log

    if matches:
        for m in matches:
            title, latin, allergen = m[0], m[1], m[2]
            
            allergens.add(allergen)
            
            if not latin: latin = ''                                     # latin not present
            else: latin = latin.replace('(', '\\(').replace(')', '\\)')  # (mytilus spp.) < with brackets
            replace_rgx = f"{title}\\s*{latin}\\s*\\({allergen}\\)"
            
            # sub_group_id_str = title
            # sub_group_id += 1
            # sub_groups[sub_group_id_str] = { title: (latin, allergen, replace_rgx) }

            # sub_group_id_str = f"##{global_subgroup_id:03}"
            # global_subgroup_id += 1
            # all_sub_groups[sub_group_id_str] = { title: (latin, allergen, replace_rgx) }
            
            i_string = re.sub(replace_rgx, f'{title}', i_string)

#        print_subgroups(sub_groups)
    
    print(f"\ni_string-r: {i_string}\n")

    return {'i_string':i_string, 'allergens': allergens} 




# ALLERGENS ARE THE REAL TARGETS HERE
# replace (x%)
# replace ; with ,
# scan for fish/seafood w/ latin names allergens in () (mollusc) remove - record allergens
# scan for allergens in () (milk) remove - record
# while (there are still base brackets)
#   title will be classifier or ingredient
# scan for ':'
# think about blowing the stack haricot bean bug - tinned beans
def proces_ots_i_list_into_allergens_and_base_ingredients(i_string, ri_name, i_tree={}):
    # replace (x%)
    i_string = filter_noise(i_string, False)  # TODO test contains vs contains: may may contain

    # replace ; with ,
    i_string = i_string.replace(';', ',')

    # scan for fish/seafood w/ latin names allergens in () (mollusc) remove - record allergens
    ots_info = scan_for_seafood_and_fish(i_string)

    # loop until bracket pairs removed
    # matches = re.findall(rgx_bracket_pair_with_title, ots_info['i_string'])  
    # while(matches):
    #     next_list = replace_base_bracket_items(ots_info)

    #     matches = re.findall(rgx_bracket_pair_with_title, ots_info['i_string'])  




def ast_from_ots_i_list(i_list, ri_name):
    if not brackets_balance(i_list):
        raise(f'BRACKET DONT BALANCE in i_list: {ri_name}')
    

def process_ots_ingredient_string(i_list, ri_name):
    pass

# aliases = {}
# atomic_LUT = {}
# component_file_LUT = {}

if __name__ == '__main__':
    
    ots_i_list = {}

    for i in atomic_LUT:
        if atomic_LUT[i]['igdt_type'] == 'ots' and atomic_LUT[i]['ingredients'] != '__igdts__':
            # print(f"== [{i}]")
            # print(f"\t{atomic_LUT[i]['ingredients']}")
            ots_i_list[i] = atomic_LUT[i]['ingredients']

    ots_i_list['seafood extravaganza'] = "Surimi (46%) (Alaska Pollock (Theragra chalcogramma) (Fish), Hake (Merluccius merluccius) (Fish), Sugar), Water, Sugar, Potato Starch, Wheat Starch, Rapeseed Oil, Salt, Natural Flavouring (contains Crustaceans), Dried Free Range Egg White, Colour:Lycopene, Dried Free Range Egg,Wood Smoked Mussels (Mollusc), Sunflower Oil, Salt,Mussels (Mytilus Spp.) (Mollusc) (88%), Garlic Butter Sauce (12%) [Unsalted Butter (Milk) (35%), Water, Diced Onions, Garlic Purée (7%), Roasted Garlic (7%), Maize Starch, White Wine, Parsley, White Pepper],SQUID (Todarodes Pacificus) (51%) (MOLLUSC), WHEAT Flour, Modified Tapioca Starch, Thickeners: Oxidised Starch, Xanthan Gum, Guar Gum; Cornflour, Sea Salt, Dextrose, Sugar, Raising Agents: Diphosphates, Sodium Carbonates; Yeast, Fully Refined SOYBEAN OIL."
    # print('\n\n')
    # pprint(atomic_LUT['s&p pork arancini w courgette & grape salad'])

    # ots_i_list = [
    #     #'haricot beans'
    #     'sc plain choc',
    #     'green tabasco',
    #     'sbs oyster sauce',
    #     'ap',
    #     'nik naks',
    #     'tesco caesar dressing 175ml',
    #     'sbs grilled sausage meat',
    #     'white chocolate cookies',
    #     'hot cross buns',
    #     'battenberg cake',
    #     'chicken tikka pakora',
    #     'chicken samosa'
    # ]
        
    # # sort ingredient into order of shorted list of ingredients 1st
    # sorted_list = []
    # for ri_name in ots_i_list:
    #     print(f"{len(atomic_LUT[ri_name]['ingredients'])} - {ri_name}")
    #     sorted_list.append((len(atomic_LUT[ri_name]['ingredients']), ri_name))

    # sorted_list.sort(key= lambda x: x[0] )
    # ots_i_list = [tup[1] for tup in sorted_list if tup[1]]
    # #pprint(ots_i_list)

    check_list = ['preserved herring','scampi','','','','','','','','','','','','']

    for ri_name in ots_i_list:
        i_list = ''#process_ots_ingredient_string(atomic_LUT[ri_name]['ingredients'], ri_name)
        i_string = ots_i_list[ri_name]
        print(f"\n\n\nR======= {ri_name} - brackets_balance:{brackets_balance(i_string)} =======     =======     =======\n\n{i_string}")                
        i_string = filter_noise(i_string, False)
        ots_info = scan_for_seafood_and_fish(i_string)
        print('> > - - - - scanned for seafood - - - - brackets next \/ ')
        i_list = replace_base_bracket_items(ots_info)
        print(f"i_string: {ots_info['i_string']}")
        print(f"allergens: {ots_info['allergens']}")
        print('=======     =======     =======\n')
        sub_groups = {}
    
    print_subgroups(all_sub_groups)
    print(get_allergens_headings())
    # add (sulphites) (milk) (from milk) (cows' milk)
    # if get_allergens_headings - loop in bracket

    # titles = []
    # for id, item in all_sub_groups.items():
    #     title, content = item.popitem()
    #     titles.append(title.strip())
    
    # print(f"unique titles:{Counter(titles).most_common()}")
    # for title, count in Counter(titles).most_common():
    #     print(f"'{title}',")



