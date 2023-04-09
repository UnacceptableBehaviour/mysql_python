#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
from pprint import pprint
from pathlib import Path
import os

from product_info import ProductInfo

from food_sets import atomic_LUT
from food_sets import follow_alias 
import json



MISSING_INGREDIENTS_FILE_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB.json')
MISSING_INGREDIENTS_FILE_JSON_CCM = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB_CCM.json')
MISSING_INGREDIENTS_FILE_JSON_PY = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_PY.json')
NUTRIENT_FILE_PATH = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info.txt')
URL_CACHE_STILL_TO_PROCESS_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_URL_TO_PROCESS.json')
URL_CACHE_ALREADY_RETRIEVED_JSON = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_URL_CACHE.json')

url_cache = {}
if URL_CACHE_ALREADY_RETRIEVED_JSON.exists():
    with open(URL_CACHE_ALREADY_RETRIEVED_JSON, 'r') as f:
        content = f.read()
        url_cache = json.loads(content)

# TODO - catch file corrupt exception
urls_to_process = {}
if URL_CACHE_STILL_TO_PROCESS_JSON.exists():
    with open(URL_CACHE_STILL_TO_PROCESS_JSON, 'r') as f:
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
        print(f"i_still_to_process:{i_still_to_process}")
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

scrub_found(urls_to_process)

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




def main():
    pass

if __name__ == '__main__':

    ingredents_to_find = []    
    t1 = []
    t2 = []
    t3 = []
    # - - - - load MISSING INGREDIENTS from JSON files

    # - - list is created by cost_menu.rb
    # we want INGREDIENTS, NUTRITION & COST information for these items
    with open(MISSING_INGREDIENTS_FILE_JSON, 'r') as f:
        content = f.read()
        t1_cost = json.loads(content)

    # - - list is created by process_nutridocs.py
    # looking for ALLERGENS, nutrients NOT IMPORTANT because the ots ingredient has nutrition info
    # we want INGREDIENTS & COST info - for pricing a component
    with open(MISSING_INGREDIENTS_FILE_JSON_PY, 'r') as f:
        content = f.read()
        t2_process = json.loads(content)

    # - - list is created by ccm_nutridoc_web.rb - from DTK helpers
    # we want INGREDIENTS, NUTRITION & COST information for these items
    with open(MISSING_INGREDIENTS_FILE_JSON_CCM, 'r') as f:
        content = f.read()
        t3_dtk_ccm = json.loads(content)        
    
    
    def url_w_tuple_string_listing(i):
        i_width = 40
        if (i in atomic_LUT) and (atomic_LUT[i]['url']):        # i has url
            return ({atomic_LUT[i]['url']}, f"{i.rjust(i_width)}  {atomic_LUT[i]['url']}")        
        
        if i in atomic_LUT:                                     # see if alias has url
            a = follow_alias(i)
            print(f'a={a}')
            if a:
                if 'url' in atomic_LUT[a].keys():
                    a_url = atomic_LUT[a]['url']
                    i_and_a = f"{i}({a})"
                    print(f'i_and_a={i_and_a}')
                    return ({a_url}, f"{i_and_a.rjust(i_width)}  {a_url}")
                    
        return (None, f"{i.rjust(i_width)}  not in atomic_LUT")
    
    def show_list(title, i_list):
        print(f"- {title} -".center(80,'-'))
        for i in i_list:
            print(f'i={i}')
            _, p = url_w_tuple_string_listing(i)
            print(p)    
        print(f"- {'O'} -".center(80,'-'))
        #pprint(i_list[0])
    
    pprint(t1_cost)
    show_list('t1_cost',t1_cost)
    pprint(t2_process)
    show_list('t2_process',t2_process)
    pprint(t3_dtk_ccm)
    show_list('t3_dtk_ccm',t3_dtk_ccm)

    ingredents_to_find = t3_dtk_ccm + t1_cost + t2_process
    
    scrub_found(ingredents_to_find, True) # True passing list

    show_list('ingredents_to_find',ingredents_to_find)
        
    
    # if its in the aLUT scrape info and insert it into the nutridoc    
    # if not in aLUT scrape info insert it into template and add it to end of nutridoc


    if '-u' in sys.argv:  # problem URLS to test
        # - - - - - - 
        urls_to_process = [('kettle sea salt','https://www.sainsburys.co.uk/gol-ui/product/kettle-chips-sea-salt---balsamic-vinegar-150g'),
                        ('nik naks', 'https://www.sainsburys.co.uk/gol-ui/product/nik-naks-nice-spicy-crisps-6pk'),
                        ('hot cross buns','https://www.sainsburys.co.uk/gol-ui/product/sainsburys-fruity-hot-cross-buns--taste-the-difference-x4-280g')
                        ]
        # convert list tuple to dict
        urls_to_process = {item[0]: item[1] for item in urls_to_process}
        print('scrape tests - JUST INGREDIENTS TO START - port the ruby design for site specialisations')    
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


    
    url_count = -1
    item = None    
    nutrinfo_text = '__blank__'

    for name,url in urls_to_process.items():        

        if item:
            yn = input(f"SAVE info for > {item.ri_name} <? y/n - RET to skip\n")
            if str(yn).lower() == 'y':            
                with open(URL_CACHE_ALREADY_RETRIEVED_JSON, 'w') as f:
                    url_cache[item.product_url] = json.dumps(str(item))
                    f.write(json.dumps(url_cache))
                
                with open(NUTRIENT_FILE_PATH, 'r') as f:
                    content = f.read()
                
                insert_nutridata = '__insert_from_food_scrape__\n\n' + nutrinfo_text
                content = content.replace('__insert_from_food_scrape__', insert_nutridata)
                # print('- - - - - - - - - - - - - - - - - - - |')
                # print(insert_nutridata)
                # print('- - - - - - - - - - - - - - - - - - - |')
                # print(content)
                # print('- - - - - - - - - - - - - - - - - - - |')
                
                with open(NUTRIENT_FILE_PATH, 'w') as f:
                    f.write(content)

            item = None
            nutrinfo_text = '__blank__'
        
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

