#! /usr/bin/env python

# pre processing recipe diary to create structure data for asset pipeline
# enables
# a refresh the asset server with any new data, and a DB rebuild based on relevant adapter

from pathlib import Path
import shutil
from shutil import copy2
from pprint import pprint
import re
import sys

# RTF conversion to text
from striprtf.striprtf import rtf_to_text

from helpers_db import nix_time_ms

from food_sets import get_allergens_for, get_containsTAGS_for, parse_igdt_lines_into_igdt_list, errors, get_exploded_ingredients_as_list_from_list, scan_for_error_items
from food_sets import atomic_LUT # debug - TODO REMOVE
from food_scrape import MISSING_INGREDIENTS_FILE_JSON_PY
import json
from collections import Counter # to dump debug

FILE_LOC = 0
TMP_PATH = 1
NEW_FILE_PATH = 2
ROOT_DATE = 3
TMP_PATH_INCOMPLETE = 4
#
def get_nutridoc_list_rtf():
    base_dir = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components')

    #y971_NUTRITEST_recipes_20191123-06.rtf
    #y(\d{3})_NUTRITEST_recipes_(.*?).rtf
    # $1 'course no.'
    # $2 daterange
    from_to = []

    print('\nNutridocs Found:')
    for file_loc in base_dir.rglob('*_NUTRITEST_recipes_*.rtf'):
        if opt_dict['verbose_mode']:
            print(file_loc)
        else:
            print(re.search(r'(y\d{3})_', file_loc.stem).group(1), end=' ')
        # print(f"{file_loc.parent} -- {file_loc.name} -- {file_loc.stem}")

        new_file=f"{file_loc.stem}.txt"
        tmp_path = file_loc.parent.joinpath(file_loc.stem).joinpath('_i_w_r_auto_tmp')
        tmp_path_incomplete = file_loc.parent.joinpath(file_loc.stem).joinpath('_i_w_r_auto_tot0g')
        new_file_path = tmp_path.joinpath(new_file)
        root_date = re.search(r'(\d{8})-', file_loc.stem).group(1)
        # order SENSITIVE - see above consts - TOD chacge to dict?
        from_to.append([file_loc, tmp_path, new_file_path, root_date, tmp_path_incomplete])
        
    return sorted(from_to)

def version_temp_assets_create_new_tmp_dirs(tmp_path, tmp_path_incomplete):
    tmp_path = Path(tmp_path)
    tmp_path_incomplete = Path(tmp_path_incomplete)
    
    #timestamp & relable last temp directories - avoid polution
    nix_time = nix_time_ms()
    if tmp_path.exists():
        tmp_path.rename(tmp_path.parent.joinpath(f"_{nix_time}{tmp_path.stem}"))
    if tmp_path_incomplete.exists():
        tmp_path_incomplete.rename(tmp_path_incomplete.parent.joinpath(f"_{nix_time}{tmp_path_incomplete.stem}"))
    tmp_path.mkdir(parents=True, exist_ok=True)
    tmp_path_incomplete.mkdir(parents=True, exist_ok=True)
    
    return (tmp_path.exists() and tmp_path_incomplete.exists())


def get_text_content_of_file(rtf_filepath):

    with open(rtf_filepath,'r') as f:
        rtf = f.read()

    return rtf_to_text(rtf)             # convert to text and return


def get_costing_section_from_main_doc(text):
    match = re.search(r'_course_cost_start_(.*?)_course_cost_end_', text, re.MULTILINE | re.DOTALL ) # the recipes
    #
    recipe_text = 'costing_section_not_found'

    if match:
        recipe_text = match.group(1)

    return recipe_text


def get_images_from_lead_image(image):
    return 'implement_image_search.jpg'



recipe_count = 0
def get_zero_pad_6dig_count():
    global recipe_count
    recipe_count+=1
    secs = recipe_count % 60
    mins = int(recipe_count / 60 % 60)
    hrs = int(recipe_count / 3600 % 24)
    return f"{hrs:02}{mins:02}{secs:02}"

