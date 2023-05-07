#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import itertools
from pprint import pprint
from pathlib import Path
from collections import Counter

aliases = {}

atomic_LUT = {}
NUTRIENT_FILE_PATH = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info.txt')
NUTRIENT_FILE_BACKUPS = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_bak')

component_file_LUT = {}
COMPONENT_DIR_PATH = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/')

import json
ots_I_set = set()
OTS_INGREDIENTS_FOUND = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_ots_ingredients_found.json')
if OTS_INGREDIENTS_FOUND.exists():
    with open(OTS_INGREDIENTS_FOUND, 'r') as f:
        content = f.read()
        ots_I_set = set(json.loads(content))

def save_ots_ingredients_found():
    global ots_I_set
    print(f"Prune ots_I_set from: {len(ots_I_set)}")
    ots_I_set = ots_I_set - set(atomic_LUT.keys())      # remove ingredients we know about
    print(f"Saving ots_I_set: {len(ots_I_set)}")    
    
    with open(OTS_INGREDIENTS_FOUND, 'w') as f:
        ots_i_string = json.dumps(list(ots_I_set))
        f.write(ots_i_string)

from timestamping import nix_time_ms
import shutil
def backup_nutrinfo_txt():
    target = NUTRIENT_FILE_BACKUPS.joinpath(f"{nix_time_ms()}_{NUTRIENT_FILE_PATH.name}")
    shutil.copy(NUTRIENT_FILE_PATH, target)
    print(f"BACKUP: {NUTRIENT_FILE_BACKUPS.name}/{target.name}")
    

# atomic_LUT        
# Item: large dried chillies
# {'alias': 'dried chillies',
#  'alias_file': ('y445', '20210511_123843_dried chillies.txt'),
#  'alias_nutrients': True,
#  'igdt_type': 'derived',
#  'ingredients': '__igdts__',
#  'ndb_no': '',
#  'ndb_no_url_alias': 'ndb_no=dried chillies',
#  'txtfile': '',
#  'url': ''}

IGD_TYPE_UNCHECKED = -1
IGD_TYPE_ATOMIC    = 0
IGD_TYPE_DERIVED   = 1
IGD_TYPE_OTS       = 2   # Off The Shelf
IGD_TYPE_DTK       = 3   # Daily TracKer 

def get_igdt_type(ri_name):
    igdt_type = IGD_TYPE_UNCHECKED

    if ri_name in atomic_LUT.keys():
        igdt_type_text = atomic_LUT[ri_name]['igdt_type']
    
        if igdt_type_text == 'atomic':
            igdt_type = IGD_TYPE_ATOMIC
        
        if igdt_type_text == 'derived':
            igdt_type = IGD_TYPE_DERIVED
        
        if igdt_type_text == 'ots':
            igdt_type = IGD_TYPE_OTS    

    return igdt_type


def dump_atomic_LUT(i):
    print(f"{atomic_LUT[i]['igdt_type'].ljust(8)} {str(atomic_LUT[i]['ndb_no']).center(7)} {i.ljust(40)} - {atomic_LUT[i]['txtfile_short']}")
    if atomic_LUT[i]['alias']: print(f"\tA: {atomic_LUT[i]['alias'].ljust(40)} - Nutrinfo:{atomic_LUT[i]['alias_nutrients']} - F:{atomic_LUT[i]['alias_file']} <")
    if atomic_LUT[i]['url']: print(f"\tU: {atomic_LUT[i]['url'].ljust(40)}")
    if atomic_LUT[i]['ingredients']!='__igdts__': print(f"\tIL:{atomic_LUT[i]['ingredients']}")


def follow_alias(i):
    alias = atomic_LUT[i]['alias']
    if alias == 'pkg':  # data was taken from ingredient packaging there is no alias
        return(None)

    if alias:
        if atomic_LUT[alias]['ingredients']!='__igdts__' or atomic_LUT[alias]['url']:
            return(alias)
        if alias in atomic_LUT:
            return(follow_alias(alias))
    else:
        return(None)

# enter prawn to get all components with prawn in the name!
def search(search_term):
    print(f"\n==> Searching for {search_term} . .\n")
    for i in atomic_LUT.keys():
        if re.search(search_term, i):
            dump_atomic_LUT(i)


def build_file_LUT():
    file_list = COMPONENT_DIR_PATH.glob('*_NUTRITEST_recipes_*/_i_w_r_auto_tmp/*.txt')
    for f in file_list:
        m = re.search(r'\d{8}_\d{6}_(.*?).txt', str(f))
        if m:
            #print(f"{m.group(1)} - {f.name}")
            component_file_LUT[m.group(1)] = f
            get_ingredients_from_component_file(m.group(1)) # cache file & log rcoi/ri_name mismatch


errors = {
    'txt_title_NO_match_rcp':[],        # = collected by code (if hash # next to error type)
    'derived_w_file_HAS_ndb_no':[],     #
    'ndb_no_neg99':[],                  #
    'derived_HAS_http_SB_ots': [],      #
    'derived_HAS_atomic_alias':[],
    'ots_ingredients_missing':[],       #
    'ots_NO_url':[],                    #
    'unknown_alias':[],                 #
    'dead_ends_in_this_pass': [],
    'items_not_triggering_TAGS' :[],
    'expected_derived_atomic_no_file': []
}

def build_atomic_LUT(verbose=False):

    content = ''
    with NUTRIENT_FILE_PATH.open('r') as f:
        #content = f.readlines()
        content = f.read()

    # FIRST PASS to get all component names
    for m in re.finditer( r'--- for the nutrition information(.*?)\((.*?)\).*?ingredients:(.*?)$.*?igdt_type:(.*?)$', content, re.MULTILINE | re.DOTALL ):
        component, ndb_no_url_alias, ingredients, igdt_type = m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()
        if component == '': continue
        atomic_LUT[component] = {}   

    print(f"atomic_LUT FOUND ({len(atomic_LUT)})")

    for m in re.finditer( r'--- for the nutrition information(.*?)\((.*?)\).*?ingredients:(.*?)$.*?igdt_type:(.*?)$', content, re.MULTILINE | re.DOTALL ):
        component, ndb_no_url_alias, ingredients, igdt_type = m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()
        if component == '': continue
        # print(f"{component}", end=':')
        # print(f"{component in atomic_LUT.keys()}", end=' ')
        # pprint(atomic_LUT)
        atomic_LUT[component]['ingredients'] = ingredients
        atomic_LUT[component]['igdt_type'] = igdt_type
        atomic_LUT[component]['ndb_no_url_alias'] = ndb_no_url_alias
        # (ndb_no=https://www.bla)      # online resource to ingredient
        # (ndb_no=11367)                # info from FDA DB - \(ndb_no=\d+\)
        # (per 100g)                    # derived ingredient
        # (ndb_no=-99)
        # (ndb_no=sea bream fillets)    # alias to another entry - which could be any of the above

        # find
        # ots w/o __igdts__ NO   URL  - list and add URL
        # ots w/o __igdts__ with URL  - pass to scrape tool       << add helper to retrieve

        txtfile = ''
        txtfile_short = ''
        alias = ''
        url = ''
        ndb_no = ''
        alias_file = ''
        alias_nutrients = False
        
        if (ndb_no_url_alias != 'per 100g'):
            if ndb_no_url_alias == 'ndb_no=-99':
                ndb_no = -99
            else:                
                m1 = re.search(r'ndb_no=\b(\d{5})\b', ndb_no_url_alias)
                m2 = re.search(r'ndb_no=(http.*?$)', ndb_no_url_alias)
                m3 = re.search(r'ndb_no=([\w &]+?$)', ndb_no_url_alias)

                if m1:   ndb_no = m1.group(1)
                elif m2: url    = m2.group(1)
                elif m3: alias  = m3.group(1)


            alias_file_found = alias in component_file_LUT
            if alias_file_found:                
                m = re.search(r'(y\d{3})_NUTRITEST', str(component_file_LUT[alias]))
                alias_file = (m.group(1), component_file_LUT[alias].name)
            
            
            alias_nutrients_found = alias in atomic_LUT
            if alias_nutrients_found:
                alias_nutrients = True
            else:
                errors['unknown_alias'].append((component, alias))

            if component in aliases:
                aliases[component].append((component, alias))
            else:
                aliases[component] = [(component, alias)]        

        if component in component_file_LUT:
            txtfile = component_file_LUT[component]
            m = re.search(r'(y\d{3})_NUTRITEST', str(txtfile))
            txtfile_short = (m.group(1), txtfile.name)    
                
        
        atomic_LUT[component]['txtfile']         = txtfile
        atomic_LUT[component]['txtfile_short']   = txtfile_short
        atomic_LUT[component]['alias']           = alias
        atomic_LUT[component]['url']             = url
        atomic_LUT[component]['ndb_no']          = ndb_no
        atomic_LUT[component]['alias_file']      = alias_file
        atomic_LUT[component]['alias_nutrients'] = alias_nutrients

        
        if (igdt_type == 'derived') and url:
            errors['derived_HAS_http_SB_ots'].append((component, igdt_type, url))
        
        if (ndb_no_url_alias == 'ndb_no=-99'):
            errors['ndb_no_neg99'].append((component, igdt_type))
        
        if (igdt_type == 'ots') and (ingredients == '__igdts__'):
            errors['ots_ingredients_missing'].append((igdt_type, component, ndb_no_url_alias))

        if (igdt_type == 'ots') and not url:
            errors['ots_NO_url'].append((igdt_type, component, ndb_no_url_alias))
            
        if (igdt_type == 'derived') and txtfile and ndb_no:
            errors['derived_w_file_HAS_ndb_no'].append((component, Path(txtfile).name, ndb_no))

            
        if verbose and (ndb_no_url_alias != 'per 100g'):
            print(f"\nItem: {component}")
            pprint(atomic_LUT[component])            


    return len(atomic_LUT)

# keep it simple to start
# remove QUID (34%) no's - these could be used to revese engineer a recipe in conjunction w/ nutrition info
# downcase and remove whitespace and .
# TODO - need a lot more data to REFINE
# Scan for allergens in brackets: like wood smoked mussels (mollusc)
# scan for ingredients in BRACKETS - allergens often inside
# Preservative (Sodium Metabisulphite)
# This: Acidity Regulators (Acetic Acid, Citric Acid), splits to
# 'Acidity Regulators (Acetic Acid' and
# 'Citric Acid'



# # store these in composite
# acidity regulator: ascorbic acid;
# anti-caking agent: silicon dioxide)
# colour: beetroot red;
# acid: citric acid;
# stabiliser: guar gum;

# ingredient classifier: ingredient name
IC_IGDT = re.compile(r"([a-z -]+):([a-z ]+)([,;\]\}\)])", re.MULTILINE | re.DOTALL )

def remove_igdt_classifiers(i_string):
    classifiers = {}
    for m in re.finditer(IC_IGDT, i_string):
        print(f"\ng0 - {m.group(0)}")
        print(f"g1 - {m.group(1)}")
        print(f"g2 - {m.group(2)}")
        print(f"g3 - {m.group(3)}")
        if m.group(1) in classifiers: classifiers[m.group(1)].append(m.group(2).strip())
        else: classifiers[m.group(1)] = [m.group(2).strip()]
    
    i_string = re.sub(IC_IGDT, r"\2\3", i_string)    # \3 preserves brakets ), }, ], & semi colon ;
    # print(f"\n{i_string}\n")
    i_string = re.sub(';', ',', i_string)            # replace semicolon w/ a comma
    return((i_string, classifiers))

