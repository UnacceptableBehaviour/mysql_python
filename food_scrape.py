#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import itertools
from pprint import pprint
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def main():
    pass

if __name__ == '__main__':

    print('scrape tests - JUST INGREDIENTS TO START - port the ruby design for ste specialisations')
    driver = webdriver.Chrome('chromedriver')
    

    # try these - in frerquency order
    #
    # sainsburies - milano sausage
    # https://www.sainsburys.co.uk/gol-ui/product/sainsburys-italian-milano-salami-slices-86g
    driver.get('https://www.sainsburys.co.uk/gol-ui/product/sainsburys-italian-milano-salami-slices-86g')
    
    urls_to_process = ['https://www.sainsburys.co.uk/shop/gb/groceries/sainsburys-cannellini-beans-in-water-410g',
                       'https://www.sainsburys.co.uk/shop/gb/groceries/mission-6-deli-mini-wrap-186g',
                       'https://www.sainsburys.co.uk/gol-ui/product/flying-goose-sriracha-hot-sauce-455ml']
    
    print(f"By.ID: {By.ID}")
    print(f"By.CSS_SELECTOR: {By.CSS_SELECTOR}")
    print(f"By.TAG_NAME: {By.TAG_NAME}")
    print(f"By.CLASS_NAME: {By.CLASS_NAME}")
    # ID = "id"
    # NAME = "name"
    # XPATH = "xpath"
    # LINK_TEXT = "link text"
    # PARTIAL_LINK_TEXT = "partial link text"
    # TAG_NAME = "tag name"
    # CLASS_NAME = "class name"
    # CSS_SELECTOR = "css selector"

    # click - to accept cookies
    #<button id="onetrust-accept-btn-handler">Accept All Cookies</button>
    while (True):
        try:
            cookie_button = driver.find_element(By.ID,'onetrust-accept-btn-handler')
            print('cookie_button')
            pprint(cookie_button)
        except Exception as exp:
            print(exp)
            print('cookie_button NOT FOUND')
        
        try:
            cookie_button.send_keys(Keys.RETURN)
        except Exception as exp:
            print(exp)
            print('cookie_button NOT PRESSED')
    
        try:
            elist = driver.find_elements(By.CSS_SELECTOR, ".productDataItemHeader + .productText")            
            for e in elist:
                print(f"len(e):{len(e)}")
                print(f"> > > - - - - - - {e.text}")
                pprint(e)        
        except Exception as exp:
            print(exp)
            print('NOTHING!')
        
        
        try:
            #igd = driver.find_element(By.CSS_SELECTOR(".productText[text^=INGREDIENTS:]"));
            ptext_c_list = driver.find_elements(By.CSS_SELECTOR, ".productText");
            for e in ptext_c_list:
                print(f"> > > - - - - - - {e.text}")
                pprint(e)   
        except Exception as exp:
            print(exp)
            print('No ingredients for you!')

# xpaths
# follow h3 Ingredients
# //*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div/section[2]/ul/li[1]/div[2]/div/div/productcontent/htmlcontent/div[3]/p[2]
# //*[@id="root"]/div[2]/div[2]/div[2]/div/div/div/div/section[2]/ul/li[1]/div[2]/div/div/productcontent/htmlcontent/div[4]/p[2]
# 
# //*[@id="mainPart"]/div[3]/div/div/ul
# //*[@id="mainPart"]/div[3]/div/div/ul

        try:
            e = driver.find_element(By.CLASS_NAME, 'pd__header')
            print(f"len(e.text):{len(e.text)}")            
            print(f"> > > - - - - - - {e.text}")
            pprint(e)        
        except Exception as exp:
            print(exp)
            print('NOTHING!')
    
        yn = input('HEY? y/(n)\n')
    
        
    # <h3 class="productDataItemHeader">Ingredients</h3>
    # next sibling
    # <div class="productText">
    #     <p></p>
    #     <p><strong>INGREDIENTS:</strong>Pork, Salt, Sugar, Dextrose, White Pepper, Antioxidant: Sodium Ascorbate;&nbsp;Garlic, Preservatives: Potassium Nitrate, Sodium Nitrite.</p><p></p>
    #     <p>Packaged in a protective atmosphere</p>
    # </div>
    
    
    
    
    yn = input('HEY? y/(n)\n')
    
    
    
    
    
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