TEMPLATE = Path('./templates_recipe/date_time_recipe_name_template.txt')
RECIPES_PROCESSED = 0
MISSING_IMAGES = 1
INGREDIENTS_TOTAL_0G = 2
RECIPES_WITH_NON_ZERO_TOTALS = 3
AVAILABLE_RECIPE_IMAGES = 4
MISSING_SUB_INGREDIENTS_LIST = 5
def produce_recipe_txts_from_costing_section(costing_section, fileset, available_recipe_images, opt_dict={}):
    recipes_processed = []
    missing_images = []
    recipes_w_total_0g = []
    recipes_with_non_zero_totals = []
    missing_ingredients_list = []

    # print('> - - - - - S \ ')
    # pprint(fileset)
    # #tmp_path = file_loc.parent.joinpath(file_loc.stem).joinpath('_i_w_r_auto_tmp')
    # print(fileset[TMP_PATH_INCOMPLETE])
    # print('> - - - - - E / ')

    target_file_name = ''
    root_date = fileset[ROOT_DATE]

    # remove diary entries
    DIARY_PATTERN  = re.compile(r"------------------ for the \d\d\d\d calories (.*?) \((.*?)\)(.*?)$(.*?)Total\s*\((.*?)\).*?$", re.M | re.S)
    costing_section = DIARY_PATTERN.sub('', costing_section)    # remove diary entries
    #print(costing_section)

    # create regex
    PATTERN  = re.compile(r"------------------ for the (.*?) \((.*?)\)(.*?)$(.*?)Total\s*\((.*?)\)(.*?)^description:(.*?)^notes:(.*?)^stars:(.*?)^type:(.*?)^lead_image:(.*?)username:(.*?)$", re.M | re.S)

    # scan text for recipes
    for match in PATTERN.finditer(costing_section):
        name, serving_info, notes_after_serve, ingredients, tot_yield, method, description, notes, stars, type_tag, lead_image, username = match.groups()
        original_text = match.group(0)        
        if 'calories' in name: continue         # diary entry
        if 'recipe_name' in name: continue      # blank template

        target_path = fileset[TMP_PATH]         # reset target path in case changed to TMP_PATH_INCOMPLETE below

        recipes_processed.append(name)          # a dict would make search faster no? but for these numbers meh

        lead_image = str(lead_image).strip()    # convert None to ''

        # maintain a list if images without templates
        lead_image_from_title = None
        try:
            lead_image_from_title = available_recipe_images.pop(name)   # remove from available images
        except KeyError:
            # ONLY APPEND IF lead_image is blank - may not match title - OR leave in as reminder
            if lead_image == '' or lead_image == '_li_':
                missing_images.append(name)

        if (lead_image == '' or lead_image == '_li_') and lead_image_from_title != None:

            replacement = f"lead_image: {lead_image_from_title} "

            if lead_image == '_li_':
                original_text = re.sub('lead_image: _li_', replacement, original_text, re.M | re.S)
            else:
                original_text = re.sub('lead_image:', replacement, original_text, re.M | re.S)
            
            lead_image = lead_image_from_title          # found image that matches title so use it!
            
            #print(f"\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n{lead_image}\n{replacement}\n{original_text}\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|")


        username = str(username).strip()

        target_file_name = lead_image.lower().replace('.jpg', '.txt')

        # if no lead_image to base filename on - use root_date
        if target_file_name == '':
            target_file_name = f"{root_date}_{get_zero_pad_6dig_count()}_{name}.txt"

        print(f"allergens for: {name} <")
        
        exploded_list_of_ingredients = get_exploded_ingredients_as_list_from_list(parse_igdt_lines_into_igdt_list(ingredients))
        missing_ingredients = scan_for_error_items(exploded_list_of_ingredients)
        if missing_ingredients:
            missing_ingredients_list.append((name, missing_ingredients))
        
        insertion_dict = {  '__recipe_name__' : name,
                    '__serving_info__' : serving_info,
                    '__ingredients__' : ingredients.strip(),
                    '__total_yield__' : tot_yield,
                    '__method__' : method.strip().replace("'","''"),    # SQL escape for ' is '' 'x2 - - \
                    '__description__' : description.strip(),                                              #
                    '__notes__' : (str(notes).strip() + ('\n' + str(notes_after_serve)).strip()).replace("'","''"),  # if notes_after_serve existd put it on the next line!
                    '__stars__' : str(stars).strip(),
                    '__allergens__' : ', '.join(get_allergens_for(parse_igdt_lines_into_igdt_list(ingredients))),
                    '__tags__' : ', '.join(get_containsTAGS_for(parse_igdt_lines_into_igdt_list(ingredients))),
                    '__type__' : type_tag.strip(),
                    '__images__' : get_images_from_lead_image(lead_image),
                    '__lead_image__' : lead_image,
                    '__username__' : username,
                    '__exploded_igdt_list__' : ', '.join(exploded_list_of_ingredients) }
        
        rcp = ''
        with TEMPLATE.open('r') as f:
            rcp = f.read()

        for marker in insertion_dict:
            #print(f"INSERTING: {marker} - {type(insertion_dict[marker])} - {insertion_dict[marker]}")
            rcp = rcp.replace(marker, insertion_dict[marker])

        if 'Total (0g)' in rcp:
            recipes_w_total_0g.append(name)
            target_path = fileset[TMP_PATH_INCOMPLETE]
        else:
            recipes_with_non_zero_totals.append(name)

        place_txt_file = target_path.joinpath(target_file_name)
        place_img_file = target_path.joinpath(lead_image)
        source_img_file = target_path.parent.joinpath(lead_image)


        # create component templates for processing into recipes
        # & DB of some description - ORM later in pipeline
        if opt_dict['generate_output_in_tmp_folders']:
            # write the recipe to folder
            with place_txt_file.open('w') as f:
                f.write(rcp)

        #if image exist copy it over
        if lead_image != '' and lead_image != '_li_':
            if opt_dict['generate_output_in_tmp_folders']:
                copy2(source_img_file, place_img_file)

        if opt_dict['verbose_mode']:
            # show actions if live (IE NOT option -ct)            
            print('> - - - Proposed file generation: NOT LIVE')
            print(place_txt_file)
            print(source_img_file)
            print(place_img_file)
            print(rcp)
            print('> - - -')

    return [recipes_processed, missing_images, recipes_w_total_0g, recipes_with_non_zero_totals, available_recipe_images, missing_ingredients_list]