ALLERGENS = re.compile('\((contains)*:*\s*([\w ]+)\)')
# assumes lower case
def screen_for_allergens(i_string):
    allergens = []
    for m in re.finditer(ALLERGENS, i_string):
        allergens.append(m.group(2))        
    return(list(set(allergens)))  


QUID_PC = re.compile('\(*[\d.]+%\)*')       # 3% (45%) 3.5% (3.5%)  QUID_PC = re.compile('\((\d+%)\)')
PUREE = re.compile('purée')
CONTAINS = re.compile('contains:*\s*')      # contains: allergen
IGDT_TITLE = re.compile('ingredients:')     # ingredients:sugar cane, cane molasses.
regex_noise = [QUID_PC, CONTAINS, PUREE, IGDT_TITLE]

def filter_noise(i_string, dbg=True):    
    if dbg: print(f"\nrgx-i:{i_string}")

    for r in regex_noise:
        i_string = re.sub(r,'',i_string).strip()
    
    if dbg: print(f"\nrgx-o:{i_string}")
    return(i_string)

def flatten_tree(i_tree, with_super_ingredient=False):
    flat = []
    for leaf in i_tree:
        if isinstance(leaf, dict):      # branch
            for key in leaf.keys():     # should only be one!
                flat = flat + flatten_tree(leaf[key])
                if with_super_ingredient: flat = flat + [key]
        else:
            flat.append(leaf)
    return flat


# TODO replace with
# def process_ots_i_list_into_allergens_and_base_ingredients(i_string):
# in food_set_test.pt

def process_ots_ingredient_string(ingredient_string, ingredient_name=''):
    global ots_I_set    # keep track of ingredients found in OTS items
    print(f"[process_ots_ingredient_string] for ({ingredient_name})")
    composite_data = {}
    composite_data['ri_name'] = ingredient_name
    composite_data['orig_i_string'] = ingredient_string
    # ORDER DEPENDANT - STRING PROCESSING
    i_string = ingredient_string.lower()    # removed from each function do ONCE!
    composite_data['allergens'] = screen_for_allergens(i_string)     # testing
    i_string = filter_noise(i_string)
    i_string, composite_data['classifiers'] = remove_igdt_classifiers(i_string)

    ret_list = []
    c_pos = -1

    def split_out_sublists_in_brackets(b=-1):
        nonlocal c_pos
        nonlocal i_string
        nonlocal ret_list
        
        # scan by character
        b += 1          # bracket count () start at 0
        i = ''          # ingredient
        key_igdt = ''   # ingredient with sub ingredients
        sub_dict = {}
        sub_i_list = []
        #print(f"\n\n> - split_out_sublists_in_brackets (b={b})")
        while (c_pos < len(i_string)-1): # TODO check this -1 correct
            c_pos += 1
            c = i_string[c_pos]
            print(c, end='.')
            if (c==',') and not b:               # no bracket in ingredient - store it
                if i: ret_list.append(i.strip())
                if sub_dict: ret_list.append(sub_dict)
                #print(f"\n[,{b}] i:{i} - k:{key_igdt} - {sub_i_list} - {sub_dict}")
                i = ''
                sub_dict = {}
                continue
            if (c==',') and b:                  # inside brackets store ingredients in sublist
                if i: sub_i_list.append(i.strip())
                if sub_dict: sub_i_list.append(sub_dict)
                i = ''
                sub_dict = {}            
                #print(f"\n[,{b}] i:{i} - k:{key_igdt} - {sub_i_list} - {sub_dict}")
                continue
            if (c=='('):
                key_igdt = i.strip()
                sub_dict[key_igdt] = split_out_sublists_in_brackets(b)
                i = ''
                #print(f"\n[({b}] i:{i} - k:{key_igdt} - {sub_i_list} - {sub_dict}")
                continue
            if (c==')'):    # bracket end to construct dict with result
                sub_i_list.append(i.strip())
                #print(f"\n[){b}] i:{i} - k:{key_igdt} - {sub_i_list} - {sub_dict}")
                return(sub_i_list)
    
            i += c        
        
        return(ret_list)
    
    composite_data['i_tree'] = split_out_sublists_in_brackets()    
    composite_data['i_list'] = sorted(list(set(flatten_tree(composite_data['i_tree']))))
    ots_I_set = ots_I_set | set(composite_data['i_list'])
    print('\n|A|')
    print(composite_data['allergens'])
    print(get_allergens_for(composite_data['allergens']))       
    print(get_allergens_for(composite_data['i_list']))
    composite_data['allergens'] += get_allergens_for(composite_data['allergens'])   # filter latin & other names
    composite_data['allergens'] += get_allergens_for(composite_data['i_list']) 
    print('|')
    pprint(composite_data)
    print('|')
    return composite_data
            

def parse_igdt_lines_into_igdt_list(lines=''):
    i_list = []

    lines = [ l.strip() for l in lines.splitlines() ]
    lines = list(filter(None, lines)) 

    # remove qty & comment from each line
    for line in lines:
        parts = [ item.strip() for item in line.split('\t') if (len(item) > 0) & ('#' not in item) & ('(' not in item) & (item.strip() != '') ] # remove comments
     
        parts.pop(0)    # remove qty
        try:
            i_list.append(parts.pop(0))
        except IndexError:
            pass

    i_list = list(dict.fromkeys(i_list))        # remove duplicates from list    
    i_list = list(filter(None, i_list))         # remove empty strings
    return i_list


CACHE_recipe_component_or_ingredient = {}
def get_ingredients_from_component_file(recipe_component_or_ingredient):
    rcoi = recipe_component_or_ingredient
    
    if rcoi in CACHE_recipe_component_or_ingredient:
        content = CACHE_recipe_component_or_ingredient[rcoi]
    else:
        if rcoi in component_file_LUT:
            with component_file_LUT[rcoi].open('r') as f:
                content = f.read()
                CACHE_recipe_component_or_ingredient[rcoi] = content
        else:
            errors['expected_derived_atomic_no_file'].append((rcoi))
            return([rcoi])    
    
    m = re.search(r'--- for the (.*?) \((.*?)\)(.*?)Total \((.*?)\).*?__end_recipe__', content, re.MULTILINE | re.DOTALL)
    
    if m:
        ri_name, servings, ingredients_lines, total_yield = m.group(1), m.group(2), m.group(3), m.group(4)
 
        if rcoi == ri_name:
            return parse_igdt_lines_into_igdt_list(ingredients_lines)
        else:
            errors['txt_title_NO_match_rcp'].append((rcoi, ri_name))
            return f"txt_title_NO_match_rcp>{rcoi}|{ri_name}<alias"
    else:
        return 'ERROR: bad_template'

# TODO REMOVE
def remove_error(possible_err_string):
    #'unknown_component>alias_NF>coriander sauce|per 100g'
    # 'ots_i_miss>sherry vinegar'    
    e_list = possible_err_string.split('>')
    if len(e_list) > 1:
        print(f"possible_err_string:{possible_err_string}")
        return e_list.pop()
    return possible_err_string



# recursive compile ingredients including OTS if ingredients available
# for single item - see function below for list
def get_ingredients_as_text_list_R(recipe_component_or_ingredient, d=0): # takes str:name
    d += 1
    rcoi = remove_error(recipe_component_or_ingredient)
    i_list = [f"unknown_component>{rcoi}<"]
    
    if rcoi in atomic_LUT:
        igdt_type = atomic_LUT[rcoi]['igdt_type']
        
        if igdt_type == 'atomic':
            i_list = [atomic_LUT[rcoi]['ingredients']] if atomic_LUT[rcoi]['ingredients'] != '__igdts__' else [rcoi]
        
        elif igdt_type == 'ots':
            if atomic_LUT[rcoi]['ingredients'] == '__igdts__':
                i_list = [f"ots_i_miss>{rcoi}<"]
                # TODO follow_alias(rcoi) to see if ingredients there!
            else:
                # TODO test on more formats - mostly sbs at the mo!
                # TODO pass allergen info from OTS composite['allergens']
                composite = process_ots_ingredient_string(atomic_LUT[rcoi]['ingredients'], rcoi)
                i_list = composite['i_list']
        
        elif igdt_type == 'derived':
            if rcoi not in component_file_LUT:
                alias = re.sub('ndb_no=', '', atomic_LUT[rcoi]['ndb_no_url_alias'])
                if alias in component_file_LUT:
                    print(f"\n{'    '*(d-1)}=A> {alias} < file [{component_file_LUT[alias].name}]")
                    s_list = get_ingredients_from_component_file(alias)
                else:
                    s_list = [f"alias_NF>{rcoi}|{alias}<"]            
            else:
                print(f"\n{'    '*(d-1)}==> {rcoi} < file [{component_file_LUT[rcoi].name}]")
                s_list = get_ingredients_from_component_file(rcoi)

            print(f"{'    '*(d-1)}{s_list}")
            #print('-*-')
            
            if s_list == 'ERROR: bad_template':
                i_list = [f"bad_template_in_file>{rcoi}<"]
            else:
                i_list = []
                for i in s_list:
                    sub_list = get_ingredients_as_text_list_R(i,d)
                    i_list = i_list + sub_list
                    #print(f"{'    '*d}{sub_list}")
            
        else:
            i_list = [f"unknown_igdt_type>{rcoi}<"]
    
    i_list = sorted(list(set(i_list)))
    errors['dead_ends_in_this_pass'] += scan_for_error_items(i_list) 
    
    return sorted(list(set(i_list)))# remove duplicates    


def get_exploded_ingredients_as_list_from_list(i_list):
    exploded_list = []
    for i in i_list:
        exploded_list += get_ingredients_as_text_list_R(i)
    
    save_ots_ingredients_found()
    
    return(sorted(list(set(exploded_list))))

# returns (c_list: list of components in rcoi, i_list: list of ingredients and posible subcomponents)
#            ^^                                  ^^
def get_exploded_ingredients_and_components_for_DB_from_name(comps_and_rcoi, d=0): # takes str:name    
    d += 1

    #print(f"comps_and_rcoi:{comps_and_rcoi}")
    #pprint(comps_and_rcoi)

    c_list, recipe_component_or_ingredient = comps_and_rcoi

    #print(f"c_list:{c_list}")
    #print(f"recipe_component_or_ingredient:{recipe_component_or_ingredient}")

    rcoi = remove_error(recipe_component_or_ingredient) 
    i_list = [f"unknown_component>{rcoi}<"]
    
    if rcoi in atomic_LUT:
        igdt_type = atomic_LUT[rcoi]['igdt_type']
        
        if igdt_type == 'atomic':
            i_list = [atomic_LUT[rcoi]['ingredients']] if atomic_LUT[rcoi]['ingredients'] != '__igdts__' else [rcoi]
        
        elif igdt_type == 'ots':
            i_list=[rcoi]
        
        elif igdt_type == 'derived':
            if rcoi not in c_list:
                c_list.append(rcoi)            

            if rcoi not in component_file_LUT:
                alias = re.sub('ndb_no=', '', atomic_LUT[rcoi]['ndb_no_url_alias'])
                if alias in component_file_LUT:
                    print(f"\n{'    '*(d-1)}=A> {alias} < file [{component_file_LUT[alias].name}]")
                    s_list = get_ingredients_from_component_file(alias)
                else:
                    s_list = [f"alias_NF>{rcoi}|{alias}<"]            
            else:
                print(f"\n{'    '*(d-1)}==> {rcoi} < file [{component_file_LUT[rcoi].name}]")
                s_list = get_ingredients_from_component_file(rcoi)

            #print(f"{'    '*(d-1)}C{c_list}")
            print(f"{'    '*(d-1)}S{s_list}")
            #print('-*-')
            
            if s_list == 'ERROR: bad_template':
                i_list = [f"bad_template_in_file>{rcoi}<"]
            else:
                i_list = []
                for i in s_list:
                    c_list, sub_list = get_exploded_ingredients_and_components_for_DB_from_name((c_list,i),d)
                    i_list = i_list + sub_list
                    #print(f"{'    '*d}{sub_list}")
            
        else:
            i_list = [f"unknown_igdt_type>{rcoi}<"]
    
    i_list = sorted(list(set(i_list))) # remove duplicates

    errors['dead_ends_in_this_pass'] += scan_for_error_items(i_list) 
    
    return (c_list, i_list)


    


