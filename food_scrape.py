#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
from pprint import pprint
from pathlib import Path
import shutil
import os

from timestamping import hr_readable_from_nix, nix_time_ms

from product_info import ProductInfo

from food_sets import atomic_LUT
from food_sets import follow_alias 
import json

# missing ingreidient list sources
MISSING_INGREDIENTS_FILE_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB.json')
MISSING_INGREDIENTS_FILE_JSON_CCM = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB_CCM.json')
MISSING_INGREDIENTS_FILE_JSON_PY = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_PY.json')
MI_FILES = [MISSING_INGREDIENTS_FILE_JSON,
            MISSING_INGREDIENTS_FILE_JSON_CCM,
            MISSING_INGREDIENTS_FILE_JSON_PY]

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
    
    for ri_name in atomic_LUT:
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


if __name__ == '__main__':

    backup_file_with_nix_timestamp(NUTRIENT_FILE_PATH)
    sys.exit(0)

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


    if '-u' in sys.argv:  # problem URLS to test against
        # - - - - - - 
        urls_to_process = [ ('kettle sea salt','https://www.sainsburys.co.uk/gol-ui/product/kettle-chips-sea-salt---balsamic-vinegar-150g'),
                            ('nik naks', 'https://www.sainsburys.co.uk/gol-ui/product/nik-naks-nice-spicy-crisps-6pk'),
                            ('hot cross buns','https://www.sainsburys.co.uk/gol-ui/product/sainsburys-fruity-hot-cross-buns--taste-the-difference-x4-280g')
                            ]
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
                search_url = i.replace(' ','%20')
                default = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{search_url}"
                os.system(f'open {default}')
                url = input(f'\nEnter URL for "{i}"? y/n - RET to skip\n')                
                if str(url).lower() == '': continue
                urls_to_process[i] = url
                print('urls_to_process: - - - S')
                pprint(urls_to_process)
                print('urls_to_process: - - - E')
                with open(URL_CACHE_STILL_TO_PROCESS_JSON, 'w') as f:
                    json.dump(urls_to_process, f)



    for name,url in urls_to_process.items():        
        
        print('- - - url - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \ ')
        print(url)
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - / ')        
        
        if url == '': continue

        yn = input(f'FIND info for "{name}"? y/n - RET to skip\n')
        if str(yn).lower() == 'n': sys.exit(0)
        if str(yn).lower() == '': continue

        print(f"Getting: {url}")        
        item = ProductInfo(name, url)        
        nutrinfo_text = item.nutrinfo_str()

        print('- - FOUND - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print(item)
        print('- - - - - - - - -')
        print(nutrinfo_text)
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')        

        if item:
            yn = input(f"SAVE info for > {item.ri_name} <? y/n - RET to skip\n")
            if str(yn).lower() == 'y':            
                # with open(URL_CACHE_ALREADY_RETRIEVED_JSON, 'w') as f:
                #     url_cache[item.product_url] = json.dumps(str(item))
                #     f.write(json.dumps(url_cache))
                
                with open(NUTRIENT_FILE_PATH, 'r') as f:
                    content = f.read()
                
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

