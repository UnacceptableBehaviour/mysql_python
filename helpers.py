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

# serve files from http://192.168.1.13:8000/static/sql_recipe_data.csv
# $ cd /a_syllabus/lang/python/repos/assest_server 
# $ http-server -p 8000 --cors 
import urllib.request
# urllib.request.urlretrieve ("http://192.168.1.13:8000/static/sql_recipe_data.csv", "sql_recipe_data.csv")
# url = urllib.parse.quote(url, safe='/:')  # make sure files w/ spaces OK

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
def get_csv_from_server_as_disctionary(force_reload=False):
    url = 'http://192.168.1.13:8000/static/sql_recipe_data.csv'       
    print("----- get_csv_from_server_as_disctionary -----------------------------------")    
    
    url = urllib.parse.quote(url, safe='/:')  # replace spaces if there are any - urlencode
    print(url)
    
    csv_file = url.split('/')[-1]    
    print(csv_file)
    
    local_file_name = f"./scratch/{csv_file}"

    urllib.request.urlretrieve(url, local_file_name)

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

def process_single_recipe_text_into_dictionary(recipe_text, dbg_file_name='file_name.txt'):
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
    match = re.search( r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\).*?description:(.*?)$.*?stars:(.*?)$.*?allergens:(.*?)$.*?tags:(.*?)$', recipe_text, re.MULTILINE | re.DOTALL )
    we_have_tags = True
    
    if (match == None):
        match = re.search( r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)', recipe_text, re.MULTILINE | re.DOTALL )
        we_have_tags = False
        #recipe_regex.search( recipe_text, re.MULTILINE | re.DOTALL )
        #match = recipe_regex

    #match = re.search( r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)', recipe_text, re.MULTILINE | re.DOTALL )
    if (match):
        # Matches
        # 1 - name
        # 2 - servings
        # 3 - ingredients
        # 4 - yield
        # 5 - description
        # 6 - stars (user_rating)
        # 7 - allergens
        # 8 - tags
        
        # easy to detect failure in the data
        recipe_info = {
            'ri_name':"Initialised as NO MATCH",
            'ingredients':"Pure green",
            'description':'invent_me',
            'user_rating':0,
            'allergens': [ 'none_listed' ],
            'tags': [ 'none_listed' ],
            'servings': 0,
            'yield': '0g'
        }     
        recipe_info['ri_name'] = match.group(1).strip()
        recipe_info['servings'] = match.group(2).strip()
        recipe_info['yield'] = match.group(4).strip()

        
        # fix broken lines before processing
        # the return group is split mid line - this is used to fix that
        i_list = (''.join( match.group(3).strip() ) ).split("\n")
        
        # remove comments (after #) from ingredients in recipe: 10g allspice     # woa that's gonna be strong!
        for index, line in enumerate(i_list):
            i_list[index] = ( re.sub('#.*', '', line) ).strip()
            
        # shold check db to find subcomponents
        for index, line in enumerate(i_list):
            # split using tabs, remove white space, remove blanks
            line = line.split("\t")
            
            # use list comprehension to run function on each line_item
            # turn result into an list with [ ]  [contents of list]
            line = [line_item.strip() for line_item in line]
            
            # strip blanks out list() same as [] < assumption
            i_list[index] = list( filter(None, line) )
            
            # default to ATOMIC until subcomponent found
            i_list[index].insert(ATOMIC_INDEX,1)                                   # indicates atmonic ingredient            
            
            if not re.match(r'\(.*?\)', i_list[index][SERVING_INDEX]):  # look for serving info (x)                
                i_list[index].insert(SERVING_INDEX,'(0)')                           # insert (0) if not present

        
        # create tag & allergens entries, populate them if they exist
        if we_have_tags:
            recipe_info['description'] = match.group(5).strip()
            stars = match.group(6).strip()
            if stars == '':
                stars = 0
            recipe_info['user_rating'] = int(stars)
            recipe_info['allergens'] = [ a.strip() for a in match.group(7).strip().rstrip(",").split(',') ]    # create list of strings
            recipe_info['tags'] = [ a.strip() for a in match.group(8).strip().rstrip(",").split(',') ]                

        # TODO remove after schema redisgn
        if recipe_info['allergens'][0] == "":
            recipe_info['allergens'] = [ 'none_listed' ]
        if recipe_info['tags'][0] == "":
            recipe_info['tags'] = [ 'none_listed' ]        

        
        print(f"NAME: {match.group(1).strip()}")
        print(f"SERVINGS: ({match.group(2).strip()})")
        print(f"INGREDIENTS:\n")
        pprint(i_list)
        print(f"YIELD: {match.group(4).strip()}")
        print(f"ALLERGENS: {' '.join(recipe_info['allergens'])}")
        print(f"TAGS: {' '.join(recipe_info['tags'])}")
        
        recipe_info['ingredients'] = i_list
        
    else:
        msg = f"BAD TEMPLATE IN {dbg_file_name}\n{recipe_text}"
        print(f"{msg} \n< - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = < < !!")        
        # raise exception here
        log_exception("\n** BAD TEMPLATE **\n", f"\n{recipe_text}\n")
    
    return recipe_info

