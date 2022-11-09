#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import itertools
from pprint import pprint
from pathlib import Path


#from helpers_db import get_ingredients_as_text_list

atomic_LUT = {}
components_aliases_LUT = {} # need?
NUTREINT_FILE_PATH = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info.txt')

component_file_LUT = {}
COMPONENT_DIR_PATH = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/')

def search(search_term):
    print(f"\n==> Searching for {search_term} . .\n")
    for i in atomic_LUT.keys():
        if re.search(search_term, i):
            print(f"{i.ljust(40)} - {atomic_LUT[i]['ndb_no_url_alias']}", end='\t')
            alias = re.sub('ndb_no=', '', atomic_LUT[i]['ndb_no_url_alias'])
            if i in component_file_LUT.keys():          print(f"rcoi:{component_file_LUT[i].name}")
            elif alias in component_file_LUT.keys():    print(f"A:{alias} - {component_file_LUT[alias].name}")
            else: print()
    
    print(f"\n ^ ingredients w/ {search_term} \n")


def build_file_LUT():
    file_list = COMPONENT_DIR_PATH.glob('*_NUTRITEST_recipes_*/_i_w_r_auto_tmp/*.txt')
    for f in file_list:
        m = re.search(r'\d{8}_\d{6}_(.*?).txt', str(f))
        if m:
            #print(f"{m.group(1)} - {f.name}")
            component_file_LUT[m.group(1)] = f
            get_ingredients_from_component_file(m.group(1)) # cache file & log rcoi/ri_name mismatch


errors = {
    'txt_title_NO_match_rcp':[],        #
    'derived_w_file_HAS_ndb_no':[],     #
    'ndb_no_neg99':[],                  #
    'derived_HAS_http_SB_ots': [],      #
    'derived_HAS_atomic_alias':[],
    'ots_ingredients_missing':[],       #
    'unknown_alias':[],
}
aliases = {}
def build_atomic_LUT():
    aliases = {}
    content = ''
    with NUTREINT_FILE_PATH.open('r') as f:
        #content = f.readlines()
        content = f.read()

    for m in re.finditer( r'--- for the nutrition information(.*?)\((.*?)\).*?ingredients:(.*?)$.*?igdt_type:(.*?)$', content, re.MULTILINE | re.DOTALL ):
        component, ndb_no_url_alias, ingredients, igdt_type = m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()
        if component == '': continue
        # print(f"{component}", end=':')
        # print(f"{component in atomic_LUT.keys()}", end=' ')
        # pprint(atomic_LUT)
        atomic_LUT[component] = {}        
        atomic_LUT[component]['ingredients'] = ingredients
        atomic_LUT[component]['igdt_type'] = igdt_type
        atomic_LUT[component]['ndb_no_url_alias'] = ndb_no_url_alias
        # (ndb_no=https://www.bla)      # online resource to ingredient
        # (ndb_no=11367)                # info from FDA DB - \(ndb_no=\d+\)
        # (per 100g)                    # derived ingredient
        # (ndb_no=-99)
        # (ndb_no=sea bream fillets)    # alias to another entry - which could be any of the above
        if ( re.search('\(ndb_no=\d+\)', ndb_no_url_alias) ):
            alias = (re.search('\(ndb_no=(\d+)\)', ndb_no_url_alias).group(1))
            # track multiples
            if alias in aliases:
                aliases[alias].append(component)
            else:
                aliases[alias] = [component]
            if alias in component_file_LUT:
                atomic_LUT[component]['alias'] = alias
        
        if ('http' in ndb_no_url_alias):
            errors['derived_HAS_http_SB_ots'].append((component, igdt_type, ndb_no_url_alias))
        
        if (ndb_no_url_alias == 'ndb_no=-99'):
            errors['ndb_no_neg99'].append((component, igdt_type))
        
        if (igdt_type == 'ots') and (ingredients == '__igdts__'):
            errors['ots_ingredients_missing'].append((component, '__igdts__'))
            
        if (igdt_type == 'derived') and (component in component_file_LUT) and (re.search('\(ndb_no=\d+\)', ndb_no_url_alias)):
            ndb_no = re.search('\(ndb_no=(\d+)\)', ndb_no_url_alias).group(1)
            errors['derived_w_file_HAS_ndb_no'].append(component)
            
        if (igdt_type == 'derived') and (ndb_no_url_alias != 'per 100g'):          
            if ('http' not in ndb_no_url_alias) and not ( re.search('\(ndb_no=\d+\)', ndb_no_url_alias) ):
                alias = re.sub('ndb_no=', '', ndb_no_url_alias)
            print(component)
            if component in component_file_LUT: print(component_file_LUT[component])
            elif alias in component_file_LUT: print(f"{alias} - {component_file_LUT[alias]}")            
            else:
                r = re.search('\(ndb_no=\d+\)', ndb_no_url_alias)
                pprint(r)
                print(f"no file - C:{component} - A:{alias} - {r}")
            pprint(atomic_LUT[component])
            print()
        

    return len(atomic_LUT)

