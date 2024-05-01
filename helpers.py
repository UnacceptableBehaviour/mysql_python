#! /usr/bin/env python

# Quick note on generating a call graph - darwin / osx
	# $ pip install pycallgraph
	# $ brew install graphviz
	# $ pycallgraph --include "helpers.*" graphviz -- ./populate_db.py
	# # http://pycallgraph.slowchop.com/en/master/guide/command_line_usage.html

# helper functions

import csv
import itertools
import re
import copy                 # copy.deepcopy()
from pathlib import Path

from pprint import pprint # giza a look

# serve files from http://192.168.1.13:8000/static/sql_recipe_data.csv  < HTTP ASSET SERVER
# use http://127.0.0.1:8000 so SSL on main site doesn't block retrieval
# > cd /a_syllabus/lang/python/repos/asset_server
# > http-server -p 8000 --cors
#
# SSL asset.server
# https://asset.server:8080                                             < HTTPS ASSET SERVER
# > cd /a_syllabus/lang/python/repos/asset_server
# > http-server  --cors -S -C ./scratch/asCerts/server.crt -K ./scratch/asCerts/server.key
#
# do we still need --cors Cross Origin headers since its SSL?
#
import urllib.request
from  urllib.error import URLError

from food_sets import get_igdt_type
from food_sets import IGD_TYPE_UNCHECKED, IGD_TYPE_DERIVED 
from food_sets import get_exploded_ingredients_and_components_for_DB_from_name
# print('food_sets import IGD_TYPE_UNCHECKED, IGD_TYPE_DERIVED ')
# print(IGD_TYPE_UNCHECKED)
# print(IGD_TYPE_DERIVED)

# indexes for ingredients row
ATOMIC_INDEX = 0                    # default value is 1 - TRUE
QTY_IN_G_INDEX = 1
SERVING_INDEX = 2
INGREDIENT_INDEX = 3


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# load a csv file into a list of dictionaries
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_csv_from_server_as_disctionary(url):
    print("----- get_csv_from_server_as_disctionary -----------------------------------")

    url = urllib.parse.quote(url, safe='/:')  # replace spaces if there are any - urlencode
    print(url)

    csv_file = url.split('/')[-1]
    print(csv_file)

    local_file_name = f"./scratch/{csv_file}"
    
    print("> request <")
    pprint(urllib.request)
        
    while (not Path(local_file_name).exists()):
        try:    
            urllib.request.urlretrieve(url, local_file_name) # fails on HTTPS - need certs sorting
        except (ConnectionRefusedError, URLError):
            print('\n\nConnectionRefusedError: asset server must be serveing on HTTP  \
                \nOpen terminal. \
                \ncd python/asset_server; http-server -p 8000 --cors \
                \nHit RETURN to continue . .')
            wait = input()

    sql_dict = {}

    with open(local_file_name) as csv_to_sql_file:
        csv_reader = csv.DictReader(csv_to_sql_file, delimiter=',')

        entry = {}

        entries = 0

        for row in csv_reader:
            entry = {}                          # create a new dictionary for each entry

            for col_key in csv_reader.fieldnames:
                entry[col_key] = row[col_key]   # create and info dictionary

            sql_dict[entries] = entry

            entries +=1

    pprint(sql_dict[23])

    print("----- reponse ------------------------------------------------------------")
    print(sql_dict.__class__.__name__)
    print(type(sql_dict))
    print(f"ENTRIES: {len(sql_dict)} 0-{len(sql_dict)-1}")
    print(f">---------------------------------------- DICTIONARY LOADED >------------")
    
    Path(local_file_name).unlink(missing_ok=True)

    return sql_dict


def log_exception(message, exception):
    print("------ caught exception rectrieving url - - - - - - < S")
    print(f"NOTE:{message}\n")
    print(exception)
    f = open('./scratch/error_log.txt', 'a')
    f.write(f"\n\nNOTE: {message} <\n{exception}")
    f.close()
    print("------ caught exception rectrieving url - - - - - - < E")
    return 0