NUTRIDOC_LIST = [
                # 2019 * * *
                #'nutridoc_no' # ~#recipes/#missing_images - recipe types list rough idea of content
                # #'y950',       # ~15   - xmas type recipes - A LOT of product - leave for now.
                # 'y951',       #* DONE 0101-18 70/10 - lots of toast & lo-cal                       MISSING IMAGES: 10 ['wmgt', 'buttered wmgt', 'mixed vegetable risotto', 'ham snack', 'coffee', 'milled linseed ingredients', 'poached egg on tomato mgt', 'poached egg on tomato mmgt', 'left over fish broth', 'apple mirin']
                # 'y952',       #* DONE 0119-31 17/10 - breads & broths                              MISSING IMAGES: 3 ['aubergine and leek w lemon grass soup', 'bun bo huey stock cube', 'pork and blue cheese kebab']  TODO sourdough ring loaf, sourdough boule, confit duck, a few images need tagging
                # 'y953',       #* DONE 0201-14 0/0   - NO_RECIPES_FOR_DTK
                # 'y954',       #* DONE 0214-28 48/13 - stews, tortilla, salads, roasts, snacks      MISSING IMAGES: 10 ['dashi stock', 'lemon dashi dip', 'mixed low cal snack lunch 20190214', 'chicken stock', 'aubergine and chicken liver pate', 'compare aubergine with brussels pate', 'cup of tea', 'home made chicken gravy', 'pea and spring onion gravy', 'mums coconut custard']
                # 'y955',       #* DONE 0301-14 33/15 - couscous madness DOTT! some good lo cal rcps  MISSING IMAGES: 4 ['sweet melon dressing', 'tomato red onion and lettuce w sweet melon', 'beetroot and tomato salad', 'mixed veg sunflower seed couscous']
                # 'y956',       #  DONE 0315-28 ~48/10 - brisket, burgers, broths, croquettes, frying absorbtion experiments
                # 'y957',       #  DONE 0329-11  32   - super healthy, meatballs, pastas, bread, beetroot burger
                # 'y958',       #  DONE 0412-25 34/6  - sushi, snack, grains, tortilla, fish
                # 'y959',       #  DONE 0429-09 16/22 - IPtodo - fish, comfort, snacks, seasoning, desert
                # 'y960',       #  DONE 0510-23 28/5  - pies, salads, grains, seafood, dessert
                # 'y961',       #  DONE 0524-06 42/15 - brisket, salads, soups, sushi, breads x3, 15 extra LOW hanging fruit!
                # 'y962',       #  DONE 0607-20 19/9  - sushi, french sticks, brisket, broths
                # 'y963',       #  DONE 0621-04 19/3  - prawns, burgers, veggie burgers, couscous
                # 'y964',       #  DONE         43/24    - tortilla, fish, roast lamb, cheerry tart,  also alot of 3D CAD linux bike, protoyping & scenery
                # 'y965',       #  DONE         39/19  - burgers, pasta, fish, lamb, salads
                # 'y966',       #  DONE         61/19 - fish, salads, carbless, veggie, sandwiches,
                # 'y967',       #  DONE         29/6 - roast pork, fejoida, fish, veggie carbless - TODO meat free burger
                # 'y968',       #  DONE 0830-12 72/17 - lo-cal, pastry, creme pat, roasts, salads
                # 'y969',       #  DONE         23/27 - 2 month stretch / messy split diary from rcp
                # 'y970',       #  DONE 1109-22 24/6 - bakes, veggie  mousaka, cauliflower cheese, meatballs, fish
                # 'y971',       #  DONE 1123-06 24/2 - broths, fish, bakewell tart & fudge, veg bake
                # 'y972',       #  DONE 1207-20 19/4 -
                # 'y973',       #  DONE 1221-03 28/11 - xmas, beef, brioche, broths, fennel pate, french stick - TODO: beef forerib, lamb chops, oils
                #               #  * * * 2020 * * *
                # 'y974',       #  DONE 0104-17 - 18/1  crispy prawns, stir fry, arancini, moussakas, roast potatoes & salads
                # 'y975',       #  DONE 0118-31 - 19/14: images processed - templates in place - REQ: fill in ~50% complete  MISSING IMAGES:1 ['bst']
                # 'y976',       #  SUSHI TODO DONE 0201-14 42/45- standard sushi templates bringing in
                # 'y977',       #  SUSHI TODO DONE 0215-28 - 18/37: images processed - templates in place - REQ: fill in ~ 4/54 complete - sushi, moussaka, tag n cheese, salads, comfort MISSING IMAGES: 1 ['red pepper & tomatoes']
                # 'y978',       #* DONE 0229-13 54/5 - sushi, croquettes, wraps, fish, veg, stirfry  MISSING IMAGES: 5 ['mon8pm 200302', 'late snack 20200304', 'mpy', 'snack 20200311', 'sushi & lamb chops']
                # 'y979',       #  DONE 0314-27 - 34/4: broths, dumpling dough, cabbage, figs, sticky pork
                # 
                # #_doc_#         status dateRange - RCP/incomplete : type of content
                # 
                # 'y420',       #       0328-10 - 0/21: images processed - templates in place - REQ: fill in
                # 'y421',       #       0411-24 - 4/52: images processed - templates in place - REQ: fill in
                # 'y422',       #* DONE 0425-08 - 46/3: salads, broths, comfort, pizza               MISSING IMAGES: 4 ['vc water', 'smoked mussels inc oil', 'buttered crumpet', 'pear pickle']
                # 'y423',       #* DONE 0509-22 - 58/9: salads, steak chops kofte, tarts, cake       MISSING IMAGES: 3 ['red wine & blue cheese sauce', 'salmon fishsticks', 'coconutapple']
                # 'y424',       #* DONE 0523-05 - 48/8: chermoula, guinea fowl chinese leaf wraps    MISSING IMAGES: 2 ['sourdough bap', 'hereford pate']
                # 'y425',       #* DONE 0606-19 - 51/1: salads, steak chops kofte, tarts, breads     MISSING IMAGES: 6 ['waterc', 'halfwaterc', 'haggis yorkie', 'indian dips', 'roast chicken dinner', 'drink snack 20200619']
                # 'y426',       #  DONE 0620-04 - 45/21: << TODO croquettes, salads, flatbread,      MISSING IMAGES: 3 ['packed lunch 20200621', 'tom & couscous em broth', 'em test broth']
                # 'y427',       #       0705-18 - 29/2:  flat bread, baguettes, rhubarb tart
                # 'y428',       #  DONE 0719-01 - 15/29:   < mustard chicken sequence, cardamom flatbreads
                #               #       0801-14 - no nutridoc!?
                # 'y429',       #       0815-28 - 50/4:
                # 'y430',       #  DONE 0829-11 - 50/26: salads roast burgers snacks bakes . . . TODO loads of good stuff!
                # 'y431',       #       0912-25 - 4 /2:
                # 'y432',       #  DONE 0929-09 - 15/42: loads of material!
                 'y433',       #       1010-23 - 12/2:
                # 'y434',       #       1024-06 - 00/0:
                # 'y435',       #       1107-20 -
                # 'y436',       #       1121-04 -
                # 'y437',       #       1205-18 - 00/28
                # 'y438',       #       1024-06 - 00/0:
                # 'y439',       #       0116-0212 - 00/0:
                # 'y440',       #       0601-15
                # 'y441',       #  DONE 0313-26 - 53/02: pizza, wontan, kofte, maki, salads          MISSING IMAGES: 6 ['basic broth','feijoada & maki broth','steamed veg broth','steamed veg broth w potato','hot chocolate','macchiato']
                # 'y442',       #  DONE 0327-09 - 62/00: salads, sanwiches, keto, fermented          MISSING IMAGES: 7 ['liver & onions', 'feijoada broth', 'post bike ham salad ', 'turkey & squid balls w chinese leaf ', 'brined red cabbage', 'garlic butter prawns', '7.5pc brine']
                # 'y443',       #  DONE 0410-23 -
                # 'y444',       #       0424-07 - 60/12: GOOD lo-cal set !! inc: prawn & melon salad w soft boiled eggs // prawn & bamboo broth
                # 'y445',       #       0508-21 - 53/05: broths, bento, cassoulet, flans
                # 'y446',
                # 'y447',
                # 'y448',       #  DONE 0703-23 - 41/30
                # 'y449',
                # 'y450',
                # 'y451',
                # 'y452',
                # 'y453',
                #'y454',
                #'y455',

    
# * next to done means superfluous image files removed
]


