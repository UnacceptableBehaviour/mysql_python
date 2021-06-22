#! /usr/bin/env python

# pre processing recipe diary to create structure data for asset pipeline
# enables
# a refresh the asset server with any new data, and a DB rebuild based on relevant adapter

from pathlib import Path
from shutil import copy2
from pprint import pprint
import re
import sys

# RTF conversion to text
from striprtf.striprtf import rtf_to_text

from food_sets import get_allergens_for,get_containsTAGS_for

FILE_LOC = 0
TMP_PATH = 1
NEW_FILE_PATH = 2
ROOT_DATE = 3
#
def get_nutridoc_list_rtf():
    base_dir = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components')

    #y971_NUTRITEST_recipes_20191123-06.rtf
    #y(\d{3})_NUTRITEST_recipes_(.*?).rtf
    # $1 'course no.'
    # $2 daterange
    from_to = []

    for file_loc in base_dir.rglob('*_NUTRITEST_recipes_*.rtf'):
        print(file_loc)
        # print(file_loc.name)
        # print(file_loc.parent)
        # print(file_loc.stem)
        new_file=f"{file_loc.stem}.txt"
        tmp_path = file_loc.parent.joinpath(file_loc.stem).joinpath('_i_w_r_auto_tmp')
        new_file_path = tmp_path.joinpath(new_file)
        root_date = re.search(r'(\d{8})-', file_loc.stem).group(1)
        # print(new_file_path ) # target
        # print(tmp_path)
        # print(type(tmp_path))
        from_to.append([file_loc, tmp_path, new_file_path, root_date])
        tmp_path.mkdir(parents=True, exist_ok=True)
        #print(f"RootDate-{root_date}")

    return from_to


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

    # remove duplicates from list
    i_list = list(dict.fromkeys(i_list))
    # remove empty strings
    i_list = list(filter(None, i_list))

    return i_list


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

OVER_WRITE_FILES = True
DUMBY_RUN = False
TEMPLATE = Path('./templates_recipe/date_time_recipe_name_template.txt')
RECIPES_PROCESSED = 0
MISSING_IMAGES = 1
INGREDIENTS_TOTAL_0G = 2
RECIPES_WITH_NON_ZERO_TOTALS = 3
AVAILABLE_RECIPE_IMAGES = 4
def produce_recipe_txts_from_costing_section(costing_section, fileset, available_recipe_images, overwrite=False):
    recipes_processed = []
    missing_images = []
    recipes_w_total_0g = []
    recipes_with_non_zero_totals = []

    # print('> - - - - - S \ ')
    # pprint(fileset)
    # #tmp_path = file_loc.parent.joinpath(file_loc.stem).joinpath('_i_w_r_auto_tmp')
    # print(fileset[TMP_PATH].parent.joinpath('_i_w_r_auto_tot0g'))
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

        if 'calories' in name: continue

        target_path = fileset[TMP_PATH]         # reset target path in case changed to _i_w_r_auto_tot0g below

        recipes_processed.append(name)          # a dict would make search faster no? but for these numbes meh

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

            #print(f"\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n{lead_image}\n{replacement}\n{original_text}\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|")


        username = str(username).strip()

        target_file_name = lead_image.lower().replace('.jpg', '.txt')

        # if no lead_image to base filename on - use root_date
        if target_file_name == '':
            target_file_name = f"{root_date}_{get_zero_pad_6dig_count()}_{name}.txt"

        insertion_dict = {  '__recipe_name__' : name,
                    '__serving_info__' : serving_info,
                    '__ingredients__' : ingredients.strip(),
                    '__total_yield__' : tot_yield,
                    '__method__' : method.strip(),
                    '__description__' : description.strip(),
                    '__notes__' : str(notes).strip() + ('\n' + str(notes_after_serve)).strip(),  # if notes_after_serve existd put it on the next line!
                    '__stars__' : str(stars).strip(),
                    '__allergens__' : ', '.join(get_allergens_for(parse_igdt_lines_into_igdt_list(ingredients))),
                    '__tags__' : ', '.join(get_containsTAGS_for(parse_igdt_lines_into_igdt_list(ingredients))),
                    '__type__' : type_tag.strip(),
                    '__images__' : get_images_from_lead_image(lead_image),
                    '__lead_image__' : lead_image,
                    '__username__' : username}

        rcp = ''
        with TEMPLATE.open('r') as f:
            rcp = f.read()

        for marker in insertion_dict:
            #print(f"INSERTING: {marker} - {type(insertion_dict[marker])} - {insertion_dict[marker]}")
            rcp = rcp.replace(marker, insertion_dict[marker])

        if 'Total (0g)' in rcp:
            recipes_w_total_0g.append(name)
            target_path = fileset[TMP_PATH].parent.joinpath('_i_w_r_auto_tot0g')
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            recipes_with_non_zero_totals.append(name)

        place_txt_file = target_path.joinpath(target_file_name)
        place_img_file = target_path.joinpath(lead_image)
        source_img_file = target_path.parent.joinpath(lead_image)


        # create component templates for processing into recipes
        # & DB of some description - ORM later in pipeline
        if overwrite == True:
            # write the recipe to folder
            with place_txt_file.open('w') as f:
                f.write(rcp)

        #if image exist copy it over
        if lead_image != '' and lead_image != '_li_':
            if overwrite == True:
                copy2(source_img_file, place_img_file)

        if overwrite == True:
            # show actions if live (IE NOT option -ct)
            print(place_txt_file)
            print(source_img_file)
            print(place_img_file)
            print(rcp)
        else:
            # print original with image inserted into lead_image: img.jpg   < where was blank
            print(original_text + '\n')



    return [recipes_processed, missing_images, recipes_w_total_0g, recipes_with_non_zero_totals, available_recipe_images]


