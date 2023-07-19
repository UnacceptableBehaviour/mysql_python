#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
from pprint import pprint
from pathlib import Path
import shutil
import os

import time     # sleep()
from timestamping import hr_readable_from_nix, nix_time_ms

from product_info import ProductInfo

from food_sets import atomic_LUT
from food_sets import follow_alias 
import json # JSONDecodeError

import atexit           

from scrape_tests import tests, urls_to_process_all_dict
# pprint(tests['https://www.waitrose.com/ecom/products/essential-chicken-thighs-skin-on-bone-in/519514-707754-707755'])
# print('\n|\n|\n|\n')
# pprint(urls_to_process_all_dict['ocd'])
# print('\n|\n|\n|\n')

# missing ingreidient list sources
# from food_sets import OTS_INGREDIENTS_FOUND # check format is compatible and integrate it into items to scrape
MISSING_INGREDIENTS_FILE_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB.json')
MISSING_INGREDIENTS_FILE_JSON_CCM = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB_CCM.json')
MISSING_INGREDIENTS_FILE_JSON_PY = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_PY.json')
# in progress - interrupted
URL_CACHE_STILL_TO_PROCESS_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_URL_TO_PROCESS.json')

MI_FILES = {'-c': MISSING_INGREDIENTS_FILE_JSON,          # cost_menu.rb
            '-d': MISSING_INGREDIENTS_FILE_JSON_CCM,      # DTK web interface: ccm_nutridoc_web.rb
            '-p': MISSING_INGREDIENTS_FILE_JSON_PY,       # process_nutridocs.py 
            '-m': URL_CACHE_STILL_TO_PROCESS_JSON         # compiled list, interupted while processing
            }            

# target
NUTRIENT_FILE_PATH = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info.txt')
NUTRINFO_BACKUP_DIR = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_bak')
URL_CACHE_ALREADY_RETRIEVED_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_URL_CACHE.json')

url_cache = {}
if URL_CACHE_ALREADY_RETRIEVED_JSON.exists():
    try:
        with open(URL_CACHE_ALREADY_RETRIEVED_JSON, 'r') as f:
            url_cache = json.load(f)
    except json.decoder.JSONDecodeError:
        print(f"\n\n\n\n\n\n\n* * * * WARNING * * * * Error loading URL cache {URL_CACHE_ALREADY_RETRIEVED_JSON.name}\n\n\n\n\n\n\n")
        url_cache = {}
        # TODO - L delete corrupt file?

def save_url_CACHE():
    with open(URL_CACHE_ALREADY_RETRIEVED_JSON, 'w') as f:
        json.dump(url_cache, f)

atexit.register(save_url_CACHE)


missing_items_to_process = {}
def save_urls_still_to_process():
    with open(URL_CACHE_STILL_TO_PROCESS_JSON, 'w') as f:
        json.dump(missing_items_to_process, f)


def backup_file_with_nix_timestamp(file_path, backup_dir=NUTRINFO_BACKUP_DIR):
    nutri_file = Path(file_path).name
    nix_t = nix_time_ms()
    backup_name = f"{hr_readable_from_nix(nix_t).replace(' ','_')}_{nix_t}_{nutri_file}"
    bu_target = backup_dir.joinpath(backup_name)
    try:
        shutil.copyfile(file_path, bu_target)
        print(f"\n\nBACKED UP {file_path.name} to:\n{bu_target}\n")
    except Exception as e: # TODO - H remove ALL
        print(f"\n\n* * * WARNING * * *\n\nBackup failed: {bu_target}\n")
        print(e)
        print("* * * WARNING * * *\n\n")

    return (bu_target)


def get_outstanding_urls_to_process_from_atomicLUT():
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
    
    for ri_name in atomic_LUT:  # TODO return a match if its OTS & has NO INGREDIENTS
        url = atomic_LUT[ri_name]['url']
        if url:
            if atomic_LUT[ri_name]['ingredients'] == '__igdts__':
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

    print()
    for source in dict_of_urls_to_process:
        print(f"S: {str(source).rjust(10)} [{len(dict_of_urls_to_process[source])}]")

    return dict_of_urls_to_process