# DOC_NAME                                        RECIPES  COMPLETE  TOTAL 0g  TMP FROM IMG  MISSING IMG
# y420_NUTRITEST_recipes_20200328-10.rtf           25       0         25          1             0      
# y421_NUTRITEST_recipes_20200411-24.rtf           52       2         50          3             0      
# y422_NUTRITEST_recipes_20200425-08.rtf           45       40        5           3             4      
# y423_NUTRITEST_recipes_20200509-22.rtf           58       49        9           0             3      
# y424_NUTRITEST_recipes_20200523-05.rtf           48       37        11          3             2      
# y425_NUTRITEST_recipes_20200606-19.rtf           51       46        5           2             6      
# y426_NUTRITEST_recipes_20200620-04.rtf           65       46        19          4             3      
# y427_NUTRITEST_recipes_20200705-18.rtf           32       30        2           3             29     
# y428_NUTRITEST_recipes_20200719-31.rtf           44       15        29          0             3      
# y429_NUTRITEST_recipes_20200815-28.rtf           54       50        4           1             47     
# y430_NUTRITEST_recipes_20200829-11.rtf           76       50        26          0             3      
# y431_NUTRITEST_recipes_20200912-25.rtf           6        4         2           0             6      
# y432_NUTRITEST_recipes_20200926-09.rtf           57       15        42          1             3      
# y433_NUTRITEST_recipes_20201010-23.rtf           50       12        38          0             1      
# y434_NUTRITEST_recipes_20201024-06.rtf           37       36        1           1             36     
# y435_NUTRITEST_recipes_20201107-20.rtf           0        0         0           0             0      
# y436_NUTRITEST_recipes_20201121-04.rtf           0        0         0           0             0      
# y437_NUTRITEST_recipes_20201205-18.rtf           28       0         28          0             0      
# y438_NUTRITEST_recipes_20201219-0115.rtf         2        2         0           0             2      
# y439_NUTRITEST_recipes_20210116-0212.rtf         23       0         23          0             0      
# y440_NUTRITEST_recipes_20210213-0312.rtf         42       6         36          0             2      
# y441_NUTRITEST_recipes_20210313-26.rtf           53       51        2           2             6      
# y442_NUTRITEST_recipes_20210327-09.rtf           62       62        0           10            7      
# y443_NUTRITEST_recipes_20210410-23.rtf           63       43        20          1             5      
# y444_NUTRITEST_recipes_20210424-07.rtf           60       25        35          1             12     
# y445_NUTRITEST_recipes_20210508-21.rtf           52       8         44          1             5      
# y446_NUTRITEST_recipes_20210522-0618.rtf         77       20        57          0             3
# DOC_NAME                                        RECIPES  COMPLETE  TOTAL 0g  TMP FROM IMG  MISSING IMG
# y447_NUTRITEST_recipes_20210619-02.rtf           42       40        2           1             41     
# y448_NUTRITEST_recipes_20210703-23.rtf           73       43        30          0             1      
# y449_NUTRITEST_recipes_20210724-0820.rtf         77       53        24          0             7      
# y450_NUTRITEST_recipes_20210821-1015.rtf         12       10        2           0             12     
# y451_NUTRITEST_recipes_20211016-1205.rtf         9        8         1           0             9      
# y452_NUTRITEST_recipes_20211206-0108_xmas.rtf    6        1         5           0             6      
# y453_NUTRITEST_recipes_20220219-0930.rtf         99       67        32          8             11     
# y454_NUTRITEST_recipes_20221001-31.rtf           40       38        2           17            1
#
# y951_NUTRITEST_recipes_20190101-18.rtf           79       71        8           1             10     
# y952_NUTRITEST_recipes_20190119-31.rtf           17       17        0           3             3
#
# y954_NUTRITEST_recipes_20190214-28.rtf           48       43        5           14            10     
# y955_NUTRITEST_recipes_20190301-14.rtf           33       33        0           15            4      
# y956_NUTRITEST_recipes_20190315-28.rtf           48       38        10          0             4      
# y957_NUTRITEST_recipes_20190329-11.rtf           32       31        1           1             0      
# y958_NUTRITEST_recipes_20190412-25.rtf           40       33        7           3             1      
# y959_NUTRITEST_recipes_20190426-09.rtf           36       17        19          6             2      
# y960_NUTRITEST_recipes_20190510-23.rtf           34       27        7           1             1      
# y961_NUTRITEST_recipes_20190524-06.rtf           57       41        16          1             1      
# y962_NUTRITEST_recipes_20190607-20.rtf           19       18        1           9             0      
# y963_NUTRITEST_recipes_20190621-04.rtf           19       15        4           0             0      
# y964_NUTRITEST_recipes_20190705-18.rtf           46       46        0           23            0      
# y965_NUTRITEST_recipes_20190719-01.rtf           58       39        19          4             3      
# y966_NUTRITEST_recipes_20190802-15.rtf           80       61        19          3             5      
# y967_NUTRITEST_recipes_20190816-29.rtf           40       32        8           4             2      
# y968_NUTRITEST_recipes_20190830-12.rtf           89       72        17          5             4      
# y969_NUTRITEST_recipes_20190913-1108.rtf         50       23        27          1             1
# DOC_NAME                                        RECIPES  COMPLETE  TOTAL 0g  TMP FROM IMG  MISSING IMG
# y970_NUTRITEST_recipes_20191109-22.rtf           30       29        1           1             0      
# y971_NUTRITEST_recipes_20191123-06.rtf           26       24        2           1             3      
# y972_NUTRITEST_recipes_20191207-20.rtf           23       19        4           1             0      
# y973_NUTRITEST_recipes_20191221-03.rtf           39       28        11          0             5      
# y974_NUTRITEST_recipes_20200104-17.rtf           19       18        1           3             0      
# y975_NUTRITEST_recipes_20200118-31.rtf           33       19        14          5             1      
# y976_NUTRITEST_recipes_20200201-14.rtf           87       42        45          2             3      
# y977_NUTRITEST_recipes_20200215-28.rtf           55       18        37          5             0      
# y978_NUTRITEST_recipes_20200229-13.rtf           54       53        1           43            5      
# y979_NUTRITEST_recipes_20200314-27.rtf           38       34        4           9             4   