def main():
    pass


NUTRIDOC_LIST = [
                # 2019 * * *
# 'nutridoc_no' # ~#recipes/#missing_images - recipe types list rough idea of content
# 'y950',       # ~15   - xmas type recipes - A LOT of product - leave for now.
# 'y951',       #* DONE 0101-18 70/10 - lots of toast & lo-cal                       MISSING IMAGES: 10 ['wmgt', 'buttered wmgt', 'mixed vegetable risotto', 'ham snack', 'coffee', 'milled linseed ingredients', 'poached egg on tomato mgt', 'poached egg on tomato mmgt', 'left over fish broth', 'apple mirin']
# 'y952',       #* DONE 0119-31 17/10 - breads & broths                              MISSING IMAGES: 3 ['aubergine and leek w lemon grass soup', 'bun bo huey stock cube', 'pork and blue cheese kebab']  TODO sourdough ring loaf, sourdough boule, confit duck, a few images need tagging
#  #'y953',     #* DONE 0201-14 0/0   - NO_RECIPES_FOR_DTK
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
#               #* 2020 * * *
# 'y974',       #  DONE 0104-17 - 18/1  crispy prawns, stir fry, arancini, moussakas, roast potatoes & salads
# 'y975',       #  DONE 0118-31 - 19/14: images processed - templates in place - REQ: fill in ~50% complete  MISSING IMAGES:1 ['bst']
# 'y976',       #  SUSHI TODO DONE 0201-14 42/45- standard sushi templates bringing in
# 'y977',       #  SUSHI TODO DONE 0215-28 - 18/37: images processed - templates in place - REQ: fill in ~ 4/54 complete - sushi, moussaka, tag n cheese, salads, comfort MISSING IMAGES: 1 ['red pepper & tomatoes']
# 'y978',       #* DONE 0229-13 54/5 - sushi, croquettes, wraps, fish, veg, stirfry  MISSING IMAGES: 5 ['mon8pm 200302', 'late snack 20200304', 'mpy', 'snack 20200311', 'sushi & lamb chops']
# 'y979',       #  DONE 0314-27 - 34/4: broths, dumpling dough, cabbage, figs, sticky pork
 'y420',       #       0328-10 - 0/21: images processed - templates in place - REQ: fill in
 'y421',       #       0411-24 - 4/52: images processed - templates in place - REQ: fill in
# 'y422',       #* DONE 0425-08 - 46/3: salads, broths, comfort, pizza               MISSING IMAGES: 4 ['vc water', 'smoked mussels inc oil', 'buttered crumpet', 'pear pickle']
# 'y423',       #* DONE 0509-22 - 58/9: salads, steak chops kofte, tarts, cake       MISSING IMAGES: 3 ['red wine & blue cheese sauce', 'salmon fishsticks', 'coconutapple']
# 'y424',       #* DONE 0523-05 - 48/8: chermoula, guinea fowl chinese leaf wraps    MISSING IMAGES: 2 ['sourdough bap', 'hereford pate']
# 'y425',       #* DONE 0606-19 - 51/1: salads, steak chops kofte, tarts, breads     MISSING IMAGES: 6 ['waterc', 'halfwaterc', 'haggis yorkie', 'indian dips', 'roast chicken dinner', 'drink snack 20200619']
# 'y426',       #  DONE 0620-04 - 45/21: << TODO croquettes, salads, flatbread,      MISSING IMAGES: 3 ['packed lunch 20200621', 'tom & couscous em broth', 'em test broth']
 'y427',       #       0705-18 - 29/2:  flat bread, baguettes, rhubarb tart
# 'y428',       #  DONE 0719-01 - 15/29:   < mustard chicken sequence, cardamom flatbreads
               #       0801-14 - no nutridoc!?
 'y429',       #       0815-28 - 50/4:
# 'y430',       #  DONE 0829-11 - 50/26: salads roast burgers snacks bakes . . . TODO loads of good stuff!
# 'y431',       #       0912-25 - 4 /2:
# 'y432',       #  DONE 0929-09 - 15/42: loads of material!
 'y433',       #       1010-23 - 12/2:
 'y434',       #       1024-06 - 00/0:
 'y435',       #       1107-20 -
 'y436',       #       1121-04 -
 'y437',       #       1205-18 - 00/28
 'y438',       #       1024-06 - 00/0:
# 'y439',       #     0116-0212 - 00/0:
# 'y440',       #  0601-15
# 'y441',       #  DONE 0313-26 - 53/02: pizza, wontan, kofte, maki, salads          MISSING IMAGES: 6 ['basic broth','feijoada & maki broth','steamed veg broth','steamed veg broth w potato','hot chocolate','macchiato']
# 'y442',       #  DONE 0327-09 - 62/00: salads, sanwiches, keto, fermented          MISSING IMAGES: 7 ['liver & onions', 'feijoada broth', 'post bike ham salad ', 'turkey & squid balls w chinese leaf ', 'brined red cabbage', 'garlic butter prawns', '7.5pc brine']
# 'y443',       #  DONE 0410-23 -
 'y444',       #       0424-07 - 60/12: GOOD lo-cal set !! inc: prawn & melon salad w soft boiled eggs // prawn & bamboo broth
 'y445',       #       0508-21 - 53/05: broths, bento, cassoulet, flans
  # 'y446',
# * next to done means superfluous image files removed
]