CACHED_NUTRINFO_ENTRIES = {}
def build_cached_nutrinfo_entries(): # removes duplicate entries from file.
    print("- - - Building: CACHED_NUTRINFO_ENTRIES:")
    duplicates = 0
    content = ''
    with NUTRIENT_FILE_PATH.open('r') as f:
        #content = f.readlines()
        content = f.read()
    
    content_copy = content

    for m in re.finditer( r'------------------ for the nutrition information(.*?)\((.*?)\).*?ingredients:(.*?)$.*?igdt_type:(.*?)$', content, re.MULTILINE | re.DOTALL ):
        component, ndb_no_url_alias, ingredients, igdt_type = m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()
        if component == '': continue
        
        component_match_string = m.group(0)
        
        if component in CACHED_NUTRINFO_ENTRIES:
            duplicates += 1
            if CACHED_NUTRINFO_ENTRIES[component] == component_match_string:
                print(f"\nDuplicate found: [{component}] removing item")
                content_copy = content_copy.replace(component_match_string, '', 1)
            else:
                print(f"\nDuplicate found: [{component}]\n{CACHED_NUTRINFO_ENTRIES[component]}\n{component_match_string}\n\n")
        else:
            CACHED_NUTRINFO_ENTRIES[component] = component_match_string

    print(f"- - - Finished Building: CACHED_NUTRINFO_ENTRIES: [{len(CACHED_NUTRINFO_ENTRIES)}] entries. [{duplicates}] duplicates found")

    with open(NUTRIENT_FILE_PATH, 'w') as f:
        f.write(content_copy)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def scrub_found(items_to_scrub):
    if items_to_scrub == None: return
    # if atomic_LUT[i] elements are the following, then they are also STILL TO FIND
    #  'igdt_type': 'ots',
    #  'ingredients': '__igdts__',
    copy_of_urls_to_process = dict(items_to_scrub)

    for i_still_to_process in copy_of_urls_to_process:        
        if i_still_to_process in atomic_LUT.keys():
            if (atomic_LUT[i_still_to_process]['igdt_type'] == 'ots') and (atomic_LUT[i_still_to_process]['ingredients'] == '__igdts__'):
                print(f"> - - - [{i_still_to_process}] STILL TO FIND") # pull info from net
            else:
                print(f"> - - - [{i_still_to_process}] FOUND")
                del items_to_scrub[i_still_to_process]
        else:
            print(f"> - - - [{i_still_to_process}] STILL TO FIND")

    copy_of_urls_to_process = None


def get_url_from_atomic_LUT(i):
    if (i in atomic_LUT) and (atomic_LUT[i]['url']):        # i has url
        return {atomic_LUT[i]['url']}
    
    if i in atomic_LUT:                                     # see if alias has url
        a = follow_alias(i)
        if a and (a in atomic_LUT):
            if 'url' in atomic_LUT[a].keys():
                return atomic_LUT[a]['url']
                
    return ''


def show_list(title, i_dict):
    i_width = 40
    t_width = 80
    print(f"- {title} -".center(t_width,'-'))
    url_updates = {}
    if i_dict:
        for i,url in i_dict.items():            
            if not url:                
                url = get_url_from_atomic_LUT(i)
                url_updates[i] = url

            print(f"{i.rjust(i_width)}  [{url}]")
    i_dict.update(url_updates)
    print(f"- {len(url_updates)} updates -".center(t_width,'-'))

def open_search_in_browser_get_url_from_user(name):
    product_url = None

    if ('sbs' in name) or ('sainsburys' in name):
        search_for = name.replace(' ','%20').replace('sbs','').replace('sainsburys','').strip()
        search_url = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{search_for}"

    elif ('tsc' in name) or ('tesco' in name):
        search_for = name.replace(' ','%20').replace('tsc','').replace('tesco','').strip()
        search_url = f"https://www.tesco.com/groceries/en-GB/search?query={search_for}"

    elif ('ald' in name) or ('aldi' in name):
        search_for = name.replace(' ','+').replace('ald','').replace('aldi','').strip()
        search_url = f"https://groceries.aldi.co.uk/en-GB/Search?keywords={search_for}"

    elif ('asd' in name) or ('asda' in name):
        search_for = name.replace(' ','%20').replace('asd','').replace('asda','').strip()
        search_url = f"https://groceries.asda.com/search/{search_for}"

    elif ('wtr' in name) or ('waitrose' in name):
        search_for = name.replace(' ','%20').replace('wtr','').replace('waitrose','').strip()
        search_url = f"https://www.waitrose.com/ecom/shop/search?&searchTerm={search_for}"

    else:
        search_for = name.replace(' ','%20')
        #default = f"https://www.tesco.com/groceries/en-GB/search?query={search_for}"
        search_url = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{search_for}"

    os.system(f'open {search_url}')
    url_or_return = input(f'Enter URL for item "{name}"?\n- Ret to skip\n')
    if 'http' in url_or_return: product_url = url_or_return

    return product_url

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

