#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import itertools
from pprint import pprint
from pathlib import Path

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# 
# # for expected conditions
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

from product_info import ProductInfo

from food_sets import atomic_LUT, component_file_LUT, backup_nutrinfo_txt, ots_I_set, save_ots_ingredients_found, follow_alias 
import json
MISSING_INGREDIENTS_FILE_JSON = '/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_RB.json'
MISSING_INGREDIENTS_FILE_JSON_PY = '/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info_missing_ingredients_PY.json'
NUTRIENT_FILE_PATH = Path('/Users/simon/Desktop/supperclub/foodlab/_MENUS/_courses_components/z_product_nutrition_info.txt')


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

def initialise_nutrient_hash():
    return { 'energy': 0.0,
            'fat': 0.0,
            'saturates': 0.0,
            'mono-unsaturates': 0.0,
            'poly-unsaturates': 0.0,
            'omega_3_oil': 0.0,
            'carbohydrates': 0.0,
            'sugars': 0.0,
            'fibre': 0.0,
            'starch': 0.0,
            'protein': 0.0,
            'salt': 0.0,
            'alcohol': 0.0 }

igdts = 'British Potato, Vegetable Oil (Rapeseed Oil, Sunflower Oil), Yeast Extract Powder, Rice Flour, Sugar, Onion Powder, Flavourings, Yeast Powder, Salt, Nutmeg, Smoked Salt, Black Pepper, Acid: Citric Acid; Bay Leaf, Carob Flour, Black Pepper Extract, Nutmeg Extract, Unsmoked Bacon Extract, Pork Sausage Extract.'

def nutri_string(name, nutrition_info_per_100g, ndb_no='per 100g', i_list='__igdts__', igdt_type='__igdt_type__'):
    # build nutrient
    if 'http' in ndb_no: ndb_no=f"ndb_no='{ndb_no}'"
    
    nutrient_string = f"------------------ for the nutrition information {name} ({ndb_no})\n"
    
    for nut, val in nutrition_info_per_100g.items():
        if nut == 'energy':
            nutrient_string = nutrient_string + f"{nut}".ljust(20)+"\t"+f"{ round(val, 0) }".rjust(10)+"\n"
        else:
            nutrient_string = nutrient_string +  f"{nut}".ljust(20)+"\t"+f"{ round(val, 2) }".rjust(10)+"\n"
    
    nutrient_string = nutrient_string +  "Total (100g)".rjust(60)+"\n"
    
    nutrient_string_to_file = f"\n\n{nutrient_string}ingredients: {i_list}\nigdt_type: {igdt_type}"
        
    return (nutrient_string_to_file)




def main():
    pass

if __name__ == '__main__':

    target_components = []
    t1 = []
    t2 = []
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
    
    
    def listing(i):
        i_width = 40
        if (i in atomic_LUT) and (atomic_LUT[i]['url']):
            return ({atomic_LUT[i]['url']}, f"{i.rjust(i_width)}  {atomic_LUT[i]['url']}")        
        elif i in atomic_LUT:
            a = follow_alias(i)
            pprint(a)
            if a:
                alias = atomic_LUT[i]['alias']
                i_and_a = f"{i}({alias})"
                return ({a['url']}, f"{i_and_a.rjust(i_width)}  {a['url']}")
        else:
            return (None, f"{i.rjust(i_width)}  not in atomic_LUT")
    
    def show_list(title, i_list):
        print(f"- {title} -".center(80,'-'))
        for i in i_list:
            _, p = listing(i)
            print(p)    
        print(f"- {'O'} -".center(80,'-'))
    
    show_list('t1_cost',t1_cost)
    show_list('t2_process',t2_process)
    
    # urls_to_process = []
    # 
    # for i in t1_cost:
    #     url, p = listing(i)
    #     print(p)
    #     if url == None:
    #         url = input(f"URL for {i}?\n")            
    #     urls_to_process.append((i, url))
    # 
    # for i in t2_process:
    #     url, p = listing(i)
    #     print(p)
    #     if url == None:
    #         url = input(f"URL for {i}?\n")            
    #     urls_to_process.append((i, url))    
    # 
    # print()
    # pprint(urls_to_process)
    #
    
    print(nutri_string('flying pigs', initialise_nutrient_hash(), atomic_LUT['balsamic vinegar']['url'], igdts, 'ots'))

    #sys.exit(0)
    
    
    # if its in the aLUT scrape info and insert it into the nutridoc
    
    # if not in aLUT scrape info insert it into template and add it to end of nutridoc
    
    urls_to_process = [('pearl barley',
                        'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-pearl-barley-500g'),
                       ('cooked pearl barley', ''),
                       ('blooming mushrooms', ''),
                       ('veg soup', ''),
                       ('beansprout dryfry', ''),
                       ('niknacks',
                        'https://www.sainsburys.co.uk/gol-ui/product/kp-nik-naks-nice-n-spicy-grab-bag-50g'),
                       ('sbs pastry twist',
                        'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-gruyere-poppy-twists-taste-the-difference-100g'),
                       ('duck crown',
                        'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-duck-breast-fillets-340g'),
                       ('balsamic vinegar',
                        'https://www.sainsburys.co.uk/shop/gb/groceries/sainsburys-balsamic-vinegar-500ml'),
                       ('goats cheese',
                        'https://www.sainsburys.co.uk/gol-ui/product/coeur-de-lion-la-buche-goats-cheese-150g'),
                       ('blackcurrant conserve',
                        'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-blackcurrant-conserve--taste-the-difference-340g'),
                       ('bread flour',
                        'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-strong-white-bread-flour--unbleached-15kg')]


    print('scrape tests - JUST INGREDIENTS TO START - port the ruby design for site specialisations')    
    
    url_count = -1

    while (True):
        url_count += 1
        name, url = urls_to_process[url_count]
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print(url)
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')        
        
        if url == '': continue

        yn = input(f'Find info for "{name}"? y/n - RET to skip\n')
        if str(yn).lower() == 'n': sys.exit(0)
        if str(yn).lower() == '': continue

        print(f"Getting: {urls_to_process[url_count]}")
        
        item = ProductInfo(name, url)

        print(f"\n\nItem: {item.ri_name} - {item.product_name}\nIngredients:{item.i_list}")

            
    
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
# Selenium Hello World
# https://www.browserstack.com/guide/locators-in-selenium
# https://www.browserstack.com/guide/get-html-source-of-web-element-in-selenium-webdriver

# To run interactive:
# open python and load driver
# % python
# uncommment & paste in interactive shell:
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