empty_recipe = '''
------------------ for the recipe_name (1)
180m		coffee												# notes, comments
													Total (0g)
description:
notes:
stars: 1
type: ferment, lunchbox, hmtakeout, takeout, dough, bread, pasta, sandwich, burger,
pizza, sauce, supplement, beverage, snack, breakfast, brunch, homegrown, salad, soup,
preserve, component, amuse, side, starter, sushi, fish, lightcourse, bao, main, crepe,
dessert, p4, cheese, comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot
lead_image: _li_
username: carter snapdragonpics


'''

empty_lower_template = '''
description:
notes:
stars: 1
type: ferment, lunchbox, hmtakeout, takeout, dough, bread, pasta, sandwich, burger,
pizza, sauce, supplement, beverage, snack, breakfast, brunch, homegrown, salad, soup,
preserve, component, amuse, side, starter, sushi, fish, lightcourse, bao, main, crepe,
dessert, p4, cheese, comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot
lead_image: _li_
username: carter snapdragonpics



-'''

def dump_missing_sub_ingredients_across_all_docs_to_JSON(sub_i_hash):
# {'y433_NUTRITEST_recipes_20201010-23.rtf': [('duck crown & caramelised onions',       < component
#     ^^ nutridoc_name                          [('unknown_component',                  < sub_list
#                                                'duck crown')]),
#     
#                                             ('tangerine dressing',                    < component
#                                              [('ots_i_miss',                          < sub_list
#                                                'balsamic vinegar')]),
#                                             
#                                             ('goats cheese & pecan salad',            < component
#                                              [('ots_i_miss',                          < sub_list
#                                                'balsamic vinegar'),
#                                               ('ots_i_miss', 'goats cheese')])
#                                             ]     ^^ err         ^^ sub_i
    missing_subs = {}

    for nutridoc_name, c_list in sub_i_hash.items():
        m = re.search(r'(y\d\d\d)', nutridoc_name)
        if m:
            nutridoc_no = m.group(1)
        for component, sub_list in c_list:
            for err, sub_i in sub_list:
                if sub_i in missing_subs:
                    missing_subs[sub_i].append(component)
                else:
                    missing_subs[sub_i] = [nutridoc_no, component]
    
    pprint(missing_subs)
    MISSING_INGREDIENTS_FILE_JSON_PY
    missing_to_file = json.dumps([ k for k,i in missing_subs.items()])
    with open(MISSING_INGREDIENTS_FILE_JSON_PY, 'w') as f:
        f.write(missing_to_file)
        
    print(missing_to_file)
    
    return missing_subs
        
    
    



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# start processing, generate above report & and assets fro downstream processing
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
opt_dict = {
    'create_empty_templates_from_image_names': False,
    'verbose_mode':  False,
    'clean_old_files_NO_backup_inspect':  False,
    'clean_old_files_NO_backup_HOT':  False,
    'generate_output_in_tmp_folders':  False,
    'help': False
}

