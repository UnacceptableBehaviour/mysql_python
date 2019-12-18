#! /usr/bin/env python




# refresh the asset server with any new data
#import subprocess
from random import randint  # TODO - remove

from pathlib import Path
from pprint import pprint
import re

# RTF conversion to text
from striprtf.striprtf import rtf_to_text


FILE_LOC = 0
TMP_PATH = 1
NEW_FILE_PATH = 2
#
def get_nutridoc_list_rtf():
    base_dir = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components')

    #y971_NUTRITEST_recipes_20191123-06.rtf
    #y(\d{3})_NUTRITEST_recipes_(.*?).rtf
    # $1 'course no.'
    # $2 daterange
    from_to = []
    
    for file_loc in base_dir.rglob('*_NUTRITEST_recipes_*.rtf'):
        if 'y977' in file_loc.name: continue
        # print(file_loc)
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
        print(f"RootDate-{root_date}")

    return from_to


def get_text_content_of_file(rtf_filepath):
    
    with open(rtf_filepath,'r') as f:
        rtf = f.read()
            
    return rtf_to_text(rtf)


def get_costing_section_from_main_doc(text):
    match = re.search(r'_course_cost_start_(.*?)_course_cost_end_', text, re.MULTILINE | re.DOTALL ) # the recipes
    # 
    recipe_text = 'costing_section_not_found'
    
    if match:
        recipe_text = match.group(1)
    
    return recipe_text


def get_allergens_from_ingredients(igds):
    return 'dairy, eggs, peanuts, nuts, seeds_lupin, seeds_sesame, seeds_mustard, fish, molluscs, shellfish, alcohol, celery, gluten, soya, sulphur_dioxide'

def get_tags_from_ingredients(igds):
    return 'vegan, veggie, cbs, chicken, pork, beef, seafood, shellfish, gluten_free, ns_pregnant'

def get_type_from_ingredients(igds):
    return 'component, amuse, side, starter, fish, lightcourse, main, crepe, dessert, p4, cheese, comfort, low_cal, serve_cold, serve_rt, serve_warm, serve_hot'

def get_images_from_lead_image(image):
    return 'implement_image_search.jpg'


TEMPLATE = Path('./scratch/date_time_recipe_name_template.txt')
def produce_recipe_txts_from_costing_section(costing_section, target_path):
    
    # create regex
    PATTERN  = re.compile(r"--- for the (.*?) \((.*?)\)(.*?)$(.*?)Total\s*\((.*?)\)(.*?)---", re.M | re.S)
    
    # scan text for recipes    
    for match in PATTERN.finditer(costing_section):
        name, serving_info, notes, ingredients, tot_yield, method = match.groups()
        
        if 'calories' in name: continue        
        #print(f"name: {name},\n {serving_info},\n {ingredients},\n {tot_yield},\n {method}\n-\n")
        
        lead_image = '20190101_165049_p_l_a_c_e__f_i_l_l_e_r__i_m_a_g_e.jpg'
        
        # get lead image out of method (and remove line)
        try:
            image_match = re.search(r'^(image:(.*?)$)', method, re.M | re.S)
            remove_line,lead_image = image_match.groups()
            method = method.replace(remove_line, '')
        except:
            pass
        
        
        
        insertion_dict = {  '__recipe_name__' : name,
                    '__serving_info__' : serving_info,
                    '__ingredients__' : ingredients.strip(),
                    '__total_yield__' : tot_yield,
                    '__method__' : method.strip(),
                    '__notes__' : notes, #'add improvement comments',
                    '__description__' : 'describe me',
                    '__stars__' : str(randint(1,5)),
                    '__allergens__' : get_allergens_from_ingredients(ingredients),
                    '__tags__' : get_tags_from_ingredients(ingredients),
                    '__type__' : get_type_from_ingredients(ingredients),
                    '__images__' : get_images_from_lead_image(lead_image),
                    '__lead_image__' : lead_image}
        
        rcp = ''
        with TEMPLATE.open('r') as f:
            rcp = f.read()
        
        for marker in insertion_dict:
            rcp = rcp.replace(marker, insertion_dict[marker])
        
        print(rcp)
        # get the date_time_from lead image
        # recipe_file = target_path.joinpath(f"{root_date}_{incrementing_time}_{name})
        
        # write to target_path


def main():
    pass



if __name__ == '__main__':
    #main()
    # with PyCallGraph(output=graphviz, config=config):
    #     main()
    
    # 'recipe_name' : recipe_text
    processed_recipes = {}
    
    # Create directories from nutridocd
    files_to_process = get_nutridoc_list_rtf()
    
    # FILE_LOC = 0
    # TMP_PATH = 1
    # NEW_FILE_PATH = 2
    # take contents out of each file and create text docs
    for fileset in files_to_process:        
        #convert file from RTF to txt
        nutridoc_text = get_text_content_of_file(fileset[FILE_LOC])
        #print(nutridoc_text) # save txt here: fileset[NEW_FILE_PATH]
        
        costing_section = get_costing_section_from_main_doc(nutridoc_text)
        #print(costing_section)
        
        produce_recipe_txts_from_costing_section(costing_section, fileset[TMP_PATH])
        
        print(fileset[FILE_LOC])
        print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = \n\n\n\n")
        if 'y951' in str(fileset[FILE_LOC]):break

# Place __nutridoc.txt in dir
# 
# Scan txt with pattern
# 
# Template = open file
# 
# Insert matches into template:
# T.replace (__tag__ ,match ?!
# REGEX to 
# 
# For each












