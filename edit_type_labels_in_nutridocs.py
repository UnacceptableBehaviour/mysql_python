#! /usr/bin/env python

import sys
from pathlib import Path
from pprint import pprint
import re
import json # JSONDecodeError
from food_sets import atomic_LUT
from timestamping import nix_time_ms, hr_readable_w_nix_ms_from_nix
import shutil

NAS_PATH              = Path('/Volumes/home/dtk_backups')
MISSLABELED_FILE_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_incorrectly_labeled_WEBIF.json')

opt_dict = {
    'verbose_mode':     True,
    'backup_docs':      True,
    'edit_docs_live':   False,
    'add_labels':       False
}

if '-nb' in sys.argv:
    opt_dict['backup_docs'] = False

if '-l' in sys.argv:
    opt_dict['edit_docs_live'] = True

if '-a' in sys.argv:
    opt_dict['add_labels'] = True


help_string = f'''\n\n\n
HELP:\n
Adds or removes type labels to a list of spcecified recipes found in MISSLABELED_FILE_JSON found @
{MISSLABELED_FILE_JSON}

This json file is generated from the results of the SEARCH page that have been checked
and checked recipes SAVED. . . 

- - - options - - - 
-nb         NO document backup,
            DEFAULT is all docs backed up to
            {NAS_PATH}

-l          LIVE original docs are edited in place. 
            DEFAULT show intent

-a          ADD labels to target docs
            DEFAULT REMOVE labels from doc type list

-h          This help
'''

if ('-h' in sys.argv) or ('--h' in sys.argv) or ('-help' in sys.argv) or ('--help' in sys.argv):
    print(help_string)
    sys.exit(0)


def backup_nutri_docs_recipes_to_NAS(source_file_list):
    target_dir = NAS_PATH.joinpath('dtk_rcps').joinpath(f"{hr_readable_w_nix_ms_from_nix(nix_time_ms())}_nutri_docs_recipes")
    if NAS_PATH.exists():        
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"FAILED TO CREATE BACKUP DIR:\n{target_dir}")
        sys.exit(0)

    for f in source_file_list:
        target = target_dir.joinpath(f.name)
        print(f"backing up: {f}\nto:{target}\n")        
        shutil.copy(f, target)
    
    shutil.copy(MISSLABELED_FILE_JSON, target_dir.joinpath(MISSLABELED_FILE_JSON.name))


#pprint(info_for_scrape_intermediate_file)

with open(MISSLABELED_FILE_JSON, 'r') as f:
    incorrect_label_with_list = json.load(f)

# missing_to_file = json.dumps(info_for_scrape_intermediate_file)
# with open(MISSLABELED_FILE_JSON, 'w') as f:
#     f.write(missing_to_file)

def get_nutridoc_list_rtf(base_dir):    

    #y971_NUTRITEST_recipes_20191123-06.rtf

    file_LUT = {}
    nutri_doc_ref =''

    print(f'\nNutridocs Found:{base_dir}')
    for file_loc in base_dir.rglob('*_NUTRITEST_recipes_*.rtf'):        
        nutri_doc_ref = re.search(r'(y\d{3})_', file_loc.stem).group(1)
        file_LUT[nutri_doc_ref] = file_loc

        if opt_dict['verbose_mode']:
            print(f"{nutri_doc_ref} : {file_loc.name} - {file_loc} ")
        else:
            print(re.search(r'(y\d{3})_', file_loc.stem).group(1), end=' ')
        
    return file_LUT


nutridocs_base_dir = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/')
file_LUT_v2 = get_nutridoc_list_rtf(nutridocs_base_dir)


if opt_dict['backup_docs']:
    print('\n\nBacking up nutridocs . . .')
    source_file_list = list(file_LUT_v2.values())
    #pprint(source_file_list)    
    backup_nutri_docs_recipes_to_NAS(source_file_list)
    print('Option -nb   NO Backups to skip further backups')

    

