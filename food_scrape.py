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

# for expected conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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

    print('scrape tests - JUST INGREDIENTS TO START - port the ruby design for ste specialisations')
    driver = webdriver.Chrome('chromedriver')
    

    # try these - in frerquency order
    #
    # sainsburies - milano sausage
    # https://www.sainsburys.co.uk/gol-ui/product/sainsburys-italian-milano-salami-slices-86g
    
    
    url_count = 0
    urls_to_process = [#'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-italian-milano-salami-slices-86g',
                       'https://www.sainsburys.co.uk/shop/gb/groceries/sainsburys-cannellini-beans-in-water-410g',
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

    cookie_barrier = True
    delay_in_seconds = 3
    
    while (True):
        url = urls_to_process[url_count]
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print(url)
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')        
        driver.get(url)
        

        allow_cookies_btn_id = 'onetrust-accept-btn-handler'
        if cookie_barrier:
            try:
                print('try cookie_button w WAIT')
                cookie_button = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.ID, allow_cookies_btn_id)))
                #cookie_button = driver.find_element(By.ID,'onetrust-accept-btn-handler')
                print('cookie_button')
                pprint(cookie_button)
            except TimeoutException:
                print("Loading took too much time!")
            except Exception as exp:
                print(exp)
                print('cookie_button NOT FOUND')
            
            try:
                print('cookie_button CLICK')
                cookie_button.send_keys(Keys.RETURN)
                cookie_barrier = False            
            except Exception as exp:
                print(exp)
                print('cookie_button NOT clicked')
    
    
        try:    # wait content load
            css_selector = 'h3.productDataItemHeader, h3.itemHeader'
            print(f'# # #> waiting for h3 tags: {css_selector}')
            h3_tags = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            #driver.find_elements(By.CSS_SELECTOR, 'h3.productDataItemHeader')
        except TimeoutException:
            print("Waiting for INGREDIENTS took too much time!")
        except Exception as exp:
            print(exp)
            print('Ingredients NOT FOUND')
                
        try:
            css_selector = 'h3, .productDataItemHeader, .productIngredients, .productText'
            print(f'# # #> getting list of element w selector: {css_selector}')
            #elist = WebDriverWait(driver, delay_in_seconds).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))            
            elist = driver.find_elements(By.CSS_SELECTOR, css_selector)            
            for e in elist:
                print(f"len(e):{len(e)}")
                print(f"> > > - - - - - - {e.text}")
                pprint(e)        
        except Exception as exp:
            print(exp)
            print('NOTHING!')
        
        
        # try:
        #     css_selector = ".productText"
        #     #css_selector = ".productDataItemHeader, .productText"
        #     print(f'# # #> getting list of element w selector: {css_selector}')            
        #     print('getting list of element w selector: .productText')
        #     #igd = driver.find_element(By.CSS_SELECTOR(".productText[text^=INGREDIENTS:]"));
        #     ptext_c_list = driver.find_elements(By.CSS_SELECTOR, ".productText");
        #     for e in ptext_c_list:
        #         print(f"> > > - - - - - - {e.text}")
        #         pprint(e)   
        # except Exception as exp:
        #     print(exp)
        #     print('No ingredients for you!')
        # 
        # 
        # 
        # try:
        #     e = driver.find_element(By.CLASS_NAME, 'pd__header')
        #     print(f"len(e.text):{len(e.text)}")            
        #     print(f"> > > - - - - - - {e.text}")
        #     pprint(e)        
        # except Exception as exp:
        #     print(exp)
        #     print('NOTHING!')

    
        yn = input('Try again? (y)/n\n')
        if str(yn).lower() == 'n': sys.exit(0)
        elif 'http' in yn:
            url_count += 1
            print(f"Getting: {urls_to_process[url_count]}")
            
    
        
    # <h3 class="productDataItemHeader">Ingredients</h3>
    # next sibling
    # <div class="productText">
    #     <p></p>
    #     <p><strong>INGREDIENTS:</strong>Pork, Salt, Sugar, Dextrose, White Pepper, Antioxidant: Sodium Ascorbate;&nbsp;Garlic, Preservatives: Potassium Nitrate, Sodium Nitrite.</p><p></p>
    #     <p>Packaged in a protective atmosphere</p>
    # </div>
    
    
    
    

    
    
    
    
    
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





# Experimets
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
# driver.find_elements(By.CSS_SELECTOR, "h3:contains('Ingredients')") # Message: invalid selector: An invalid or illegal selector was specified
# driver.find_elements(By.CSS_SELECTOR, "h3[text='Ingredients']")     # returns []
# driver.find_elements(By.CSS_SELECTOR, 'h3.productDataItemHeader')   # returns [e1, e2. . .] e = <selenium.webdriver.remote.webelement.WebElement (session="2d914c403b343e929ad84c84ada411f7", element="a32d21a9-e4f0-4936-ac2d-87c07a14f834")>
#
# pprint(driver.find_elements(By.CSS_SELECTOR, "h3.productDataItemHeader")[2].text)                 # 'Ingredients'
# pprint(driver.find_elements(By.CSS_SELECTOR, "h3.productDataItemHeader[text='Ingredients']"))     # []