# keep it simple to start
# remove QUID (34%) no's - these could be used to revese engineer a recipe in conjunction w/ nutrition info
# downcase and remove whitespace and .
def process_off_the_shelf_ingredients_list(i_list):    
    # new_list = [ re.sub('\(\d+%\)', '', i).lower().strip(' .') for i in i_list.split(',') ]
    # print(i_list)
    # print(new_list)
    return [ re.sub('\(\d+%\)', '', i).lower().strip(' .') for i in i_list.split(',') ]

def parse_igdt_lines_into_igdt_list(lines=''):
    i_list = []

    lines = [ l.strip() for l in lines.splitlines() ]
    lines = list(filter(None, lines))

    # remove qty & comment from each line
    for line in lines:
        parts = [ item.strip() for item in line.split('\t') if (len(item) > 0) & ('#' not in item) & ('(' not in item) ] # remove comments
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
        with component_file_LUT[rcoi].open('r') as f:
            content = f.read()
            CACHE_recipe_component_or_ingredient[rcoi] = content
    
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


# recursive compile ingredients including OTS if ingredients available    
def get_ingredients_as_text_list(recipe_component_or_ingredient, d=0): # takes str:name
    d += 1
    rcoi = recipe_component_or_ingredient
    i_list = [f"unknown_component:{rcoi}"]
    
    if rcoi in atomic_LUT:
        igdt_type = atomic_LUT[rcoi]['igdt_type']
        
        if igdt_type == 'atomic':
            i_list = [atomic_LUT[rcoi]['ingredients']] if atomic_LUT[rcoi]['ingredients'] != '__igdts__' else [rcoi]
        
        elif igdt_type == 'ots':
            if atomic_LUT[rcoi]['ingredients'] == '__igdts__':
                i_list = [f"ots_i_miss>{rcoi}<"]
            else:
                # TODO need an ingredients processing call - a lot of different formats
                i_list = process_off_the_shelf_ingredients_list(atomic_LUT[rcoi]['ingredients'])
        
        elif igdt_type == 'derived':
            if rcoi not in component_file_LUT:
                print(atomic_LUT[rcoi])
                alias = re.sub('ndb_no=', '', atomic_LUT[rcoi]['ndb_no_url_alias'])
                if alias in component_file_LUT:
                    print(f"{'    '*(d-1)}=A> {alias} < file [{component_file_LUT[alias].name}]")
                    s_list = get_ingredients_from_component_file(alias)
                else:
                    s_list = [f"alias_NF>{rcoi}|{alias}<"]            
            else:
                print(f"{'    '*(d-1)}==> {rcoi} < file [{component_file_LUT[rcoi].name}]")
                s_list = get_ingredients_from_component_file(rcoi)
            #print(f"{'    '*d}L:", end=' ')
            print(s_list)
            if s_list == 'ERROR: bad_template':
                i_list = [f"bad_template_in_file>{rcoi}<"]
            else:
                i_list = []
                for i in s_list:
                    print_list = get_ingredients_as_text_list(i,d)
                    i_list = i_list + print_list
                    print(f"{'    '*d}{print_list}")
            
            # pass them one at a time to get_ingredients_as_text_list
            #i_list = i_list + get_ingredients_as_text_list(rcoi) 
        else:
            i_list = [f"unknown_igdt_type>{rcoi}<"]
    
    return i_list



build_file_LUT()