#pprint(file_LUT)
# {'y965': PosixPath('./y965_NUTRITEST_recipes_20190719-01.rtf'),
#  'y966': PosixPath('./y966_NUTRITEST_recipes_20190802-15.rtf'),
#  'y967': PosixPath('./y967_NUTRITEST_recipes_20190816-29.rtf'),
#  'y968': PosixPath('./y968_NUTRITEST_recipes_20190830-12.rtf'),
#  'y969': PosixPath('./y969_NUTRITEST_recipes_20190913-1108.rtf'),
#  'y970': PosixPath('./y970_NUTRITEST_recipes_20191109-22.rtf'),
#  'y971': PosixPath('./y971_NUTRITEST_recipes_20191123-06.rtf'),
#  'y972': PosixPath('./y972_NUTRITEST_recipes_20191207-20.rtf')}

# corrections_dict = {}
# label = 'dessert'
# remove_label = []
# remove_dict = {
# 'y425':['salad & chermoula stock'],
# 'y429':['roast lamb couscous'],
# 'y430':['burger salad'],
# 'y441':['cavolo nero cm','avocado & fishstick cm','avocado & grape salad'],
# 'y442':['fishsticks & cucumber yogurt','beetroot humous yogurt dip'],
# 'y443':['chicken liver & avocado pate'],
# 'y453':['stuffed globe courgette','bb humous w chicken chermoula wrap','prawn & chive wrap'],
# 'y455':['beef spinach & kimchi omelette'],
# 'y457':['chicken thigh pancake','fried egg & cheddar beef burger w onion chips','wild garlic chapos','chicken & yogurt kimchi mini wrap','chicken & kimchi egg wrap w tomatoes','chicken & kimchi egg wrap','chapos','kimchi yogurt'],
# 'y458':['ham & tomato on wild garlic chapo','coriander mayo on wild garlic chapo','squid caprese','seared ribeye & awsome sauce','steak & mushroom on wild garlic chapo'],
# 'y459':['chicken & sweet onion mini wrap','spring greens & kimchi','courgette spaghetti w strawberries basil'],
# 'y460':['prawn & spring onion pancake','spring greens kimchi & sweet pickled onion'],
# 'y957':['aubergine pate crouton w egg'],
# 'y959':['movie snacks 20190506','melon parma & couscous'],
# 'y963':['prawn couscous w garlic flatbread'],
# 'y967':['green bean and leek coconut curry'],
# 'y968':['honey onion and cucumber w chilli & lime'],
# 'y976':['chicken pancake w cardamom jelly','water chestnut & courgette pancake w lemon sole','water chestnut & courgette pancake w tuna','water chestnut & courgette salad','water chestnut & courgette pancake w fish'],
# 'y978':['turkey sushi & omelette wrap','omelette wrap w shredded salad'],
# }


# for nut_id, rcp_list in remove_dict.items():
#     corrections_dict[file_LUT_v2[nut_id]] = rcp_list

def remove_labels_v4(label, corrections_dict):
    for file, recipes in corrections_dict.items():
        with open(file, 'r') as f:
            content = f.read()
        print(f">=- - - - scanning: {file.name}\nfor{recipes}\n\n")
        for recipe in recipes:
            pattern = re.compile(r'(------------------ for the {} \(.*?\).*?)(?=username:)'.format(recipe), re.DOTALL)
            match = pattern.search(content)
            if match:
                print(f"found: {recipe} < {file.name}")
                recipe_content = match.group(1)
                print(f"recipe_content:\n{recipe_content}\n - - ")
                print(f"group(0):\n{match.group(0)}\n - - ")
                type_pattern = re.compile(r'(?<=\ntype: )(.*?)(?=\nlead_image:)', re.DOTALL)
                type_match = type_pattern.search(recipe_content)
                if type_match:
                    type_content = type_match.group(1)
                    print(f"type_content: {type_content} < pre {label}")
                    type_content = type_content.replace(label, '')
                    print(f"type_content: {type_content} < post")
                    type_content = re.sub(r'^\s*,\s*\b', ' ', type_content)         # remove leading comma
                    type_content = re.sub(r'(\s*,\s*,\s*)', ', ', type_content)     # remove label1, ,label2
                    #type_content = re.sub(r'\b\s*,\s*\\', '\\\\', type_content)         # remove trailing comma
                    recipe_content = recipe_content[:type_match.start(1)] + type_content + recipe_content[type_match.end(1):]
                    print(recipe_content)
                    print('- - - - \n\n')
                content = content[:match.start(1)] + recipe_content + content[match.end(1):]
        new_path = Path('./',file.name)
        #with open(new_path, 'w') as f:
        with open(file, 'w') as f:
            f.write(content)