if '-ct' in sys.argv:                           # for recipes that have an image but for which there is no recipe template
    opt_dict['create_empty_templates_from_image_names'] = True

if '-v' in sys.argv:
    opt_dict['verbose_mode'] = True
    
if '-c' in sys.argv:
    opt_dict['clean_old_files_NO_backup_inspect'] = True

if '-clean' in sys.argv:                            # TODO - implement
    opt_dict['clean_old_files_NO_backup_inspect'] = True
    opt_dict['clean_old_files_NO_backup_HOT'] = True

if '-go' in sys.argv:
    opt_dict['generate_output_in_tmp_folders'] = True

if ('-h' in sys.argv) or ('--h' in sys.argv) or ('-help' in sys.argv) or ('--help' in sys.argv):
    opt_dict['help'] = True

# 'nutridoc' : (recipes process, [list missing images])
processed_nutridocs = {}

# Create directories from nutridocd
files_to_process = []
nutridocs_found = get_nutridoc_list_rtf()


print(f"\n\nProcessing: LIVE?:{opt_dict['generate_output_in_tmp_folders']} . . Use opt -go for LIVE run")
for f in nutridocs_found:
    filename = str(f[0].name)
    docID = re.match(r'^(y\d\d\d)', filename).group(1)
    if docID in NUTRIDOC_LIST:
        files_to_process.append(f)
        if opt_dict['verbose_mode']:
            print(filename)
        else:
            print(docID, end=' ')

print('\n')
#sys.exit(0)