#atomic_LUT['chicken']['ndb_no_url_alias'] = 'holy smoke batman'
build_atomic_LUT()
#pprint([(k, atomic_LUT[k]['ndb_no_url_alias']) for k in atomic_LUT.keys() if atomic_LUT[k]['igdt_type'] == 'atomic'])
#pprint(atomic_LUT['chicken'])

#pprint()

target = 'guinea fowl tagine w couscous & salad'
    # guinea fowl tagine (derived)
    #     chermoula (derived)
    # couscous chermoula (derived)
    #     veg stock (ots)
    # green leaf & orange beet (derived)
    #     orange beetroot (derived)
    #     lemon vinaigrette (derived)
pprint(atomic_LUT[target])
print('chicken - atomic_LUT')
pprint(atomic_LUT['chicken'])
print('chicken - component_file_LUT')
pprint(component_file_LUT[target])

print(f"> - - - - {target} - - - - <")
print(get_ingredients_as_text_list(target))

show_txt_title_NO_match_rcp = False
if show_txt_title_NO_match_rcp == True:
    print(f"errors['txt_title_NO_match_rcp']: {len(errors['txt_title_NO_match_rcp'])}")
    for rcoi, ri_name in errors['txt_title_NO_match_rcp']:
        print(rcoi)
        pprint(atomic_LUT[rcoi]) if rcoi in atomic_LUT else print(f"NO: {rcoi} in atomic_LUT")
        print(ri_name)
        pprint(atomic_LUT[ri_name]) if ri_name in atomic_LUT else print(f"NO: {ri_name} in atomic_LUT")
        print('-')


print(f"\nCACHE_recipe_component_or_ingredient: {len(CACHE_recipe_component_or_ingredient)}")
print("\nERRORS found")
for e in errors.keys():
    print(f"{e} ({len(errors[e])})")


print('\nSearch?')
while(True):
    yn = input('Continue ingredient/(n)\n')
    if (yn=='') or (yn.strip().lower() == 'n'): sys.exit(0)
    search(yn)

sys.exit(0)

# def build_atomic_ingredients():
#     atomic_ingredients = set()
# 
#     content = ''
#     with NUTREINT_FILE_PATH.open('r') as f:
#         #content = f.readlines()
#         content = f.read()
# 
#     for m in re.finditer( r'--- for the nutrition information(.*?)\(.*?igdt_type:(.*?)$', content, re.MULTILINE | re.DOTALL ):
#         ingredient = m.group(1).strip()
#         igdt_type =  m.group(2).strip()
#         if igdt_type == 'atomic':       # ots = off the shelf, derived = in house recipe, atomic = basic ingredient
#             atomic_ingredients = atomic_ingredients | {ingredient}
# 
#     return atomic_ingredients


def build_igdt_type_dict():
    pass





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
               'casein','custard','ice cream','milk powder'}

# usually product of some type katsuobushi or fish sauce for example
dairy_derived_no_recipe =  {'panna cota','brussels pate', 'cheese cake', 'creme patissiere','roulade'}

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
                  'abergavenny goats cheese'}
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
    'butter' : {'salted butter','cornish butter','ghee','clarified butter'},
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
              'egg solids','egg white','egg yolk'}

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

nuts_derived_no_recipe = {'mortadella','salted cashews','honey roast peanuts','honey roast cashews','baklava','cantuccini','almond oil'}

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

    return fish


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# SHELLFISH - MOLLUSCS - theres quite a list here: https://en.wikipedia.org/wiki/List_of_edible_molluscs
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
molluscs_basic = {'abalone','escargot','squid','hereford snail','mussel','limpits','winkles','whelks','clams','mussels',
                  'oyster','scallop','octopus','squid','cuttlefish'}

molluscs_derived_no_recipe =  {'oyster sauce', 'smoked mussels inc oil', 'smoked mussels'}