# def remove_label(label, coma_separated_label_string):
#     # Split the string into a list of labels
#     label_list = coma_separated_label_string.split(',')
    
#     # Strip whitespace from each label and convert to lowercase
#     label_list = [l.strip().lower() for l in label_list]
    
#     # Remove the specified label from the list
#     if label.lower() in label_list:
#         label_list.remove(label.lower())
    
#     # Sort the list of labels in alphabetical order
#     label_list.sort()
    
#     # Recombine the list into a comma-separated string
#     result = ', '.join(label_list)
    
#     return result

# def add_label(label, coma_separated_label_string):
#     # Split the string into a list of labels
#     label_list = coma_separated_label_string.split(',')
    
#     # Strip whitespace from each label and convert to lowercase
#     label_list = [l.strip().lower() for l in label_list]
    
#     # Add the specified label to the list if it is not already present
#     if label.lower() not in label_list:
#         label_list.append(label.lower())
    
#     # Sort the list of labels in alphabetical order
#     label_list.sort()
    
#     # Recombine the list into a comma-separated string
#     result = ', '.join(label_list)
    
#     return result


def add_remove_label(label, coma_separated_label_string, add=True):
    # type labels may be on multiple lines
    # remove \n
    coma_separated_label_string = re.sub(r'\s', '', coma_separated_label_string)
    # remove rtf EOL character '\'
    coma_separated_label_string = re.sub(r'\\', '', coma_separated_label_string)

    label_list = coma_separated_label_string.split(',')
    
    label_list = [l.strip().lower() for l in label_list]
    
    if add:
        if label.lower() not in label_list:
            label_list.append(label.lower())
    else:
        if label.lower() in label_list:
            label_list.remove(label.lower())
    
    label_list.sort()
    
    result = ', '.join(label_list)
    
    result += '\\'  # add rtf EOL character '\'

    return result


def edit_nutridoc_labels(label, corrections_dict, add=True):
    for file, recipes in corrections_dict.items():
        with open(file, 'r') as f:
            content = f.read()
        print(f">=- - - - scanning: {file.name}\nfor{recipes}\n\n")
        for recipe in recipes:
            pattern = re.compile(r'(------------------ for the {} \(.*?\).*?)(?=username:)'.format(recipe), re.DOTALL)
            match = pattern.search(content)
            if match:
                print(f"found: {recipe} < {file.name}")
                recipe_content = match.group(1)
                print(f"recipe_content:\n{recipe_content}\n - - ")
                print(f"group(0):\n{match.group(0)}\n - - ")
                type_pattern = re.compile(r'(?<=\ntype: )(.*?)(?=\nlead_image:)', re.DOTALL)
                type_match = type_pattern.search(recipe_content)
                if type_match:
                    type_content = type_match.group(1)
                    print(f"type_content: {type_content} < pre {label}")
                    type_content = add_remove_label(label, type_content, add)
                    # type_content = type_content.replace(label, '')                    
                    # type_content = re.sub(r'^\s*,\s*\b', ' ', type_content)         # remove leading comma
                    # type_content = re.sub(r'(\s*,\s*,\s*)', ', ', type_content)     # remove label1, ,label2
                    #type_content = re.sub(r'\b\s*,\s*\\', '\\\\', type_content)         # remove trailing comma
                    print(f"type_content: {type_content} < post")
                    recipe_content = recipe_content[:type_match.start(1)] + type_content + recipe_content[type_match.end(1):]
                    print(recipe_content)
                    print('- - - - \n\n')
                content = content[:match.start(1)] + recipe_content + content[match.end(1):]
        new_path = Path('./',file.name)
        #with open(new_path, 'w') as f:
        with open(file, 'w') as f:
            f.write(content)




