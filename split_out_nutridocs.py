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
TEMPLATE = Path('./templates_recipe/date_time_recipe_name_template.txt')
def produce_recipe_txts_from_costing_section(costing_section, fileset, overwrite=False):
    recipes_processed = 0
    missing_images = []
    
    target_file_name = ''
    target_path = fileset[TMP_PATH]
    root_date = fileset[ROOT_DATE]
    
    # create regex
    PATTERN  = re.compile(r"--- for the (.*?) \((.*?)\)(.*?)$(.*?)Total\s*\((.*?)\)(.*?)^description:(.*?)^stars:(.*?)^type:(.*?)^lead_image:(.*?)username:(.*?)$", re.M | re.S)
    
    # scan text for recipes    
    for match in PATTERN.finditer(costing_section):
        name, serving_info, notes, ingredients, tot_yield, method, description, stars, type_tag, lead_image, username = match.groups()
        
        if 'calories' in name: continue        
        #print(f"name: {name},\n {serving_info},\n {ingredients},\n {tot_yield},\n {method}\n-\n")
        
        lead_image = str(lead_image).strip() #'20190101_165049_p_l_a_c_e__f_i_l_l_e_r__i_m_a_g_e.jpg'
        username = str(username).strip()
        
        # # get lead image out of method (and remove line)
        # try:
        #     image_match = re.search(r'^(image:(.*?)$)', method, re.M | re.S)
        #     remove_line,lead_image = image_match.groups()
        #     method = method.replace(remove_line, '')
        #     target_file_name = lead_image.replace('.jpg', '.txt')
        # except:
        #     pass
        
        target_file_name = lead_image.replace('.jpg', '.txt')
        
        # if no lead_image to base filename on - use root_date
        if target_file_name == '':
            target_file_name = f"{root_date}_{get_zero_pad_6dig_count()}_{name}.txt"
                
        insertion_dict = {  '__recipe_name__' : name,
                    '__serving_info__' : serving_info,
                    '__ingredients__' : ingredients.strip(),
                    '__total_yield__' : tot_yield,
                    '__method__' : method.strip(),
                    '__notes__' : notes, #'add improvement comments',
                    '__description__' : description.strip(),
                    '__stars__' : str(stars).strip(),
                    '__allergens__' : ', '.join(get_allergens_for(parse_igdt_lines_into_igdt_list(ingredients))),
                    '__tags__' : ', '.join(get_containsTAGS_for(parse_igdt_lines_into_igdt_list(ingredients))),
                    '__type__' : type_tag,
                    '__images__' : get_images_from_lead_image(lead_image),
                    '__lead_image__' : lead_image,
                    '__username__' : username}
        
        rcp = ''
        with TEMPLATE.open('r') as f:
            rcp = f.read()
        
        for marker in insertion_dict:
            print(f"INSERTING: {marker} - {type(insertion_dict[marker])} - {insertion_dict[marker]}")
            rcp = rcp.replace(marker, insertion_dict[marker])
        
        place_txt_file = target_path.joinpath(target_file_name)
        place_img_file = target_path.joinpath(lead_image)
        source_img_file = target_path.parent.joinpath(lead_image)
        print(place_txt_file)
        print(source_img_file)
        print(place_img_file)
        print(rcp)
        
        recipes_processed += 1
        if overwrite == True:
            # write the recipe to folder
            with place_txt_file.open('w') as f:            
                f.write(rcp)
        
        
        #if image exist copy it over
        if lead_image != '':
            if overwrite == True:
                copy2(source_img_file, place_img_file)
        else:
            missing_images.append(name)
        
        # get the date_time_from lead image
        # recipe_file = target_path.joinpath(f"{root_date}_{incrementing_time}_{name})
        
        # write to target_path
    return (recipes_processed, missing_images)


def main():
    pass


NUTRIDOC_LIST = [
# 'nutridoc_no' # ~#recipes/#missing_images - recipe types list rough idea of content
# 'y950',       # ~15   - xmas type recipes
# 'y951',       # 60-70 - bit scrambled 50% done - needs template adding + image name
# 'y952',       # ~12   - bread, and other 
# 'y953',       # ~7    - move, fairly low quality, some product
# 'y954',       # ~35   - start propper - better bread 
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
# 'y975',
# 'y976',      # 
# 'y977',       # 52/1 - sushi, moussaka, tag n cheese, salads, comfort
              # methods & recipes TODO
#'y978',       # DONE 54/5 - sushi, croquettes, wraps, fish, veg, stirfry etc
                #      missing ['mon8pm 200302', 'late snack 20200304', 'mpy', 'snack 20200311', 'sushi & lamb chops']
# 'y979',       # 0314-27 - 43/4: images processed - templates in place - REQ: fill in ~ 50% complete
# 'y420',       # 0328-10 - 21/0: images processed - templates in place - REQ: fill in
# 'y421',       # 0411-24 - 56/0: images processed - templates in place - REQ: fill in
'y422',       # 0425-08 - 31/31: images processed - add image name to templates - REQ: recipes mostly complete
get this scripty to check nutridoc_text for already present templates and skip them /
add relevant image to existing template? just skip format now

# 'y423',       # 0509-22
# 'y424',       # 0523-05
# 'y425',       # 0606-19
# 'y440',       # 0601-15
]


empty_recipe = '''
------------------ for the recipe_name (1)
180m		coffee												# notes, comments
													Total (0g)
description:
thoughts:
stars: 1
type: supplement, snack, breakfast, brunch, salad, soup, component, amuse, side, starter, fish, lightcourse,
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

        if create_templates_from_image_names:
            templates_from_images = ''
            for file_loc in nutridoc_dir.glob('*.jpg'):                
                m = re.match('\d{8}_\d{6}_(.*?)\.jpg', file_loc.name)
                if m:
                    #print(m.group(1))
                    template_img = empty_recipe.replace('recipe_name', m.group(1))
                    template_img = template_img.replace('_li_', file_loc.name)
                    templates_from_images += template_img
                    print(template_img)    
        else:        
            #convert file from RTF to txt
            nutridoc_text = get_text_content_of_file(fileset[FILE_LOC])
            #print(nutridoc_text) # save txt here: fileset[NEW_FILE_PATH]
            
            costing_section = get_costing_section_from_main_doc(nutridoc_text)
            #print(costing_section)
            
            no_processed = produce_recipe_txts_from_costing_section(costing_section, fileset, OVER_WRITE_FILES)
            #no_processed = produce_recipe_txts_from_costing_section(costing_section, fileset)
            processed_nutridocs[fileset[FILE_LOC].name] = no_processed
            
            # list images w recipe name
            print(fileset[FILE_LOC], f"\nGENERATED: {no_processed[0]} recipes", f"\nMISSING IMAGES: {len(no_processed[1])}\n{no_processed[1]}")
            print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \n\n\n\n")
    
    # report
    print("\n\n\nREPORT - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")
    for name, image_info in processed_nutridocs.items():
        print(f"NUTRIDOC: {name}\nRECIPES: {image_info[0]}\nMISSING IMAGES:{len(no_processed[1])}\n{no_processed[1]}\n")

    print("\n\nIf building NUTRIDOC from image set build text templates for each image using './split_out_nutridocs.py -ct' ")
    pprint(NUTRIDOC_LIST)
    