def get_recipe_file_contents_from_asset_server(recipe_text_filename):
    recipe_text = 'FILE ACCESS ERROR: NO FILE or NO DATA IN FILE'
    
    print("----- get_recipe_ingredients_and_yield -------------------------------------------------")
    base_url = 'http://192.168.1.13:8000/static/recipe/'
    url = f"{base_url}{recipe_text_filename}"
    print(url)

    # IN  http://192.168.1.13:8000/static/recipe/20190228_163410_monkfish and red pepper skewers.txt
    # url = url.replace(" ", "%20")          # WORKS 
    # OUT http://192.168.1.13:8000/static/recipe/20190228_163410_monkfish%20and%20red%20pepper%20skewers.txt

    # get recipe text from assest server
    url = urllib.parse.quote(url, safe='/:')  # WORKS - likely more robust
    print(url)
    
    local_file_name = f"./scratch/{recipe_text_filename}"    
    print(local_file_name)

    try:
        ret_val = urllib.request.urlretrieve(url, local_file_name)    
        #pprint(ret_val)
    
        file_info  = Path(local_file_name)
        
        if file_info.is_file():
            print(f"File exists: {file_info}")
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
        print(f"RETRIEVED URL: finally segment")
        
    return recipe_text



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# load a text file from asset server
#                  - convert into partial recipe dictionary
#                  - ingredients, yield & servings
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_recipe_ingredients_and_yields_from_file(recipe_text_filename, recipe_name):
    recipe_without_tags = {}
    recipe_info = {}
    recipies_and_subcomponents = []
        
    orig_recipe_text = get_recipe_file_contents_from_asset_server(recipe_text_filename)
    print("------------------------------------------------------------ ORIGINAL --------")
    print("------------------------------------------------------------------------------")
    # this text may have multiple components, only one of which might have tags!
    print(orig_recipe_text)
    print("#* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * <-==S")    
    
    # create list of recipes - these have optionally listed fields - 'tags:', 'allergens:', 'notes:', 'description:', 'stars:' 
    for m in re.finditer( r'(^-+- for the (.*?) \(.*?Total \(.*?\))', orig_recipe_text, re.MULTILINE | re.DOTALL ):    
        recipe_without_tags[m.group(2)] = m.group(1)
        #                    name         whole component / recipe

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # add optionally listed tags: & allergens: fields to recipes found
    # go through recipe line by aline and pull out tags & allergens
    recipe_title = ''
    for line in iter(orig_recipe_text.splitlines()):
        print(f"L: {line}")
        # check for start of recipe
        m = re.match( r'(^-+- for the (.*?) \()', line)
        if m:
            recipe_title = m.group(2)
            print(f"RECORDING R:{recipe_title} <")
            continue
        
        # ADD processing for:
        # notes: // multiline - later
        # description:
        # stars:
        # allergens: dairy, eggs, peanuts, nuts, seeds_lupin, seeds_sesame, seeds_mustard, fish, molluscs, shellfish, alcohol, celery, gluten, soya, sulphur_dioxide
        # tags: vegan, veggie, cbs, chicken, pork, beef, seafood, shellfish, gluten_free, ns_pregnant, 
        # type: amuse, side, starter, fish, lightcourse, main, crepe, dessert, p4, cheese, comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot
        
        m = re.match( r'((^tags:)|(^allergens:)|(^description:)|(^stars:))', line)
        if m:
            recipe_without_tags[recipe_title] += f"\n{line}"
            print(f"APPENDED R:{recipe_title} < {line}")
        
    print("#* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * <-==E")
    
    pprint(recipe_without_tags)    
    
    # for key in dict.iterkeys(): ...
    # for value in dict.itervalues(): ...
    # for key, value in dict.iteritems(): ...
    #
    # recipe_without_tags now has tags!
    for title, recipe_text in recipe_without_tags.items():
        print(recipe_text)
        
        # create a dictionary for each recipe / subcoponent        
        recipe_info = process_single_recipe_text_into_dictionary(recipe_text, recipe_text_filename)
        
        # collect components together and return a list of recipes
        recipies_and_subcomponents.append(recipe_info)
    
    print("#* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * ^* * * <-==EE")

    
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
#{'ingredients': [[1, '250g', '(0)', 'cauliflower'],    # sublist
#                 [1, '125g', '(0)', 'grapes'],
#                 [1, '200g', '(4)', 'tangerines'],
#                 [1, '55g', '(0)', 'dates'],
#   atomic >-------1, '8g', '(0)', 'coriander'],
#                 [1, '8g', '(0)', 'mint'],
#                 [1, '4g', '(0)', 'chillies'],
#   sub_comp >-----0, '45g', '(0)', 'pear and vanilla reduction lite'],
#                 [1, '2g', '(0)', 'salt'],
#                 [1, '2g', '(0)', 'black pepper'],
#                 [1, '30g', '(0)', 'flaked almonds']],
#  'ri_name': 'cauliflower california',
#  'atomic' : 0
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# scans through the list of ingredients looking for subcompnents
# marks with atomic (index 0) with a 0 to indicate a subcomponent
# then recurive calls on that subcompnent to process its ingredients
def mark_subcomponents(recipies_and_subcomponents, recipe_dict, search_ingredient):

    recipe_dict['atomic'] = 0    
    print(f"\tFOUND: {recipe_dict['ri_name']} <")
    
    # iterate through its ingredients and see if there is an entry for
    # that ingredient in the headline recipe ingredients list
    # if so it's a subcoponent, mark it and search it too                   *
    
    for i2, ingredient in enumerate(recipe_dict['ingredients']):
        print(f"\t\ti2: {ingredient} <")

        recipe_is_a_subcomponent = ingredient_in_recipe_list(ingredient, recipies_and_subcomponents)

        if recipe_is_a_subcomponent:        # found a subcomponent
            print(f"\t\t\tSUB MARKED: {recipe_is_a_subcomponent['ri_name']} <")

            # mark ATOMIC 0 - false            
            recipe_dict['ingredients'][i2][ATOMIC_INDEX] = 0
            
            # check it's ingredients for sub components            
            mark_subcomponents(recipies_and_subcomponents, recipe_is_a_subcomponent, ingredient)
            print(f"\t\t\tend of SC --< {recipe_is_a_subcomponent['ri_name']}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def mark_ingredients_as_subcomponents_or_leave_as_atomic(recipies_and_subcomponents, headline_recipe_name):
    
    print("== ENTER: mark_ingredients_as_subcomponents_or_leave_as_atomic -      -      -      -      -      -     |")
    pprint(recipies_and_subcomponents)
    
    # find headline (recipe_name) recipe in list
    for i1, rcp in enumerate(recipies_and_subcomponents):                
        print(f"r_&_sc: {rcp['ri_name']} <")
        
        # look for headline recipe and start there
        if rcp['ri_name'] == headline_recipe_name:          # found headline recipe
            mark_subcomponents(recipies_and_subcomponents, recipies_and_subcomponents[i1], headline_recipe_name)
                    
    print("== EXIT: mark_ingredients_as_subcomponents_or_leave_as_atomic -      -      -      -      -      -      |")
    # if so call this function again passing in the subcomponent as the head



def is_recipe_in_nutrion_database(ri_name):
    return None

def merge_nutrient_information_into_each_dictionary(components, recipe_name, sql_row=''):
    
    db_id = int(sql_row['ri_id']) * 100
        
    for i, r in enumerate(components):
        db_id += 1
        #print(f"merging:{r['ri_name']}")
        #pprint(sql_row)
        
        nutri_dict = is_recipe_in_nutrion_database(r['ri_name'])
                
        # merge data from relevant source
        if nutri_dict:
            components[i] = {**r, **nutri_dict}            
        
        elif r['ri_name'] == sql_row['ri_name']:            
            components[i] = {**r, **sql_row}
            
        else:
            print(f">{r['ri_name']}< NOT PRESENT IN Nutrient Database * * *")
        
        components[i]['ri_id'] = db_id
        #pprint(components[i])
        #print(f"merged:{r['ri_name']} ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# creates recipe dictionaries based on the csv column headers
# and ingredients in the text files
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_list_of_recipes_and_components_from_recipe_id(sql_row):
        
    recipe_text_filename = sql_row['text_file']
    recipe_name = sql_row['ri_name']
    
    components = get_recipe_ingredients_and_yields_from_file(recipe_text_filename, recipe_name)

    print(f"LIST:{type(components)} - - - - - - - - - - - - - - B E F O R E <*|*>")
    
    for r in components:
        print("r in components - - - - - - < S ")
        pprint(r)
        print("r in components - - - - - - < E ")

    print(f" - - 'ri_name's - - ")
    
    print(f"RECURSING = = = = = = = = = = = = - - - - - - - - - - - - - - <S")
    mark_ingredients_as_subcomponents_or_leave_as_atomic(components, recipe_name)
    print(f"RECURSING = = = = = = = = = = = = - - - - - - - - - - - - - - <E")
    
    
    print(f"LIST:{type(components)} - - - - - - - - - - - - - - A F T E R <*|*>")
    
    for r in components:
        print("r in components - - - - - - < S ")
        pprint(r)
        print("r in components - - - - - - < E ")

    print(f" - - 'ri_name's - - ")

    print(f"MERGING = = = = = = = = = = = = - - - - - - - - - - - - - - <S {len(components)}")
    merge_nutrient_information_into_each_dictionary(components, recipe_name, sql_row)
    print(f"MERGING = = = = = = = = = = = = - - - - - - - - - - - - - - <E")
    
    print(f"LIST:{type(components)} - - - - - - - - - - - - - - A F T E R <*|*>")
    
    for r in components:
        print("r in components - - - - - - < S ")
        pprint(r)
        print("r in components - - - - - - < E ")

    print(f" - - 'ri_name's - - ")


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
    
    
                

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def explode_ingredients_in_recipe(recipies_and_subcomponents, headline_recipe_name):
    
    print("== E X P L O D I N G:  explode_ingredients_in_recipe      -      -      -      -      -      -     |S - - - - - -")
    # find headline (recipe_name) recipe in list
    for i, rcp in enumerate(recipies_and_subcomponents):
        
        # look for headline recipe and start there
        if rcp['ri_name'] == headline_recipe_name:          # found headline recipe
            #new_ingredients = copy.deepcopy(recipies_and_subcomponents[i]['ingredients'])
            #pprint(new_ingredients)
            new_ingredients = {}
            print("== EXPL HEADLINE < < S")
            pprint(recipies_and_subcomponents[i])
            print("== EXPL HEADLINE < < E")
            
            add_subcomponents_ingredients(recipies_and_subcomponents, recipies_and_subcomponents[i], new_ingredients)
            print("== E X P L O D I N G:  ------------new_list------------<S")
            pprint(new_ingredients)
            print("== E X P L O D I N G:  ------------new_list------------<E")
            
            #pprint(new_ingredients.first())
            
            # construct ingredients list: i_dict = { 'ingredients' : [] }
            i_list = []            
            
            for build_ingredients, qty in new_ingredients.items():
                i_list.append([1, f"{round(qty,2)}g", '(0)', build_ingredients])
            
            #pprint(i_list)
            
            recipies_and_subcomponents[i]['ingredients'] = i_list
            #print(recipies_and_subcomponents) #['ingredients'] = i_list
            print(f"i: {i}")
            
            print("== EXPL HEADLINE EXPLODED < < S")
            pprint(recipies_and_subcomponents[i])
            print("== EXPL HEADLINE EXPLODED < < E")            
                    
    print("== E X P L O D I N G:  explode_ingredients_in_recipe      -      -      -      -      -      -     |E")


def create_exploded_recipe(sql_row):
    recipe_text_filename = sql_row['text_file']
    recipe_name = sql_row['ri_name']
        
    print(f"= E  X  P  L  O  D  E:{recipe_name} - - - - - - - - - - - - - - S")

    components = get_recipe_ingredients_and_yields_from_file(recipe_text_filename, recipe_name)

    mark_ingredients_as_subcomponents_or_leave_as_atomic(components, recipe_name)
    
    explode_ingredients_in_recipe(components, recipe_name)

    merge_nutrient_information_into_each_dictionary(components, recipe_name, sql_row)

    print(f"= E  X  P  L  O  D  E:{recipe_name} - - - - - - - - - - - - - - E")

    # this should return top level component only! Rest is polution.
    return components


def get_nutirents_for_redipe_id(db, ri_id):

    fields = ['ri_id','ri_name','n_En','n_Fa','n_Fs','n_Su','n_Sa','serving_size']
    qry_string = ', '.join(fields)

    db_lines = db.execute(f"SELECT {qry_string} FROM exploded WHERE ri_id={ri_id};").fetchall()
    
    # dont need this for single ID since all info on one query line
    for line in db_lines:
        rcp = {}        
        for index, content in enumerate(line):
            print( f"\nQRY Line{line} {type(line)}\nC:{content} - {type(content)}<" )            
            type_string = str(type(content))

            if type_string == "<class 'decimal.Decimal'>":                
                rcp[fields[index]] = round(float(content),2)

            else:
                rcp[fields[index]] = content

        nutrients = rcp

    return nutrients

    
if __name__ == '__main__':
    # print("-----  get CSV ------------------------------------S")
    # fetch_file = 'http://192.168.1.13:8000/static/sql_recipe_data.csv'
    # get_csv_from_server_as_disctionary(fetch_file)
    # print("-----  get CSV ------------------------------------E")

    recipe_text = '20190103_170558_chicken beetroot w broccoli and greens.txt'
    #recipe_text = '20190109_143622_crabcakes.txt'
    #urllib.request = 'http://192.168.1.13:8000/static/recipe/20190109_143622_crabcakes.txt'
    get_recipe_ingredients_and_yields_from_file_test(recipe_text,'chicken beetroot w broccoli and greens')