# process Nutridocs into text & image pairs initial stage in pipeline
for fileset in files_to_process:
    nutridoc_dir = fileset[TMP_PATH].parent

    # convert file from RTF to txt
    nutridoc_text = get_text_content_of_file(fileset[FILE_LOC])
    #print(nutridoc_text) # save txt here: fileset[NEW_FILE_PATH]

    costing_section = get_costing_section_from_main_doc(nutridoc_text)
    if opt_dict['verbose_mode']: print(costing_section)


    # GET list of available recipe IMAGES format: date_time_recipe.jpg
    #   EG: 20200428_181655_fried chicken coating pancakes.jpg
    available_recipe_images = {}
    for image_file in nutridoc_dir.glob('*.jpg'):
        m = re.match('\d{8}_\d{6}_(.*?)\.jpg', image_file.name)
        if m:
            recipe_name = m.group(1)
            available_recipe_images[recipe_name] = image_file.name
            if opt_dict['verbose_mode']: print(f"Rcp img:{recipe_name} = {available_recipe_images[recipe_name]}")
    
    # # # # # add opt -ili  insert lead image
    #
    # at this point have enough info to load rtf (fileset[FILE_LOC])
    # scan for recipe templates key:recipe_name  image: available_recipe_images[recipe_name]
    # insert image into text / NOT could be brittle if rtf file has any formatting in template like bold due to rtf markdown 
    #
    # # # # #
    
    if opt_dict['generate_output_in_tmp_folders']:
        version_temp_assets_create_new_tmp_dirs(fileset[TMP_PATH], fileset[TMP_PATH_INCOMPLETE])
    
    recipes_and_missing_imgs = produce_recipe_txts_from_costing_section(costing_section, fileset, available_recipe_images, opt_dict)

    if opt_dict['create_empty_templates_from_image_names']:
        for recipe_name, image_file in available_recipe_images.items():
            #print(recipe_name, image_file)
            template_img = empty_recipe.replace('recipe_name', recipe_name)
            template_img = template_img.replace('_li_', image_file)
            print(template_img)


    processed_nutridocs[fileset[FILE_LOC].name] = recipes_and_missing_imgs

    print(f"\nREPORT: = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \ ")
    print(fileset[FILE_LOC].name,
          f"\nGENERATED: {len(recipes_and_missing_imgs[0])} recipes",
          f"\nTEMPLATES FROM IMAGES: {len(available_recipe_images)}",
          f"\nMISSING IMAGES: {len(recipes_and_missing_imgs[MISSING_IMAGES])}\n{recipes_and_missing_imgs[MISSING_IMAGES]}",
          f"\nMISSING SUB INGDTS: {len(recipes_and_missing_imgs[MISSING_SUB_INGREDIENTS_LIST])}\n{recipes_and_missing_imgs[MISSING_SUB_INGREDIENTS_LIST]}")
    print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \n")

# report
missing_images_across_all_docs = {}
missing_sub_ingredients_across_all_docs = {}
print("\n\n\nREPORT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")
#pprint(processed_nutridocs)
print('^^processed_nutridocs^^')
for name, nutri_doc_info in processed_nutridocs.items():
    # all_recipes, miss_img, total_0g, complete_rcp = [],[],[],[]

    print(fileset[FILE_LOC].name, f" -: {len(nutri_doc_info[RECIPES_PROCESSED])} recipes")

    print(f"COMPLETE:       {len(nutri_doc_info[RECIPES_WITH_NON_ZERO_TOTALS])}  < < - - - - - - - - -<")
    if opt_dict['verbose_mode']: print(nutri_doc_info[RECIPES_WITH_NON_ZERO_TOTALS])

    print(f"TOTAL 0g:       {len(nutri_doc_info[INGREDIENTS_TOTAL_0G])}  < < - - - - - - - - -<")
    if opt_dict['verbose_mode']: print(nutri_doc_info[INGREDIENTS_TOTAL_0G])

    print(f"TMPLT FRM IMG:  {len(nutri_doc_info[AVAILABLE_RECIPE_IMAGES])}  < < - - - - - - - - -<")
    if opt_dict['verbose_mode']: print(nutri_doc_info[AVAILABLE_RECIPE_IMAGES])

    print(f"MISSING IMAGES: {len(nutri_doc_info[MISSING_IMAGES])}  < < - - - - - - - - -<")
    if opt_dict['verbose_mode']: print(nutri_doc_info[MISSING_IMAGES])

    print(f"MISSING SUB INGREDIENTS: {len(nutri_doc_info[MISSING_SUB_INGREDIENTS_LIST])}  < < - - - - - - - - -<")
    if opt_dict['verbose_mode']: print(nutri_doc_info[MISSING_SUB_INGREDIENTS_LIST])

    print("\nMissing image recipe names:\n")
    for i in nutri_doc_info[MISSING_IMAGES]:
        print(i)
    # missing_images_across_all_docs[name] = nutri_doc_info[MISSING_IMAGES]
    # missing_sub_ingredients_across_all_docs[name] = nutri_doc_info[MISSING_SUB_INGREDIENTS_LIST]

print("\n\n\nREPORT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")
doc_name = 'y452_NUTRITEST_recipes_20211206-0108_xmas.rtf'
column_headers = ['RECIPES','COMPLETE','TOTAL 0g','TMP FROM IMG','MISSING IMG']
header = 'DOC_NAME'.ljust(len(doc_name)+3) + '  '.join(column_headers)
print(header)
for name, nutri_doc_info in processed_nutridocs.items():
    # stats = dict(zip(column_headers, immage_info_list))
    stats = {
        'RECIPES': nutri_doc_info[RECIPES_PROCESSED],
        'COMPLETE': nutri_doc_info[RECIPES_WITH_NON_ZERO_TOTALS],
        'TOTAL 0g': nutri_doc_info[INGREDIENTS_TOTAL_0G],
        'TMP FROM IMG': nutri_doc_info[AVAILABLE_RECIPE_IMAGES],
        'MISSING IMG': nutri_doc_info[MISSING_IMAGES],
        'MISSING SUB INGREDIENTS': nutri_doc_info[MISSING_SUB_INGREDIENTS_LIST]
    }
    row = name.ljust(len(doc_name))
    for col, data in stats.items():
        row += str(len(data)).center(len(col)+2)

    print(row)
    missing_images_across_all_docs[name] = nutri_doc_info[MISSING_IMAGES]
    missing_sub_ingredients_across_all_docs[name] = nutri_doc_info[MISSING_SUB_INGREDIENTS_LIST]