def scan_for_error_items(i_list, return_all_ingredients=False):
    e_list = []
    for i in i_list:
        m = re.match('(.*?)>(.*?)<',i)
        if m:
            err, item = m.group(1), m.group(2)
            e_list.append((err, item))
        elif return_all_ingredients:
            e_list.append(('no_error', i))

    return e_list



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# build LUT's CACHE recipes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
print('>--A build_file_LUT')
build_file_LUT()

print('>--B build_atomic_LUT')
build_atomic_LUT() # pass True for debug o/p

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


#sys.exit(0) # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




class FoodSetsError(Exception):
    '''TODO Move this and other error classes to separate file: exceptions.py'''
    pass

class UnkownAllergenType(FoodSetsError):
    '''Raised when interface used incorrectly - non existent allergen type passed in'''
    pass

class IncorrectTypeForIngredients(FoodSetsError):
    '''Ingredients should be str or list'''
    pass

# simple allergen detection - this could explode into a massively time consuming exersize so keep it simple!
# Brief: should work with the ingredients in the current data set ~1400 ingredients
# Basic guide: https://www.food.gov.uk/sites/default/files/media/document/top-allergy-types.pdf
#
# a call to get_allergens_for(['cod','flour','egg','water','soda water','salt','veg oil','corn flour'])
# should return ['dairy', 'eggs', 'fish', 'gluten']
#
# alcohol classification should be limited to rum, vodka, gin, whisky, red wine, white wine, champagne, cava, scrumpy
# - that's enough for scope of this exersize
#
# # # #
# the section following allergens is to deal with classifying for belief systems: IE no beef, no pork,
# veggie, vegan, etc
# and is aimed at recipes / components
#
# so similarly a call to
#   get_containsTAGS_for(['seared seabass','sauteed potatoes'])
#   > fish, dairy
#
#   get_containsTAGS_for(['slow roast lamb','roast potatoes','caramelised carrots'])
#   > lamb, dairy
#
#   get_containsTAGS_for(['water cress w/ sage','ewes milk curd','oats & sunflower seeds'])
#   > veggie, dairy, sunflower seeds
#
#   get_containsTAGS_for(['watermelon gazpacho w/ prawns & mango salsa'])   < recipe in DB
#   > prawns, chilli
#
#   get_containsTAGS_for(['couscous chermoula'])   < recipe in DB
#   > veggie, nuts, gluten
#
#   get_containsTAGS_for(['ldl mild salsa dip'])   < shop bought ingredient - ots (Off The Shelf - need lookup)
#   > ots
#




# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DAIRY
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
dairy_basic = {'milk','cows milk','goats milk','sheeps milk','fermented milk','yogurt','cream','butter','cheese',
               'casein','custard','ice cream','milk powder','dried skimmed milk'}

# usually product of some type katsuobushi or fish sauce for example
dairy_derived_no_recipe =  {'panna cota','brussels pate', 'cheese cake', 'creme patissiere','roulade', 'parmesan crisps'}

# different names same thing
dairy_alt = [
    {'yoghurt','yogurt'},
    {'custard', 'creme anglaise'},
    {'creme patissiere', 'creme patissier'},
    {'whippy-san','whippy san'},
    {'parmesan','parmigiano-reggiano','parmesan cheese'},
    {'mature cheddar','mature cheddar cheese'},
    {'roquefort','roquetfort'},   # 2nd is misspelling
    {'st agur','st agur cheese','saint agur blue cheese'},
    {'feta','feta cheese','greek feta'},
    {'philadelphia','philadelphia soft cheese','cream cheese','soft cheese','soft white cheese'},
    {'brie','somerset brie'},
]

# have to give cheese a super set of its own!
# notes on categories here: https://recipes.howstuffworks.com/food-facts/different-types-of-cheese.htm
cheese_subsets = {
    'fresh cheese' : {'cottage cheese','queso fresco','cream cheese','mascarpone','ricotta','ricotta lite','chevre','feta','feta light','cotija','panela','halloumi','fromage blanc','queso blanco'}, # feta can be an aged cheese too
    'cream cheese' : {'philadelphia','roule','garlic roule','garlic & herb roule','boursin'},
    'pasta filata' : {'mozzarella','burrata','provolone','queso oaxaca','scamorza affumicata','caciocavallo','cheddar mozzarella 50/50 mix','chefs larder grated mozzarella and cheddar','chedoza','grated mozzarella and cheddar'},
    'soft-ripened cheese' : {'brie','camembert','cambozola','goats cheese','chavroux goats cheese'},       # bloomy rind
    'semi-soft cheese' : {'havarti','muenster','munster','jarlsberg','chaumes','red leicester'},
    'washed-rind cheese' : {'limburger','taleggio','epoisses','alsatian munster'},
    'blue cheese' : {'roquefort','stilton','gorgonzola','sweet gorgonzola','danish blue', 'st agur'},
    'semi-hard cheese' : {'cheddar','gouda','mature gouda','edam','monterey jack','emmental','swiss','gruyere','extra mature cheddar',
                          'mature cheddar','mild cheddar','leerdammer light cheese','leerdammer'},
    'hard cheese' : {'parmesan','parmigiano-reggiano','asiago','pecorino','manchego',},
    'unsorted' : {'cheese slices','wensleydale cheese','port salut cheese','president brie','edam mild wedge','french camembert',
                  'president camembert','jarlsberg cheese','german cambozola','swiss le gruyere','cinco lanzas 16 months',
                  'taleggio cheese','petit pont leveque cheese','hochland sortett','castello extra creamy brie',
                  'grated mozzarella','austrian smoked cheese','blue stilton standard','saint agur creme',
                  'butlers blacksticks blue','inglewhite farmhouse blue cheese','castello creamy blue ',
                  'abergavenny goats cheese','medium fat hard cheese'}
}

cheese = {'cheese'}
for cheese_cat, cheese_set in cheese_subsets.items():
    cheese = cheese | {cheese_cat} | cheese_set

# subsets - common name with various types
dairy_subsets = {
    'milk' : {'skimmed milk','semi skimmed milk','full fat milk','whole milk','1% skimmed milk','1% milk','2% milk','bob'},
    'fermented milk' : {'sour cream','soured milk'},
    'yogurt' : {'greek yoghurt','natural yoghurt','skyr'},
    'cream' : {'single cream','double cream','squirty cream','whipping cream','clotted cream','creme fraiche'},
    'butter' : {'salted butter','unsalted butter','cornish butter','ghee','clarified butter'},
    'cheese' : cheese,
    'casein' : {'milk protein','whey protein'},
    'ice cream' : {'gelato','ice milk','whippy san','frozen custard','frozen yoghurt'},
}



def build_dairy_set():
    dairy = {'dairy'}

    for key, val in dairy_subsets.items():
        union = val | {key}     # include the categegory generalisation
        dairy = dairy | union

    for val in dairy_alt:
        dairy = dairy | val       # include different names for each dairy

    dairy = dairy | dairy_derived_no_recipe

    dairy = dairy | dairy_basic

    return dairy

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# EGGS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
eggs_basic = {'eggs','egg','quails egg','duck egg','hens egg','albumin','albumen','dried egg','powdered egg',
              'egg solids','egg white','egg yolk','pasteurised egg','pasteurised egg white', 'pasteurised egg yolk',
              'dried free range egg white', 'dried egg'}

# usually product of some type katsuobushi or fish sauce for example
eggs_derived_no_recipe =  {'lecithin','marzipan','marshmallows','nougat','pretzels','pasta', 'eggnog','lysozyme'
                           'mayo','mayonnaise','meringue','meringue powder','ovalbumin','surimi','egg tofu'}

eggs_alt = [{'mayo','hman mayo','chefs larder mayo','mayonaise'}]

def build_eggs_set():
    eggs = {'eggs'}

    for val in eggs_alt:
        eggs = eggs | val

    eggs = eggs | eggs_derived_no_recipe

    eggs = eggs | eggs_basic

    return eggs


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PEANUTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
peanuts_basic = {'peanuts', 'peanut'}

# usually product of some type katsuobushi or fish sauce for example
peanuts_derived_no_recipe =  {'peanut butter'}

def build_peanuts_set():
    peanuts = {'peanuts'}

    peanuts = peanuts | peanuts_derived_no_recipe

    peanuts = peanuts | peanuts_basic

    return peanuts


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# NUTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
nuts_basic = {'almonds','brazil nuts','cashews','chestnuts','filberts','hazelnuts','hickory nuts','macadamia nuts',
              'pecans','pistachios','walnuts'}

nuts_derived_no_recipe = {'mortadella','salted cashews','honey roast peanuts','honey roast cashews','baklava',
                          'cantuccini','almond oil','roasted sliced nuts'}

def build_nuts_set():
    nuts = {'nuts'}

    nuts = nuts | nuts_derived_no_recipe

    nuts = nuts | nuts_basic

    return nuts


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SEEDS_LUPIN       - related to peanut
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
seeds_lupin_basic = {'lupin','lupin seeds','lupin flour'}

#seeds_lupin_derived_no_recipe =  {'',''}

# different names same thing
# seeds_lupin_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]

# subsets - common name with various types
#seeds_lupin_subsets = { }

def build_seeds_lupin_set():
    seeds_lupin = {'seeds_lupin'}

    # for key, val in seeds_lupin_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     seeds_lupin = seeds_lupin | union
    #
    # for val in seeds_lupin_alt:
    #     seeds_lupin = seeds_lupin | val       # include different names for each
    #
    # seeds_lupin = seeds_lupin | seeds_lupin_derived_no_recipe

    seeds_lupin = seeds_lupin | seeds_lupin_basic

    return seeds_lupin

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SEEDS_SESAME
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
seeds_sesame_basic = {'sesame','sesame seeds','sesame paste','sesame oil','sesame flour','sesame salt'}