# DOC_NAME                                   RECIPES  COMPLETE  TOTAL 0g  TMP FROM IMG  MISSING IMG
# y437_NUTRITEST_recipes_20201205-18.rtf      28       0         28          0             0
# y436_NUTRITEST_recipes_20201121-04.rtf      0        0         0           0             0
# y445_NUTRITEST_recipes_20210508-21.rtf      53       8         45          0             5
# y435_NUTRITEST_recipes_20201107-20.rtf      0        0         0           0             0
# y420_NUTRITEST_recipes_20200328-10.rtf      25       0         25          1             0
# y438_NUTRITEST_recipes_20201219-0115.rtf    2        2         0           0             2
# y433_NUTRITEST_recipes_20201010-23.rtf      50       12        38          0             1
# y444_NUTRITEST_recipes_20210424-07.rtf      60       24        36          1             12
# y429_NUTRITEST_recipes_20200815-28.rtf      54       50        4           1             47
# y421_NUTRITEST_recipes_20200411-24.rtf      52       2         50          3             0
# y427_NUTRITEST_recipes_20200705-18.rtf      32       30        2           3             29
# y434_NUTRITEST_recipes_20201024-06.rtf      37       36        1           1             36


empty_recipe = '''
------------------ for the recipe_name (1)
180m		coffee												# notes, comments
													Total (0g)
description:
notes:
stars: 1
type: dough, bread, sandwich, sauce, supplement, beverage, snack, breakfast, brunch, salad,
 soup, component, amuse, side, starter, sushi, fish, lightcourse, main, crepe, dessert, p4, cheese,
 comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot
lead_image: _li_
username: carter snapdragonpics


'''