# to go from (passed to server from JS webIF)
# incorrect_label_with_list
# { 'dessert':['salad & chermoula stock','roast lamb couscous','burger salad','cavolo nero cm',
#              'avocado & fishstick cm','avocado & grape salad','fishsticks & cucumber yogurt',
#              'beetroot humous yogurt dip','chicken liver & avocado pate'] }

# to
# label = 'dessert'
# remove_dict = {
#     'y425':['salad & chermoula stock'],
#     'y429':['roast lamb couscous'],
#     'y430':['burger salad'],
#     'y441':['cavolo nero cm','avocado & fishstick cm','avocado & grape salad'],
#     'y442':['fishsticks & cucumber yogurt','beetroot humous yogurt dip'],
#     'y443':['chicken liver & avocado pate']
# }

# use - scan through atomic_LUT[rcp_name]['txtfile_short'][0] to get nutridoc ID
# from food_sets import atomic_LUT
#atomic_LUT['mixed omelette & parma']['txtfile_short'][0] returns 'y444'

remove_dict = {}
label = list(incorrect_label_with_list.keys())[0]
for ri_name in incorrect_label_with_list[label]:
    if ri_name not in atomic_LUT: continue
    print(f'\n{ri_name}')
    pprint(atomic_LUT[ri_name])
    nutri_doc_id = atomic_LUT[ri_name]['txtfile_short'][0]
    if nutri_doc_id in remove_dict.keys():
        remove_dict[nutri_doc_id].append(ri_name)
    else:
        remove_dict[nutri_doc_id] = [ri_name]


# to go to filenames instead of ID to get corrections_dict
corrections_dict = {}
for nut_id, rcp_list in remove_dict.items():
    corrections_dict[file_LUT_v2[nut_id]] = rcp_list
    
# label = 'dessert'
# corrections_dict= {
#     PosixPath('./y965_NUTRITEST_recipes_20190719-01.rtf'):['salad & chermoula stock'],
#     PosixPath('./y970_NUTRITEST_recipes_20191109-22.rtf'):['roast lamb couscous'],
#     PosixPath('./y970_NUTRITEST_recipes_20191109-22.rtf'):['burger salad'],
#     PosixPath('./y970_NUTRITEST_recipes_20191109-22.rtf'):['cavolo nero cm','avocado & fishstick cm','avocado & grape salad'],
#     PosixPath('./y970_NUTRITEST_recipes_20191109-22.rtf'):['fishsticks & cucumber yogurt','beetroot humous yogurt dip'],
#     PosixPath('./y970_NUTRITEST_recipes_20191109-22.rtf'):['chicken liver & avocado pate']
# }


for f, rcp_list in corrections_dict.items():
    print(f"\n{f.name} - {rcp_list}")
print(f"\nRemoving label: {label}")
print('\n\n')

if opt_dict['edit_docs_live']:
    print(f"\n\n* * * * * * * * * *\n\nTHIS IS LIVE AND WILL EDIT\n{nutridocs_base_dir}\n                                                     ^ ^ ^\n* * * * * * * * * *\n\n")
    #remove_labels_v4(label, corrections_dict)
    edit_nutridoc_labels(label, corrections_dict, opt_dict['add_labels'])
else:
    print("\n\n* * * WARNING NO EDITS WERE MADE * * *\n")
    print('Option -l   For live run to edit docs')

if not opt_dict['backup_docs']:
    print("\n\n* * * WARNING NO BACKUPS WERE MADE * * *\n")
    
print(f"Run process_nutridocs.py update with:\n\n\t{list( remove_dict.keys() )}\n")






# Does generative AI mean you no longer need to save code? (or anything that can be generated?)
# Is it the end of libraries?
# Will generative AI produce so much data it's:
#     either imposible to store everying 
#     or it meaningless to store evrything since it can be generated at will anyway?

# Generated data is non deterministic, so this means that although the jist of functionality may be there
# it may vary subtly.

# This variation maybe better - innovative.

# So a framework for assessing newly generated content in comparison to presedents 
# would be useful to determine progress or novelty.

# In an engineering /  scientific setting this would be valuable.
