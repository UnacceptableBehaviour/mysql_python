#! /usr/bin/env python




# refresh the asset server with any new data
#import subprocess

from pathlib import Path
from pprint import pprint
import re

# RTF conversion to text
from striprtf.striprtf import rtf_to_text



def get_nutridoc_list_rtf():
    base_dir = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components')

    #y971_NUTRITEST_recipes_20191123-06.rtf
    #y(\d{3})_NUTRITEST_recipes_(.*?).rtf
    # $1 'course no.'
    # $2 daterange
    
    for file_loc in base_dir.rglob('*_NUTRITEST_recipes_*.rtf'):
        print(file_loc)
        print(file_loc.name)
        print(file_loc.parent)
        print(file_loc.stem)
        new_file=f"{file_loc.stem}.txt"
        print(file_loc.parent.joinpath(file_loc.stem).joinpath('_i_w_r_tmp').joinpath(new_file) ) # targer        
        print('-')




def main():
    pass



if __name__ == '__main__':
    #main()
    # with PyCallGraph(output=graphviz, config=config):
    #     main()
    
    # tests
    get_nutridoc_list_rtf()
    print("\n\n\n\n")
    
    rtf_filename = '/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/y971_NUTRITEST_recipes_20191123-06.rtf'
    with open(rtf_filename,'r') as f:
        rtf = f.read()
            
    text = rtf_to_text(rtf)
    print(text)
    print("\n\n\n\n")
    # # section of interest (_course_cost_start_)(.*?)(_course_cost_end_) # the recipes
    # # each recipe
    match = re.search(r'_course_cost_start_(.*?)_course_cost_end_', text, re.MULTILINE | re.DOTALL ) # the recipes
    # 
    recipe_text = 'arse'
    if match:
        recipe_text = match.group(1)
        print('* * * * MATCH')
        print(recipe_text)
        print("\n\n\n\n")
    else:
        print('* * * * NOOO MATCH')
        print(recipe_text)
        print("\n\n\n\n")
    # 
    # #
    # # match = re.search( r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)', recipe_text, re.MULTILINE | re.DOTALL )
    # 
    # match = re.search( r'^-+- for the (.*) \((\d+)\)(.*)^\s+Total \((.*?)\)', recipe_text, re.MULTILINE | re.DOTALL )
    # 
    #
    # --- for the (.*?) \((.*?)\)(.*?)Total\s*\((.*?)\)(.*?)---
    PATTERN  = re.compile(r"--- for the (.*?) \((.*?)\)(.*?)Total\s*\((.*?)\)(.*?)---", re.M | re.S)
    
    for match in PATTERN.finditer(recipe_text):
        pprint(match.groups())
        print(len(match.groups()))
        print(type(match.groups()))
        name, serving_info, ingredients, tot_yield, method = match.groups()
        print("- - - - match - - - -")
        print(f"name: {name},\n {serving_info},\n {ingredients},\n {tot_yield},\n {method}\n-\n")
    













