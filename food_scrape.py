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
from food_sets import get_exploded_ingredients_and_components_for_DB_from_name
import json

# missing ingreidient list sources
from food_sets import OTS_INGREDIENTS_FOUND # check format is compatible and integrate it into items to scrape
MISSING_INGREDIENTS_FILE_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB.json')
MISSING_INGREDIENTS_FILE_JSON_CCM = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB_CCM.json')
MISSING_INGREDIENTS_FILE_JSON_PY = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_PY.json')
MI_FILES = [MISSING_INGREDIENTS_FILE_JSON,
            MISSING_INGREDIENTS_FILE_JSON_CCM,
            MISSING_INGREDIENTS_FILE_JSON_PY,
            #OTS_INGREDIENTS_FOUND
            ]

MI_FILES = [MISSING_INGREDIENTS_FILE_JSON_PY]
            
# in progress - interrupted
URL_CACHE_STILL_TO_PROCESS_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_URL_TO_PROCESS.json')

# target
NUTRIENT_FILE_PATH = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info.txt')
NUTRINFO_BACKUP_DIR = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_bak')
URL_CACHE_ALREADY_RETRIEVED_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_URL_CACHE.json')

# url_cache = {}
# if URL_CACHE_ALREADY_RETRIEVED_JSON.exists():
#     with open(URL_CACHE_ALREADY_RETRIEVED_JSON, 'r') as f:
#         content = f.read()
#         url_cache = json.loads(content)

def backup_file_with_nix_timestamp(file_path, backup_dir=NUTRINFO_BACKUP_DIR):
    nutri_file = Path(file_path).name
    nix_t = nix_time_ms()
    backup_name = f"{hr_readable_from_nix(nix_t).replace(' ','_')}_{nix_t}_{nutri_file}"
    bu_target = backup_dir.joinpath(backup_name)
    try:
        shutil.copyfile(file_path, bu_target)
        print(f"\n\nBACKED UP {file_path.name} to:\n{bu_target}\n")
    except Exception as e:
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
def build_cached_nutrinfo_entries():
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

help_info = '''
> food_scrape.py -a                 # scan z_product_nutrition_info.txt for missing i_list / url
                                    # scrape & fill in details on prompt
> 
> food_scrape.py -a -noprompt       # scan z_product_nutrition_info.txt for missing i_list / url
                                    # scrape & fill in details - DON'T ASK PERMISSION
                                    #
                                    # backup of z_product_nutrition_info.txt in
                                    # '''+str(NUTRINFO_BACKUP_DIR)+'''

> food_scrape.py                    # take missing ingredients generated by cost_menu.rb, process_nutridocs.py, & DTK web
                                    # scrape & fill in details on prompt

-noprompt                           # don't ask - works with all options                                    
                                                                                                            
> food_scrape.py -u                 # go through debug list of items instead
'''