# https://allergyfacts.org.au/images/pdf/sesamef.pdf
seeds_sesame_derived_no_recipe =  {'falafel','sesame burger bun', 'sesame bap','gomashio','halva','baklava','pretzels',
                                   'tahina','aqua libra','benne','benniseed','dukkah','gingelly seeds','hummus','pasteli',
                                   'sesarmol','sesomolina','sim sim','til'} # 'tahina' is a sesame sauce!
# different names same thing
seeds_sesame_alt = [
    {'sesame paste','tahini'},
    {'gomasio','gomashio','sesame salt'},
]

# subsets - common name with various types
#seeds_sesame_subsets = {}

def build_seeds_sesame_set():
    seeds_sesame = {'seeds_sesame'}

    # for key, val in seeds_sesame_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     seeds_sesame = seeds_sesame | union

    for val in seeds_sesame_alt:
        seeds_sesame = seeds_sesame | val       # include different names for each seeds_sesame

    seeds_sesame = seeds_sesame | seeds_sesame_derived_no_recipe

    seeds_sesame = seeds_sesame | seeds_sesame_basic

    return seeds_sesame

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SEEDS_MUSTARD
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
seeds_mustard_basic = {'mustard','mustard seeds','french mustard','english mustard','american mustard','yellow mustard',
                       'dijon mustard','dijon','liquid mustard','mustard powder'}

# usually product of some type katsuobushi or fish sauce for example
seeds_mustard_derived_no_recipe =  {'ham sandwich','mayo','mayonnaise','brown mustard','beer mustard','honey mustard','hot mustard','sweet mustard'}

# different names same thing
seeds_mustard_alt = [
    {'whole grain mustard','whole-grain mustard'},
    {'american mustard','yellow mustard'},
]

# subsets - common name with various types
#seeds_mustard_subsets = {}
def build_seeds_mustard_set():
    seeds_mustard = {'seeds_mustard'}

    # for key, val in seeds_mustard_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     seeds_mustard = seeds_mustard | union

    for val in seeds_mustard_alt:
        seeds_mustard = seeds_mustard | val       # include different names for each seeds_mustard

    seeds_mustard = seeds_mustard | seeds_mustard_derived_no_recipe

    seeds_mustard = seeds_mustard | seeds_mustard_basic

    return seeds_mustard

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# FISH
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
fish_basic = {'anchovies','barracuda','basa','bass','black cod','blowfish','bluefish','bombay duck','bonito','bream',
              'brill','butter fish','catfish','cod','dogfish','dorade','eel','flounder','grouper','gurnard','haddock',
              'hake','halibut','herring','ilish','john dory','lamprey','ling','lingcod','mackerel','mahi mahi','monkfish',
              'mullet','orange roughy','parrotfish','patagonian toothfish','perch','pike','pilchard','plaice','pollock',
              'pomfret','pompano','sablefish','salmon','sanddab','sardine','sea bass','shad','shark','skate',
              'smelt','snakehead','snapper','sole','sprat','sturgeon','surimi','swordfish','tilapia','tilefish',
              'trout','tuna','turbot','wahoo','whitefish','whiting','witch','whitebait'}

fish_latin = {'theragra chalcogramma','alaska pollock',
              'merluccius merluccius','european hake','cornish salmon','herring hake'}


fish_derived_no_recipe = {'katsuobushi','dashi','fish stock cube','fish sauce','cured salmon','smoked salmon','worcestershire sauce'}

# exceptions, sub sets & alternate names
# different name same fish
fish_alt = [
    {'black cod','sablefish'},
    {'patagonian toothfish', 'chilean sea bass'},
    {'dab', 'sanddab'},
    {'witch','righteye flounder'},      # there's about 10 righteye type around australias coast!
    {'sea bass','seabass'},             # the correct spelling is sea bass
    {'summer flounder','fluke'},
    {'river cobler','pangaseus','basa','swai'},
    {'caviar','sturgeon roe'},
    {'ikura','salmon roe'},
    {'kazunoko','herring roe'},
    {'masago','capelin roe'},
    {'tobiko','flying-fish roe'},
    {'anchovies','anchovy'},
    {'worcestershire sauce','lea and perrins'},
    {'ling','cooked ling'},
    {'mackerel','smoked mackerel fillet','mackerel fillet'}
]

# subsets
fish_subsets = {
    'catfish' : {'river cobler','pangaseus','basa','channel catfish','blue catfish','ikan keli','magur','hedu','etta','swai'},
    'cod' : { 'pacific cod', 'atlantic cod' },
    'bass' : {'bass','striped bass'},
    'eel' : {'eel','conger eel'},
    'flounder' : {'plaice','gulf flounder','summer flounder','winer flounder','european flounder','which flounder','halibut','olive flounder'},
    'salmon' : {'sockeye salmon','alaskan salmon','chinook salmon','pink salmon','coho salmon'},
    'sanddab' : {'pacific sanddab'},   # there are a lot of these
    'shad' : {'alewife','american shad'},
    'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
    'trout' : {'trout','rainbow trout'},
    'tuna' : {'albacore tuna','bigeye tuna','bluefin tuna','dogtooth tuna','skipjack tuna','yellowfin tuna'},
    'roe' : {'caviar','sturgeon roe','ikura','salmon roe','kazunoko','herring roe','lumpfish roe','masago','capelin roe','shad roe','tobiko','flying-fish roe'}
}


def build_fish_set():
    fish = {'fish'}

    for key, val in fish_subsets.items():
        union = val | {key}     # include the categegory generalisation
        fish = fish | union

    for val in fish_alt:
        fish = fish | val       # include different names for each fish

    fish = fish | fish_derived_no_recipe

    fish = fish | fish_basic
    
    fish = fish | fish_latin

    return fish


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SHELLFISH - MOLLUSCS - theres quite a list here: https://en.wikipedia.org/wiki/List_of_edible_molluscs
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
molluscs_basic = {'abalone','escargot','squid','snail','snails','hereford snails','mussel','limpits','winkles','whelks','clams','mussels',
                  'oyster','oysters','scallop','octopus','cuttlefish'}

molluscs_derived_no_recipe =  {'oyster sauce', 'smoked mussels inc oil', 'smoked mussels', 'wood smoked mussels', 'wood smoked mussels (mollusc)',
                               'cooked squid'}

# different names same thing
molluscs_alt = [
    {'snails','escargot','helix aspersa'},
    {'cuttlefish', 'sepia'},
    {'small squid','small squid tubes','large squid','large squid tubes','squid tubes','squid'},
]

# subsets - common name with various types
molluscs_subsets = {
    'clams' : { 'blood cockle','cockles','mussels','hard clams','grooved carpet shell','quahog','leukoma','paphies',
               'pismo clam','smooth clam','tuatua' },
    'abalone' : { 'black abalone','blacklip abalone','green abalone','green ormer','haliotis corrugata','red abalone',
                 'white abalone','pāua' },
    'mussels' : { 'blue mussels','blue mussel','california mussel','mediterranean mussel' },
    'oyster' : { 'auckland oyster','dredge oyster','mangrove oyster','ostrea angasi','ostrea edulis','pacific oyster',
                'rock oyster','sydney rock oyster','portuguese oyster'},
    'razor clams' : { 'atlantic jackknife clam','ensis','ensis macha','pacific razor clam','pod razor','razor shell',
                     'sinonovacula' },
}

# TODO change molluscs to mollusc  - hits ots i_list (mollusc)
def build_molluscs_set():
    molluscs = {'mollusc','molluscs'}

    for key, val in molluscs_subsets.items():
        union = val | {key}     # include the categegory generalisation
        molluscs = molluscs | union

    for val in molluscs_alt:
        molluscs = molluscs | val       # include different names for each molluscs

    molluscs = molluscs | molluscs_derived_no_recipe

    molluscs = molluscs | molluscs_basic

    return molluscs

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SHELLFISH - CRUSTACEANS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
crustaceans_basic = {'crustaceans','langoustine','crab','crayfish','prawn','prawns','shrimp','shrimps','langostino','lobster'}

# usually product of some type katsuobushi or fish sauce for example
crustaceans_derived_no_recipe =  {'salt and pepper squid','lobster bisque', 'shrimp paste', 'dried shrimp'}

# different names same thing
crustaceans_alt = [
    {'langostino', 'squat lobster'},
    {'norway lobster', 'dublin bay prawn', 'langoustine','langostine'},
    {'prawn','prawns','shrimp','shrimps','large head on shell on prawns', 'large head on shell on prawn', 'large prawns', 'large prawn',
     'hoso prawn','hoso prawns','so prawn','so prawns','shell on jumbo king prawn', 'shell on jumbo king prawns'},
    {'crayfish','crawfish', 'crawdads', 'freshwater lobsters', 'mountain lobsters', 'mudbugs', 'yabbies',
     'cangrejo de rio'},
    {'cangrejo', 'crab', 'crab meat', 'crab claws', 'white crab meat', 'brown crab meat'}
]

# subsets - common name with various types
crustaceans_subsets = {
    'crab' : { 'brown crab','dungeness crab','mud crab','sand crab','alaskan king crab','norwegian king crab','king crab','snow crab','blue crab','soft shell crab' },
    'lobster' : {'american lobster','rock lobster','spiny lobster','red lobster','canadian lobster'},
    'crayfish' : {'marron','koura'},
    'prawns' : {'tiger prawns','king prawns','cooked prawns','fresh prawns','fresh water prawns','tiger prawn',
                'king prawn','cooked prawn','fresh prawn','fresh water prawn'}
}
def build_crustaceans_set():
    crustaceans = {'crustacean','crustaceans'}

    for key, val in crustaceans_subsets.items():
        union = val | {key}     # include the categegory generalisation
        crustaceans = crustaceans | union

    for val in crustaceans_alt:
        crustaceans = crustaceans | val       # include different names for each

    crustaceans = crustaceans | crustaceans_derived_no_recipe

    crustaceans = crustaceans | crustaceans_basic

    return crustaceans

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ALCOHOL
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
alcohol_basic = {'alcohol','rum','vodka','gin','whisky','red wine','white wine','wine','champagne','cava','scrumpy',
                 'scrumpy jack','larger','cider abv5','corona','corona extra','red wine abv12.5','white wine 12.5',
                 'white wine abv12.5','white wine','tennessee honey lemonade abv5.0','tennessee honey lemonade',
                 'disaronno amaretto liqueur 28%ABV','disaronno amaretto liqueur','disaronno amaretto liqueur abv28',
                 'amaretto liqueur','amaretto','omega cider','port wine','port wine abv18','malbec port','baileys abv17',
                 'baileys','baileys irish cream abv17','mrs irish meadow abv14','mrs irish meadow','sbs madeira abv17.5',
                 'sbs madeira','madeira','marsala','marsala abv18','old rosie'}

# usually product of some type katsuobushi or fish sauce for example
alcohol_derived_no_recipe =  {'rum baba','tiramisu','cocktail'}

# different names same thing
alcohol_alt = [
    {'scrumpy','scrumpy jack'},
    {'larger', 'red stripe'},
    {'cocktails','cocktail'},
]

# subsets - common name with various types
alcohol_subsets = {
    'cocktails' : {'tequila sunrise','black russian','margarita','mojito','caipirina'}
}