# different names same thing
molluscs_alt = [
    {'snails','escargot','helix aspersa'},
    {'cuttlefish', 'sepia'},
    {'small squid','small squid tubes','squid tubes','squid'},
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

def build_molluscs_set():
    molluscs = {'molluscs'}

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
crustaceans_basic = {'crustaceans','langoustine','crab','crayfish','prawns','shrimp','langostino','lobster'}

# usually product of some type katsuobushi or fish sauce for example
crustaceans_derived_no_recipe =  {'salt and pepper squid','lobster bisque', 'shrimp paste'}

# different names same thing
crustaceans_alt = [
    {'langostino', 'squat lobster'},
    {'norway lobster', 'dublin bay prawn', 'langoustine','langostine'},
    {'prawns','shrimp'},
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
    crustaceans = {'crustaceans'}

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
gluten_basic = {'gluten','wheat','wheat germ','rye','barley','bulgur','couscous','farina','graham flour',
                'kamut','khorasan wheat','semolina','spelt','triticale','oats','oat bran','flour' }

# usually product of some type katsuobushi or fish sauce for example
gluten_derived_no_recipe =  {'malt vinegar','pasta','bread','pastry','pizza','seitan','flat bread','lamb samosa','veg samosa',
                             'samosa'}

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
    'flour' : { 'plain flour','self raising flour','strong flour','bread flour' },
    'flat bread' : {'torta','matzo','pita','naan','roti','paratha','banh','tortilla','wrap','injera','pancake'}, # injera is gluten free if made of 100% teff flour
    'pasta' : {'orzo','spaghetti','macaroni','tagliatele','linguini','fusili','lasagna','rigatoni','farfale','ravioli',
               'fettuccini','penne'}, # a a million other types!
    'bread' : {'sliced bread','sourdough','brown bread','tiger loaf','french stick','giraffe bread','baguette','burger bun',
               'brioche','demi brioche','baton','biscuit','bagel','cornbread','rye bread','milk bread','galic pizza',
               'garlic bread','turkish bread','ciabata','bun','focaccia','mgt','multi grain','seeded batch','thick sliced bread',
               'thick sliced seeded bread','sandwich loaf','white bread','olive bread','poppy seed roll','bap', 'crumpet',
               'seeded baguette','seeded baguette round','baguette round','sourdough round','wholemeal tortilla wrap'},
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
soya_basic = {'soy','soya','edamame','soy sauce','tofu','soy milk','condensed soy milk','miso','soy nuts','tamari','shoyu',
              'teriyaki','tempeh','textured soy protein','tsp','textured vegetable protein','tvp','soy flour',
              'soybean oil','soy lecithin','natto','kinako'}

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
sulphur_dioxide_basic = {'sulphur dioxide', 'sulphites'}

# usually product of some type katsuobushi or fish sauce for example
#sulphur_dioxide_derived_no_recipe =  {'',''}

def build_sulphur_dioxide_set():
    sulphur_dioxide = {'sulphur_dioxide'}

    #sulphur_dioxide = sulphur_dioxide | sulphur_dioxide_derived_no_recipe

    sulphur_dioxide = sulphur_dioxide | sulphur_dioxide_basic

    return sulphur_dioxide



#pork
# coppa
# milano salami
# milano salami pre crisp
# milano salami crisp
# modena salami
# modena crisps

conv_list ='''
plain text list here
'''






# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# HEADINGS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_allergens_headings():
    return {'dairy', 'eggs', 'peanuts', 'nuts', 'seeds_lupin', 'seeds_sesame', 'seeds_mustard', 'fish', 'shellfish', 'molluscs', 'crustaceans', 'alcohol', 'celery', 'gluten', 'soya', 'sulphur_dioxide'}

# ingredients for each component already recursed and stored in exploded
# add_subcomponents_ingredients
def does_component_contain_allergen(component, allergen):
    allergen_present = False

    if allergen in get_allergens_headings():
        allergen_set = allergenLUT[allergen]
    else:
        raise(UnkownAllergenType(f"ERROR: unknown allergen: {allergen} <"))

    ingredients_of_component = get_ingredients_as_text_list(component)

    if ingredients_of_component == None:     # its an ATOMIC ingredient
        return component in allergen_set

    else:
        for i in ingredients_of_component:
            if i in allergen_set:
                return True

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
    'molluscs' : build_molluscs_set(),
    'crustaceans' : build_crustaceans_set(),
    'alcohol' : build_alcohol_set(),
    'celery' : build_celery_set(),
    'gluten' : build_gluten_set(),
    'soya' : build_soya_set(),
    'sulphur_dioxide' : build_sulphur_dioxide_set()
}

def get_allergens_for(list_of_ingredients):
    allergens_detected = []

    if list_of_ingredients.__class__ == str:
        list_of_ingredients = [list_of_ingredients]

    if list_of_ingredients.__class__ == list:
        # build complete list - from local DB
        # will not follow URL to inet for ingredients of off the shelf items

        add_ingredients = []
        for i in list_of_ingredients:
            add_me = get_ingredients_as_text_list(i)
            if add_me:
                add_ingredients = add_ingredients + add_me
            else:   # ingredient not in DB
                #print(f"INGREDIENT NOT FOUND IN DATABASE: {i} << WARNING * *")
                #print(f"NF:{i}<")
                pass # TODO - log


        # flatten so there's only one of each
        list_of_ingredients = list(set(list_of_ingredients + add_ingredients))

        for i in list_of_ingredients:
            for allergen in allergenLUT:
                if i in allergenLUT[allergen]:
                    allergens_detected.append(allergen)

    else:
        raise(IncorrectTypeForIngredients("get_allergens_for: pass str or list"))

    allergens_detected = list(set(allergens_detected))

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
pork_basic = {'pork','carvery pork','pork belly','roast pork','trotters','pigs trotters','pigs ears','roast peppered pork loin',
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
    'cured pork' : {'milano','salami','parma','parma ham','serano ham','serano','lomo','chorizo','fuet','charcuterie','pancetta',
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
              'diced beef','stewing beef','casserole steak','braising steak','beef flank','hanger steak','gelatine powder'}

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
              'lamb chuck','lamb loin','saddle of lamb'}

# usually product of some type katsuobushi or fish sauce for example
lamb_derived_no_recipe =  {'lamb samosa','lamb kofte','donner kebab','lamb bao bun'}

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

    for val in duck_alt:
        duck = duck | val       # include different names for each duck

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
    #'crustaceans' : build_crustaceans_set(),
    'lamb' : build_lamb_set(),
    'fish' : build_fish_set(),
    'game' : build_game_set(),
    'other' : build_other_edible_animal_set(),
    # 'set_name' : build_XXX_set(),
}
inverse_containsTAGS_LUT = {
    #'gluten_free' : build_gluten_set(),     # if its not in this set its gluten free!
    # 'ns_pregnant' : build_XXX_set(),
    'veggie' : build_not_veggie_set(),    # if its not in this set its veggie!
    'vegan' : build_not_vegan_set(),      # if its not in this set its vegan!
}