if __name__ == '__main__':
    if ('-h' in sys.argv) or ('--h' in sys.argv) or ('-help' in sys.argv) or ('--help' in sys.argv):
        print(help_info)
        sys.exit(0)

    opt_no_prompt = False

    build_cached_nutrinfo_entries()

    backup_file_with_nix_timestamp(NUTRIENT_FILE_PATH)    

    # TODO - catch file corrupt exception
    urls_to_process = {}
    if URL_CACHE_STILL_TO_PROCESS_JSON.exists():
        with open(URL_CACHE_STILL_TO_PROCESS_JSON, 'r') as f:
            print(f"LOADING JSON: {URL_CACHE_STILL_TO_PROCESS_JSON}")
            urls_to_process = json.load(f)

    def scrub_found(items_to_scrub, is_list=False):
        # if atomic_LUT[i] elements are the following, then they are also STILL TO FIND
        #  'igdt_type': 'ots',
        #  'ingredients': '__igdts__',
        if is_list:
            copy_of_urls_to_process = list(items_to_scrub)
        else:
            copy_of_urls_to_process = dict(items_to_scrub)

        for i_still_to_process in copy_of_urls_to_process:        
            if i_still_to_process in atomic_LUT.keys():
                if (atomic_LUT[i_still_to_process]['igdt_type'] == 'ots') and (atomic_LUT[i_still_to_process]['ingredients'] == '__igdts__'):
                    print(f"> - - - [{i_still_to_process}] STILL TO FIND") # pull info from net
                else:
                    print(f"> - - - [{i_still_to_process}] FOUND")
                    if is_list:
                        items_to_scrub.remove(i_still_to_process)
                    else:
                        del items_to_scrub[i_still_to_process]
            else:
                print(f"> - - - [{i_still_to_process}] STILL TO FIND")

        copy_of_urls_to_process = None


    def url_w_tuple_string_listing(i):
        i_width = 40
        if (i in atomic_LUT) and (atomic_LUT[i]['url']):        # i has url
            return ({atomic_LUT[i]['url']}, f"{i.rjust(i_width)}  {atomic_LUT[i]['url']}")        
        
        if i in atomic_LUT:                                     # see if alias has url
            a = follow_alias(i)
            if a:
                if 'url' in atomic_LUT[a].keys():
                    a_url = atomic_LUT[a]['url']
                    i_and_a = f"{i}({a})"
                    return ({a_url}, f"{i_and_a.rjust(i_width)}  {a_url}")
                    
        return (None, f"{i.rjust(i_width)}  not in atomic_LUT")


    def show_list(title, i_list):
        print(f"- {title} -".center(80,'-'))
        for i in i_list:
            _, p = url_w_tuple_string_listing(i)
            print(p)    
        print(f"- {'O'} -".center(80,'-'))



    # - - - - load MISSING INGREDIENTS from JSON files
    scrub_found(urls_to_process)

    ingredents_to_find = []    

    # - - lists created by cost_menu.rb, process_nutridocs.py and DTK
    for fname in MI_FILES:
        with open(fname, 'r') as f:
            content = json.load(f)
        
        show_list(fname.name, content)
        ingredents_to_find = list(set(ingredents_to_find + content))

    show_list('ingredents_to_find', ingredents_to_find)

    scrub_found(ingredents_to_find, True) # True passing list

    show_list('ingredents_to_find', ingredents_to_find)
        

    # if its in the aLUT scrape info and insert it into the nutridoc    
    # if not in aLUT scrape info insert it into template and add it to end of nutridoc

    if '-noprompt' in sys.argv:
        opt_no_prompt = True

    if '-u' in sys.argv:  # problem URLS to test against
    #if True: # debugger
        # - - - - - - 
        # urls_to_process = [ 
        #                     ('kettle sea salt','https://www.sainsburys.co.uk/gol-ui/product/kettle-chips-sea-salt---balsamic-vinegar-150g'),
        #                     ('nik naks', 'https://www.sainsburys.co.uk/gol-ui/product/nik-naks-nice-spicy-crisps-6pk'),
        #                     ('hot cross buns','https://www.sainsburys.co.uk/gol-ui/product/sainsburys-fruity-hot-cross-buns--taste-the-difference-x4-280g'),
        #                     ('haggis','https://www.sainsburys.co.uk/gol-ui/product/macsween-traditional-haggis-454g'), 
        #                     ('crisps','https://www.sainsburys.co.uk/shop/gb/groceries/walkers-cheese---onion-crisps-6x25g'), 
        #                     ('veg stock cube','https://www.sainsburys.co.uk/shop/gb/groceries/knorr-stock-cubes--vegetable-x8-80g'),
        #                     ('actimel veg','https://www.sainsburys.co.uk/shop/gb/groceries/actimel-fruit-veg-cultured-shot-green-smoothie-6x100g-%28600g%29'),
        #                     ('beef monster munch','https://www.sainsburys.co.uk/shop/gb/groceries/monster-munch-roast-beef-x6-25g'),
        #                     ('wotsits','https://www.sainsburys.co.uk/shop/gb/groceries/walkers/walkers-wotsits-really-cheesy-crisp-snacks-36g'),
        #                     ]
        urls_to_process = [ #('kettle sea salt','https://www.sainsburys.co.uk/gol-ui/product/kettle-chips-sea-salt---balsamic-vinegar-150g'),
                            #('black turtle beans','https://www.tesco.com/groceries/en-GB/products/256530942'), # frist address
                            #('cheese & garlic flat bread','https://www.tesco.com/groceries/en-GB/products/288610223'),
                            #('tsc apple and raspberry juice','https://www.tesco.com/groceries/en-GB/products/278994762'),
                            #('bacon frazzles','https://www.tesco.com/groceries/en-GB/products/260085541'),
                            #('frazzles','https://www.tesco.com/groceries/en-GB/products/260085541'),
                            #('kikkoman soy sauce','https://www.tesco.com/groceries/en-GB/products/281865197'),
                            #('tsc soy sauce','https://www.tesco.com/groceries/en-GB/products/294781229'),
                            #('veg oil','https://www.tesco.com/groceries/en-GB/products/254918073'),
                            #('large medjool dates','https://www.tesco.com/groceries/en-GB/products/302676947'),                            
                            ('tsc roquefort','https://www.tesco.com/groceries/en-GB/products/277465578'),
                            ('anchovies','https://www.tesco.com/groceries/en-GB/products/310103367'),
                            ('salted cashews','https://www.tesco.com/groceries/en-GB/products/297385240'),    # NO NUTRITION TABLE - USE AS test case fall back on 
                            ('tsc smoked mackerel','https://www.tesco.com/groceries/en-GB/products/251631139'), # NUTRITION table has ug & mg in nutrition table
                            ('beaujolais villages','https://www.tesco.com/groceries/en-GB/products/252285938'),
                            ('tsc chicken roll','https://www.tesco.com/groceries/en-GB/products/299955420'),
                            ('pork ribs','https://www.tesco.com/groceries/en-GB/products/281085768'),
                            ('chicken stock cubes',''),
                            ('fish fingers','https://www.tesco.com/groceries/en-GB/products/302861814'),
                            ('',''),
                            ('',''),
                            ('',''),
                            ('',''),
                            ('',''),
                            #('smoked ham','https://groceries.aldi.co.uk/en-GB/p-cooked-smoked-ham-400g/5027951005828'), # horendous multiple products in single list: Cooked Ham Trimmings, Smoked Ham Trimmings, Peppered Ham Trimmings, Smoke Breaded Ham Trimmings & Honey Roasted Ham Trimmings Ingreadients back to back W/O punctuation!
                            ]
        # urls_to_process = [('mrs butterscotch crunch','https://groceries.morrisons.com/webshop/product/Border-Sweet-Memories-Butterscotch-Crunch/483706011'),
        #                    ('mrs chicken korma','https://groceries.morrisons.com/webshop/product/Morrisons-Takeaway-Chicken-Korma/299170011'),
        #                    ('70% choc','https://groceries.morrisons.com/webshop/product/Lindt-Excellence-70-Cocoa-Dark-Chocolate/115160011'),
        #                    ('clarified butter','https://groceries.morrisons.com/webshop/product/KTC-Pure-Butter-Ghee/233485011'),
        #                    ('condensed milk','https://groceries.morrisons.com/webshop/product/Carnation-Cook-with-Condensed-Milk/110802011'),
        #                    ('mature gouda','https://groceries.morrisons.com/webshop/product/Morrisons-The-Best-Mature-Old-Amsterdam-Gouda/416709011?from=search&param=mature%20gouda'),
        #                    ('hovis cracker','https://groceries.morrisons.com/webshop/product/Hovis-Crackers/289557011'),
        #                    ('diced chorizo','https://groceries.morrisons.com/webshop/product/Elpozo-Iberico-Chorizo-Ring/456216011'),
        #                    ('chorizo','https://groceries.morrisons.com/webshop/product/Elpozo-Iberico-Chorizo-Ring/456216011'),
        #                    ('clay oven garlic and coriander naan','https://groceries.morrisons.com/webshop/product/The-Clay-Oven-Bakery-Garlic--Coriander-Naan-Bread/336891011?param=naan&from=search'),
        #                    ('smoked mackerel fillet','https://groceries.morrisons.com/webshop/product/Morrisons-Smoked-Mackerel-Fillets/442534011'),
        #                    ('beetroot brioche bun','https://groceries.morrisons.com/webshop/product/Morrisons-The-Best-Beetroot-Brioche-Rolls-/427428011'),
        #                    ('mrs tikka masala sauce','https://groceries.morrisons.com/webshop/product/Morrisons-Tikka-Masala-Sauce/215269011'),
        #                    ('spanish goats cheese','https://groceries.morrisons.com/webshop/product/Morrisons-Somerset-Goats-Cheese/111950011'),
        #                    ('caramac buttons','https://groceries.morrisons.com/webshop/product/Caramac-Giant-Buttons/450664011?from=search&param=caramac'),
        #                    ('caramac','https://groceries.morrisons.com/webshop/product/Caramac-Giant-Buttons/450664011?from=search&param=caramac'),
        #                    ('cream cheese','https://groceries.morrisons.com/webshop/product/Philadelphia-Original-Soft-Cheese/251401011'),
        #                    ('pistachios','https://groceries.morrisons.com/webshop/product/Morrisons-Pistachios/120506011'),
        #                    ('pistachio nuts','https://groceries.morrisons.com/webshop/product/Morrisons-Pistachios/120506011'),
        #                    ('crunchie bar','https://groceries.morrisons.com/webshop/product/Cadbury-Crunchie-Chocolate-Bar-4-Pack/269519011'),
        #                    ('white bread','https://groceries.morrisons.com/webshop/product/Morrisons-White-Toastie-Loaf/217833011'),
        #                    ('hoisin sauce','https://groceries.morrisons.com/webshop/product/Flying-Goose-Hoisin-Sauce/387755011'),
        #                    ('giant mrs yorkshire pudding','https://groceries.morrisons.com/webshop/product/Morrisons-Giant-Yorkshire-Pudding/111374011'),
        #                    ('mrs beef stock cube as prepared','https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011'),
        #                    ('beef stock','https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011'),
        #                    ('mrs beef stock cube','https://groceries.morrisons.com/webshop/product/Morrisons-Beef-Stock-Cubes-12s/265316011'),
        #                    ('wholegrain mustard','https://groceries.morrisons.com/webshop/product/Morrisons-Wholegrain-Mustard/121390011'),
        #                    ('mrs veg samosa','https://groceries.morrisons.com/webshop/product/Morrisons-Indian-Takeaway-Vegetable-Samosas/114583011?from=search&param=samosa')],     
        # convert list tuple to dict
        urls_to_process = {item[0]: item[1] for item in urls_to_process}
        print('= = = Running scrape tests = = =')

    elif '-a' in sys.argv: # use atomicLUT as source        
        utp = get_outstanding_urls_to_process_from_atomicLUT()
        # S: sainsburys [259]
        # S:      tesco [4]
        # S:  morrisons [28]
        # S:       asda [3]
        for ri_name, url in utp['sainsburys']:
            urls_to_process[ri_name] = url

    else:
        # BUILD list URLS for missing items
        for i in ingredents_to_find:
            if i in urls_to_process.keys(): continue     # already have URL

            url, igdt_url_str = url_w_tuple_string_listing(i)
            if url:
                urls_to_process[i] = url
            else: # ask user
                search_for = i.replace(' ','%20')
                default = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{search_for}"
                os.system(f'open {default}')
                url = input(f'\nEnter URL for "{i}"? y/n - RET to skip\n')                
                if str(url).lower() == '': continue
                urls_to_process[i] = url
                print('urls_to_process: - - - S')
                pprint(urls_to_process)
                print('urls_to_process: - - - E')
                with open(URL_CACHE_STILL_TO_PROCESS_JSON, 'w') as f:
                    json.dump(urls_to_process, f)


    # lets process . . . 
    for name,url in urls_to_process.items():        
        
        item = None

        while True:
            if opt_no_prompt:
                time.sleep(0.1) # be polite don't hammer the server

            print('- - - url - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \ ')
            print(url)
            print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - / ')        
            
            #if url == '': continue

            if not opt_no_prompt:
                yn = input(f'FIND info for "{name}"? y/n \n- n to skip\nRET to get info\n')
                if str(yn).lower() == 'n': break
                if 'http' in yn: url = yn
                if 's' == yn:                     
                    # if 'sainsburys' in url:
                    #     search_for = name.replace(' ','%20')
                    #     sbs_search = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{search_for}"
                    # if 'tesco' in url:
                    #     search_for = name.replace(' ','%20')
                    #     tsc_search = f"https://www.tesco.com/groceries/en-GB/search?query={search_for}"
                    # if 'aldi' in url
                    #     search_for = name.replace(' ','+')
                    #     ald_search = f"https://groceries.aldi.co.uk/en-GB/Search?keywords={search_for}"                    
                    search_for = name.replace(' ','%20')
                    default = f"https://www.tesco.com/groceries/en-GB/search?query={search_for}"
                    os.system(f'open {default}')                

            igdt_type = 'atomic'    # default
            if name in atomic_LUT:
                igdt_type = atomic_LUT[name]['igdt_type']
            print(f"Getting [{name}][{igdt_type}] from: {url}")        
            item = ProductInfo(name, url, igdt_type)        
            nutrinfo_text = item.nutrinfo_str()

            print('- - FOUND - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
            print(item)
            print('- - - - - - - - -')
            print(nutrinfo_text)
            print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')        

            #if item['nutrition_info']['energy'] != 0: break
            #pprint(item)
            #pprint(item.nutrition_info['energy'])
            if (item.nutrition_info['energy'] != 0) or opt_no_prompt: break

        if item:
            if not opt_no_prompt:
                yn = input(f"SAVE info for > {item.ri_name} <? y/n - n to skip\nRET to SAVE\n")
            else:
                yn = ''                

            if str(yn).lower() == '' and (item.nutrition_info['energy'] != 0):            
                # with open(URL_CACHE_ALREADY_RETRIEVED_JSON, 'w') as f:
                #     url_cache[item.product_url] = json.dumps(str(item))
                #     f.write(json.dumps(url_cache))
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