# (^-+- for the.*?Total \(.*?\)).*?(allergens:.*?tags:.*?$)* NO
# (^-+- for the.*?Total) \(.*?\) RECIPE
# ((^-+- for the.*?Total) \(.*?\)).*?(allergens:.*?$.*?tags:.*?$)   RECIPE w/ allergens following
# ((^-+- for the.*?Total) \(.*?\)).*?((allergens:(.*?)$.*?tags:(.*?)$)) RECIPE capture allergens & tags
# (^-+- for the.*?(tags:.*?$))  simplified RECIPE w tags
# example text:
# ------------------ for the swiss breakfast (1)
# 40g		swiss meusli no added sugar
# 10g		sugar
# 150g		semi skimmed milk
# 													Total (200g)
# method: put everything in bowl
# notes:
# description: describe me
# stars: 2
# allergens: dairy, nuts, seeds_lupin, gluten
# tags: veggie
# images:
# lead_image: 20200101_063015_swiss breakfast.jpg
# __end_recipe__
def process_single_recipe_text_into_dictionary(recipe_text, dbg_file_name='file_name.txt', dbg_print=False):
    recipe_info = None

    # REGEX: allergens & tags below recipe
    # ^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\).*?allergens:(.*?)$.*?tags:(.*?)$
    #ant_regex = re.compile(r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\).*?allergens:(.*?)$.*?tags:(.*?)$')

    # REGEX: recipe
    # ^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)
    #recipe_regex = re.compile(r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)')

    #ant_regex.search( recipe_text, re.MULTILINE | re.DOTALL )
    #match = ant_regex


    # try 'allergens & tags below recipe' match first since 'recipe' will match both
    # should match template: date_time_recipe_name_template.txt
    #                                   1      2               3                4                5               6           7          8              9         10        11         12               13           14
    match = re.search( r'^-+- for the (.*) \((\w+)\)[\s\w]*?$(.*)^\s+Total \((.*?)\).*?method:(.*?)description:(.*?)notes:(.*?)stars:(.*?)allergens:(.*?)tags:(.*?)type:(.*?)images:(.*?)lead_image:(.*?)username:(.*?)^.*?__end_recipe__', recipe_text, re.MULTILINE | re.DOTALL )

    #match = re.search( r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)', recipe_text, re.MULTILINE | re.DOTALL )
    if (match):
        # Matches
        # 1 - name
        # 2 - servings
        # 3 - ingredients
        # 4 - yield
        # 5 - method
        # 6 - notes
        # 7 - description
        # 8 - stars (user_rating)
        # 9 - allergens
        # 10 - tags
        # 11 - type
        # 12 - images (steps, image list)
        # 13 - lead image
        # 14 - username

        # easy to detect failure in the data
        recipe_info = {
            'ri_name':"Initialised as NO MATCH",
            'lead_image':'slms.jpg',
            'ingredients':"Pure green",
            'images':[ 'image_list.jpg' ],
            'method':'use your instinct, be creative',
            'notes':"it'll turn out better next time if you do this",
            'description':'invent_me',
            'user_rating':0,
            'username':'carter',
            'allergens': [ 'none_listed' ],
            'tags': [ 'none_listed' ],
            'types': [ 'none_listed' ],
            'servings': 0,
            'yield': '0g'
        }
        recipe_info['ri_name'] = match.group(1).strip()
        recipe_info['servings'] = match.group(2).strip()
        recipe_info['yield'] = match.group(4).strip()
        recipe_info['method'] = match.group(5).strip()
        recipe_info['description'] = match.group(6).strip()
        recipe_info['notes'] = match.group(7).strip()
        stars = match.group(8).strip()
        if stars == '':
            stars = 0
        recipe_info['user_rating'] = round(float(stars),1)
        recipe_info['allergens'] = [ a.strip() for a in match.group(9).strip().rstrip(",").split(',') ]    # create list of strings
        recipe_info['tags'] = [ a.strip() for a in match.group(10).strip().rstrip(",").split(',') ]
        recipe_info['types'] = [ a.strip() for a in match.group(11).strip().rstrip(",").split(',') ]
        recipe_info['images'] = match.group(12).strip()
        recipe_info['lead_image'] = match.group(13).strip()
        recipe_info['username'] = match.group(14).strip()
        # TODO fix magic numbers ^ 1-14

        # fix broken lines before processing
        # the return group is split mid line - this is used to fix that
        i_list = (''.join( match.group(3).strip() ) ).split("\n")


        # remove comments (after #) from ingredients in recipe: 10g allspice     # woa that's gonna be strong!
        for index, line in enumerate(i_list):
            i_list[index] = ( re.sub('#.*', '', line) ).strip()

        # print(">>>DEBUG<<<-S")
        # print(f"recipe_info['ri_name']:{recipe_info['ri_name']}< recipe_info['servings']:{recipe_info['servings']}<")
        # pprint(i_list)
        # print(">>>DEBUG<<<-E")

        # should check db to find subcomponents TODO - HIGH
        for index, line in enumerate(i_list):
            # split using tabs, remove white space, remove blanks
            line = line.split("\t")

            # use list comprehension to run function on each line_item
            # turn result into an list with [ ]  [contents of list]
            line = [line_item.strip() for line_item in line]

            # strip blanks out list() same as [] < assumption
            i_list[index] = list( filter(None, line) )

            # default to UKNOWN until all elements present
            i_list[index].insert(ATOMIC_INDEX, IGD_TYPE_UNCHECKED)

            #print(f"[{SERVING_INDEX}]\nline:{line} <\ni_list:{i_list[index]}<\nindex:{index}")
            #pprint(i_list)
            if not re.match(r'\(.*?\)', i_list[index][SERVING_INDEX]):  # look for serving info (x)
                i_list[index].insert(SERVING_INDEX,'(0)')                           # insert (0) if not present

            # look up igdt_type
            i_list[index][ATOMIC_INDEX] = get_igdt_type(i_list[index][INGREDIENT_INDEX])


        # TODO remove after schema redesign
        if recipe_info['allergens'][0] == "":
            recipe_info['allergens'] = [ 'none_listed' ]
        if recipe_info['tags'][0] == "":
            recipe_info['tags'] = [ 'none_listed' ]

        # if there is a weight where no of servings SB it means there is no spceific servings
        # its a by weigh component like flour rice or dough
        # replace the weight EG 430g with -1
        # DB is expecting a number not a string
        if re.match(r'\d+g', recipe_info['servings']):
            recipe_info['servings'] = -1
        else:
            pprint(re.match(r'g', recipe_info['servings']))

        if dbg_print:
            print('- - - - - process_single_recipe_text_into_dictionary')
            print(f"NAME: {recipe_info['ri_name']}")
            print(f"SERVINGS: ({recipe_info['servings']})")
            print(f"INGREDIENTS:\n")
            pprint(i_list)
            print(f"YIELD: {recipe_info['yield']}")
            print(f"ALLERGENS: {' '.join(recipe_info['allergens'])}")
            print(f"TAGS: {' '.join(recipe_info['tags'])}")

        recipe_info['ingredients'] = i_list

    else:
        msg = f"BAD TEMPLATE IN {dbg_file_name}\n{recipe_text}"
        print(f"{msg} \n< - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = < < !!")
        # raise exception here
        log_exception("\n** BAD TEMPLATE **\n", f"\n{recipe_text}\n")

    return recipe_info