def get_containsTAGS_for(list_of_ingredients):
    containsTAGS_detected = []

    if list_of_ingredients.__class__ == str:
        list_of_ingredients = [list_of_ingredients]

    if list_of_ingredients.__class__ == list:
        # build complete list - from local DB
        # will not follow URL to inet for ingredients of off the shelf items

        add_ingredients = []
        for i in list_of_ingredients:
            add_me = get_ingredients_as_text_list(i)
            if add_me:
                add_ingredients = add_ingredients + add_me
            else:   # ingredient not in DB
                #print(f"INGREDIENT NOT FOUND IN DATABASE: {i} << WARNING * *")
                #print(f"NF:{i}<")
                pass # TODO - log


        # flatten so there's only one of each
        list_of_ingredients = list(set(list_of_ingredients + add_ingredients))

        # TRUE LOOKUP
        for i in list_of_ingredients:
            for containsTAG in containsTAGS_LUT:
                if i in containsTAGS_LUT[containsTAG]:
                    containsTAGS_detected.append(containsTAG)

        # INVERSE LOOKUP - build_atomic_ingredients
        remove_tags = []
        for i in list_of_ingredients:

            for containsTAG in inverse_containsTAGS_LUT:
                if (get_ingredients_as_text_list(i) != None) or (i in atomic_LUT.keys()) :         # it has to be in the data base to work!
                    containsTAGS_detected.append(containsTAG)

                #print(f"containsTAGS_detected:{containsTAGS_detected} - - - -")
                #print(f"checking SET:{containsTAG} for {i}")
                if i in inverse_containsTAGS_LUT[containsTAG]:
                    # DBG_LEV_4 print(f"\tSET:{containsTAG} - {i} NOT PRESENT")
                    remove_tags.append(containsTAG)

        # at on of this containsTAGS_detected may look like ['veggie','vegan','veggie','veggie','vegan']
        # flatten it to ['veggie','vegan']
        # if a single occurance of a non veggie or non vegan item occured remove the veggie or vegan tag
        containsTAGS_detected = set(containsTAGS_detected)
        # DBG_LEV_4 print(f"containsTAGS_detected:{containsTAGS_detected} - - - - S")
        # DBG_LEV_4 print(f"remove_tags: {remove_tags}")
        remove_tags = set(remove_tags)
        containsTAGS_detected = containsTAGS_detected - remove_tags
        # DBG_LEV_4 print(f"containsTAGS_detected:{containsTAGS_detected} - - - - E")

    else:
        raise(IncorrectTypeForIngredients("get_allergens_for: pass str or list"))


    containsTAGS_detected = list(set(containsTAGS_detected))    # remove duplicates

    return containsTAGS_detected



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

    #print(build_fish_set())

    #print(cheese_subsets)

    # cheese = {'cheese'}
    # #[cheese | cheese_set for cheese_set in cheese_subsets ]
    # for cheese_cat, cheese_set in cheese_subsets.items():
    #     cheese = cheese | {cheese_cat} | cheese_set
    #
    # print(cheese) # all the cheese



    # print('NON VEGAN')
    # print(build_not_vegan_set())

    print('\ncauliflower california')
    print(get_ingredients_as_text_list('cauliflower california'))

    print('\ncardamom donuts w lamb & harissa broth')
    print(get_ingredients_as_text_list('cardamom donuts w lamb & harissa broth'))

    #
    print('\ntiger baguette round')
    print(get_ingredients_as_text_list('tiger baguette round'))


    print("\nget_ingredients_as_text_list('pork fennel & orange kofte')")
    print(get_ingredients_as_text_list('pork fennel & orange kofte'))

    print("\nget_ingredients_as_text_list('plain turkey & chicken kofte mix')")
    print(get_ingredients_as_text_list('plain turkey & chicken kofte mix'))

    print("\ndoes_component_contain_allergen('pork fennel & orange kofte', 'dairy')")
    print(does_component_contain_allergen('pork fennel & orange kofte', 'dairy'))

    print("\ndoes_component_contain_allergen('pork fennel & orange kofte', 'soya')")
    print(does_component_contain_allergen('pork fennel & orange kofte', 'soya'))

    print("\ndoes_component_contain_allergen('plain turkey & chicken kofte mix', 'soya')")
    print(does_component_contain_allergen('plain turkey & chicken kofte mix', 'soya'))


    print("\nget_allergens_for(get_ingredients_as_text_list('pork fennel & orange kofte'))")
    print(get_allergens_for(get_ingredients_as_text_list('pork fennel & orange kofte')))

    print("\nget_allergens_for(get_ingredients_as_text_list('plain turkey & chicken kofte mix'))")
    print(get_allergens_for(get_ingredients_as_text_list('plain turkey & chicken kofte mix')))

    # TODO does_component_contain_allergen NOT recursive

    print("\n\n - - - - ATOMIC - - - - \n\n")
    print(build_atomic_ingredients())
    #
    # print(get_ingredients_as_text_list('tomatoes'))
    #
    # print(get_containsTAGS_for('hatchet salad'))
    # print(get_allergens_for('hatchet salad'))
    #
    # containsTAGS_detected = []
    # containsTAGS_detected = set(containsTAGS_detected) | {'blarny'}
    # print(containsTAGS_detected)
    # containsTAGS_detected = set(containsTAGS_detected) | {'double blarny'}
    # print(containsTAGS_detected)
    # # for tag in containsTAGS_detected:       < SORRY NO CAN DO - RuntimeError: Set changed size during iteration
    # #     print(f"DISCARDING: {tag}")
    # #     containsTAGS_detected.discard(tag)
    # # containsTAGS_detected = set(containsTAGS_detected)  - {'blarny'}
    # print(containsTAGS_detected)

    # print('- - -')
    # print(build_not_vegan_set())

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