def build_alcohol_set():
    alcohol = {'alcohol'}

    for key, val in alcohol_subsets.items():
        union = val | {key}     # include the categegory generalisation
        alcohol = alcohol | union

    for val in alcohol_alt:
        alcohol = alcohol | val       # include different names for each

    alcohol = alcohol | alcohol_derived_no_recipe

    alcohol = alcohol | alcohol_basic

    return alcohol

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CELERY
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
celery_basic = {'celery','celery sticks','celery leaves','celery spice','celery seeds','celery salt','celeriac'}

# usually product of some type katsuobushi or fish sauce for example
celery_derived_no_recipe =  {'chicken stock','lamb stock', 'beef stock', 'fish stock', 'pork stock', 'veggie stock',
                             'vegetable stock', 'veg stock', 'chicken stock cube','lamb stock cube', 'beef stock cube',
                             'fish stock cube', 'pork stock cube', 'veggie stock cube', 'vegetable stock cube',
                             'veg stock cube', 'marmite'}

def build_celery_set():
    celery = {'celery'}

    celery = celery | celery_derived_no_recipe

    celery = celery | celery_basic

    return celery






# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GLUTEN
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
gluten_basic = {'gluten','wholegrain wheat','wheat','wheat protein','wheat germ','wholegrain rye','rye','wholegrain barley',
                'barley','bulgur','couscous','farina','graham flour','kamut','khorasan wheat','semolina','spelt','triticale',
                'flour' }

# usually product of some type katsuobushi or fish sauce for example
gluten_derived_no_recipe =  {'malt vinegar','pasta','bread','pastry','pizza','seitan','flat bread','lamb samosa','veg samosa',
                             'samosa','pie','pies','malted wheat flakes','wheat starch'}

# different names same thing
gluten_alt = [
    {'nan','naan','naaan bread',},
    {'pita','pitta bread'},
    {'rotti','roti'},
    {'tortilla wrap','tortilla','wrap'},
    {'sbs wholemeal tortilla wrap','wholemeal tortilla wrap'}
]

# subsets - common name with various types
gluten_subsets = {
    'flour' : { 'plain flour','self raising flour','strong flour','bread flour','wheat flour','barley flour','rye flour' },
    'flat bread' : {'torta','matzo','pita','naan','roti','paratha','banh','tortilla','wrap','injera','pancake'}, # injera is gluten free if made of 100% teff flour
    'pasta' : {'orzo','spaghetti','macaroni','tagliatele','linguini','fusili','lasagna','rigatoni','farfale','ravioli',
               'fettuccini','penne'}, # and a million other types! shoul catch these unrollin ingredients list!
    'bread' : {'sliced bread','sourdough','brown bread','tiger loaf','french stick','giraffe bread','baguette','burger bun',
               'brioche','demi brioche','baton','biscuit','bagel','cornbread','rye bread','milk bread','pizza','garlic pizza',
               'garlic bread','turkish bread','ciabata','bun','focaccia','mgt','multi grain','seeded batch','thick sliced bread',
               'thick sliced seeded bread','sandwich loaf','white bread','olive bread','poppy seed roll','bap', 'crumpet',
               'seeded baguette','seeded baguette round','baguette round','sourdough round','wholemeal tortilla wrap','seeded panini',
               'panini', 'seeded folded flatbreads aldi', 'sff'},
}
def build_gluten_set():
    gluten = {'gluten'}

    for key, val in gluten_subsets.items():
        union = val | {key}     # include the categegory generalisation
        gluten = gluten | union

    for val in gluten_alt:
        gluten = gluten | val       # include different names for each gluten

    gluten = gluten | gluten_derived_no_recipe

    gluten = gluten | gluten_basic

    return gluten

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SOYA
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
soya_basic = {'soy','soya','edamame','soybeans','soy bean','soyabeans','soya bean','soy bean','soy sauce','tofu',
              'soy milk','condensed soy milk','miso','soy nuts','tamari','shoyu','fermented soya bean',
              'teriyaki','tempeh','textured soy protein','tsp','textured vegetable protein','tvp','soy flour',
              'soybean oil','soy lecithin','natto','kinako','soya flour'}

# usually product of some type katsuobushi or fish sauce for example
soya_derived_no_recipe =  {'condensed soy milk','tofu','douhua'}

# different names same thing
soya_alt = [
    {'soy milk','soymilk'},
    {'soy sauce','tamari','shoyu'},     # tamari is traditionally made soy sauce - does not use wheat and is gluten free
                                        # shoyu is japanese for soy sauce
    {'textured soy protein','tsp'},
    {'textured vegetable protein ','tvp'},
    {'white miso','shiro miso'},
    {'yellow miso','shinshu miso'},
    {'red miso','aka miso'},
    {'teriyaki','teriyaki sauce','teriyake','teriyake sauce'},

]

# subsets - common name with various types
soya_subsets = {
    'tofu' : {'silken tofu','extra soft tofu','soft tofu','medium tofu','firm tofu','extra firm tofu','super firm tofu',
              'noodling','tofu noodles','tofu sponge','egg tofu','pressed tofu','fermented tofu','tofu skin','tofu sticks',
              'fried tofu','tofu pockets','tofu puffs'},
    'miso' : {'red miso','yellow miso','white miso','awase miso','barley miso',}
}

def build_soya_set():
    soya = {'soya'}

    for key, val in soya_subsets.items():
        union = val | {key}     # include the categegory generalisation
        soya = soya | union

    for val in soya_alt:
        soya = soya | val       # include different names for each soya

    soya = soya | soya_derived_no_recipe

    soya = soya | soya_basic

    return soya

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SULPHUR_DIOXIDE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
sulphur_dioxide_basic = {'sulphur dioxide', 'sulphites', 'sodium metabisulphite', 'triphosphates'}

# usually product of some type katsuobushi or fish sauce for example
#sulphur_dioxide_derived_no_recipe =  {'',''}

def build_sulphur_dioxide_set():
    sulphur_dioxide = {'sulphur_dioxide'}

    #sulphur_dioxide = sulphur_dioxide | sulphur_dioxide_derived_no_recipe

    sulphur_dioxide = sulphur_dioxide | sulphur_dioxide_basic

    return sulphur_dioxide