def get_recipe_file_contents_from_asset_server(recipe_text_filename, dbg_print=False):
    recipe_text = 'FILE ACCESS ERROR: NO FILE or NO DATA IN FILE'

    if dbg_print: print("----- get_recipe_ingredients_and_yield -------------------------------------------------")
    #base_url = 'https://asset.server:8080/static/recipe/'
    base_url = 'http://127.0.0.1:8000/static/recipe/'
    url = f"{base_url}{recipe_text_filename}"
    if dbg_print: print(url)

    # IN  https://asset.server:8080/static/recipe/20190228_163410_monkfish and red pepper skewers.txt
    # url = url.replace(" ", "%20")          # WORKS
    # OUT https://asset.server:8080/static/recipe/20190228_163410_monkfish%20and%20red%20pepper%20skewers.txt

    # get recipe text from assest server
    url = urllib.parse.quote(url, safe='/:')  # WORKS - likely more robust
    if dbg_print: print(url)

    local_file_name = f"./scratch/{recipe_text_filename}"
    if dbg_print: print(local_file_name)

    try:
        ret_val = urllib.request.urlretrieve(url, local_file_name)
        #pprint(ret_val)

        file_info  = Path(local_file_name)

        if file_info.is_file():
            print(f"File downloaded: {file_info}")
            f = open(local_file_name, 'r')              # load local file to work with
        else:
            print(f"File NOT PRESENT: {file_info}")
            return

        recipe_text = f.read()
        f.close()

    except Exception as e:
        msg = f"Recipe txt file not present: {recipe_text_filename}"
        log_exception(msg, e)
        recipe_text = f"---- for the missing recipe (1)\n100\t ingredients\n  Total (0g)"

    finally:
        if dbg_print: print(f"RETRIEVED URL: finally segment")

    return recipe_text



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# load a text file from asset server
#                  - convert into recipe dictionary for each component
#                  - ingredients, yield & servings
#                  - end of reipe denoted by marker __end_recipe__
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_recipe_ingredients_and_yields_from_file(recipe_text_filename, recipe_name, dbg_print=False):
    recipe_with_tags = {}
    recipe_info = {}
    recipies_and_subcomponents = []

    orig_recipe_text = get_recipe_file_contents_from_asset_server(recipe_text_filename, dbg_print)
    if dbg_print: print("------------------------------------------------------------ ORIGINAL --------")
    # this text may have multiple components, only one of which might have tags!
    if dbg_print: print(orig_recipe_text)
    if dbg_print: print("#* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * <-==S")

    # create list of recipes - these have optionally listed fields - 'tags:', 'allergens:', 'notes:', 'description:', 'stars:'
    for m in re.finditer( r'(^-+- for the (.*?) \(.*?__end_recipe__)', orig_recipe_text, re.MULTILINE | re.DOTALL ):
        recipe_with_tags[m.group(2)] = m.group(1)
        #                    name         whole component / recipe


    # recipe_with_tags now has tags!
    for title, recipe_text in recipe_with_tags.items():
        if dbg_print: print(recipe_text)

        # create a dictionary for each recipe / subcoponent
        recipe_info = process_single_recipe_text_into_dictionary(recipe_text, recipe_text_filename, dbg_print)

        # collect components together and return a list of recipes
        recipies_and_subcomponents.append(recipe_info)

    if dbg_print: print("#* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * <-==EE")

    return recipies_and_subcomponents


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def ingredient_in_recipe_list(ingredient, recipies_and_subcomponents):
    found = None

    for recipe in recipies_and_subcomponents:
        if recipe['ri_name'] == ingredient[INGREDIENT_INDEX]:
            found = recipe

    return found

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# typical recipe
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#{'ingredients': [[0, '250g', '(0)', 'cauliflower'],    # sublist
#                 [0, '125g', '(0)', 'grapes'],
#                 [0, '200g', '(4)', 'tangerines'],
#                 [0, '55g', '(0)', 'dates'],
#   atomic >-------0, '8g', '(0)', 'coriander'],
#                 [0, '8g', '(0)', 'mint'],
#                 [0, '4g', '(0)', 'chillies'],
#   sub_comp >-----1, '45g', '(0)', 'pear and vanilla reduction lite'],
#                 [0, '2g', '(0)', 'salt'],
#                 [0, '2g', '(0)', 'black pepper'],
#                 [0, '30g', '(0)', 'flaked almonds']],
#  'ri_name': 'cauliflower california',
#  'igdt_type' : -1 to 3  see below
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# //  IGDT_TYPE: UNCHECKED / ATOMIC / DERIVED / OTS / DTK
# //                 -1         0        1       2     3
# let IGD_TYPE_UNCHECKED = -1;
# let IGD_TYPE_ATOMIC    = 0;
# let IGD_TYPE_DERIVED   = 1;
# let IGD_TYPE_OTS       = 2;   // Off The Shelf
# let IGD_TYPE_DTK       = 3;   // Daily TracKer 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# scans through the list of ingredients looking for subcompnents
# marks with atomic (index 0) with a 1 to indicate a subcomponent
# then recurive calls on that subcompnent to process its ingredients
def mark_subcomponents(recipies_and_subcomponents, recipe_dict, search_ingredient, dbg_print=False):

    #recipe_dict['atomic'] = 0    # deprecated use igdt_type instead
    recipe_dict['igdt_type'] = IGD_TYPE_DERIVED # TODO ATOMIC BREAKS DB create 

    if dbg_print: print(f"\tFOUND: {recipe_dict['ri_name']} <")

    # iterate through its ingredients and see if there is an entry for
    # that ingredient in the headline recipe ingredients list
    # if so it's a subcoponent, mark it and search it too                   *

    for i2, ingredient in enumerate(recipe_dict['ingredients']):
        if dbg_print: print(f"\t\ti2: {ingredient} <")

        recipe_is_a_subcomponent = ingredient_in_recipe_list(ingredient, recipies_and_subcomponents)

        if recipe_is_a_subcomponent:        # found a subcomponent
            if dbg_print: print(f"\t\t\tSUB MARKED: {recipe_is_a_subcomponent['ri_name']} <")

            recipe_dict['ingredients'][i2][ATOMIC_INDEX] = IGD_TYPE_DERIVED

            # check it's ingredients for sub components
            mark_subcomponents(recipies_and_subcomponents, recipe_is_a_subcomponent, ingredient, dbg_print)
            if dbg_print: print(f"\t\t\tend of SC --< {recipe_is_a_subcomponent['ri_name']}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def mark_ingredients_as_subcomponents_or_leave_as_atomic(recipies_and_subcomponents, headline_recipe_name, dbg_print=False):

    if dbg_print: print("== ENTER: mark_ingredients_as_subcomponents_or_leave_as_atomic -      -      -      -      -      -     |")
    if dbg_print: pprint(recipies_and_subcomponents)

    # find headline (recipe_name) recipe in list
    for i1, rcp in enumerate(recipies_and_subcomponents):
        if dbg_print: print(f"r_&_sc: {rcp['ri_name']} <")

        # look for headline recipe and start there
        if rcp['ri_name'] == headline_recipe_name:          # found headline recipe
            mark_subcomponents(recipies_and_subcomponents, recipies_and_subcomponents[i1], headline_recipe_name, dbg_print)

    if dbg_print: print("== EXIT: mark_ingredients_as_subcomponents_or_leave_as_atomic -      -      -      -      -      -      |")
    # if so call this function again passing in the subcomponent as the head



def is_recipe_in_nutrion_database(ri_name):
    return None


# TODO ATOMIC only 1 component ever passed in refactor
def merge_nutrient_information_into_each_dictionary(components, recipe_name, sql_row=''):
    # TODO ATOMIC - seem to remember this was to accomodate multiple components
    db_id = int(sql_row['ri_id']) * 100

    for i, r in enumerate(components):
        db_id += 1
        # print(f"merging:{r['ri_name']}")
        # pprint(sql_row)

        nutri_dict = is_recipe_in_nutrion_database(r['ri_name'])

        # merge data from relevant source
        if nutri_dict:
            components[i] = {**r, **nutri_dict}

        elif r['ri_name'] == sql_row['ri_name']:
            components[i] = {**r, **sql_row}

        else:
            print(f">{r['ri_name']}< NOT PRESENT IN Nutrient Database * * *")

        # print(f"merge_nutrient_information_into_each_dictionary:C-{i}")
        # components[i]['ri_id'] = db_id
        components[i]['ri_id'] = sql_row['ri_id']
        #pprint(components[i])
        #print(f"merged:{r['ri_name']} ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# creates recipe dictionaries based on the csv column headers
# and ingredients in the text files
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_list_of_recipes_and_components_from_recipe_id(sql_row, dbg_print=False):

    recipe_text_filename = sql_row['text_file']
    recipe_name = sql_row['ri_name']

    components = get_recipe_ingredients_and_yields_from_file(recipe_text_filename, recipe_name, dbg_print)

    if dbg_print: print(f"LIST:{type(components)} - - - - - - - - - - - - - - B E F O R E <*|*>")

    for r in components:
        if dbg_print: print("r in components - - - - - - < S ")
        if dbg_print: pprint(r)
        if dbg_print: print("r in components - - - - - - < E ")

    if dbg_print: print(f" - - 'ri_name's - - ")

    if dbg_print: print(f"RECURSING = = = = = = = = = = = = - - - - - - - - - - - - - - <S")
    mark_ingredients_as_subcomponents_or_leave_as_atomic(components, recipe_name, dbg_print)
    if dbg_print: print(f"RECURSING = = = = = = = = = = = = - - - - - - - - - - - - - - <E")


    if dbg_print: print(f"LIST:{type(components)} - - - - - - - - - - - - - - A F T E R <*|*>")

    for r in components:
        if dbg_print: print("r in components - - - - - - < S ")
        if dbg_print: pprint(r)
        if dbg_print: print("r in components - - - - - - < E ")

    if dbg_print: print(f" - - 'ri_name's - - ")

    if dbg_print: rint(f"MERGING = = = = = = = = = = = = - - - - - - - - - - - - - - <S {len(components)}")
    #
    #
    # TODO ATOMIC - is this function doing anything? - it add Nutrinfo & fuck up ri_id # !?
    merge_nutrient_information_into_each_dictionary(components, recipe_name, sql_row)
    #
    #
    #
    if dbg_print: print(f"MERGING = = = = = = = = = = = = - - - - - - - - - - - - - - <E")

    if dbg_print: print(f"LIST:{type(components)} - - - - - - - - - - - - - - A F T E R <*|*>")

    for r in components:
        if dbg_print: print("r in components - - - - - - < S ")
        if dbg_print: pprint(r)
        if dbg_print: print("r in components - - - - - - < E ")

    if dbg_print: print(f" - - 'ri_name's - - ")

    return components



def inc_recipe_counter(max_id):

    file_name = './scratch/rcp_count.txt'

    if Path(file_name).is_file():
        f = open(file_name, 'r')
        count = f.read()
        if count == '':
            count = 0
        f.close()
        print(f"read counter:{count}")
        count = int(count)
        count += 1
        count = count % (max_id-1)   # loop after reaching max_id

    else:
        print(f"initialise counter:0")
        count = 0

    f = open(file_name, 'w')
    f.write(str(count))
    f.close()
    print(f"wrote counter:{count}")

    return count




def qty_to_float(qty):
    qty = qty.lower().replace('ml','g')      # QUICK HACK to GET POC - CUE DENSITY POLICE
    qty = round( float( qty.replace('g','') ), 2)
    return qty

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# scans through the list of ingredients looking for subcomponents
# retrive ingredients and add them to headline recipe
# then recurive calls on that subcompnent to process its ingredients
def add_subcomponents_ingredients(recipies_and_subcomponents, recipe_dict, new_list, qty=0):

    if qty == 0:
        qty = qty_to_float( recipe_dict['yield'] )      # if passing in a recipe with no qty assume making 1 of them

    multiplier = (qty / qty_to_float( recipe_dict['yield'] ))

    # print("== ADD SUBC_BITS < < S")
    # pprint(recipe_dict)
    # print(f"mult {multiplier}")
    # print(f"qty {qty}")
    # print("== ADD SUBC_BITS < < E")

    # iterate through its ingredients and looking for subcomponents
    for i, ingredient in enumerate(recipe_dict['ingredients']):

        recipe_is_a_subcomponent = ingredient_in_recipe_list(ingredient, recipies_and_subcomponents)

        if recipe_is_a_subcomponent:        # found a subcomponent
            add_subcomponents_ingredients(recipies_and_subcomponents, recipe_is_a_subcomponent, new_list, qty_to_float(ingredient[QTY_IN_G_INDEX]) )
            #print(f"\t\t\tend of SC --< {recipe_is_a_subcomponent['ri_name']}")

        else:
            new_list = update_ingredients_list(new_list, ingredient, multiplier)

    return



def update_ingredients_list(master, new_item, multiplier):

    # all ingredients in g - remove
    qty = qty_to_float( new_item[QTY_IN_G_INDEX] ) * multiplier

    ingredient = new_item[INGREDIENT_INDEX]

    if ingredient in master:
        master[ingredient] += qty
    else:
        master[ingredient] = qty

    # print(f"\n-\nmaster class:{type(master)}")
    # pprint(master)
    # print(f"new_item class:{type(new_item)}")
    # pprint(new_item)
    # print(f"mult {multiplier}")
    # print(f"qty {qty}")
    # print(f"new_item class:{type(new_item)}\n-\n")

    return master


# CREATE TABLE IF NOT EXISTS exploded (
#   id BIGSERIAL PRIMARY KEY,
#   ri_id BIGINT NOT NULL UNIQUE,

#   ri_name VARCHAR(100) NOT NULL,
#   igdt_type SMALLINT DEFAULT -1,
  
#   ingredients     VARCHAR(1000) ARRAY,
# );
def create_exploded_recipe(sql_row):
    ri_name = sql_row['ri_name']
    c_list, i_list = get_exploded_ingredients_and_components_for_DB_from_name(([],ri_name))
    components_and_ingerdients_list = c_list + i_list

    print(f"c_list: {c_list}")
    print(f"i_list: {i_list}")
    print(f"components_and_ingerdients_list:\n{components_and_ingerdients_list}\n- - - /")

    db_entry = {
        'ri_id':        sql_row['ri_id'],
        'ri_name':      ri_name,
        'igdt_type':    get_igdt_type(ri_name),
        'ingredients':  components_and_ingerdients_list
    }
    return db_entry





if __name__ == '__main__':
    # print("-----  get CSV ------------------------------------S")
    # fetch_file = 'https://asset.server:8080/static/sql_recipe_data.csv'
    # get_csv_from_server_as_disctionary(fetch_file)
    # print("-----  get CSV ------------------------------------E")

    recipe_text = '20190103_170558_chicken beetroot w broccoli and greens.txt'
    #recipe_text = '20190109_143622_crabcakes.txt'
    #urllib.request = 'https://asset.server:8080/static/recipe/20190109_143622_crabcakes.txt'
    get_recipe_ingredients_and_yields_from_file_test(recipe_text,'chicken beetroot w broccoli and greens')