empty_lower_template = '''
description:
notes:
stars: 1
type: dough, bread, sandwich, sauce, supplement, beverage, snack, breakfast, brunch, salad,
 soup, component, amuse, side, starter, sushi, fish, lightcourse, main, crepe, dessert, p4, cheese,
 comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot
lead_image: _li_
username: carter snapdragonpics



-'''

if __name__ == '__main__':
    split_recipes_from_diary_entry = False
    create_templates_from_image_names = False
    verbose_mode = False

    if '-sp' in sys.argv:
        split_recipes_from_diary_entry = True

    if '-ct' in sys.argv:
        create_templates_from_image_names = True

    if '-v' in sys.argv:
        verbose_mode = True

    #main()
    # with PyCallGraph(output=graphviz, config=config):
    #     main()

    #parse_igdt_lines_into_igdt_list()

    #sys.exit()

    # 'nutridoc' : (recipes process, [list missing images])
    processed_nutridocs = {}

    # Create directories from nutridocd
    files_to_process = get_nutridoc_list_rtf()

    for f in files_to_process:
        check = 'NOT PRESENT'
        filename = str(f[0].name)
        m = re.match(r'^(y\d\d\d)', filename)
        print(f"M: {m.group(1)} {m.group(1) in NUTRIDOC_LIST}<")
        for nutridoc_no in NUTRIDOC_LIST:
            if nutridoc_no in filename:
                check = 'PRESENT'
        #pprint(f)
        print(filename, check)

    #sys.exit()

    # FILE_LOC = 0
    # TMP_PATH = 1
    # NEW_FILE_PATH = 2
    # take contents out of each file and create text docs
    for fileset in files_to_process:
        filename = str(fileset[0].name)
        m = re.match(r'^(y\d\d\d)', filename)

        nutridoc_dir = fileset[1].parent
        print(m.group(1))
        if m.group(1) in NUTRIDOC_LIST:
            print(f"PROCESSING - - - - : {str(fileset[FILE_LOC])} * *\nIN:{nutridoc_dir}")
        else:
            print(f"SKIPPING: {str(fileset[FILE_LOC])}")
            continue

        print(f"create_templates_from_image_names: {create_templates_from_image_names} - {filename}")

        # convert file from RTF to txt
        nutridoc_text = get_text_content_of_file(fileset[FILE_LOC])
        #print(nutridoc_text) # save txt here: fileset[NEW_FILE_PATH]

        costing_section = get_costing_section_from_main_doc(nutridoc_text)
        print(costing_section)

        print("\n**\n**\nIf reading this re-run with option -sp: './split_out_nutridocs.py -sp' \nand shift-G search for '- UUU -' to find the beginning of the separated recipes\n**\n**\n")

        if split_recipes_from_diary_entry == True:
            DIARY_RCP_ENTRY = re.compile(r"(----------------- for the.*?^-)", re.M | re.S)
            diary_text = ""
            recipes = "-"
            print(" - MMM -")
            for match in DIARY_RCP_ENTRY.finditer(costing_section):
                extract = match.group(1)
                if 'calories' in extract:
                    diary_text = diary_text + extract
                else:
                    extract += '~'      # w/o this it matches the start of the recipe!
                    #print("\n - o -")
                    #print(extract)
                    #print(re.sub('\s-~',empty_lower_template, extract))
                    new_template = re.sub('\s-~',empty_lower_template, extract)
                    #print(new_template)
                    recipes = recipes + new_template
                    #print("- - - recipes - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
                    #print(recipes)
                print("\n - ^ -")

            print(" - UUU -")
            print(recipes)
            print(diary_text)
            print("Diary & recipe components separated & description:, notes: etc added to recipes")
            sys.exit(0)

        # get list of available recipe images format: date_time_recipe.jpg - EG: 20200428_181655_fried chicken coating pancakes.jpg
        available_recipe_images = {}
        for image_file in nutridoc_dir.glob('*.jpg'):
            m = re.match('\d{8}_\d{6}_(.*?)\.jpg', image_file.name)
            if m:
                recipe_name = m.group(1)
                available_recipe_images[recipe_name] = image_file.name
                print(f"Rcp img:{recipe_name} = {available_recipe_images[recipe_name]}")

        recipes_and_missing_imgs = None
        if create_templates_from_image_names:
            recipes_and_missing_imgs = produce_recipe_txts_from_costing_section(costing_section, fileset, available_recipe_images, DUMBY_RUN)
        else:
            recipes_and_missing_imgs = produce_recipe_txts_from_costing_section(costing_section, fileset, available_recipe_images, OVER_WRITE_FILES)


        if create_templates_from_image_names:
            templates_from_images = ''

            for recipe_name, image_file in available_recipe_images.items():
                #print(recipe_name, image_file)
                template_img = empty_recipe.replace('recipe_name', recipe_name)
                template_img = template_img.replace('_li_', image_file)
                templates_from_images += template_img
                print(template_img)


        processed_nutridocs[fileset[FILE_LOC].name] = recipes_and_missing_imgs

        print(f"REPORT: = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \ ")
        print(fileset[FILE_LOC].name, f"\nGENERATED: {len(recipes_and_missing_imgs[0])} recipes",
              f"\nTEMPLATES FROM IMAGES: {len(available_recipe_images)}",
              f"\nMISSING IMAGES: {len(recipes_and_missing_imgs[MISSING_IMAGES])}\n{recipes_and_missing_imgs[MISSING_IMAGES]}")
        print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \n\n\n\n")

    # report
    missing_images_across_all_docs = {}
    print("\n\n\nREPORT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")
    pprint(processed_nutridocs)
    print('^^processed_nutridocs^^')
    for name, image_info in processed_nutridocs.items():
        # all_recipes, miss_img, total_0g, complete_rcp = [],[],[],[]


        print(fileset[FILE_LOC].name, f" -: {len(image_info[RECIPES_PROCESSED])} recipes")

        print(f"COMPLETE:       {len(image_info[RECIPES_WITH_NON_ZERO_TOTALS])}  < < - - - - - - - - -<")
        if verbose_mode: print(image_info[RECIPES_WITH_NON_ZERO_TOTALS])

        print(f"TOTAL 0g:       {len(image_info[INGREDIENTS_TOTAL_0G])}  < < - - - - - - - - -<")
        if verbose_mode: print(image_info[INGREDIENTS_TOTAL_0G])

        print(f"TMPLT FRM IMG:  {len(image_info[AVAILABLE_RECIPE_IMAGES])}  < < - - - - - - - - -<")
        if verbose_mode: print(image_info[AVAILABLE_RECIPE_IMAGES])

        print(f"MISSING IMAGES: {len(image_info[MISSING_IMAGES])}  < < - - - - - - - - -<")
        if verbose_mode: print(image_info[MISSING_IMAGES])

        print("\nMissing image recipe names:\n")
        for i in image_info[MISSING_IMAGES]:
            print(i)
        missing_images_across_all_docs[name] = image_info[MISSING_IMAGES]

    print("\n\n\nREPORT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")
    doc_name = 'y425_NUTRITEST_recipes_20200606-0919.rtf'
    column_headers = ['RECIPES','COMPLETE','TOTAL 0g','TMP FROM IMG','MISSING IMG']
    header = 'DOC_NAME'.ljust(len(doc_name)+3) + '  '.join(column_headers)
    print(header)
    for name, image_info in processed_nutridocs.items():
        # stats = dict(zip(column_headers, immage_info_list))
        stats = {
            'RECIPES': image_info[RECIPES_PROCESSED],
            'COMPLETE': image_info[RECIPES_WITH_NON_ZERO_TOTALS],
            'TOTAL 0g': image_info[INGREDIENTS_TOTAL_0G],
            'TMP FROM IMG': image_info[AVAILABLE_RECIPE_IMAGES],
            'MISSING IMG': image_info[MISSING_IMAGES]
        }
        row = name.ljust(len(doc_name))
        for col, data in stats.items():
            row += str(len(data)).center(len(col)+2)

        print(row)
        missing_images_across_all_docs[name] = image_info[MISSING_IMAGES]

    print("\n\nIf building NUTRIDOC from image set build text templates for each image using './split_out_nutridocs.py -ct' ")
    pprint(NUTRIDOC_LIST)
    pprint(missing_images_across_all_docs)

#
# RECIPES_PROCESSED = 0
# MISSING_IMAGES = 1
# INGREDIENTS_TOTAL_0G = 2
# RECIPES_WITH_NON_ZERO_TOTALS = 3
# AVAILABLE_RECIPE_IMAGES = 4

    #pprint(recipes_and_missing_imgs)
    #pprint(processed_nutridocs)