conv_list ='''
plain text list here
'''



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# HEADINGS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_allergens_headings():
    #return {'dairy', 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'shellfish', 'molluscs', 'crustaceans', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide'}
    return {'dairy', 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'molluscs', 'crustaceans', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide'}

# ingredients for each component already recursed and stored in exploded
# add_subcomponents_ingredients
def does_component_contain_allergen(component, allergen):
    allergen_present = False

    if allergen in get_allergens_headings():
        allergen_set = allergenLUT[allergen]
    else:
        raise(UnkownAllergenType(f"ERROR: unknown allergen: {allergen} <"))

    ingredients_of_component = get_ingredients_as_text_list_R(component)
        
    # filter err out of err>name<   - TODO REMOVE w/ ATOMIC implementation? Its passive only
        # scan_for_error_items returns a list of tuples (err, ingredient)
        # only errors unless return_all_ingredients=True
    ingredients_of_component = [i for e, i in scan_for_error_items(ingredients_of_component, return_all_ingredients=True) ]

    if allergen == 'molluscs':
        pprint(allergen_set)
    
    for i in ingredients_of_component:
        if allergen == 'molluscs':
            print(f"{i}")
        if i in allergen_set:
            return (allergen, i, component)
    
    return allergen_present

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ALLERGEN SETS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
allergenLUT = {
    'dairy' : build_dairy_set(),
    'eggs' : build_eggs_set(),
    'peanuts' : build_peanuts_set(),
    'nuts' : build_nuts_set(),
    'seeds_lupin' : build_seeds_lupin_set(),
    'seeds_sesame' : build_seeds_sesame_set(),
    'seeds_mustard' : build_seeds_mustard_set(),
    'fish' : build_fish_set(),
    #'shellfish' : build_molluscs_set() | build_crustaceans_set(),     superfluous result: ['soya', 'crustaceans', 'fish', 'celery', 'shellfish', 'dairy']
    'molluscs' : build_molluscs_set(),
    'crustaceans' : build_crustaceans_set(),
    'alcohol' : build_alcohol_set(),
    'celery' : build_celery_set(),
    'gluten' : build_gluten_set(),
    'soya' : build_soya_set(),
    'sulphur_dioxide' : build_sulphur_dioxide_set()
}

    
def get_allergens_for(list_of_ingredients, show_provenance=False):
    allergens_detected = []

    if list_of_ingredients.__class__ == str:
        list_of_ingredients = [list_of_ingredients]

    if list_of_ingredients.__class__ == list:
        # build complete list - from local assets
        # will not follow URL to inet for ingredients of off the shelf items

        add_ingredients = []
        for i in list_of_ingredients:
            add_ingredients += get_ingredients_as_text_list_R(i)

        # flatten so there's only one of each
        list_of_ingredients = list(set(list_of_ingredients + add_ingredients))

        # filter err out of err>name<   - TODO REMOVE w/ ATOMIC implementation? Its passive only
            # scan_for_error_items returns a list of tuples (err, ingredient)
            # only errors unless return_all_ingredients=True
        list_of_ingredients = [i for e, i in scan_for_error_items(list_of_ingredients, return_all_ingredients=True) ]

        for i in list_of_ingredients:
            for allergen in allergenLUT:
                if i in allergenLUT[allergen]:
                    allergens_detected.append((allergen, i))

    else:
        raise(IncorrectTypeForIngredients("get_allergens_for: pass str or list"))

    if show_provenance:
        print("ALLERGEN show_provenance:")
        pprint(allergens_detected)
        
    allergens_detected = list(set([ a for a,i in allergens_detected]))

    return allergens_detected



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CHICKEN
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
chicken_basic = {'chicken','chicken dark meat','chicken breast',
                 'chicken fat','chicken wing w skin','cornfed chicken','chicken wing','chicken roll',
                 'crispy chicken skin','chicken bites','chicken liver','chicken stock cube','chicken stock cubes',
                 'chicken thigh','chicken brown meat','chicken dark meat','chicken breast','poached chicken thigh',
                 'chicken stock','chicken liver','chicken gravy','home made chicken gravy','roast chicken',
                 'fried chicken breast','fried chicken thigh','fried chicken wing','fried chicken quarter',
                 'chicken mince','minced chicken','chicken skin','chicken heart','chicken crown'
                 }

# usually product of some type katsuobushi or fish sauce for example
chicken_derived_no_recipe =  {'mrs chicken korma','chicken korma'}

# different names same thing
chicken_alt = [
    {'chicken dark meat','chicken brown meat','chicken thigh','chicken oysters'},
    #{'another1', 'another2'},
]

# subsets - common name with various types
# chicken_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }

def build_chicken_set():
    chicken = {'chicken'}

    # for key, val in chicken_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     chicken = chicken | union

    for val in chicken_alt:
        chicken = chicken | val       # include different names for each

    chicken = chicken | chicken_derived_no_recipe

    chicken = chicken | chicken_basic

    return chicken


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# PORK
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
pork_basic = {'pork','carvery pork','pork belly','british pork belly','roast pork','trotters','pigs trotters','pigs ears','roast peppered pork loin',
              'pork ribs','pork_alt loin','pork_alt chop','pork tenderloin','pork shoulder chop','pork shoulder','pork leg',
              'pigs cheeks','pig cheeks','pigs cheeks oyesters','osso buco','pigs hock','spare ribs','rack of ribs','bacon',
              'cured pork','pork sausage','ham','gelatine sheets'
              }

# usually product of some type katsuobushi or fish sauce for example
pork_derived_no_recipe =  {'sweet and sour pork balls in batter','crispy pork','sweet and sour pork','pork gyoza'}

# different names same thing - go through cured pork add to this list
pork_alt = [
    {'streaky bacon','bacon rashers'},
    {'trotters','pigs trotters'},
]

# subsets - common name with various types
pork_subsets = {
    'pork sausage' : {'breakfast sausages','hot dogs','asda chorizo sausages','cumberland sausage','bc cumberland sausages',
                      'ttd cumberland sausages','cumberland sausages','pork sausages','milano cured sausage'},
    'ham' : {'pepper ham','cooked ham','ldl smoked ham','smoked ham','w&s breadcrumb ham','parma ham','sbs parma ham',
             'sandwich ham','cooked ham trimmings lidl','sbs cooked ham','sbs basics ham','smoked ham was','smoked ham trimmings',
             'boiled ham'},
    'cured pork' : {'milano','milano salami','modena salami','salami','parma','parma ham','serano ham','serano','lomo','chorizo','fuet','charcuterie','pancetta',
                    'brawn','jamon','jamon iberico','lardo','bologna','bauernschinken','butifarra','butifarra negra','butifarra blanca',
                    'morcilla','boudin','boudin blanc','zungenwurst','boudin noir','chorizo','coppa','culatello','finocchiona',
                    'guanciale','kabanos','landjager','liverwurst','lonzino','mortadella','nduja','paio','pepperoni','prosciutto',
                    'saucisson','saucisson sec','saucisson darles','soppressata','summer sausage','speck','zungenwurst'},
    'bacon' : {'thick smoked bacon','smoked bacon','bacon lean','smoked rindless bacon','streaky bacon','bacon rashers','lardons',
               'back bacon','smoked streaky bacon'},
}

def build_pork_set():
    pork = {'pork'}

    for key, val in pork_subsets.items():
        union = val | {key}     # include the categegory generalisation
        pork = pork | union

    for val in pork_alt:
        pork = pork | val       # include different names for each

    pork = pork | pork_derived_no_recipe

    pork = pork | pork_basic

    return pork

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# BEEF
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
beef_basic = {'beef','shortribs','roast beef','beef silverside w&s','sbs ttd beef steak burger','beef burger','beef stock cube',
              'mrs beef stock cube as prepared','beef stock','mrs beef stock cube','5% beef mince','12% beef mince','15% beef mince',
              '20% beef mince','5% minced beef','12% minced beef','15% minced beef','20% minced beef','beef brisket','beef fillet',
              'flat iron steak','rump steak','sirloin steak','fillet steak','ribeye','ribeye steak','forerib','forerib joint',
              'beef joint','silverside','topside','top rump','ox cheek','beef shin','oxtail','beef meatballs','beef sausages',
              'diced beef','stewing beef','casserole steak','braising steak','beef flank','hanger steak','gelatine powder','aldi beef trimmings'}

# usually product of some type katsuobushi or fish sauce for example
beef_derived_no_recipe =  {'shredded beef'}

# different names same thing
beef_alt = [
    {'beef tataki','tataki','beef carpaccio','carpaccio'},
    {'another1', 'another2'},
]

# subsets - common name with various types
beef_subsets = {
    'cured beef' : {'cecina vacuno','billtong','beef jerky','pastrami','bologna','landjager','pepperoni','soujouk','zungenwurst',
                    'bresaola'},
    'beef cold cuts' : {'carvery beef','corned beef','tongue','roast beef slices','tataki','carpaccio'},
    #'beef cold cuts' : {'','','','','','','','','','','','','','','','' },
}
def build_beef_set():
    beef = {'beef'}

    for key, val in beef_subsets.items():
        union = val | {key}     # include the categegory generalisation
        beef = beef | union

    for val in beef_alt:
        beef = beef | val       # include different names for each beef

    beef = beef | beef_derived_no_recipe

    beef = beef | beef_basic

    return beef

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# LAMB
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
lamb_basic = {'lamb','hogget','mutton','roast lamb shoulder','lamb shoulder','lamb leg','lamb shank','lamb leg kabob',
              'lamb leg kabab','roast leg lamb lean','lamb chop lean','lamb chops lean','lamb chop wfat','lamb chops wfat',
              'barnsley chop','lamb chop rounds','diced lamb','lambs liver','lamb neck','rack of lamb','lamb cutlets',
              'leg of lamb','roast lamb','roast leg of lamb','lamb rump','lamb breast','lamb belly','lamb flank',
              'lamb chuck','lamb loin','saddle of lamb','lamb leg steaks','lamb leg steak'}

# usually product of some type katsuobushi or fish sauce for example
lamb_derived_no_recipe =  {'lamb samosa','lamb kofte','donner kebab','lamb bao bun','seared lamb'}

# different names same thing
lamb_alt = [
    {'lamb breast','lamb belly'},
    {'lamb gyoza','lamb dumpling'},
]

# subsets - common name with various types
lamb_subsets = {
    'lamb kebab' : { 'donner','donner meat','shish kebab','souvlaki','giros','gyro','diced lamb kebab','diced lamb' },
}
def build_lamb_set():
    lamb = {'lamb'}

    for key, val in lamb_subsets.items():
        union = val | {key}     # include the categegory generalisation
        lamb = lamb | union

    for val in lamb_alt:
        lamb = lamb | val       # include different names for each lamb

    lamb = lamb | lamb_derived_no_recipe

    lamb = lamb | lamb_basic

    return lamb


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# DUCK
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
duck_basic = {'duck','duck fat','duck breast meat only raw','duck meat only raw','duck leg quarter','duck thigh','duck breast',
              'whole duck','duck heart','duck tongue','duck neck','duck wing','duck crown'}

duck_derived_no_recipe =  {'peking duck','crispy duck','aunt bessies duck fat roast potatoes','skewered duck hearts'}

# different names same thing
# duck_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]

# subsets - common name with various types
# duck_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }
def build_duck_set():
    duck = {'duck'}

    # for key, val in duck_subsets.items():
    #     union = val | {key}     # include the categegory generalisation
    #     duck = duck | union

    # for val in duck_alt:
    #     duck = duck | val       # include different names for each duck

    duck = duck | duck_derived_no_recipe

    duck = duck | duck_basic

    return duck

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# GAME
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
game_basic =  {'dove','snipes','goose','woodcock','wild turkey','quail','pheasant','partridge','grouse','pigeon','teal',
               'hare','rabbit','venison','deer'}

game_derived_no_recipe = {'pigeon stew','venison pot pie'}

# different names same thing
game_alt = [
    {'grouse', 'red grouse'},
    {'snipe','common snipe'},
    {'venison', 'deer'},
    {'venison backstrap','venison loin'},
    {'venison shoulder','venison chuck'},
    {'venison shank','venison osso buco'},
    {'venison leg','venison round'},
    {'minced venison','venison mince'},
]

# subsets - common name with various types
# TODO sort this list & remove duplicates
# bird cuts {'bird','bird fat','bird breast meat only raw','bird meat only raw','bird leg quarter','bird thigh','bird breast',
#            'whole bird','bird heart','bird tongue','bird neck','bird wing','bird crown',
#            'bird dark meat','bird breast', 'bird fat','bird wing w skin','cornfed bird','bird wing','bird roll',
#            'crispy bird skin','bird bites','bird liver','bird stock cube','bird stock cubes',
#            'bird thigh','bird brown meat','bird dark meat','bird breast','poached bird thigh',
#            'bird stock','bird liver','bird gravy','home made bird gravy','roast bird',
#            'fried bird breast','fried bird thigh','fried bird wing','fried bird quarter',
#            'bird mince','minced bird','bird skin','bird heart'}
game_subsets = {
    'partridge' : { 'grey partridge','red legged partridge' },
    'deer' : {'venison rump','venison loin','venison tenderloin','venison shoulder','venison shank','venison ribs',
              'venison neck','venison flank','venison leg','venison mince','venison saddle'},
    'turkey' : {'turkey breast meat only raw','turkey meat only raw','turkey leg quarter','turkey thigh','turkey breast',
                'whole turkey','turkey wing','turkey crown','turkey leg','turkey thigh','turkey breast','turkey dark meat',
                'turkey breast', 'turkey fat','turkey wing w skin','cornfed turkey','turkey wing','turkey roll',
                'crispy turkey skin','turkey thigh','turkey brown meat','turkey dark meat','poached turkey thigh',
                'turkey stock','turkey gravy','home made turkey gravy','roast turkey','fried turkey breast',
                'fried turkey thigh','fried turkey wing','fried turkey quarter','turkey mince','minced turkey',
                'turkey skin','turkey burger'}

}
def build_game_set():
    game = {'game'}

    for key, val in game_subsets.items():
        union = val | {key}     # include the categegory generalisation
        game = game | union

    for val in game_alt:
        game = game | val       # include different names for each game

    game = game | game_derived_no_recipe

    game = game | game_basic

    return game

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# other_edible_animal
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
other_edible_animal_basic = {'aligator','frog', 'empala','emu','kangaroo','antelope','elk','alligator','bat','crocodile',
                             'guinea pig','kangaroo','ostrich','rat','snake','crickets'}

# subsets - common name with various types
other_edible_animal_subsets = {
    'frog' : { 'frogs','frogs legs' },
    'aligator' : { 'aligator collar','aligator knuckle','aligator chuck tender','aligator front hock',
                   'aligator flank steak','aligator thin ribs','aligator prime ribs','aligator sirloin',
                   'aligator fillet','aligator ribeye','aligator tail','aligator hind hock' },
    'crocodile' : { 'crocodile collar','crocodile knuckle','crocodile chuck tender','crocodile front hock',
                   'crocodile flank steak','crocodile thin ribs','crocodile prime ribs','crocodile sirloin',
                   'crocodile fillet','crocodile ribeye','crocodile tail','crocodile hind hock' },
    'kangaroo' : { 'kangaroo steak','kangaroo ribs','kangaroo tail','kangaroo rump','kangaroo tenderloin',
                  'kangaroo shoulder','kangaroo ribs','kangaroo neck','kangaroo flank','kangaroo leg','kangaroo mince',
                  'kangaroo saddle','kangaroo loin','kangaroo striploin','kangaroo diced','kangaroo mince',
                  'minced kangaroo'},
    'insects' : { 'mealworm','mealworms','cricket','crickets' },
}

def build_other_edible_animal_set():
    other_edible_animal = {'other_edible_animal'}

    for key, val in other_edible_animal_subsets.items():
        union = val | {key}     # include the categegory generalisation
        other_edible_animal = other_edible_animal | union

    other_edible_animal = other_edible_animal | other_edible_animal_basic

    return other_edible_animal

# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # NS_PREGNANT
# # pregnant: alcohol, uncooked mould-ripened soft cheese, uncooked blue cheese, raw eggs, raw or rare meat (toxoplasmosis),
# #           cured meats, pate, liver, Vit A, raw fish that has not been pre-frozen (worms), shark, swordfish or marlin,
# #           minimise tuna (mercury)# quite a few soft cheeses are fine! Source NHS
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# allergen_basic = {'',''}
#
# # usually product of some type katsuobushi or fish sauce for example
# allergen_derived_no_recipe =  {'',''}
#
# # different names same thing
# allergen_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]
#
# # subsets - common name with various types
# allergen_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }
# def build_allergen_set():
#     allergen = {'allergen'}
#
#     for key, val in allergen_subsets.items():
#         union = val | {key}     # include the categegory generalisation
#         allergen = allergen | union
#
#     for val in allergen_alt:
#         allergen = allergen | val       # include different names for each allergen
#
#     allergen = allergen | allergen_derived_no_recipe
#
#     allergen = allergen | allergen_basic
#
#     return allergen







# ELEMENTS
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # HEADING
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# allergen_basic = {'',''}
#
# # usually product of some type katsuobushi or fish sauce for example
# allergen_derived_no_recipe =  {'',''}
#
# # different names same thing
# allergen_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]
#
# # subsets - common name with various types
# allergen_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }
# def build_allergen_set():
#     allergen = {'allergen'}
#
#     for key, val in allergen_subsets.items():
#         union = val | {key}     # include the categegory generalisation
#         allergen = allergen | union
#
#     for val in allergen_alt:
#         allergen = allergen | val       # include different names for each allergen
#
#     allergen = allergen | allergen_derived_no_recipe
#
#     allergen = allergen | allergen_basic
#
#     return allergen


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # COMBINATIONS
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#'vegan, veggie, cbs, , , , ns_pregnant'

# not striclty true but from a vegan perspective ok
#seafood = fish | molluscs | crustaceans

# NOT veggie
def build_not_veggie_set():
    not_veggie = build_chicken_set() |               \
                 build_duck_set() |                  \
                 build_pork_set() |                  \
                 build_beef_set() |                  \
                 build_molluscs_set() |              \
                 build_crustaceans_set() |           \
                 build_lamb_set() |                  \
                 build_fish_set() |                  \
                 build_game_set() |                  \
                 build_other_edible_animal_set()

    return not_veggie

# NOT vegan
def build_not_vegan_set():
    not_vegan = build_not_veggie_set() | \
                build_dairy_set() |      \
                build_eggs_set()

    return not_vegan



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# 'CONTAINS' TAG SETS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

containsTAGS_LUT = {
    'chicken' : build_chicken_set(),
    'pork' : build_pork_set(),
    'beef' : build_beef_set(),
    'shellfish' : build_molluscs_set() | build_crustaceans_set(),
    #'molluscs' : build_molluscs_set(),
    #'crustaceans' : build_crustaceans_set(),
    'lamb' : build_lamb_set(),
    'fish' : build_fish_set(),
    'game' : build_game_set(),
    #'insects' : TODO break out from other
    'other' : build_other_edible_animal_set(),
    # 'set_name' : build_XXX_set(),
}
inverse_containsTAGS_LUT = {
    'gluten_free' : build_gluten_set(),     # if its not in this set its gluten free!
    #'ns_pregnant' : build_XXX_set(),
    'veggie' : build_not_veggie_set(),    # if its not in this set its veggie!
    'vegan' : build_not_vegan_set(),      # if its not in this set its vegan!
}
# do we need the veggie / vegan sets?
veggie_mutex_set = set(['chicken','pork','beef','shellfish','molluscs','crustaceans','lamb','fish','game','insects','other'])
vegan_mutex_set = set(['chicken','pork','beef','shellfish','molluscs','crustaceans','lamb','fish','game','insects','other','eggs','dairy'])

    
def get_containsTAGS_for(list_of_ingredients, show_provenance=False):
    TAGS_detected = []

    if list_of_ingredients.__class__ == str:
        list_of_ingredients = [list_of_ingredients]

    if list_of_ingredients.__class__ == list:
        # build complete list - from local DB
        # will not follow URL to inet for ingredients of off the shelf items

        exploded_list = []
        for i in list_of_ingredients:
            exploded_list += get_ingredients_as_text_list_R(i)

        # filter err out of err>name<   - TODO REMOVE w/ ATOMIC implementation? Its passive only
            # scan_for_error_items returns a list of tuples (err, ingredient)
            # only errors unless return_all_ingredients=True
        exploded_list = [i for e, i in scan_for_error_items(exploded_list, return_all_ingredients=True) ]

        # flatten so there's only one of each
        list_of_ingredients = list(set(exploded_list))

        # TRUE LOOKUP
        for i in list_of_ingredients:
            for tag in containsTAGS_LUT:
                if i in containsTAGS_LUT[tag]:
                    TAGS_detected.append((tag, i))

        # INVERSE LOOKUP - build_atomic_ingredients
        # I think we only need this loop to get provenance info!
        if show_provenance:
            for i in list_of_ingredients:
                for tag in inverse_containsTAGS_LUT:
                    if i not in inverse_containsTAGS_LUT[tag]:
                        TAGS_detected.append((tag, i))
        
        vv_flag = True
        for i in list_of_ingredients:
            if i in inverse_containsTAGS_LUT['vegan']:
                vv_flag = False
                break   # no need to check any more!
                
        v_flag = True
        for i in list_of_ingredients:
            if i in inverse_containsTAGS_LUT['veggie']:
                v_flag = False
                break   # no need to check any more!
            
        gf_flag = True
        for i in list_of_ingredients:
            if i in inverse_containsTAGS_LUT['gluten_free']:
                gf_flag = False     # gluten found!!! brrr
                break   # no need to check any more!            

    else:
        raise(IncorrectTypeForIngredients("get_allergens_for: pass str or list"))

    if show_provenance:
        pprint(TAGS_detected)
        #pprint([ (t,i) for t,i in TAGS_detected if t == 'gluten_free'])

    TAGS_detected = set([ t for t,i in TAGS_detected])

    # meaty_goodness = TAGS_detected - set(['veggie', 'gluten_free', 'vegan'])
    # 
    # if meaty_goodness & vegan_mutex_set:
    #     TAGS_detected = TAGS_detected - set(['vegan'])
    # else:
    #     TAGS_detected = TAGS_detected or set(['vegan'])
    # 
    # if meaty_goodness & veggie_mutex_set:
    #     TAGS_detected = TAGS_detected - set(['veggie'])
    # else:
    #     TAGS_detected = TAGS_detected or set(['veggie'])

    if vv_flag:
        TAGS_detected = TAGS_detected or set(['vegan'])
    else:
        TAGS_detected = TAGS_detected - set(['vegan'])

    if v_flag:
        TAGS_detected = TAGS_detected or set(['veggie'])
    else:
        TAGS_detected = TAGS_detected - set(['veggie'])
        
    if gf_flag:
        TAGS_detected = TAGS_detected or set(['gluten_free'])
    else:
        TAGS_detected = TAGS_detected - set(['gluten_free'])

    return list(TAGS_detected)



def main():
    pass

if __name__ == '__main__':

    print('>--1')
    show_txt_title_NO_match_rcp = False
    if show_txt_title_NO_match_rcp == True:
        print(f"errors['txt_title_NO_match_rcp']: {len(errors['txt_title_NO_match_rcp'])}")
        for rcoi, ri_name in errors['txt_title_NO_match_rcp']:
            print(rcoi)
            pprint(atomic_LUT[rcoi]) if rcoi in atomic_LUT else print(f"NO: {rcoi} in atomic_LUT")
            print(ri_name)
            pprint(atomic_LUT[ri_name]) if ri_name in atomic_LUT else print(f"NO: {ri_name} in atomic_LUT")
            print('-')

    print('>--2')
    def dbg_i_list_as_text_from_component_name(c):
        i_list = get_ingredients_as_text_list_R(c)
        print(f"\n|\n|\n \_  I_LIST_as_text_FROM_component_NAME:{c}")
        print(f"\nLIST({c}){i_list}")
        return(i_list)

    def dbg_does_component_contain_allergen(c, a):
        print(f"\nDoes COMPONENT <<{c}>> contain ALLERGEN <<{a}>> ? <<{does_component_contain_allergen(c, a)}>> ")
    
    def dbg_get_allergens_for_component_recursive(c,sp=False):
        print(f"\nget_ALLERGENS_FOR_Recurse: {c}")
        print(f"\nALLERGENS:{get_allergens_for(get_ingredients_as_text_list_R(c), sp)}")
    
    def dbg_unroll_all_seperately(c,sp=False):
        for a in get_allergens_headings():
            print(f"\nDoes COMPONENT <<{c}>> contain ALLERGEN <<{a}>> ? <<{does_component_contain_allergen(c, a)}>> ")
        print(f"\nget_ALLERGENS_FOR_Recurse: {c}")
        print(get_allergens_for(get_ingredients_as_text_list_R(c), sp))
        
    def tag_test(c, sp):
        #dbg_i_list_as_text_from_component_name(c)
        t_list = get_containsTAGS_for(c, sp)
        print(f"\n\nTAGS:{t_list}")
        return(t_list)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# check errors & investigate 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -    
    def error_table(e):
        print(f"\n\n# # # # # # # # # # # errors['{e}'] ({len(errors[e])}) # # # # # # # # # # # S")    
        pprint(Counter(errors[e]).most_common())
        print(f"# # # # # # # # # # # errors['{e}'] # # # # # # # # # # # E\n\n")
    
    # for e in errors.keys():
    #     error_table(e)
    
    error_keys = [
                   'txt_title_NO_match_rcp',
                  # 'derived_w_file_HAS_ndb_no',
                  # 'ndb_no_neg99',
                   'derived_HAS_http_SB_ots',
                  # 'derived_HAS_atomic_alias',
                  # 'ots_ingredients_missing',
                  # 'ots_NO_url',
                  # 'unknown_alias',                  
                  # 'items_not_triggering_TAGS',
                   'dead_ends_in_this_pass',
                   'expected_derived_atomic_no_file'
                  ]

    for e in error_keys:
        error_table(e)
    
    print(f"\nCACHE_recipe_component_or_ingredient: {len(CACHE_recipe_component_or_ingredient)}")
    print("\nERRORS found")
    for e in errors.keys():
        print(f"{e} ({len(errors[e])})")

    print('>--3 Aliases')
    #pprint(aliases)
        
    print('>--4')
    
    def diagnostics(c, sp=False):
        print('> DIG = = = = - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  S get i_list')
        i_list = get_ingredients_as_text_list_R(c)
        print('> DIG = = = = - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  M1 allergens')
        a_list = get_allergens_for(get_ingredients_as_text_list_R(c), sp)
        print('> DIG = = = = - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  M2 tags')
        t_list = get_containsTAGS_for(c, sp)
        print('> DIG = = = = - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  M3 exploded for DB')
        component_list, i_sub_list = get_exploded_ingredients_and_components_for_DB_from_name(([],c))
        #print(f"COMPONENT_LIST: {component_list}")
        #print(f"I_SUB_LIST: {i_sub_list}")
        exploded_list = component_list + i_sub_list
        print('> DIG = = = = - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  RESULT - S')
        print(f"\nINGREDIENTS FOR ({c}): {i_list}")
        print(f"\nEXPLODED (included sub components DB) FOR ({c}): {exploded_list}")
        print(f"\nALLERGENS: {a_list}")
        print(f"\nTAGS: {t_list}")
        ots_i_miss_list = []
        for i in i_list:
            m = re.search(r'ots_i_miss>(.*?)<', i)
            if m:
                ots_i_miss_list.append(m.group(1))
        print(f"OTS_I_MISS: {ots_i_miss_list}")
        switch_aliases = []
        url_list = []
        for i in ots_i_miss_list:
            alias = follow_alias(i)                     # alias_with_link_or_ingredients
            if alias:
                switch_aliases.append((i, alias))                
                print(f"following: [{i}] alias to: [{alias}]")
                dump_atomic_LUT(alias)
                if atomic_LUT[alias]['url']: url_list.append(atomic_LUT[alias]['url'])
            else:
                dump_atomic_LUT(i)
                if atomic_LUT[i]['url']: url_list.append(atomic_LUT[i]['url'])
            print()
        print(f"{url_list}")
        if c not in CACHE_recipe_component_or_ingredient:
            get_ingredients_from_component_file(c)          # get & cache
        if c in CACHE_recipe_component_or_ingredient:
            print(CACHE_recipe_component_or_ingredient[c])
        else:
            print(f"I:'{c}' HAS NO FILE - atomic?:{atomic_LUT[c]['igdt_type']}")

        pprint(atomic_LUT[c])
        print('> DIG = = = = - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  - - -  RESULT - E')

    rcoi = 'beef & humous mini wrap' # Receipe Component Or Ingredient
    diagnostics(rcoi) # diagnostics(rcoi, True) # show provenance of allegen or tags
    search(rcoi)
    print(f"\n>--- atomic_LUT[{rcoi}] - - \ ")
    pprint(atomic_LUT[rcoi])



    print('\n'*15 + '\nSearch?')
    while(True):
        yn = input('Continue ingredient/(n)\n')
        if (yn=='') or (yn.strip().lower() == 'n'): sys.exit(0)
        diagnostics(yn)
        search(yn)        
    
    # beef & humous mini wrap:
    # exploded: baby spinach, beef, bell pepper, black pepper, bramley apples, butter, carrots, chillies, cone cabbage,
    #           coriander, coriander leaf, coriander seeds, cornflour, cumin seeds, fennel seeds, garlic, garlic puree,
    #           ginger, ground black pepper, honey, lemon juice, lemon zest, mustard flour, olive oil,
    #           
    #           ots_i_miss>cannellini beans<,
    #           ots_i_miss>mini wrap<,
    #           ots_i_miss>rapeseed oil<,              
    #           ots_i_miss>sriracha chilli sauce<,
    #           ots_i_miss>white wine vinegar<,
    #           
    #           paprika, rapeseed oil, red onion, rioja red wine, salt, savoy cabbage, sherry vinegar, sodium nitrite,
    #           spring onions, sugar, tomato, triphosphates, water


    
    # print('\nDump error table? Enter one of the following error KEYS . .')
    # while(True):
    #     [ print(e) for e in errors.keys() ]
    #     yn = input('Error type/(n)\n')
    #     if (yn=='') or (yn.strip().lower() == 'n'): sys.exit(0)
    #     #pprint(errors[yn])
    #     pprint(errors)
    #     pprint(aliases)    

    
    
# ELEMENTS
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # HEADING
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# allergen_basic = {'',''}
#
# # usually product of some type katsuobushi or fish sauce for example
# allergen_derived_no_recipe =  {'',''}
#
# # different names same thing
# allergen_alt = [
#     {'name1','name2'},
#     {'another1', 'another2'},
# ]
#
# # subsets - common name with various types
# allergen_subsets = {
#     'cod' : { 'pacific cod', 'atlantic cod' },
#     'snapper' : {'red snapper','northern red snapper','rockfish','rock cod','pacific snapper'}, # suspect grouping but hey, lets get it working!
# }
# def build_allergen_set():
#     allergen = {'allergen'}
#
#     for key, val in allergen_subsets.items():
#         union = val | {key}     # include the categegory generalisation
#         allergen = allergen | union
#
#     for val in allergen_alt:
#         allergen = allergen | val       # include different names for each allergen
#
#     allergen = allergen | allergen_derived_no_recipe
#
#     allergen = allergen | allergen_basic
#
#     return allergen


# TURN INTO TESTS
    # sp=True
    # tag_test('lamb kofte',sp)
    # # dbg_get_allergens_for_component_recursive
    # tag_test('lamb kofte v2',sp)
    # # dbg_get_allergens_for_component_recursive
    # tag_test('kofte & couscous salad sandwich',sp)
    # # dbg_get_allergens_for_component_recursive
    # tag_test('s&p prawns w squid',sp)
    # # dbg_get_allergens_for_component_recursive
    # tag_test('mini turkey ball kebab',sp)
    # # dbg_get_allergens_for_component_recursive
    # tag_test('prawn sauce w blue cheese & garlic',sp)
    # dbg_get_allergens_for_component_recursive('prawn sauce w blue cheese & garlic',sp)
    # dbg_get_allergens_for_component_recursive('lamb humous & kimchi mini wrap',sp)    
    # tag_test('lamb humous & kimchi mini wrap',sp)
    
    
    # OTS ingredient list processing tests
    # search_tag = 0
    # def dbg_process_ots_ingredient_string(tx):
    #     global search_tag
    #     search_tag += 1
    #     composite = process_ots_ingredient_string(tx)
    #     print('\n')
    #     pprint(composite)
    #     print(f"\n>-{search_tag}\n")
    #     print(tx)
    #     # print('\n')
    #     # pprint(t1.split(','))
    #     print('\n')
    # 
    # 
    # # https://www.sainsburys.co.uk/gol-ui/product/sainsburys-steak-red-wine-pie-taste-the-difference-500g
    # dbg_process_ots_ingredient_string("British Beef (31%), Fortified Wheat Flour (Wheat Flour, Calcium Carbonate, Iron, Niacin, Thiamin), Margarine (Palm Fat, Water, Rapeseed Oil, Salt, Emulsifier: Mono- and Diglycerides of Fatty Acids), Water, Butter 3.5% (Cows' Milk), Ruby Port (3%), Caramelised Onion (Onion, Muscovado Sugar, Sunflower Oil), Beef Stock Paste (Cooked Beef, Rehydrated Potato Flakes, Salt, Cane Molasses, Caramelised Sugar Syrup, Onion Powder, Black Pepper), Smoked Dry Cure British Bacon Lardons (2%) (Pork Belly, Sea Salt, Sugar, Preservatives: Sodium Nitrite, Sodium Nitrate; Antioxidant: Sodium Ascorbate), Malbec Red Wine (2%), Corn Starch, Barley Malt Extract, Dextrose, Rusk (Fortified Wheat Flour (Wheat Flour, Calcium Carbonate, Iron, Niacin, Thiamin), Water, Salt), Spirit Vinegar, Tomato Paste, Salt, Pasteurised Free Range Egg, White Pepper, Thyme, Bay, Black Pepper, Parsley.")
    # # https://www.sainsburys.co.uk/gol-ui/product/higgidy-spinach--feta---pine-nut-pie-270g
    # dbg_process_ots_ingredient_string("Water, Spinach (14%), Mature Cheddar Cheese (Milk), Feta Cheese (Milk) (12%), Sautéed Onion (Onions, Rapeseed Oil), Wheat Flour (contains Calcium Carbonate, Iron, Niacin, Thiamin), Vegetable Oils (Sustainable Palm Oil*, Rapeseed Oil), Free Range Whole Egg, Red Peppers (4%), Spelt Flour (Wheat), Dried Skimmed Milk, Cornflour, Butter (Milk), Double Cream (Milk), Pine Nuts, Brown Linseeds, Golden Linseeds, Poppy Seeds, Salt, Black Pepper, Nutmeg, Cayenne Pepper, Paprika, Mustard Powder, *www.higgidy.co.uk/palmoil")
    # # https://www.sainsburys.co.uk/gol-ui/product/lindahls-pro-kvarg-banoffee-pie-150g
    # dbg_process_ots_ingredient_string("Quark (Skimmed Milk, Whey Proteins (from Milk), Lactic Cultures, Microbial Rennet), Banana Caramel Flavour preparation [Water, Modified Maize Starch, Colour (Carotenes), Safflower Concentrate, Carrot Concentrate, Spirulina Concentrate, Natural Flavourings, Sweeteners (Aspartame, Acesulfame K)]")
    # #  https://www.sainsburys.co.uk/gol-ui/product/jssc-char-sui-pork-belly-450g
    # bpork = "British Pork Belly (80%), Char Sui Style Glaze (15%) (Water, Sugar, Soy Sauce (Water, Soy Beans (Soya), Salt, Spirit Vinegar), Fermented Soya Bean (Soy Beans (Soya), Water, Salt), Onions, Garlic Purée, Ginger Purée, Red Wine Vinegar, Cornflour, Red Chilli Purée , Caramelised Sugar Syrup, Concentrated Plum Juice, Star Anise, Cinnamon, Fennel Seed, Black Pepper, Clove), Brown Sugar, Home Pickling Mix (Sugar, Salt, Maltodextrin, Apple Cider Vinegar Powder, Acidity Regulator: Ascorbic Acid; Anti-caking Agent: Silicon Dioxide), Cornflour, Dehydrated Soy Sauce (Maltodextrin, Soy Beans (Soya), Salt, Spirit Vinegar), Garlic Powder, Caramelised Sugar, Colour: Beetroot Red; Onion Powder, Yeast Extract, Smoked Salt, Black Pepper, Acid: Citric Acid; Ginger, Salt, Chilli Powder, Stabiliser: Guar Gum; Paprika Extract, Pimento, Flavouring, Star Anise, Aniseed Extract."
    # dbg_process_ots_ingredient_string(bpork)
    # # https://www.sainsburys.co.uk/gol-ui/product/sainsburys-sweet---sour-chicken-with-rice-450g
    # dbg_process_ots_ingredient_string("Egg Fried Rice (Water, Long Grain Rice, Pasteurised Egg, Onion, Peas, Rapeseed Oil, Sesame Oil, Ginger Purée, Salt, Fermented Soya Bean, Wheat), Cooked Marinated Chicken Breast (20%) (Chicken Breast, Rapeseed Oil, Cornflour, Ginger Purée), Water, Sugar, Onion, Red Pepper, Pineapple, Tomato Paste, Cornflour, Concentrated Pineapple Juice, Spirit Vinegar, Rapeseed Oil, Ginger Purée, Salt, Colour:Paprika Extract; Fermented Soya Bean, Wheat, Cane Molasses, Onion Purée, Tamarind, Cinnamon, Clove, Garlic Purée.")
    # 



    # target = 'guinea fowl tagine w couscous & salad'
    #     # guinea fowl tagine (derived)
    #     #     chermoula (derived)
    #     # couscous chermoula (derived)
    #     #     veg stock (ots)
    #     # green leaf & orange beet (derived)
    #     #     orange beetroot (derived)
    #     #     lemon vinaigrette (derived)
    # pprint(atomic_LUT[target])
    # print('chicken - atomic_LUT')
    # pprint(atomic_LUT['chicken'])
    # print('chicken - component_file_LUT')
    # pprint(component_file_LUT[target])
    # 
    # print(f"\n\n> - - - - {target} - - - - <")
    # i_list = get_ingredients_as_text_list_R(target)
    # e_list = scan_for_error_items(i_list)
    # print(f"\n{i_list}")
    # print('problems:')
    # print(f"{e_list}")
    # print('\nCall DEP')