help_info = '''
> scrape.py -a                 # scan z_product_nutrition_info.txt for missing i_list / url
                                    # scrape & fill in details on prompt
> 
> scrape.py -a -noprompt       # scan z_product_nutrition_info.txt for missing i_list / url
                                    # scrape & fill in details - DON'T ASK PERMISSION
                                    #
                                    # backup of z_product_nutrition_info.txt in
                                    # '''+str(NUTRINFO_BACKUP_DIR)+'''

> scrape.py                    # take missing ingredients generated by cost_menu.rb, process_nutridocs.py, & DTK web
                                    # scrape & fill in details on prompt

                               # if any of -c, -d, -p are present EXCLUDE thos that aren't in the options
> scrape.py -c                 # process cost_menu.rb missing ONLY 
> scrape.py -d                 # process ccm_nutridoc_web.rb missing ONLY (DTK web interface)
> scrape.py -p                 # process process_nutridocs.py missing ONLY
> scrape.py -c -d              # process cost_menu.rb & ccm_nutridoc_web.rb missing ONLY


-noprompt                           # don't ask - works with all options                                    
                                                                                                            
> scrape.py -u                 # go through debug list of items instead
'''


if __name__ == '__main__':
    if ('-h' in sys.argv) or ('--h' in sys.argv) or ('-help' in sys.argv) or ('--help' in sys.argv):
        print(help_info)
        sys.exit(0)

    opt_no_prompt = False

    backup_file_with_nix_timestamp(NUTRIENT_FILE_PATH)    

    build_cached_nutrinfo_entries() # and remove duplicate entries
        

    # - - process lists created by cost_menu.rb, process_nutridocs.py and DTK

    # look for -c -d -p option in argv
    common_keys = set(MI_FILES.keys()).intersection(set(sys.argv))
    if len(common_keys) == 0:
        common_keys = set(MI_FILES.keys())
        # don't ovewrite saved keys if only doing single set of keys
        atexit.register(save_urls_still_to_process) # otherwise save unprocessed if theres a crash
    
    for key in common_keys: 
        fname = MI_FILES[key]

        try:
            if fname.exists():
                with open(fname, 'r') as f:            
                    content = json.load(f)
                    print(f"LOADED JSON: {fname} [{len(content)}]")

        except json.decoder.JSONDecodeError:
            print(f"ERROR decoding: {fname.name} . . Deleting.")
            Path.unlink(fname)
        except Exception as e: # TODO - remove
            pprint(e)
            print(e.__traceback__)
        
        show_list(fname.name, content)
        
        # Keep them
        for key, value in content.items():
            if key not in missing_items_to_process:
                missing_items_to_process[key] = value

        # ** unpack dict
        # creat new dict from 2 {**d1, **d2}
        # dict comprehension {key: value for key, value in new_content.items() if key not in missing_items_to_process}
        # one liner version:
        # missing_items_to_process = {**missing_items_to_process, **{key: value for key, value in new_content.items() if key not in missing_items_to_process}}


    scrub_found(missing_items_to_process)
    show_list('missing_items_to_process', missing_items_to_process)
     

    # if its in the aLUT scrape info and insert it into the nutridoc    
    # if not in aLUT scrape info insert it into template and add it to end of nutridoc

    if '-noprompt' in sys.argv:
        opt_no_prompt = True

    if '-u' in sys.argv:  # problem URLS to test against
    #if True: # debugger

        missing_items_to_process = {#'asd es multigrain sliced bread': 'https://groceries.asda.com/product/seeded-grains-bread/asda-extra-special-multigrain-sliced-loaf/1000383113960',
                            'tsc cooked beetroot': 'https://www.tesco.com/groceries/en-GB/products/261808728',
                            'flying pigs': 'https://www.sainsburys.co.uk/gol-ui/product/mr-porky-original-pork-scratchings-65g',                        
                            'ald salt & pepper calamari': 'https://groceries.aldi.co.uk/en-GB/p-the-fishmonger-salt-pepper-calamari-225g/4088600518596',
                            'thick smoked back bacon': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-thick-smoked-bacon-rashers-x6-300g',
                            'aunties sticky toffee pudding': 'https://www.sainsburys.co.uk/gol-ui/product/auntys-sticky-toffee-puddings-200g',
                            'sbs roast beef': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-roast-beef-130g',
                            'breaded ham': 'https://groceries.asda.com/product/ham-pork-slices/asda-10-slices-breaded-ham/910003011020',
                            'champagne': 'https://groceries.asda.com/product/champagne/moet-chandon-imperial-brut-champagne/33171',
                            'cooked thick smoked back bacon': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-thick-smoked-bacon-rashers-x6-300g',
                            'cracker': 'https://groceries.asda.com/product/cream-crackers/asda-rosemary-crackers/1000311822923',                        
                            'haagen-dazs strawberry cheesecake ice cream': 'https://www.sainsburys.co.uk/gol-ui/product/h%C3%A4agen-dazs-ice-cream-strawberry-cheesecake-460ml',
                            'lemon tart w pistachio icecream': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-tarte-au-citron--taste-the-difference-500g',
                            'lindt salted caramel chocolate': 'https://www.sainsburys.co.uk/gol-ui/product/lindt-lindor-salted-caramel-200g',
                            'niknaks': 'https://www.sainsburys.co.uk/gol-ui/product/nik-naks-nice-spicy-crisps-6pk',
                            'red food colouring': 'https://www.tesco.com/groceries/en-GB/products/313749125',
                            'red lentils': 'https://www.sainsburys.co.uk/gol-ui/product/ktc-red-lentils-1kg',
                            'red wine vinegar': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-wine-vinegar--red-wine-500ml',
                            'sbs ancient grain pave': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-ancient-grain-pave-taste-the-difference-400g',
                            'sbs pastry twist': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-cheddar-cheese-twists-125g',
                            'sbs pepperoni': 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-pepperoni-sampling-pack-42g',
                            'sweet chilli sauce': 'https://www.sainsburys.co.uk/gol-ui/product/blue-dragon-original-thai-sweet-chilli-sauce-380g-6529621-p',                        
                            '':'https://www.sainsburys.co.uk/gol-ui/product/activia-bio-yogurt-strawberry-4x125g', # come up ZERO energy but OK other!? Split tabel issue?
                            }       

        print('= = = Running scrape tests = = =')

    elif '-a' in sys.argv: # use atomicLUT as source        
        utp = get_outstanding_urls_to_process_from_atomicLUT()
        # S: sainsburys [259]
        # S:      tesco [4]
        # S:  morrisons [28]
        # S:       asda [3]
        for ri_name, url in utp['morrisons']:   # TODO - H set to all or allow passing arg to specify
            missing_items_to_process[ri_name] = url

    else:
        # BUILD list URLS for missing items
        for name,url in missing_items_to_process.items():
            print(f"name:{name} - url:[{url}]")
            if (url == 'skip'): continue                    # derived don't need url
            if url: continue                                # already have URL

            url = get_url_from_atomic_LUT(name)
            if url:
                missing_items_to_process[name] = url
            
            else: # ask user
                product_url = open_search_in_browser_get_url_from_user(name)
                
                if product_url == None: 
                    missing_items_to_process[name] = 'skip'
                    continue
                
                missing_items_to_process[name] = product_url
                
        print('missing_items_to_process: - - - S')
        pprint(missing_items_to_process)
        print('missing_items_to_process: - - - E')
        with open(URL_CACHE_STILL_TO_PROCESS_JSON, 'w') as f:
            json.dump(missing_items_to_process, f)


    # lets process . . . 
    # cache entries in url_cache save cache to disc
    for name,product_url in missing_items_to_process.items():        
        if product_url == 'skip': continue

        item = None

        while True:
            if opt_no_prompt:
                time.sleep(0.1) # be polite don't hammer the server

            print('- - - url - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \ ')
            print(product_url)
            print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - / ')        

            if not opt_no_prompt:
                yn = input(f'FIND info for "{name}"? y/n \n- n to skip\n- s to open browser get another url\nRET to get info\n')
                
                if str(yn).lower() == 'n': break
                if 'http' in yn: product_url = yn
                if 's' == yn.strip(): # get url from web
                    product_url = open_search_in_browser_get_url_from_user(name)
                    if product_url == None: break

            igdt_type = 'ots'    # default
            if name in atomic_LUT:
                print('- - - atomic? - S')
                pprint(atomic_LUT[name])                
                igdt_type = atomic_LUT[name]['igdt_type']
                print('- - - atomic? - E')

            print(f"Getting [{name}][{igdt_type}] from: {product_url}")
            if product_url == None: break

            # TODO H - check cache to see if already retrieved
            item = ProductInfo(name, product_url, igdt_type)        
            nutrinfo_text = item.nutrinfo_str()

            print('- - FOUND - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
            print(item)
            print('- - - - - - - - -')
            print(nutrinfo_text)
            print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')        

            if (item.nutrition_info['energy'] != 0) or opt_no_prompt: break

        if item:
            if not opt_no_prompt:
                yn = input(f"SAVE info for > {item.ri_name} <? y/n - n to skip\nRET to SAVE\n")
            else:
                yn = ''      

            if str(yn).lower() == '' and (item.nutrition_info['energy'] != 0):            
                # TODO H - cache ProductInfo to disc using url as key
                # store info in json {url: item}
                with open(URL_CACHE_ALREADY_RETRIEVED_JSON, 'w') as f:
                    url_cache[item.product_url] = json.dumps(str(item))
                    f.write(json.dumps(url_cache))
 
                with open(NUTRIENT_FILE_PATH, 'r') as f:
                    content = f.read()
                
                if name in atomic_LUT:
                    target_rcp = CACHED_NUTRINFO_ENTRIES[name]
                    content = content.replace(target_rcp, nutrinfo_text, 1)
                    print(f"\n\n== ri_name: {name}\n---\n{target_rcp}\n---\n")

                else: # new ingredient
                    insert_nutridata = '__insert_from_food_scrape__\n\n' + nutrinfo_text
                    content = content.replace('__insert_from_food_scrape__', insert_nutridata)
                
                with open(NUTRIENT_FILE_PATH, 'w') as f:
                    f.write(content)

            item = None
            nutrinfo_text = '__blank__'


# # > = = = = Using expected conditions to wait for cookie popup
# 
# #from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# #from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException
# 
# driver = webdriver.Firefox()
# driver.get("url")
# delay_in_seconds = 3
# allow_cookies_btn_id = 'onetrust-accept-btn-handler'
# try:
#     myElem = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.ID, allow_cookies_btn_id)))
#     print("Page is ready!")
# except TimeoutException:
#     print("Loading took too much time!")
#     
# # > = = = =    
#             
    
    # case 1: https://www.sainsburys.co.uk/gol-ui/product/sainsburys-italian-milano-salami-slices-86g
    # <h3 class="productDataItemHeader">Ingredients</h3>    XPATH
    # next sibling
    # <div class="productText">     < not unique
    #     <p></p>
    #     <p><strong>INGREDIENTS:</strong>Pork, Salt, Sugar, Dextrose, White Pepper, Antioxidant: Sodium Ascorbate;&nbsp;Garlic, Preservatives: Potassium Nitrate, Sodium Nitrite.</p><p></p>
    #     <p>Packaged in a protective atmosphere</p>
    # </div>
    
    # https://stackoverflow.com/questions/23887592/find-next-sibling-element-in-selenium-python
    # ^ uses JS - passing webelement and 
    
    # >>> driver.find_elements(By.XPATH, "//h3[contains(text(),'Ingredients')]")[0].text
    # 'Ingredients'
    # driver.find_element(By.XPATH, "//h3[contains(text(),'Ingredients')]").text
    # 'Ingredients'
    # driver.find_element(By.XPATH, "//h3[contains(text(),'Ingredients')]/following-sibling::div")
    # >>> driver.find_element(By.XPATH, "//h3[contains(text(),'Ingredients')]/following-sibling::div").text
    # 'INGREDIENTS:Pork, Salt, Sugar, Dextrose, White Pepper, Antioxidant: Sodium Ascorbate; Garlic, Preservatives: Potassium Nitrate, Sodium Nitrite.\nPackaged in a protective atmosphere'


    
    
    #case 2: https://www.sainsburys.co.uk/gol-ui/product/flying-goose-brand-sriracha-hot-chilli-sauce-455ml
    #
    # ---- ingredients
    # <div class="longTextItems">
    # <h3 class="itemHeader">Ingredients</h3>
    #     <ul class="productIngredients">               <- CSS '.productIngredients' driver.find_element(By.CSS_SELECTOR,'.productIngredients').text()
    #         <li>Chilli 70%, </li>
    #         <li>Sugar Syrup, </li>
    #         <li>Salt, </li>
    #         <li>Water, </li>
    #         <li>Flavour Enhancer: E621, </li>
    #         <li>Acids: E260, E330, </li>
    #         <li>Stabilizer: E415, </li>
    #         <li>Preservative: E202</li>
    #     </ul>
    # </div>
    
    # driver.find_element(By.CSS_SELECTOR,'.productIngredients').text
    # 'Chilli 70%, Sugar Syrup, Salt, Water, Flavour Enhancer: E621, Acids: E260, E330, Stabilizer: E415, Preservative: E202'

    # ---- ri_name - item
    # <h1 class="pd__header" data-test-id="pd-product-title">Flying Goose Brand Sriracha Hot Chilli Sauce 455ml</h1>
    
    # >>> driver.find_elements(By.CSS_SELECTOR,'.pd__header')
    # [<selenium.webdriver.remote.webelement.WebElement (session="f0c9bc5e7e6e8a1d8c45382f74f2d41a", element="b4c0b3a0-490a-4d9b-910a-ee133d3973ef")>]
    # ONLY ONE - 
    # 
    # >>> driver.find_element(By.CSS_SELECTOR,'.pd__header').text
    # 'Flying Goose Brand Sriracha Hot Chilli Sauce 455ml'
    
    
    
    
    #
    # coop - coop mini garlic naan 
    # https://shop.coop.co.uk/product/987eb538-1b3d-4fe9-948b-ee2acff7f44b
    #
    # japan centre
    # https://www.japancentre.com/en/products/3000-tokon-seaweed-salad-mix
    


# REFS
# Quick setup video for osx Catalina: https://www.youtube.com/watch?v=7R5n0sNSza
# activate venv
# pip install selenium
# install ChromeDriver: https://chromedriver.chromium.org/downloads (I installed 107)
#   % cd /Users/simon/Downloads 
#   % mv chromedriver /usr/local/bin
#   navigated to it and Rclick open it to get it to run
#   Starting ChromeDriver 107.0.5304.62 (1eec40d3a5764881c92085aaee66d25075c159aa-refs/branch-heads/5304@{#942}) on port 9515
#   Only local connections are allowed.
#   Please see https://chromedriver.chromium.org/security-considerations for suggestions on keeping ChromeDriver safe.
#   ChromeDriver was started successfully.
#   Seems OK DBL clicking
#   USE following to over ride the dev verification warning
#   xattr -d com.apple.quarantine /usr/local/bin/chromedriver
#
# On Chrome version change an update to chromedriver will be required:
# install ChromeDriver: https://chromedriver.chromium.org/downloads (I installed 111)
#   download relevant zip chromedriver_mac64.zip renamed chromedriver_mac64_111.zip
#   dblClick to extract
#   % cd /Users/simon/Downloads/chromedriver_mac64_111
#   % mv chromedriver /usr/local/bin/chromedriver                 # overwrite current version (107)
#   % xattr -d com.apple.quarantine /usr/local/bin/chromedriver   # overs OS warning
#   % run script as before!
#
# Selenium Hello World
# https://www.browserstack.com/guide/locators-in-selenium
# https://www.browserstack.com/guide/get-html-source-of-web-element-in-selenium-webdriver

# To run interactive:
# open python and load driver
# % python
# uncommment & paste in interactive shell:
# - -
# from pprint import pprint
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# 
# # for expected conditions
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# driver = webdriver.Chrome('chromedriver')
# driver.get('https://www.sainsburys.co.uk/gol-ui/product/flying-goose-brand-sriracha-hot-chilli-sauce-455ml')
# driver.get('https://www.sainsburys.co.uk/gol-ui/product/sainsburys-italian-milano-salami-slices-86g')
# - -
# click cookie button
# test calls!

# Selectors
# Selenium Docs - https://selenium-python.readthedocs.io/
# API basic - https://selenium-python.readthedocs.io/locating-elements.html#locating-elements-by-css-selectors
# More useful examples
# https://www.guru99.com/locators-in-selenium-ide.html
# https://code.tutsplus.com/tutorials/the-30-css-selectors-you-must-memorize--net-16048
# children, sibling dynamically created id
# https://devqa.io/selenium-css-selectors/

# Selenium - WebElement interface
# https://www.selenium.dev/
# https://www.selenium.dev/documentation/webdriver/elements/



# Experimets - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# ID = "id"
# NAME = "name"
# XPATH = "xpath"
# LINK_TEXT = "link text"
# PARTIAL_LINK_TEXT = "partial link text"
# TAG_NAME = "tag name"
# CLASS_NAME = "class name"
# CSS_SELECTOR = "css selector"
#
# Element to wait for
# depending on product could be either
# <h3 class="itemHeader">Ingredients</h3>
# <h3 class="productDataItemHeader">Ingredients</h3>
# h3 with text content 'Ingredients'

# xpaths
# follow h3 Ingredients
# //*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div/section[2]/ul/li[1]/div[2]/div/div/productcontent/htmlcontent/div[3]/p[2]
# //*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div/section[2]/ul/li[1]/div[2]/div/div/productcontent/htmlcontent/div[4]/p[2]
# 
# //*[@id="mainPart"]/div[3]/div/div/ul
# //*[@id="mainPart"]/div[3]/div/div/ul

# //*[ contains (text(), 'Ingredients' ) ]
# ID
# WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.ID, allow_cookies_btn_id)))
# XPATH
# WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.XPATH, "//*[ contains (text(), 'Ingredients' ) ]")))
# driver.find_elements(By.LINK_TEXT, "Ingredients") # nothing!
# driver.find_element(By.LINK_TEXT, "Ingredients") # nothing!
# driver.find_element(By.XPATH, "//*[ contains (text(), 'Ingredients' ) ]"))    # element w/ text

# driver.find_element(By.CSS_SELECTOR, "Ingredients") # nothing!
# driver.find_elements(By.CSS_SELECTOR, 'h3:contains("^ab$")')        # Message: invalid selector: An invalid or illegal selector was specified
# driver.find_elements(By.CSS_SELECTOR, 'h3:contains("Ingredients")') # Message: invalid selector: An invalid or illegal selector was specified
# :contains() pseudo class deprecated CSS3 https://saucelabs.com/resources/articles/selenium-tips-css-selectors
# driver.find_elements(By.CSS_SELECTOR, "h3:contains('Ingredients')") # Message: invalid selector: An invalid or illegal selector was specified
# driver.find_elements(By.CSS_SELECTOR, "h3[text='Ingredients']")     # returns []
# driver.find_elements(By.CSS_SELECTOR, 'h3.productDataItemHeader')   # returns [e1, e2. . .] e = <selenium.webdriver.remote.webelement.WebElement (session="2d914c403b343e929ad84c84ada411f7", element="a32d21a9-e4f0-4936-ac2d-87c07a14f834")>
#
# pprint(driver.find_elements(By.CSS_SELECTOR, "h3.productDataItemHeader")[2].text)                 # 'Ingredients'
# pprint(driver.find_elements(By.CSS_SELECTOR, "h3.productDataItemHeader[text='Ingredients']"))     # []