print("\n\nIf building NUTRIDOC from image set build text templates for each image using './process_nutridocs.py -ct' ")
pprint(NUTRIDOC_LIST)
print('\n> Missing IMAGES across ALL docs - - - - - - - - - - - - - - - < < < < MISSING * * *')
pprint(missing_images_across_all_docs)
print('\n> Missing SUB INGREDIENTS across ALL docs - - - - - - - - - - - - - - - < < < < MISSING * * *')
dump_missing_sub_ingredients_across_all_docs_to_JSON(missing_sub_ingredients_across_all_docs)

nutridocs_found = get_nutridoc_list_rtf()
if opt_dict['clean_old_files_NO_backup_inspect'] == True:
    print("\n\n\n* * REMOVING * * empty folders from _courses_components & _nix_time_i_w_r_auto_tmp/0g backups.\n") 
    yn = input('Continue? y/(n)\n\n')
    if yn.strip().lower() != 'y': sys.exit(0)
    
    for file_set in nutridocs_found:
        base_dir = str(file_set[1].parent)
        #print('\n\n')
        print(f"\n{base_dir}")
        sub_dirs = [f for f in Path(base_dir).glob('*') if f.is_dir()]
        for sub_d in sub_dirs:
            no_of_files = [f for f in Path(sub_d).glob('*')]
            #print(f"\t{len(no_of_files)} - {sub_d}")
            if len(no_of_files) == 0:
                print(f"\tREMOVING {sub_d}\n")
                sub_d.rmdir()
            else:
                #print(f"\tdir: {sub_d}\n")
                if re.search(r'(_\d*_i_w_r_auto_tot0g)', str(sub_d)):
                    print(f"\t** REMOVING ** 0g ({len(no_of_files)} files): {sub_d}")
                    if opt_dict['clean_old_files_NO_backup_HOT']: shutil.rmtree(sub_d)
                    
                if re.search(r'(_\d*_i_w_r_auto_tmp)', str(sub_d)):
                    print(f"\t** REMOVING ** tmp ({len(no_of_files)} files): {sub_d}")
                    if opt_dict['clean_old_files_NO_backup_HOT']: shutil.rmtree(sub_d)
                    
    if opt_dict['clean_old_files_NO_backup_HOT'] == False:
        print("Use: \n\tprocess_nutridocs.py -clean \n\nto HOT DELETE directories & contents.")


help = '''
Options Information
No arguments:            Report status of files selected in NUTRIDOC_LIST

-ct                      Create empty Templates from image names
                         for recipes that have an image but for which there is no recipe template

-v                       Verbose mode 
    
-c                       show what -clean would delete
-clean                   Clean old files NO backup - removes asset backup directory after completion
                         
-go                      Generate Output in tmp folders - for populate_db.py

'''

print("\n\n# # # # # # # # # # # errors['dead_ends_in_this_pass'] # # # # # # # # # # # S")    
pprint(Counter(errors['dead_ends_in_this_pass']).most_common())
# print("\n\n# # # # # # # # # # # errors['ots_ingredients_missing'] # # # # # # # # # # # S")    
# pprint(Counter(errors['ots_ingredients_missing']).most_common())
# pprint(Counter(errors['txt_title_NO_match_rcp']).most_common())
# 
# # SB easy to fix
#pprint(Counter(errors['ots_NO_url']).most_common())
# pprint(Counter(errors['derived_HAS_http_SB_ots']).most_common())
#pprint(Counter(errors['ndb_no_neg99']).most_common())
# pprint(Counter(errors['unknown_alias']).most_common())
# pprint(Counter(errors['items_not_triggering_TAGS']).most_common())
# 
# # wah?
# pprint(Counter(errors['derived_HAS_atomic_alias']).most_common())
# pprint(Counter(errors['derived_w_file_HAS_ndb_no']).most_common())
print("# # # # # # # # # # # errors['dead_ends_in_this_pass'] # # # # # # # # # # # E\n\n")
for k in errors.keys():
    print(k, len(errors[k]))
print("# # # # # # # # # # # errors.keys # # # # # # # # # # # E\n\n")

def print_urls_to_process():
    dict_of_urls_to_process = {}
    
    supplier_regex = [  
      r'(sainsburys)',  # sbs
      r'(morrisons)',   # mrs
      r'(tesco)',       # tsc
      r'(waitrose)',    # wtr
      r'(coop)',        # cop
      r'(asda)',        # asd
      r'(ocado)',       # ocd
      r'(booker)',      # bkr
      r'(aldi)'         # ald
    ]
    
    for ri_name in atomic_LUT:
        url = atomic_LUT[ri_name]['url']
        if url:
            match = None
            for r in supplier_regex:
                m = re.search(r, url)            
                if m:
                    match = m.group(1)
                    break
            if match in dict_of_urls_to_process:
                dict_of_urls_to_process[match].append( (ri_name, url) )
            else:
                dict_of_urls_to_process[match] = [ (ri_name, url) ]
            
    pprint(dict_of_urls_to_process)
    return dict_of_urls_to_process
    
print_urls_to_process()

    
opt_setting = [ v for k, v in opt_dict.items() if v]
if not opt_setting: print(help)
# TODO
# add -c(lean) option
