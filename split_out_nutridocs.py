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
def produce_recipe_txts_from_costing_section(costing_section, fileset, available_recipe_images, overwrite=False):
    recipes_processed = []
    missing_images = []
    
    target_file_name = ''
    target_path = fileset[TMP_PATH]
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
        
        recipes_processed.append(name)          # a dict would make search faster no? but for these numbes meh
        
        lead_image = str(lead_image).strip()    # convert None to ''
        
        # maintain a list if images without templates
        lead_image_from_title = None
        try:
            lead_image_from_title = available_recipe_images.pop(name)   # remove from available images
        except KeyError:
            # ONLY APPEND IF lead_image is blank - may not match title - OR leave in as reminder
            if lead_image == '':
                missing_images.append(name)        
                
        if lead_image == '' and lead_image_from_title != None:
            lead_image = lead_image_from_title
            # fill in the lead image in the original template
            replacement = f"lead_image: {lead_image} "
            #original_text = re.sub('lead_image:\s*?$', replacement, original_text, re.M | re.S)  # << NO WORK?? works in pythex?            
            original_text = re.sub('lead_image:', replacement, original_text, re.M | re.S)
            #print(f"\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n{lead_image}\n{replacement}\n{original_text}\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|")
                                    
        
        username = str(username).strip()        
        
        target_file_name = lead_image.replace('.jpg', '.txt')
        
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
        if lead_image != '':
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

            
        
    return (recipes_processed, missing_images)


def main():
    pass


NUTRIDOC_LIST = [
# 'nutridoc_no' # ~#recipes/#missing_images - recipe types list rough idea of content
# 'y950',       # ~15   - xmas type recipes - A LOT of product - leave for now.
# 'y951',       # DONE 0101-18 70/10 - lots of toast & lo-cal                       MISSING IMAGES: 10 ['wmgt', 'buttered wmgt', 'mixed vegetable risotto', 'ham snack', 'coffee', 'milled linseed ingredients', 'poached egg on tomato mgt', 'poached egg on tomato mmgt', 'left over fish broth', 'apple mirin']
# 'y952',       # DONE 0119-31 17/10 - breads & broths                              MISSING IMAGES: 3 ['aubergine and leek w lemon grass soup', 'bun bo huey stock cube', 'pork and blue cheese kebab']  TODO sourdough ring loaf, sourdough boule, confit duck, a few images need tagging
#  #'y953',     # DONE 0201-14 0/0   - NO_RECIPES_FOR_DTK
#'y954',         # TODO > 0214-28 42/3 >> MISSING IMAGES: 41  - start propper - better bread 
# 'y955',       # ~30   - some good lo cal rcps    
# 'y956',       # ~40   - brisket, burgers, broths
# 'y957',       # ~25   - super healthy, meatbaslls, pastas, bread, beetroot burger
# 'y958',       # ~20   - sushi, snack, grains, tortilla, fish
# 'y959',       # ~10   - fish, comfort, snacks, seasoning
# 'y960',       # ~20   - pies, salads, grains, seafood, icecream
# 'y961',       
# 'y962',       #       - started 50% done - needs template adding + image name - sushi, french sticks, brisket, broths
# 'y963',       # ~12   - empty copy - image ~16 cous cous, tortilla, salmon
# 'y964',       #       - tortilla, fish, roast lamb, cheerry tart,  also alot of 3D CAD linux bike, protoyping & scenery
# 'y965',
# 'y966',
# 'y967',
# 'y968',
# 'y969',
# 'y970',
# 'y971',
# 'y972',       # ~13   - lazy days
# 'y973',
# 'y974',
# 'y975',        # 50%        0118-31 - 33/16: images processed - templates in place - REQ: fill in ~50% complete  MISSING IMAGES:1 ['bst']
# 'y976',       # SUSHI      0201-14 - images need sorting, tagging & processing, standard sushi templates bringing in 
# 'y977',       # SUSHI      0215-28 - 54/1: images processed - templates in place - REQ: fill in ~ 4/54 complete - sushi, moussaka, tag n cheese, salads, comfort MISSING IMAGES: 1 ['red pepper & tomatoes']
# 'y978',       # DONE 0229-13 54/5 - sushi, croquettes, wraps, fish, veg, stirfry  MISSING IMAGES: 5 ['mon8pm 200302', 'late snack 20200304', 'mpy', 'snack 20200311', 'sushi & lamb chops']
# 'y979',       #       0314-27 - 43/4: images processed - templates in place - REQ: fill in ~ 50% complete
# 'y420',       #       0328-10 - 21/0: images processed - templates in place - REQ: fill in
# 'y421',       #       0411-24 - 56/0: images processed - templates in place - REQ: fill in
# 'y422',       # DONE 0425-08 - 46/3: salads, broths, comfort, pizza               MISSING IMAGES: 4 ['vc water', 'smoked mussels inc oil', 'buttered crumpet', 'pear pickle']
# 'y423',       # DONE 0509-22 - 58/9: salads, steak chops kofte, tarts, cake       MISSING IMAGES: 3 ['red wine & blue cheese sauce', 'salmon fishsticks', 'coconutapple']
# 'y424',       # DONE 0523-05 - 48/8: chermoula, guinea fowl chinese leaf wraps    MISSING IMAGES: 2 ['sourdough bap', 'hereford pate']
# 'y425',       # 0606-19
# 'y440',       # 0601-15
]


empty_recipe = '''
------------------ for the recipe_name (1)
180m		coffee												# notes, comments
													Total (0g)
description:
notes:
stars: 1
type: sauce, supplement, beverage, snack, breakfast, brunch, salad, soup, component, amuse, side, starter, fish, lightcourse,
	main, crepe, dessert, p4, cheese, comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot
lead_image: _li_
username: carter snapdragonpics


'''


if __name__ == '__main__':
    create_templates_from_image_names = False

    if '-ct' in sys.argv:
        create_templates_from_image_names = True
    
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
        #print(costing_section)
        
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
              f"\nMISSING IMAGES: {len(recipes_and_missing_imgs[1])}\n{recipes_and_missing_imgs[1]}")
        print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \n\n\n\n")
    
    # report
    print("\n\n\nREPORT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")
    for name, image_info in processed_nutridocs.items():
        print(f"NUTRIDOC: {name}\nRECIPES: {image_info[0]}\nMISSING IMAGES:{len(recipes_and_missing_imgs[1])}\n{recipes_and_missing_imgs[1]}\n")
    
    print("\n\nIf building NUTRIDOC from image set build text templates for each image using './split_out_nutridocs.py -ct' ")
    pprint(NUTRIDOC_LIST)
    
    
    
    
    
    